"""Mide velocidad y accesibilidad con la API gratuita de PageSpeed Insights."""
from __future__ import annotations

from typing import Any, Optional

import httpx

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CATEGORIAS = ("performance", "accessibility", "best-practices", "seo")


def _numero(auditorias: dict[str, Any], clave: str) -> Optional[float]:
    valor = (auditorias.get(clave) or {}).get("numericValue")
    return float(valor) if isinstance(valor, (int, float)) else None


def medir(url: str, api_key: str, timeout: float = 90.0) -> Optional[dict[str, Any]]:
    """Devuelve las métricas o None si no hay clave o Google no responde."""
    if not api_key:
        return None
    parametros: list[tuple[str, str]] = [("url", url), ("strategy", "mobile"), ("locale", "es"), ("key", api_key)]
    parametros += [("category", c) for c in CATEGORIAS]
    try:
        r = httpx.get(API, params=parametros, timeout=timeout)
        if r.status_code != 200:
            return None
        datos = r.json()
    except (httpx.HTTPError, ValueError):
        return None
    return interpretar(datos)


def interpretar(datos: dict[str, Any]) -> Optional[dict[str, Any]]:
    lh = datos.get("lighthouseResult") or {}
    categorias = lh.get("categories") or {}
    auditorias = lh.get("audits") or {}
    if not categorias:
        return None

    def nota(clave: str) -> Optional[int]:
        valor = (categorias.get(clave) or {}).get("score")
        return round(valor * 100) if isinstance(valor, (int, float)) else None

    lcp = _numero(auditorias, "largest-contentful-paint")
    peso = _numero(auditorias, "total-byte-weight")
    campo = (datos.get("loadingExperience") or {}).get("overall_category")
    return {
        "rendimiento": nota("performance"),
        "accesibilidad": nota("accessibility"),
        "buenas_practicas": nota("best-practices"),
        "seo": nota("seo"),
        "lcp_s": round(lcp / 1000, 1) if lcp is not None else None,
        "cls": _numero(auditorias, "cumulative-layout-shift"),
        "tbt_ms": _numero(auditorias, "total-blocking-time"),
        "peso_mb": round(peso / 1_000_000, 1) if peso is not None else None,
        "usuarios_reales": campo,  # FAST | AVERAGE | SLOW | None (sin datos suficientes)
    }
