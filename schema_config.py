"""
Schema Configuration for Health and Wellness PDF Form Fields
Maps the fillable PDF form fields to extraction rules.
"""

# Section boundaries by page number
SECTION_CONFIG = {
    "demographics": {"pages": [1], "y_range": (150, 290)},
    "my_purpose": {"pages": [1], "y_range": (290, 400)},
    "health_goals": {"pages": [1], "y_range": (400, 600)},
    "summary": {"pages": [2], "y_range": (100, 500)},
    "functional_medicine": {"pages": [2], "y_range": (500, 800)},
    "vitals": {"pages": [3], "y_range": (70, 550)},
    "inbody": {"pages": [3, 4], "y_range": (550, 800)},
    "physical_exam": {"pages": [5], "y_range": (80, 800)},
    "lab_results": {"pages": [6, 7], "y_range": (80, 700)},
    "imaging": {"pages": [7, 8, 9], "y_range": (600, 600)},
    "goals_section": {"pages": [10, 11], "y_range": (70, 700)},
    "action_plan": {"pages": [12], "y_range": (70, 700)},
    "labs_references": {"pages": [13], "y_range": (70, 300)},
    "follow_up": {"pages": [13, 14], "y_range": (280, 400)},
}

# Named field definitions with extraction rules
NAMED_FIELDS = {
    # Page 1 - Demographics
    "Name": {
        "page": 1,
        "extract_type": "label_value",
        "labels": ["Name:", "Name"],
        "section": "demographics"
    },
    "Identification number": {
        "page": 1,
        "extract_type": "label_value",
        "labels": ["Identification number", "ID number"],
        "section": "demographics"
    },
    "Date of birth": {
        "page": 1,
        "extract_type": "label_value",
        "labels": ["Date of birth", "DOB"],
        "section": "demographics"
    },
    
    # Page 1 - Purpose and Goals
    "My Purpose": {
        "page": 1,
        "extract_type": "section_text",
        "after_header": "Why do I want to improve my health?",
        "before_header": "MY PRIMARY HEALTH GOALS",
        "section": "my_purpose"
    },
    "HealthGoal1": {
        "page": 1,
        "extract_type": "numbered_list",
        "list_index": 0,
        "column": "goals",
        "section": "health_goals"
    },
    "Imp1": {
        "page": 1,
        "extract_type": "numbered_list",
        "list_index": 0,
        "column": "importance",
        "section": "health_goals"
    },
    "Healthgoal2": {
        "page": 1,
        "extract_type": "numbered_list",
        "list_index": 1,
        "column": "goals",
        "section": "health_goals"
    },
    "Imp2": {
        "page": 1,
        "extract_type": "numbered_list",
        "list_index": 1,
        "column": "importance",
        "section": "health_goals"
    },
    "Healthgoal3": {
        "page": 1,
        "extract_type": "numbered_list",
        "list_index": 2,
        "column": "goals",
        "section": "health_goals"
    },
    "Imp3": {
        "page": 1,
        "extract_type": "numbered_list",
        "list_index": 2,
        "column": "importance",
        "section": "health_goals"
    },
    
    # Page 2 - Summary and Functional Medicine
    "Summary": {
        "page": 2,
        "extract_type": "section_text",
        "after_header": "2.1. SUMMARY:",
        "before_header": "2.2. FUNCTIONAL MEDICINE",
        "section": "summary"
    },
    "FuncMedApproach": {
        "page": 2,
        "extract_type": "section_text",
        "after_header": "Functional Medicine Focus",
        "before_header": "2.3. VITAL SIGNS",
        "section": "functional_medicine"
    },
    
    # Page 3 - Vitals
    "bmivalue": {
        "page": 3,
        "extract_type": "table_value",
        "row_label": "BODY MASS INDEX",
        "column": "value",
        "section": "vitals"
    },
    "Additional parameter": {
        "page": 3,
        "extract_type": "section_text",
        "after_header": "Additional parameters",
        "section": "vitals"
    },
}

