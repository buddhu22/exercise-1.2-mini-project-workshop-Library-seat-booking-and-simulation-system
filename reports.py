"""Booking reports and CSV schedule export."""
import csv
import logging
from pathlib import Path
from typing import Any
from booking import RESOURCES
from validators import parse_date

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
CSV_FIELDS = ["booking_id", "resource_id", "date", "start_time", "end_time", "user_id", "purpose", "status"]


def usage_report(bookings: list[dict[str, Any]]) -> list[tuple[str, str, int]]:
    """Return resource usage counts, including historical cancelled bookings."""
    counts = {resource["resource_id"]: 0 for resource in RESOURCES}
    for booking in bookings:
        resource_id = booking.get("resource_id")
        if resource_id in counts:
            counts[resource_id] += 1
    names = {resource["resource_id"]: resource["name"] for resource in RESOURCES}
    return sorted(((rid, names[rid], count) for rid, count in counts.items()),
                  key=lambda row: (-row[2], row[0]))


def cancelled_report(bookings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return cancelled booking records."""
    return [item for item in bookings if item.get("status") == "Cancelled"]


def export_schedule_csv(schedule: list[dict[str, Any]], schedule_date: str,
                        output_dir: Path = OUTPUT_DIR) -> Path:
    """Export a date's schedule to a CSV file and return its path."""
    normalized_date = parse_date(schedule_date).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"daily_schedule_{normalized_date}.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(schedule)
    logging.info("Exported daily schedule CSV for %s.", normalized_date)
    return path
