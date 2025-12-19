#!/usr/bin/env python3
"""CSV converter: transforms the raw CRM export into the upload-ready format.

Usage (drag-and-drop-friendly on macOS):
    python convert.py /path/to/Next_Day_Service_Appointment-20251219.csv

Outputs 19decapp_converted.csv alongside the input file.
"""
from __future__ import annotations

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Tuple

OUTPUT_NAME = "11 Ready.csv"

PHONE_PRIORITY = ("C", "H", "W", "B")  # cell > home > work > business


def normalize_phone(raw: str) -> str:
    """Pick the best phone from the CRM "Phone Numbers" field.

    The CRM field can look like: "H: (813) 326-9813C: (813) 326-9813".
    We extract labeled numbers, prefer C > H > W > B, and return digits only.
    """
    if not raw:
        return ""

    # Capture label and its digits, even when labels are adjacent.
    matches: Iterable[Tuple[str, str]] = re.findall(r"(C|H|W|B):\s*([0-9\s\-\(\)]+)", raw)
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
    """Split customer name into first and last (last token = last name)."""
    if not full:
        return "", ""
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def parse_vehicle(vehicle: str) -> Tuple[str, str]:
    """Return (year, model) from the CRM vehicle string."""
    if not vehicle or len(vehicle) < 5:
        return "", ""
    year_candidate = vehicle[:4]
    year = year_candidate if year_candidate.isdigit() else ""
    model = vehicle[5:] if year else vehicle
    return year, model


def parse_datetime(dt_str: str) -> Tuple[str, str]:
    """Split CRM datetime into (Appointment, Time)."""
    if not dt_str:
        return "", ""
    try:
        dt = datetime.strptime(dt_str.strip(), "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        return "", ""
    # Use %-d on macOS/Linux, %#d on Windows
    day = dt.day
    appointment = dt.strftime(f"%A, %B {day}, %Y")
    time_24h = dt.strftime("%H:%M")
    return appointment, time_24h


def clean_payment(val: str) -> str:
    return val.strip() if val else ""


def normalize_rate(val: str) -> str:
    return val.strip() if val else ""


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python convert.py /path/to/source.csv")
        sys.exit(1)

    src_path = Path(sys.argv[1]).expanduser()
    if not src_path.is_file():
        print(f"Source file not found: {src_path}")
        sys.exit(1)

    with src_path.open(newline="", encoding="utf-8-sig") as f:
        content = f.read()
    
    # Skip header lines until we find the CSV header row
    lines = content.split('\n')
    header_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('"Customer"'):
            header_idx = i
            break
    
    if header_idx == -1:
        print("Could not find CSV header row")
        sys.exit(1)
    
    # Join remaining lines and parse as CSV
    csv_content = '\n'.join(lines[header_idx:])
    rows = list(csv.DictReader(csv_content.splitlines()))

    seen = set()
    output_rows = []

    for row in rows:
        vehicle = (row.get("Vehicle") or "").strip()
        if not vehicle or len(vehicle) < 5:
            continue  # drop rows with missing/invalid vehicle

        phone = normalize_phone(row.get("Phone Numbers", ""))
        first, last = split_name(row.get("Customer", ""))
        year, model = parse_vehicle(vehicle)
        vin = (row.get("VIN") or "").strip()
        miles = (row.get("Mileage") or "").strip()
        appointment, time_24h = parse_datetime(row.get("Appointment Date", ""))
        rate = normalize_rate(row.get("Rate", ""))
        purchase_date = (row.get("Purchase Date") or "").strip()
        lender = (row.get("Bank Name") or row.get("P/L") or "").strip()
        payment = clean_payment(row.get("Payment") or "")

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
