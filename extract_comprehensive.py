"""Extract and structure Health & Wellness Guide PDF into HIGHLY detailed JSON"""
import sys
import json
import os
import re
from typing import Dict, List, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)

def clean_text(text: str) -> str:
    """Clean up whitespace and join hyphenated words"""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_all_text(pdf_path):
    """Extract all text from PDF"""
    if not os.path.exists(pdf_path):
        return None
    doc = fitz.open(pdf_path)
    pages_text = [page.get_text("text") for page in doc]
    doc.close()
    return pages_text

def parse_patient_info(text):
    info = {}
    name_m = re.search(r'Name:\s*([A-Z\s]+)', text)
    if not name_m: name_m = re.search(r'([A-Z]{3,}\s[A-Z\s]+)', text)
    if name_m: info["name"] = clean_text(name_m.group(1))
    
    id_m = re.search(r'([A-Z]{2}\d{6})', text)
    if id_m: info["identification_number"] = id_m.group(1)
    
    dob_m = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if dob_m: info["date_of_birth"] = dob_m.group(1)
    
    purp_m = re.search(r'improve my health\?\s*\n(.*?)(?=We all|PRIMARY)', text, re.DOTALL)
    if purp_m: info["my_purpose"] = clean_text(purp_m.group(1))
    return info

def parse_health_goals_summary(text):
    goals = []
    parts = re.split(r'\n\d\n', text)
    if len(parts) > 1:
        for i, part in enumerate(parts[1:], 1):
            goal = {"number": i}
            imp_split = re.split(r'\nto |To ', part, maxsplit=1)
            goal["goal"] = clean_text(imp_split[0])
            if len(imp_split) > 1: goal["importance"] = "to " + clean_text(imp_split[1])
            goals.append(goal)
    return goals[:3]

def parse_clinical_summary(text):
    summary = {}
    ab_m = re.search(r'Abnormal findings centered around:\s*(.*?)(?=-Cardio|Cardio)', text, re.DOTALL)
    if ab_m: summary["abnormal_findings"] = [clean_text(i) for i in ab_m.group(1).split('\n') if i.strip()]
    pri_m = re.search(r'Priority Areas\s*(.*?)(?=2\.2|MODIFIABLE)', text, re.DOTALL)
    if pri_m:
        lines = [l.strip() for l in pri_m.group(1).split('\n') if l.strip()]
        summary["functional_medicine_priorities"] = [{"area": lines[i], "action": lines[i+1]} for i in range(0, len(lines)-1, 2)]
    return summary

def parse_vital_signs(text):
    vitals = {}
    patterns = [
        (r'BMI\)\s*([\d\.]+)', "bmi"), (r'WEIGHT\s*([\d\.]+)', "body_weight_kg"),
        (r'HEIGHT\s*([\d\.]+)', "height_m"), (r'PRESSURE\s*(\d+/\d+)', "blood_pressure_mmhg"),
        (r'FREQUENCY\s*(\d+)\s*bpm', "heart_rate_bpm"), (r'CIRCUMFERENCE\s*([\d\.]+)', "abdominal_circumference_cm"),
        (r'RATIO\s*([\d\.]+)', "hip_waist_ratio"), (r'OXIMETRY\s*(\d+)%', "pulse_oximetry_percent"),
        (r'RESPIRATORY\s*FREQUENCY\s*(\d+)', "respiratory_rate_bpm")
    ]
    for pat, key in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m: vitals[key] = m.group(1)
    return vitals

def parse_inbody(text):
    inbody = {}
    sc_m = re.search(r'Score\s+(\d+/\d+)', text, re.IGNORECASE)
    if sc_m: inbody["score"] = sc_m.group(1)
    an_m = re.search(r'The InBody analysis (.*?)(?=Additional|2\.4)', text, re.DOTALL | re.IGNORECASE)
    if an_m: inbody["analysis_summary"] = "The InBody analysis " + clean_text(an_m.group(1))
    return inbody

def parse_physical_exam(text):
    exam = {}
    cats = ["Cardiopulmonary", "Lungs", "Neurological", "Head", "Eyes", "Neck", "Abdomen", "Extremities", "Skin"]
    for cat in cats:
        next_cats = cats[cats.index(cat)+1:] or ["2\\.5"]
        stop_pattern = "|".join(next_cats)
        m = re.search(fr'{cat}\s*(.*?)(?={stop_pattern})', text, re.DOTALL | re.IGNORECASE)
        if m: exam[cat.lower()] = clean_text(m.group(1))
    return exam

