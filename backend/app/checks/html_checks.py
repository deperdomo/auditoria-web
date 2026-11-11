"""Comprobaciones sobre el HTML de la portada. Sin IA: son reglas fijas."""
from __future__ import annotations

import json
import re
from typing import Any, Optional
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup

from ..security import Descarga, UrlNoValida, descargar

RASTREADORES = {
    "Google Analytics / Tag Manager": ("googletagmanager.com", "google-analytics.com", "gtag("),
    "Píxel de Meta (Facebook)": ("connect.facebook.net", "fbq("),
    "Hotjar": ("static.hotjar.com", "hotjar.com/c/"),
    "Microsoft Clarity": ("clarity.ms",),
    "Píxel de TikTok": ("analytics.tiktok.com",),
    "LinkedIn Insight": ("snap.licdn.com",),
    "Google Ads / DoubleClick": ("doubleclick.net", "googleadservices.com"),
}

GESTORES_COOKIES = (
    "cookiebot", "onetrust", "cookielaw", "complianz", "cmplz", "cookieyes", "cookie-law-info",
    "iubenda", "usercentrics", "didomi", "quantcast", "termly", "cookie-script", "osano",
    "borlabs", "klaro", "tarteaucitron", "axeptio", "cookie-notice", "cookieconsent",
    "cookie-consent", "cookiefirst", "moove_gdpr", "gdpr-cookie",
    "eu-cookie-compliance", "eu_cookie_compliance", "cookie-banner", "cookiebanner", "cookie_banner",
    "cookies-banner", "cookie-bar", "cookiebar", "cookie-prefs", "cookies-box", "cookie_notice",
    "consent-tracking-api", "consentmanager", "cookiehub", "cookiepro", "trustarc", "civiccomputing",
    "cookieinformation", "real-cookie-banner", "gtag('consent'", 'gtag("consent"',
)

TELEFONO = re.compile(r"(?<!\d)(?:\+34|0034)?[\s.-]?[6789]\d{2}[\s.-]?\d{2,3}[\s.-]?\d{2,3}[\s.-]?\d{0,2}(?!\d)")


def _texto(etiqueta: Any) -> str:
    return etiqueta.get_text(" ", strip=True) if etiqueta else ""


def _meta(sopa: BeautifulSoup, **atributos: str) -> Optional[str]:
    etiqueta = sopa.find("meta", attrs=atributos)
    contenido = etiqueta.get("content") if etiqueta else None
    return contenido.strip() if isinstance(contenido, str) and contenido.strip() else None


def _tipos_json_ld(sopa: BeautifulSoup) -> list[str]:
    tipos: list[str] = []

    def recorrer(nodo: Any) -> None:
        if isinstance(nodo, dict):
            tipo = nodo.get("@type")
            if isinstance(tipo, str):
                tipos.append(tipo)
            elif isinstance(tipo, list):
                tipos.extend(t for t in tipo if isinstance(t, str))
            for valor in nodo.values():
                recorrer(valor)
        elif isinstance(nodo, list):
            for elemento in nodo:
                recorrer(elemento)

    for script in sopa.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            recorrer(json.loads(script.string or ""))
        except (ValueError, TypeError):
            continue
    return sorted(set(tipos))


