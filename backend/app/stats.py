"""Resumen de comportamiento para el panel: embudo, ofertas y actividad reciente."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

PASOS_WEB = ("home_view", "url_submit", "report_view", "door_view", "door_click", "lead_submit")


def _props(evento: dict[str, Any]) -> dict[str, Any]:
    try:
        valor = json.loads(evento.get("props_json") or "{}")
        return valor if isinstance(valor, dict) else {}
    except ValueError:
        return {}


def _entero(valor: Any) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def calcular(audits: list[dict], events: list[dict], leads: list[dict]) -> dict[str, Any]:
    por_audit: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "vistas": 0, "sesiones": set(), "scroll": 0, "segundos": 0,
        "vio_ofertas": False, "ofertas": set(), "soluciones": 0, "moviles": 0,
    })
    sesiones_por_paso: dict[str, set[str]] = {p: set() for p in PASOS_WEB}
    clics_oferta: Counter[str] = Counter()
    soluciones: Counter[str] = Counter()
    origen_de_sesion: dict[str, str] = {}

    for e in events:
        nombre, sesion, props = e["name"], e["session_id"], _props(e)
        if nombre in sesiones_por_paso:
            sesiones_por_paso[nombre].add(sesion)
        if nombre == "page_view":
            origen_de_sesion.setdefault(sesion, e.get("utm_source") or e.get("referrer") or "directo")
        if nombre == "door_click":
            clics_oferta[str(props.get("door"))] += 1
        if nombre == "finding_open":
            soluciones[str(props.get("id"))] += 1
        aid = e.get("audit_id")
        if not aid:
            continue
        a = por_audit[aid]
        if nombre == "report_view":
            a["vistas"] += 1
            a["sesiones"].add(sesion)
            a["moviles"] += 1 if e.get("device") == "movil" else 0
        elif nombre == "scroll_depth":
            a["scroll"] = max(a["scroll"], _entero(props.get("pct")))
        elif nombre == "engaged":
            a["segundos"] = max(a["segundos"], _entero(props.get("s")))
        elif nombre == "door_view":
            a["vio_ofertas"] = True
        elif nombre == "door_click":
            a["ofertas"].add(str(props.get("door")))
        elif nombre == "finding_open":
            a["soluciones"] += 1

    leads_por_audit: Counter[str] = Counter(l["audit_id"] for l in leads if l.get("audit_id"))
    leads_por_oferta: Counter[str] = Counter(l["door"] for l in leads)

    grupos: dict[str, dict[str, int]] = defaultdict(lambda: {
        "informes": 0, "abiertos": 0, "leyeron_mitad": 0, "vieron_ofertas": 0, "clic_oferta": 0, "dejaron_email": 0,
    })
    filas = []
    for au in audits:
        if au["status"] != "listo":
            continue
        a = por_audit.get(au["id"]) or {"vistas": 0, "sesiones": set(), "scroll": 0, "segundos": 0,
                                        "vio_ofertas": False, "ofertas": set(), "soluciones": 0, "moviles": 0}
        grupo = (au.get("sector") or "(sin sector)") if au["source"] == "envio" else "Visitantes de la web"
        g = grupos[grupo]
        g["informes"] += 1
        g["abiertos"] += 1 if a["vistas"] else 0
        g["leyeron_mitad"] += 1 if a["scroll"] >= 50 else 0
        g["vieron_ofertas"] += 1 if a["vio_ofertas"] else 0
        g["clic_oferta"] += 1 if a["ofertas"] else 0
        g["dejaron_email"] += 1 if leads_por_audit.get(au["id"]) else 0
        filas.append({
            "id": au["id"], "dominio": au["domain"], "origen": au["source"], "sector": au.get("sector"),
            "lote": au.get("batch"), "nota": au.get("score"), "creado": au["created_at"],
            "vistas": a["vistas"], "visitantes": len(a["sesiones"]), "desde_movil": a["moviles"],
            "scroll": a["scroll"], "segundos": a["segundos"], "vio_ofertas": a["vio_ofertas"],
            "ofertas": sorted(a["ofertas"]), "soluciones_abiertas": a["soluciones"],
            "emails": leads_por_audit.get(au["id"], 0),
        })

    dominio_de = {au["id"]: au["domain"] for au in audits}
    recientes = [{
        "ts": e["ts"], "evento": e["name"], "dominio": dominio_de.get(e.get("audit_id") or ""),
        "props": _props(e), "dispositivo": e.get("device"), "sesion": e["session_id"][:8],
    } for e in events[:200]]

    return {
        "totales": {
            "informes": sum(1 for a in audits if a["status"] == "listo"),
            "errores": sum(1 for a in audits if a["status"] == "error"),
            "eventos": len(events),
            "emails": len(leads),
        },
        "embudo_web": [{"paso": p, "sesiones": len(sesiones_por_paso[p])} for p in PASOS_WEB],
        "embudo_por_grupo": [{"grupo": nombre, **valores} for nombre, valores in sorted(grupos.items())],
        "ofertas": [{"oferta": o, "clics": clics_oferta.get(o, 0), "emails": leads_por_oferta.get(o, 0)}
                    for o in ("gratis",)],
        "soluciones_mas_abiertas": [{"id": k, "veces": v} for k, v in soluciones.most_common(10)],
        "origenes": [{"origen": k, "visitantes": v} for k, v in Counter(origen_de_sesion.values()).most_common(20)],
        "informes": filas[:300],
        "emails": [{"ts": l["ts"], "oferta": l["door"], "email": l["email"],
                    "dominio": dominio_de.get(l.get("audit_id") or "")} for l in leads[:200]],
        "recientes": recientes,
    }
