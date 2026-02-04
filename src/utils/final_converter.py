import json
import fitz

def pdf_to_structured_json(pdf_path, output_json):
    doc = fitz.open(pdf_path)
    structured_data = []

    for page_num, page in enumerate(doc):
        page_id = f"Page {page_num + 1}"
        
        # 1. Add general page text as one block
        text = page.get_text("text").strip()
        if text:
            structured_data.append({
                "question": f"{page_id} - Full Text",
                "content": text
            })
        
        # 2. Extract and format tables
        tabs = page.find_tables()
        for i, tab in enumerate(tabs):
            table_data = tab.extract()
            # Convert table to a readable string format for the "content" field
            table_str = ""
            for row in table_data:
                cleaned_row = [str(cell) if cell else "" for cell in row]
                table_str += " | ".join(cleaned_row) + "\n"
            
            structured_data.append({
                "question": f"{page_id} - Table {i+1}",
                "content": table_str.strip()
            })
            
            # Also add a structured version if they want to see internal JSON logic
            # but the user asked for "questions with content" format.

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)
    
    doc.close()
    return structured_data

def update_doc_creator_with_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    with open("doc_creator.py", "w", encoding="utf-8") as f:
        f.write("import json\n\n")
        f.write(f"test_data = {json.dumps(data, indent=4)}\n\n")
        f.write("""
def create_doc(data, output_file="final_comprehensive_report.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("HEALTH AND WELLNESS - FULL PDF EXTRACTION REPORT\\n")
        f.write("="*80 + "\\n\\n")
        
        for item in data:
            f.write(f"--- {item['question']} ---\\n")
            f.write(f"{item['content']}\\n")
            f.write("\\n" + "="*40 + "\\n\\n")
            
    print(f"Final report created: {output_file}")

if __name__ == "__main__":
    create_doc(test_data)
""")

if __name__ == "__main__":
    pdf_path = r"c:\hackathon\Gemini_CLI\PEPSI\Health and wellness guide example.pdf"
    output_json = "final_extracted_content.json"
    
    print("Extracting ALL content and tables...")
    structured_json = pdf_to_structured_json(pdf_path, output_json)
    print(f"Saved {len(structured_json)} items (Text Blocks & Tables) to {output_json}")
    
    print("Updating doc_creator.py...")
    update_doc_creator_with_json(output_json)
    print("Done!")
