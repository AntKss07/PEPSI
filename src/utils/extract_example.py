"""
Script to extract text content from the example PDF (filled health report)
"""
import fitz  # PyMuPDF
import json

def extract_text_with_structure(pdf_path):
    """Extract text content from a PDF with page structure"""
    doc = fitz.open(pdf_path)
    content = []
    
    for page_num, page in enumerate(doc):
        # Get text blocks for better structure understanding
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
                    "block_type": block[5] if len(block) > 5 else "text"
                }
                page_content["blocks"].append(block_info)
        
        content.append(page_content)
    
    doc.close()
    return content

# Extract from example PDF
print("=" * 60)
print("EXTRACTING CONTENT FROM EXAMPLE PDF (FILLED REPORT)")
print("=" * 60)

example_pdf = r"c:\KSS\PROJECTS\PEPSI\Health and wellness guide example.pdf"
content = extract_text_with_structure(example_pdf)

# Print page-by-page content
for page in content:
    print(f"\n{'='*60}")
    print(f"PAGE {page['page']}")
    print("="*60)
    print(page['text'])

# Save detailed content
with open("example_pdf_content.json", "w", encoding="utf-8") as f:
    json.dump(content, f, indent=2, ensure_ascii=False)

print("\n\nSaved detailed content to example_pdf_content.json")
