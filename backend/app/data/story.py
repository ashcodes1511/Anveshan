"""
In-memory case store.
"""

import uuid
from datetime import datetime
from typing import Optional

_CASES: list[dict] = []
_EVENTS: list[dict] = []


# -----------------------------
# Event History Storage
# -----------------------------

def add_event(event: dict):
    _EVENTS.append(event)


def get_user_events(user_id: str, limit: int = 20):
    events = [
        e for e in _EVENTS
        if e.get("user_id") == user_id
    ]

    events.sort(
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )

    return events[:limit]


# -----------------------------
# Case Queue
# -----------------------------

def add_case(event: dict, risk_response: dict) -> dict:

    case = {
        "id": str(uuid.uuid4())[:8],
        "created_at": datetime.utcnow().isoformat(),
        "event": event,
        "risk": risk_response,
        "decision": None  # None | FROZEN | ALLOWED
    }

    _CASES.insert(0, case)

    return case


def list_cases(limit: int = 50) -> list[dict]:
    return _CASES[:limit]


def get_case(case_id: str) -> Optional[dict]:
    return next(
        (c for c in _CASES if c["id"] == case_id),
        None
    )


def set_decision(
    case_id: str,
    decision: str
) -> Optional[dict]:

    case = get_case(case_id)

    if case:
        case["decision"] = decision

    return case


def stats() -> dict:

    total = len(_CASES)

    high = sum(
        1 for c in _CASES
        if c["risk"]["risk_level"] == "HIGH"
    )

    frozen = sum(
        1 for c in _CASES
        if c["decision"] == "FROZEN"
    )

    return {
        "total_cases": total,
        "high_risk": high,
        "frozen": frozen
    }