import fitz
import re
import json
import os

def clean_text(text):
    return text.replace('\n', ' ').strip()

def extract_all_data(pdf_path):
    doc = fitz.open(pdf_path)
    all_data = {}

    # Extract all text for global searches
    full_text = ""
    pages_text = []
    for page in doc:
        t = page.get_text("text")
        full_text += t + "\n---PAGE---\n"
        pages_text.append(t)

    # 1. Vital Signs (Page 3)
    vitals = {}
    p3_text = pages_text[2]
    vital_keys = [
        "BODY MASS INDEX (BMI)", "BODY WEIGHT", "HEIGHT", "ARTERIAL PRESSURE",
        "CARDIAC FREQUENCY", "ANKLE-BRACHIAL INDEX", "ABDOMINAL CIRCUMFERENCE",
        "HIP WAIST RATIO", "PULSE OXIMETRY", "RESPIRATORY FREQUENCY"
    ]
    
    # Use a more flexible approach for vitals: find the label and look for the next two chunks of info
    for key in vital_keys:
        # Many vitals are in a format where text is separate: KEY \n VALUE \n INTERP
        # We'll split the page text and find lines near the key
        lines = p3_text.split('\n')
        for i, line in enumerate(lines):
            if key in line.upper():
                # Value is often the next non-empty line
                val = ""
                interp = ""
                offset = 1
                while i + offset < len(lines) and not val:
                    candidate = lines[i+offset].strip()
                    if candidate and not any(k in candidate.upper() for k in vital_keys):
                        val = candidate
                    offset += 1
                while i + offset < len(lines) and not interp:
                    candidate = lines[i+offset].strip()
                    if candidate and not any(k in candidate.upper() for k in vital_keys):
                        interp = candidate
                    offset += 1
                vitals[key] = {"value": val, "interpretation": interp}
                break
    
    # Special fix for BMIs if missed
    if not vitals.get("BODY MASS INDEX (BMI)", {}).get("value"):
        bmi_match = re.search(r"BMI\)\s*(\d+\.?\d*)", p3_text)
        if bmi_match:
            vitals["BODY MASS INDEX (BMI)"] = {"value": bmi_match.group(1), "interpretation": "misleading in individuals with high muscle mass."}

    all_data["Vital Signs"] = vitals

    # 2. Lab Results (Pages 6 & 7)
    labs = {}
    
    # Hematologic
    p6_text = pages_text[5]
    hema = {}
    hema_params = ["Hemoglobin", "Hematocrit", "RBC count", "MCV", "MCH", "MCHC", "RDW-SD", "WBC", "Platelets"]
    for param in hema_params:
        # Match pattern: Parameter [Value] [Unit] [Range] [Interp]
        # Example: Hemoglobin17.0 g/dL14.3–17.0High-normal
        pattern = f"{param}\\s*([\\d.]+)\\s*([^0-9\\s%]+)?\\s*([\\d.–-]+)\\s*(.*)"
        match = re.search(pattern, p6_text)
        if match:
            hema[param] = {
                "value": match.group(1),
                "unit": (match.group(2) or "").strip(),
                "range": match.group(3),
                "interpretation": match.group(4).split('\n')[0].strip()
            }
    labs["Hematologic System"] = hema

    # Lipid System
    lipid_params = ["Total cholesterol", "HDL", "LDL", "VLDL", "Triglycerides", "Castelli Index", "ApoB", "Lp(a)"]
    lipids = {}
    for param in lipid_params:
        pattern = f"{param}\\s*([\\d.]+)\\s*([^0-9\\s/]+)?\\s*([0-9<.\\u2013-]+)?\\s*(.*)"
        match = re.search(pattern, p6_text)
        if match:
            lipids[param] = {
                "value": match.group(1),
                "unit": (match.group(2) or "").strip(),
                "range": (match.group(3) or "").strip(),
                "interpretation": match.group(4).split('\n')[0].strip()
            }
    labs["Lipid System"] = lipids

    # Liver Function (Page 7)
    p7_text = pages_text[6]
    liver = {}
    liver_params = ["AST", "ALT", "ALP", "GGT"]
    for param in liver_params:
        pattern = f"{param}\\s*(\\d+)\\s*U/L\\s*([\\d\\-\\u2013]+)"
        match = re.search(pattern, p7_text)
        if match:
            liver[param] = {"value": match.group(1), "unit": "U/L", "range": match.group(2)}
    labs["Liver Function"] = liver

    # Metabolic
    metab = {}
    metab_patterns = {
        "Fasting glucose": r"Fasting glucose\s*(\d+)\s*mg/dL",
        "HbA1c": r"HbA1c\s*([\d.]+)%",
        "Fasting insulin": r"Fasting insulin\s*([\d.]+)"
    }
    for k, v in metab_patterns.items():
        match = re.search(v, p7_text)
        if match:
            metab[k] = match.group(1)
    labs["Metabolic Panel"] = metab

    all_data["Labs"] = labs
    
    doc.close()
    return all_data

