# fleet_utils.py
# Helper utilities for KM-Waechter.

MILES_PER_KM = 0.6214


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a value as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list; 0 if the list is empty."""
    if not values:
        return 0
    return sum(values) / len(values)
