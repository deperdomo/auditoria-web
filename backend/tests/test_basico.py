import os
import tempfile

os.environ["DATABASE_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["ADMIN_TOKEN"] = "token-de-prueba"
os.environ["PAGESPEED_API_KEY"] = ""
os.environ["RATE_LIMIT_PER_HOUR"] = "3"

import pytest
from fastapi.testclient import TestClient

from app import audit, main, security
from app.checks.html_checks import analizar_html
from app.report import construir_informe
from app.security import UrlNoValida, normalizar_url

HTML_BUENO = """<!doctype html><html lang="es"><head>
<title>Fisioterapia en Chamberí | Clínica Ejemplo Madrid</title>
<meta name="description" content="Clínica de fisioterapia en Chamberí. Tratamos lesiones deportivas, dolor de espalda y rehabilitación. Pide cita hoy mismo por teléfono.">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta property="og:title" content="x"><meta property="og:image" content="https://e.es/a.jpg">
<link rel="icon" href="/favicon.ico">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"LocalBusiness","name":"x"}</script>
</head><body><h1>Fisioterapia</h1>
<a href="tel:+34910000000">910 000 000</a> <a href="/aviso-legal">Aviso legal</a>
<a href="/privacidad">Política de privacidad</a></body></html>"""

HTML_MALO = """<html><head><meta name="robots" content="noindex">
<script src="https://www.googletagmanager.com/gtag/js?id=G-1"></script></head>
<body><p>Llámanos al 612 345 678</p><img src="a.jpg"><img src="b.jpg"><img src="c.jpg"></body></html>"""


def test_normalizar_url():
    assert normalizar_url("MiNegocio.es") == "https://minegocio.es/"
    assert normalizar_url("http://a.com/x?y=1#z") == "http://a.com/x?y=1"
    for mala in ["", "localhost", "ftp://a.com", "http://127.0.0.1", "https://a.com:8080", "https://u:p@a.com", "a b.com"]:
        with pytest.raises(UrlNoValida):
            normalizar_url(mala)


def test_bloquea_direcciones_internas(monkeypatch):
    def falso(host, *a, **k):
        return [(2, 1, 6, "", ("169.254.169.254", 0))]
    monkeypatch.setattr(security.socket, "getaddrinfo", falso)
    with pytest.raises(UrlNoValida):
        security.comprobar_host_publico("metadatos.ejemplo.com")


def test_informe_bueno_y_malo():
    bueno = analizar_html(HTML_BUENO, "https://e.es/")
    bueno.update(sitemap=True, http_redirige=True)
    psi = {"rendimiento": 95, "accesibilidad": 96, "lcp_s": 1.8, "cls": 0.02, "peso_mb": 1.1}
    informe = construir_informe(bueno, psi)
    assert informe["puntuacion"] == 100
    assert informe["resumen"]["mal"] == 0

    malo = analizar_html(HTML_MALO, "http://e.es/")
    malo.update(sitemap=False, http_redirige=None)
    informe = construir_informe(malo, None)
    ids = {h["id"]: h["estado"] for c in informe["categorias"] for h in c["hallazgos"]}
    assert ids["seo_noindex"] == "mal"
    assert ids["leg_https"] == "mal"
    assert ids["leg_cookies"] == "mal"
    assert ids["con_contacto"] == "mejorable"   # teléfono escrito pero no pulsable
    assert ids["seo_alt"] == "mejorable"
    assert informe["velocidad_medida"] is False
    assert informe["puntuacion"] < 40
    for c in informe["categorias"]:
        for h in c["hallazgos"]:
            assert "{" not in h["titulo"] + h["explicacion"] + h["accion"]


def test_api_completa(monkeypatch):
    monkeypatch.setattr(main, "comprobar_host_publico", lambda host: None)

    def falso_ejecutar(audit_id, url):
        datos = analizar_html(HTML_MALO, url)
        datos.update(sitemap=False, http_redirige=None, url_final=url)
        main.db.guardar_resultado(audit_id, construir_informe(datos, None))
    monkeypatch.setattr(audit, "ejecutar", falso_ejecutar)

    c = TestClient(main.app)
    assert c.post("/api/audits", json={"url": "no es una url"}).status_code == 422

    r = c.post("/api/audits", json={"url": "ejemplo-prueba.es", "sector": "x"})
    assert r.status_code == 200
    aid = r.json()["id"]
    informe = c.get(f"/api/audits/{aid}").json()
    assert informe["status"] == "listo" and informe["result"]["categorias"]
    assert c.post("/api/audits", json={"url": "ejemplo-prueba.es"}).json() == {"id": aid, "reutilizado": True}

    # límite por IP: 3 por hora (ya va 1)
    assert c.post("/api/audits", json={"url": "dos.es"}).status_code == 200
    assert c.post("/api/audits", json={"url": "tres.es"}).status_code == 200
    assert c.post("/api/audits", json={"url": "cuatro.es"}).status_code == 429

    # el administrador no tiene límite y puede etiquetar sector y lote
    admin = {"X-Admin-Token": "token-de-prueba"}
    r = c.post("/api/audits", json={"url": "clinica.es", "sector": "clinicas", "batch": "l1"}, headers=admin)
    envio = r.json()["id"]

    def ev(nombre, audit_id=None, **props):
        return c.post("/api/events", json={"session_id": "s1", "name": nombre, "audit_id": audit_id, "props": props})
    assert ev("report_view", envio).status_code == 204
    assert ev("scroll_depth", envio, pct=75).status_code == 204
    assert ev("door_view", envio).status_code == 204
    assert ev("door_click", envio, door="pdf").status_code == 204
    assert ev("Nombre Malo").status_code == 422

    assert c.post("/api/leads", json={"email": "a@b.es", "door": "pdf", "consent": False}).status_code == 422
    assert c.post("/api/leads", json={"email": "mal", "door": "pdf", "consent": True}).status_code == 422
    assert c.post("/api/leads", json={"email": "A@b.es", "door": "pdf", "consent": True, "audit_id": envio}).status_code == 201

    assert c.get("/api/admin/stats").status_code == 403
    s = c.get("/api/admin/stats", headers=admin).json()
    grupo = next(g for g in s["embudo_por_grupo"] if g["grupo"] == "clinicas")
    assert grupo == {"grupo": "clinicas", "informes": 1, "abiertos": 1, "leyeron_mitad": 1,
                     "vieron_ofertas": 1, "clic_oferta": 1, "dejaron_email": 1}
    assert s["ofertas"][0] == {"oferta": "pdf", "clics": 1, "emails": 1}
    assert s["totales"]["emails"] == 1


def test_falsos_positivos_vistos_en_webs_reales():
    """Casos sacados de portadas reales en las que el informe decía que faltaba algo que sí estaba."""
    html = """<html lang="es"><head><title>x</title>
    <script src="https://www.googletagmanager.com/gtm.js"></script>
    <script>var c = {"eu_cookie_compliance": {}};</script></head><body>
    <img src="a.svg" alt="" aria-hidden="true"><img src="b.svg" alt=""><img src="c.jpg"><img src="d.jpg" alt="Sala">
    <a href="/general/condiciones-de-uso">Condiciones de uso</a> <a href="/privacy">Privacidad</a>
    <a href="/contacto">Contacto</a> <a href="/servicios">Servicios</a></body></html>"""
    datos = analizar_html(html, "https://e.es/")
    assert datos["imagenes_sin_alt"] == 1          # alt="" es una imagen decorativa bien marcada
    assert datos["aviso_legal"] and datos["gestor_cookies"] and not datos["poco_contenido"]
    ids = {h["id"]: h["estado"] for c in construir_informe(datos, None)["categorias"] for h in c["hallazgos"]}
    assert ids["leg_aviso"] == "bien" and ids["leg_cookies"] == "mejorable"
    assert ids["con_contacto_enlace"] == "mejorable" and "con_contacto" not in ids

    # Portada que pinta todo con JavaScript: no se afirma que falte lo que no se puede ver.
    hueca = analizar_html("<html><head><title>Tienda</title></head><body><div id='root'></div></body></html>", "https://e.es/")
    informe = construir_informe(hueca, None)
    ids = {h["id"] for c in informe["categorias"] for h in c["hallazgos"]}
    assert informe["contenido_dinamico"] and not ids & {"leg_aviso", "leg_privacidad", "con_contacto", "seo_h1"}
