# Universal PDF-to-JSON Extractor

A robust, universal PDF extraction tool that converts any PDF document into a structured JSON file while faithfully preserving the original layout, hierarchy, and content.

## Features

- **Universal Compatibility**: Works with ANY PDF document, not hardcoded to specific templates.
- **Structure Preservation**: Maintains page-by-page structure and detects headings, subheadings, lists, and tables.
- **Form Field Support**: Automatically extracts data from fillable PDF forms (widgets).
- **Spatial Awareness**: Uses block positioning to reconstruct the reading order correctly.
- **Multiple Extraction Modes**: obtain data in `structured` (hierarchical), `detailed` (structured + raw), or `flat` (line-by-line) formats.

## Setup

1. **Prerequisites**: Python 3.6+
2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line:

```bash
python pdf_to_json.py <input_pdf> [output_json]
```

### Examples

**Basic Usage (Default Structured Mode):**
Extracts `report.pdf` to `report_extracted.json`.
```bash
python pdf_to_json.py data/report.pdf
```

**Custom Output Path:**
```bash
python pdf_to_json.py data/report.pdf -o results/datalog.json
```

**Detailed Mode:**
Includes both structured content and raw line data, plus form fields.
```bash
python pdf_to_json.py data/report.pdf -m detailed
```

**Flat Mode:**
Simple line-by-line extraction per page.
```bash
python pdf_to_json.py data/report.pdf -m flat
```

**Batch Processing:**
Process multiple files at once.
```bash
python pdf_to_json.py data/file1.pdf data/file2.pdf
```

## JSON Output Structure

The output JSON follows a consistent schema:

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
        },
        {
          "type": "image", 
          "description": "[Image/graphic element]"
        }
      ],
      "form_fields": {
        "FieldName": "User Input Value"
      }
    },
    ...
  }
}
```

## Project Structure

```
PEPSI/
├── pdf_to_json.py      # Main universal extraction script
├── requirements.txt    # Python dependencies (PyMuPDF)
├── README.md           # Documentation
└── data/               # Input PDF files and JSON outputs
```
