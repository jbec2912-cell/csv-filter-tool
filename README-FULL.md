# CSV Filter Tool

Convert Next Day Service Appointment exports into standardized format.

## Features

✓ Web interface (Vercel)  
✓ Command-line script (local)  
✓ Handles malformed CSV with line wrapping  
✓ Parses customer info, vehicle details, phone numbers  
✓ Formats dates and times  
✓ Deduplicates records  

## Web App (Vercel)

Visit: https://your-vercel-url.vercel.app

Upload your `Next_Day_Service_Appointment-*.csv` file and download the converted `11_Ready.csv`.

## Local Command Line

```bash
python3 /Users/jamescollins/Downloads/csv-filter-tool/convert_appointment.py /path/to/your/file.csv
```

Or:
```bash
cd /Users/jamescollins/Downloads/csv-filter-tool
python3 convert_appointment.py /path/to/your/file.csv
```

**macOS tip:** Type the command, then drag your CSV file into Terminal to auto-fill the path.

## What It Does

- Parses malformed Next_Day CSV with line wrapping in quoted fields
- Filters out rows without vehicle information  
- Splits customer names (first + last with proper capitalization)
- Extracts 2-digit year, Make, Model from vehicle field
- Formats appointment dates as "Saturday, December 20" (no year)
- Extracts phone numbers with priority: Cell > Home > Work > Business
- Converts all phone numbers to digits only
- Deduplicates on (VIN, Appointment, Time) — keeps first occurrence
- Outputs clean CSV with columns:
  - phone_number, Customer, Last Name, Year, Make, Model, Vin, Miles, Appointment, Time, Rate, Purchase Date, Lender, Payment

## Installation

### Local
- Python 3.6+ (uses only standard library)
- No external dependencies

### Web App
```bash
pip install -r requirements.txt
python3 app.py
```

Then visit: http://localhost:5000

## File Structure

```
.
├── convert_appointment.py    # Local CLI script
├── app.py                     # Flask web app
├── templates/
│   └── index.html             # Web interface
├── requirements.txt           # Python dependencies
├── vercel.json               # Vercel config
└── README.md
```

## GitHub

Repository: https://github.com/yourusername/csv-filter-tool

Clone:
```bash
git clone https://github.com/yourusername/csv-filter-tool.git
cd csv-filter-tool
```

## Deployment

### Vercel

1. Push code to GitHub
2. Go to https://vercel.com/import
3. Select your repository
4. Deploy (auto-detects Flask app)
5. Share the generated URL

## License

MIT
