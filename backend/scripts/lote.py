"""Genera informes por lotes para enviarlos a negocios.

Uso (con el backend en marcha):
    python scripts/lote.py ../lotes/ejemplo.csv --lote clinicas-1

El CSV de entrada tiene dos columnas: url,sector
Escribe ../lotes/<lote>-resultado.csv con el enlace de cada informe.
Los informes creados así quedan marcados como «envio», con su sector y su lote,
para que el panel separe el embudo por sector.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import ajustes  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv_entrada", type=Path)
    p.add_argument("--lote", required=True, help="Nombre del lote, por ejemplo clinicas-1")
    p.add_argument("--api", default="http://127.0.0.1:8000")
    args = p.parse_args()

    cabeceras = {"X-Admin-Token": ajustes.admin_token}
    salida = args.csv_entrada.parent / f"{args.lote}-resultado.csv"
    with args.csv_entrada.open(newline="", encoding="utf-8") as f:
        filas = [fila for fila in csv.DictReader(f) if (fila.get("url") or "").strip()]

    resultados = []
    with httpx.Client(base_url=args.api, headers=cabeceras, timeout=30) as api:
        for n, fila in enumerate(filas, 1):
            url, sector = fila["url"].strip(), (fila.get("sector") or "").strip() or None
            r = api.post("/api/audits", json={"url": url, "sector": sector, "batch": args.lote})
            if r.status_code != 200:
                print(f"[{n}/{len(filas)}] {url}: rechazada ({r.json().get('detail')})")
                resultados.append({"url": url, "sector": sector, "estado": "rechazada", "nota": "", "enlace": ""})
                continue
            audit_id = r.json()["id"]
            estado, nota = "pendiente", ""
            for _ in range(80):  # hasta ~4 minutos
                time.sleep(3)
                datos = api.get(f"/api/audits/{audit_id}").json()
                estado = datos["status"]
                if estado != "pendiente":
                    nota = (datos.get("result") or {}).get("puntuacion", "")
                    break
            enlace = f"{ajustes.public_base_url}/informe/{audit_id}" if estado == "listo" else ""
            print(f"[{n}/{len(filas)}] {url}: {estado} {nota}")
            resultados.append({"url": url, "sector": sector, "estado": estado, "nota": nota, "enlace": enlace})

    with salida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["url", "sector", "estado", "nota", "enlace"])
        w.writeheader()
        w.writerows(resultados)
    print(f"Hecho: {salida}")


if __name__ == "__main__":
    main()
