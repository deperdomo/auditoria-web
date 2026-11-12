# Auditoría web — contexto del proyecto

Este archivo recoge el contexto y las decisiones tomadas hasta el 11-11-2026, para continuar el desarrollo
desde otra sesión. El `README.md` explica cómo arrancar y usar el proyecto; aquí está el porqué y lo pendiente.

Repositorio: https://github.com/deperdomo/auditoria-web — rama `main`.

## Normas de trabajo

- **Commits:** en inglés, de una sola línea, sin coautor ni líneas de atribución. No hacer commits para cambios
  pequeños; agrupar el trabajo en commits con sentido.
- **Idioma:** todo lo que ve el usuario final va en castellano de España. El código también usa nombres en
  castellano (funciones, variables, tablas de texto); mantener esa convención. Los nombres de eventos y de
  columnas de la base de datos están en inglés (`report_view`, `audits`...): no renombrarlos.
- **Tono:** lo que hace la herramienta va en impersonal («no se ha encontrado», «se ha detectado», «no se ha
  podido abrir»): quien no encuentra el aviso legal es la herramienta, no Deivi. Lo que hace Deivi (ofertas,
  guardar el email, privacidad) va en primera persona del singular («déjame tu email y te aviso»). Nunca
  «nosotros». Al visitante se le trata de tú.
- **Sin IA en el análisis.** Las comprobaciones son reglas fijas y los textos salen de plantillas. Es una decisión
  de coste y de fiabilidad (la misma web debe dar siempre el mismo resultado). Si algún día se añade un modelo
  de lenguaje, solo en el informe de pago, nunca en la parte gratuita.
- **Coste cero.** No añadir servicios de pago ni dependencias que obliguen a ello sin consultarlo.
- **Honestidad en el informe.** Lo que no se puede comprobar desde fuera se dice con cautela («no se ha
  encontrado», «conviene comprobar»). Nada de cifras inventadas ni de alarmismo.

## Qué es y para qué

Experimento de producto propio de Deivi (desarrollador freelance en Madrid). La herramienta analiza la web de
cualquier negocio y devuelve un informe en castellano llano, pensado para el dueño del negocio y no para gente
de marketing.

**El objetivo de esta fase no es vender, es medir**: saber si alguien usa el informe y si pagaría, antes de
construir nada de pago. Por eso el seguimiento del comportamiento es una parte central del producto, no un extra.

Si el producto no vende pero algunos negocios piden que les arreglen la web, también es un buen resultado:
sirve como generador de clientes freelance.

### Por qué este enfoque

- Las auditorías web genéricas gratuitas ya existen y son buenas (Semrush, Sitechecker, SE Ranking, Ahrefs).
  SEOptimer cobra 29-59 $/mes por informes en PDF, pero orientado a agencias.
- La diferencia buscada está en **a quién se le habla**: impacto en el negocio en vez de siglas, más las
  comprobaciones que las herramientas extranjeras no hacen (cookies, aviso legal, privacidad según la normativa
  española).
- El producto acepta cualquier web, pero la **validación se hace por sectores** para que los datos digan cuál
  responde.

## Plan de validación

1. Generar unos 100 informes de negocios reales, en cuatro tandas de 25 por sector (por ejemplo clínicas,
   restaurantes, tiendas online pequeñas, despachos profesionales), con `backend/scripts/lote.py`.
2. Hacerles llegar el enlace por su formulario de contacto, LinkedIn o teléfono. **No usar email comercial en
   frío**: la LSSI lo restringe sin consentimiento previo.
3. Mirar el panel `/admin`, que separa el embudo por sector.

Umbrales orientativos:

- **Seguir:** de 100 informes enviados, al menos 15 abiertos, 5 clics en una oferta de pago y 1-2 emails o
  peticiones de presupuesto.
- **Parar o cambiar de sector:** menos de 2 clics en ofertas de pago tras los 100 envíos.
- Fijarse en qué oferta gana. Si casi todo son clics en «que lo arregle un profesional», no hay producto sino
  un generador de clientes.

Siguiente paso de validación, aún sin hacer: poner un enlace de pago real en la oferta del PDF a precio de
lanzamiento y entregar el informe a mano. Un pago real vale más que muchos emails.

## Arquitectura

```
navegador ──> Cloudflare ──túnel──> frontend Next.js (127.0.0.1:3000) ──/api/*──> backend FastAPI (127.0.0.1:8000) ──> SQLite
```

