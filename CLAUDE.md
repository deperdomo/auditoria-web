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
- **Sin IA en el análisis.** Las comprobaciones son reglas fijas y los textos salen de plantillas. Es una decisión
  de coste y de fiabilidad (la misma web debe dar siempre el mismo resultado). Si algún día se añade un modelo
  de lenguaje, solo en el informe de pago, nunca en la parte gratuita.
- **Coste cero.** No añadir servicios de pago ni dependencias que obliguen a ello sin consultarlo.
- **Honestidad en el informe.** Lo que no se puede comprobar desde fuera se dice con cautela («no hemos
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
navegador ──> frontend Next.js (puerto 3000) ──/api/*──> backend FastAPI (127.0.0.1:8000) ──> SQLite
```

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
| `components/Ofertas.tsx` + `lib/ofertas.ts` | Las tres puertas falsas y la ventana del email |
| `app/admin/page.tsx` + `components/Panel.tsx` | Panel de comportamiento |
| `app/privacidad/page.tsx` | Texto de privacidad, con huecos por completar |
| `lib/track.ts` | Envío de eventos al backend y, si está configurado, a Umami |

### Seguimiento

- Sin cookies y sin guardar la IP. El identificador de sesión vive solo en memoria (se pierde al recargar).
  Es deliberado: una herramienta que señala fallos de cookies no puede tener los suyos.
- La lista de eventos está en el `README.md`. `trackUnaVez` evita duplicados.
- Las visitas del propio Deivi se excluyen: entrar en `/admin` marca el navegador, o `?notrack=1` en cualquier
  página (`?notrack=0` lo deshace).
- Umami es opcional y aún no está instalado. La fuente de verdad es la tabla `events`.

### Las tres puertas falsas

`pdf` (19 €, pago único), `vigilancia` (9 €/mes) y `arreglo` (presupuesto). Los precios son **provisionales**,
puestos sin consultar; Deivi tiene que confirmarlos. La ventana dice claramente que el servicio aún no está
disponible y pide el email con casilla de consentimiento.

## Estado actual

Hecho y comprobado:

- Los 4 tests del backend pasan (`cd backend && python -m pytest`).
- El frontend compila (`npm run build`).
- El flujo completo a través del frontend funciona con un informe de prueba insertado a mano: leer informe,
  registrar evento, guardar email, estadísticas.

**Sin comprobar todavía:**

- **Ningún análisis contra una web real.** El entorno donde se escribió no resolvía dominios externos. Es lo
  primero que hay que probar: pasar varias webs conocidas y revisar que los hallazgos son ciertos.
- La llamada real a PageSpeed (los nombres de las métricas se tomaron de la API v5; verificar que llegan).
- El aspecto en un navegador. El CSS se escribió sin verlo renderizado.

## Pendiente, por orden

1. Probar en local con webs reales y corregir falsos positivos y textos que suenen mal.
2. Conseguir la clave de PageSpeed y ponerla en `backend/.env`.
3. Confirmar precios de las ofertas (`frontend/lib/ofertas.ts`).
4. Completar los datos del titular en `frontend/app/privacidad/page.tsx`.
5. Desplegar en el servidor de Oracle (ver abajo).
6. Instalar Umami en el mismo servidor (opcional).
7. Primera tanda de envíos.

Ideas aparcadas, no empezar sin consultarlo:

- Comprobación real de cookies con Playwright (abrir la web en un navegador sin interfaz y ver qué se carga
  antes de aceptar). Ahora es una heurística sobre los scripts del HTML.
- Analizar más páginas además de la portada.
- Generar el PDF de pago.
- Capa de redacción con un modelo de lenguaje, solo en el informe de pago.

## Despliegue en el servidor de Oracle

Decisión tomada: **todo en el servidor Ubuntu de Oracle Cloud, no en Vercel**. Motivos: el backend necesita
disco persistente (SQLite) y tareas en segundo plano, y el plan gratuito de Vercel no admite uso comercial.

Diseño previsto, **aún sin hacer**:

1. Un subdominio de `deiviperdomo.dev` con un registro A a la IP del servidor.
2. Caddy delante con HTTPS automático, reenviando al frontend en el puerto 3000. Debe añadir `X-Forwarded-For`
   (Caddy lo hace por defecto).
3. Dos servicios de systemd: `uvicorn app.main:app --host 127.0.0.1 --port 8000` y `next start`.
4. Un script de despliegue: `git pull`, instalar dependencias, `npm run build`, reiniciar los servicios.
5. Copia diaria del archivo SQLite (contiene los emails y todo el registro de comportamiento).
6. Abrir los puertos 80 y 443 tanto en la lista de seguridad de Oracle como en el cortafuegos de la instancia.

No se conoce el tamaño de la instancia. Si tiene 1 GB de memoria, `next build` puede necesitar swap.

En el servidor, `backend/.env` necesita: `ADMIN_TOKEN` largo y aleatorio, `PAGESPEED_API_KEY`,
`TRUST_PROXY=true` y `PUBLIC_BASE_URL` con el dominio público.

## Detalles que conviene saber antes de tocar

- **`BACKEND_URL` se fija al compilar** el frontend, no al arrancarlo. Si cambia, hay que volver a compilar.
- **IP del visitante:** con `TRUST_PROXY=true` se toma la *última* IP de `X-Forwarded-For`, la que añade el
  proxy propio; las anteriores las puede falsificar el visitante. Si algún día se pone Cloudflare delante, esto
  hay que cambiarlo (la última sería la de Cloudflare). Sin proxy delante, Next no añade la cabecera y todas las
  visitas cuentan como `127.0.0.1`: en local, subir `RATE_LIMIT_PER_HOUR`.
- **Límite por IP en memoria:** se reinicia con el backend y no funciona con varios procesos. Arrancar
  `uvicorn` con un solo worker.
- **SSRF:** el servidor descarga URLs que escribe cualquiera. `security.py` rechaza IPs literales, puertos que
  no sean 80/443 y cualquier host que resuelva a una dirección no pública, y valida cada redirección. No
  sustituir `descargar()` por una llamada directa a `httpx` con redirecciones automáticas.
- **`ADMIN_TOKEN`:** si está vacío o vale `cambia-esto`, el panel y el modo lote quedan desactivados.
- **Caché:** una misma URL pedida por un visitante en menos de `CACHE_HOURS` devuelve el informe existente.
- **RGPD:** la tabla `leads` contiene emails con su fecha de consentimiento. No exportarla ni subirla al
  repositorio; `backend/data/*.db` está en `.gitignore`.
- **Python:** el código es compatible con 3.10 o superior.
- **Aviso de pytest** sobre `httpx` y `starlette.testclient`: es una advertencia de obsolescencia, no un fallo.
