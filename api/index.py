#!/usr/bin/env python3
"""Flask web app for CSV conversion - Vercel compatible."""

import csv
import re
from datetime import datetime
from io import StringIO, BytesIO
from flask import Flask, render_template, request, send_file, jsonify
import os
from typing import Dict, Tuple

# When running under Vercel, this file lives in api/, but templates/ is at project root.
# Point Flask to the correct templates directory explicitly.
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

PHONE_PRIORITY = ("C", "H", "W", "B")


def normalize_phone(raw: str) -> str:
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
    if not full:
        return "", ""
    parts = full.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def parse_vehicle(vehicle: str) -> Tuple[str, str, str]:
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


def convert_csv(file_content: str) -> str:
    """Convert Next_Day CSV to standard format."""
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
        "phone_number", "Customer", "Last Name", "Year", "Make", "Model",
        "Vin", "Miles", "Appointment", "Time", "Rate", "Purchase Date",
        "Lender", "Payment",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

    return output.getvalue()


@app.route("/")
@app.route("/api")
@app.route("/index")
@app.route("/api/index")
def index():
    return render_template("index.html")


# On Vercel, requests arrive at /api/*, and Flask sees the path without the /api prefix.
# So the browser should call /api/convert, and Flask should register /convert here.
@app.route("/convert", methods=["POST"])
@app.route("/api/convert", methods=["POST"])
@app.route("/index/convert", methods=["POST"])
@app.route("/api/index/convert", methods=["POST"])
def api_convert():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        content = file.read().decode("utf-8-sig")
        converted = convert_csv(content)
        
        output = BytesIO(converted.encode("utf-8"))
        output.seek(0)
        
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name="11_Ready.csv"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
