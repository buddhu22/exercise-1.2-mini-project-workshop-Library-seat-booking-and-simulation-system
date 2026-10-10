"""JSON persistence for bookings."""
import json
import logging
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BOOKINGS_FILE = DATA_DIR / "bookings.json"


def load_bookings(path: Path = BOOKINGS_FILE) -> list[dict[str, Any]]:
    """Load bookings, initializing missing/corrupt files with an empty list."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.warning("Booking file missing; initialized an empty booking list.")
        save_bookings([], path)
        return []
    except json.JSONDecodeError:
        logging.exception("Booking JSON is corrupted; preserving it and using an empty in-memory list.")
        print("Warning: bookings.json is invalid. It has not been overwritten; using an empty list for this session.")
        return []
    except OSError:
        logging.exception("Could not read booking file.")
        print("Warning: booking data could not be read. Using an empty list for this session.")
        return []
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        logging.error("Booking JSON has an invalid structure.")
        print("Warning: booking data has an invalid structure. Using an empty list for this session.")
        return []
    return data


def save_bookings(bookings: list[dict[str, Any]], path: Path = BOOKINGS_FILE) -> None:
    """Write booking data as readable UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(bookings, file, indent=2, ensure_ascii=False)
        file.write("\n")
