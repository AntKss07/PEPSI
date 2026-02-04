"""
Test script for PDF extraction and field mapping
"""
import json
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from services.field_mapper import extract_and_map

# Get project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Test with example PDF
pdf_path = os.path.join(PROJECT_ROOT, "data", "Health and wellness guide example.pdf")

print("=" * 60)
print("Testing PDF Extraction")
print("=" * 60)

try:
    result = extract_and_map(pdf_path)
    
    # Count filled fields
    filled = sum(1 for v in result.values() if v)
    total = len(result)
    
    print(f"\nTotal fields: {total}")
    print(f"Filled fields: {filled}")
    print(f"Extraction rate: {filled/total*100:.1f}%")
    
    # Show key fields
    print("\n" + "=" * 60)
    print("Key Extracted Values:")
    print("=" * 60)
    
    key_fields = ["patient_name", "patient_id", "date_of_birth", 
                  "my_purpose", "health_goal_1", "health_goal_1_importance", 
                  "health_goal_2", "health_goal_3", "clinical_summary", "bmi_value"]
    
    for field in key_fields:
        value = result.get(field, {})
        if isinstance(value, dict):
            display_value = value.get("value", "")
        else:
            display_value = value
        display_value = display_value[:80] + "..." if len(str(display_value)) > 80 else display_value
        status = "✓" if display_value else "✗"
        print(f"{status} {field}: {display_value or '(empty)'}")
    
    # Save full output
    output_path = os.path.join(PROJECT_ROOT, "docs", "sample_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nFull output saved to: {output_path}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
