"""
Synthetic dataset generator - normal vs. attack sequences.
"""

import random
import uuid
from datetime import datetime, timedelta
USERS = [
    {
        "user_id": "cust_1",
        "lat": 12.9716,
        "lon": 77.5946,
        "device": "device_1"
    },
    {
        "user_id": "cust_2",
        "lat": 19.0760,
        "lon": 72.8777,
        "device": "device_2"
    },
    {
        "user_id": "cust_3",
        "lat": 28.6139,
        "lon": 77.2090,
        "device": "device_3"
    },
    {
        "user_id": "cust_4",
        "lat": 17.3850,
        "lon": 78.4867,
        "device": "device_4"
    }
]


def generate_random_normal_event():
    user = random.choice(USERS)

    return generate_normal_event(
        user["user_id"],
        user["lat"],
        user["lon"],
        user["device"]
    )


def generate_random_attack_event():
    user = random.choice(USERS)

    return generate_attack_sequence(
        user["user_id"],
        user["lat"],
        user["lon"]
    )
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

    sim_changed = random.choice([True, False])

    return {
        "user_id": user_id,
        "event_type": random.choice(["login", "transaction"]),
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": new_device,
        "latitude": attacker_lat,
        "longitude": attacker_lon,

        "sim_change_flag": sim_changed,
        "sim_change_minutes_ago": random.randint(1, 60) if sim_changed else None,

        "transaction_amount": round(
            random.uniform(1000, 150000), 2
        ),
    }


if __name__ == "__main__":

    print(
        generate_random_normal_event()
    )

    print(
        generate_random_attack_event()
    )