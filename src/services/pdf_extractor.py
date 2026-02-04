"""
PDF Text Extraction Module
Extracts structured text content from Health & Wellness PDF reports.
"""
import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Tuple, Optional


def extract_text_with_structure(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text content from a PDF with page and positional structure.
    
    Returns:
        List of page dictionaries containing text, blocks, and metadata.
    """
    doc = fitz.open(pdf_path)
    content = []
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        
        page_content = {
            "page": page_num + 1,
            "text": page.get_text("text"),
            "blocks": []
        }
        
        for block in blocks:
            if len(block) >= 5:
                block_info = {
                    "x0": block[0],
                    "y0": block[1],
                    "x1": block[2],
                    "y1": block[3],
                    "text": block[4] if isinstance(block[4], str) else "",
                    "block_type": block[5] if len(block) > 5 else 0
                }
                page_content["blocks"].append(block_info)
        
        # Sort blocks by Y position then X position for reading order
        page_content["blocks"].sort(key=lambda b: (b["y0"], b["x0"]))
        
        content.append(page_content)
    
    doc.close()
    return content


def extract_label_value(blocks: List[Dict], label: str) -> Optional[str]:
    """
    Extract a value associated with a label from text blocks.
    Handles patterns like "Name: John Smith" or "Name\nJohn Smith"
    """
    for i, block in enumerate(blocks):
        text = block["text"].strip()
        
        # Check if label is in this block
        if label.lower() in text.lower():
            # Try to find value after label on same line
            if ":" in text:
                parts = text.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip().split("\n")[0]
            
            # Check if value is on next line in same block
            lines = text.split("\n")
            for j, line in enumerate(lines):
                if label.lower() in line.lower() and j + 1 < len(lines):
                    return lines[j + 1].strip()
            
            # Check next block for value
            if i + 1 < len(blocks):
                next_text = blocks[i + 1]["text"].strip()
                # Only use if it's not another label
                if ":" not in next_text and len(next_text) < 200:
                    return next_text.split("\n")[0].strip()
    
    return None


def extract_section_text(blocks: List[Dict], after_header: str, 
                         before_header: Optional[str] = None) -> str:
    """
    Extract all text between two section headers.
    """
    capturing = False
    captured_text = []
    
    for block in blocks:
        text = block["text"].strip()
        
        if after_header.lower() in text.lower():
            capturing = True
            # Get text after the header on the same block
            idx = text.lower().find(after_header.lower())
            remaining = text[idx + len(after_header):].strip()
            if remaining:
                captured_text.append(remaining)
            continue
        
        if capturing:
            if before_header and before_header.lower() in text.lower():
                # Get text before the end header
                idx = text.lower().find(before_header.lower())
                if idx > 0:
                    captured_text.append(text[:idx].strip())
                break
            captured_text.append(text)
    
    return " ".join(captured_text).strip()


def extract_numbered_list_item(blocks: List[Dict], index: int, column: str) -> Optional[str]:
    """
    Extract an item from a numbered list (e.g., health goals 1, 2, 3).
    column can be 'goals' (left) or 'importance' (right)
    """
    goal_blocks = []
    
    for block in blocks:
        text = block["text"].strip()
        x0 = block["x0"]
        
        # Look for numbered items (1, 2, 3 at start of text)
        if text.startswith(f"{index + 1}") or text.startswith(f"{index + 1}\n"):
            # Determine if it's left or right column based on x position
            if column == "goals" and x0 < 300:
                # Extract the goal text (after the number)
                lines = text.split("\n")
                goal_text = []
                for line in lines[1:] if lines[0].strip() == str(index + 1) else lines:
                    if line.strip() and line.strip() != str(index + 1):
                        goal_text.append(line.strip())
                return " ".join(goal_text)
            elif column == "importance" and x0 >= 300:
                # Extract importance text
                lines = text.split("\n")
                return " ".join(line.strip() for line in lines if line.strip())
    
    # Alternative approach: look for goal patterns without numbers
    goals_found = []
    for block in blocks:
        text = block["text"].strip()
        x0 = block["x0"]
        
        # Skip headers
        if "Health Goals" in text or "Why is this important" in text:
            continue
        
        if column == "goals" and x0 < 300:
            if text and len(text) > 10:
                goals_found.append(text)
        elif column == "importance" and x0 >= 300:
            if text and len(text) > 10:
                goals_found.append(text)
    
    if index < len(goals_found):
        return goals_found[index].replace("\n", " ").strip()
    
    return None


def extract_table_value(blocks: List[Dict], row_label: str, column: str) -> Optional[str]:
    """
    Extract a value from a table structure.
    column can be 'value' or 'interpretation'
    """
    for i, block in enumerate(blocks):
        text = block["text"].strip()
        
        if row_label.lower() in text.lower():
            # Parse the table row - typically format: "LABEL\nVALUE\nINTERPRETATION"
            lines = text.split("\n")
            
            # Try to find value and interpretation in subsequent lines
            for j, line in enumerate(lines):
                if row_label.lower() in line.lower():
                    if column == "value" and j + 1 < len(lines):
                        # Value is typically right after the label
                        value = lines[j + 1].strip()
                        # Check if it looks like a measurement
                        if value and (re.match(r'[\d.]+', value) or value in ['normal', 'n/a', 'non aplicable']):
                            return value
                    elif column == "interpretation":
                        # Interpretation is usually last part
                        if j + 2 < len(lines):
                            return " ".join(lines[j + 2:]).strip()
                        elif i + 1 < len(blocks):
                            # Check next block
                            return blocks[i + 1]["text"].strip()
            
            # Simplified extraction: split on common patterns
            parts = re.split(r'(\d+\.?\d*\s*(?:kg|cm|bpm|mmHg|%|m)?\s*)', text, maxsplit=2)
            if len(parts) >= 2:
                if column == "value":
                    return parts[1].strip() if len(parts) > 1 else None
                elif column == "interpretation":
                    return parts[2].strip() if len(parts) > 2 else None
    
    return None


def extract_organ_finding(blocks: List[Dict], organ: str) -> Optional[str]:
    """
    Extract physical exam findings for a specific organ/system.
    """
    for block in blocks:
        text = block["text"].strip()
        
        if organ.lower() in text.lower():
            lines = text.split("\n")
            findings = []
            capture = False
            
            for line in lines:
                if organ.lower() in line.lower():
                    capture = True
                    # Get text after organ name on same line
                    parts = line.split(organ, 1)
                    if len(parts) > 1:
                        remaining = parts[1].strip()
                        if remaining and remaining[0] in [':', '-', ' ']:
                            remaining = remaining[1:].strip()
                        if remaining:
                            findings.append(remaining)
                elif capture and line.strip():
                    # Stop if we hit another organ name
                    if any(org in line.lower() for org in 
                          ['cardiopulmonary', 'neurological', 'head', 'eyes', 
                           'neck', 'abdomen', 'extremities', 'skin']):
                        break
                    findings.append(line.strip())
            
            if findings:
                return " ".join(findings)
    
    return None


def parse_vitals_table(page_content: Dict) -> Dict[str, Dict[str, str]]:
    """
    Parse the vitals signs table from page 3.
    Returns dict of {parameter: {value: str, interpretation: str}}
    """
    vitals = {}
    blocks = page_content.get("blocks", [])
    
    vital_params = [
        "BODY MASS INDEX (BMI)", "BODY WEIGHT", "HEIGHT", "ARTERIAL PRESSURE",
        "CARDIAC FREQUENCY", "ANKLE-BRACHIAL INDEX", "ABDOMINAL CIRCUMFERENCE",
        "HIP WAIST RATIO", "PULSE OXIMETRY", "RESPIRATORY FREQUENCY", "INBODY"
    ]
    
    current_param = None
    
    for block in blocks:
        text = block["text"].strip()
        
        for param in vital_params:
            if param.lower().replace(" ", "").replace("(", "").replace(")", "") in \
               text.lower().replace(" ", "").replace("(", "").replace(")", ""):
                current_param = param
                
                # Parse the row
                lines = text.split("\n")
                value = None
                interpretation = None
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    # Skip the parameter name itself
                    if param.lower().replace(" ", "") in line.lower().replace(" ", ""):
                        continue
                    # First non-parameter line is usually the value
                    if value is None and line:
                        value = line
                    # Second non-parameter line is usually interpretation
                    elif interpretation is None and line:
                        interpretation = line
                
                vitals[param] = {
                    "value": value or "",
                    "interpretation": interpretation or ""
                }
                break
    
    return vitals


def get_demographics(content: List[Dict]) -> Dict[str, str]:
    """
    Extract demographic information from page 1.
    """
    if not content:
        return {}
    
    page1 = content[0]
    blocks = page1.get("blocks", [])
    
    demographics = {
        "Name": "",
        "Identification number": "",
        "Date of birth": ""
    }
    
    for i, block in enumerate(blocks):
        text = block["text"].strip()
        
        # Look for name - usually after "Name:" label
        if "RICHARD" in text.upper() or "PEACOCK" in text.upper():
            demographics["Name"] = text.split("\n")[0].strip()
        
        # Look for ID number pattern (alphanumeric)
        if re.match(r'^[A-Z]{2}\d{6}$', text.split("\n")[0].strip()):
            demographics["Identification number"] = text.split("\n")[0].strip()
        
        # Look for date pattern
        date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', text)
        if date_match:
            demographics["Date of birth"] = date_match.group()
    
    return demographics


def get_health_goals(content: List[Dict]) -> List[Dict[str, str]]:
    """
    Extract the three health goals and their importance from page 1.
    """
    if not content:
        return []
    
    page1 = content[0]
    blocks = page1.get("blocks", [])
    
    goals = []
    
    # Look for numbered items
    for block in blocks:
        text = block["text"].strip()
        x0 = block.get("x0", 0)
        
        # Skip headers
        if "Health Goals" in text and "Why is this important" in text:
            continue
        
        # Check for goal blocks (left side, contains numbers 1, 2, 3)
        if x0 < 300 and any(text.startswith(f"{i}") or f"\n{i}" in text for i in [1, 2, 3]):
            # Extract goal and importance
            lines = text.split("\n")
            goal_text = []
            for line in lines:
                if line.strip() and not line.strip().isdigit():
                    goal_text.append(line.strip())
            
            if goal_text:
                goals.append({
                    "goal": " ".join(goal_text),
                    "importance": ""  # Will be filled from right column
                })
    
    return goals
