# Exercise 1.2 — Library Seat and Equipment Booking Simulator

## Project objective

This beginner-friendly command-line project demonstrates basic secure application development through validation, clear booking rules, JSON persistence, CSV export, reporting, and timestamped audit logs. All resource and user IDs are fictional examples.

## Case scenario

A small fictional library lends study seats, laptops, and a projector in time slots. A user with a synthetic ID can reserve a resource, look up reservations, or cancel a reservation. The simulator prevents two active bookings from using the same resource at overlapping times.

## Features

- View a fixed catalogue of fictional resources.
- Create and cancel bookings while preserving cancellation history.
- Search by booking ID, resource ID, or date.
- View a date's schedule sorted by resource and start time.
- Export a daily schedule to CSV.
- Report resource booking counts and cancelled bookings.
- Save bookings in JSON and recover from missing or malformed JSON safely.
- Record significant events in `logs/app.log`.

## Project structure

```text
app.py                  Menu and user interaction
booking.py              Resource catalogue and booking rules
storage.py              JSON persistence
reports.py              Reports and CSV export
validators.py           Date, time, and required-text validation
data/bookings.json       Current booking records
data/                    Created automatically if missing
output/                  Daily CSV exports
logs/app.log             Timestamped application log
tests/test_booking.py    Automated tests
README.md                This guide
requirements.txt         No third-party packages required
```

## How the application works

`app.py` displays a menu and passes user input to small functions in the other modules. `booking.py` validates booking rules, including overlap. Time slots use half-open intervals: an existing 10:00–12:00 booking conflicts with 11:00–13:00, while 12:00–13:00 is allowed. `storage.py` loads and saves the JSON list. If the file is missing, it creates an empty list. If the JSON is corrupted, it logs and warns, preserves the bad file, and continues with an empty in-memory list for that run. `reports.py` produces reports and CSV output.

## How to run

Requires Python 3.10 or newer. From the project directory:

```bash
python app.py
```

To run the automated tests:

```bash
python -m unittest discover -s tests -v
```

The project uses only the Python standard library; `requirements.txt` is intentionally empty.

## Sample usage

Choose `2. Book Resource`, then enter values such as:

```text
Resource ID: LIB-SEAT-001
Date (YYYY-MM-DD): 2026-10-08
Start time (HH:MM): 10:00
End time (HH:MM): 11:00
Synthetic user ID: SYN-001
Purpose: Study
Booking ID: BKG-001
```

A second booking for `LIB-SEAT-001` from 10:30 to 11:30 on the same date will be rejected. A booking starting at 11:00 can be accepted because end times are exclusive.

## Data storage

Bookings are stored in `data/bookings.json`. The program creates the directory and file when first needed. CSV exports are named `output/daily_schedule_YYYY-MM-DD.csv`. Logs are written to `logs/app.log`. Paths are built with `pathlib` relative to the project files.

## Security practices

- The catalogue and sample IDs are fictional.
- The CLI asks only for synthetic user IDs and a purpose; it does not request contact details.
- User input is trimmed and validated before use.
- No `eval`, `exec`, shell commands, secrets, or external packages are used.
- Malformed JSON is reported to the user and preserved for recovery instead of silently overwritten.
- Cancellations update status and retain history.

## Testing

The test suite covers valid booking, nonexistent resources, overlap rejection, adjacent non-overlap, invalid dates/times, cancellation, missing/corrupt JSON, duplicate IDs, empty input, lookup, schedule, reports, and CSV output. An invalid menu choice is covered by a simple dispatch check. Expected behavior is encoded in each test assertion; the actual results are printed by `unittest`.

## Limitations

- JSON is suitable for a small learning exercise, but simultaneous writers can overwrite each other's updates and it is not a transactional database.
- This simplified time-slot model has no authentication, authorization, opening hours, maximum duration, or recurring reservations.
- If JSON is corrupted, the application preserves the file and uses an empty list in memory. An operator must repair or restore the file before previously saved bookings can be used.
- User IDs are not authenticated; the simulator trusts the ID typed into the CLI.

## Future improvements

A later version could add authentication, opening-hour rules, a database with transactions, and a guided recovery utility for malformed JSON. A wait-list could be added separately after the core booking flow is stable.
