#!/usr/bin/env bash
# Copia diaria de la base de datos (emails con consentimiento y todo el registro de comportamiento).
# Usa la API de copia de SQLite, que es segura con el backend escribiendo. Guarda 30 días.
# ponytail: la copia queda en el mismo disco; protege de borrados y corrupción, no de perder el servidor.
set -euo pipefail
origen="$(dirname "$0")/../backend/data/auditoria.db"
destino="$HOME/backups/auditoria-web"
[ -f "$origen" ] || exit 0
mkdir -p "$destino" && chmod 700 "$destino"
python3 - "$origen" "$destino/auditoria-$(date +%F).db" <<'PY'
import sqlite3, sys
with sqlite3.connect(sys.argv[1]) as o, sqlite3.connect(sys.argv[2]) as d:
    o.backup(d)
PY
find "$destino" -name 'auditoria-*.db' -mtime +30 -delete
