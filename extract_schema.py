"""
Script to extract form fields from the fillable PDF to understand the schema
"""
import fitz  # PyMuPDF
import json
from collections import defaultdict

def extract_form_fields(pdf_path):
    """Extract all form fields from a PDF"""
    doc = fitz.open(pdf_path)
    fields = []
    
    for page_num, page in enumerate(doc):
        # Get form widgets (fields) on this page
        for widget in page.widgets():
            field_info = {
                "field_name": widget.field_name,
                "field_type": widget.field_type_string,
                "field_value": widget.field_value,
                "page": page_num + 1,
                "rect": list(widget.rect),
            }
            fields.append(field_info)
    
    doc.close()
    return fields

def extract_text_content(pdf_path):
    """Extract text content from a PDF"""
    doc = fitz.open(pdf_path)
    content = []
    
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        content.append({
            "page": page_num + 1,
            "text": text
        })
    
    doc.close()
    return content

# Extract from fillable PDF
print("=" * 60)
print("EXTRACTING FORM FIELDS FROM FILLABLE PDF")
print("=" * 60)

fillable_pdf = r"c:\KSS\PROJECTS\PEPSI\HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf"
fields = extract_form_fields(fillable_pdf)

print(f"\nFound {len(fields)} form fields:")
print("-" * 60)

# Group by field type
by_type = defaultdict(list)
for f in fields:
    by_type[f["field_type"]].append(f)

for ftype, field_list in by_type.items():
    print(f"\n{ftype} fields ({len(field_list)}):")
    for f in field_list:
        print(f"  - {f['field_name']} (page {f['page']})")

# Save fields to JSON for reference
with open("form_fields_schema.json", "w") as f:
    json.dump(fields, f, indent=2)

print("\n\nSaved complete schema to form_fields_schema.json")

# Also extract text from fillable PDF for context
print("\n" + "=" * 60)
print("EXTRACTING TEXT CONTENT FROM FILLABLE PDF")
print("=" * 60)

text_content = extract_text_content(fillable_pdf)
for page in text_content:
    print(f"\n--- Page {page['page']} ---")
    print(page['text'][:2000])  # First 2000 chars per page

# Save text content
with open("fillable_pdf_text.json", "w") as f:
    json.dump(text_content, f, indent=2)

print("\n\nSaved text content to fillable_pdf_text.json")
