"""
Configuration for the AI-Optimised Load-Balancing Framework
Group 13 - IPAM, University of Sierra Leone
"""

# ====================== SIMULATION PARAMETERS ======================
SIMULATION_TIME = 3600          # seconds (1 hour simulated)
NUM_NODES = 25                  # number of peer devices
AREA_SIZE = 400                 # metres (village-scale area)
TRANSMISSION_RANGE = 100        # metres (Wi-Fi Direct / Bluetooth range)

# Mobility
MOBILITY_MODEL = "random_waypoint"
MIN_SPEED = 0.5                 # m/s
MAX_SPEED = 2.0                 # m/s
PAUSE_TIME = 30                 # seconds

# Node resources
INITIAL_BATTERY = 100.0         # %
BATTERY_DRAIN_TX = 0.08         # % per packet transmitted
BATTERY_DRAIN_RX = 0.05         # % per packet received
BATTERY_DRAIN_IDLE = 0.001      # % per second idle
MIN_BATTERY_TO_FORWARD = 15.0   # %

# Link quality
BASE_BANDWIDTH = 5.0            # Mbps
SIGNAL_VARIATION = 0.3          # ±30% random variation
PACKET_SIZE = 50                # KB (small/medium files only)

# Traffic
NUM_MESSAGES = 200              # total messages to send
MESSAGE_GENERATION_RATE = 0.1   # messages per second (average)

# ====================== AI MODEL ======================
AI_MODEL_TYPE = "random_forest"  # "decision_tree" or "random_forest"
FEATURE_COLUMNS = [
    "battery_level",
    "signal_strength",
    "available_bandwidth",
    "node_reliability",
    "queue_length",
    "recent_success_rate"
]
TRAINING_SAMPLES = 2000

# ====================== EVALUATION ======================
BASELINES = ["random", "round_robin", "ai"]
METRICS = [
    "throughput",
    "latency",
    "packet_delivery_ratio",
    "energy_consumption",
    "load_fairness"
]

# Paths
RESULTS_DIR = "results"
DATA_DIR = "data"
RANDOM_SEED = 42