"""Core booking rules and operations."""
from datetime import date, time
from typing import Any
from validators import parse_date, parse_time, required_text

RESOURCES = [
    {"resource_id": "LIB-SEAT-001", "type": "Study Seat", "name": "Study Seat 1", "location": "Quiet Zone A", "status": "Available"},
    {"resource_id": "LIB-SEAT-002", "type": "Study Seat", "name": "Study Seat 2", "location": "Quiet Zone A", "status": "Available"},
    {"resource_id": "LAP-001", "type": "Laptop", "name": "Laptop 1", "location": "Equipment Desk", "status": "Available"},
    {"resource_id": "LAP-002", "type": "Laptop", "name": "Laptop 2", "location": "Equipment Desk", "status": "Available"},
    {"resource_id": "PROJ-001", "type": "Projector", "name": "Projector 1", "location": "Workshop Room", "status": "Available"},
]


def intervals_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    """Return true when half-open intervals intersect; back-to-back slots are allowed."""
    # Half-open intervals [start, end) mean an end exactly at the next start is allowed.
    return start_a < end_b and start_b < end_a


def find_overlap(bookings: list[dict[str, Any]], resource_id: str, booking_date: date,
                 start_time: time, end_time: time) -> dict[str, Any] | None:
    """Find an active booking that overlaps the requested resource/date/time."""
    for booking in bookings:
        if (booking.get("status") == "Active"
                and booking.get("resource_id") == resource_id
                and booking.get("date") == booking_date.isoformat()):
            existing_start = parse_time(str(booking.get("start_time", "")))
            existing_end = parse_time(str(booking.get("end_time", "")))
            if intervals_overlap(start_time, end_time, existing_start, existing_end):
                return booking
    return None


def create_booking(bookings: list[dict[str, Any]], resource_id: str, booking_date: str,
                   start_time: str, end_time: str, user_id: str, purpose: str,
                   booking_id: str) -> dict[str, Any]:
    """Validate and append one booking. Raises ValueError for rejected requests."""
    resource_id = required_text(resource_id, "Resource ID").upper()
    user_id = required_text(user_id, "User ID")
    purpose = required_text(purpose, "Purpose")
    booking_id = required_text(booking_id, "Booking ID").upper()
    resource = next((r for r in RESOURCES if r["resource_id"] == resource_id), None)
    if resource is None:
        raise ValueError("That resource does not exist.")
    if any(item.get("booking_id") == booking_id for item in bookings):
        raise ValueError("That booking ID is already in use.")
    requested_date = parse_date(booking_date)
    start = parse_time(start_time)
    end = parse_time(end_time)
    if end <= start:
        raise ValueError("End time must be later than start time.")
    if resource.get("status") != "Available":
        raise ValueError("That resource is not available.")
    if find_overlap(bookings, resource_id, requested_date, start, end):
        raise ValueError("That time overlaps an existing active booking.")
    record = {
        "booking_id": booking_id,
        "resource_id": resource_id,
        "date": requested_date.isoformat(),
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
        "user_id": user_id,
        "purpose": purpose,
        "status": "Active",
    }
    bookings.append(record)
    return record


def cancel_booking(bookings: list[dict[str, Any]], booking_id: str) -> tuple[bool, str]:
    """Mark a booking cancelled without removing its audit record."""
    booking_id = required_text(booking_id, "Booking ID").upper()
    booking = next((item for item in bookings if item.get("booking_id") == booking_id), None)
    if booking is None:
        return False, "Booking not found."
    if booking.get("status") == "Cancelled":
        return False, "That booking is already cancelled."
    booking["status"] = "Cancelled"
    return True, "Booking cancelled."


def lookup_bookings(bookings: list[dict[str, Any]], field: str, value: str) -> list[dict[str, Any]]:
    """Search by booking ID, resource ID, or date."""
    value = required_text(value, "Search value")
    if field == "date":
        value = parse_date(value).isoformat()
    elif field in {"booking_id", "resource_id"}:
        value = value.upper()
    else:
        raise ValueError("Unsupported search field.")
    return [item for item in bookings if str(item.get(field, "")).upper() == value.upper()]


def daily_schedule(bookings: list[dict[str, Any]], schedule_date: str) -> list[dict[str, Any]]:
    """Return bookings on a date sorted by resource and start time."""
    target = parse_date(schedule_date).isoformat()
    return sorted((item for item in bookings if item.get("date") == target),
                  key=lambda item: (item.get("resource_id", ""), item.get("start_time", "")))
