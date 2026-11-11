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

## En el servidor

Está publicado en https://auditoria.deiviperdomo.dev, en el servidor de Oracle, detrás de un túnel de Cloudflare.

```bash
deploy/desplegar.sh                            # actualizar con lo último de main
sudo systemctl restart auditoria-backend       # tras cambiar backend/.env
journalctl -u auditoria-backend -f             # registros (o auditoria-frontend)
```

La base de datos se copia cada noche en `~/backups/auditoria-web/` (`deploy/copia.sh`). Los detalles del
despliegue están en `CLAUDE.md`.

## Clave de PageSpeed

Sin `PAGESPEED_API_KEY` todo funciona menos la medición de velocidad. Es gratuita y no pide tarjeta:

1. Entra en https://console.cloud.google.com con tu cuenta de Google y crea un proyecto (o elige uno).
2. Menú > «APIs y servicios» > «Biblioteca», busca **PageSpeed Insights API** y pulsa «Habilitar».
3. «APIs y servicios» > «Credenciales» > «Crear credenciales» > «Clave de API».
4. En la clave, «Restricciones de API» > «Restringir clave» > marca solo PageSpeed Insights API.
5. Pégala en `backend/.env` (`PAGESPEED_API_KEY=...`) y reinicia el backend.

`/api/health` devuelve `"mide_velocidad": true` cuando la clave está cargada.

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

Además, Cloudflare Web Analytics cuenta visitas y páginas vistas (sin cookies; el fragmento está en
`frontend/app/layout.tsx` y solo se carga en producción). Ahí sí cuentan tus visitas.

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

- Revisa precios y textos de las ofertas en `frontend/lib/ofertas.ts`.
- Revisa el tono de los textos del informe en `backend/app/plantillas.py`.
- `BACKEND_URL` se fija al compilar el frontend (`npm run build`), no al arrancarlo.

## Limitaciones conocidas

- Solo se analiza la portada.
- Las webs que bloquean herramientas automáticas y las portadas de más de 5 MB no se analizan: se dice tal cual.
- Si la portada lo pinta todo con JavaScript, no se comprueban los textos legales ni el contacto, y el informe
  lo avisa.
- El aviso legal, la privacidad y el contacto se buscan en el HTML inicial; si la web los pinta con JavaScript,
  pueden salir como «no encontrados».
- Las cookies se detectan por los scripts presentes, sin abrir un navegador real. No confirma si el banner
  bloquea de verdad; por eso el informe lo dice como «conviene comprobar».
- El límite por IP vive en memoria: se reinicia con el backend y no sirve con varios procesos.
