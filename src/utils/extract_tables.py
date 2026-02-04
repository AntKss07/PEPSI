import fitz
import re
import json

def extract_tables_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_tables = {}

    # Page 3: Vital Signs Table
    page3 = doc[2]
    text3 = page3.get_text("text")
    vitals = {}
    vital_patterns = [
        "BODY MASS INDEX (BMI)", "BODY WEIGHT", "HEIGHT", "ARTERIAL PRESSURE",
        "CARDIAC FREQUENCY", "ABDOMINAL CIRCUMFERENCE", "HIP WAIST RATIO",
        "PULSE OXIMETRY", "RESPIRATORY FREQUENCY"
    ]
    
    for pattern in vital_patterns:
        # Search for pattern followed by value and interpretation
        match = re.search(f"{re.escape(pattern)}\\s*\\n?([^\\n]+)\\s*\\n?([^\\n]+)", text3)
        if match:
            vitals[pattern] = {
                "value": match.group(1).strip(),
                "interpretation": match.group(2).strip()
            }
    extracted_tables["Vital Signs"] = vitals

    # Page 6 & 7: Laboratory Results Table
    lab_results = {}
    for page_num in [5, 6]: # Pages 6 and 7 (0-indexed)
        page = doc[page_num]
        text = page.get_text("text")
        
        # Hematologic System
        if "Hematologic System" in text:
            hema = {}
            lines = text.split("\n")
            # Hemoglobin17.0 g/dL14.3–17.0High-normal
            # Pattern: NameValueUnitReferenceInterpretation
            params = ["Hemoglobin", "Hematocrit", "RBC count", "MCV", "MCH", "MCHC", "RDW-SD", "WBC", "Platelets"]
            for param in params:
                pattern = f"{param}\\s*([\\d.]+)\\s*([^0-9\\s]+)?\\s*([\\d.–-]+)\\s*(.*)"
                match = re.search(pattern, text)
                if match:
                    hema[param] = {
                        "value": match.group(1),
                        "unit": match.group(2) or "",
                        "reference": match.group(3),
                        "interpretation": match.group(4).strip()
                    }
            lab_results["Hematologic System"] = hema

        # Cardiovascular / Lipid System
        if "Cardiovascular / Lipid" in text:
            lipids = {}
            params = ["Total cholesterol", "HDL", "LDL", "VLDL", "Triglycerides", "Castelli Index", "ApoB", "Lp(a)"]
            for param in params:
                pattern = f"{param}\\s*([\\d.]+)\\s*([^0-9\\s/]+)?\\s*([\\d.–-]+|\\s*<[^\\s]+)?\\s*(.*)"
                match = re.search(pattern, text)
                if match:
                    lipids[param] = {
                        "value": match.group(1),
                        "unit": match.group(2) or "",
                        "reference": match.group(3) or "",
                        "interpretation": match.group(4).strip()
                    }
            lab_results["Cardiovascular / Lipid System"] = lipids

    extracted_tables["Laboratory Results"] = lab_results
    doc.close()
    return extracted_tables

if __name__ == "__main__":
    pdf_path = r"c:\hackathon\Gemini_CLI\PEPSI\Health and wellness guide example.pdf"
    tables = extract_tables_from_pdf(pdf_path)
    print(json.dumps(tables, indent=2))
    
    with open("extracted_tables.json", "w", encoding="utf-8") as f:
        json.dump(tables, f, indent=2)
    print("\nSaved to extracted_tables.json")
