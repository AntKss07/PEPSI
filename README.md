# PEPSI — PDF Extraction, Processing & Smart Insertion

A powerful PDF automation toolkit that **extracts** structured data from any PDF, **maps** content between documents using spatial intelligence, and **fills** fillable PDF forms — all from the command line.

---

## ✨ Key Features

- **Universal PDF → JSON Extraction** — Converts any PDF into structured JSON, preserving layout, headings, tables, and form fields.
- **Intelligent PDF → PDF Mapping** — Automatically maps text from a source PDF to form fields in a target PDF using calibrated spatial transforms.
- **Smart Form Filling** — Fills fillable PDF templates with data from JSON files.
- **Cross-Page Alignment** — Handles source/target documents with different page counts, page sizes (A4 ↔ Letter), and layouts.
- **100% Field Coverage** — Achieves full field mapping (144/144) on complex medical forms with dense tables.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.6+

### Install
```bash
pip install -r requirements.txt
```

---

## 📖 How It Works

### Core Logic

**Step 1 — `pdf_to_json.py` (Extract)**

Opens a PDF → reads every page → extracts plain text + form field values → saves as JSON.

```python
import fitz  # PyMuPDF
import json

def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    result = {"metadata": {"file_name": pdf_path, "total_pages": len(doc)}, "pages": {}}
    
    for i, page in enumerate(doc):
        text = page.get_text("text")          # plain text
        fields = {}
        for widget in page.widgets():         # form fields
            fields[widget.field_name] = widget.field_value
        
        result["pages"][f"page_{i+1}"] = {
            "page_number": i + 1,
            "text": text,
            "form_fields": fields
        }
    return result
```

**Step 2 — `json_to_pdf.py` (Fill)**

Opens a blank fillable PDF → matches JSON keys to form field names → fills them in → saves.

```python
import fitz, json

def fill_form(json_path, template_pdf, output_pdf):
    with open(json_path) as f:
        data = json.load(f)  # {"field_name": "value", ...}
    
    doc = fitz.open(template_pdf)
    for page in doc:
        for widget in page.widgets():
            if widget.field_name in data:
                widget.field_value = data[widget.field_name]
                widget.update()
    
    doc.save(output_pdf)
```

**Step 3 — `map_fields.py` (Map — The Smart Part)**

This is the spatial intelligence engine. It bridges a filled source PDF with a blank target form:

```
1. Open source PDF (filled) + target PDF (blank form)
2. Find common keywords on Page 1 (e.g., "Name", "Date")
3. Calculate scale/offset between the two PDFs
4. For each field in target → convert coordinates → extract text from source
5. Save as JSON
```

The coordinate math:
```python
# If "Name" is at x=100 in source and x=120 in target:
# scale_x = target_width / source_width
# Then for any target field at position (tx, ty):
# source_x = (tx - offset_x) / scale_x
```

Key techniques used:
| Stage | Technique | Purpose |
|-------|-----------|---------|
| 1 | **Keyword Calibration** | Finds shared text ("Name", "Date of birth") on Page 1 to compute scale (sx, sy) and offset (dx, dy) |
| 2 | **Inverse Transform** | Converts each target field's coordinates back to source PDF space |
| 3 | **Clip-Based Extraction** | Uses `get_text("text", clip=...)` to extract text at the computed location with proper word spacing |
| 4 | **Smart Buffering** | Extends clip rightward for wide fields (paragraphs), keeps narrow for value fields |
| 5 | **Cross-Page Search** | Searches adjacent source pages (+1, +2, +3, -1) to handle page count mismatches |

---

## 🛠 Usage

### 1. Extract PDF → JSON

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

```bash
python map_fields.py <source_pdf> <target_fillable_pdf> <output_json>
```

**Example:**
```bash
python map_fields.py "data/Health and wellness guide example.pdf" "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf" "data/mapped_data.json"
```

### 3. Fill PDF Form from JSON

```bash
python json_to_pdf.py <input_json> <template_pdf> [output_pdf]
```

**Example:**
```bash
python json_to_pdf.py "data/mapped_data.json" "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf" "data/Filled_Health_Guide.pdf"
```

### Full Pipeline (2 Commands)

```bash
# Step 1: Extract & map fields from source PDF to target form
python map_fields.py "data/source.pdf" "data/template.pdf" "data/mapped_data.json"

# Step 2: Fill the template with mapped data
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

---

## 📁 Project Structure

```
PEPSI/
├── pdf_to_json.py       # Step 1: Universal PDF → JSON extractor
├── map_fields.py        # Step 3: Intelligent PDF → PDF field mapper
├── json_to_pdf.py       # Step 2: JSON → PDF form filler
├── requirements.txt     # Python dependencies (PyMuPDF)
├── README.md            # This file
└── data/                # Input/output PDFs and JSON files
    ├── Health and wellness guide example.pdf    # Sample source (filled)
    ├── HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf  # Sample template (blank)
    ├── mapped_data.json                        # Generated mapping
    └── Filled_Health_Guide.pdf                 # Final filled output
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Fields Mapped | **144 / 144 (100%)** |
| Source Pages | 14 |
| Target Pages | 11 |
| Processing Time | < 2 seconds |

---

## 📋 JSON Output Schema

```json
{
  "metadata": {
    "file_name": "example.pdf",
    "total_pages": 5
  },
  "pages": {
    "page_1": {
      "page_number": 1,
      "text": "Full plain text of the page...",
      "form_fields": {
        "FieldName": "User Input Value"
      }
    }
  }
}
```

---

## 🧰 Recommended Build Order

```
Week 1:  pdf_to_json.py  → test on any PDF
Week 2:  json_to_pdf.py  → test with a fillable PDF form
Week 3:  map_fields.py   → combine both + add coordinate math
```

---

## 🛠 Dependencies

- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) — PDF parsing, text extraction, and form field manipulation

## 📄 License

MIT
