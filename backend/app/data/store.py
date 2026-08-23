"""
In-memory case store.

Acts as a lightweight stand-in for a real database. Every scored event
gets appended here so the dashboard can show a live queue instead of
one-off single scores. Swap this for SQLite/Postgres later without
changing the API shape.
"""

import uuid
from datetime import datetime
from typing import Optional

_CASES: list[dict] = []


def add_case(event: dict, risk_response: dict) -> dict:
    case = {
        "id": str(uuid.uuid4())[:8],
        "created_at": datetime.utcnow().isoformat(),
        "event": event,
        "risk": risk_response,
        "decision": None,  # None | "FROZEN" | "ALLOWED"
    }
    _CASES.insert(0, case)  # newest first
    return case


def list_cases(limit: int = 50) -> list[dict]:
    return _CASES[:limit]


def get_case(case_id: str) -> Optional[dict]:
    return next((c for c in _CASES if c["id"] == case_id), None)


def set_decision(case_id: str, decision: str) -> Optional[dict]:
    case = get_case(case_id)
    if case:
        case["decision"] = decision
    return case


def stats() -> dict:
    total = len(_CASES)
    high = sum(1 for c in _CASES if c["risk"]["risk_level"] == "HIGH")
    frozen = sum(1 for c in _CASES if c["decision"] == "FROZEN")
    return {"total_cases": total, "high_risk": high, "frozen": frozen}