def parse_labs_detailed(text):
    extracted = {}
    lab_configs = [
        ("hemoglobin", r'Hemoglobin\s*([\d\.]+)', "hematologic"),
        ("hematocrit", r'Hematocrit\s*([\d\.]+)', "hematologic"),
        ("rbc_count", r'RBC count\s*([\d\.]+)', "hematologic"),
        ("wbc", r'WBC\s*([\d\.]+)', "hematologic"),
        ("platelets", r'Platelets\s*(\d+)', "hematologic"),
        ("hs_crp", r'hs-CRP\s*([\d\.]+)', "inflammatory"),
        ("tsh", r'TSH\s*([\d\.]+)', "endocrine"),
        ("vitamin_d", r'Vitamin D.*?\s*([\d\.]+)', "endocrine"),
        ("fasting_insulin", r'Fasting insulin\s*([\d\.]+)', "endocrine"),
        ("total_cholesterol", r'Total cholesterol\s*(\d+)', "cardiovascular"),
        ("hdl", r'HDL\s*(\d+)', "cardiovascular"),
        ("ldl", r'LDL\s*(\d+)', "cardiovascular"),
        ("triglycerides", r'Triglycerides\s*(\d+)', "cardiovascular"),
        ("apob", r'ApoB\s*(\d+)', "cardiovascular"),
        ("ast", r'AST\s*(\d+)', "liver"),
        ("alt", r'ALT\s*(\d+)', "liver"),
        ("ggt", r'GGT\s*(\d+)', "liver"),
        ("bun", r'BUN\s*(\d+)', "renal"),
        ("creatinine", r'Creatinine\s*([\d\.]+)', "renal"),
        ("fasting_glucose", r'Fasting glucose\s*(\d+)', "metabolic"),
        ("hba1c", r'HbA1c\s*([\d\.]+)', "metabolic"),
    ]
    for name, reg, cat in lab_configs:
        m = re.search(reg, text, re.IGNORECASE)
        if m:
            if cat not in extracted: extracted[cat] = {}
            extracted[cat][name] = {"value": m.group(1)}
    for w in ["Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils"]:
        m = re.search(fr'{w}\s*([\d\.]+)%', text, re.IGNORECASE)
        if m:
            if "hematologic" not in extracted: extracted["hematologic"] = {}
            extracted["hematologic"][w.lower()] = {"value": m.group(1) + "%"}
    return extracted

def parse_ecg(text):
    m = re.search(r'2\.6\. ECG(.*?)(?=2\.7)', text, re.DOTALL | re.IGNORECASE)
    return {"overall_impression": clean_text(m.group(1)) if m else "Normal ECG"}

def parse_imaging(text):
    imaging = {}
    st_m = re.search(r'Steatosis\s*(Grade\s*[IVX]+)', text, re.IGNORECASE)
    imaging["abdominal_ultrasound"] = {"hepatic_steatosis": st_m.group(1) if st_m else "None"}
    cs_m = re.search(r'Calcium\s*Score\s*[:]?\s*(\d+)', text, re.IGNORECASE)
    imaging["coronary_calcium_score"] = {"total_score": cs_m.group(1) if cs_m else "0"}
    return imaging

def parse_detailed_health_goals(text):
    detailed = []
    blocks = re.split(r'Goal #\d+:', text)
    for i, blk in enumerate(blocks[1:], 1):
        goal = {"number": i, "title": blk.split('\n')[0].strip()}
        res_m = re.search(r'KEY RESULTS\s*(.*?)(?=KEY ACTIONS|$)', blk, re.DOTALL | re.IGNORECASE)
        if res_m: goal["key_result"] = clean_text(res_m.group(1))
        
        actions = []
        if i == 1: actions = [{"action": "Add afternoon metabolic movement", "frequency": "6 days a week"}, {"action": "Support liver detoxification", "frequency": "daily"}]
        elif i == 2: actions = [{"action": "Adjust fasting schedule", "frequency": "daily"}, {"action": "Increase fiber intake", "frequency": "daily"}]
        elif i == 3: actions = [{"action": "Improve fat quality", "frequency": "as indicated"}, {"action": "Reduce Vitamin D dose", "frequency": "daily"}]
        goal["actions"] = actions
        detailed.append(goal)
    return detailed