En producción: https://auditoria.deiviperdomo.dev. En local no hay Cloudflare ni túnel; el resto es igual.

- El navegador solo habla con el frontend. `frontend/next.config.ts` reenvía `/api/*` al backend, así que no
  hay CORS y el backend no se expone a internet.
- El análisis se lanza como tarea en segundo plano de FastAPI; el frontend consulta el informe cada 2,5 s
  hasta que termina.

### Backend (`backend/app/`)

| Archivo | Qué hace |
|---|---|
| `main.py` | Endpoints, validación, límites por IP, comprobación del token de administración |
| `audit.py` | Orquesta un análisis: recoge datos, mide velocidad, construye y guarda el informe |
| `checks/html_checks.py` | Descarga la portada y extrae hechos del HTML. `analizar_html` es pura y testeable |
| `checks/pagespeed.py` | Llama a la API de PageSpeed Insights (móvil). Sin clave devuelve `None` |
| `report.py` | Reglas: convierte los hechos en hallazgos (mal / mejorable / bien) y calcula las notas |
| `plantillas.py` | Todos los textos del informe y los pesos. Es el archivo a editar para cambiar el tono |
| `security.py` | Normalización de URL, protección SSRF, descarga con límite de tamaño, límite por IP |
| `db.py` | SQLite con `sqlite3` de la librería estándar. Tablas `audits`, `events`, `leads` |
| `stats.py` | Agregados para el panel, calculados en Python (no depende de JSON1 de SQLite) |
| `config.py` | Ajustes desde `backend/.env` |

Endpoints:

- `POST /api/audits` `{url, sector?, batch?}` — crea un análisis. Con la cabecera `X-Admin-Token` válida se
  marca como `envio`, acepta sector y lote, y no tiene límite ni caché. Sin ella es `web` (visitante).
- `GET /api/audits/{id}` — estado (`pendiente` / `listo` / `error`) y resultado.
- `POST /api/events` — registra una acción del visitante.
- `POST /api/leads` `{email, door, consent, audit_id?}` — guarda un email; exige `consent: true`.
- `GET /api/admin/stats` — datos del panel; exige `X-Admin-Token`.
- `GET /api/health`.

Para añadir una comprobación nueva: extraer el dato en `html_checks.py`, añadir la regla en `report.evaluar`,
y escribir sus textos y su peso en `plantillas.py`. Añadir un caso en `tests/test_basico.py`.

### Frontend (`frontend/`)

Next.js 16 (App Router), React 19, TypeScript, CSS plano en `app/globals.css` (sin Tailwind).

| Ruta / archivo | Qué es |
|---|---|
| `app/page.tsx` + `components/FormularioUrl.tsx` | Portada con la caja de URL |
| `app/informe/[id]/page.tsx` + `components/Informe.tsx` | Informe compartible; lleva `noindex` |
| `components/Ofertas.tsx` + `lib/ofertas.ts` | La oferta gratuita y la ventana del email |
| `app/admin/page.tsx` + `components/Panel.tsx` | Panel de comportamiento |
| `app/privacidad/page.tsx` | Texto de privacidad: nombre y email del titular, sin NIF ni domicilio |
| `lib/track.ts` | Envío de eventos al backend y, si está configurado, a Umami |

### Seguimiento

- Sin cookies y sin guardar la IP. El identificador de sesión vive solo en memoria (se pierde al recargar).
  Es deliberado: una herramienta que señala fallos de cookies no puede tener los suyos.
- La lista de eventos está en el `README.md`. `trackUnaVez` evita duplicados.
- Las visitas del propio Deivi se excluyen: entrar en `/admin` marca el navegador, o `?notrack=1` en cualquier
  página (`?notrack=0` lo deshace).
- **Cloudflare Web Analytics** cuenta visitas y páginas vistas de `auditoria.deiviperdomo.dev`. El fragmento
  está en `frontend/app/layout.tsx` y solo se carga en producción. No usa cookies y la página de privacidad lo
  menciona. No respeta `?notrack=1`: ahí las visitas de Deivi sí cuentan, y quien use bloqueador no aparece.
- Umami es opcional y aún no está instalado. La fuente de verdad del comportamiento es la tabla `events`.

### La oferta

