import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS orientation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL DEFAULT 'nouvelle',
            created_at TEXT NOT NULL,
            person_first_name TEXT NOT NULL,
            person_last_name TEXT NOT NULL,
            person_phone TEXT,
            person_email TEXT,
            person_birthdate TEXT,
            person_address TEXT,
            sender_name TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            sender_organization TEXT,
            sender_email TEXT,
            sender_message TEXT,
            modalite TEXT,
            diagnostic_data TEXT
        );

        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orientation_id INTEGER NOT NULL REFERENCES orientation(id),
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS history_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orientation_id INTEGER NOT NULL REFERENCES orientation(id),
            event_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def get_all_orientations(status_filter: list[str] | None = None) -> list[dict]:
    conn = get_db()
    if status_filter:
        placeholders = ",".join("?" for _ in status_filter)
        rows = conn.execute(
            f"SELECT * FROM orientation WHERE status IN ({placeholders}) ORDER BY created_at DESC",
            status_filter,
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM orientation ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_orientation(orientation_id: int) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM orientation WHERE id = ?", (orientation_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    if result["diagnostic_data"]:
        result["diagnostic_data"] = json.loads(result["diagnostic_data"])
    return result


def update_orientation_status(orientation_id: int, new_status: str):
    now = datetime.now().isoformat()
    conn = get_db()
    conn.execute(
        "UPDATE orientation SET status = ? WHERE id = ?",
        (new_status, orientation_id),
    )
    event_type = {"acceptee": "accepted", "refusee": "refused"}[new_status]
    conn.execute(
        "INSERT INTO history_event (orientation_id, event_type, created_at) VALUES (?, ?, ?)",
        (orientation_id, event_type, now),
    )
    conn.commit()
    conn.close()


def get_messages(orientation_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM message WHERE orientation_id = ? ORDER BY created_at DESC",
        (orientation_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_message(orientation_id: int, author_name: str, content: str):
    now = datetime.now().isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO message (orientation_id, author_name, content, created_at) VALUES (?, ?, ?, ?)",
        (orientation_id, author_name, content, now),
    )
    conn.commit()
    conn.close()


def get_history(orientation_id: int) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM history_event WHERE orientation_id = ? ORDER BY created_at ASC",
        (orientation_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