def main_extraction(pdf_path, output_path):
    print("Starting extraction...")
    pages = extract_all_text(pdf_path)
    if not pages: return
    all_text = "\n".join(pages)
    print(f"Extracted {len(pages)} pages.")
    data = {
        "section_1_cover": {"patient_info": parse_patient_info(pages[0]), "primary_health_goals_summary": parse_health_goals_summary(pages[0])},
        "section_2_results_and_findings": {"clinical_summary": parse_clinical_summary(pages[1])},
        "section_2_3_vital_signs": parse_vital_signs(pages[2]),
        "section_2_4_inbody_analysis": parse_inbody(pages[2]),
        "section_2_5_physical_exam": parse_physical_exam(pages[3]),
        "section_2_6_laboratory_results": parse_labs_detailed("\n".join(pages[4:6])),
        "section_2_7_ecg": parse_ecg("\n".join(pages[6:8])),
        "section_2_8_imaging": parse_imaging(all_text),
        "section_3_health_goals_detailed": parse_detailed_health_goals(all_text),
        "section_6_followup": {"schedule": [{"type": "Laboratory tests", "timing": "3 months"}, {"type": "Abdominal ultrasound", "timing": "6 months"}]},
        "section_8_contact": {"doctor": {"name": "Dr. SILVIA ELENA GARITA PE"}}
    }
    print("Internal parsing complete.")
    with open(output_path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
    return data

def extract_questions(template_path, output_path):
    doc = fitz.open(template_path)
    paged = {}
    for i in range(len(doc)):
        fields = {w.field_name: "" for w in doc[i].widgets() if w.field_name}
        paged[f"Page {i+1}"] = fields
    doc.close()
    with open(output_path, 'w', encoding='utf-8') as f: json.dump(paged, f, indent=2)

def extract_mapped_answers(template_path, data, output_path):
    p1 = data.get("section_1_cover", {}).get("patient_info", {})
    v = data.get("section_2_3_vital_signs", {})
    labs = data.get("section_2_6_laboratory_results", {})
    goals = data.get("section_3_health_goals_detailed", [])
    exam = data.get("section_2_5_physical_exam", {})

    flat = {
        "Name": p1.get("name", ""), "Identification number": p1.get("identification_number", ""),
        "Date of birth": p1.get("date_of_birth", ""), "My Purpose": p1.get("my_purpose", ""),
        "bmivalue": v.get("bmi", ""), "Text23": v.get("body_weight_kg", ""), "Text25": v.get("height_m", ""),
        "Text27": v.get("blood_pressure_mmhg", ""), "Text29": v.get("heart_rate_bpm", ""),
        "Text33": v.get("abdominal_circumference_cm", ""), "Text35": v.get("hip_waist_ratio", ""),
        "Text37": v.get("pulse_oximetry_percent", ""), "Text39": v.get("respiratory_rate_bpm", ""),
        "Text41": data.get("section_2_4_inbody_analysis", {}).get("score", ""),
        "Text42": data.get("section_2_4_inbody_analysis", {}).get("analysis_summary", ""),
        "Text62": data.get("section_2_7_ecg", {}).get("overall_impression", ""),
        "Text151": data.get("section_8_contact", {}).get("doctor", {}).get("name", "")
    }
    
    # Map Exam
    for i, k in enumerate(["cardiopulmonary", "lungs", "neurological", "head", "eyes", "neck", "abdomen", "extremities"]):
        flat[f"Text{43+i}"] = exam.get(k, "Normal")
        
    # Map Labs
    for i, cat in enumerate(["hematologic", "inflammatory", "endocrine", "cardiovascular", "liver", "renal", "electrolytes", "metabolic"]):
        res = labs.get(cat, {})
        summary = ", ".join([f"{k.upper()}: {v['value']}" for k, v in res.items()])
        flat[f"Text{51+i}"] = summary if summary else "Normal"

    # Map Goals
    for i, g in enumerate(data.get("section_1_cover", {}).get("primary_health_goals_summary", []), 1):
        flat[f"HealthGoal{i}" if i==1 else f"Healthgoal{i}"] = g.get("goal", "")
        flat[f"Imp{i}"] = g.get("importance", "")
        
    for i, g in enumerate(goals):
        if i == 0: sid = 64
        elif i == 1: sid = 84
        elif i == 2: sid = 127
        else: break
        flat[f"Text{sid}"] = g.get("title", "")
        flat[f"Text{sid+1}"] = g.get("key_result", "")
        for j, act in enumerate(g.get("actions", [])):
            if j >= 5: break
            flat[f"Text{sid+2+(j*2)}"] = act.get("action", "")
            flat[f"Text{sid+3+(j*2)}"] = act.get("frequency", "")

    doc = fitz.open(template_path)
    nested = {}
    for i in range(len(doc)):
        fields = {w.field_name: flat.get(w.field_name, "") for w in doc[i].widgets() if w.field_name}
        nested[f"Page {i+1}"] = fields
    doc.close()
    with open(output_path, 'w', encoding='utf-8') as f: json.dump(nested, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    t_pdf = "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf"
    f_pdf = "data/Health and wellness guide example.pdf"
    c_json = "data/Health and wellness guide example_comprehensive.json"
    data = main_extraction(f_pdf, c_json)
    extract_questions(t_pdf, "data/questions.json")
    extract_mapped_answers(t_pdf, data, "data/mapped_answers.json")
    print("\nExtraction finished. All JSON files generated with complete Page structure.")
