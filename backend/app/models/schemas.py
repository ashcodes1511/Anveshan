"""
Data schemas for SwapShield.

An "event" represents a single login or transaction attempt that we
want to score for fraud risk.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Event(BaseModel):
    """A single login / transaction event submitted for scoring."""

    user_id: str = Field(..., description="Unique identifier for the user")
    event_type: str = Field(..., description="'login' or 'transaction'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    device_id: Optional[str] = Field(None, description="Device fingerprint hash")
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    sim_change_flag: bool = Field(
        False, description="True if a SIM-change was reported for this user recently"
    )
    sim_change_minutes_ago: Optional[int] = Field(
        None, description="Minutes since the last known SIM-change event"
    )

    transaction_amount: Optional[float] = Field(
        None, description="Amount involved, only set for event_type='transaction'"
    )


class SignalBreakdown(BaseModel):
    """One contributing signal to the overall risk score."""

    signal: str
    triggered: bool
    points: int
    reason: str


class RiskResponse(BaseModel):
    """Output of the scoring engine for a given event."""

    user_id: str
    event_type: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str  # LOW / MEDIUM / HIGH
    signals: list[SignalBreakdown]
    explanation: str
    action: str  # ALLOW / REVIEW / FREEZE
