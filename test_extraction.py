"""
Test script for PDF extraction and field mapping
"""
import json
from field_mapper import extract_and_map

# Test with example PDF
pdf_path = r"c:\KSS\PROJECTS\PEPSI\Health and wellness guide example.pdf"

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
    
    key_fields = ["Name", "Identification number", "Date of birth", 
                  "My Purpose", "HealthGoal1", "Imp1", "Healthgoal2", 
                  "Healthgoal3", "Summary", "bmivalue"]
    
    for field in key_fields:
        value = result.get(field, "")
        display_value = value[:80] + "..." if len(value) > 80 else value
        status = "✓" if value else "✗"
        print(f"{status} {field}: {display_value or '(empty)'}")
    
    # Save full output
    output_path = r"c:\KSS\PROJECTS\PEPSI\sample_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nFull output saved to: {output_path}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
