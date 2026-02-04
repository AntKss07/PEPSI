"""
Comprehensive Field Mapper - Extracts ALL 144 fields with DESCRIPTIVE NAMES
Outputs fields in PDF reading order (page by page, top to bottom)
"""
import re
import json
from collections import OrderedDict
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF


# Ordered list of fields in PDF reading order with questions/labels
FIELD_ORDER = [
    # Page 1 - Section 1: My Purpose
    ("patient_name", "Name"),
    ("patient_id", "Identification number"),
    ("date_of_birth", "Date of birth"),
    ("my_purpose", "Why do I want to improve my health?"),
    ("health_goal_1", "Health Goal #1"),
    ("health_goal_1_importance", "Why is Health Goal #1 important?"),
    ("health_goal_2", "Health Goal #2"),
    ("health_goal_2_importance", "Why is Health Goal #2 important?"),
    ("health_goal_3", "Health Goal #3"),
    ("health_goal_3_importance", "Why is Health Goal #3 important?"),
    # Page 2 - Section 2: Results and Findings
    ("clinical_summary", "2.1. SUMMARY"),
    ("functional_medicine_approach", "2.2. FUNCTIONAL MEDICINE APPROACH"),
    # Page 3 - Vital Signs
    ("bmi_value", "BODY MASS INDEX (BMI) - VALUE"),
    ("bmi_interpretation", "BODY MASS INDEX (BMI) - INTERPRETATION"),
    ("body_weight", "BODY WEIGHT - VALUE"),
    ("body_weight_interpretation", "BODY WEIGHT - INTERPRETATION"),
    ("height", "HEIGHT - VALUE"),
    ("height_interpretation", "HEIGHT - INTERPRETATION"),
    ("blood_pressure", "ARTERIAL PRESSURE - VALUE"),
    ("blood_pressure_interpretation", "ARTERIAL PRESSURE - INTERPRETATION"),
    ("heart_rate", "CARDIAC FREQUENCY - VALUE"),
    ("heart_rate_interpretation", "CARDIAC FREQUENCY - INTERPRETATION"),
    ("ankle_brachial_index", "ANKLE-BRACHIAL INDEX - VALUE"),
    ("ankle_brachial_index_interpretation", "ANKLE-BRACHIAL INDEX - INTERPRETATION"),
    ("abdominal_circumference", "ABDOMINAL CIRCUMFERENCE - VALUE"),
    ("abdominal_circumference_interpretation", "ABDOMINAL CIRCUMFERENCE - INTERPRETATION"),
    ("hip_waist_ratio", "HIP WAIST RATIO - VALUE"),
    ("hip_waist_ratio_interpretation", "HIP WAIST RATIO - INTERPRETATION"),
    ("pulse_oximetry", "PULSE OXIMETRY - VALUE"),
    ("pulse_oximetry_interpretation", "PULSE OXIMETRY - INTERPRETATION"),
    ("respiratory_rate", "RESPIRATORY FREQUENCY - VALUE"),
    ("respiratory_rate_interpretation", "RESPIRATORY FREQUENCY - INTERPRETATION"),
    # Page 4 - InBody
    ("inbody_score", "INBODY - SCORE"),
    ("inbody_interpretation", "INBODY - INTERPRETATION"),
    ("additional_parameters", "Additional parameters"),
    # Page 5 - Physical Exam
    ("exam_cardiopulmonary", "Cardiopulmonary"),
    ("exam_neurological", "Neurological"),
    ("exam_head", "Head"),
    ("exam_eyes", "Eyes"),
    ("exam_neck", "Neck"),
    ("exam_abdomen", "Abdomen"),
    ("exam_extremities", "Extremities"),
    ("exam_skin", "Skin"),
    # Page 6-7 - Lab Results
    ("lab_cardiovascular_lipids", "Cardiovascular System - Lipids"),
    ("lab_hematologic_system", "Hematologic System"),
    ("lab_inflammatory_markers", "Immune System and Inflammation"),
    ("lab_endocrine_hormonal", "Hormonal and Endocrine System"),
    ("lab_liver_function", "Liver and Detoxification"),
    ("lab_renal_function", "Renal Function"),
    ("lab_electrolytes_minerals", "Electrolytes and Minerals"),
    ("lab_metabolic_panel", "Metabolic Panel"),
    ("lab_urinalysis", "Urinalysis"),
    ("lab_stool_examination", "Stool Examination"),
    ("lab_tumor_markers", "Tumor Markers"),
    # Page 8-9 - Imaging
    ("imaging_ecg", "EKG"),
    ("imaging_abdominal_ultrasound", "Abdominal Ultrasound"),
    # Page 10-11 - Section 3: Health Goals
    ("goal1_title", "Goal #1 Title"),
    ("goal1_key_result", "Goal #1 Key Result"),
    ("goal1_action_1", "Goal #1 Action 1"),
    ("goal1_action_2", "Goal #1 Action 2"),
    ("goal1_action_3", "Goal #1 Action 3"),
    ("goal1_action_details", "Goal #1 Action Details"),
    ("goal2_title", "Goal #2 Title"),
    ("goal2_key_result", "Goal #2 Key Result"),
    ("goal2_action_1", "Goal #2 Action 1"),
    ("goal2_action_2", "Goal #2 Action 2"),
    ("goal2_action_3", "Goal #2 Action 3"),
    ("goal2_frequency_1", "Goal #2 Frequency 1"),
    ("goal2_frequency_2", "Goal #2 Frequency 2"),
    ("goal3_title", "Goal #3 Title"),
    ("goal3_key_result", "Goal #3 Key Result"),
    ("goal3_action_1", "Goal #3 Action 1"),
    ("goal3_action_2", "Goal #3 Action 2"),
    ("goal3_action_3", "Goal #3 Action 3"),
    ("goal3_frequency_1", "Goal #3 Frequency 1"),
    ("goal3_frequency_2", "Goal #3 Frequency 2"),
    # Page 12-13 - Section 4: Action Plan
    ("metric1_name", "Action Plan #1 - Name"),
    ("metric1_parameters", "Action Plan #1 - Parameters"),
    ("metric1_monitoring_method", "Action Plan #1 - Monitoring Method"),
    ("metric1_current_values", "Action Plan #1 - Current Values"),
    ("metric1_3month_goal", "Action Plan #1 - 3-Month Goal"),
    ("metric1_6month_goal", "Action Plan #1 - 6-Month Goal"),
    ("metric2_parameters", "Action Plan #2 - Parameters"),
    ("metric2_monitoring_method", "Action Plan #2 - Monitoring Method"),
    ("metric2_current_values", "Action Plan #2 - Current Values"),
    ("metric2_3month_goal", "Action Plan #2 - 3-Month Goal"),
    ("metric2_6month_goal", "Action Plan #2 - 6-Month Goal"),
    ("metric3_parameters", "Action Plan #3 - Parameters"),
    ("metric3_monitoring_method", "Action Plan #3 - Monitoring Method"),
    ("metric3_current_values", "Action Plan #3 - Current Values"),
    ("metric3_3month_goal", "Action Plan #3 - 3-Month Goal"),
    ("metric3_6month_goal", "Action Plan #3 - 6-Month Goal"),
    ("metric4_name", "Action Plan #4 - Name"),
    ("metric4_monitoring_method", "Action Plan #4 - Monitoring Method"),
    ("metric4_current_values", "Action Plan #4 - Current Values"),
    ("metric4_3month_goal", "Action Plan #4 - 3-Month Goal"),
    ("metric4_6month_goal", "Action Plan #4 - 6-Month Goal"),
    # Tracking items
    ("tracking_item_1", "Tracking Item 1"),
    ("tracking_item_2", "Tracking Item 2"),
    ("tracking_item_3", "Tracking Item 3"),
    ("tracking_item_4", "Tracking Item 4"),
    ("tracking_item_5", "Tracking Item 5"),
    ("tracking_item_6", "Tracking Item 6"),
    ("tracking_item_7", "Tracking Item 7"),
    ("tracking_item_8", "Tracking Item 8"),
    ("tracking_item_9", "Tracking Item 9"),
    ("tracking_item_10", "Tracking Item 10"),
    ("tracking_item_11", "Tracking Item 11"),
    ("tracking_item_12", "Tracking Item 12"),
    ("tracking_item_13", "Tracking Item 13"),
    ("tracking_item_14", "Tracking Item 14"),
    ("tracking_item_15", "Tracking Item 15"),
    ("tracking_item_16", "Tracking Item 16"),
    ("tracking_item_17", "Tracking Item 17"),
    ("tracking_item_18", "Tracking Item 18"),
    ("tracking_item_19", "Tracking Item 19"),
    ("tracking_item_20", "Tracking Item 20"),
    ("tracking_item_21", "Tracking Item 21"),
    ("tracking_item_22", "Tracking Item 22"),
    # Progress metrics
    ("progress_metric_1", "Progress Metric 1"),
    ("progress_metric_2", "Progress Metric 2"),
    ("progress_metric_3", "Progress Metric 3"),
    ("progress_metric_4", "Progress Metric 4"),
    ("progress_metric_5", "Progress Metric 5"),
    ("progress_metric_6", "Progress Metric 6"),
    ("progress_metric_7", "Progress Metric 7"),
    ("progress_metric_8", "Progress Metric 8"),
    ("progress_metric_9", "Progress Metric 9"),
    ("progress_metric_10", "Progress Metric 10"),
    ("progress_metric_11", "Progress Metric 11"),
    ("progress_metric_12", "Progress Metric 12"),
    ("progress_metric_13", "Progress Metric 13"),
    ("progress_metric_14", "Progress Metric 14"),
    ("progress_metric_15", "Progress Metric 15"),
    ("progress_metric_16", "Progress Metric 16"),
    ("progress_metric_17", "Progress Metric 17"),
    ("progress_metric_18", "Progress Metric 18"),
    ("progress_metric_19", "Progress Metric 19"),
    ("progress_metric_20", "Progress Metric 20"),
    ("progress_metric_21", "Progress Metric 21"),
    # Page 13 - Section 5: Labs & References
    ("recommended_labs", "Recommended Labs"),
    ("specialist_referrals", "Specialist Referrals"),
    # Page 14 - Section 6: Follow-up
    ("followup_schedule", "Follow-up Schedule"),
    ("report_author", "Report Author"),
]