# Table field mappings for generic Text## fields
# Maps Text field names to (page, row_label, column) tuples
VITALS_TABLE_FIELDS = {
    "Text22": ("BMI", "interpretation"),
    "Text23": ("BODY WEIGHT", "value"),
    "Text24": ("BODY WEIGHT", "interpretation"),
    "Text25": ("HEIGHT", "value"),
    "Text26": ("HEIGHT", "interpretation"),
    "Text27": ("ARTERIAL PRESSURE", "value"),
    "Text28": ("ARTERIAL PRESSURE", "interpretation"),
    "Text29": ("CARDIAC FREQUENCY", "value"),
    "Text30": ("ANKLE-BRACHIAL INDEX", "value"),
    "Text31": ("CARDIAC FREQUENCY", "interpretation"),
    "Text32": ("ANKLE-BRACHIAL INDEX", "interpretation"),
    "Text33": ("ABDOMINAL CIRCUMFERENCE", "value"),
    "Text34": ("ABDOMINAL CIRCUMFERENCE", "interpretation"),
    "Text35": ("HIP WAIST RATIO", "value"),
    "Text36": ("HIP WAIST RATIO", "interpretation"),
    "Text37": ("PULSE OXIMETRY", "value"),
    "Text38": ("PULSE OXIMETRY", "interpretation"),
    "Text39": ("RESPIRATORY FREQUENCY", "value"),
    "Text40": ("RESPIRATORY FREQUENCY", "interpretation"),
    "Text41": ("INBODY", "value"),
    "Text42": ("INBODY", "interpretation"),
}

PHYSICAL_EXAM_FIELDS = {
    "Text43": ("Cardiopulmonary", "findings"),
    "Text44": ("Neurological", "findings"),
    "Text45": ("Head", "findings"),
    "Text46": ("Eyes", "findings"),
    "Text47": ("Neck", "findings"),
    "Text48": ("Abdomen", "findings"),
    "Text49": ("Extremities", "findings"),
    "Text50": ("Skin", "findings"),
}

LAB_RESULT_SECTIONS = {
    "Text51": "Hematologic System",
    "Text52": "Inflammatory Markers",
    "Text53": "Endocrine System",
    "Text54": "Tumor Markers",
    "Text55": "Cardiovascular System",
    "Text56": "Liver Function",
    "Text57": "Renal Function",
    "Text58": "Electrolytes",
    "Text59": "Metabolic Panel",
    "Text60": "Urinalysis",
    "Text61": "Stool Examination",
}

IMAGING_FIELDS = {
    "Text62": "EKG",
    "Text63": "Images",
}

# Goal and Action Plan fields (pages 7-10)
GOAL_FIELDS = {
    "Text64": ("Goal1", "key_result_1"),
    "Text65": ("Goal1", "key_action_1.1"),
    "Text66": ("Goal1", "key_action_1.2"),
    "Text67": ("Goal1", "key_action_1.3"),
    "Text68": ("Goal1", "key_result_2"),
    "Text69": ("Goal1", "key_action_2.1"),
    "Text70": ("Goal2", "title"),
    "Text71": ("Goal2", "key_result_header"),
    "Text72": ("Goal2", "key_action_1.1"),
    "Text73": ("Goal2", "key_action_1.2"),
    "Text74": ("Goal2", "key_action_1.3"),
    "Text75": ("Goal2", "key_result_2"),
    "Text76": ("Goal2", "key_action_2.1"),
    "Text77": ("Goal3", "title"),
    "Text78": ("Goal3", "key_result_1"),
    "Text79": ("Goal3", "key_action_1.1"),
    "Text80": ("Goal3", "key_action_1.2"),
    "Text81": ("Goal3", "key_action_1.3"),
    "Text82": ("Goal3", "key_result_2"),
    "Text83": ("Goal3", "key_action_2.1"),
}

