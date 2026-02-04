"""
Test Document Creator - Generates a document showing the ordered JSON structure
with questions and extracted content arranged by PDF page order.
"""
import json
from collections import OrderedDict

# Sample extracted data in PDF reading order
ORDERED_EXTRACTED_DATA = OrderedDict([
    # ============== PAGE 1 - SECTION 1: MY PURPOSE ==============
    ("patient_name", {
        "page": 1,
        "section": "Section 1: My Purpose",
        "question": "Name",
        "value": "RICHARD ALLEN PEACOCK"
    }),
    ("patient_id", {
        "page": 1,
        "section": "Section 1: My Purpose",
        "question": "Identification number",
        "value": "AC737267"
    }),
    ("date_of_birth", {
        "page": 1,
        "section": "Section 1: My Purpose",
        "question": "Date of birth",
        "value": "11/07/1960"
    }),
    ("my_purpose", {
        "page": 1,
        "section": "Section 1: My Purpose",
        "question": "Why do I want to improve my health?",
        "value": "Me and my wife like to do hiking and enjoy outdoors and also I want to be healthy to be with my grandkids and kids."
    }),
    ("health_goal_1", {
        "page": 1,
        "section": "Section 1: My Purpose - Health Goals",
        "question": "Health Goal #1",
        "value": "Improve liver health by reducing inflammation and normalizing liver enzymes."
    }),
    ("health_goal_1_importance", {
        "page": 1,
        "section": "Section 1: My Purpose - Health Goals",
        "question": "Why is Health Goal #1 important?",
        "value": "to protect the liver, improves metabolism, reduces cardiovascular risk, and restores whole-body health."
    }),
    ("health_goal_2", {
        "page": 1,
        "section": "Section 1: My Purpose - Health Goals",
        "question": "Health Goal #2",
        "value": "Improve Insulin Sensitivity and Metabolic Flexibility"
    }),
    ("health_goal_2_importance", {
        "page": 1,
        "section": "Section 1: My Purpose - Health Goals",
        "question": "Why is Health Goal #2 important?",
        "value": "to prevent progression to type 2 diabetes"
    }),
    ("health_goal_3", {
        "page": 1,
        "section": "Section 1: My Purpose - Health Goals",
        "question": "Health Goal #3",
        "value": "Improve lipid balance and reduce long-term cardiovascular risk"
    }),
    ("health_goal_3_importance", {
        "page": 1,
        "section": "Section 1: My Purpose - Health Goals",
        "question": "Why is Health Goal #3 important?",
        "value": "to prevent progression of atherosclerosis."
    }),

    # ============== PAGE 2 - SECTION 2: RESULTS AND FINDINGS ==============
    ("clinical_summary", {
        "page": 2,
        "section": "Section 2: Results and Findings",
        "question": "2.1. SUMMARY",
        "value": "Richard shows:\nNormal findings in: CBC, Renal function, Thyroid, PSA, Electrolytes, Glucose metabolism, Urinalysis & stool exam, Lp(a) (excellent), Inflammatory markers only mildly elevated\n-Abnormal findings centered around:\nNAFLD grade II → Elevated AST/ALT, ferritin, low HDL, elevated LDL, mild insulin resistance\nVitamin D excess → 81.8 ng/mL\nApoB slightly elevated\nhs-CRP mildly elevated\n-Cardiovascular risk remains LOW because:\nCAC score = 15, Lp(a) extremely low, ApoB moderate, HDL low due to fatty liver, not arterial disease, High muscularity and high physical activity"
    }),
    ("functional_medicine_approach", {
        "page": 2,
        "section": "Section 2: Results and Findings",
        "question": "2.2. FUNCTIONAL MEDICINE APPROACH: MODIFIABLE LIFESTYLES AND DYSFUNCTIONS",
        "value": "Reverse NAFLD (primary goal)\nImprove liver detox phases, mitochondrial fat oxidation, hepatic glucose handling.\nImprove hepatic insulin sensitivity\nAdjust macronutrient timing; increase fiber and plants; adjust fructose load.\nLower inflammation\nThrough nutrition, circadian alignment, and omega-3.\nSupport mitochondrial function\nMaintain exercise, optimize micronutrients (magnesium, B-complex).\nNormalize Vitamin D\nReduce dose.\nImprove evening metabolic activity\nIntroduce low-intensity movement after 3–4 pm.\nDermatologic follow-up\nActinic keratosis & ulcerated lesion require evaluation."
    }),

    # ============== PAGE 3 - VITAL SIGNS ==============
    ("bmi_value", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "BODY MASS INDEX (BMI) - VALUE",
        "value": "31.1"
    }),
    ("bmi_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "BODY MASS INDEX (BMI) - INTERPRETATION",
        "value": "misleading in individuals with high muscle mass"
    }),
    ("body_weight", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "BODY WEIGHT - VALUE",
        "value": "109.9 kg"
    }),
    ("body_weight_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "BODY WEIGHT - INTERPRETATION",
        "value": "normal"
    }),
    ("height", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "HEIGHT - VALUE",
        "value": "1.88 m"
    }),
    ("height_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "HEIGHT - INTERPRETATION",
        "value": "normal"
    }),
    ("blood_pressure", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "ARTERIAL PRESSURE - VALUE",
        "value": "145/83 mmHg"
    }),
    ("blood_pressure_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "ARTERIAL PRESSURE - INTERPRETATION",
        "value": "STAGE II"
    }),
    ("heart_rate", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "CARDIAC FREQUENCY - VALUE",
        "value": "51 bpm"
    }),
    ("heart_rate_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "CARDIAC FREQUENCY - INTERPRETATION",
        "value": "normal for an athlete man"
    }),
    ("ankle_brachial_index", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "ANKLE-BRACHIAL INDEX - VALUE",
        "value": "non applicable"
    }),
    ("ankle_brachial_index_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "ANKLE-BRACHIAL INDEX - INTERPRETATION",
        "value": "Not applicable for this patient"
    }),
    ("abdominal_circumference", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "ABDOMINAL CIRCUMFERENCE - VALUE",
        "value": "102.8 cms"
    }),
    ("abdominal_circumference_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "ABDOMINAL CIRCUMFERENCE - INTERPRETATION",
        "value": "out of range, normal less than 101"
    }),
    ("hip_waist_ratio", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "HIP WAIST RATIO - VALUE",
        "value": "0.91"
    }),
    ("hip_waist_ratio_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "HIP WAIST RATIO - INTERPRETATION",
        "value": "slightly out of range, normal 0.90"
    }),
    ("pulse_oximetry", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "PULSE OXIMETRY - VALUE",
        "value": "96%"
    }),
    ("pulse_oximetry_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "PULSE OXIMETRY - INTERPRETATION",
        "value": "normal"
    }),
    ("respiratory_rate", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "RESPIRATORY FREQUENCY - VALUE",
        "value": "15 bpm"
    }),
    ("respiratory_rate_interpretation", {
        "page": 3,
        "section": "2.3. VITAL SIGNS AND BODY COMPOSITION",
        "question": "RESPIRATORY FREQUENCY - INTERPRETATION",
        "value": "normal"
    }),

    # ============== PAGE 4 - INBODY ==============
    ("inbody_score", {
        "page": 4,
        "section": "2.3. VITAL SIGNS - InBody Analysis",
        "question": "INBODY - SCORE",
        "value": "94/100"
    }),
    ("inbody_interpretation", {
        "page": 4,
        "section": "2.3. VITAL SIGNS - InBody Analysis",
        "question": "INBODY - INTERPRETATION",
        "value": "a 65-year-old man, 188 cm tall and weighing 109.9 kg, with an exceptionally strong and well-preserved body composition for his age. His skeletal muscle mass is 49.7 kg, which is well above average and places him in a category of excellent muscularity."
    }),
    ("additional_parameters", {
        "page": 4,
        "section": "2.3. VITAL SIGNS - InBody Analysis",
        "question": "Additional parameters",
        "value": "InBody analysis parameters included (see page 4)"
    }),

    # ============== PAGE 5 - PHYSICAL EXAM ==============
    ("exam_cardiopulmonary", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Cardiopulmonary",
        "value": "Regular rhythm, no audible murmurs. Lungs: Even breath sounds bilaterally, well ventilated."
    }),
    ("exam_neurological", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Neurological",
        "value": "Alert and oriented; no neurological deficits."
    }),
    ("exam_head", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Head",
        "value": "Normocephalic."
    }),
    ("exam_eyes", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Eyes",
        "value": "Pupils equal, round, and reactive to light; extraocular movements intact."
    }),
    ("exam_neck", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Neck",
        "value": "Symmetrical, no palpable masses."
    }),
    ("exam_abdomen", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Abdomen",
        "value": "Soft and depressible; non-tender to palpation; no masses."
    }),
    ("exam_extremities", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Extremities",
        "value": "Symmetrical; no signs of acute deep venous thrombosis; presence of venous insufficiency changes with ochre dermatitis in the left lower limb; distal pulses normal and symmetric; no pedal edema."
    }),
    ("exam_skin", {
        "page": 5,
        "section": "2.4. PHYSICAL EXAM",
        "question": "Skin",
        "value": "Normal coloration, adequate turgor. On the right temporal region, there is a non-ulcerated actinic keratosis measuring approximately 1 × 1 cm."
    }),

    # ============== PAGE 6-7 - LAB RESULTS ==============
    ("lab_cardiovascular_lipids", {
        "page": 6,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Cardiovascular System - Lipids",
        "value": "Total cholesterol 203 mg/dL (Mildly high), HDL 36 mg/dL (Low), LDL 140 mg/dL (Elevated), VLDL 27 mg/dL (Normal), Triglycerides 133 mg/dL (Normal), ApoB 112 mg/dL (Moderate), Lp(a) 1.9 mg/dL (Excellent)"
    }),
    ("lab_hematologic_system", {
        "page": 6,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Hematologic System",
        "value": "Hemoglobin 17.0 g/dL (High-normal), Hematocrit 46.7% (Normal), RBC 5.75 ×10⁶/µL (Slightly elevated), WBC 6.98 ×10³/µL (Normal)"
    }),
    ("lab_inflammatory_markers", {
        "page": 6,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Immune System and Inflammation",
        "value": "hs-CRP 1.5 mg/L (Mild metabolic inflammation → consistent with NAFLD)"
    }),
    ("lab_endocrine_hormonal", {
        "page": 6,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Hormonal and Endocrine System",
        "value": "TSH 2.40 uIU/mL (Normal), Testosterone 490.9 ng/dL (Excellent for age), Vitamin D 81.8 ng/mL (Elevated), Fasting insulin 14.4 µIU/mL (High-normal)"
    }),
    ("lab_liver_function", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Liver and Detoxification",
        "value": "AST 56 U/L (Elevated), ALT 54 U/L (Elevated), ALP 74 U/L (Normal), GGT 39 U/L (Normal)"
    }),
    ("lab_renal_function", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Renal Function",
        "value": "BUN 19 mg/dL (Normal), Creatinine 1.04 mg/dL (Normal), eGFR Normal"
    }),
    ("lab_electrolytes_minerals", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Electrolytes and Minerals",
        "value": "Sodium 139 mmol/L (Normal), Potassium 4.2 mmol/L (Normal), Magnesium 1.9 mg/dL (Normal-low)"
    }),
    ("lab_metabolic_panel", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Metabolic Panel",
        "value": "Fasting glucose 92 mg/dL (Normal), HbA1c 5.1% (Excellent)"
    }),
    ("lab_urinalysis", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Urinalysis",
        "value": "Clear, yellow urine (Normal), pH 5.0, No protein/glucose/blood"
    }),
    ("lab_stool_examination", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Stool Examination",
        "value": "No RBCs, No WBCs, No parasites, Normal"
    }),
    ("lab_tumor_markers", {
        "page": 7,
        "section": "2.5. LABORATORY RESULTS",
        "question": "Tumor Markers",
        "value": "PSA 0.80 ng/mL (Excellent; very low prostate cancer risk)"
    }),

    # ============== PAGE 8-9 - IMAGING ==============
    ("imaging_ecg", {
        "page": 8,
        "section": "2.6. DIAGNOSTIC IMAGING AND ELECTROCARDIOGRAM",
        "question": "EKG",
        "value": "(Normal Study) Normal sinus rhythm, Rate ~60–70 bpm, Normal intervals, No ischemia or infarction signs"
    }),
    ("imaging_abdominal_ultrasound", {
        "page": 9,
        "section": "2.6. DIAGNOSTIC IMAGING AND ELECTROCARDIOGRAM",
        "question": "Abdominal Ultrasound",
        "value": "Moderate hepatic steatosis (grade II), Moderate pancreatic lipomatosis, Benign simple renal cyst (right kidney), Otherwise normal"
    }),

    # ============== PAGE 10-11 - SECTION 3: HEALTH GOALS ==============
    ("goal1_title", {
        "page": 10,
        "section": "Section 3: Health Goals - Goal #1",
        "question": "Goal #1 Title",
        "value": "Reverse Fatty Liver (NAFLD Grade II)"
    }),
    ("goal1_key_result", {
        "page": 10,
        "section": "Section 3: Health Goals - Goal #1",
        "question": "Goal #1 Key Result",
        "value": "Improve liver health by reducing inflammation and normalizing liver enzymes."
    }),
    ("goal1_action_1", {
        "page": 10,
        "section": "Section 3: Health Goals - Goal #1",
        "question": "Goal #1 Action 1",
        "value": "Implement a liver-focused, anti-inflammatory diet: Reduce fructose, increase vegetables to 6-7 servings/day."
    }),
    ("goal1_action_2", {
        "page": 10,
        "section": "Section 3: Health Goals - Goal #1",
        "question": "Goal #1 Action 2",
        "value": "Add afternoon metabolic movement: 10-15 minutes of light walking after lunch and dinner."
    }),
    ("goal1_action_3", {
        "page": 10,
        "section": "Section 3: Health Goals - Goal #1",
        "question": "Goal #1 Action 3",
        "value": "Support liver detoxification pathways with adequate hydration and phytonutrients."
    }),
    ("goal2_title", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #2",
        "question": "Goal #2 Title",
        "value": "Improve Insulin Sensitivity and Metabolic Flexibility"
    }),
    ("goal2_key_result", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #2",
        "question": "Goal #2 Key Result",
        "value": "Reduce hepatic insulin resistance and improve metabolic efficiency."
    }),
    ("goal2_action_1", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #2",
        "question": "Goal #2 Action 1",
        "value": "Adjust fasting and feeding schedule: Add small protein-based afternoon snack."
    }),
    ("goal2_action_2", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #2",
        "question": "Goal #2 Action 2",
        "value": "Increase daily fiber intake: 1-2 teaspoons of psyllium or ground flaxseed."
    }),
    ("goal2_action_3", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #2",
        "question": "Goal #2 Action 3",
        "value": "Add low-intensity cardio sessions: 12-20 minutes of Zone 2-3 cardio 3 times per week."
    }),
    ("goal3_title", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #3",
        "question": "Goal #3 Title",
        "value": "Optimize Cardiovascular Risk and Improve Lipid Profile"
    }),
    ("goal3_key_result", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #3",
        "question": "Goal #3 Key Result",
        "value": "Improve lipid balance and reduce long-term cardiovascular risk."
    }),
    ("goal3_action_1", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #3",
        "question": "Goal #3 Action 1",
        "value": "Improve fat quality and increase natural omega-3 intake: Eat fatty fish 2-3 times per week."
    }),
    ("goal3_action_2", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #3",
        "question": "Goal #3 Action 2",
        "value": "Reduce Vitamin D supplementation: Lower dose to 2,000-3,000 IU/day."
    }),
    ("goal3_action_3", {
        "page": 11,
        "section": "Section 3: Health Goals - Goal #3",
        "question": "Goal #3 Action 3",
        "value": "Mandatory post-meal walking: 10-12 minutes of walking after the largest meal."
    }),

    # ============== PAGE 12-13 - SECTION 4: ACTION PLAN ==============
    ("metric1_name", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #1 - Name",
        "value": "Improve Liver Health (Reverse NAFLD Grade II)"
    }),
    ("metric1_parameters", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #1 - Parameters",
        "value": "ALT, AST, Ferritin, hs-CRP"
    }),
    ("metric1_current_values", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #1 - Current Values",
        "value": "ALT: 54 U/L, AST: 56 U/L, Ferritin: 315 ng/mL, hs-CRP: 1.5 mg/L"
    }),
    ("metric1_3month_goal", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #1 - 3-Month Goal",
        "value": "ALT <45, AST <45, Ferritin <250, hs-CRP <1.0"
    }),
    ("metric1_6month_goal", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #1 - 6-Month Goal",
        "value": "ALT <40, AST <40, Ferritin <200, hs-CRP <0.8"
    }),
    ("metric2_parameters", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #2 - Parameters",
        "value": "Fasting insulin, Fasting glucose, Waist circumference"
    }),
    ("metric2_current_values", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #2 - Current Values",
        "value": "Fasting insulin: 14.4 µIU/mL, Fasting glucose: 92 mg/dL, Waist: 102.8 cm"
    }),
    ("metric2_3month_goal", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #2 - 3-Month Goal",
        "value": "Insulin <12, Glucose 88-92, Waist -2 cm"
    }),
    ("metric2_6month_goal", {
        "page": 12,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #2 - 6-Month Goal",
        "value": "Insulin <10, Glucose 85-90, Waist -4-5 cm"
    }),
    ("metric3_parameters", {
        "page": 13,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #3 - Parameters",
        "value": "LDL, HDL, ApoB, Vitamin D"
    }),
    ("metric3_current_values", {
        "page": 13,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #3 - Current Values",
        "value": "LDL: 140 mg/dL, HDL: 36 mg/dL, ApoB: 112 mg/dL, Vitamin D: 81.8 ng/mL"
    }),
    ("metric3_3month_goal", {
        "page": 13,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #3 - 3-Month Goal",
        "value": "LDL <125, HDL >38, ApoB <105, Vitamin D 60-70"
    }),
    ("metric3_6month_goal", {
        "page": 13,
        "section": "Section 4: Action Plan",
        "question": "Action Plan #3 - 6-Month Goal",
        "value": "LDL 100-120, HDL >40, ApoB <100, Vitamin D 50-65"
    }),

    # ============== PAGE 13 - SECTION 5: LABS & REFERENCES ==============
    ("recommended_labs", {
        "page": 13,
        "section": "Section 5: Complimentary Labs and Clinical References",
        "question": "Recommended Labs",
        "value": "not necessary at this time"
    }),
    ("specialist_referrals", {
        "page": 13,
        "section": "Section 5: Complimentary Labs and Clinical References",
        "question": "Specialist Referrals",
        "value": "Dermatologist, Peripheral vascular surgeon"
    }),

    # ============== PAGE 14 - SECTION 6: FOLLOW-UP ==============
    ("followup_schedule", {
        "page": 14,
        "section": "Section 6: Follow-up and Frequency",
        "question": "Follow-up Schedule",
        "value": "abdominal ultrasound in 6 months, labs in 3 months"
    }),
    ("report_author", {
        "page": 14,
        "section": "Section 6: Follow-up and Frequency",
        "question": "Report Author",
        "value": "Dr. SILVIA ELENA GARITA PEÑA"
    }),
])


