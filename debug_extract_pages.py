import fitz
import os

pdf_path = 'data/Health and wellness guide example.pdf'
doc = fitz.open(pdf_path)
os.makedirs('data/raw_pages', exist_ok=True)

for i, page in enumerate(doc):
    with open(f'data/raw_pages/page_{i+1}.txt', 'w', encoding='utf-8') as f:
        f.write(page.get_text())
doc.close()
print("Extracted all pages to data/raw_pages/")
