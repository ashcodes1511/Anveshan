from fastapi import APIRouter
from app.models.schemas import Event, RiskResponse
from app.engine.scoring import score_event

router = APIRouter()


@router.post("/score-event", response_model=RiskResponse)
def score_event_endpoint(event: Event):
    """
    Score a single login/transaction event and return a risk score
    (0-100), risk level, per-signal explanation, and suggested action.
    """
    return score_event(event)
