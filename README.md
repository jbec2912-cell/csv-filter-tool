# CSV Filter Tool

Drag-and-drop friendly script to turn the CRM export (e.g., `Next_Day_Service_Appointment-20251219.csv`) into the upload-ready format (like `19decapp.csv`). Rows without a Vehicle are dropped.

## Quick use
1) Open Terminal and `cd /Users/jamescollins/Downloads/csv-filter-tool`.
2) Run:
   
   ```bash
   python convert.py /path/to/Next_Day_Service_Appointment-20251219.csv
   ```

   Tip: on macOS you can type `python convert.py `, then drag the CSV into the terminal to fill the path, then press Enter.

3) The file `11 Ready.csv` is written next to the source file.

## Rules implemented
- Drop any row with a missing/too-short Vehicle field.
- Name: split last token as last name; the rest as first name.
- Vehicle: first 4 chars → Year (if digits); rest → Model.
- Appointment: reformatted to `Saturday, December 20, 2025` and `HH:MM` 24-hour time.
- Phone: pick the best labeled number in priority `C > H > W > B`, digits only.
- Rate, Purchase Date, Lender (`Bank Name` or `P/L`), Payment copied/trimmed.
- Deduplicate on `(VIN, Appointment, Time)` — keep first occurrence.

## Output columns
`phone_number, Customer, Last Name, Year, Model, Vin, Miles, Appointment, Time, Rate, Purchase Date, Lender, Payment`

## Notes
- Uses only the Python standard library; no installs needed.
- If you need a different output name, change `OUTPUT_NAME` near the top of `convert.py` (currently `11 Ready.csv`).
- If you need to keep rows without phone numbers, the script already allows blanks; only Vehicle is required.
