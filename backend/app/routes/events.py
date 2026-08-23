from fastapi import APIRouter, HTTPException
from app.models.schemas import Event, RiskResponse
from app.engine.scoring import score_event
from app.data import store, generator

router = APIRouter()


@router.post("/score-event", response_model=RiskResponse)
def score_event_endpoint(event: Event):
    """Score a single event, save it as a case, and return the verdict."""
    result = score_event(event)
    store.add_case(event.model_dump(mode="json"), result.model_dump())
    return result


@router.get("/cases")
def list_cases(limit: int = 50):
    """Return the live case queue, newest first."""
    return store.list_cases(limit)


@router.post("/cases/{case_id}/decision")
def decide_case(case_id: str, decision: str):
    """Record an analyst decision: 'FROZEN' or 'ALLOWED'."""
    if decision not in ("FROZEN", "ALLOWED"):
        raise HTTPException(400, "decision must be FROZEN or ALLOWED")
    case = store.set_decision(case_id, decision)
    if not case:
        raise HTTPException(404, "case not found")
    return case


@router.get("/stats")
def get_stats():
    return store.stats()


@router.post("/simulate")
def simulate_event(kind: str = "random"):
    """
    Generate a synthetic event (normal or attack) and score it, so the
    live queue can be demoed without manually typing every case.
    kind: 'normal' | 'attack' | 'random'
    """
    import random
    if kind == "random":
        kind = random.choice(["normal", "normal", "normal", "attack"])  # attacks rarer

    if kind == "attack":
        raw = generator.generate_attack_sequence("demo_user", 12.9716, 77.5946)
    else:
        raw = generator.generate_normal_event("demo_user", 12.9716, 77.5946, "device_abc123")

    event = Event(**raw)
    result = score_event(event)
    store.add_case(event.model_dump(mode="json"), result.model_dump())
    return result