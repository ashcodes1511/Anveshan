from app.models.schemas import Event
from app.engine.scoring import score_event


def test_normal_event_is_low_risk():
    event = Event(
        user_id="demo_user",
        event_type="login",
        device_id="device_abc123",
        latitude=12.97,
        longitude=77.59,
        sim_change_flag=False,
    )
    result = score_event(event)
    assert result.risk_level == "LOW"
    assert result.action == "ALLOW"


def test_full_attack_sequence_is_high_risk():
    event = Event(
        user_id="demo_user",
        event_type="transaction",
        device_id="device_unknown_999",
        latitude=25.0,
        longitude=90.0,
        sim_change_flag=True,
        sim_change_minutes_ago=10,
        transaction_amount=50000,
    )
    result = score_event(event)
    assert result.risk_score >= 70
    assert result.risk_level == "HIGH"
    assert result.action == "FREEZE"