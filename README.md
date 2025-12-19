# CSV Filter Tool

Drag-and-drop friendly script to turn the CRM export (e.g., `Next_Day_Service_Appointment-20251219.csv`) into the upload-ready format (like `19decapp.csv`). Rows without a Vehicle are dropped.

## Quick use
1) Open Terminal and `cd /Users/jamescollins/Downloads/csv-filter-tool`.
2) Run:
   
   ```bash
   python convert_appointment.py /path/to/Next_Day_Service_Appointment-20251219.csv
   ```

   Tip: on macOS you can type `python convert_appointment.py `, then drag the CSV into the terminal to fill the path, then press Enter.

3) The file `11_Ready.csv` is written next to the source file.

## Rules implemented
- Drop any row with a missing/too-short Vehicle field.
- Name: split last token as last name; the rest as first name.
- Vehicle: first 4 chars → two-digit Year; second token → Make; remaining tokens → Model.
- Appointment: reformatted to `Saturday, December 20` (no year) and `HH:MM` 24-hour time.
- Phone: pick the best labeled number in priority `C > H > W > B`, digits only.
- Rate, Purchase Date, Lender (`Bank Name` or `P/L`), Payment copied/trimmed.
- Deduplicate on `(VIN, Appointment, Time)` — keep first occurrence.

## Output columns
`phone_number, Customer, Last Name, Year, Make, Model, Vin, Miles, Appointment, Time, Rate, Purchase Date, Lender, Payment`

## Notes
- Uses only the Python standard library; no installs needed.
- If you need a different output name, change `OUTPUT_NAME` near the top of `convert_appointment.py` (currently `11_Ready.csv`).
- If you need to keep rows without phone numbers, the script already allows blanks; only Vehicle is required.
