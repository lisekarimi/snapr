"""Utility functions for text processing."""

import re


def extract_tagged_price(output: str) -> float:
    """Extracts a float price from a string based on 'Price is $' keyword."""
    try:
        contents = output.split("Price is $")[1].replace(",", "")
        match = re.search(r"[-+]?\d*\.\d+|\d+", contents)
        return float(match.group()) if match else 0.0
    except Exception:
        return 0.0


def extract_price(output: str) -> float:
    """Extracts a float price from a string.

    If no number is found, returns 0.0.
    """
    try:
        cleaned_text = output.replace("$", "").replace(",", "")
        match = re.search(r"[-+]?\d*\.\d+|\d+", cleaned_text)
        if match:
            return round(float(match.group()), 2)
        return 0.0
    except Exception:
        # Optionally log the exception or handle differently
        return 0.0
