"""
deep_audit.py
Exhaustive search: for each missing field, search ALL source pages for matching text.
Also dumps full text of each source page to help understand page alignment.
"""
import fitz
import json

SOURCE = "data/Health and wellness guide example.pdf"
TARGET = "data/HEALTH AND WELLNESS GUIDE - Fillable Guide 1.pdf"

mapped = json.load(open("data/mapped_data.json"))
src = fitz.open(SOURCE)
tgt = fitz.open(TARGET)

# Transform from map_fields.py
keywords = ["Name", "Date of birth", "Identification"]
src_rects, tgt_rects = [], []
for w in keywords:
    s = src[0].search_for(w)
    t = tgt[0].search_for(w)
    if s and t:
        src_rects.append(s[0])
        tgt_rects.append(t[0])

sx = sum(t.width/s.width for s,t in zip(src_rects, tgt_rects) if s.width > 1) / len(src_rects)
sy = sum(t.height/s.height for s,t in zip(src_rects, tgt_rects) if s.height > 1) / len(src_rects)
dx = sum(t.x0 - s.x0*sx for s,t in zip(src_rects, tgt_rects)) / len(src_rects)
dy = sum(t.y0 - s.y0*sy for s,t in zip(src_rects, tgt_rects)) / len(src_rects)

def tgt_to_src(rect):
    return fitz.Rect(
        (rect.x0 - dx) / sx,
        (rect.y0 - dy) / sy,
        (rect.x1 - dx) / sx,
        (rect.y1 - dy) / sy
    )

out = open("data/deep_audit.txt", "w", encoding="utf-8")
out.write(f"Source: {len(src)} pages, Target: {len(tgt)} pages\n")
out.write(f"Transform: sx={sx:.3f} sy={sy:.3f} dx={dx:.1f} dy={dy:.1f}\n\n")

# 1. Show first 200 chars of each source page to understand structure
out.write("=" * 60 + "\nSOURCE PAGE SUMMARIES\n" + "=" * 60 + "\n")
for i in range(len(src)):
    text = src[i].get_text("text")[:200].replace("\n", " | ")
    out.write(f"Source Page {i+1}: {text}\n\n")

# 2. Show first 200 chars of each target page
out.write("=" * 60 + "\nTARGET PAGE SUMMARIES\n" + "=" * 60 + "\n")
for i in range(len(tgt)):
    text = tgt[i].get_text("text")[:200].replace("\n", " | ")
    out.write(f"Target Page {i+1}: {text}\n\n")

# 3. For each missing field, search ALL source pages
out.write("=" * 60 + "\nMISSING FIELD ANALYSIS\n" + "=" * 60 + "\n")
for tgt_page_idx in range(len(tgt)):
    tgt_page = tgt[tgt_page_idx]
    for widget in tgt_page.widgets():
        name = widget.field_name
        if name in mapped:
            continue
        
        wr = widget.rect
        sr = tgt_to_src(wr)
        
        out.write(f"\nTarget Page {tgt_page_idx+1} | {name} | TargetRect: {wr}\n")
        out.write(f"  Expected Source Rect: {sr}\n")
        
        # Search on SAME page index
        if tgt_page_idx < len(src):
            clip50 = fitz.Rect(sr.x0-50, sr.y0-50, sr.x1+50, sr.y1+50)
            text = src[tgt_page_idx].get_text("text", clip=clip50).strip()
            out.write(f"  Same page (Src {tgt_page_idx+1}, 50px): '{text[:150]}'\n")
        
        # Search on SHIFTED pages (+1, +2, +3, -1)
        for offset in [1, 2, 3, -1]:
            sp = tgt_page_idx + offset
            if 0 <= sp < len(src):
                clip50 = fitz.Rect(sr.x0-50, sr.y0-50, sr.x1+50, sr.y1+50)
                text = src[sp].get_text("text", clip=clip50).strip()
                if text:
                    out.write(f"  Shifted page (Src {sp+1}, 50px): '{text[:150]}'\n")

out.close()
print("Deep audit saved to data/deep_audit.txt")
src.close()
tgt.close()