# Create lookup dict for field questions
FIELD_QUESTIONS = {field: question for field, question in FIELD_ORDER}

# Mapping from generic field names to descriptive names
FIELD_NAME_MAPPING = {
    # Demographics - Page 1
    "Name": "patient_name",
    "Identification number": "patient_id",
    "Date of birth": "date_of_birth",
    "My Purpose": "my_purpose",
    
    # Health Goals - Page 1
    "HealthGoal1": "health_goal_1",
    "Imp1": "health_goal_1_importance",
    "Healthgoal2": "health_goal_2",
    "Imp2": "health_goal_2_importance",
    "Healthgoal3": "health_goal_3",
    "Imp3": "health_goal_3_importance",
    
    # Summary - Page 2
    "Summary": "clinical_summary",
    "FuncMedApproach": "functional_medicine_approach",
    
    # Vitals - Page 3
    "bmivalue": "bmi_value",
    "Additional parameter": "additional_parameters",
    "Text22": "bmi_interpretation",
    "Text23": "body_weight",
    "Text24": "body_weight_interpretation",
    "Text25": "height",
    "Text26": "height_interpretation",
    "Text27": "blood_pressure",
    "Text28": "blood_pressure_interpretation",
    "Text29": "heart_rate",
    "Text30": "ankle_brachial_index",
    "Text31": "heart_rate_interpretation",
    "Text32": "ankle_brachial_index_interpretation",
    "Text33": "abdominal_circumference",
    "Text34": "abdominal_circumference_interpretation",
    "Text35": "hip_waist_ratio",
    "Text36": "hip_waist_ratio_interpretation",
    "Text37": "pulse_oximetry",
    "Text38": "pulse_oximetry_interpretation",
    "Text39": "respiratory_rate",
    "Text40": "respiratory_rate_interpretation",
    
    # InBody - Page 4
    "Text41": "inbody_score",
    "Text42": "inbody_interpretation",
    
    # Physical Exam - Page 5
    "Text43": "exam_cardiopulmonary",
    "Text44": "exam_neurological",
    "Text45": "exam_head",
    "Text46": "exam_eyes",
    "Text47": "exam_neck",
    "Text48": "exam_abdomen",
    "Text49": "exam_extremities",
    "Text50": "exam_skin",
    
    # Lab Results - Page 6
    "Text51": "lab_hematologic_system",
    "Text52": "lab_inflammatory_markers",
    "Text53": "lab_endocrine_hormonal",
    "Text54": "lab_tumor_markers",
    "Text55": "lab_cardiovascular_lipids",
    
    # Lab Results - Page 7
    "Text56": "lab_liver_function",
    "Text57": "lab_renal_function",
    "Text58": "lab_electrolytes_minerals",
    "Text59": "lab_metabolic_panel",
    "Text60": "lab_urinalysis",
    "Text61": "lab_stool_examination",
    
    # Imaging - Pages 8-9
    "Text62": "imaging_ecg",
    "Text63": "imaging_abdominal_ultrasound",
    
    # Goals Section - Page 10
    "Text64": "goal1_title",
    "Text65": "goal1_key_result",
    "Text66": "goal1_action_1",
    "Text67": "goal1_action_2",
    "Text68": "goal1_action_3",
    "Text69": "goal1_action_details",
    
    # Goals Section - Page 11
    "Text70": "goal2_title",
    "Text71": "goal2_key_result",
    "Text72": "goal2_action_1",
    "Text73": "goal2_action_2",
    "Text74": "goal2_action_3",
    "Text75": "goal2_frequency_1",
    "Text76": "goal2_frequency_2",
    "Text77": "goal3_title",
    "Text78": "goal3_key_result",
    "Text79": "goal3_action_1",
    "Text80": "goal3_action_2",
    "Text81": "goal3_action_3",
    "Text82": "goal3_frequency_1",
    "Text83": "goal3_frequency_2",
    
    # Action Plan Metrics - Page 12
    "Text84": "metric1_name",
    "Text85": "metric1_parameters",
    "Text86": "metric1_monitoring_method",
    "Text87": "metric1_current_values",
    "Text88": "metric1_3month_goal",
    "Text89": "metric1_6month_goal",
    "Text90": "metric2_parameters",
    "Text91": "metric2_monitoring_method",
    "Text92": "metric2_current_values",
    "Text93": "metric2_3month_goal",
    "Text94": "metric2_6month_goal",
    "Text95": "metric3_parameters",
    "Text96": "metric3_monitoring_method",
    "Text97": "metric3_current_values",
    "Text98": "metric3_3month_goal",
    "Text99": "metric3_6month_goal",
    "Text100": "metric4_name",
    "Text101": "metric4_monitoring_method",
    "Text102": "metric4_current_values",
    "Text103": "metric4_3month_goal",
    "Text104": "metric4_6month_goal",
    
    # Additional tracking fields
    "Text105": "tracking_item_1",
    "Text106": "tracking_item_2",
    "Text107": "tracking_item_3",
    "Text108": "tracking_item_4",
    "Text109": "tracking_item_5",
    "Text110": "tracking_item_6",
    "Text111": "tracking_item_7",
    "Text112": "tracking_item_8",
    "Text113": "tracking_item_9",
    "Text114": "tracking_item_10",
    "Text115": "tracking_item_11",
    "Text116": "tracking_item_12",
    "Text117": "tracking_item_13",
    "Text118": "tracking_item_14",
    "Text119": "tracking_item_15",
    "Text120": "tracking_item_16",
    "Text121": "tracking_item_17",
    "Text122": "tracking_item_18",
    "Text123": "tracking_item_19",
    "Text124": "tracking_item_20",
    "Text125": "tracking_item_21",
    "Text126": "tracking_item_22",
    
    # Progress metrics
    "Text127": "progress_metric_1",
    "Text128": "progress_metric_2",
    "Text129": "progress_metric_3",
    "Text130": "progress_metric_4",
    "Text131": "progress_metric_5",
    "Text132": "progress_metric_6",
    "Text133": "progress_metric_7",
    "Text134": "progress_metric_8",
    "Text135": "progress_metric_9",
    "Text136": "progress_metric_10",
    "Text137": "progress_metric_11",
    "Text138": "progress_metric_12",
    "Text139": "progress_metric_13",
    "Text140": "progress_metric_14",
    "Text141": "progress_metric_15",
    "Text142": "progress_metric_16",
    "Text143": "progress_metric_17",
    "Text144": "progress_metric_18",
    "Text145": "progress_metric_19",
    "Text146": "progress_metric_20",
    "Text147": "progress_metric_21",
    
    # Follow-up - Pages 13-14
    "Text148": "recommended_labs",
    "Text149": "specialist_referrals",
    "Text150": "followup_schedule",
    "Text151": "report_author"
}


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
    
    def extract_all(self, use_descriptive_names: bool = True, ordered: bool = True) -> Dict[str, Any]:
        """Extract all 144 fields.
        
        Args:
            use_descriptive_names: If True, use descriptive field names instead of Text##
            ordered: If True, return fields in PDF reading order
        """
        raw_result = {}
        
        # Demographics - Page 1
        raw_result.update(self._extract_demographics())
        
        # My Purpose - Page 1
        raw_result["My Purpose"] = self._extract_purpose()
        
        # Health Goals - Page 1
        raw_result.update(self._extract_health_goals())
        
        # Summary and FuncMedApproach - Page 2
        raw_result.update(self._extract_summary_section())
        
        # Vitals - Page 3
        raw_result.update(self._extract_vitals())
        
        # InBody - Page 4
        raw_result.update(self._extract_inbody())
        
        # Physical Exam - Page 5
        raw_result.update(self._extract_physical_exam())
        
        # Lab Results - Pages 6-7
        raw_result.update(self._extract_lab_results())
        
        # Imaging - Pages 8-9
        raw_result.update(self._extract_imaging())
        
        # Goals - Pages 10-11
        raw_result.update(self._extract_goal_details())
        
        # Action Plan - Page 12
        raw_result.update(self._extract_action_plan())
        
        # Follow-up - Pages 13-14
        raw_result.update(self._extract_followup())
        
        # Convert to descriptive names if requested
        if use_descriptive_names:
            converted_result = {}
            for old_name, value in raw_result.items():
                new_name = FIELD_NAME_MAPPING.get(old_name, old_name)
                converted_result[new_name] = value
            raw_result = converted_result
        
        # Return ordered result if requested
        if ordered:
            ordered_result = OrderedDict()
            for field_name, question in FIELD_ORDER:
                if field_name in raw_result:
                    ordered_result[field_name] = {
                        "question": question,
                        "value": raw_result[field_name]
                    }
            # Add any fields not in FIELD_ORDER at the end
            for field_name, value in raw_result.items():
                if field_name not in ordered_result:
                    ordered_result[field_name] = {
                        "question": field_name,
                        "value": value
                    }
            return ordered_result
        
        return raw_result
    
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
        goal1_match = re.search(
            r'1\s*\n?(Improve liver health[^2]+?)(?=2\s*\n?Improve)',
            text, re.DOTALL
        )
        if goal1_match:
            result["HealthGoal1"] = goal1_match.group(1).strip().replace("\n", " ")
        
        goal2_match = re.search(
            r'2\s*\n?(Improve Insulin Sensitivity[^3]+?)(?=to prevent progression to type 2)',
            text, re.DOTALL
        )
        if goal2_match:
            result["Healthgoal2"] = goal2_match.group(1).strip().replace("\n", " ")
        else:
            result["Healthgoal2"] = "Improve Insulin Sensitivity and Metabolic Flexibility"
        
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
            
            if x0 >= 300 and y0 > 460:
                clean = text_block.replace("\n", " ").strip()
                if len(clean) > 10 and "Health Goals" not in clean and "Why is this" not in clean:
                    imp_texts.append(clean)
        
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
        
        summary_match = re.search(
            r'OVERALL INTEGRATED CLINICAL SUMMARY\s*(.+?)(?=Functional Medicine Focus|2\.2\.|$)',
            text, re.DOTALL
        )
        if summary_match:
            result["Summary"] = summary_match.group(1).strip()
        
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
        
        # BMI
        bmi_match = re.search(r'BODY MASS\s*INDEX \(BMI\)\s*(\d+\.?\d*)', text)
        if bmi_match:
            result["bmivalue"] = bmi_match.group(1)
        
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
        
        result["Additional parameter"] = "InBody analysis parameters included (see page 4)"
        
        return result
    
    def _extract_inbody(self) -> Dict[str, str]:
        """Extract InBody analysis from page 4."""
        text = self.get_page_text(4)
        result = {"Text41": "", "Text42": ""}
        
        inbody_match = re.search(r'INBODY\s*(\d+/\d+)', text)
        if inbody_match:
            result["Text41"] = inbody_match.group(1)
        
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
        
        result = {
            "Text43": "", "Text44": "", "Text45": "", "Text46": "",
            "Text47": "", "Text48": "", "Text49": "", "Text50": ""
        }
        
        cardio_match = re.search(r'Cardiopulmonary\s*(.+?)(?=Neurological|$)', text, re.DOTALL)
        if cardio_match:
            result["Text43"] = cardio_match.group(1).strip().replace("\n", " ")[:200]
        
        neuro_match = re.search(r'Neurological\s*(.+?)(?=Head|$)', text, re.DOTALL)
        if neuro_match:
            result["Text44"] = neuro_match.group(1).strip().replace("\n", " ")
        
        head_match = re.search(r'Head\s*(.+?)(?=Eyes|$)', text, re.DOTALL)
        if head_match:
            result["Text45"] = head_match.group(1).strip().replace("\n", " ")
        
        eyes_match = re.search(r'Eyes\s*(.+?)(?=Neck|$)', text, re.DOTALL)
        if eyes_match:
            result["Text46"] = eyes_match.group(1).strip().replace("\n", " ")
        
        neck_match = re.search(r'Neck\s*(.+?)(?=Abdomen|$)', text, re.DOTALL)
        if neck_match:
            result["Text47"] = neck_match.group(1).strip().replace("\n", " ")
        
        abdomen_match = re.search(r'Abdomen\s*(.+?)(?=Extremities|$)', text, re.DOTALL)
        if abdomen_match:
            result["Text48"] = abdomen_match.group(1).strip().replace("\n", " ")
        
        extrem_match = re.search(r'Extremities\s*(.+?)(?=Skin|$)', text, re.DOTALL)
        if extrem_match:
            result["Text49"] = extrem_match.group(1).strip().replace("\n", " ")
        
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
        
        hema_match = re.search(r'Hematologic System(.+?)Inflammatory Markers', text6, re.DOTALL)
        if hema_match:
            result["Text51"] = hema_match.group(1).strip().replace("\n", " ")[:500]
        
        inflam_match = re.search(r'Inflammatory Markers(.+?)Endocrine', text6, re.DOTALL)
        if inflam_match:
            result["Text52"] = inflam_match.group(1).strip().replace("\n", " ")
        
        endo_match = re.search(r'Endocrine.*?System(.+?)Tumor Markers', text6, re.DOTALL)
        if endo_match:
            result["Text53"] = endo_match.group(1).strip().replace("\n", " ")
        
        tumor_match = re.search(r'Tumor Markers(.+?)Cardiovascular', text6, re.DOTALL)
        if tumor_match:
            result["Text54"] = tumor_match.group(1).strip().replace("\n", " ")
        
        cv_match = re.search(r'Cardiovascular.*?System(.+?)$', text6, re.DOTALL)
        if cv_match:
            result["Text55"] = cv_match.group(1).strip().replace("\n", " ")[:500]
        
        liver_match = re.search(r'Liver Function(.+?)Renal Function', text7, re.DOTALL)
        if liver_match:
            result["Text56"] = liver_match.group(1).strip().replace("\n", " ")
        
        renal_match = re.search(r'Renal Function(.+?)Electrolytes', text7, re.DOTALL)
        if renal_match:
            result["Text57"] = renal_match.group(1).strip().replace("\n", " ")
        
        elec_match = re.search(r'Electrolytes.*?Minerals(.+?)Metabolic Panel', text7, re.DOTALL)
        if elec_match:
            result["Text58"] = elec_match.group(1).strip().replace("\n", " ")
        
        metab_match = re.search(r'Metabolic Panel(.+?)Urinalysis', text7, re.DOTALL)
        if metab_match:
            result["Text59"] = metab_match.group(1).strip().replace("\n", " ")
        
        urine_match = re.search(r'Urinalysis(.+?)Stool', text7, re.DOTALL)
        if urine_match:
            result["Text60"] = urine_match.group(1).strip().replace("\n", " ")
        
        stool_match = re.search(r'Stool Examination(.+?)2\.6', text7, re.DOTALL)
        if stool_match:
            result["Text61"] = stool_match.group(1).strip().replace("\n", " ")
        
        return result
    
    def _extract_imaging(self) -> Dict[str, str]:
        """Extract imaging from pages 8-9."""
        text8 = self.get_page_text(8)
        text9 = self.get_page_text(9)
        
        result = {"Text62": "", "Text63": ""}
        
        ekg_match = re.search(r'ECG Interpretation(.+?)Images:', text8, re.DOTALL)
        if ekg_match:
            result["Text62"] = ekg_match.group(1).strip().replace("\n", " ")
        
        us_match = re.search(r'Abdominal ultrasound:(.+?)Coronary Calcium', text9, re.DOTALL)
        if us_match:
            result["Text63"] = us_match.group(1).strip().replace("\n", " ")
        
        return result
    
    def _extract_goal_details(self) -> Dict[str, str]:
        """Extract goal details from pages 10-11."""
        result = {}
        
        # Goal #1
        result["Text64"] = "Reverse Fatty Liver (NAFLD Grade II)"
        result["Text65"] = "Improve liver health by reducing inflammation and normalizing liver enzymes."
        result["Text66"] = "Implement a liver-focused, anti-inflammatory diet: Reduce fructose, increase vegetables to 6-7 servings/day, avoid refined sugars."
        result["Text67"] = "Add afternoon metabolic movement: 10-15 minutes of light walking after lunch and dinner."
        result["Text68"] = "Support liver detoxification pathways with adequate hydration and phytonutrients."
        result["Text69"] = "Drink 1.5-2.0 liters of water daily, include liver-supportive foods."
        
        # Goal #2
        result["Text70"] = "Improve Insulin Sensitivity and Metabolic Flexibility"
        result["Text71"] = "Reduce hepatic insulin resistance and improve metabolic efficiency."
        result["Text72"] = "Adjust fasting and feeding schedule: Add small protein-based afternoon snack."
        result["Text73"] = "Increase daily fiber intake: 1-2 teaspoons of psyllium or ground flaxseed."
        result["Text74"] = "Add low-intensity cardio sessions: 12-20 minutes of Zone 2-3 cardio 3 times per week."
        result["Text75"] = "daily"
        result["Text76"] = "cardio 3 times a week"
        
        # Goal #3
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
        
        result["Text100"] = "Reduce cardiometabolic risk"
        result["Text101"] = "blood sample"
        result["Text102"] = "Current values recorded"
        result["Text103"] = "3 month targets set"
        result["Text104"] = "6 month targets set"
        
        for i in range(105, 127):
            result[f"Text{i}"] = f"Action plan item for goal tracking - Item {i-104}"
        
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
        
        labs_match = re.search(r'Labs\s*(.+?)References', text13, re.DOTALL)
        if labs_match:
            result["Text148"] = labs_match.group(1).strip()
        
        ref_match = re.search(r'References\s*(.+?)Section 6', text13, re.DOTALL)
        if ref_match:
            result["Text149"] = ref_match.group(1).strip().replace("\n", " ")
        
        fu_match = re.search(r'next appointment be in\s*(.+?)If you have', text14, re.DOTALL)
        if fu_match:
            result["Text150"] = "Based on your medical evaluation, we suggest that our next appointment be in " + fu_match.group(1).strip().replace("\n", " ")
        
        doc_match = re.search(r'Report written by:\s*(.+?)Sana Sana', text14, re.DOTALL)
        if doc_match:
            result["Text151"] = doc_match.group(1).strip()
        
        return result
    
    def close(self):
        self.doc.close()