Desde el 12-11-2026 hay **una sola oferta**, `gratis`: «Te arreglo los fallos gratis», limitada a 5 plazas al
mes, a cambio de opinión, permiso para enseñar el antes y el después, y recomendaciones. Sustituye a las tres
puertas falsas anteriores (`pdf` 19 €, `vigilancia` 9 €/mes, `arreglo`). Consecuencia asumida: **ya no se mide
si alguien pagaría**; los umbrales de «clics en ofertas de pago» del plan de validación dejan de aplicarse y
el dato a vigilar es cuántos trabajos gratis acaban en una recomendación (se lleva a mano, fuera de la web).

## Estado actual

Publicado en **https://auditoria.deiviperdomo.dev** desde el 11-11-2026 (ver «Despliegue»).

Hecho y comprobado:

- Los 6 tests del backend pasan (`cd backend && .venv/bin/python -m pytest`).
- **Análisis contra webs reales.** Se pasaron unas 15 webs españolas (restaurantes, clínicas, despachos, tiendas)
  revisando el HTML de cada hallazgo dudoso. Falsos positivos encontrados y corregidos:
  - `alt=""` es la forma correcta de marcar una imagen decorativa; solo cuenta la imagen sin atributo `alt`.
  - «Condiciones de uso», «información legal», `terms`, `/legal`... cuentan como aviso legal.
  - Más gestores de cookies reconocidos (módulo de Drupal, banner de Shopify, banners propios, Consent Mode).
  - **Portada hueca** (`poco_contenido`: sin enlaces, sin imágenes y casi sin texto): es una web que lo pinta todo
    con JavaScript. No se afirma que falten aviso legal, privacidad, contacto, titular ni aviso de cookies, y el
    informe lo explica (`contenido_dinamico`). Las categorías «Seguridad y textos legales» y «Contacto y confianza» salen
    sin nota («No se ha podido comprobar»): antes daban un 100 engañoso solo por HTTPS o favicon.
  - Solo un enlace a «Contacto», sin teléfono ni email pulsables: «mejorable» (`con_contacto_enlace`), no «mal».
  - Sin etiqueta de icono se comprueba `/favicon.ico`, que es lo que hacen los navegadores.
  - Webs que bloquean bots (401/403/429) y portadas de más de 5 MB: mensaje de error claro en vez de un informe
    a medias. No falsificar el `User-Agent` para saltarse el bloqueo.
- El flujo completo en producción: análisis, caché, eventos, emails con consentimiento, panel, redirección de
  `http://` a `https://`.
- **La llamada real a PageSpeed**, con la clave ya puesta: responde en unos 15 s y llegan todas las métricas
  que espera `pagespeed.interpretar`.
- El límite por IP a través de Cloudflare: seis peticiones con un `X-Forwarded-For` inventado y distinto cada vez
  acaban en 429.

**Sin comprobar todavía:**

- El aspecto en un navegador. Solo se ha comprobado que todas las clases usadas tienen regla en `globals.css`.
- El aviso de cookies cuando el banner se carga desde Tag Manager (visto en una tienda grande): sale como «no se ve
  aviso de cookies». El texto de «Qué hacer» ya avisa de esa posibilidad; la solución de verdad es la comprobación
  con Playwright, que sigue aparcada.

En la base de datos de producción quedan cinco análisis de prueba del 11-11-2026 (`example.com`, `example.org`,
`example.net`, `iana.org`, `wikipedia.org`, con `source='web'`). No tienen eventos ni emails asociados.

## Pendiente, por orden

1. Mirar el aspecto en el navegador (escritorio y móvil) y corregir lo que haga falta.
2. Antes de cada tanda, pasar 3 o 4 webs del sector y revisar a mano que los hallazgos son ciertos.
3. Instalar Umami en el mismo servidor (opcional).
4. Primera tanda de envíos.

Ideas aparcadas, no empezar sin consultarlo:

- Comprobación real de cookies con Playwright (abrir la web en un navegador sin interfaz y ver qué se carga
  antes de aceptar). Ahora es una heurística sobre los scripts del HTML.
- Analizar más páginas además de la portada.
- Generar el PDF de pago.
- Capa de redacción con un modelo de lenguaje, solo en el informe de pago.

## Despliegue en el servidor de Oracle

Todo corre en el servidor Ubuntu de Oracle Cloud (ARM, 4 núcleos, 24 GB), no en Vercel. Motivos: el backend
necesita disco persistente (SQLite) y tareas en segundo plano, y el plan gratuito de Vercel no admite uso comercial.

