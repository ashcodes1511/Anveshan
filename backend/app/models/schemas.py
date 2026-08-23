"""
Data schemas for SwapShield.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Event(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    event_type: str = Field(..., description="'login' or 'transaction'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    device_id: Optional[str] = Field(None, description="Device fingerprint hash")
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    sim_change_flag: bool = Field(False, description="True if a SIM-change was reported recently")
    sim_change_minutes_ago: Optional[int] = Field(None, description="Minutes since last SIM-change")

    transaction_amount: Optional[float] = Field(None, description="Amount, only for transactions")


class SignalBreakdown(BaseModel):
    signal: str
    triggered: bool
    points: int
    reason: str


class RiskResponse(BaseModel):
    user_id: str
    event_type: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str
    signals: list[SignalBreakdown]
    explanation: str
    action: str