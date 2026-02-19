# PEPSI — PDF Extraction, Processing & Smart Insertion

A powerful PDF automation toolkit that **extracts** structured data from any PDF, **maps** content between documents using spatial intelligence, and **fills** fillable PDF forms — all from the command line.

## ✨ Key Features

- **Universal PDF → JSON Extraction** — Converts any PDF into structured JSON, preserving layout, headings, tables, and form fields.
- **Intelligent PDF → PDF Mapping** — Automatically maps text from a source PDF to form fields in a target PDF using calibrated spatial transforms.
- **Smart Form Filling** — Fills fillable PDF templates with data from JSON files.
- **Cross-Page Alignment** — Handles source/target documents with different page counts, page sizes (A4 ↔ Letter), and layouts.
- **100% Field Coverage** — Achieves full field mapping (144/144) on complex medical forms with dense tables.

## 🚀 Quick Start

### Prerequisites
- Python 3.6+

### Install
```bash
pip install -r requirements.txt
```

## 📖 Usage

### 1. Extract PDF → JSON

Convert any PDF document into structured JSON:

```bash
python pdf_to_json.py <input_pdf> [output_json]
```

**Examples:**
```bash
# Basic extraction (structured mode)
python pdf_to_json.py data/report.pdf

# Custom output path
python pdf_to_json.py data/report.pdf -o results/data.json

# Detailed mode (structured + raw line data + form fields)
python pdf_to_json.py data/report.pdf -m detailed

# Flat mode (simple line-by-line)
python pdf_to_json.py data/report.pdf -m flat

# Batch processing
python pdf_to_json.py data/file1.pdf data/file2.pdf
```

### 2. Map Source PDF → Target Form Fields

Automatically extract text from a filled PDF and map it to the matching fields in a blank fillable PDF template:

```bash
python map_fields.py <source_pdf> <target_fillable_pdf> <output_json>
```

**Example:**
```bash
python map_fields.py "data/Health and wellness guide example.pdf" "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf" "data/mapped_data.json"
```

**How it works:**
1. Computes an affine transform (scale + offset) from shared keywords on Page 1.
2. For each form field in the target PDF, converts its coordinates back to source space.
3. Extracts text from the source at that location using a calibrated clipping rectangle.
4. Searches across multiple source pages to handle page count mismatches (e.g., 14-page source → 11-page target).
5. Outputs a clean JSON mapping of `{ "field_name": "extracted_value" }`.

### 3. Fill PDF Form from JSON

Fill a blank fillable PDF template with data from a JSON file:

```bash
python json_to_pdf.py <input_json> <template_pdf> [output_pdf]
```

**Example:**
```bash
python json_to_pdf.py "data/mapped_data.json" "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf" "data/Filled_Health_Guide.pdf"
```

### Full Pipeline (2 Commands)

Map data from a source PDF and fill a form in one workflow:

```bash
# Step 1: Extract & map fields
python map_fields.py "data/source.pdf" "data/template.pdf" "data/mapped_data.json"

# Step 2: Fill the template
python json_to_pdf.py "data/mapped_data.json" "data/template.pdf" "data/Filled_Form.pdf"
```

### Scan-and-Fill Workflow (Manual)

If you want to manually fill a form:

```bash
# Step 1: Scan the form to discover field names
python json_to_pdf.py --scan "data/MyForm.pdf" "data/my_answers.json"

# Step 2: Edit my_answers.json with your data
# Step 3: Fill the form
python json_to_pdf.py "data/my_answers.json" "data/MyForm.pdf" "data/Filled_Form.pdf"
```

## 📁 Project Structure

```
PEPSI/
├── pdf_to_json.py       # Universal PDF → JSON extractor
├── map_fields.py        # Intelligent PDF → PDF field mapper
├── json_to_pdf.py       # JSON → PDF form filler
├── requirements.txt     # Python dependencies (PyMuPDF)
├── README.md            # This file
└── data/                # Input/output PDFs and JSON files
    ├── Health and wellness guide example.pdf    # Sample source
    ├── HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf  # Sample template
    ├── mapped_data.json                        # Generated mapping
    └── Filled_Health_Guide.pdf                 # Final filled output
```

## 🔧 How the Mapping Engine Works

The `map_fields.py` engine uses a multi-stage approach to achieve high-accuracy mapping:

| Stage | Technique | Purpose |
|-------|-----------|---------|
| 1 | **Keyword Calibration** | Finds shared text ("Name", "Date of birth") on Page 1 to compute scale (sx, sy) and offset (dx, dy) between source and target |
| 2 | **Inverse Transform** | Converts each target field's coordinates back to source PDF space |
| 3 | **Clip-Based Extraction** | Uses PyMuPDF's `get_text("text", clip=...)` to extract text at the computed location, preserving proper word spacing |
| 4 | **Smart Buffering** | Extends clip rightward for wide fields (paragraphs) to capture full sentences, keeps narrow for value fields |
| 5 | **Cross-Page Search** | When text isn't found on the same page, searches adjacent source pages (+1, +2, +3, -1) to handle page count mismatches |

### Performance

| Metric | Value |
|--------|-------|
| Fields Mapped | **144 / 144 (100%)** |
| Source Pages | 14 |
| Target Pages | 11 |
| Processing Time | < 2 seconds |

## 📋 JSON Output Schema

```json
{
  "metadata": {
    "file_name": "example.pdf",
    "total_pages": 5,
    "extraction_mode": "detailed"
  },
  "pages": {
    "page_1": {
      "page_number": 1,
      "structured_content": [
        {
          "heading": "Section Title",
          "content": ["Paragraph text...", "More text..."]
        }
      ],
      "form_fields": {
        "FieldName": "User Input Value"
      }
    }
  }
}
```

## 🛠 Dependencies

- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) — PDF parsing, text extraction, and form field manipulation

## 📄 License

MIT
