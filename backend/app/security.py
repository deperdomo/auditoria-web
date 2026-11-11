"""Validación de URLs y descarga segura.

El servidor descarga webs que escribe cualquiera, así que hay que impedir que
alguien lo use para alcanzar direcciones internas (localhost, red privada, el
servicio de metadatos de la nube...). Esto se conoce como SSRF.
"""
from __future__ import annotations

import ipaddress
import socket
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

USER_AGENT = "Mozilla/5.0 (compatible; AuditoriaWebBot/0.1)"
MAX_BYTES = 5_000_000
MAX_REDIRECCIONES = 5


class UrlNoValida(ValueError):
    """La URL no se puede analizar. El mensaje es apto para mostrar al usuario."""


def normalizar_url(cruda: str) -> str:
    cruda = (cruda or "").strip()
    if not cruda or len(cruda) > 2000 or any(c.isspace() for c in cruda):
        raise UrlNoValida("Escribe la dirección de una web, por ejemplo minegocio.es")
    if "://" not in cruda:
        cruda = "https://" + cruda
    try:
        partes = urlsplit(cruda)
        puerto = partes.port
    except ValueError:
        raise UrlNoValida("Esa dirección no parece válida.")
    if partes.scheme not in ("http", "https"):
        raise UrlNoValida("Solo se pueden analizar direcciones http o https.")
    if partes.username or partes.password:
        raise UrlNoValida("Esa dirección no parece válida.")
    host = (partes.hostname or "").lower().rstrip(".")
    if not host or "." not in host:
        raise UrlNoValida("Escribe la dirección completa, por ejemplo minegocio.es")
    if puerto not in (None, 80, 443):
        raise UrlNoValida("Solo se pueden analizar webs en los puertos habituales.")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise UrlNoValida("Escribe un nombre de dominio, no una dirección IP.")
    red = host if puerto is None else f"{host}:{puerto}"
    return urlunsplit((partes.scheme, red, partes.path or "/", partes.query, ""))


def dominio_de(url: str) -> str:
    host = urlsplit(url).hostname or ""
    return host[4:] if host.startswith("www.") else host


def comprobar_host_publico(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError):
        raise UrlNoValida("No se ha encontrado ese dominio. Revisa que esté bien escrito.")
    if not infos:
        raise UrlNoValida("No se ha encontrado ese dominio. Revisa que esté bien escrito.")
    for info in infos:
        texto = str(info[4][0]).split("%")[0]
        ip = ipaddress.ip_address(texto)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            raise UrlNoValida("Esa dirección no es una web pública.")


@dataclass
class Descarga:
    url_final: str
    estado: int
    texto: str
    cabeceras: dict[str, str]
    ms: int
    saltos: list[str] = field(default_factory=list)
    truncada: bool = False  # se cortó al llegar a max_bytes: lo que falte no se ha visto


def descargar(url: str, *, max_bytes: int = MAX_BYTES, timeout: float = 12.0) -> Descarga:
    """Descarga una URL siguiendo redirecciones a mano y validando cada salto."""
    actual = url
    saltos: list[str] = []
    inicio = time.monotonic()
    cabeceras = {"User-Agent": USER_AGENT, "Accept-Language": "es-ES,es;q=0.9"}
    with httpx.Client(follow_redirects=False, timeout=timeout, headers=cabeceras) as cliente:
        for _ in range(MAX_REDIRECCIONES + 1):
            comprobar_host_publico(urlsplit(actual).hostname or "")
            with cliente.stream("GET", actual) as r:
                if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
                    saltos.append(actual)
                    actual = normalizar_url(urljoin(actual, r.headers["location"]))
                    continue
                trozos: list[bytes] = []
                total = 0
                for trozo in r.iter_bytes():
                    trozos.append(trozo)
                    total += len(trozo)
                    if total >= max_bytes:
                        break
                cuerpo = b"".join(trozos)[:max_bytes]
                try:
                    texto = cuerpo.decode(r.encoding or "utf-8", errors="replace")
                except LookupError:
                    texto = cuerpo.decode("utf-8", errors="replace")
                return Descarga(
                    url_final=actual,
                    estado=r.status_code,
                    texto=texto,
                    cabeceras={k.lower(): v for k, v in r.headers.items()},
                    ms=int((time.monotonic() - inicio) * 1000),
                    saltos=saltos,
                    truncada=total >= max_bytes,
                )
    raise UrlNoValida("Esa web redirige demasiadas veces y no se ha podido abrir.")


class LimitePorIp:
    """Límite sencillo en memoria: N acciones por ventana de tiempo y por IP."""

    def __init__(self, maximo: int, ventana_s: int) -> None:
        self.maximo = maximo
        self.ventana_s = ventana_s
        self._marcas: dict[str, deque[float]] = defaultdict(deque)

    def permitir(self, ip: str) -> bool:
        ahora = time.monotonic()
        cola = self._marcas[ip]
        while cola and ahora - cola[0] > self.ventana_s:
            cola.popleft()
        if len(cola) >= self.maximo:
            return False
        cola.append(ahora)
        if len(self._marcas) > 50_000:
            self._marcas.clear()
        return True
