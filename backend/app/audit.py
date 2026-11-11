"""Ejecuta un análisis completo y guarda el resultado."""
from __future__ import annotations

import logging

from . import db
from .checks import html_checks, pagespeed
from .config import ajustes
from .report import construir_informe
from .security import UrlNoValida

log = logging.getLogger("auditoria")


def ejecutar(audit_id: str, url: str) -> None:
    try:
        datos = html_checks.recoger_datos(url)
        psi = pagespeed.medir(datos.get("url_final") or url, ajustes.pagespeed_api_key)
        db.guardar_resultado(audit_id, construir_informe(datos, psi))
    except UrlNoValida as error:
        db.guardar_error(audit_id, str(error))
    except Exception:  # un fallo inesperado no debe dejar el informe «pendiente» para siempre
        log.exception("Fallo analizando %s", url)
        db.guardar_error(audit_id, "Ha habido un problema al analizar esta web. Inténtalo de nuevo en unos minutos.")
