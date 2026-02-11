import fitz
pdfs = ['data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf', 'data/Health and wellness guide example.pdf']
for pdf in pdfs:
    try:
        doc = fitz.open(pdf)
        w_count = sum(len(list(p.widgets())) for p in doc)
        print(f"{pdf}: {w_count} widgets")
        doc.close()
    except Exception as e:
        print(f"{pdf}: Error {e}")
