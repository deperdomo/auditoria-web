"""Textos del informe, en castellano llano y hablándole al dueño del negocio.

Cada comprobación tiene un texto por estado (mal / mejorable / bien). Los huecos
entre llaves se rellenan con los datos medidos. Edita aquí para cambiar el tono;
no hace falta tocar la lógica.
"""
from __future__ import annotations

CATEGORIAS = {
    "velocidad": "Velocidad",
    "movil": "Móvil y facilidad de uso",
    "google": "Que te encuentren en Google",
    "legal": "Seguridad y textos legales",
    "confianza": "Contacto y confianza",
}

PLANTILLAS: dict[str, dict] = {
    # ---------------- Velocidad ----------------
    "vel_puntuacion": {
        "cat": "velocidad", "peso": 3,
        "mal": {
            "titulo": "Tu web es lenta en el móvil ({nota}/100)",
            "explicacion": "Google le da un {nota} sobre 100 en velocidad desde un móvil. Cuanto más tarda una página, más gente se va antes de verla, y Google también lo tiene en cuenta al ordenar los resultados.",
            "accion": "Lo habitual es reducir el peso de las imágenes, quitar complementos que no se usan y activar la caché. Suele ser trabajo de unas horas para alguien técnico.",
        },
        "mejorable": {
            "titulo": "La velocidad en móvil es aceptable, pero mejorable ({nota}/100)",
            "explicacion": "Google le da un {nota} sobre 100. No es un problema grave, pero hay margen: las webs que cargan rápido retienen a más visitantes.",
            "accion": "Revisa las imágenes más pesadas y los scripts de terceros (chats, mapas, vídeos incrustados).",
        },
        "bien": {
            "titulo": "Tu web carga rápido en el móvil ({nota}/100)",
            "explicacion": "Google le da un {nota} sobre 100 en velocidad. Está por encima de lo habitual.",
            "accion": "Nada que hacer. Vuelve a medirlo cuando añadas contenido nuevo.",
        },
    },
    "vel_lcp": {
        "cat": "velocidad", "peso": 2,
        "mal": {
            "titulo": "Lo principal de la página tarda {lcp} segundos en aparecer",
            "explicacion": "Es el tiempo hasta que el visitante ve el contenido importante (normalmente la foto o el titular de arriba). Google considera bueno menos de 2,5 segundos.",
            "accion": "Casi siempre se debe a una imagen de cabecera demasiado grande. Comprimirla y servirla en un formato moderno (WebP) suele arreglarlo.",
        },
        "mejorable": {
            "titulo": "Lo principal de la página tarda {lcp} segundos en aparecer",
            "explicacion": "Está cerca del límite que Google considera bueno (2,5 segundos).",
            "accion": "Optimiza la imagen o el bloque más grande de la parte superior de la portada.",
        },
        "bien": {
            "titulo": "El contenido principal aparece enseguida ({lcp} s)",
            "explicacion": "El visitante ve lo importante en menos de 2,5 segundos.",
            "accion": "Nada que hacer.",
        },
    },
    "vel_peso": {
        "cat": "velocidad", "peso": 1,
        "mal": {
            "titulo": "La portada pesa {peso} MB",
            "explicacion": "Es mucho para una portada. Con datos móviles tarda en bajar y consume la tarifa del visitante.",
            "accion": "Reduce el tamaño de las imágenes y los vídeos. Una portada normal no debería pasar de 2 MB.",
        },
        "mejorable": {
            "titulo": "La portada pesa {peso} MB",
            "explicacion": "Algo más de lo recomendable. Se nota sobre todo con mala cobertura.",
            "accion": "Comprime las imágenes más grandes.",
        },
        "bien": {
            "titulo": "La portada es ligera ({peso} MB)",
            "explicacion": "Baja rápido incluso con mala cobertura.",
            "accion": "Nada que hacer.",
        },
    },
    "vel_saltos": {
        "cat": "velocidad", "peso": 1,
        "mal": {
            "titulo": "La página da saltos mientras carga",
            "explicacion": "Los elementos se mueven de sitio al cargar y el visitante puede pulsar donde no quería. Resulta molesto y Google lo penaliza.",
            "accion": "Hay que reservar el espacio de imágenes, anuncios y banners antes de que carguen.",
        },
        "mejorable": {
            "titulo": "La página se mueve un poco mientras carga",
            "explicacion": "Algunos elementos cambian de sitio durante la carga.",
            "accion": "Indica el ancho y el alto de las imágenes en el código.",
        },
        "bien": {
            "titulo": "La página es estable mientras carga",
            "explicacion": "Nada se mueve de sitio de forma inesperada.",
            "accion": "Nada que hacer.",
        },
    },
    # ---------------- Móvil ----------------
    "mov_viewport": {
        "cat": "movil", "peso": 3,
        "mal": {
            "titulo": "La web no está preparada para móviles",
            "explicacion": "Falta la configuración básica que adapta la página al tamaño de la pantalla. En un móvil se verá diminuta o habrá que desplazarse de lado. La mayoría de las visitas a un negocio local llegan desde el móvil.",
            "accion": "Hay que adaptar el diseño a móviles. Si la web es antigua, a veces compensa más rehacerla que parchearla.",
        },
        "bien": {
            "titulo": "La web se adapta a la pantalla del móvil",
            "explicacion": "Tiene la configuración básica para verse bien en pantallas pequeñas.",
            "accion": "Nada que hacer.",
        },
    },
    "mov_accesibilidad": {
        "cat": "movil", "peso": 2,
        "mal": {
            "titulo": "A parte de tus visitantes les cuesta usar la web ({nota}/100)",
            "explicacion": "Hay textos con poco contraste, botones sin nombre o elementos difíciles de pulsar. Afecta sobre todo a personas mayores o con problemas de visión.",
            "accion": "Aumenta el contraste de los textos, agranda los botones y pon nombre a los enlaces que solo son un icono.",
        },
        "mejorable": {
            "titulo": "La web se puede usar, con algunos fallos de accesibilidad ({nota}/100)",
            "explicacion": "Hay detalles que dificultan el uso a algunas personas: contraste, tamaños o botones sin nombre.",
            "accion": "Revisa el contraste de los textos y el tamaño de los botones.",
        },
        "bien": {
            "titulo": "La web es fácil de usar para casi todo el mundo ({nota}/100)",
            "explicacion": "Buen contraste, botones identificables y estructura clara.",
            "accion": "Nada que hacer.",
        },
    },
    # ---------------- Google ----------------
    "seo_noindex": {
        "cat": "google", "peso": 4,
        "mal": {
            "titulo": "Tu web le está pidiendo a Google que no la muestre",
            "explicacion": "La portada lleva una instrucción (\"noindex\") que impide que aparezca en los resultados de búsqueda. Suele quedarse puesta por error después de construir la web.",
            "accion": "Quita esa instrucción. En WordPress está en Ajustes > Lectura > «Disuadir a los motores de búsqueda».",
        },
        "bien": {
            "titulo": "Google puede mostrar tu web en sus resultados",
            "explicacion": "No hay nada que le impida aparecer en las búsquedas.",
            "accion": "Nada que hacer.",
        },
    },
    "seo_titulo": {
        "cat": "google", "peso": 2,
        "mal": {
            "titulo": "La portada no tiene título",
            "explicacion": "El título es la línea azul que se ve en Google y lo primero que lee quien te busca. Sin él, Google pone lo que le parece.",
            "accion": "Escribe un título de 50-60 caracteres con lo que haces y dónde: «Fisioterapia en Chamberí | Nombre».",
        },
        "mejorable": {
            "titulo": "El título de la portada se puede aprovechar mejor ({largo} caracteres)",
            "explicacion": "Ahora dice: «{titulo}». Lo ideal son 50-60 caracteres que digan qué haces y dónde; más largo se corta en Google y más corto desperdicia espacio.",
            "accion": "Reescríbelo con tu servicio principal y tu zona.",
        },
        "bien": {
            "titulo": "El título de la portada tiene buena longitud",
            "explicacion": "Ahora dice: «{titulo}».",
            "accion": "Comprueba que menciona lo que haces y dónde.",
        },
    },
    "seo_descripcion": {
        "cat": "google", "peso": 2,
        "mal": {
            "titulo": "Falta la descripción que aparece en Google",
            "explicacion": "Es el texto gris bajo el título en los resultados. Sin ella, Google muestra un trozo cualquiera de la página, que no suele convencer a nadie.",
            "accion": "Escribe 2 frases (unos 150 caracteres) con lo que ofreces y un motivo para entrar.",
        },
        "mejorable": {
            "titulo": "La descripción para Google tiene una longitud poco adecuada ({largo} caracteres)",
            "explicacion": "Lo recomendable son entre 120 y 160 caracteres. Si es más larga se corta; si es más corta, no convence.",
            "accion": "Ajústala a unas 2 frases.",
        },
        "bien": {
            "titulo": "La descripción para Google está bien",
            "explicacion": "Tiene una longitud adecuada para mostrarse entera.",
            "accion": "Nada que hacer.",
        },
    },
    "seo_h1": {
        "cat": "google", "peso": 1,
        "mejorable": {
            "titulo": "La portada no tiene un titular principal claro",
            "explicacion": "Hemos encontrado {h1} titulares principales y debería haber exactamente uno. Es lo que le dice a Google (y al visitante) de qué va la página.",
            "accion": "Deja un único titular principal con tu servicio y tu zona.",
        },
        "bien": {
            "titulo": "La portada tiene un titular principal",
            "explicacion": "Google puede identificar de qué va la página.",
            "accion": "Nada que hacer.",
        },
    },
    "seo_sitemap": {
        "cat": "google", "peso": 1,
        "mejorable": {
            "titulo": "No hemos encontrado el mapa del sitio",
            "explicacion": "Es un archivo que le dice a Google qué páginas tiene tu web. Sin él, puede tardar más en descubrir las nuevas.",
            "accion": "Genera un sitemap.xml (casi todos los gestores lo hacen solos) y envíalo en Google Search Console.",
        },
        "bien": {
            "titulo": "Tienes mapa del sitio",
            "explicacion": "Google puede descubrir todas tus páginas.",
            "accion": "Nada que hacer.",
        },
    },
    "seo_datos": {
        "cat": "google", "peso": 1,
        "mejorable": {
            "titulo": "No le das a Google los datos de tu negocio",
            "explicacion": "Existe una forma de indicarle a Google tu dirección, horario y teléfono para que los muestre directamente en los resultados. Tu web no la usa.",
            "accion": "Añade los «datos estructurados» de tu negocio (tipo LocalBusiness). Es una tarea técnica breve.",
        },
        "bien": {
            "titulo": "Le das a Google datos sobre tu negocio",
            "explicacion": "Tu web incluye datos estructurados ({tipos}).",
            "accion": "Comprueba que la dirección y el horario están al día.",
        },
    },
    "seo_compartir": {
        "cat": "google", "peso": 1,
        "mejorable": {
            "titulo": "Al compartir tu web por WhatsApp sale sin imagen",
            "explicacion": "Cuando alguien pega tu enlace en WhatsApp o en redes, no aparece la vista previa con foto y título. Los enlaces sin imagen reciben menos clics.",
            "accion": "Añade las etiquetas de vista previa (Open Graph) con una imagen de 1200×630.",
        },
        "bien": {
            "titulo": "Tu web se ve bien al compartirla",
            "explicacion": "Al pegar el enlace en WhatsApp o redes aparece con imagen y título.",
            "accion": "Nada que hacer.",
        },
    },
    "seo_alt": {
        "cat": "google", "peso": 1,
        "mejorable": {
            "titulo": "{sin_alt} de {imagenes} imágenes no tienen descripción",
            "explicacion": "Google no ve las fotos: lee el texto que las describe. Sin él, pierdes la opción de aparecer en la búsqueda de imágenes y las personas ciegas no saben qué hay.",
            "accion": "Escribe una descripción corta en cada imagen importante.",
        },
        "bien": {
            "titulo": "Las imágenes tienen descripción",
            "explicacion": "Google y los lectores de pantalla pueden entenderlas.",
            "accion": "Nada que hacer.",
        },
    },
    # ---------------- Legal ----------------
    "leg_https": {
        "cat": "legal", "peso": 4,
        "mal": {
            "titulo": "Tu web aparece como «No seguro»",
            "explicacion": "No usa conexión cifrada (https). El navegador muestra un aviso de «No es seguro» junto a la dirección, y eso espanta a cualquiera que vaya a dejar sus datos.",
            "accion": "Activa el certificado SSL. La mayoría de alojamientos lo incluyen gratis.",
        },
        "mejorable": {
            "titulo": "La versión antigua de tu dirección no lleva a la segura",
            "explicacion": "Quien entre escribiendo http:// en vez de https:// se queda en una versión sin cifrar.",
            "accion": "Configura una redirección automática de http a https.",
        },
        "bien": {
            "titulo": "La conexión es segura (https)",
            "explicacion": "El navegador muestra el candado y los datos viajan cifrados.",
            "accion": "Nada que hacer.",
        },
    },
    "leg_aviso": {
        "cat": "legal", "peso": 2,
        "mal": {
            "titulo": "No hemos encontrado el aviso legal",
            "explicacion": "En la portada no hay ningún enlace a un aviso legal. Si la web es de un negocio, la ley española (LSSI) obliga a identificar al titular: nombre o razón social, NIF, domicilio y contacto.",
            "accion": "Añade una página de aviso legal y enlázala en el pie. Si ya existe, comprueba que el enlace se ve.",
        },
        "bien": {
            "titulo": "Hay enlace al aviso legal",
            "explicacion": "La portada enlaza a un aviso legal o a unas condiciones.",
            "accion": "Comprueba que los datos del titular están completos y al día.",
        },
    },
    "leg_privacidad": {
        "cat": "legal", "peso": 2,
        "mal": {
            "titulo": "No hemos encontrado la política de privacidad",
            "explicacion": "Si la web recoge datos (un formulario de contacto ya cuenta), el RGPD obliga a explicar qué se hace con ellos. En la portada no hay ningún enlace.",
            "accion": "Añade una política de privacidad y enlázala en el pie y junto a cada formulario.",
        },
        "bien": {
            "titulo": "Hay enlace a la política de privacidad",
            "explicacion": "La portada enlaza a la política de privacidad.",
            "accion": "Comprueba que menciona todos los formularios y herramientas que usas.",
        },
    },
    "leg_cookies": {
        "cat": "legal", "peso": 3,
        "mal": {
            "titulo": "Usas herramientas de seguimiento y no vemos aviso de cookies",
            "explicacion": "Hemos detectado {rastreadores} y ninguno de los sistemas habituales de consentimiento. Estas herramientas necesitan el permiso del visitante antes de activarse; no pedirlo es uno de los motivos de sanción más frecuentes.",
            "accion": "Instala un gestor de consentimiento que bloquee estas herramientas hasta que el visitante acepte.",
        },
        "mejorable": {
            "titulo": "Tienes aviso de cookies; conviene comprobar que bloquea de verdad",
            "explicacion": "Hemos detectado {rastreadores} y un sistema de consentimiento. Desde fuera no podemos confirmar que las herramientas esperen al «Aceptar»: es un fallo muy común que el banner sea solo decorativo.",
            "accion": "Abre la web en una ventana de incógnito y comprueba que nada se activa antes de aceptar.",
        },
        "bien": {
            "titulo": "No hemos detectado herramientas de seguimiento",
            "explicacion": "En la portada no aparecen las herramientas de analítica o publicidad más habituales, así que no hace falta pedir consentimiento por ellas.",
            "accion": "Si instalas analítica o píxeles de publicidad, recuerda añadir el aviso.",
        },
    },
    # ---------------- Confianza ----------------
    "con_contacto": {
        "cat": "confianza", "peso": 3,
        "mal": {
            "titulo": "No hay forma rápida de contactar desde la portada",
            "explicacion": "No hemos encontrado teléfono, email ni WhatsApp en la portada. Quien llega con prisa y no ve cómo contactar, se va a otra web.",
            "accion": "Pon el teléfono y un botón de contacto bien visibles arriba y en el pie.",
        },
        "mejorable": {
            "titulo": "El teléfono no se puede pulsar para llamar",
            "explicacion": "Hay un teléfono escrito, pero desde el móvil no se puede tocar para llamar: hay que copiarlo a mano. Es un cambio de un minuto que da llamadas.",
            "accion": "Convierte el número en un enlace de llamada (tel:).",
        },
        "bien": {
            "titulo": "Es fácil contactar desde la portada",
            "explicacion": "Hay formas directas de contacto ({medios}).",
            "accion": "Nada que hacer.",
        },
    },
    "con_favicon": {
        "cat": "confianza", "peso": 1,
        "mejorable": {
            "titulo": "Falta el icono de la pestaña",
            "explicacion": "Tu web no tiene el pequeño logo que aparece en la pestaña del navegador y en los resultados de Google en el móvil. Es un detalle, pero sin él la web parece a medio hacer.",
            "accion": "Sube tu logo como icono del sitio (favicon).",
        },
        "bien": {
            "titulo": "Tienes icono en la pestaña",
            "explicacion": "Tu logo aparece en la pestaña del navegador.",
            "accion": "Nada que hacer.",
        },
    },
}
