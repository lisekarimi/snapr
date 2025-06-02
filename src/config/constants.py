# src/config/constants.py
"""Constants for configuration across the project."""

from pathlib import Path

import tomllib

# ==================== PROJECT METADATA ====================
root = Path(__file__).parent.parent.parent
with open(root / "pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)

PROJECT_NAME = pyproject["project"]["name"]
VERSION = pyproject["project"]["version"]

# ==================== ENVIRONMENT CONFIG ====================
ENV = "PROD"  # "PROD" # or "DEV"
IS_PROD = ENV == "PROD"
IS_DEMO_VERSION = IS_PROD  # True if PROD, False if DEV

# App naming for Modal
APP_NAME = f"{PROJECT_NAME}-{ENV.lower()}-{VERSION}"

# ==================== APPLICATION LIMITS ====================
MAX_DEMO_RUNS_PER_DAY = 5
MAX_LOG_LINES = 50
MAX_DEALS_PER_FEED = 20
MAX_CATEGORY_SELECTION = 3
MEMORY_EXPIRATION_DAYS = 5

# ==================== BUSINESS LOGIC ====================
CURRENCY = "$"
DEAL_THRESHOLD = 50

# ==================== PATHS ====================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEMORY_DIR = BASE_DIR / "memory"
STATE_FILE = MEMORY_DIR / "demo_state.json"
DEALS_FILE = MEMORY_DIR / "memory.json"
