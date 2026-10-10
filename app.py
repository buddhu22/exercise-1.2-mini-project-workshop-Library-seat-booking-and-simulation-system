"""Menu-driven library seat and equipment booking simulator."""
import logging
from pathlib import Path
from booking import RESOURCES, cancel_booking, create_booking, daily_schedule, lookup_bookings
from reports import cancelled_report, export_schedule_csv, usage_report
from storage import BASE_DIR, load_bookings, save_bookings

LOG_DIR = BASE_DIR / "logs"


def setup_logging() -> None:
    """Configure timestamped application logging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG_DIR / "app.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")


def show_records(records: list[dict], empty_message: str = "No matching bookings found.") -> None:
    """Print booking records in a consistent readable layout."""
    if not records:
        print(empty_message)
        return
    for item in records:
        print(f"{item.get('booking_id')} | {item.get('resource_id')} | {item.get('date')} "
              f"{item.get('start_time')}-{item.get('end_time')} | user {item.get('user_id')} | "
              f"{item.get('purpose')} | {item.get('status')}")


def view_resources() -> None:
    print("\nResource Catalogue")
    for resource in RESOURCES:
        print(f"{resource['resource_id']} | {resource['type']} | {resource['name']} | "
              f"{resource['location']} | {resource['status']}")


def run() -> None:
    setup_logging()
    bookings = load_bookings()
    menu = ("\n========================================\n"
            " Library Seat & Equipment Booking\n"
            "========================================\n"
            "1. View Resources\n2. Book Resource\n3. Cancel Booking\n"
            "4. Lookup Booking\n5. View Daily Schedule\n6. Export Daily Schedule to CSV\n"
            "7. Most-Used Resources Report\n8. Cancelled Bookings Report\n9. Exit")
    while True:
        print(menu)
        try:
            choice = input("Enter your choice: ").strip()
        except EOFError:
            print("\nInput ended. Goodbye.")
            return
        if choice == "1":
            view_resources()
        elif choice == "2":
            try:
                record = create_booking(bookings, input("Resource ID: "), input("Date (YYYY-MM-DD): "),
                                        input("Start time (HH:MM): "), input("End time (HH:MM): "),
                                        input("Synthetic user ID: "), input("Purpose: "),
                                        input("Booking ID: "))
                save_bookings(bookings)
                logging.info("Booking created: %s", record["booking_id"])
                print(f"Booking created: {record['booking_id']}")
            except (ValueError, OSError) as exc:
                logging.warning("Booking rejected: %s", exc)
                print(f"Booking not created: {exc}")
            except Exception:
                logging.exception("Unexpected error while creating booking.")
                print("Booking could not be created due to an application error.")
        elif choice == "3":
            try:
                changed, message = cancel_booking(bookings, input("Booking ID: "))
                if changed:
                    save_bookings(bookings)
                    logging.info("Booking cancelled.")
                print(message)
            except (ValueError, OSError) as exc:
                logging.warning("Cancellation rejected: %s", exc)
                print(f"Cancellation not completed: {exc}")
        elif choice == "4":
            try:
                field = input("Search by booking ID, resource ID, or date: ").strip().lower()
                field = {"booking id": "booking_id", "resource id": "resource_id"}.get(field, field)
                if field not in {"booking_id", "resource_id", "date"}:
                    raise ValueError("Choose booking ID, resource ID, or date.")
                show_records(lookup_bookings(bookings, field, input("Search value: ")))
            except ValueError as exc:
                logging.warning("Invalid lookup input: %s", exc)
                print(exc)
        elif choice in {"5", "6"}:
            try:
                schedule_date = input("Date (YYYY-MM-DD): ")
                records = daily_schedule(bookings, schedule_date)
                if choice == "5":
                    show_records(records, "No bookings for that date.")
                else:
                    path = export_schedule_csv(records, schedule_date)
                    print(f"CSV exported to {path}")
            except (ValueError, OSError) as exc:
                logging.exception("Schedule operation failed.")
                print(f"Could not complete schedule operation: {exc}")
        elif choice == "7":
            print("Resource ID     Resource Name       Bookings")
            print("---------------------------------------------")
            for resource_id, name, count in usage_report(bookings):
                print(f"{resource_id:<15} {name:<20} {count}")
        elif choice == "8":
            records = cancelled_report(bookings)
            if not records:
                print("No cancelled bookings.")
            else:
                print("Booking ID | Resource ID | Date | User ID | Purpose")
                for item in records:
                    print(f"{item.get('booking_id')} | {item.get('resource_id')} | {item.get('date')} | "
                          f"{item.get('user_id')} | {item.get('purpose')}")
        elif choice == "9":
            print("Goodbye.")
            return
        else:
            logging.warning("Invalid menu choice entered.")
            print("Invalid choice. Enter a number from 1 to 9.")


if __name__ == "__main__":
    run()
