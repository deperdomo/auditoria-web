# Auditoría web

Herramienta que analiza la web de un negocio y devuelve un informe en castellano llano.
Es un experimento: el objetivo es **medir si alguien la usa y si pagaría**, antes de construir nada de pago.

- `backend/` — FastAPI. Analiza la web con reglas fijas (sin IA) y guarda todo en SQLite.
- `frontend/` — Next.js. Portada, informe compartible, tres ofertas de prueba y panel `/admin`.
- `lotes/` — CSV de entrada y salida para generar informes en lote y enviarlos.

## Arrancar en local (Windows)

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # y edita ADMIN_TOKEN y PAGESPEED_API_KEY
uvicorn app.main:app --reload --port 8000
```

Frontend (en otra terminal):

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Abre http://localhost:3000. El panel está en http://localhost:3000/admin (pide el `ADMIN_TOKEN`).

Tests del backend: `cd backend` y `python -m pytest`.

## Clave de PageSpeed

Sin `PAGESPEED_API_KEY` todo funciona menos la medición de velocidad. Para obtenerla: Google Cloud Console >
crear proyecto > APIs y servicios > habilitar «PageSpeed Insights API» > Credenciales > crear clave de API.
Es gratuita.

## Qué se registra de cada visitante

Sin cookies y sin guardar la IP. Cada acción se guarda en la tabla `events` con un identificador de sesión
que solo vive en memoria:

| Evento | Cuándo |
|---|---|
| `home_view`, `url_focus`, `url_submit`, `url_error` | Portada: entra, pincha en la caja, envía, falla |
| `report_view`, `report_ready`, `report_error` | Abre un informe; termina de cargarse (con segundos de espera y nota) |
| `scroll_depth` | Baja al 25, 50, 75 y 100 % del informe |
| `engaged` | Lleva 15, 30, 60, 120 y 300 s con el informe a la vista |
| `finding_open` | Despliega «Qué hacer» de un problema |
| `door_view`, `door_click` | Llega a las ofertas; pulsa una (con cuál y a qué precio) |
| `lead_submit`, `lead_modal_close` | Deja el email; cierra la ventana sin dejarlo |
| `copy_link`, `new_audit_click` | Copia el enlace; vuelve a analizar otra web |

**Tus visitas no cuentan** en el navegador desde el que hayas entrado en `/admin`, o en cualquiera
donde abras una página con `?notrack=1` (se deshace con `?notrack=0`).

Umami es opcional: rellena las dos variables `NEXT_PUBLIC_UMAMI_*` del frontend y recibirá los mismos eventos.

## Generar informes para enviar

Con el backend en marcha:

```powershell
cd backend
python scripts/lote.py ..\lotes\clinicas.csv --lote clinicas-1
```

El CSV de entrada tiene dos columnas, `url,sector`. La salida (`lotes/clinicas-1-resultado.csv`) trae el enlace
de cada informe. El panel separa el embudo por sector.

## Antes de publicar

- Completa los datos entre corchetes de `frontend/app/privacidad/page.tsx`.
- Revisa precios y textos de las ofertas en `frontend/lib/ofertas.ts`.
- Revisa el tono de los textos del informe en `backend/app/plantillas.py`.
- En el servidor: el backend escuchando solo en `127.0.0.1`, y nginx o Caddy delante del frontend con HTTPS
  (el proxy debe añadir `X-Forwarded-For` para que el límite por IP funcione).
- `BACKEND_URL` se fija al compilar el frontend (`npm run build`), no al arrancarlo.

## Limitaciones conocidas

- Solo se analiza la portada.
- El aviso legal, la privacidad y el contacto se buscan en el HTML inicial; si la web los pinta con JavaScript,
  pueden salir como «no encontrados».
- Las cookies se detectan por los scripts presentes, sin abrir un navegador real. No confirma si el banner
  bloquea de verdad; por eso el informe lo dice como «conviene comprobar».
- El límite por IP vive en memoria: se reinicia con el backend y no sirve con varios procesos.
