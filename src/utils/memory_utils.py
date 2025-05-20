"""Utilities for handling deal memory and persistence."""

from datetime import datetime, timezone
from typing import Dict, List

from src.config.constants import DEALS_FILE
from src.utils.file_io import load_json, write_json


def save_opportunities_to_memory(
    new_opportunities: List[Dict], memory_path: str = DEALS_FILE
) -> None:
    """Updates opportunities with deduplication and saves to memory."""
    existing_data = load_json(memory_path) or {"opportunities": []}

    all_opportunities = existing_data.get("opportunities", []) + new_opportunities
    unique_by_url = {op["url"]: op for op in all_opportunities}
    final_list = list(unique_by_url.values())

    write_json(
        memory_path,
        {
            "opportunities": final_list,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        },
    )
