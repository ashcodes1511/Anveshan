"""
Anveshan scoring engine.
Rule-based + statistical anomaly checks (no ML) so every score is explainable.
"""
import random
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

from app.models.schemas import Event, RiskResponse, SignalBreakdown
from app.engine.signals import check_activity_gap
from app.config import (
    WEIGHTS,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
    IMPOSSIBLE_TRAVEL_KM,
    SIM_CHANGE_WINDOW_MINUTES,
    AMOUNT_DEVIATION_RATIO,
)

USER_BASELINE = {
    f"cust_{i}": {
        "known_devices": {f"device_{i}"},
        "home_lat": random.choice([12.9716, 19.0760, 28.6139, 17.3850]),
        "home_lon": random.choice([77.5946, 72.8777, 77.2090, 78.4867]),
        "avg_transaction_amount": random.randint(1000, 10000),
        "last_event_timestamp": datetime.utcnow()
    }
    for i in range(1, 101)
}

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def score_event(event: Event) -> RiskResponse:
    baseline = USER_BASELINE.get(event.user_id, {})
    if event.user_id not in USER_BASELINE:
     USER_BASELINE[event.user_id] = {
        "known_devices": set(),
        "avg_transaction_amount": 5000,
        "last_event_timestamp": datetime.utcnow()
    }
    signals: list[SignalBreakdown] = []
    total_score = 0

    known_devices = baseline.get("known_devices", set())
    is_new_device = bool(event.device_id) and event.device_id not in known_devices
    signals.append(SignalBreakdown(
        signal="device_fingerprint_change",
        triggered=is_new_device,
        points=WEIGHTS["new_device"] if is_new_device else 0,
        reason=(f"Device '{event.device_id}' not seen before" if is_new_device else "Device recognized"),
    ))
    if is_new_device:
        total_score += WEIGHTS["new_device"]

    if event.latitude is not None and event.longitude is not None and "home_lat" in baseline:
        distance = haversine_km(baseline["home_lat"], baseline["home_lon"], event.latitude, event.longitude)
        impossible_travel = distance > IMPOSSIBLE_TRAVEL_KM
        signals.append(SignalBreakdown(
            signal="geo_velocity_impossible_travel",
            triggered=impossible_travel,
            points=WEIGHTS["impossible_travel"] if impossible_travel else 0,
            reason=(f"Event location is {distance:.0f} km from usual location" if impossible_travel else "Location consistent"),
        ))
        if impossible_travel:
            total_score += WEIGHTS["impossible_travel"]

    sim_recent = event.sim_change_flag and (
        event.sim_change_minutes_ago is None or event.sim_change_minutes_ago <= SIM_CHANGE_WINDOW_MINUTES
    )
    signals.append(SignalBreakdown(
        signal="recent_sim_change",
        triggered=sim_recent,
        points=WEIGHTS["sim_change_recent"] if sim_recent else 0,
        reason=(f"SIM change reported {event.sim_change_minutes_ago} min ago" if sim_recent else "No recent SIM change"),
    ))
    if sim_recent:
        total_score += WEIGHTS["sim_change_recent"]

    if event.event_type == "transaction" and event.transaction_amount is not None:
        avg = baseline.get("avg_transaction_amount")
        if avg:
            ratio = event.transaction_amount / avg
            amount_deviation = ratio >= AMOUNT_DEVIATION_RATIO
            signals.append(SignalBreakdown(
                signal="transaction_amount_deviation",
                triggered=amount_deviation,
                points=WEIGHTS["amount_deviation"] if amount_deviation else 0,
                reason=(f"Amount is {ratio:.1f}x average" if amount_deviation else "Amount within normal range"),
            ))
            if amount_deviation:
                total_score += WEIGHTS["amount_deviation"]

    last_seen = baseline.get("last_event_timestamp")
    gap_triggered, gap_reason = check_activity_gap(event.timestamp, last_seen)
    signals.append(SignalBreakdown(
        signal="activity_gap_anomaly",
        triggered=gap_triggered,
        points=WEIGHTS["activity_gap_anomaly"] if gap_triggered else 0,
        reason=gap_reason,
    ))
    if gap_triggered:
        total_score += WEIGHTS["activity_gap_anomaly"]

    total_score = min(total_score, 100)
    import random

if total_score < MEDIUM_RISK_THRESHOLD:      # LOW
    total_score = random.randint(1, 29)

elif total_score < HIGH_RISK_THRESHOLD:      # MEDIUM
    total_score = random.randint(30, 69)

else:                                        # HIGH
    total_score = random.randint(70, 100)
    if total_score >= HIGH_RISK_THRESHOLD:
        risk_level, action = "HIGH", "FREEZE"
    elif total_score >= MEDIUM_RISK_THRESHOLD:
        risk_level, action = "MEDIUM", "REVIEW"
    else:
        risk_level, action = "LOW", "ALLOW"

    triggered_reasons = [s.reason for s in signals if s.triggered]
    explanation = "Flagged due to: " + "; ".join(triggered_reasons) if triggered_reasons else "No unusual signals detected."
    if event.device_id:
     baseline.setdefault("known_devices", set()).add(event.device_id)
     baseline["last_event_timestamp"] = event.timestamp

    return RiskResponse(
        user_id=event.user_id,
        event_type=event.event_type,
        risk_score=total_score,
        risk_level=risk_level,
        signals=signals,
        explanation=explanation,
        action=action,
    )