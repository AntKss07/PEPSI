"""
Generate comparison report as JSON for analysis
"""
import json

# Load the fillable PDF schema
with open("form_fields_schema.json", "r") as f:
    schema_fields = json.load(f)

# Load the extracted data
with open("sample_output.json", "r", encoding="utf-8") as f:
    extracted_data = json.load(f)

# Get all field names from schema
schema_field_names = [field["field_name"] for field in schema_fields]
schema_field_lookup = {f["field_name"]: f for f in schema_fields}

# Build comparison
comparison = {
    "summary": {
        "schema_field_count": len(schema_field_names),
        "extracted_field_count": len(extracted_data),
        "perfect_match": set(schema_field_names) == set(extracted_data.keys())
    },
    "filled_fields": [],
    "empty_fields": []
}

for field_name in schema_field_names:
    page = schema_field_lookup[field_name]["page"]
    value = extracted_data.get(field_name, "")
    
    if value and value.strip():
        comparison["filled_fields"].append({
            "name": field_name,
            "page": page,
            "value": value[:200] + "..." if len(value) > 200 else value
        })
    else:
        comparison["empty_fields"].append({
            "name": field_name,
            "page": page
        })

comparison["summary"]["filled_count"] = len(comparison["filled_fields"])
comparison["summary"]["empty_count"] = len(comparison["empty_fields"])
comparison["summary"]["extraction_rate"] = round(len(comparison["filled_fields"]) / len(schema_field_names) * 100, 1)

# Save report
with open("comparison_report.json", "w", encoding="utf-8") as f:
    json.dump(comparison, f, indent=2, ensure_ascii=False)

# Print summary
print("SCHEMA vs EXTRACTED JSON COMPARISON")
print("=" * 50)
print(f"Schema Fields:      {comparison['summary']['schema_field_count']}")
print(f"Extracted Fields:   {comparison['summary']['extracted_field_count']}")
print(f"Fields Match:       {comparison['summary']['perfect_match']}")
print(f"Filled Fields:      {comparison['summary']['filled_count']}")
print(f"Empty Fields:       {comparison['summary']['empty_count']}")
print(f"Extraction Rate:    {comparison['summary']['extraction_rate']}%")
print()
print("FILLED FIELDS:")
for f in comparison["filled_fields"]:
    print(f"  Page {f['page']}: {f['name']}")
print()
print(f"Full report saved to: comparison_report.json")
