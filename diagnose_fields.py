"""
diagnose_fields.py
Find where each missing field is, and what text exists nearby in the source PDF.
"""
import fitz
import json

SOURCE = "data/Health and wellness guide example.pdf"
TARGET = "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf"

# Load mapped data
mapped = json.load(open("data/mapped_data.json"))

src = fitz.open(SOURCE)
tgt = fitz.open(TARGET)

# Get transform params (from map_fields.py logic)
keywords = ["Name", "Date of birth", "Identification"]
src_rects, tgt_rects = [], []
for w in keywords:
    s = src[0].search_for(w)
    t = tgt[0].search_for(w)
    if s and t:
        src_rects.append(s[0])
        tgt_rects.append(t[0])

sx_s = [t.width/s.width for s,t in zip(src_rects, tgt_rects) if s.width > 1]
sy_s = [t.height/s.height for s,t in zip(src_rects, tgt_rects) if s.height > 1]
sx = sum(sx_s)/len(sx_s)
sy = sum(sy_s)/len(sy_s)
dx_s = [t.x0 - s.x0*sx for s,t in zip(src_rects, tgt_rects)]
dy_s = [t.y0 - s.y0*sy for s,t in zip(src_rects, tgt_rects)]
dx = sum(dx_s)/len(dx_s)
dy = sum(dy_s)/len(dy_s)

# Inverse transform: given target coords, find source coords
# target = source * scale + offset
# source = (target - offset) / scale
def tgt_to_src(rect):
    return fitz.Rect(
        (rect.x0 - dx) / sx,
        (rect.y0 - dy) / sy,
        (rect.x1 - dx) / sx,
        (rect.y1 - dy) / sy
    )

out = open("data/field_diagnosis.txt", "w", encoding="utf-8")
out.write(f"Transform: sx={sx:.3f} sy={sy:.3f} dx={dx:.1f} dy={dy:.1f}\n\n")

for page_idx in range(min(len(src), len(tgt))):
    tgt_page = tgt[page_idx]
    src_page = src[page_idx]
    
    for widget in tgt_page.widgets():
        name = widget.field_name
        if name in mapped:
            continue  # Skip already mapped
        
        # Where is this field on the target?
        wr = widget.rect
        # Convert to source coordinates
        sr = tgt_to_src(wr)
        
        # Search for ANY text in the source at this location (expanded by 15px)
        expanded = fitz.Rect(sr.x0-15, sr.y0-15, sr.x1+15, sr.y1+15)
        
        # Get text in that area
        text_in_area = src_page.get_text("text", clip=expanded).strip()
        
        out.write(f"Page {page_idx+1} | Field: {name}\n")
        out.write(f"  Target rect: {wr}\n")
        out.write(f"  Source rect (inverse): {sr}\n")
        out.write(f"  Text found nearby: '{text_in_area[:100]}'\n\n")

out.close()
print("Diagnosis saved to data/field_diagnosis.txt")

src.close()
tgt.close()
