#!/usr/bin/env python3
"""
JSON-to-PDF Form Filler
========================
Fills a blank PDF form using data from a JSON file.
Automatically maps JSON keys (field names) to PDF form widgets.

Features:
  - Supports flat JSON objects ({"Name": "John"})
  - Supports nested JSON structures (extracts all terminal values)
  - Supports the output format of `pdf_to_json.py` specifically
  - Matches exact field names

Usage:
  python json_to_pdf.py <input.json> <template.pdf> [output.pdf]

"""

import sys
import os
import json
import argparse
from typing import Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install PyMuPDF")
    sys.exit(1)


def flatten_json(data: Dict[str, Any], extracted_fields: Dict[str, str] = None) -> Dict[str, str]:
    """
    Recursively search for potential form field values in a JSON object.
    
    Supports:
      1. Direct "form_fields" blocks (from pdf_to_json.py detailed mode)
      2. Structured content blocks: {"subheading": "Name:", "content": ["Value"]}
      3. Flat key-value pairs
    """
    if extracted_fields is None:
        extracted_fields = {}

    if isinstance(data, dict):
        # 1. Direct form_fields block
        if "form_fields" in data and isinstance(data["form_fields"], dict):
            for k, v in data["form_fields"].items():
                if isinstance(v, (str, int, float, bool)):
                    extracted_fields[k] = str(v)
        
        # 2. Structured Content "Smart Mapping" (for pdf_to_json.py structured output)
        # matches: { "subheading": "Name:", "content": ["John Doe"] }
        label = data.get("subheading") or data.get("heading")
        content = data.get("content")
        
        if label and content and isinstance(content, list) and len(content) > 0:
            # Clean the label: remove trailing colons and extra spaces ("Name:" -> "Name")
            clean_key = str(label).strip().rstrip(":")
            # Use the first text line as the value
            value = str(content[0])
            
            # Add to our flat map if not already present
            if clean_key not in extracted_fields:
                extracted_fields[clean_key] = value

        # 3. Iterate deeper
        for key, value in data.items():
            if isinstance(value, dict):
                flatten_json(value, extracted_fields)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        flatten_json(item, extracted_fields)
            elif isinstance(value, (str, int, float, bool)):
                # If it's a leaf node, likely a flat key-value pair
                extracted_fields[key] = str(value)
                    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                flatten_json(item, extracted_fields)

    return extracted_fields


def fill_pdf(json_path: str, pdf_template_path: str, output_path: str):
    """
    Fill the PDF widgets with data from JSON.
    """
    print(f"{'='*60}")
    print(f"  Source JSON:    {json_path}")
    print(f"  Template PDF:   {pdf_template_path}")
    print(f"  Output PDF:     {output_path}")
    print(f"{'='*60}")

    # 1. Load Data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Flatten/Extract Data
    form_data = flatten_json(data)
    print(f"  [INFO] Found {len(form_data)} potential data fields in JSON.")

    # 3. Open PDF
    doc = fitz.open(pdf_template_path)
    if doc.is_encrypted:
        print("  [ERROR] PDF is encrypted. Cannot populate fields.")
        return

    # Force PDF viewers to re-render field appearances
    # This is the key fix for blank fields
    try:
        if doc.is_form_pdf:
            doc.xref_set_key(doc.pdf_catalog(), "AcroForm/NeedAppearances", "true")
    except Exception:
        pass  # Not critical, some PDFs don't have AcroForm

    filled_count = 0
    not_found_count = 0

    # 4. Iterate over pages and widgets
    for page_num, page in enumerate(doc):
        # Get all widgets on the page
        widgets = page.widgets()
        if not widgets:
            continue
            
        for widget in widgets:
            field_name = widget.field_name
            if not field_name:
                continue

            # Try to find a value for this field
            if field_name in form_data:
                fill_value = form_data[field_name]
                
                # Update the widget
                widget.field_value = fill_value
                widget.text_fontsize = 0  # Auto-fit text to field size
                
                # Persist the change and regenerate appearance stream
                try:
                    widget.update() 
                    filled_count += 1
                except Exception as e:
                    print(f"  [WARN] Failed to update field '{field_name}': {e}")
            else:
                 # Optional: print(f"Field not found in JSON: {field_name}")
                 not_found_count += 1

    # 5. Save output with clean rendering
    try:
        doc.save(output_path, garbage=3, deflate=True)
        print(f"  [OK] Successfully filled PDF. Saved to: {output_path}")
        print(f"       Total Fields Filled: {filled_count}")
        print(f"       Total Matches Missed: {not_found_count} (Fields in PDF but not in text)")
    except Exception as e:
        print(f"  [ERROR] Failed to save PDF: {e}")
    finally:
        doc.close()

    print(f"{'='*60}\n")


def generate_template(pdf_path: str, json_output_path: str):
    """
    Scans a PDF for form fields and generates a blank JSON template.
    """
    print(f"{'='*60}")
    print(f"  Scanning PDF:   {pdf_path}")
    print(f"  Output JSON:    {json_output_path}")
    print(f"{'='*60}")

    doc = fitz.open(pdf_path)
    fields = {}
    
    for page in doc:
        for widget in page.widgets():
            if widget.field_name:
                fields[widget.field_name] = ""
    
    doc.close()

    if not fields:
        print("  [WARN] No form fields found in this PDF!")
    else:
        print(f"  [INFO] Found {len(fields)} form fields.")

    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(fields, f, indent=2)
    
    print(f"  [OK] Saved blank template to: {json_output_path}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Fill a PDF form from JSON, or scan a PDF to generate a JSON template.")
    
    # Mode 1: Fill PDF (default)
    parser.add_argument("input", nargs="?", help="Input JSON file (or PDF file if using --scan)")
    parser.add_argument("template", nargs="?", help="Template PDF file (or Output JSON if using --scan)")
    parser.add_argument("output", nargs="?", help="Output PDF file")
    
    # Mode 2: Scan PDF
    parser.add_argument("--scan", action="store_true", help="Scan the input PDF and generate a blank JSON template")

    args = parser.parse_args()

    # Handle Scan Mode
    if args.scan:
        if not args.input or not args.template:
            print("Usage for scan: python json_to_pdf.py --scan <input_pdf> <output_json>")
            sys.exit(1)
        
        pdf_path = args.input
        json_out = args.template
        
        if not os.path.exists(pdf_path):
             print(f"Error: PDF file not found: {pdf_path}")
             sys.exit(1)
             
        generate_template(pdf_path, json_out)
        return

    # Handle Fill Mode (Standard)
    if not args.input or not args.template:
        parser.print_help()
        sys.exit(1)

    json_path = args.input
    pdf_path = args.template
    
    if args.output:
        out_path = args.output
    else:
        base = os.path.splitext(pdf_path)[0]
        out_path = f"{base}_filled.pdf"

    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)
        
    if not os.path.exists(pdf_path):
        print(f"Error: PDF template not found: {pdf_path}")
        sys.exit(1)

    fill_pdf(json_path, pdf_path, out_path)


if __name__ == "__main__":
    main()
