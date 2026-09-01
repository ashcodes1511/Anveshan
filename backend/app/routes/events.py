from fastapi import APIRouter, HTTPException

from app.models.schemas import Event, RiskResponse
from app.engine.scoring import score_event
from app.data import store, generator

router = APIRouter()


@router.post("/score-event", response_model=RiskResponse)
def score_event_endpoint(event: Event):

    result = score_event(event)

    store.add_event(event.model_dump(mode="json"))

    store.add_case(
        event.model_dump(mode="json"),
        result.model_dump()
    )

    return result


@router.get("/history/{user_id}")
def history(user_id: str):
    return store.get_user_events(user_id)


@router.get("/cases")
def list_cases(limit: int = 50):
    return store.list_cases(limit)


@router.post("/cases/{case_id}/decision")
def decide_case(case_id: str, decision: str):

    if decision not in ("FROZEN", "ALLOWED"):
        raise HTTPException(
            status_code=400,
            detail="decision must be FROZEN or ALLOWED"
        )

    case = store.set_decision(case_id, decision)

    if not case:
        raise HTTPException(
            status_code=404,
            detail="case not found"
        )

    return case


@router.get("/stats")
def get_stats():
    return store.stats()


@router.post("/reset")
def reset_demo():
    store.clear_all()
    return {"message": "Demo data cleared"}

@router.post("/reset")
def reset_demo():
    import sqlite3

    conn = sqlite3.connect("anveshan.db")
    conn.execute("DELETE FROM cases")
    conn.execute("DELETE FROM events")
    conn.commit()
    conn.close()

    return {"message": "Demo data cleared"}
@router.post("/simulate")
def simulate_event(kind: str = "random"):

    import random

    if kind == "random":
        kind = random.choice(
            ["normal", "normal", "normal", "attack"]
        )

    if kind == "attack":
        raw = generator.generate_random_attack_event()
    else:
        raw = generator.generate_random_normal_event()

    event = Event(**raw)

    result = score_event(event)

    store.add_event(
        event.model_dump(mode="json")
    )

    store.add_case(
        event.model_dump(mode="json"),
        result.model_dump()
    )

    return result
    