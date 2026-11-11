from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def _bool(nombre: str, defecto: bool) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes")


class Ajustes:
    def __init__(self) -> None:
        self.pagespeed_api_key = os.getenv("PAGESPEED_API_KEY", "").strip()
        self.admin_token = os.getenv("ADMIN_TOKEN", "").strip()
        ruta = Path(os.getenv("DATABASE_PATH", "data/auditoria.db"))
        self.database_path = ruta if ruta.is_absolute() else RAIZ / ruta
        self.rate_limit_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "5"))
        self.cache_hours = int(os.getenv("CACHE_HOURS", "24"))
        self.trust_proxy = _bool("TRUST_PROXY", True)
        self.public_base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:3000").rstrip("/")


ajustes = Ajustes()
