# CSV Filter Tool

Converts the Next_Day Service Appointment export from your CRM into the standardized 19decapp format.

## Quick Start

```bash
cd /Users/jamescollins/Downloads/csv-filter-tool
python3 convert_appointment.py /path/to/Next_Day_Service_Appointment-*.csv
```

**Tip:** On macOS, type `python3 convert_appointment.py ` then drag the CSV file into Terminal, then press Enter.

**Output:** Creates `11 Ready.csv` in the same directory as the input file.

## What It Does

- ✓ Parses malformed Next_Day CSV export (handles line wrapping in quotes)
- ✓ Extracts customer, vehicle, and appointment information  
- ✓ Formats appointment dates as `Saturday, December 20, 2025`
- ✓ Formats times as `HH:MM` (24-hour format)
- ✓ Extracts phone numbers with priority: Cell > Home > Work > Business
- ✓ Deduplicates on `(VIN, Appointment, Time)` — keeps first occurrence
- ✓ Filters out rows missing vehicle information

## Output Format

Columns: `phone_number, Customer, Last Name, Year, Model, Vin, Miles, Appointment, Time, Rate, Purchase Date, Lender, Payment`

## Available Scripts

| Script | Purpose |
|--------|---------|
| `convert_appointment.py` | **Recommended** - Handles malformed CSV with line wrapping |
| `convert.py` | Original script for cleaner CSV files |

## Requirements

- Python 3.6+ (uses only Python standard library)
- No external dependencies needed

## Notes

- Phone numbers extracted as digits only (no formatting)
- Empty fields like Rate, Purchase Date, Payment preserved as blank
- P/L field used as fallback for Lender if Bank Name is empty
- Output name can be customized by editing `OUTPUT_NAME` in the script
