"""Deletes a file if it's older than a specified number of days."""

import os
import time

from src.config.constants import MEMORY_EXPIRATION_DAYS


def delete_if_old(path: str, max_age_days: int = MEMORY_EXPIRATION_DAYS) -> None:
    """Deletes file if older than max_age_days."""
    if os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age > max_age_days * 86400:
            os.remove(path)
