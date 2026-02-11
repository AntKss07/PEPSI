import fitz
doc = fitz.open('data/Health and wellness guide example.pdf')
with open('debug_text.txt', 'w', encoding='utf-8') as f:
    f.write("--- PAGE 3 ---\n")
    f.write(doc[2].get_text())
    f.write("\n--- PAGE 4 ---\n")
    f.write(doc[3].get_text())
doc.close()
