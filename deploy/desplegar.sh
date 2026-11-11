#!/usr/bin/env bash
# Actualiza el servidor con lo último de main. Uso: deploy/desplegar.sh
set -euo pipefail
cd "$(dirname "$0")/.."

git pull --ff-only
backend/.venv/bin/pip install -q -r backend/requirements.txt
(cd backend && .venv/bin/python -m pytest -q)   # si un test falla, no se despliega
# ponytail: se compila sobre el .next en uso; unos segundos de posible error hasta el reinicio.
# Si llega a molestar, compilar en otra carpeta y cambiarla de golpe.
(cd frontend && npm ci --no-audit --no-fund && npm run build)
sudo systemctl restart auditoria-backend auditoria-frontend
curl -fsS --retry 15 --retry-connrefused --retry-delay 1 http://127.0.0.1:3000/api/health && echo " — desplegado"
