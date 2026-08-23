"""
Time-since-last-activity signal.
"""

from datetime import datetime
from typing import Optional
from app.config import ACTIVITY_GAP_ANOMALY_MINUTES


def check_activity_gap(
    current_timestamp: datetime,
    last_event_timestamp: Optional[datetime],
) -> tuple[bool, str]:
    if last_event_timestamp is None:
        return False, "No prior activity on record to compare against"

    gap_minutes = (current_timestamp - last_event_timestamp).total_seconds() / 60

    if gap_minutes >= ACTIVITY_GAP_ANOMALY_MINUTES:
        days = int(gap_minutes // 1440)
        return True, f"Account inactive for {days} days before this event"

    return False, "Activity gap within normal range"