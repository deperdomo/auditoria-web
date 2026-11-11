"""Convierte los datos medidos en hallazgos con texto y calcula la nota."""
from __future__ import annotations

from typing import Any, Optional

from .plantillas import CATEGORIAS, PLANTILLAS

PUNTOS = {"bien": 1.0, "mejorable": 0.5, "mal": 0.0}


def _tramo(valor: Optional[float], malo: float, regular: float, mayor_es_peor: bool = True) -> Optional[str]:
    if valor is None:
        return None
    if mayor_es_peor:
        return "mal" if valor > malo else "mejorable" if valor > regular else "bien"
    return "mal" if valor < malo else "mejorable" if valor < regular else "bien"


def evaluar(datos: dict[str, Any], psi: Optional[dict[str, Any]]) -> list[tuple[str, str, dict[str, Any]]]:
    """Devuelve (id de plantilla, estado, datos para el texto) de cada comprobación."""
    r: list[tuple[str, str, dict[str, Any]]] = []

    def anadir(clave: str, estado: Optional[str], **campos: Any) -> None:
        if estado and estado in PLANTILLAS[clave]:
            r.append((clave, estado, campos))

    # Velocidad (solo si PageSpeed ha respondido)
    if psi:
        anadir("vel_puntuacion", _tramo(psi.get("rendimiento"), 50, 90, mayor_es_peor=False), nota=psi.get("rendimiento"))
        lcp = psi.get("lcp_s")
        anadir("vel_lcp", _tramo(lcp, 4.0, 2.5), lcp=str(lcp).replace(".", ","))
        peso = psi.get("peso_mb")
        anadir("vel_peso", _tramo(peso, 4.0, 2.0), peso=str(peso).replace(".", ","))
        anadir("vel_saltos", _tramo(psi.get("cls"), 0.25, 0.1))
        anadir("mov_accesibilidad", _tramo(psi.get("accesibilidad"), 70, 90, mayor_es_peor=False), nota=psi.get("accesibilidad"))

    # Móvil
    anadir("mov_viewport", "bien" if datos.get("viewport") else "mal")

    # Google
    anadir("seo_noindex", "mal" if datos.get("noindex") else "bien")
    largo = datos.get("titulo_len", 0)
    titulo = (datos.get("titulo") or "")[:90]
    anadir("seo_titulo", "mal" if largo == 0 else "mejorable" if largo < 20 or largo > 65 else "bien", largo=largo, titulo=titulo)
    largo_d = datos.get("descripcion_len", 0)
    anadir("seo_descripcion", "mal" if largo_d == 0 else "mejorable" if largo_d < 70 or largo_d > 170 else "bien", largo=largo_d)
    vacia = bool(datos.get("poco_contenido"))  # portada pintada con JavaScript: lo ausente no se puede afirmar
    h1 = datos.get("h1", 0)
    if not vacia:
        anadir("seo_h1", "bien" if h1 == 1 else "mejorable", h1=h1)
    anadir("seo_sitemap", "bien" if datos.get("sitemap") else "mejorable")
    tipos = datos.get("datos_estructurados") or []
    anadir("seo_datos", "bien" if tipos else "mejorable", tipos=", ".join(tipos[:4]))
    anadir("seo_compartir", "bien" if datos.get("og_titulo") and datos.get("og_imagen") else "mejorable")
    imagenes = datos.get("imagenes", 0)
    sin_alt = datos.get("imagenes_sin_alt", 0)
    if imagenes >= 3:
        anadir("seo_alt", "mejorable" if sin_alt / imagenes > 0.3 else "bien", sin_alt=sin_alt, imagenes=imagenes)

    # Legal
    if not datos.get("https"):
        anadir("leg_https", "mal")
    elif datos.get("http_redirige") is False:
        anadir("leg_https", "mejorable")
    else:
        anadir("leg_https", "bien")
    if not vacia:
        anadir("leg_aviso", "bien" if datos.get("aviso_legal") else "mal")
        anadir("leg_privacidad", "bien" if datos.get("privacidad") else "mal")
    rastreadores = datos.get("rastreadores") or []
    nombres = ", ".join(rastreadores)
    if not rastreadores:
        anadir("leg_cookies", "bien")
    elif datos.get("gestor_cookies"):
        anadir("leg_cookies", "mejorable", rastreadores=nombres)
    elif not vacia:  # en una portada hueca el aviso lo pinta JavaScript: no se puede afirmar que falte
        anadir("leg_cookies", "mal", rastreadores=nombres)

    # Confianza
    medios = [n for n, ok in (("teléfono", datos.get("tel_clicable")), ("email", datos.get("email")),
                              ("WhatsApp", datos.get("whatsapp"))) if ok]
    if medios:
        anadir("con_contacto", "bien", medios=", ".join(medios))
    elif datos.get("tel_en_texto"):
        anadir("con_contacto", "mejorable")
    elif datos.get("pagina_contacto"):
        anadir("con_contacto_enlace", "mejorable")
    elif not vacia:
        anadir("con_contacto", "mal")
    anadir("con_favicon", "bien" if datos.get("favicon") else "mejorable")
    return r


def _nota(pares: list[tuple[str, int]]) -> Optional[int]:
    total = sum(peso for _, peso in pares)
    if not total:
        return None
    return round(100 * sum(PUNTOS[estado] * peso for estado, peso in pares) / total)


def construir_informe(datos: dict[str, Any], psi: Optional[dict[str, Any]]) -> dict[str, Any]:
    orden = {"mal": 0, "mejorable": 1, "bien": 2}
    por_categoria: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORIAS}
    pesos: dict[str, list[tuple[str, int]]] = {c: [] for c in CATEGORIAS}
    resumen = {"mal": 0, "mejorable": 0, "bien": 0}

    for clave, estado, campos in evaluar(datos, psi):
        plantilla = PLANTILLAS[clave]
        textos = plantilla[estado]
        categoria = plantilla["cat"]
        por_categoria[categoria].append({
            "id": clave,
            "estado": estado,
            "titulo": textos["titulo"].format(**campos),
            "explicacion": textos["explicacion"].format(**campos),
            "accion": textos["accion"].format(**campos),
        })
        pesos[categoria].append((estado, plantilla["peso"]))
        resumen[estado] += 1

    categorias = []
    for clave, nombre in CATEGORIAS.items():
        hallazgos = sorted(por_categoria[clave], key=lambda h: orden[h["estado"]])
        if hallazgos:
            categorias.append({"id": clave, "nombre": nombre, "puntuacion": _nota(pesos[clave]), "hallazgos": hallazgos})

    todos = [par for lista in pesos.values() for par in lista]
    return {
        "puntuacion": _nota(todos),
        "resumen": resumen,
        "categorias": categorias,
        "velocidad_medida": psi is not None,
        "contenido_dinamico": bool(datos.get("poco_contenido")),
        "url_final": datos.get("url_final"),
        "tecnologia": datos.get("tecnologia"),
    }
