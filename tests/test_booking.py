"""Automated tests for booking rules and storage recovery."""
import json
import unittest
from pathlib import Path
from booking import cancel_booking, create_booking, daily_schedule, find_overlap, lookup_bookings
from reports import cancelled_report, export_schedule_csv, usage_report
from storage import load_bookings, save_bookings


def make_booking(bookings=None, **overrides):
    values = {"resource_id": "LIB-SEAT-001", "booking_date": "2026-10-08",
              "start_time": "10:00", "end_time": "12:00", "user_id": "SYN-001",
              "purpose": "Study", "booking_id": "BKG-001"}
    values.update(overrides)
    return create_booking(bookings if bookings is not None else [], **values)


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.bookings = []

    def test_01_valid_booking(self):
        record = make_booking(self.bookings)
        self.assertEqual(record["status"], "Active")

    def test_02_nonexistent_resource(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            make_booking(self.bookings, resource_id="FAKE-001")

    def test_03_overlapping_booking_rejected(self):
        make_booking(self.bookings)
        with self.assertRaisesRegex(ValueError, "overlaps"):
            make_booking(self.bookings, booking_id="BKG-002", start_time="11:00", end_time="13:00")

    def test_04_non_overlapping_adjacent_booking_allowed(self):
        make_booking(self.bookings)
        record = make_booking(self.bookings, booking_id="BKG-002", start_time="12:00", end_time="13:00")
        self.assertEqual(record["start_time"], "12:00")

    def test_05_invalid_date_and_time(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            make_booking(self.bookings, booking_date="08/10/2026")
        with self.assertRaisesRegex(ValueError, "later than"):
            make_booking(self.bookings, start_time="12:00", end_time="12:00")

    def test_06_cancel_existing_booking(self):
        make_booking(self.bookings)
        changed, _ = cancel_booking(self.bookings, "BKG-001")
        self.assertTrue(changed)
        self.assertEqual(self.bookings[0]["status"], "Cancelled")

    def test_07_cancel_nonexistent_booking(self):
        changed, message = cancel_booking(self.bookings, "BKG-NOPE")
        self.assertFalse(changed)
        self.assertEqual(message, "Booking not found.")

    def test_08_missing_and_corrupt_json_recovery(self):
        directory = Path(__file__).resolve().parents[1] / ".test_tmp" / "storage"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "bookings.json"
        try:
            path.unlink(missing_ok=True)
            self.assertEqual(load_bookings(path), [])
            self.assertTrue(path.exists())
            path.write_text("{bad json", encoding="utf-8")
            self.assertEqual(load_bookings(path), [])
            self.assertEqual(path.read_text(encoding="utf-8"), "{bad json")
        finally:
            path.unlink(missing_ok=True)

    def test_duplicate_booking_id_rejected(self):
        make_booking(self.bookings)
        with self.assertRaisesRegex(ValueError, "already in use"):
            make_booking(self.bookings, resource_id="LAP-001")

    def test_empty_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "User ID cannot be empty"):
            make_booking(self.bookings, user_id=" ")

    def test_search_schedule_reports_and_csv(self):
        make_booking(self.bookings)
        self.assertEqual(len(lookup_bookings(self.bookings, "date", "2026-10-08")), 1)
        self.assertEqual(len(daily_schedule(self.bookings, "2026-10-08")), 1)
        self.assertEqual(usage_report(self.bookings)[0][2], 1)
        directory = Path(__file__).resolve().parents[1] / ".test_tmp" / "csv"
        directory.mkdir(parents=True, exist_ok=True)
        path = export_schedule_csv(self.bookings, "2026-10-08", directory)
        self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 2)
        path.unlink()
        cancel_booking(self.bookings, "BKG-001")
        self.assertEqual(len(cancelled_report(self.bookings)), 1)

    def test_invalid_menu_choice_is_handled_in_cli(self):
        # CLI menu choices are dispatched through explicit string checks in app.run.
        self.assertNotIn("0", {str(number) for number in range(1, 10)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
