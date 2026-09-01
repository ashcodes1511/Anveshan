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
def generate_normal_event(user_id, home_lat, home_lon, known_device):
    return {
        "user_id": user_id,
        "event_type": random.choice(["login", "transaction"]),
        "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(0, 500))).isoformat(),

        # 20% chance of new device
        "device_id": known_device if random.random() < 0.8 else f"device_{uuid.uuid4().hex[:6]}",

        "latitude": home_lat + random.uniform(-0.05, 0.05),
        "longitude": home_lon + random.uniform(-0.05, 0.05),

        # occasional SIM change
        "sim_change_flag": random.random() < 0.15,
        "sim_change_minutes_ago": random.randint(1, 60),

        "transaction_amount": round(random.uniform(200, 5000), 2),
    }


def generate_attack_sequence(user_id: str, home_lat: float, home_lon: float):

    attacker_lat = home_lat + random.uniform(1, 20)
    attacker_lon = home_lon + random.uniform(1, 20)
    new_device = "device_{uuid.uuid4().hex[:8]}"

    sim_changed = random.random() < 0.7
    
    return {
        "user_id": user_id,
        "event_type": random.choice(["login", "transaction"]),
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": new_device,
        "latitude": attacker_lat,
        "longitude": attacker_lon,

        "sim_change_flag": sim_changed,
        "sim_change_minutes_ago": random.randint(1, 60) if sim_changed else None,

        "transaction_amount": round(random.choice([
        random.uniform(1000, 5000),
        random.uniform(5000, 20000),
        random.uniform(20000, 150000)
    ]),
    2
),
        
    }


if __name__ == "__main__":

    print(
        generate_random_normal_event()
    )

    print(
        generate_random_attack_event()
    )