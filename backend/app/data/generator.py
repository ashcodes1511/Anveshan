"""
Synthetic dataset generator - normal vs. attack sequences.
"""

import random
import uuid
from datetime import datetime, timedelta


random.seed(42)


def generate_normal_event(user_id: str, home_lat: float, home_lon: float, known_device: str):
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
    print("Normal event:", generate_normal_event("demo_user", 12.9716, 77.5946, "device_abc123"))
    print("Attack event:", generate_attack_sequence("demo_user", 12.9716, 77.5946))