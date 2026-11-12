from __future__ import annotations

import json
import re
import secrets
from typing import Any, Optional

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from . import audit, db, stats
from .config import ajustes
from .security import LimitePorIp, UrlNoValida, comprobar_host_publico, dominio_de, normalizar_url

app = FastAPI(title="Auditoría web", docs_url=None, redoc_url=None)
db.iniciar()

limite_analisis = LimitePorIp(ajustes.rate_limit_per_hour, 3600)
limite_eventos = LimitePorIp(1500, 3600)
limite_contactos = LimitePorIp(10, 3600)

NOMBRE_EVENTO = re.compile(r"^[a-z0-9_]{1,40}$")
EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[a-zA-Z]{2,24}$")
OFERTAS = {"gratis"}


def ip_de(request: Request) -> str:
    if ajustes.trust_proxy:
        # Se toma la última IP de la lista: es la que añade tu proxy (nginx/Caddy).
        # Las anteriores las puede inventar el propio visitante.
        reenviada = request.headers.get("x-forwarded-for")
        if reenviada:
            return reenviada.split(",")[-1].strip()
    return request.client.host if request.client else "desconocida"


def es_admin(token: Optional[str]) -> bool:
    configurado = ajustes.admin_token
    if not configurado or configurado == "cambia-esto" or not token:
        return False
    return secrets.compare_digest(token, configurado)


class NuevoAnalisis(BaseModel):
    url: str = Field(max_length=2000)
    sector: Optional[str] = Field(default=None, max_length=60)
    batch: Optional[str] = Field(default=None, max_length=60)


class Evento(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    name: str = Field(max_length=40)
    audit_id: Optional[str] = Field(default=None, max_length=32)
    props: dict[str, Any] = Field(default_factory=dict)
    path: Optional[str] = Field(default=None, max_length=300)
    referrer: Optional[str] = Field(default=None, max_length=500)
    utm_source: Optional[str] = Field(default=None, max_length=100)


class Contacto(BaseModel):
    email: str = Field(max_length=255)
    door: str = Field(max_length=20)
    consent: bool
    audit_id: Optional[str] = Field(default=None, max_length=32)
    session_id: Optional[str] = Field(default=None, max_length=64)


@app.get("/api/health")
def salud() -> dict[str, Any]:
    return {"ok": True, "mide_velocidad": bool(ajustes.pagespeed_api_key)}


@app.post("/api/audits")
def crear_analisis(cuerpo: NuevoAnalisis, request: Request, tareas: BackgroundTasks,
                   x_admin_token: Optional[str] = Header(default=None)) -> dict[str, Any]:
    admin = es_admin(x_admin_token)
    try:
        url = normalizar_url(cuerpo.url)
        comprobar_host_publico(url.split("/")[2].split(":")[0])
    except UrlNoValida as error:
        raise HTTPException(status_code=422, detail=str(error))

    if not admin:
        reciente = db.buscar_reciente(url, ajustes.cache_hours)
        if reciente:
            return {"id": reciente, "reutilizado": True}
        if not limite_analisis.permitir(ip_de(request)):
            raise HTTPException(status_code=429, detail="Has hecho muchos análisis seguidos. Prueba de nuevo dentro de una hora.")

    audit_id = secrets.token_urlsafe(8)
    db.crear_audit(audit_id, url, dominio_de(url), "envio" if admin else "web",
                   cuerpo.sector if admin else None, cuerpo.batch if admin else None)
    tareas.add_task(audit.ejecutar, audit_id, url)
    return {"id": audit_id, "reutilizado": False}


@app.get("/api/audits/{audit_id}")
def leer_analisis(audit_id: str) -> dict[str, Any]:
    fila = db.leer_audit(audit_id)
    if not fila:
        raise HTTPException(status_code=404, detail="Ese informe no existe.")
    return {
        "id": fila["id"],
        "status": fila["status"],
        "url": fila["url"],
        "domain": fila["domain"],
        "created_at": fila["created_at"],
        "error": fila["error"],
        "result": json.loads(fila["result_json"]) if fila["result_json"] else None,
    }


@app.post("/api/events", status_code=204)
def registrar_evento(evento: Evento, request: Request) -> None:
    if not NOMBRE_EVENTO.match(evento.name):
        raise HTTPException(status_code=422, detail="Evento no válido.")
    if len(json.dumps(evento.props)) > 2000:
        raise HTTPException(status_code=422, detail="Demasiados datos.")
    if not limite_eventos.permitir(ip_de(request)):
        return None
    agente = request.headers.get("user-agent", "")
    db.guardar_evento(evento.session_id, evento.name, evento.audit_id, evento.props, evento.path,
                      evento.referrer, evento.utm_source, "movil" if "Mobi" in agente else "escritorio")
    return None


@app.post("/api/leads", status_code=201)
def registrar_contacto(contacto: Contacto, request: Request) -> dict[str, bool]:
    if not contacto.consent:
        raise HTTPException(status_code=422, detail="Necesito tu consentimiento para guardar el email.")
    email = contacto.email.strip().lower()
    if not EMAIL.match(email):
        raise HTTPException(status_code=422, detail="Ese email no parece válido.")
    if contacto.door not in OFERTAS:
        raise HTTPException(status_code=422, detail="Oferta no válida.")
    if not limite_contactos.permitir(ip_de(request)):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Prueba más tarde.")
    db.guardar_lead(contacto.audit_id, contacto.session_id, contacto.door, email)
    return {"ok": True}


@app.get("/api/admin/stats")
def estadisticas(x_admin_token: Optional[str] = Header(default=None)) -> dict[str, Any]:
    if not es_admin(x_admin_token):
        raise HTTPException(status_code=403, detail="Token incorrecto o sin configurar.")
    return stats.calcular(*db.todo_para_estadisticas())


@app.delete("/api/admin/audits/{audit_id}", status_code=204)
def borrar_analisis(audit_id: str, x_admin_token: Optional[str] = Header(default=None)) -> None:
    if not es_admin(x_admin_token):
        raise HTTPException(status_code=403, detail="Token incorrecto o sin configurar.")
    if not db.borrar_audit(audit_id):
        raise HTTPException(status_code=404, detail="Ese informe no existe.")
