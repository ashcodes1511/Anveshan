"""
Central configuration for SwapShield's scoring engine.
"""

WEIGHTS = {
   "new_device": 15,
"impossible_travel": 25,
"sim_change_recent": 40,
"amount_deviation": 15,
"activity_gap_anomaly": 5,
}

HIGH_RISK_THRESHOLD = 70
MEDIUM_RISK_THRESHOLD = 40
IMPOSSIBLE_TRAVEL_KM = 300
SIM_CHANGE_WINDOW_MINUTES = 180
AMOUNT_DEVIATION_RATIO = 5
ACTIVITY_GAP_ANOMALY_MINUTES = 43200  # 30 days