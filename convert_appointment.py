#!/usr/bin/env python3
"""Convert Next_Day Service Appointment CSV to the 19decapp format."""

import csv
import re
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, Tuple

OUTPUT_NAME = "11_Ready.csv"
PHONE_PRIORITY = ("C", "H", "W", "B")


def normalize_phone(raw: str) -> str:
    """Pick the best phone from the CRM 'Phone Numbers' field."""
    if not raw:
        return ""
    matches = re.findall(r"(C|H|W|B):\s*([0-9\s\-\(\)]+)", raw)
    phones: Dict[str, str] = {}
    for label, number in matches:
        digits = re.sub(r"\D", "", number)
        if digits:
            phones[label] = digits

    for label in PHONE_PRIORITY:
        if label in phones:
            return phones[label]
    return ""


def split_name(full: str) -> Tuple[str, str]:
    """Split customer name into first and last."""
    if not full:
        return "", ""
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def parse_vehicle(vehicle: str) -> Tuple[str, str, str]:
    """Return (year_2digit, make, model) from the vehicle string."""
    if not vehicle or len(vehicle) < 5:
        return "", "", ""

    parts = vehicle.split()
    if len(parts) < 2:
        return "", "", ""

    year_candidate = parts[0]
    if not year_candidate.isdigit() or len(year_candidate) != 4:
        return "", "", ""

    year_2digit = year_candidate[-2:]
    make = parts[1]
    model = " ".join(parts[2:]) if len(parts) > 2 else ""

    return year_2digit, make, model


def parse_datetime(dt_str: str) -> Tuple[str, str]:
    """Split CRM datetime into (Appointment, Time) without the year in Appointment."""
    if not dt_str:
        return "", ""
    try:
        dt = datetime.strptime(dt_str.strip(), "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        return "", ""
    day = dt.day
    appointment = dt.strftime(f"%A, %B {day}")
    time_24h = dt.strftime("%H:%M")
    return appointment, time_24h


def convert_content(file_content: str) -> Tuple[str, int]:
    """Convert raw CSV text into the target CSV string and return row count."""
    reader = csv.reader(file_content.splitlines())
    all_rows = list(reader)

    header_idx = -1
    for i, row in enumerate(all_rows):
        if len(row) > 0 and "Customer" in row[0]:
            header_idx = i
            break

    if header_idx == -1:
        raise ValueError("Could not find CSV header row")

    headers = all_rows[header_idx]
    data_rows = all_rows[header_idx + 1:]

    header_map = {h: i for i, h in enumerate(headers)}

    required_fields = {"Customer", "Vehicle", "VIN", "Mileage", "Appointment Date", "Rate", "Phone Numbers"}
    if not required_fields.issubset(set(headers)):
        missing = required_fields - set(headers)
        raise ValueError(f"Missing required headers: {missing}")

    seen = set()
    output_rows = []

    for row in data_rows:
        while len(row) < len(headers):
            row.append("")

        customer = (row[header_map.get("Customer", 0)] or "").strip()
        vehicle = (row[header_map.get("Vehicle", 1)] or "").strip()
        vin = (row[header_map.get("VIN", 2)] or "").strip()
        miles = (row[header_map.get("Mileage", 3)] or "").strip()
        appt_date = (row[header_map.get("Appointment Date", 4)] or "").strip()
        rate = (row[header_map.get("Rate", 5)] or "").strip()
        p_l = (row[header_map.get("P/L", 6)] or "").strip()
        purchase_date = (row[header_map.get("Purchase Date", 7)] or "").strip()
        bank_name = (row[header_map.get("Bank Name", 8)] or "").strip()
        payment = (row[header_map.get("Payment", 9)] or "").strip()
        phone_numbers = (row[header_map.get("Phone Numbers", 11)] or "").strip()

        if not vehicle or len(vehicle) < 5:
            continue

        phone = normalize_phone(phone_numbers)
        first, last = split_name(customer)
        first = first.capitalize() if first else ""
        last = last.capitalize() if last else ""
        year_2digit, make, model = parse_vehicle(vehicle)
        appointment, time_24h = parse_datetime(appt_date)

        if not appointment or not time_24h:
            continue

        lender = bank_name if bank_name else p_l

        dedup_key = (vin, appointment, time_24h)
        if vin and dedup_key in seen:
            continue
        seen.add(dedup_key)

        output_rows.append({
            "phone_number": phone,
            "Customer": first,
            "Last Name": last,
            "Year": year_2digit,
            "Make": make,
            "Model": model,
            "Vin": vin,
            "Miles": miles,
            "Appointment": appointment,
            "Time": time_24h,
            "Rate": rate,
            "Purchase Date": purchase_date,
            "Lender": lender,
            "Payment": payment,
        })

    output = StringIO()
    fieldnames = [
        "phone_number",
        "Customer",
        "Last Name",
        "Year",
        "Make",
        "Model",
        "Vin",
        "Miles",
        "Appointment",
        "Time",
        "Rate",
        "Purchase Date",
        "Lender",
        "Payment",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

    return output.getvalue(), len(output_rows)


def convert_file(src_path: Path) -> Path:
    """Convert a CSV file on disk using the shared converter."""
    content = src_path.read_text(encoding="utf-8-sig")
    converted_csv, row_count = convert_content(content)
    out_path = src_path.with_name(OUTPUT_NAME)
    out_path.write_text(converted_csv, encoding="utf-8")
    print(f"✓ Wrote {row_count} rows to {out_path}")
    return out_path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python convert_appointment.py /path/to/Next_Day_Service_Appointment-*.csv")
        sys.exit(1)

    src_path = Path(sys.argv[1]).expanduser()
    if not src_path.is_file():
        print(f"Source file not found: {src_path}")
        sys.exit(1)

    try:
        convert_file(src_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Conversion failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