def analizar_html(html: str, url_final: str) -> dict[str, Any]:
    """Extrae hechos del HTML. Función pura: no hace peticiones de red."""
    sopa = BeautifulSoup(html, "html.parser")
    bajo = html.lower()

    titulo = _texto(sopa.title)
    descripcion = _meta(sopa, name="description")
    robots = (_meta(sopa, name="robots") or "").lower()
    etiqueta_html = sopa.find("html")
    idioma = etiqueta_html.get("lang") if etiqueta_html else None

    imagenes = sopa.find_all("img")
    # alt="" es la forma correcta de marcar una imagen decorativa: solo cuenta si falta el atributo.
    sin_alt = [i for i in imagenes if i.get("alt") is None
               and i.get("aria-hidden") != "true" and i.get("role") != "presentation"]

    enlaces = sopa.find_all("a")
    textos_enlaces = [(_texto(a).lower(), str(a.get("href") or "").lower()) for a in enlaces]

    def hay_enlace(*patrones: str) -> bool:
        return any(any(p in texto or p in href for p in patrones) for texto, href in textos_enlaces)

    hrefs = [href for _, href in textos_enlaces]
    tel_clicable = any(h.startswith("tel:") for h in hrefs)
    texto_visible = sopa.get_text(" ", strip=True)
    tel_en_texto = bool(TELEFONO.search(texto_visible))
    generador = _meta(sopa, name="generator")

    return {
        "https": urlsplit(url_final).scheme == "https",
        "titulo": titulo,
        "titulo_len": len(titulo),
        "descripcion_len": len(descripcion) if descripcion else 0,
        "h1": len(sopa.find_all("h1")),
        "viewport": bool(_meta(sopa, name="viewport")),
        "idioma": idioma if isinstance(idioma, str) and idioma.strip() else None,
        "noindex": "noindex" in robots,
        "favicon": bool(sopa.find("link", rel=lambda v: bool(v) and "icon" in " ".join(v if isinstance(v, list) else [v]).lower())),
        "og_titulo": bool(_meta(sopa, property="og:title")),
        "og_imagen": bool(_meta(sopa, property="og:image")),
        "datos_estructurados": _tipos_json_ld(sopa),
        "imagenes": len(imagenes),
        "imagenes_sin_alt": len(sin_alt),
        "aviso_legal": hay_enlace("aviso legal", "aviso-legal", "avisolegal", "legal notice", "nota legal", "terminos", "términos",
                                  "condiciones de uso", "condiciones-de-uso", "condiciones generales", "condiciones-generales",
                                  "condiciones legales", "información legal", "informacion-legal", "advertencia legal",
                                  "advertencia-legal", "terms", "/legal"),
        "privacidad": hay_enlace("privacidad", "privacy", "protección de datos", "proteccion-de-datos"),
        "enlace_cookies": hay_enlace("cookies"),
        "tel_clicable": tel_clicable,
        "tel_en_texto": tel_en_texto,
        "email": any(h.startswith("mailto:") for h in hrefs),
        "whatsapp": any("wa.me/" in h or "api.whatsapp.com" in h for h in hrefs),
        "pagina_contacto": hay_enlace("contacto", "contacta", "contáctanos", "contact"),
        # Portada casi vacía: el contenido lo pinta JavaScript y aquí no se ve. Sin enlaces, imágenes ni texto,
        # «no se ha encontrado X» no significa nada, así que esas comprobaciones se omiten.
        "poco_contenido": len(enlaces) < 3 and not imagenes and len(texto_visible) < 300,
        "rastreadores": [nombre for nombre, marcas in RASTREADORES.items() if any(m in bajo for m in marcas)],
        "gestor_cookies": any(g in bajo for g in GESTORES_COOKIES),
        "tecnologia": generador[:60] if generador else None,
    }


def _existe(url: str) -> Optional[Descarga]:
    try:
        d = descargar(url, max_bytes=200_000, timeout=8.0)
    except (UrlNoValida, httpx.HTTPError):
        return None
    return d if d.estado == 200 else None


def recoger_datos(url: str) -> dict[str, Any]:
    """Descarga la portada y recursos auxiliares y devuelve todos los hechos."""
    try:
        portada = descargar(url)
    except httpx.HTTPError:
        if url.startswith("https://"):
            try:
                portada = descargar("http://" + url[len("https://"):])
            except httpx.HTTPError:
                raise UrlNoValida("No se ha podido abrir esa web. Comprueba que la dirección es correcta y que funciona.")
        else:
            raise UrlNoValida("No se ha podido abrir esa web. Comprueba que la dirección es correcta y que funciona.")
    if portada.estado in (401, 403, 429):
        raise UrlNoValida("Esa web no deja que la revisen herramientas automáticas, así que no se puede analizar.")
    if portada.truncada:
        raise UrlNoValida("La portada de esa web pesa demasiado para analizarla entera, y un informe a medias no sería fiable.")
    if portada.estado >= 400:
        raise UrlNoValida(f"La web ha respondido con un error ({portada.estado}) y no se puede analizar.")
    if "<html" not in portada.texto.lower() and "<body" not in portada.texto.lower():
        raise UrlNoValida("Esa dirección no devuelve una página web.")

    datos = analizar_html(portada.texto, portada.url_final)
    partes = urlsplit(portada.url_final)
    base = f"{partes.scheme}://{partes.netloc}"
    datos["url_final"] = portada.url_final
    datos["respuesta_ms"] = portada.ms

    # ¿La versión sin cifrar redirige a la segura?
    datos["http_redirige"] = None
    if datos["https"]:
        try:
            insegura = descargar(f"http://{partes.netloc}/", max_bytes=50_000, timeout=8.0)
            datos["http_redirige"] = insegura.url_final.startswith("https://")
        except (UrlNoValida, httpx.HTTPError):
            datos["http_redirige"] = None

    robots = _existe(f"{base}/robots.txt")
    texto_robots = robots.texto.lower() if robots and "<html" not in robots.texto.lower() else ""
    datos["robots_txt"] = bool(texto_robots)
    datos["sitemap"] = "sitemap:" in texto_robots or _existe(f"{base}/sitemap.xml") is not None
    if not datos["favicon"]:  # sin etiqueta <link>, los navegadores usan /favicon.ico si existe
        icono = _existe(f"{base}/favicon.ico")
        datos["favicon"] = bool(icono and icono.cabeceras.get("content-type", "").startswith("image"))
    return datos
