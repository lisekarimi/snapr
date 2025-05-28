"""Handles persistent state management and access control for the application."""

import datetime
import os
import threading
from typing import Any, Dict, Tuple

from src.config.constants import IS_DEMO_VERSION, MAX_DEMO_RUNS_PER_DAY, STATE_FILE
from src.ui.formatting import get_server_timezone
from src.utils.file_io import load_json, write_json
from src.utils.logger import console

state_lock = threading.Lock()


def get_default_state() -> Dict[str, Any]:
    """Returns the default initial state dictionary."""
    return {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "run_count": 0}


def get_state() -> Dict[str, Any]:
    """Get the current state from the JSON file, initializing if needed."""
    if not os.path.exists(STATE_FILE):
        default_state = get_default_state()
        write_json(STATE_FILE, default_state)
        return default_state

    try:
        state = load_json(STATE_FILE)

        # Reset counter if it's a new day
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if state["date"] != current_date:
            state = get_default_state()
            write_json(STATE_FILE, state)

        return state

    except Exception as e:
        console.print(f"Error reading state file: {e}", style="red")
        return get_default_state()


def update_state(state_updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update the state file with new values."""
    current_state = get_state()
    current_state.update(state_updates)
    write_json(STATE_FILE, current_state)
    return current_state


def can_run_app() -> Tuple[bool, str]:
    """Check if the app can be run based on demo restrictions."""
    # No restrictions if not running in demo mode
    if not IS_DEMO_VERSION:
        return True, ""

    # Get server timezone for both cases
    server_time = get_server_timezone()
    server_time = f"🌐 {server_time}"

    # Load current run state
    state = get_state()
    runs_left = MAX_DEMO_RUNS_PER_DAY - state["run_count"]

    # Block if daily limit reached
    if state["run_count"] >= MAX_DEMO_RUNS_PER_DAY:
        return (
            False,
            f"⛔ Daily limit reached ({MAX_DEMO_RUNS_PER_DAY} runs per day "
            f"in demo mode). Please try again tomorrow!"
            f"<br>{server_time}",
        )

    # Otherwise, allow and return runs remaining
    return (
        True,
        f"🕒 Demo mode: {runs_left} run"
        f"{'s' if runs_left != 1 else ''} left today."
        f"<br>{server_time}",
    )
