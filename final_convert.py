#!/usr/bin/env python3
"""Parse the Next_Day Service CSV export and convert to standard format."""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

OUTPUT_NAME = "11 Ready.csv"
PHONE_PRIORITY = ("C", "H", "W", "B")

# Expected header based on the first data row
EXPECTED_HEADERS = [
    "Customer", "Vehicle", "VIN", "Mileage", "Appointment Date", 
    "Rate", "P/L", "Purchase Date", "Bank Name", "Payment",
    "Sales Person", "Phone Numbers", "Service Advisor"
]


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


def parse_vehicle(vehicle: str) -> Tuple[str, str]:
    """Return (year, model) from the vehicle string."""
    if not vehicle or len(vehicle) < 5:
        return "", ""
    year_candidate = vehicle[:4]
    year = year_candidate if year_candidate.isdigit() else ""
    model = vehicle[5:].strip() if year else vehicle
    return year, model


def parse_datetime(dt_str: str) -> Tuple[str, str]:
    """Split CRM datetime into (Appointment, Time)."""
    if not dt_str:
        return "", ""
    try:
        dt = datetime.strptime(dt_str.strip(), "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        return "", ""
    day = dt.day
    appointment = dt.strftime(f"%A, %B {day}, %Y")
    time_24h = dt.strftime("%H:%M")
    return appointment, time_24h


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python final_convert.py /path/to/source.csv")
        sys.exit(1)

    src_path = Path(sys.argv[1]).expanduser()
    if not src_path.is_file():
        print(f"Source file not found: {src_path}")
        sys.exit(1)

    # Read raw file
    with src_path.open("r", encoding="utf-8-sig") as f:
        content = f.read()

    # Use csv reader on the whole content to properly parse quoted fields
    rows = list(csv.reader(content.splitlines()))

    # Find where data starts (after header line)
    data_start = -1
    for i, row in enumerate(rows):
        if len(row) > 0 and row[0].startswith("Customer"):
            data_start = i + 1
            break

    if data_start == -1:
        print("Could not find data start")
        sys.exit(1)

    # Process data rows
    seen = set()
    output_rows = []

    for row in rows[data_start:]:
        if not row or len(row) < 3:
            continue

        # Pad row to match expected headers
        while len(row) < len(EXPECTED_HEADERS):
            row.append("")

        # Create dict from row
        data = dict(zip(EXPECTED_HEADERS, row[:len(EXPECTED_HEADERS)]))

        vehicle = (data.get("Vehicle") or "").strip()
        if not vehicle or len(vehicle) < 5:
            continue

        phone = normalize_phone(data.get("Phone Numbers", ""))
        first, last = split_name(data.get("Customer", ""))
        year, model = parse_vehicle(vehicle)
        vin = (data.get("VIN") or "").strip()
        miles = (data.get("Mileage") or "").strip()
        appointment, time_24h = parse_datetime(data.get("Appointment Date", ""))
        rate = (data.get("Rate") or "").strip()
        purchase_date = (data.get("Purchase Date") or "").strip()
        lender = (data.get("Bank Name") or data.get("P/L") or "").strip()
        payment = (data.get("Payment") or "").strip()

        if not appointment or not time_24h:
            continue

        dedup_key = (vin, appointment, time_24h)
        if vin and dedup_key in seen:
            continue
        seen.add(dedup_key)

        output_rows.append({
            "phone_number": phone,
            "Customer": first,
            "Last Name": last,
            "Year": year,
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

    # Write output
    fieldnames = [
        "phone_number",
        "Customer",
        "Last Name",
        "Year",
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

    out_path = src_path.with_name(OUTPUT_NAME)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
