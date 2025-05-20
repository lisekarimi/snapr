# src/config/constants.py
"""Constants for configuration across the project."""

import os

from dotenv import load_dotenv

from src.version import __version__

# Load deploy.env to get PROJECT_NAME
load_dotenv("src/config/deploy.env")

# Get PROJECT_NAME with no fallback
PROJECT_NAME = os.environ.get("PROJECT_NAME")

# Environment settings
ENV = os.getenv("ENV", "DEV").upper()
IS_PROD = ENV == "PROD"

# Demo flag based on environment
IS_DEMO_VERSION = True if IS_PROD else False

# App naming for Modal
APP_NAME = (
    f"{PROJECT_NAME}-prod-{__version__}"
    if IS_PROD
    else f"{PROJECT_NAME}-dev-{__version__}"
)

MAX_DEMO_RUNS_PER_DAY = 5
MAX_LOG_LINES = 50  # Maximum number of logs to keep in view
CURRENCY = "$"
DEAL_THRESHOLD = 50
MAX_DEALS_PER_FEED = 20
MAX_CATEGORY_SELECTION = 3
MEMORY_EXPIRATION_DAYS = 5

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")

STATE_FILE = os.path.join(MEMORY_DIR, "demo_state.json")
DEALS_FILE = os.path.join(MEMORY_DIR, "memory.json")
