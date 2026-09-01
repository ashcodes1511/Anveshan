"""
SQLite-backed case store.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional

DB_PATH = "anveshan.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            event_json TEXT NOT NULL,
            risk_json TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            decision TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            raw_event TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_event(event: dict):
    conn = _get_conn()

    conn.execute(
        """
        INSERT INTO events
        (user_id, event_type, timestamp, raw_event)
        VALUES (?, ?, ?, ?)
        """,
        (
            event["user_id"],
            event["event_type"],
            str(event["timestamp"]),
            json.dumps(event)
        )
    )

    conn.commit()
    conn.close()


def get_user_events(user_id: str, limit: int = 20):
    conn = _get_conn()

    rows = conn.execute(
        """
        SELECT *
        FROM events
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def add_case(event: dict, risk_response: dict):
    case_id = str(uuid.uuid4())[:8]
    created_at = datetime.utcnow().isoformat()

    conn = _get_conn()

    conn.execute(
        """
        INSERT INTO cases
        (id, created_at, event_json, risk_json, risk_score, risk_level, decision)
        VALUES (?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            case_id,
            created_at,
            json.dumps(event),
            json.dumps(risk_response),
            risk_response["risk_score"],
            risk_response["risk_level"]
        )
    )

    conn.commit()
    conn.close()

    return {
        "id": case_id,
        "created_at": created_at,
        "event": event,
        "risk": risk_response,
        "decision": None
    }


def _row_to_case(row):
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "event": json.loads(row["event_json"]),
        "risk": json.loads(row["risk_json"]),
        "decision": row["decision"]
    }


def list_cases(limit: int = 50):
    conn = _get_conn()

    rows = conn.execute(
        "SELECT * FROM cases ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()

    conn.close()

    return [_row_to_case(r) for r in rows]


def get_case(case_id: str) -> Optional[dict]:
    conn = _get_conn()

    row = conn.execute(
        "SELECT * FROM cases WHERE id = ?",
        (case_id,)
    ).fetchone()

    conn.close()

    return _row_to_case(row) if row else None


def set_decision(case_id: str, decision: str):
    conn = _get_conn()

    conn.execute(
        "UPDATE cases SET decision = ? WHERE id = ?",
        (decision, case_id)
    )

    conn.commit()
    conn.close()

    return get_case(case_id)


def stats():
    conn = _get_conn()

    total = conn.execute(
        "SELECT COUNT(*) FROM cases"
    ).fetchone()[0]

    high = conn.execute(
        "SELECT COUNT(*) FROM cases WHERE risk_level='HIGH'"
    ).fetchone()[0]

    frozen = conn.execute(
        "SELECT COUNT(*) FROM cases WHERE decision='FROZEN'"
    ).fetchone()[0]

    conn.close()

    return {
        "total_cases": total,
        "high_risk": high,
        "frozen": frozen
    }


def clear_all():
    conn = _get_conn()

    conn.execute("DELETE FROM cases")
    conn.execute("DELETE FROM events")

    conn.commit()
    conn.close()


init_db()