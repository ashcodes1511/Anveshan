"""
Central configuration for SwapShield's scoring engine.

Keeping weights/thresholds here (instead of hardcoded in scoring.py)
makes them easy to tune once the synthetic dataset is generated at
scale, and easy to demo live by changing a number and re-running.
"""

# Points added to the risk score when each signal is triggered
WEIGHTS = {
    "new_device": 25,
    "impossible_travel": 30,
    "sim_change_recent": 35,
    "amount_deviation": 20,
    "activity_gap_anomaly": 10,
}

# Risk score thresholds -> risk level / action
HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40

# Distance (km) beyond which a login is treated as "impossible travel"
IMPOSSIBLE_TRAVEL_KM = 300

# How recent a SIM-change must be (minutes) to count as a live risk signal
SIM_CHANGE_WINDOW_MINUTES = 180

# Ratio of transaction amount to user's average that counts as deviation
AMOUNT_DEVIATION_RATIO = 5

# Minutes of inactivity beyond which sudden activity is treated as anomalous
ACTIVITY_GAP_ANOMALY_MINUTES = 43200  # 30 days