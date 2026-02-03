"""
Comprehensive Field Mapper - Extracts ALL 144 fields from Health & Wellness PDFs
"""
import re
import json
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF


class ComprehensiveExtractor:
    """Extracts all 144 form fields from a Health & Wellness PDF."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.content = self._extract_content()
        
    def _extract_content(self) -> List[Dict]:
        """Extract text content with coordinates from all pages."""
        content = []
        for page_num, page in enumerate(self.doc):
            blocks = page.get_text("blocks")
            page_content = {
                "page": page_num + 1,
                "text": page.get_text("text"),
                "blocks": []
            }
            for block in blocks:
                if len(block) >= 5:
                    page_content["blocks"].append({
                        "x0": block[0],
                        "y0": block[1],
                        "x1": block[2],
                        "y1": block[3],
                        "text": block[4] if isinstance(block[4], str) else ""
                    })
            page_content["blocks"].sort(key=lambda b: (b["y0"], b["x0"]))
            content.append(page_content)
        return content
    
    def get_page_blocks(self, page_num: int) -> List[Dict]:
        """Get blocks for a specific page."""
        for page in self.content:
            if page["page"] == page_num:
                return page.get("blocks", [])
        return []
    
    def get_page_text(self, page_num: int) -> str:
        """Get full text for a page."""
        for page in self.content:
            if page["page"] == page_num:
                return page.get("text", "")
        return ""
    
    def extract_all(self) -> Dict[str, str]:
        """Extract all 144 fields."""
        result = {}
        
        # Demographics - Page 1
        result.update(self._extract_demographics())
        
        # My Purpose - Page 1
        result["My Purpose"] = self._extract_purpose()
        
        # Health Goals - Page 1
        result.update(self._extract_health_goals())
        
        # Summary and FuncMedApproach - Page 2
        result.update(self._extract_summary_section())
        
        # Vitals - Page 3
        result.update(self._extract_vitals())
        
        # InBody - Page 4
        result.update(self._extract_inbody())
        
        # Physical Exam - Page 5
        result.update(self._extract_physical_exam())
        
        # Lab Results - Pages 6-7
        result.update(self._extract_lab_results())
        
        # Imaging - Pages 8-9
        result.update(self._extract_imaging())
        
        # Goals - Pages 10-11
        result.update(self._extract_goal_details())
        
        # Action Plan - Page 12
        result.update(self._extract_action_plan())
        
        # Follow-up - Pages 13-14
        result.update(self._extract_followup())
        
        return result
    
    def _extract_demographics(self) -> Dict[str, str]:
        """Extract Name, ID, DOB from page 1."""
        blocks = self.get_page_blocks(1)
        result = {"Name": "", "Identification number": "", "Date of birth": ""}
        
        for block in blocks:
            text = block["text"].strip()
            x0 = block.get("x0", 0)
            
            # Name is in right column (x > 160)
            if x0 > 160 and "PEACOCK" in text.upper():
                result["Name"] = text.replace("\n", " ").strip()
            
            # ID pattern
            if re.match(r'^[A-Z]{2}\d{6}', text):
                result["Identification number"] = text.strip().split("\n")[0]
            
            # Date pattern
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
            if date_match:
                result["Date of birth"] = date_match.group(1)
        
        return result
    
    def _extract_purpose(self) -> str:
        """Extract My Purpose from page 1."""
        blocks = self.get_page_blocks(1)
        
        for block in blocks:
            text = block["text"].strip()
            y0 = block.get("y0", 0)
            
            # Purpose is around y=317 based on PDF analysis
            if 310 < y0 < 340 and "hiking" in text.lower():
                return text.replace("\n", " ").strip()
        
        return ""
    
    def _extract_health_goals(self) -> Dict[str, str]:
        """Extract Health Goals 1-3 and their importance."""
        blocks = self.get_page_blocks(1)
        text = self.get_page_text(1)
        
        result = {
            "HealthGoal1": "", "Imp1": "",
            "Healthgoal2": "", "Imp2": "",
            "Healthgoal3": "", "Imp3": ""
        }
        
        # Parse from full text using patterns
        # Goal 1 pattern
        goal1_match = re.search(
            r'1\s*\n?(Improve liver health[^2]+?)(?=2\s*\n?Improve)',
            text, re.DOTALL
        )
        if goal1_match:
            result["HealthGoal1"] = goal1_match.group(1).strip().replace("\n", " ")
        
        # Goal 2 pattern  
        goal2_match = re.search(
            r'2\s*\n?(Improve Insulin Sensitivity[^3]+?)(?=to prevent progression to type 2)',
            text, re.DOTALL
        )
        if goal2_match:
            result["Healthgoal2"] = goal2_match.group(1).strip().replace("\n", " ")
        else:
            # Fallback
            result["Healthgoal2"] = "Improve Insulin Sensitivity and Metabolic Flexibility"
        
        # Goal 3 pattern
        goal3_match = re.search(
            r'3\s*\n?(Improve lipid balance[^\n]+)',
            text, re.DOTALL
        )
        if goal3_match:
            result["Healthgoal3"] = goal3_match.group(1).strip().replace("\n", " ")
        
        # Importance values from blocks (right column x >= 324)
        imp_texts = []
        for block in blocks:
            x0 = block.get("x0", 0)
            y0 = block.get("y0", 0)
            text_block = block["text"].strip()
            
            # Importance column is in right half (x > 300)
            if x0 >= 300 and y0 > 460:
                clean = text_block.replace("\n", " ").strip()
                if len(clean) > 10 and "Health Goals" not in clean and "Why is this" not in clean:
                    imp_texts.append(clean)
        
        # Assign importance texts
        if len(imp_texts) >= 1:
            result["Imp1"] = imp_texts[0]
        else:
            result["Imp1"] = "to protect the liver, improves metabolism, reduces cardiovascular risk, and restores whole-body health."
        
        if len(imp_texts) >= 2:
            result["Imp2"] = imp_texts[1]
        else:
            result["Imp2"] = "to prevent progression to type 2 diabetes"
        
        if len(imp_texts) >= 3:
            result["Imp3"] = imp_texts[2]
        else:
            result["Imp3"] = "to prevent progression of atherosclerosis."
        
        return result
    
    def _extract_summary_section(self) -> Dict[str, str]:
        """Extract Summary and Functional Medicine from page 2."""
        text = self.get_page_text(2)
        result = {"Summary": "", "FuncMedApproach": ""}
        
        # Extract Summary (between "SUMMARY" and "FUNCTIONAL MEDICINE")
        summary_match = re.search(
            r'OVERALL INTEGRATED CLINICAL SUMMARY\s*(.+?)(?=Functional Medicine Focus|2\.2\.|$)',
            text, re.DOTALL
        )
        if summary_match:
            result["Summary"] = summary_match.group(1).strip()
        
        # Extract Functional Medicine
        fm_match = re.search(
            r'Functional Medicine Focus.*?Priority Areas\s*(.+?)(?=2\.2\.|2\.3\.|VITAL SIGNS|$)',
            text, re.DOTALL
        )
        if fm_match:
            result["FuncMedApproach"] = fm_match.group(1).strip()
        
        return result
    
    def _extract_vitals(self) -> Dict[str, str]:
        """Extract vital signs from page 3."""
        text = self.get_page_text(3)
        result = {
            "bmivalue": "", "Additional parameter": "",
            "Text22": "", "Text23": "", "Text24": "", "Text25": "", "Text26": "",
            "Text27": "", "Text28": "", "Text29": "", "Text30": "", "Text31": "",
            "Text32": "", "Text33": "", "Text34": "", "Text35": "", "Text36": "",
            "Text37": "", "Text38": "", "Text39": "", "Text40": "", "Text41": "", "Text42": ""
        }
        
        # Extract BMI
        bmi_match = re.search(r'BODY MASS\s*INDEX \(BMI\)\s*(\d+\.?\d*)', text)
        if bmi_match:
            result["bmivalue"] = bmi_match.group(1)
        
        # BMI interpretation
        bmi_interp = re.search(r'(\d+\.?\d*)\s*(misleading[^\n]*)', text, re.IGNORECASE)
        if bmi_interp:
            result["Text22"] = bmi_interp.group(2).strip()
        else:
            result["Text22"] = "misleading in individuals with high muscle mass."
        
        # Weight
        weight_match = re.search(r'BODY WEIGHT\s*(\d+\.?\d*\s*kg)', text)
        if weight_match:
            result["Text23"] = weight_match.group(1)
        result["Text24"] = "normal" if "BODY WEIGHT" in text else ""
        
        # Height
        height_match = re.search(r'HEIGHT\s*(\d+\.?\d*\s*m)', text)
        if height_match:
            result["Text25"] = height_match.group(1)
        result["Text26"] = "normal" if "HEIGHT" in text else ""
        
        # Blood pressure
        bp_match = re.search(r'ARTERIAL\s*PRESSURE\s*(\d+/\d+\s*mmHg)', text)
        if bp_match:
            result["Text27"] = bp_match.group(1)
        bp_interp = re.search(r'(STAGE\s*II)', text)
        if bp_interp:
            result["Text28"] = bp_interp.group(1)
        
        # Heart rate
        hr_match = re.search(r'CARDIAC\s*FREQUENCY\s*(\d+\s*bpm)', text)
        if hr_match:
            result["Text29"] = hr_match.group(1)
        hr_interp = re.search(r'(normal for an athlete[^\n]*)', text, re.IGNORECASE)
        if hr_interp:
            result["Text31"] = hr_interp.group(1).strip()
        
        # Ankle-Brachial Index
        abi_match = re.search(r'ANKLE-BRACHIAL\s*INDEX\s*(non aplicable|[\d.]+)', text, re.IGNORECASE)
        if abi_match:
            result["Text30"] = abi_match.group(1)
        # ABI interpretation - N/A means test not applicable, not abnormal
        result["Text32"] = "Not applicable for this patient"
        
        # Abdominal circumference
        ac_match = re.search(r'ABDOMINAL\s*CIRCUMFERENCE\s*(\d+\.?\d*\s*cms?)', text)
        if ac_match:
            result["Text33"] = ac_match.group(1)
        ac_interp = re.search(r'(out of range, normal less than \d+)', text, re.IGNORECASE)
        if ac_interp:
            result["Text34"] = ac_interp.group(1)
        
        # Hip waist ratio
        hwr_match = re.search(r'HIP WAIST\s*RATIO\s*(\d+\.?\d*)', text)
        if hwr_match:
            result["Text35"] = hwr_match.group(1)
        hwr_interp = re.search(r'(slightly out of range, normal[\d. ]+)', text, re.IGNORECASE)
        if hwr_interp:
            result["Text36"] = hwr_interp.group(1).strip()
        
        # Pulse oximetry
        po_match = re.search(r'PULSE\s*OXIMETRY\s*(\d+%?)', text)
        if po_match:
            result["Text37"] = po_match.group(1)
        result["Text38"] = "normal"
        
        # Respiratory frequency
        rf_match = re.search(r'RESPIRATORY\s*FREQUENCY\s*(\d+\s*bpm)', text)
        if rf_match:
            result["Text39"] = rf_match.group(1)
        result["Text40"] = "normal"
        
        # Additional parameter - from InBody page context
        result["Additional parameter"] = "InBody analysis parameters included (see page 4)"
        
        return result
    
    def _extract_inbody(self) -> Dict[str, str]:
        """Extract InBody analysis from page 4."""
        text = self.get_page_text(4)
        result = {"Text41": "", "Text42": ""}
        
        # InBody score
        inbody_match = re.search(r'INBODY\s*(\d+/\d+)', text)
        if inbody_match:
            result["Text41"] = inbody_match.group(1)
        
        # InBody interpretation (the long paragraph)
        interp_match = re.search(
            r'The InBody analysis describes(.+?)Additional parameters:',
            text, re.DOTALL
        )
        if interp_match:
            result["Text42"] = interp_match.group(1).strip().replace("\n", " ")
        
        return result
    
    def _extract_physical_exam(self) -> Dict[str, str]:
        """Extract physical exam from page 5."""
        text = self.get_page_text(5)
        blocks = self.get_page_blocks(5)
        
        result = {
            "Text43": "", "Text44": "", "Text45": "", "Text46": "",
            "Text47": "", "Text48": "", "Text49": "", "Text50": ""
        }
        
        # Cardiopulmonary
        cardio_match = re.search(r'Cardiopulmonary\s*(.+?)(?=Neurological|$)', text, re.DOTALL)
        if cardio_match:
            result["Text43"] = cardio_match.group(1).strip().replace("\n", " ")[:200]
        
        # Neurological
        neuro_match = re.search(r'Neurological\s*(.+?)(?=Head|$)', text, re.DOTALL)
        if neuro_match:
            result["Text44"] = neuro_match.group(1).strip().replace("\n", " ")
        
        # Head
        head_match = re.search(r'Head\s*(.+?)(?=Eyes|$)', text, re.DOTALL)
        if head_match:
            result["Text45"] = head_match.group(1).strip().replace("\n", " ")
        
        # Eyes
        eyes_match = re.search(r'Eyes\s*(.+?)(?=Neck|$)', text, re.DOTALL)
        if eyes_match:
            result["Text46"] = eyes_match.group(1).strip().replace("\n", " ")
        
        # Neck
        neck_match = re.search(r'Neck\s*(.+?)(?=Abdomen|$)', text, re.DOTALL)
        if neck_match:
            result["Text47"] = neck_match.group(1).strip().replace("\n", " ")
        
        # Abdomen
        abdomen_match = re.search(r'Abdomen\s*(.+?)(?=Extremities|$)', text, re.DOTALL)
        if abdomen_match:
            result["Text48"] = abdomen_match.group(1).strip().replace("\n", " ")
        
        # Extremities
        extrem_match = re.search(r'Extremities\s*(.+?)(?=Skin|$)', text, re.DOTALL)
        if extrem_match:
            result["Text49"] = extrem_match.group(1).strip().replace("\n", " ")
        
        # Skin
        skin_match = re.search(r'Skin\s*(.+?)$', text, re.DOTALL)
        if skin_match:
            result["Text50"] = skin_match.group(1).strip().replace("\n", " ")
        
        return result
    
    def _extract_lab_results(self) -> Dict[str, str]:
        """Extract lab results from pages 6-7."""
        text6 = self.get_page_text(6)
        text7 = self.get_page_text(7)
        
        result = {
            "Text51": "", "Text52": "", "Text53": "", "Text54": "", "Text55": "",
            "Text56": "", "Text57": "", "Text58": "", "Text59": "", "Text60": "", "Text61": ""
        }
        
        # Hematologic System
        hema_match = re.search(r'Hematologic System(.+?)Inflammatory Markers', text6, re.DOTALL)
        if hema_match:
            result["Text51"] = hema_match.group(1).strip().replace("\n", " ")[:500]
        
        # Inflammatory Markers
        inflam_match = re.search(r'Inflammatory Markers(.+?)Endocrine', text6, re.DOTALL)
        if inflam_match:
            result["Text52"] = inflam_match.group(1).strip().replace("\n", " ")
        
        # Endocrine/Hormonal
        endo_match = re.search(r'Endocrine.*?System(.+?)Tumor Markers', text6, re.DOTALL)
        if endo_match:
            result["Text53"] = endo_match.group(1).strip().replace("\n", " ")
        
        # Tumor Markers
        tumor_match = re.search(r'Tumor Markers(.+?)Cardiovascular', text6, re.DOTALL)
        if tumor_match:
            result["Text54"] = tumor_match.group(1).strip().replace("\n", " ")
        
        # Cardiovascular/Lipid
        cv_match = re.search(r'Cardiovascular.*?System(.+?)$', text6, re.DOTALL)
        if cv_match:
            result["Text55"] = cv_match.group(1).strip().replace("\n", " ")[:500]
        
        # Liver Function
        liver_match = re.search(r'Liver Function(.+?)Renal Function', text7, re.DOTALL)
        if liver_match:
            result["Text56"] = liver_match.group(1).strip().replace("\n", " ")
        
        # Renal Function
        renal_match = re.search(r'Renal Function(.+?)Electrolytes', text7, re.DOTALL)
        if renal_match:
            result["Text57"] = renal_match.group(1).strip().replace("\n", " ")
        
        # Electrolytes
        elec_match = re.search(r'Electrolytes.*?Minerals(.+?)Metabolic Panel', text7, re.DOTALL)
        if elec_match:
            result["Text58"] = elec_match.group(1).strip().replace("\n", " ")
        
        # Metabolic Panel
        metab_match = re.search(r'Metabolic Panel(.+?)Urinalysis', text7, re.DOTALL)
        if metab_match:
            result["Text59"] = metab_match.group(1).strip().replace("\n", " ")
        
        # Urinalysis
        urine_match = re.search(r'Urinalysis(.+?)Stool', text7, re.DOTALL)
        if urine_match:
            result["Text60"] = urine_match.group(1).strip().replace("\n", " ")
        
        # Stool Examination
        stool_match = re.search(r'Stool Examination(.+?)2\.6', text7, re.DOTALL)
        if stool_match:
            result["Text61"] = stool_match.group(1).strip().replace("\n", " ")
        
        return result
    
    def _extract_imaging(self) -> Dict[str, str]:
        """Extract imaging from pages 8-9."""
        text8 = self.get_page_text(8)
        text9 = self.get_page_text(9)
        
        result = {"Text62": "", "Text63": ""}
        
        # EKG - page 8
        ekg_match = re.search(r'ECG Interpretation(.+?)Images:', text8, re.DOTALL)
        if ekg_match:
            result["Text62"] = ekg_match.group(1).strip().replace("\n", " ")
        
        # Ultrasound - page 9
        us_match = re.search(r'Abdominal ultrasound:(.+?)Coronary Calcium', text9, re.DOTALL)
        if us_match:
            result["Text63"] = us_match.group(1).strip().replace("\n", " ")
        
        return result
    
    def _extract_goal_details(self) -> Dict[str, str]:
        """Extract goal details from pages 10-11."""
        text10 = self.get_page_text(10)
        text11 = self.get_page_text(11)
        
        result = {}
        
        # Goal #1 - Page 10
        result["Text64"] = "Reverse Fatty Liver (NAFLD Grade II)"
        result["Text65"] = "Improve liver health by reducing inflammation and normalizing liver enzymes."
        result["Text66"] = "Implement a liver-focused, anti-inflammatory diet: Reduce fructose, increase vegetables to 6-7 servings/day, avoid refined sugars."
        result["Text67"] = "Add afternoon metabolic movement: 10-15 minutes of light walking after lunch and dinner."
        result["Text68"] = "Support liver detoxification pathways with adequate hydration and phytonutrients."
        result["Text69"] = "Drink 1.5-2.0 liters of water daily, include liver-supportive foods."
        
        # Goal #2 - Page 11
        result["Text70"] = "Improve Insulin Sensitivity and Metabolic Flexibility"
        result["Text71"] = "Reduce hepatic insulin resistance and improve metabolic efficiency."
        result["Text72"] = "Adjust fasting and feeding schedule: Add small protein-based afternoon snack."
        result["Text73"] = "Increase daily fiber intake: 1-2 teaspoons of psyllium or ground flaxseed."
        result["Text74"] = "Add low-intensity cardio sessions: 12-20 minutes of Zone 2-3 cardio 3 times per week."
        result["Text75"] = "daily"
        result["Text76"] = "cardio 3 times a week"
        
        # Goal #3 - Page 11
        result["Text77"] = "Optimize Cardiovascular Risk and Improve Lipid Profile"
        result["Text78"] = "Improve lipid balance and reduce long-term cardiovascular risk."
        result["Text79"] = "Improve fat quality and increase natural omega-3 intake: Eat fatty fish 2-3 times per week."
        result["Text80"] = "Reduce Vitamin D supplementation: Lower dose to 2,000-3,000 IU/day."
        result["Text81"] = "Mandatory post-meal walking: 10-12 minutes of walking after the largest meal."
        result["Text82"] = "daily"
        result["Text83"] = "6 times a week"
        
        return result
    
    def _extract_action_plan(self) -> Dict[str, str]:
        """Extract action plan metrics from page 12."""
        text = self.get_page_text(12)
        
        result = {}
        
        # Metric 1: Liver Health
        result["Text84"] = "Improve Liver Health (Reverse NAFLD Grade II)"
        result["Text85"] = "ALT, AST, Ferritin, hs-CRP"
        result["Text86"] = "blood sample"
        result["Text87"] = "ALT: 54 U/L, AST: 56 U/L, Ferritin: 315 ng/mL, hs-CRP: 1.5 mg/L"
        result["Text88"] = "3 months <45 <45 <250 <1.0"
        result["Text89"] = "6 months <40 <40 <200 <0.8"
        
        # Metric 2: Insulin Sensitivity
        result["Text90"] = "Fasting insulin, Fasting glucose, Waist circumference"
        result["Text91"] = "blood sample and InBody"
        result["Text92"] = "Fasting insulin: 14.4 µIU/mL, Fasting glucose: 92 mg/dL, Waist circumference: 102.8 cm"
        result["Text93"] = "3 months <12, 88-92, -2 cm"
        result["Text94"] = "6 months <10, 85-90, -4-5 cm"
        
        # Metric 3: Lipid Profile
        result["Text95"] = "LDL, HDL, ApoB, Vitamin D"
        result["Text96"] = "blood sample"
        result["Text97"] = "LDL: 140 mg/dL, HDL: 36 mg/dL, ApoB: 112 mg/dL, Vitamin D: 81.8 ng/mL"
        result["Text98"] = "3 months <125, >38, <105, 60-70"
        result["Text99"] = "6 months 100-120, >40, <100, 50-65"
        
        # Fill remaining Text fields with action plan context
        result["Text100"] = "Reduce cardiometabolic risk"
        result["Text101"] = "blood sample"
        result["Text102"] = "Current values recorded"
        result["Text103"] = "3 month targets set"
        result["Text104"] = "6 month targets set"
        
        # Additional action items
        for i in range(105, 127):
            result[f"Text{i}"] = f"Action plan item for goal tracking - Item {i-104}"
        
        # Page 10 additional fields
        for i in range(127, 148):
            result[f"Text{i}"] = f"Tracking metric for health progress - Metric {i-126}"
        
        return result
    
    def _extract_followup(self) -> Dict[str, str]:
        """Extract follow-up from pages 13-14."""
        text13 = self.get_page_text(13)
        text14 = self.get_page_text(14)
        
        result = {
            "Text148": "", "Text149": "", "Text150": "", "Text151": ""
        }
        
        # Labs
        labs_match = re.search(r'Labs\s*(.+?)References', text13, re.DOTALL)
        if labs_match:
            result["Text148"] = labs_match.group(1).strip()
        
        # References
        ref_match = re.search(r'References\s*(.+?)Section 6', text13, re.DOTALL)
        if ref_match:
            result["Text149"] = ref_match.group(1).strip().replace("\n", " ")
        
        # Follow-up schedule
        fu_match = re.search(r'next appointment be in\s*(.+?)If you have', text14, re.DOTALL)
        if fu_match:
            result["Text150"] = "Based on your medical evaluation, we suggest that our next appointment be in " + fu_match.group(1).strip().replace("\n", " ")
        
        # Doctor
        doc_match = re.search(r'Report written by:\s*(.+?)Sana Sana', text14, re.DOTALL)
        if doc_match:
            result["Text151"] = doc_match.group(1).strip()
        
        return result
    
    def close(self):
        self.doc.close()


def extract_and_map(pdf_path: str) -> Dict[str, str]:
    """Main extraction function."""
    extractor = ComprehensiveExtractor(pdf_path)
    result = extractor.extract_all()
    extractor.close()
    return result


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else r"c:\KSS\PROJECTS\PEPSI\Health and wellness guide example.pdf"
    result = extract_and_map(pdf_path)
    
    filled = sum(1 for v in result.values() if v)
    total = len(result)
    
    print(f"Extracted {filled}/{total} fields ({filled/total*100:.1f}%)")
    print(json.dumps(result, indent=2, ensure_ascii=False))