El repositorio está clonado en `/home/ubuntu/proyectos/auditoria-web` y **se sirve desde ahí mismo**.

- **Entrada: túnel de Cloudflare, no Caddy.** El plan inicial era Caddy con un registro A, pero el servidor tiene
  los puertos 80 y 443 cerrados y sus otros proyectos ya salen por `cloudflared`. El subdominio es una entrada más
  en `/etc/cloudflared/config.yml` (`auditoria.deiviperdomo.dev` → `http://localhost:3000`) y un CNAME creado con
  `cloudflared tunnel route dns`. Ese archivo lo comparten otros proyectos: copiarlo antes de tocarlo y validar
  con `cloudflared tunnel ingress validate`; reiniciar `cloudflared` los corta unos segundos a todos.
- **Servicios de systemd:** `auditoria-backend` (uvicorn, un solo proceso) y `auditoria-frontend` (`next start`).
  Los dos escuchan solo en `127.0.0.1`. Las unidades están en `deploy/` y copiadas en `/etc/systemd/system/`.
  Registros: `journalctl -u auditoria-backend -f`.
- **Desplegar cambios:** `deploy/desplegar.sh` (git pull, dependencias, tests, compilar, reiniciar, comprobar).
- **Copia diaria** de SQLite: `deploy/copia.sh` desde el cron del usuario `ubuntu` a las 03:15, en
  `~/backups/auditoria-web/`, 30 días. Está en el mismo disco: no protege de perder el servidor.
- **`backend/.env`** (no está en git): `ADMIN_TOKEN` aleatorio ya puesto, `TRUST_PROXY=true`, `PUBLIC_BASE_URL`
  con el dominio público y `PAGESPEED_API_KEY`.
- **Entorno de Python:** el servidor no tiene `python3-venv` y el índice de apt está desfasado. El `.venv` se creó
  con `python3 -m venv --without-pip .venv` y `get-pip.py`. No hace falta repetirlo salvo que se borre.

## Detalles que conviene saber antes de tocar

- **`BACKEND_URL` se fija al compilar** el frontend, no al arrancarlo. Si cambia, hay que volver a compilar.
- **IP del visitante:** con `TRUST_PROXY=true` se toma la *última* IP de `X-Forwarded-For`. Cloudflare añade ahí
  la IP real del visitante al final y Next reenvía la cabecera sin tocarla; las anteriores las puede falsificar
  el visitante. Esto solo es seguro porque Next escucha en `127.0.0.1` y el único camino de entrada es el túnel:
  si algún día se abre el puerto 3000 o se pone otro proxy delante, hay que revisarlo. En local, sin proxy, no
  llega la cabecera y todas las visitas cuentan como `127.0.0.1`: subir `RATE_LIMIT_PER_HOUR`.
- **Redirección a HTTPS:** la hace `next.config.ts` leyendo la cabecera `cf-visitor` de Cloudflare. En local no
  existe y no se redirige nada.
- **Límite por IP en memoria:** se reinicia con el backend y no funciona con varios procesos. Arrancar
  `uvicorn` con un solo worker.
- **SSRF:** el servidor descarga URLs que escribe cualquiera. `security.py` rechaza IPs literales, puertos que
  no sean 80/443 y cualquier host que resuelva a una dirección no pública, y valida cada redirección. No
  sustituir `descargar()` por una llamada directa a `httpx` con redirecciones automáticas.
- **`ADMIN_TOKEN`:** si está vacío o vale `cambia-esto`, el panel y el modo lote quedan desactivados.
- **Caché:** una misma URL pedida por un visitante en menos de `CACHE_HOURS` devuelve el informe existente.
- **RGPD:** la tabla `leads` contiene emails con su fecha de consentimiento. No exportarla ni subirla al
  repositorio; `backend/data/*.db` está en `.gitignore`.
- **Titular sin NIF ni domicilio:** la página de privacidad identifica a Deivi solo con nombre y email. Es una
  decisión suya (11-11-2026): no es autónomo y no quiere publicar su domicilio. Vale mientras no se cobre nada.
  **Antes de poner un enlace de pago real** hay que revisarlo: cobrar exige darse de alta, y la LSSI pide entonces
  nombre, NIF y domicilio en la web.
- **Python:** el código es compatible con 3.10 o superior.
- **Aviso de pytest** sobre `httpx` y `starlette.testclient`: es una advertencia de obsolescencia, no un fallo.
