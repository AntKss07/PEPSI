# Health and Wellness PDF Extractor

A simple Python backend to extract form field data from fillable Health and Wellness PDF documents.

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Extract from default PDF (data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf)
python extract_pdf.py

# Extract from specific PDF
python extract_pdf.py "path/to/your/pdf.pdf"
```

## Output

The script creates a structured JSON file with data organized by page:

```json
{
  "Page1": {
    "Title": "HEALTH AND WELLNESS GUIDE",
    "PersonalInfo": { "Name": "...", "IdentificationNumber": "...", "DateOfBirth": "..." },
    "WhyImproveHealth": "...",
    "MyPrimaryHealthGoals": { ... }
  },
  "Page2": { ... },
  ...
  "Page13": { ... }
}
```

## Project Structure

```
PEPSI/
├── extract_pdf.py      # Main extraction script
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/              # PDF files and output
    └── *.pdf          # Input PDF files
```