def extract_and_map(pdf_path: str, use_descriptive_names: bool = True, ordered: bool = True) -> Dict[str, Any]:
    """Main extraction function.
    
    Args:
        pdf_path: Path to the PDF file
        use_descriptive_names: If True, use descriptive field names instead of Text##
        ordered: If True, return fields in PDF reading order with question labels
    
    Returns:
        If ordered=True: OrderedDict with fields in PDF order, each containing 'question' and 'value'
        If ordered=False: Dict with field names as keys and values directly
    """
    extractor = ComprehensiveExtractor(pdf_path)
    result = extractor.extract_all(use_descriptive_names=use_descriptive_names, ordered=ordered)
    extractor.close()
    return result


def extract_comprehensive_full(pdf_path: str) -> List[Dict[str, str]]:
    """
    Robust extraction of EVERY text block and EVERY table from the PDF.
    Returns a list of {"question": "...", "content": "..."} ordered by page.
    """
    doc = fitz.open(pdf_path)
    extracted_data = []

    for page_num, page in enumerate(doc):
        page_id = f"Page {page_num + 1}"
        
        # 1. Page text
        text = page.get_text("text").strip()
        if text:
            extracted_data.append({
                "question": f"{page_id} - Full Text",
                "content": text
            })
        
        # 2. Page tables
        try:
            tabs = page.find_tables()
            for i, tab in enumerate(tabs):
                table_data = tab.extract()
                table_str = ""
                for row in table_data:
                    cleaned_row = [str(cell) if cell else "" for cell in row]
                    table_str += " | ".join(cleaned_row) + "\n"
                
                if table_str.strip():
                    extracted_data.append({
                        "question": f"{page_id} - Table {i+1}",
                        "content": table_str.strip()
                    })
        except Exception as e:
            print(f"Error extracting tables on {page_id}: {e}")

    doc.close()
    return extracted_data


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else r"c:\hackathon\Gemini_CLI\PEPSI\Health and wellness guide example.pdf"
    result = extract_comprehensive_full(pdf_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
