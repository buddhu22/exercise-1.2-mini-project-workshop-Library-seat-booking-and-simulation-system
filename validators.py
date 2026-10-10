"""Input validation helpers for the library booking simulator."""
from datetime import date, time


def required_text(value: str, field_name: str) -> str:
    """Return trimmed non-empty text or raise ValueError with a safe message."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return value.strip()


def parse_date(value: str) -> date:
    """Parse a date in YYYY-MM-DD format."""
    text = required_text(value, "Date")
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("Date must use YYYY-MM-DD format.") from exc


def parse_time(value: str) -> time:
    """Parse a 24-hour time in HH:MM format."""
    text = required_text(value, "Time")
    try:
        return time.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("Time must use 24-hour HH:MM format.") from exc
