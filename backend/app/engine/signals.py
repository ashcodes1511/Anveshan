"""
Time-since-last-activity signal.

Flags accounts that suddenly become active after a long dormant period -
a common pattern when an attacker gains access to an account the real
owner rarely uses (old/forgotten accounts are attractive targets).
"""

from datetime import datetime
from typing import Optional
from app.config import ACTIVITY_GAP_ANOMALY_MINUTES


def check_activity_gap(
    current_timestamp: datetime,
    last_event_timestamp: Optional[datetime],
) -> tuple[bool, str]:
    """
    Returns (triggered, reason).

    triggered = True if the gap since the user's last known activity
    is unusually large.
    """
    if last_event_timestamp is None:
        return False, "No prior activity on record to compare against"

    gap_minutes = (current_timestamp - last_event_timestamp).total_seconds() / 60

    if gap_minutes >= ACTIVITY_GAP_ANOMALY_MINUTES:
        days = int(gap_minutes // 1440)
        return True, f"Account inactive for {days} days before this event"

    return False, "Activity gap within normal range"