#!/usr/bin/env python3
"""Properly parse the malformed CSV by using a raw line-based approach."""

import re
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

OUTPUT_NAME = "11 Ready.csv"
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


def extract_quoted_fields(line: str) -> List[str]:
    """Extract fields from a CSV line, handling quoted fields properly."""
    fields = []
    current = ""
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append(current.strip())
            current = ""
            i += 1
            continue
        else:
            current += ch
        i += 1
    fields.append(current.strip())
    return fields


def main() -> None:
    import sys
    if len(sys.argv) != 2:
        print("Usage: python parse_csv.py /path/to/source.csv")
        sys.exit(1)

    src_path = Path(sys.argv[1]).expanduser()
    if not src_path.is_file():
        print(f"Source file not found: {src_path}")
        sys.exit(1)

    with src_path.open("r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Find header
    header_idx = -1
    for i, line in enumerate(lines):
        if '"Customer"' in line:
            header_idx = i
            break

    if header_idx == -1:
        print("Could not find header")
        sys.exit(1)

    # Parse header
    header_line = lines[header_idx]
    header_fields = extract_quoted_fields(header_line)
    header_fields = [f.strip('"') for f in header_fields]
    
    # Join lines into complete records (some records span multiple physical lines)
    record_lines = []
    current_record = ""
    for i in range(header_idx + 1, len(lines)):
        line = lines[i].rstrip('\n')
        if not line.strip():
            continue
        current_record += " " + line if current_record else line
        # Check if this line ends a record (has closing quote followed by more content or is complete)
        quote_count = current_record.count('"') - current_record.count('\\"')
        if quote_count % 2 == 0 and current_record.count(',') >= len(header_fields) - 1:
            record_lines.append(current_record)
            current_record = ""

    if current_record:
        record_lines.append(current_record)

    # Parse records
    seen = set()
    output_rows = []

    for record_line in record_lines:
        fields = extract_quoted_fields(record_line)
        fields = [f.strip('"').strip() for f in fields]
        
        if len(fields) < len(header_fields):
            fields.extend([''] * (len(header_fields) - len(fields)))

        row = dict(zip(header_fields, fields))

        vehicle = (row.get("Vehicle") or "").strip()
        if not vehicle or len(vehicle) < 5:
            continue

        phone = normalize_phone(row.get("Phone Numbers", ""))
        first, last = split_name(row.get("Customer", ""))
        year, model = parse_vehicle(vehicle)
        vin = (row.get("VIN") or "").strip()
        miles = (row.get("Mileage") or "").strip()
        appointment, time_24h = parse_datetime(row.get("Appointment Date", ""))
        rate = (row.get("Rate") or "").strip()
        purchase_date = (row.get("Purchase Date") or "").strip()
        lender = (row.get("Bank Name") or row.get("P/L") or "").strip()
        payment = (row.get("Payment") or "").strip()

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
