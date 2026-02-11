#!/usr/bin/env python3
"""
Generate questions.json and question_answers.json from the comprehensive extraction.

- questions.json: All form fields as questions, organized by page/section, with empty values
- question_answers.json: Same structure but with answers mapped from the comprehensive extraction
"""

import json
import os
import sys


def build_qa_structure(comprehensive_data):
    """
    Build a structured Q&A mapping from the comprehensive JSON.
    Returns (questions_only, questions_with_answers) as ordered dicts.
    """

    questions = {}
    qa_mapped = {}

    # ── Section 1: Cover / Patient Information ──
    pi = comprehensive_data.get("section_1_cover", {}).get("patient_info", {})
    goals_summary = comprehensive_data.get("section_1_cover", {}).get("primary_health_goals_summary", [])

    questions["Section 1 - Cover Page"] = {
        "Q1": {"question": "What is the patient's full name?", "field": "patient_name"},
        "Q2": {"question": "What is the patient's identification number?", "field": "identification_number"},
        "Q3": {"question": "What is the patient's date of birth?", "field": "date_of_birth"},
        "Q4": {"question": "What is the report date?", "field": "report_date"},
        "Q5": {"question": "What is the patient's purpose / motivation?", "field": "my_purpose"},
        "Q6": {"question": "What is Health Goal #1?", "field": "health_goal_1"},
        "Q7": {"question": "Why is Health Goal #1 important?", "field": "health_goal_1_importance"},
        "Q8": {"question": "What is Health Goal #2?", "field": "health_goal_2"},
        "Q9": {"question": "Why is Health Goal #2 important?", "field": "health_goal_2_importance"},
        "Q10": {"question": "What is Health Goal #3?", "field": "health_goal_3"},
        "Q11": {"question": "Why is Health Goal #3 important?", "field": "health_goal_3_importance"},
    }

    g1 = goals_summary[0] if len(goals_summary) > 0 else {}
    g2 = goals_summary[1] if len(goals_summary) > 1 else {}
    g3 = goals_summary[2] if len(goals_summary) > 2 else {}

    qa_mapped["Section 1 - Cover Page"] = {
        "Q1": {"question": "What is the patient's full name?", "answer": pi.get("name", "")},
        "Q2": {"question": "What is the patient's identification number?", "answer": pi.get("identification_number", "")},
        "Q3": {"question": "What is the patient's date of birth?", "answer": pi.get("date_of_birth", "")},
        "Q4": {"question": "What is the report date?", "answer": pi.get("report_date", "")},
        "Q5": {"question": "What is the patient's purpose / motivation?", "answer": pi.get("my_purpose", "")},
        "Q6": {"question": "What is Health Goal #1?", "answer": g1.get("goal", "")},
        "Q7": {"question": "Why is Health Goal #1 important?", "answer": g1.get("importance", "")},
        "Q8": {"question": "What is Health Goal #2?", "answer": g2.get("goal", "")},
        "Q9": {"question": "Why is Health Goal #2 important?", "answer": g2.get("importance", "")},
        "Q10": {"question": "What is Health Goal #3?", "answer": g3.get("goal", "")},
        "Q11": {"question": "Why is Health Goal #3 important?", "answer": g3.get("importance", "")},
    }

    # ── Section 2 - Clinical Summary ──
    cs = comprehensive_data.get("section_2_results_and_findings", {}).get("clinical_summary", {})
    fmp = comprehensive_data.get("section_2_results_and_findings", {}).get("functional_medicine_priorities", [])

    questions["Section 2 - Clinical Summary"] = {
        "Q12": {"question": "What are the normal findings?", "field": "normal_findings"},
        "Q13": {"question": "What are the abnormal findings?", "field": "abnormal_findings"},
        "Q14": {"question": "What is the cardiovascular risk level?", "field": "cardiovascular_risk"},
        "Q15": {"question": "What are the cardiovascular risk factors?", "field": "cardiovascular_risk_factors"},
        "Q16": {"question": "What are the functional medicine priorities?", "field": "functional_medicine_priorities"},
    }

    fmp_text = "; ".join([f"{p.get('area','')}: {p.get('action','')}" for p in fmp]) if fmp else ""

    qa_mapped["Section 2 - Clinical Summary"] = {
        "Q12": {"question": "What are the normal findings?", "answer": ", ".join(cs.get("normal_findings", []))},
        "Q13": {"question": "What are the abnormal findings?", "answer": ", ".join(cs.get("abnormal_findings", []))},
        "Q14": {"question": "What is the cardiovascular risk level?", "answer": cs.get("cardiovascular_risk", "")},
        "Q15": {"question": "What are the cardiovascular risk factors?", "answer": ", ".join(cs.get("cardiovascular_risk_factors", []))},
        "Q16": {"question": "What are the functional medicine priorities?", "answer": fmp_text},
    }

    # ── Section 2.3 - Vital Signs ──
    vs = comprehensive_data.get("section_2_3_vital_signs", {})
    vital_fields = [
        ("Q17", "What is the BMI?", "bmi"),
        ("Q18", "What is the body weight (kg)?", "body_weight_kg"),
        ("Q19", "What is the height (m)?", "height_m"),
        ("Q20", "What is the blood pressure (mmHg)?", "blood_pressure_mmhg"),
        ("Q21", "What is the heart rate (bpm)?", "heart_rate_bpm"),
        ("Q22", "What is the abdominal circumference (cm)?", "abdominal_circumference_cm"),
        ("Q23", "What is the hip-waist ratio?", "hip_waist_ratio"),
        ("Q24", "What is the pulse oximetry (%)?", "pulse_oximetry_percent"),
        ("Q25", "What is the respiratory rate (bpm)?", "respiratory_rate_bpm"),
    ]

    questions["Section 2.3 - Vital Signs"] = {}
    qa_mapped["Section 2.3 - Vital Signs"] = {}
    for qid, q_text, field in vital_fields:
        questions["Section 2.3 - Vital Signs"][qid] = {"question": q_text, "field": field}
        qa_mapped["Section 2.3 - Vital Signs"][qid] = {"question": q_text, "answer": vs.get(field, "")}

    # ── Section 2.4 - InBody Analysis ──
    questions["Section 2.4 - InBody Analysis"] = {
        "Q26": {"question": "What are the InBody analysis results?", "field": "inbody_results"},
    }
    qa_mapped["Section 2.4 - InBody Analysis"] = {
        "Q26": {"question": "What are the InBody analysis results?", "answer": "Not available in this report"},
    }

    # ── Section 2.5 - Physical Exam ──
    questions["Section 2.5 - Physical Exam"] = {
        "Q27": {"question": "What are the physical exam findings?", "field": "physical_exam_findings"},
    }
    qa_mapped["Section 2.5 - Physical Exam"] = {
        "Q27": {"question": "What are the physical exam findings?", "answer": "Not available in this report"},
    }

    # ── Section 2.6 - Laboratory Results ──
    labs = comprehensive_data.get("section_2_6_laboratory_results", {})

    q_num = 28
    questions["Section 2.6 - Laboratory Results"] = {}
    qa_mapped["Section 2.6 - Laboratory Results"] = {}

    lab_categories = [
        ("hematologic", "Hematologic"),
        ("inflammatory", "Inflammatory Markers"),
        ("endocrine", "Endocrine"),
        ("cardiovascular", "Cardiovascular / Lipid Panel"),
        ("liver", "Liver Function"),
        ("renal", "Renal Function"),
        ("electrolytes", "Electrolytes"),
        ("metabolic", "Metabolic"),
    ]

    for cat_key, cat_label in lab_categories:
        cat_data = labs.get(cat_key, {})
        for test_key, test_data in cat_data.items():
            qid = f"Q{q_num}"
            test_name = test_key.replace("_", " ").title()
            q_text = f"What is the {test_name} result? ({cat_label})"

            if isinstance(test_data, dict):
                val = test_data.get("value", "")
                unit = test_data.get("unit", "")
                ref = test_data.get("reference", "")
                answer = f"{val} {unit}".strip()
                if ref:
                    answer += f" (Reference: {ref})"
            else:
                answer = str(test_data)

            questions["Section 2.6 - Laboratory Results"][qid] = {
                "question": q_text,
                "field": f"{cat_key}.{test_key}",
                "category": cat_label
            }
            qa_mapped["Section 2.6 - Laboratory Results"][qid] = {
                "question": q_text,
                "answer": answer,
                "category": cat_label
            }
            q_num += 1

    # ── Urinalysis ──
    uri = labs.get("urinalysis", {})
    uri_fields = ["appearance", "ph", "protein", "glucose", "blood", "wbc", "rbc", "bacteria", "interpretation"]
    for field in uri_fields:
        qid = f"Q{q_num}"
        q_text = f"What is the urinalysis {field.replace('_', ' ')}?"
        questions["Section 2.6 - Laboratory Results"][qid] = {
            "question": q_text,
            "field": f"urinalysis.{field}",
            "category": "Urinalysis"
        }
        qa_mapped["Section 2.6 - Laboratory Results"][qid] = {
            "question": q_text,
            "answer": uri.get(field, ""),
            "category": "Urinalysis"
        }
        q_num += 1

    # ── Stool Examination ──
    stool = labs.get("stool_examination", {})
    stool_fields = ["rbc", "wbc", "parasites", "yeast", "consistency", "color", "interpretation"]
    for field in stool_fields:
        qid = f"Q{q_num}"
        q_text = f"What is the stool examination {field.replace('_', ' ')}?"
        questions["Section 2.6 - Laboratory Results"][qid] = {
            "question": q_text,
            "field": f"stool_examination.{field}",
            "category": "Stool Examination"
        }
        qa_mapped["Section 2.6 - Laboratory Results"][qid] = {
            "question": q_text,
            "answer": stool.get(field, ""),
            "category": "Stool Examination"
        }
        q_num += 1

    # ── Section 2.7 - ECG ──
    ecg = comprehensive_data.get("section_2_7_ecg", {})
    ecg_intervals = ecg.get("intervals", {})
    ecg_findings = ecg.get("findings", {})

    questions["Section 2.7 - ECG"] = {}
    qa_mapped["Section 2.7 - ECG"] = {}

    ecg_items = [
        (f"Q{q_num}", "What is the ECG rhythm?", ecg.get("rhythm", "")),
        (f"Q{q_num+1}", "What is the ECG heart rate?", ecg.get("rate", "")),
        (f"Q{q_num+2}", "What is the PR interval?", ecg_intervals.get("pr_interval", "")),
        (f"Q{q_num+3}", "What is the QRS duration?", ecg_intervals.get("qrs_duration", "")),
        (f"Q{q_num+4}", "What is the QT interval?", ecg_intervals.get("qt_interval", "")),
        (f"Q{q_num+5}", "What is the cardiac axis?", ecg_findings.get("axis", "")),
        (f"Q{q_num+6}", "Are there pathological Q waves?", ecg_findings.get("q_waves", "")),
        (f"Q{q_num+7}", "Is there ventricular hypertrophy?", ecg_findings.get("ventricular_hypertrophy", "")),
        (f"Q{q_num+8}", "What is the R wave progression?", ecg_findings.get("r_wave_progression", "")),
        (f"Q{q_num+9}", "What is the ST segment status?", ecg_findings.get("st_segment", "")),
        (f"Q{q_num+10}", "What is the T wave morphology?", ecg_findings.get("t_waves", "")),
        (f"Q{q_num+11}", "What is the overall ECG impression?", ecg.get("overall_impression", "")),
    ]

    for qid, q_text, answer in ecg_items:
        questions["Section 2.7 - ECG"][qid] = {"question": q_text, "field": qid.lower()}
        qa_mapped["Section 2.7 - ECG"][qid] = {"question": q_text, "answer": answer}

    q_num += 12

    # ── Section 2.8 - Imaging ──
    imaging = comprehensive_data.get("section_2_8_imaging", {})
    us = imaging.get("abdominal_ultrasound", {})
    cac = imaging.get("coronary_calcium_score", {})
    cac_dist = cac.get("distribution", {})

    questions["Section 2.8 - Imaging"] = {}
    qa_mapped["Section 2.8 - Imaging"] = {}

    imaging_items = [
        (f"Q{q_num}", "What is the hepatic steatosis grade?", us.get("hepatic_steatosis", "")),
        (f"Q{q_num+1}", "What is the gallbladder status?", us.get("gallbladder", "")),
        (f"Q{q_num+2}", "What is the pancreas finding?", us.get("pancreas", "")),
        (f"Q{q_num+3}", "What is the right kidney finding?", us.get("right_kidney", "")),
        (f"Q{q_num+4}", "What is the prostate size?", us.get("prostate", "")),
        (f"Q{q_num+5}", "What is the total coronary calcium score?", str(cac.get("total_score", ""))),
        (f"Q{q_num+6}", "What is the calcium score percentile?", str(cac.get("percentile", ""))),
        (f"Q{q_num+7}", "What is the coronary calcium risk level?", cac.get("risk", "")),
        (f"Q{q_num+8}", "What is the Left Main calcium score?", str(cac_dist.get("left_main", ""))),
        (f"Q{q_num+9}", "What is the LAD calcium score?", str(cac_dist.get("lad", ""))),
        (f"Q{q_num+10}", "What is the LCx calcium score?", str(cac_dist.get("lcx", ""))),
        (f"Q{q_num+11}", "What is the RCA calcium score?", str(cac_dist.get("rca", ""))),
        (f"Q{q_num+12}", "What is the PDA calcium score?", str(cac_dist.get("pda", ""))),
    ]

    for qid, q_text, answer in imaging_items:
        questions["Section 2.8 - Imaging"][qid] = {"question": q_text, "field": qid.lower()}
        qa_mapped["Section 2.8 - Imaging"][qid] = {"question": q_text, "answer": answer}

    q_num += 13

    # ── Section 3 - Health Goals (Detailed) ──
    goals = comprehensive_data.get("section_3_health_goals_detailed", [])

    questions["Section 3 - Health Goals (Detailed)"] = {}
    qa_mapped["Section 3 - Health Goals (Detailed)"] = {}

    for gi, goal in enumerate(goals, 1):
        # Goal title
        qid = f"Q{q_num}"
        questions["Section 3 - Health Goals (Detailed)"][qid] = {
            "question": f"What is the title of Health Goal #{gi}?", "field": f"goal_{gi}_title"
        }
        qa_mapped["Section 3 - Health Goals (Detailed)"][qid] = {
            "question": f"What is the title of Health Goal #{gi}?", "answer": goal.get("title", "")
        }
        q_num += 1

        # Key result
        qid = f"Q{q_num}"
        questions["Section 3 - Health Goals (Detailed)"][qid] = {
            "question": f"What is the key result for Health Goal #{gi}?", "field": f"goal_{gi}_key_result"
        }
        qa_mapped["Section 3 - Health Goals (Detailed)"][qid] = {
            "question": f"What is the key result for Health Goal #{gi}?", "answer": goal.get("key_result", "")
        }
        q_num += 1

        # Importance
        qid = f"Q{q_num}"
        questions["Section 3 - Health Goals (Detailed)"][qid] = {
            "question": f"Why is Health Goal #{gi} important?", "field": f"goal_{gi}_importance"
        }
        qa_mapped["Section 3 - Health Goals (Detailed)"][qid] = {
            "question": f"Why is Health Goal #{gi} important?", "answer": goal.get("importance", "")
        }
        q_num += 1

        # Actions
        for ai, action in enumerate(goal.get("actions", []), 1):
            qid = f"Q{q_num}"
            q_text = f"What is Action #{ai} for Health Goal #{gi}?"
            details_text = "; ".join(action.get("details", []))
            answer = f"{action.get('action', '')} — {details_text} (Frequency: {action.get('frequency', '')})"

            questions["Section 3 - Health Goals (Detailed)"][qid] = {
                "question": q_text, "field": f"goal_{gi}_action_{ai}"
            }
            qa_mapped["Section 3 - Health Goals (Detailed)"][qid] = {
                "question": q_text, "answer": answer
            }
            q_num += 1

    # ── Section 4 - Action Plan (Metrics & Targets) ──
    metrics = comprehensive_data.get("section_4_action_plan", {}).get("metrics_and_targets", [])

    questions["Section 4 - Action Plan Metrics & Targets"] = {}
    qa_mapped["Section 4 - Action Plan Metrics & Targets"] = {}

    for mi, metric in enumerate(metrics, 1):
        goal_name = metric.get("goal", "")
        monitoring = metric.get("monitoring", "")
        current = metric.get("current_values", {})
        targets = metric.get("targets", {})

        # Goal name
        qid = f"Q{q_num}"
        questions["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What is Metric Goal #{mi}?", "field": f"metric_{mi}_goal"
        }
        qa_mapped["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What is Metric Goal #{mi}?", "answer": goal_name
        }
        q_num += 1

        # Monitoring method
        qid = f"Q{q_num}"
        questions["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"How is Metric Goal #{mi} monitored?", "field": f"metric_{mi}_monitoring"
        }
        qa_mapped["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"How is Metric Goal #{mi} monitored?", "answer": monitoring
        }
        q_num += 1

        # Current values
        qid = f"Q{q_num}"
        current_str = ", ".join([f"{k}: {v}" for k, v in current.items()])
        questions["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What are the current values for Metric Goal #{mi}?", "field": f"metric_{mi}_current"
        }
        qa_mapped["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What are the current values for Metric Goal #{mi}?", "answer": current_str
        }
        q_num += 1

        # 3-month targets
        t3 = targets.get("3_month", {})
        qid = f"Q{q_num}"
        t3_str = ", ".join([f"{k}: {v}" for k, v in t3.items()])
        questions["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What are the 3-month targets for Metric Goal #{mi}?", "field": f"metric_{mi}_3month"
        }
        qa_mapped["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What are the 3-month targets for Metric Goal #{mi}?", "answer": t3_str
        }
        q_num += 1

        # 6-month targets
        t6 = targets.get("6_month", {})
        qid = f"Q{q_num}"
        t6_str = ", ".join([f"{k}: {v}" for k, v in t6.items()])
        questions["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What are the 6-month targets for Metric Goal #{mi}?", "field": f"metric_{mi}_6month"
        }
        qa_mapped["Section 4 - Action Plan Metrics & Targets"][qid] = {
            "question": f"What are the 6-month targets for Metric Goal #{mi}?", "answer": t6_str
        }
        q_num += 1

    # ── Section 5 - Complimentary Info ──
    comp = comprehensive_data.get("section_5_complimentary_info", {})

    questions["Section 5 - Complimentary Information"] = {
        f"Q{q_num}": {"question": "What specialist referrals are recommended?", "field": "referrals"},
        f"Q{q_num+1}": {"question": "Are additional labs needed?", "field": "labs_needed"},
    }
    qa_mapped["Section 5 - Complimentary Information"] = {
        f"Q{q_num}": {"question": "What specialist referrals are recommended?", "answer": ", ".join(comp.get("referrals", []))},
        f"Q{q_num+1}": {"question": "Are additional labs needed?", "answer": comp.get("labs_needed", "")},
    }
    q_num += 2

    # ── Section 6 - Follow-up ──
    fu = comprehensive_data.get("section_6_followup", {})
    schedule = fu.get("schedule", [])
    tracking = fu.get("tracking_methods", [])

    questions["Section 6 - Follow-up"] = {}
    qa_mapped["Section 6 - Follow-up"] = {}

    qid = f"Q{q_num}"
    schedule_str = "; ".join([f"{s.get('type','')}: {s.get('timing','')}" for s in schedule])
    questions["Section 6 - Follow-up"][qid] = {"question": "What is the follow-up schedule?", "field": "follow_up_schedule"}
    qa_mapped["Section 6 - Follow-up"][qid] = {"question": "What is the follow-up schedule?", "answer": schedule_str}
    q_num += 1

    qid = f"Q{q_num}"
    questions["Section 6 - Follow-up"][qid] = {"question": "What tracking methods are recommended?", "field": "tracking_methods"}
    qa_mapped["Section 6 - Follow-up"][qid] = {"question": "What tracking methods are recommended?", "answer": ", ".join(tracking)}
    q_num += 1

    # ── Section 7 - Supplements ──
    supps = comprehensive_data.get("section_7_supplements", {})

    questions["Section 7 - Supplements"] = {}
    qa_mapped["Section 7 - Supplements"] = {}

    # Safe supplements
    safe = supps.get("safe_with_rivaroxaban", [])
    qid = f"Q{q_num}"
    safe_str = "; ".join([
        f"{s.get('name','')}" + (f" ({s.get('dose','')})" if s.get('dose') else "")
        for s in safe
    ])
    questions["Section 7 - Supplements"][qid] = {"question": "Which supplements are safe with Rivaroxaban?", "field": "safe_supplements"}
    qa_mapped["Section 7 - Supplements"][qid] = {"question": "Which supplements are safe with Rivaroxaban?", "answer": safe_str}
    q_num += 1

    # Caution supplements
    caution = supps.get("use_with_caution", [])
    qid = f"Q{q_num}"
    caution_str = "; ".join([
        f"{s.get('name','')}" + (f" ({s.get('dose','')})" if s.get('dose') else "")
        for s in caution
    ])
    questions["Section 7 - Supplements"][qid] = {"question": "Which supplements should be used with caution?", "field": "caution_supplements"}
    qa_mapped["Section 7 - Supplements"][qid] = {"question": "Which supplements should be used with caution?", "answer": caution_str}
    q_num += 1

    # Avoid supplements
    avoid = supps.get("avoid", [])
    qid = f"Q{q_num}"
    avoid_str = "; ".join([f"{s.get('name','')}: {s.get('reason','')}" for s in avoid])
    questions["Section 7 - Supplements"][qid] = {"question": "Which supplements should be avoided?", "field": "avoid_supplements"}
    qa_mapped["Section 7 - Supplements"][qid] = {"question": "Which supplements should be avoided?", "answer": avoid_str}
    q_num += 1

    # ── Section 8 - Contact & Doctor ──
    contact = comprehensive_data.get("section_8_contact", {})
    doc = contact.get("doctor", {})
    ci = contact.get("contact_info", {})
    appts = contact.get("next_appointments", {})

    questions["Section 8 - Contact Information"] = {
        f"Q{q_num}": {"question": "Who is the attending doctor?", "field": "doctor_name"},
        f"Q{q_num+1}": {"question": "What is the medical organization?", "field": "organization"},
        f"Q{q_num+2}": {"question": "What is the WhatsApp contact number?", "field": "whatsapp"},
        f"Q{q_num+3}": {"question": "What is the medical team contact number?", "field": "medical_team_phone"},
        f"Q{q_num+4}": {"question": "When is the next lab appointment?", "field": "next_lab_appointment"},
        f"Q{q_num+5}": {"question": "When is the next ultrasound appointment?", "field": "next_ultrasound_appointment"},
    }
    qa_mapped["Section 8 - Contact Information"] = {
        f"Q{q_num}": {"question": "Who is the attending doctor?", "answer": doc.get("name", "")},
        f"Q{q_num+1}": {"question": "What is the medical organization?", "answer": doc.get("organization", "")},
        f"Q{q_num+2}": {"question": "What is the WhatsApp contact number?", "answer": ci.get("whatsapp", "")},
        f"Q{q_num+3}": {"question": "What is the medical team contact number?", "answer": ci.get("medical_team", "")},
        f"Q{q_num+4}": {"question": "When is the next lab appointment?", "answer": appts.get("labs", "")},
        f"Q{q_num+5}": {"question": "When is the next ultrasound appointment?", "answer": appts.get("abdominal_ultrasound", "")},
    }
    q_num += 6

    print(f"Total questions generated: {q_num - 1}")
    return questions, qa_mapped


def main():
    # Default to the comprehensive JSON
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = "data/Health and wellness guide example_comprehensive.json"

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        comprehensive_data = json.load(f)

    questions, qa_mapped = build_qa_structure(comprehensive_data)

    # Determine output directory
    out_dir = os.path.dirname(input_path) if os.path.dirname(input_path) else "data"

    # Write questions.json (questions only, no answers)
    questions_path = os.path.join(out_dir, "questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"Saved: {questions_path}")

    # Write question_answers.json (questions + answers mapped)
    qa_path = os.path.join(out_dir, "question_answers.json")
    with open(qa_path, "w", encoding="utf-8") as f:
        json.dump(qa_mapped, f, indent=2, ensure_ascii=False)
    print(f"Saved: {qa_path}")


if __name__ == "__main__":
    main()