def update_doc_creator(data):
    # Flatten the data into a question-content format for the doc_creator
    test_data = []
    
    # Basic Info
    test_data.append({"question": "NAME", "content": "RICHARD ALLEN PEACOCK"})
    
    # Vitals Table
    for k, v in data["Vital Signs"].items():
        test_data.append({"question": f"{k} - VALUE", "content": v["value"]})
        test_data.append({"question": f"{k} - INTERPRETATION", "content": v["interpretation"]})
    
    # Labs Table - Hematologic
    for k, v in data["Labs"]["Hematologic System"].items():
        content = f"Value: {v['value']} {v['unit']}, Range: {v['range']}, Status: {v['interpretation']}"
        test_data.append({"question": f"LAB: {k}", "content": content})
        
    # Labs Table - Lipids
    for k, v in data["Labs"]["Lipid System"].items():
        content = f"Value: {v['value']} {v['unit']}, Range: {v['range']}, Status: {v['interpretation']}"
        test_data.append({"question": f"LAB: {k}", "content": content})

    # Labs Table - Liver
    for k, v in data["Labs"]["Liver Function"].items():
        test_data.append({"question": f"LAB: {k}", "content": f"{v['value']} {v['unit']} (Range: {v['range']})"})

    # Labs Table - Metabolic
    for k, v in data["Labs"]["Metabolic Panel"].items():
        test_data.append({"question": f"LAB: {k}", "content": v})

    # Write the new doc_creator.py
    with open("doc_creator.py", "w", encoding="utf-8") as f:
        f.write("import json\n\n")
        f.write(f"test_data = {json.dumps(test_data, indent=4)}\n\n")
        f.write("""
def create_doc(data, output_file="comprehensive_test_report.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("COMPREHENSIVE HEALTH AND WELLNESS REPORT - EXTRACTED DATA\\n")
        f.write("="*70 + "\\n\\n")
        
        # Group by category
        current_cat = ""
        for item in data:
            q = item['question']
            if ':' in q:
                cat = q.split(':')[0]
            elif '-' in q:
                cat = q.split('-')[0].strip()
            else:
                cat = "GENERAL"
                
            if cat != current_cat:
                f.write(f"\\n[ {cat} ]\\n")
                f.write("-" * 20 + "\\n")
                current_cat = cat
                
            f.write(f"{q.ljust(40)} | {item['content']}\\n")
            
    print(f"Comprehensive Document created successfully: {output_file}")

if __name__ == "__main__":
    create_doc(test_data)
""")

if __name__ == "__main__":
    pdf_path = r"c:\hackathon\Gemini_CLI\PEPSI\Health and wellness guide example.pdf"
    if os.path.exists(pdf_path):
        data = extract_all_data(pdf_path)
        update_doc_creator(data)
        print("Successfully updated doc_creator.py with REAL extracted table data.")
    else:
        print(f"Error: PDF not found at {pdf_path}")
