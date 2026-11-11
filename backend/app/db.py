from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator, Optional

from .config import ajustes

ESQUEMA = """
CREATE TABLE IF NOT EXISTS audits (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    status TEXT NOT NULL,            -- pendiente | listo | error
    source TEXT NOT NULL,            -- web (visitante) | envio (lo generaste tú para enviarlo)
    sector TEXT,
    batch TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT,
    score INTEGER,
    result_json TEXT,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_audits_url ON audits(url, created_at);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    session_id TEXT NOT NULL,
    audit_id TEXT,
    name TEXT NOT NULL,
    props_json TEXT NOT NULL DEFAULT '{}',
    path TEXT,
    referrer TEXT,
    utm_source TEXT,
    device TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_audit ON events(audit_id);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    audit_id TEXT,
    session_id TEXT,
    door TEXT NOT NULL,
    email TEXT NOT NULL,
    consent_at TEXT NOT NULL
);
"""


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def conexion() -> Iterator[sqlite3.Connection]:
    ajustes.database_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ajustes.database_path, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA journal_mode=WAL")
        yield con
        con.commit()
    finally:
        con.close()


def iniciar() -> None:
    with conexion() as con:
        con.executescript(ESQUEMA)


# ---------- informes ----------

def crear_audit(audit_id: str, url: str, domain: str, source: str,
                sector: Optional[str], batch: Optional[str]) -> None:
    with conexion() as con:
        con.execute(
            "INSERT INTO audits (id, url, domain, status, source, sector, batch, created_at) "
            "VALUES (?, ?, ?, 'pendiente', ?, ?, ?, ?)",
            (audit_id, url, domain, source, sector, batch, ahora()),
        )


def guardar_resultado(audit_id: str, resultado: dict[str, Any]) -> None:
    with conexion() as con:
        con.execute(
            "UPDATE audits SET status='listo', finished_at=?, score=?, result_json=?, error=NULL WHERE id=?",
            (ahora(), resultado.get("puntuacion"), json.dumps(resultado, ensure_ascii=False), audit_id),
        )


def guardar_error(audit_id: str, mensaje: str) -> None:
    with conexion() as con:
        con.execute(
            "UPDATE audits SET status='error', finished_at=?, error=? WHERE id=?",
            (ahora(), mensaje, audit_id),
        )


def leer_audit(audit_id: str) -> Optional[dict[str, Any]]:
    with conexion() as con:
        fila = con.execute("SELECT * FROM audits WHERE id=?", (audit_id,)).fetchone()
    return dict(fila) if fila else None


def buscar_reciente(url: str, horas: int) -> Optional[str]:
    """Devuelve el id de un informe reciente de la misma URL hecho por un visitante."""
    limite = (datetime.now(timezone.utc) - timedelta(hours=horas)).isoformat(timespec="seconds")
    with conexion() as con:
        fila = con.execute(
            "SELECT id FROM audits WHERE url=? AND source='web' AND status!='error' AND created_at>=? "
            "ORDER BY created_at DESC LIMIT 1",
            (url, limite),
        ).fetchone()
    return fila["id"] if fila else None


# ---------- eventos y contactos ----------

def guardar_evento(session_id: str, name: str, audit_id: Optional[str], props: dict[str, Any],
                   path: Optional[str], referrer: Optional[str], utm_source: Optional[str],
                   device: str) -> None:
    with conexion() as con:
        con.execute(
            "INSERT INTO events (ts, session_id, audit_id, name, props_json, path, referrer, utm_source, device) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ahora(), session_id, audit_id, name, json.dumps(props, ensure_ascii=False),
             path, referrer, utm_source, device),
        )


def guardar_lead(audit_id: Optional[str], session_id: Optional[str], door: str, email: str) -> None:
    momento = ahora()
    with conexion() as con:
        con.execute(
            "INSERT INTO leads (ts, audit_id, session_id, door, email, consent_at) VALUES (?, ?, ?, ?, ?, ?)",
            (momento, audit_id, session_id, door, email, momento),
        )


def todo_para_estadisticas() -> tuple[list[dict], list[dict], list[dict]]:
    with conexion() as con:
        audits = [dict(f) for f in con.execute(
            "SELECT id, url, domain, status, source, sector, batch, created_at, score FROM audits "
            "ORDER BY created_at DESC LIMIT 5000")]
        events = [dict(f) for f in con.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT 100000")]
        leads = [dict(f) for f in con.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 5000")]
    return audits, events, leads
