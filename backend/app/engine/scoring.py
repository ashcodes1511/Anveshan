"""
SwapShield scoring engine.

Deliberately rule-based + simple statistical anomaly checks (no ML/deep
learning) so every score is explainable and auditable - this is a core
design choice described in the Round 1 submission.

Each signal contributes points toward a 0-100 risk score. The final
score maps to a risk level and a suggested action.

NOTE: This is an early-progress skeleton for GitHub visibility.
Thresholds/weights are placeholders to be tuned once the synthetic
dataset generator (see app/data/generator.py) is wired in.
"""

from math import radians, sin, cos, sqrt, atan2
from app.models.schemas import Event, RiskResponse, SignalBreakdown

# ---- Placeholder in-memory "known user history" store ----
# In the real system this comes from the synthetic dataset / a DB.
# Keyed by user_id -> dict of baseline behavior.
USER_BASELINE = {
    "demo_user": {
        "known_devices": {"device_abc123"},
        "home_lat": 12.9716,
        "home_lon": 77.5946,  # Bengaluru
        "avg_transaction_amount": 2500.0,
        "last_event_timestamp": None,
    }
}

# ---- Signal weights (placeholder, to be tuned with synthetic data) ----
WEIGHTS = {
    "new_device": 25,
    "impossible_travel": 30,
    "sim_change_recent": 35,
    "amount_deviation": 20,
    "activity_gap_anomaly": 10,
}

HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance between two points, in km."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def score_event(event: Event) -> RiskResponse:
    """Score a single event and return a full explainable risk response."""

    baseline = USER_BASELINE.get(event.user_id, {})
    signals: list[SignalBreakdown] = []
    total_score = 0

    # 1. New / unrecognized device
    known_devices = baseline.get("known_devices", set())
    is_new_device = bool(event.device_id) and event.device_id not in known_devices
    signals.append(
        SignalBreakdown(
            signal="device_fingerprint_change",
            triggered=is_new_device,
            points=WEIGHTS["new_device"] if is_new_device else 0,
            reason=(
                f"Device '{event.device_id}' not seen before for this user"
                if is_new_device
                else "Device recognized"
            ),
        )
    )
    if is_new_device:
        total_score += WEIGHTS["new_device"]

    # 2. Impossible travel (very rough placeholder heuristic)
    impossible_travel = False
    if event.latitude is not None and event.longitude is not None and "home_lat" in baseline:
        distance = haversine_km(
            baseline["home_lat"], baseline["home_lon"], event.latitude, event.longitude
        )
        # Placeholder: >300km from home location treated as suspicious
        # (real version compares against last login, factoring in time elapsed)
        impossible_travel = distance > 300
        signals.append(
            SignalBreakdown(
                signal="geo_velocity_impossible_travel",
                triggered=impossible_travel,
                points=WEIGHTS["impossible_travel"] if impossible_travel else 0,
                reason=(
                    f"Event location is {distance:.0f} km from user's usual location"
                    if impossible_travel
                    else "Location consistent with usual pattern"
                ),
            )
        )
        if impossible_travel:
            total_score += WEIGHTS["impossible_travel"]

    # 3. Recent SIM-change flag
    sim_recent = event.sim_change_flag and (
        event.sim_change_minutes_ago is None or event.sim_change_minutes_ago <= 180
    )
    signals.append(
        SignalBreakdown(
            signal="recent_sim_change",
            triggered=sim_recent,
            points=WEIGHTS["sim_change_recent"] if sim_recent else 0,
            reason=(
                f"SIM change reported {event.sim_change_minutes_ago} min ago"
                if sim_recent
                else "No recent SIM change on record"
            ),
        )
    )
    if sim_recent:
        total_score += WEIGHTS["sim_change_recent"]

    # 4. Transaction amount deviation
    amount_deviation = False
    if event.event_type == "transaction" and event.transaction_amount is not None:
        avg = baseline.get("avg_transaction_amount")
        if avg:
            ratio = event.transaction_amount / avg
            amount_deviation = ratio >= 5  # placeholder threshold
            signals.append(
                SignalBreakdown(
                    signal="transaction_amount_deviation",
                    triggered=amount_deviation,
                    points=WEIGHTS["amount_deviation"] if amount_deviation else 0,
                    reason=(
                        f"Amount is {ratio:.1f}x the user's average transaction"
                        if amount_deviation
                        else "Amount within normal range"
                    ),
                )
            )
            if amount_deviation:
                total_score += WEIGHTS["amount_deviation"]

    # 5. Time-since-last-activity anomaly - placeholder, not yet wired to real history
    # TODO: implement once synthetic dataset generator provides activity timestamps

    total_score = min(total_score, 100)

    if total_score >= HIGH_RISK_THRESHOLD:
        risk_level = "HIGH"
        action = "FREEZE"
    elif total_score >= MEDIUM_RISK_THRESHOLD:
        risk_level = "MEDIUM"
        action = "REVIEW"
    else:
        risk_level = "LOW"
        action = "ALLOW"

    triggered_reasons = [s.reason for s in signals if s.triggered]
    explanation = (
        "Flagged due to: " + "; ".join(triggered_reasons)
        if triggered_reasons
        else "No unusual signals detected."
    )

    return RiskResponse(
        user_id=event.user_id,
        event_type=event.event_type,
        risk_score=total_score,
        risk_level=risk_level,
        signals=signals,
        explanation=explanation,
        action=action,
    )
