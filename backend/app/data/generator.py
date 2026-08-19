"""
Synthetic data generator (early stub).

Goal: generate a realistic mix of normal user behavior and injected
"attack sequences" (new device + impossible travel + recent SIM-change
+ high-value transfer, all within a short window) so the scoring
engine can be tested and thresholds tuned without real telecom/bank data.

STATUS: skeleton only - fleshing out in the next commit with:
  - configurable number of fake users
  - realistic device/location distributions per user
  - randomized attack injection rate
  - CSV / JSON export for use in demo + dashboard
"""

import random
import uuid
from datetime import datetime, timedelta

random.seed(42)  # reproducible demo runs


def generate_normal_event(user_id: str, home_lat: float, home_lon: float, known_device: str):
    """Generate one plausible 'normal' login/transaction event for a user."""
    return {
        "user_id": user_id,
        "event_type": random.choice(["login", "transaction"]),
        "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(0, 500))).isoformat(),
        "device_id": known_device,
        "latitude": home_lat + random.uniform(-0.05, 0.05),
        "longitude": home_lon + random.uniform(-0.05, 0.05),
        "sim_change_flag": False,
        "sim_change_minutes_ago": None,
        "transaction_amount": round(random.uniform(200, 5000), 2),
    }


def generate_attack_sequence(user_id: str, home_lat: float, home_lon: float):
    """Generate an injected SIM-swap style attack sequence for a user."""
    attacker_lat = home_lat + random.uniform(5, 15)
    attacker_lon = home_lon + random.uniform(5, 15)
    new_device = f"device_{uuid.uuid4().hex[:8]}"

    return {
        "user_id": user_id,
        "event_type": "transaction",
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": new_device,
        "latitude": attacker_lat,
        "longitude": attacker_lon,
        "sim_change_flag": True,
        "sim_change_minutes_ago": random.randint(1, 60),
        "transaction_amount": round(random.uniform(20000, 100000), 2),
    }


if __name__ == "__main__":
    # Quick manual smoke test - not the final dataset pipeline
    sample_normal = generate_normal_event("demo_user", 12.9716, 77.5946, "device_abc123")
    sample_attack = generate_attack_sequence("demo_user", 12.9716, 77.5946)
    print("Normal event:", sample_normal)
    print("Attack event:", sample_attack)
