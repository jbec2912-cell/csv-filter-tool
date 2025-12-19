# Quick Start Guide

## You Now Have 2 Ways to Convert CSV Files:

### Option 1: Local Command Line (Fast, Private)

```bash
python3 /Users/jamescollins/Downloads/csv-filter-tool/convert_appointment.py /path/to/your/file.csv
```

**Result:** `11 Ready.csv` created in same folder as your input file.

---

### Option 2: Web App (Share with Others, No Installation)

#### Local Testing
```bash
cd /Users/jamescollins/Downloads/csv-filter-tool
pip install -r requirements.txt
python3 app.py
```
Then open: http://localhost:5000

#### Deploy to Vercel (Free)

1. **Initialize Git:**
   ```bash
   cd /Users/jamescollins/Downloads/csv-filter-tool
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub repo** at https://github.com/new
   - Name: `csv-filter-tool`
   - Make it Public

3. **Push to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/csv-filter-tool.git
   git branch -M main
   git push -u origin main
   ```

4. **Deploy to Vercel:**
   - Go to https://vercel.com
   - Click "Import Project"
   - Select your GitHub repo
   - Click "Deploy"
   - Get your live URL!

---

## What Each Tool Does

### Command Line (`convert_appointment.py`)
- ✓ Fastest
- ✓ Private (runs on your computer)
- ✓ Best for personal use
- ✓ Requires Terminal knowledge

### Web App (`app.py`)
- ✓ User-friendly interface
- ✓ Accessible from any browser
- ✓ Easy to share with team
- ✓ No installation needed for users
- ✓ Can be deployed on Vercel (free)

---

## Files Included

```
csv-filter-tool/
├── convert_appointment.py    ← CLI script (recommended)
├── app.py                    ← Flask web app
├── templates/index.html      ← Web interface
├── requirements.txt          ← Python dependencies
├── vercel.json              ← Vercel configuration
├── .gitignore               ← Git ignore file
├── DEPLOYMENT.md            ← Detailed deployment guide
└── README-FULL.md           ← Full documentation
```

---

## Next Steps

**Choose your path:**

- **Just need local CLI?** You're done! Use `convert_appointment.py`
- **Want a web app locally?** Follow "Local Testing" above
- **Want to share online?** Follow "Deploy to Vercel" above

Questions? Check DEPLOYMENT.md for detailed instructions!