# Action Plan metrics table fields (page 9-10)
ACTION_PLAN_FIELDS = {
    # Metric 1
    "Text84": ("Metric1", "description"),
    "Text85": ("Metric1", "metrics"),
    "Text86": ("Metric1", "monitor"),
    "Text87": ("Metric1", "current"),
    "Text88": ("Metric1", "3month"),
    "Text89": ("Metric1", "6month"),
    # Metric 2
    "Text90": ("Metric2", "metrics"),
    "Text91": ("Metric2", "monitor"),
    "Text92": ("Metric2", "current"),
    "Text93": ("Metric2", "3month"),
    "Text94": ("Metric2", "6month"),
    # Metric 3
    "Text95": ("Metric3", "metrics"),
    "Text96": ("Metric3", "monitor"),
    "Text97": ("Metric3", "current"),
    "Text98": ("Metric3", "3month"),
    "Text99": ("Metric3", "6month"),
    # Metric 4
    "Text100": ("Metric4", "metrics"),
    "Text101": ("Metric4", "monitor"),
    "Text102": ("Metric4", "current"),
    "Text103": ("Metric4", "3month"),
    "Text104": ("Metric4", "6month"),
}

# Follow-up and references
FOLLOWUP_FIELDS = {
    "Text148": "Labs",
    "Text149": "References",
    "Text150": "Follow-up schedule",
    "Text151": "Doctor info",
}

# Complete field schema list (all 151+ fields from the fillable PDF)
def build_complete_schema():
    """Build a complete schema of all form fields."""
    schema = {}
    
    # Add named fields
    for field_name, config in NAMED_FIELDS.items():
        schema[field_name] = config
    
    # Add vitals table fields
    for field_name, (label, col) in VITALS_TABLE_FIELDS.items():
        schema[field_name] = {
            "page": 3,
            "extract_type": "table_value",
            "row_label": label,
            "column": col,
            "section": "vitals"
        }
    
    # Add physical exam fields
    for field_name, (organ, col) in PHYSICAL_EXAM_FIELDS.items():
        schema[field_name] = {
            "page": 5,
            "extract_type": "organ_system",
            "organ": organ,
            "column": col,
            "section": "physical_exam"
        }
    
    # Add lab result fields
    for field_name, section in LAB_RESULT_SECTIONS.items():
        schema[field_name] = {
            "pages": [6, 7],
            "extract_type": "lab_section",
            "section_name": section,
            "section": "lab_results"
        }
    
    # Add imaging fields
    for field_name, section in IMAGING_FIELDS.items():
        schema[field_name] = {
            "pages": [7, 8, 9],
            "extract_type": "imaging_section",
            "section_name": section,
            "section": "imaging"
        }
    
    # Add goal fields
    for field_name, (goal, subfield) in GOAL_FIELDS.items():
        schema[field_name] = {
            "pages": [7, 8],
            "extract_type": "goal_section",
            "goal": goal,
            "subfield": subfield,
            "section": "goals_section"
        }
    
    # Add action plan fields
    for field_name, (metric, subfield) in ACTION_PLAN_FIELDS.items():
        schema[field_name] = {
            "pages": [9, 10],
            "extract_type": "action_plan",
            "metric": metric,
            "subfield": subfield,
            "section": "action_plan"
        }
    
    # Add remaining Text fields as generic content fields
    for i in range(105, 148):
        field_name = f"Text{i}"
        if field_name not in schema:
            schema[field_name] = {
                "pages": [9, 10, 11],
                "extract_type": "generic",
                "section": "action_plan"
            }
    
    # Add follow-up fields
    for field_name, section in FOLLOWUP_FIELDS.items():
        schema[field_name] = {
            "pages": [13, 14],
            "extract_type": "followup",
            "section_name": section,
            "section": "follow_up"
        }
    
    return schema

FIELD_SCHEMA = build_complete_schema()
