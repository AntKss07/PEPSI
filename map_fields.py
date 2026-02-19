"""
map_fields.py - Ultimate PDF-to-PDF Field Mapper
Uses calibrated affine transform + clip-based text extraction.
Handles page count mismatch by searching across multiple source pages.
Wide horizontal clip to capture full sentences.
"""
import json
import sys
import os
import re
import fitz  # PyMuPDF

def calculate_transform(src_page, tgt_page):
    """Calculate affine transform (scale + offset) from Page 1 keywords."""
    keywords = ["Name", "Date of birth", "Identification"]
    src_rects, tgt_rects = [], []
    
    for word in keywords:
        s_r = src_page.search_for(word)
        t_r = tgt_page.search_for(word)
        if s_r and t_r:
            src_rects.append(s_r[0])
            tgt_rects.append(t_r[0])
    
    if not src_rects:
        print("Warning: No alignment keywords found. Using identity.")
        return 1.0, 1.0, 0.0, 0.0

    sx_s = [t.width / s.width for s, t in zip(src_rects, tgt_rects) if s.width > 1]
    sy_s = [t.height / s.height for s, t in zip(src_rects, tgt_rects) if s.height > 1]
    sx = sum(sx_s) / len(sx_s) if sx_s else 1.0
    sy = sum(sy_s) / len(sy_s) if sy_s else 1.0
    
    dx_s = [t.x0 - s.x0 * sx for s, t in zip(src_rects, tgt_rects)]
    dy_s = [t.y0 - s.y0 * sy for s, t in zip(src_rects, tgt_rects)]
    dx = sum(dx_s) / len(dx_s) if dx_s else 0.0
    dy = sum(dy_s) / len(dy_s) if dy_s else 0.0
    
    print(f"Computed Transform: sx={sx:.3f}, sy={sy:.3f}, dx={dx:.1f}, dy={dy:.1f}")
    return sx, sy, dx, dy

def tgt_rect_to_src(rect, sx, sy, dx, dy):
    """Convert target PDF coordinates back to source PDF coordinates."""
    return fitz.Rect(
        (rect.x0 - dx) / sx,
        (rect.y0 - dy) / sy,
        (rect.x1 - dx) / sx,
        (rect.y1 - dy) / sy
    )

def extract_text_from_clip(page, clip, right_extend=5, v_buffer=3):
    """Extract text from a clipping rectangle.
    Extends RIGHT side significantly (to capture full sentences),
    keeps LEFT side tight (to avoid label bleed).
    """
    expanded = fitz.Rect(
        clip.x0 - 3,        # Keep left tight (just 3px)
        clip.y0 - v_buffer,
        clip.x1 + right_extend,  # Extend right to capture full text
        clip.y1 + v_buffer
    )
    # Clamp to page bounds
    page_rect = page.rect
    expanded = fitz.Rect(
        max(expanded.x0, page_rect.x0),
        max(expanded.y0, page_rect.y0),
        min(expanded.x1, page_rect.x1),
        min(expanded.y1, page_rect.y1)
    )
    text = page.get_text("text", clip=expanded).strip()
    if text:
        return " ".join(text.split())
    return ""

def clean_field_text(field_name, text):
    """Remove stray leading characters from label bleed-through."""
    # Only remove a leading colon with optional spaces
    text = re.sub(r'^:\s*', '', text)
    return text.strip()

def map_pdf_to_pdf(source_pdf_path, target_pdf_path, output_path):
    print(f"Mapping from {source_pdf_path} to fields in {target_pdf_path}...")
    
    try:
        src_doc = fitz.open(source_pdf_path)
        tgt_doc = fitz.open(target_pdf_path)
    except Exception as e:
        print(f"Error opening PDFs: {e}")
        return

    sx, sy, dx, dy = calculate_transform(src_doc[0], tgt_doc[0])
    
    src_pages = len(src_doc)
    tgt_pages = len(tgt_doc)
    print(f"Source: {src_pages} pages, Target: {tgt_pages} pages")
    
    mapped_data = {}
    total_widgets = 0
    
    for tgt_page_idx in range(tgt_pages):
        tgt_page = tgt_doc[tgt_page_idx]
        page_mapped = 0
        
        for widget in tgt_page.widgets():
            if not widget.field_name:
                continue
            total_widgets += 1
            
            # Convert widget rect to source coordinates
            src_rect = tgt_rect_to_src(widget.rect, sx, sy, dx, dy)
            
            # Calculate field width in source space
            field_width = src_rect.x1 - src_rect.x0
            
            # Extend RIGHT to capture full sentences, but not left (avoid labels)
            if field_width > 100:  # Wide field (paragraph/description)
                r_ext = 100
            elif field_width > 50:  # Medium field
                r_ext = 50
            else:  # Narrow field (values like "31.1", "109.9 kg")
                r_ext = 10
            v_buf = 3  # Keep vertical tight to avoid row bleed
            
            best_text = ""
            
            # Search across pages
            pages_to_try = [tgt_page_idx]
            for offset in [1, 2, 3, -1]:
                sp = tgt_page_idx + offset
                if 0 <= sp < src_pages and sp not in pages_to_try:
                    pages_to_try.append(sp)
            
            for src_page_idx in pages_to_try:
                src_page = src_doc[src_page_idx]
                
                # Try with calculated buffers
                text = extract_text_from_clip(src_page, src_rect, right_extend=r_ext, v_buffer=v_buf)
                
                # If nothing, try wider
                if not text:
                    text = extract_text_from_clip(src_page, src_rect, right_extend=r_ext+30, v_buffer=10)
                
                if text:
                    if not best_text:
                        best_text = text
                    elif src_page_idx == tgt_page_idx:
                        best_text = text
                    break
            
            if best_text:
                # Clean stray characters
                best_text = clean_field_text(widget.field_name, best_text)
                if best_text:
                    mapped_data[widget.field_name] = best_text
                    page_mapped += 1
        
        print(f"  Page {tgt_page_idx+1}: Mapped {page_mapped} fields.")

    src_doc.close()
    tgt_doc.close()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapped_data, f, indent=2, ensure_ascii=False)
    
    missed = total_widgets - len(mapped_data)
    print(f"\nMapped {len(mapped_data)} of {total_widgets} fields.")
    print(f"Missed {missed} fields (empty in source document).")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python map_fields.py <source_pdf> <target_pdf> <output_json>")
        sys.exit(1)
    map_pdf_to_pdf(sys.argv[1], sys.argv[2], sys.argv[3])
