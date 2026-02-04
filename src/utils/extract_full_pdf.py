import fitz
import json

def extract_comprehensive_data(pdf_path):
    doc = fitz.open(pdf_path)
    full_data = {
        "metadata": {
            "source": pdf_path,
            "total_pages": len(doc)
        },
        "pages": []
    }

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Extract plain text
        text = page.get_text("text")
        
        # 2. Extract tables
        tables = []
        try:
            tabs = page.find_tables()
            for tab in tabs:
                table_data = tab.extract()
                # Clean up empty rows/cols if any
                cleaned_table = [[(cell if cell else "") for cell in row] for row in table_data]
                tables.append({
                    "bbox": tab.bbox,
                    "rows": len(cleaned_table),
                    "cols": len(cleaned_table[0]) if cleaned_table else 0,
                    "data": cleaned_table
                })
        except Exception as e:
            print(f"Error extracting tables on page {page_num+1}: {e}")

        page_info = {
            "page_number": page_num + 1,
            "text": text,
            "tables": tables
        }
        full_data["pages"].append(page_info)

    doc.close()
    return full_data

if __name__ == "__main__":
    pdf_path = r"c:\hackathon\Gemini_CLI\PEPSI\Health and wellness guide example.pdf"
    data = extract_comprehensive_data(pdf_path)
    
    with open("full_pdf_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted data from {len(data['pages'])} pages and saved to full_pdf_data.json")
