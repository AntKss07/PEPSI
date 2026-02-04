# Health Report PDF Extractor

A Flask-based application that extracts structured data from Health and Wellness PDF reports using PyMuPDF.

## Project Structure

```
PEPSI/
│
├── src/                          # Main source code
│   ├── components/               # UI components (HTML, CSS, JS)
│   │   ├── index.html           # Main web interface
│   │   ├── styles.css           # Styling
│   │   └── app.js               # Frontend JavaScript
│   ├── services/                 # Core extraction logic
│   │   ├── field_mapper.py      # Field extraction & mapping
│   │   └── pdf_extractor.py     # PDF text extraction
│   ├── models/                   # Data schemas & definitions
│   │   ├── schema_config.py     # Field schema configuration
│   │   ├── form_fields_schema.json
│   │   ├── pdf_fields_ordered_schema.json
│   │   └── health_wellness_structured_schema.json
│   ├── utils/                    # Helper functions
│   │   ├── doc_creator.py       # Document generation
│   │   ├── extract_schema.py    # Schema extraction utilities
│   │   └── compare_schema.py    # Schema comparison tools
│   └── app.py                    # Flask API entry point
│
├── tests/                        # Unit and integration tests
│   ├── test_utils/              # Mock data, test helpers
│   ├── test_extraction.py       # Extraction tests
│   └── test_doc_creator.py      # Document creator tests
│
├── config/                       # Configuration files
│
├── scripts/                      # Automation scripts
│
├── docs/                         # Documentation & reports
│   ├── comparison_report.json
│   └── comprehensive_test_report.txt
│
├── data/                         # PDF files and extracted data
│   ├── example_pdf_content.json
│   └── *.pdf                    # Sample PDF files
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python src/app.py
```

2. Open http://localhost:5000 in your browser

3. Upload a Health and Wellness PDF to extract data

## API Endpoints

- `GET /` - Main web interface
- `GET /api/schema` - Get field schema
- `POST /api/extract` - Extract data from uploaded PDF
- `GET /api/health` - Health check

## Features

- **Ordered JSON Output**: Fields are extracted in PDF reading order (page by page)
- **Question Labels**: Each field includes the original question/label from the PDF
- **144 Fields**: Comprehensive extraction of all form fields
- **Structured Sections**: Data organized by PDF sections (Demographics, Vitals, Labs, etc.)

## Output Format

```json
{
  "patient_name": {
    "question": "Name",
    "value": "RICHARD ALLEN PEACOCK"
  },
  "patient_id": {
    "question": "Identification number",
    "value": "AC737267"
  },
  ...
}
```

## License

Internal use only.
