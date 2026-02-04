"""
Compare extracted JSON with fillable PDF schema
"""
import json

# Load the fillable PDF schema
with open("form_fields_schema.json", "r") as f:
    schema_fields = json.load(f)

# Load the extracted data
with open("sample_output.json", "r", encoding="utf-8") as f:
    extracted_data = json.load(f)

print("=" * 80)
print("COMPARISON: Extracted JSON vs Fillable PDF Schema")
print("=" * 80)

# Get all field names from schema
schema_field_names = [field["field_name"] for field in schema_fields]

print(f"\nSchema Fields Count: {len(schema_field_names)}")
print(f"Extracted Fields Count: {len(extracted_data)}")

# Check for missing fields in extraction
missing_from_extraction = [name for name in schema_field_names if name not in extracted_data]
extra_in_extraction = [name for name in extracted_data.keys() if name not in schema_field_names]

print(f"\n{'='*80}")
print("FIELD COVERAGE ANALYSIS")
print("=" * 80)

if missing_from_extraction:
    print(f"\n[!] Fields in Schema but MISSING from Extracted JSON ({len(missing_from_extraction)}):")
    for name in missing_from_extraction:
        print(f"   - {name}")
else:
    print("\n[OK] All schema fields are present in extracted JSON")

if extra_in_extraction:
    print(f"\n[!] Fields in Extracted JSON but NOT in Schema ({len(extra_in_extraction)}):")
    for name in extra_in_extraction:
        print(f"   - {name}")
else:
    print("\n[OK] No extra fields in extracted JSON")

# Field-by-field comparison
print(f"\n{'='*80}")
print("FIELD VALUE STATUS")
print("=" * 80)

filled_fields = []
empty_fields = []

for field in schema_fields:
    field_name = field["field_name"]
    page = field["page"]
    
    if field_name in extracted_data:
        value = extracted_data[field_name]
        if value and value.strip():
            filled_fields.append({
                "name": field_name,
                "page": page,
                "value_preview": value[:60].replace("\n", " ") + ("..." if len(value) > 60 else "")
            })
        else:
            empty_fields.append({"name": field_name, "page": page})

print(f"\n[FILLED] Fields with Values ({len(filled_fields)}/{len(schema_field_names)}):")
print("-" * 80)
print(f"{'Field Name':<30} {'Page':<6} {'Value Preview':<40}")
print("-" * 80)
for field in filled_fields:
    print(f"{field['name']:<30} {field['page']:<6} {field['value_preview']:<40}")

print(f"\n[EMPTY] Fields without Values ({len(empty_fields)}/{len(schema_field_names)}):")
print("-" * 80)
# Group by page
from collections import defaultdict
by_page = defaultdict(list)
for field in empty_fields:
    by_page[field["page"]].append(field["name"])

for page in sorted(by_page.keys()):
    fields = by_page[page]
    print(f"Page {page}: {', '.join(fields[:5])}{'...' if len(fields) > 5 else ''} ({len(fields)} fields)")

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print("=" * 80)
extraction_rate = len(filled_fields) / len(schema_field_names) * 100
print(f"Total Schema Fields:    {len(schema_field_names)}")
print(f"Fields with Values:     {len(filled_fields)}")
print(f"Empty Fields:           {len(empty_fields)}")
print(f"Extraction Rate:        {extraction_rate:.1f}%")

# Key fields status
print(f"\n{'='*80}")
print("KEY FIELDS STATUS")
print("=" * 80)
key_fields = ["Name", "Identification number", "Date of birth", "My Purpose",
              "HealthGoal1", "Imp1", "Healthgoal2", "Imp2", "Healthgoal3", "Imp3",
              "Summary", "FuncMedApproach", "bmivalue", "Additional parameter"]

for kf in key_fields:
    if kf in extracted_data:
        val = extracted_data[kf]
        status = "[OK]" if val else "[--]"
        preview = val[:50].replace("\n", " ") + "..." if val and len(val) > 50 else (val.replace("\n", " ") if val else "(empty)")
        print(f"{status} {kf:<25}: {preview}")
    else:
        print(f"[--] {kf:<25}: NOT IN OUTPUT")