def generate_text_document():
    """Generate a formatted text document from the ordered data."""
    lines = []
    lines.append("=" * 80)
    lines.append("HEALTH AND WELLNESS GUIDE - EXTRACTED DATA")
    lines.append("Patient: RICHARD ALLEN PEACOCK")
    lines.append("Extraction Date: 2025-12-04")
    lines.append("=" * 80)
    lines.append("")
    
    current_section = ""
    current_page = 0
    
    for field_name, field_data in ORDERED_EXTRACTED_DATA.items():
        page = field_data.get("page", 0)
        section = field_data.get("section", "")
        question = field_data.get("question", field_name)
        value = field_data.get("value", "")
        
        # Page header
        if page != current_page:
            current_page = page
            lines.append("")
            lines.append(f"{'─' * 40} PAGE {page} {'─' * 40}")
        
        # Section header
        if section != current_section:
            current_section = section
            lines.append("")
            lines.append(f"▶ {section}")
            lines.append("-" * 60)
        
        # Field with question and value
        lines.append(f"  Q: {question}")
        lines.append(f"  A: {value}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("END OF DOCUMENT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def generate_json_output():
    """Generate the JSON output in ordered format."""
    return json.dumps(ORDERED_EXTRACTED_DATA, indent=2, ensure_ascii=False)


def main():
    """Main function to test the ordered extraction output."""
    print("=" * 60)
    print("TEST: Ordered JSON Structure with Questions")
    print("=" * 60)
    
    # Show field count
    print(f"\nTotal fields: {len(ORDERED_EXTRACTED_DATA)}")
    
    # Show first 10 fields as sample
    print("\n--- FIRST 10 FIELDS (in PDF order) ---")
    for i, (field_name, field_data) in enumerate(ORDERED_EXTRACTED_DATA.items()):
        if i >= 10:
            break
        print(f"\n{i+1}. {field_name}")
        print(f"   Page: {field_data.get('page')}")
        print(f"   Section: {field_data.get('section')}")
        print(f"   Question: {field_data.get('question')}")
        value = field_data.get('value', '')
        if len(value) > 80:
            value = value[:80] + "..."
        print(f"   Value: {value}")
    
    # Save JSON file
    json_output = generate_json_output()
    with open("test_ordered_output.json", "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"\n✓ JSON saved to: test_ordered_output.json")
    
    # Save text document
    text_output = generate_text_document()
    with open("test_ordered_output.txt", "w", encoding="utf-8") as f:
        f.write(text_output)
    print(f"✓ Text document saved to: test_ordered_output.txt")
    
    print("\n" + "=" * 60)
    print("Test complete! Check the output files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
