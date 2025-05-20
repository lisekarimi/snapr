"""Utility functions for safely handling JSON file operations."""

import json
import os
from typing import Any, Dict

from src.utils.logger import console


def write_json(path: str, data: Dict[str, Any]) -> None:
    """Writes JSON to file, ensuring parent folder exists..

    Args:
        path (str): Full file path to write to.
        data (Dict[str, Any]): The data to write as JSON.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        console.print(f"Error writing to {path}: {e}", style="red")


def load_json(path: str) -> Dict[str, Any]:
    """Safely loads and returns JSON data from the given file path.

    Args:
        path (str): Full file path to read from.

    Returns:
        Dict[str, Any]: Parsed JSON content, or an empty dict if loading fails.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not os.path.exists(path):
            console.print(
                f"[yellow]File not found at {path}. Assuming first run.[/yellow]"
            )
            return {}

        with open(path, "r") as f:
            return json.load(f)

    except Exception as e:
        console.print(f"[red]Error reading from {path}: {e}[/red]")
        return {}
