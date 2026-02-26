"""
map_fields.py - PDF-to-PDF Field Mapper
Maps text from a filled source PDF to form fields in a blank target PDF.
Uses calibrated affine transform + word-level extraction for accuracy.
"""
import json
import sys
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

    print(f"  Transform: sx={sx:.3f}, sy={sy:.3f}, dx={dx:.1f}, dy={dy:.1f}")
    return sx, sy, dx, dy


def tgt_to_src_rect(rect, sx, sy, dx, dy):
    """Convert target PDF coordinates back to source PDF coordinates."""
    return fitz.Rect(
        (rect.x0 - dx) / sx,
        (rect.y0 - dy) / sy,
        (rect.x1 - dx) / sx,
        (rect.y1 - dy) / sy
    )


def get_words_in_area(page, clip):
    """Get all words from a page that fall within or overlap the clip area.
    Uses word-level extraction which preserves natural word boundaries.
    Returns words sorted in reading order (top-to-bottom, left-to-right).
    """
    all_words = page.get_text("words")  # [(x0,y0,x1,y1, "word", block, line, word_idx)]
    matches = []
    for w in all_words:
        wx0, wy0, wx1, wy1 = w[:4]
        word_text = w[4]
        # Check if word center falls within clip area
        wcx = (wx0 + wx1) / 2
        wcy = (wy0 + wy1) / 2
        if clip.x0 <= wcx <= clip.x1 and clip.y0 <= wcy <= clip.y1:
            matches.append(w)
    # Sort: by Y position (row), then X position (column)
    matches.sort(key=lambda w: (round(w[1], 0), w[0]))
    return matches


def words_to_text(words):
    """Convert a list of word tuples to a readable string.
    Groups words on the same line, joins with spaces.
    """
    if not words:
        return ""
    lines = []
    current_line = [words[0][4]]
    current_y = round(words[0][1], 0)

    for w in words[1:]:
        wy = round(w[1], 0)
        if abs(wy - current_y) > 5:  # New line (>5px vertical gap)
            lines.append(" ".join(current_line))
            current_line = [w[4]]
            current_y = wy
        else:
            current_line.append(w[4])

    lines.append(" ".join(current_line))
    return " ".join(lines)


def extract_field_text(src_doc, src_rect, same_page_idx, sx, sy, dx, dy, src_pages):
    """Try to extract text for a field, searching same page first, then neighbors."""
    # Build search order: same page first, then +1, +2, +3, -1
    pages_to_try = [same_page_idx]
    for offset in [1, 2, 3, -1]:
        sp = same_page_idx + offset
        if 0 <= sp < src_pages and sp not in pages_to_try:
            pages_to_try.append(sp)

    field_width = src_rect.x1 - src_rect.x0
    field_height = src_rect.y1 - src_rect.y0

    for src_page_idx in pages_to_try:
        page = src_doc[src_page_idx]

        # Tight clip: small left margin, extend right by 75% of width,
        # extend down by half field height (captures multi-line text)
        clip = fitz.Rect(
            src_rect.x0 - 3,
            src_rect.y0 - 2,
            src_rect.x1 + max(20, field_width * 0.75),
            src_rect.y1 + max(2, field_height * 0.5)
        )
        clip = clip & page.rect

        words = get_words_in_area(page, clip)
        if words:
            text = words_to_text(words)
            if text.strip():
                return text.strip()

        # Wide search: extend right by full width, down by full height
        clip_wide = fitz.Rect(
            src_rect.x0 - 10,
            src_rect.y0 - 10,
            src_rect.x1 + max(80, field_width * 1.5),
            src_rect.y1 + max(10, field_height)
        )
        clip_wide = clip_wide & page.rect

        words = get_words_in_area(page, clip_wide)
        if words:
            text = words_to_text(words)
            if text.strip():
                return text.strip()

    return ""


def map_pdf_to_pdf(source_pdf_path, target_pdf_path, output_path):
    print(f"Mapping from: {source_pdf_path}")
    print(f"        to:   {target_pdf_path}")

    try:
        src_doc = fitz.open(source_pdf_path)
        tgt_doc = fitz.open(target_pdf_path)
    except Exception as e:
        print(f"Error opening PDFs: {e}")
        return

    sx, sy, dx, dy = calculate_transform(src_doc[0], tgt_doc[0])

    src_pages = len(src_doc)
    tgt_pages = len(tgt_doc)
    print(f"  Source: {src_pages} pages, Target: {tgt_pages} pages")

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
            src_rect = tgt_to_src_rect(widget.rect, sx, sy, dx, dy)

            # Extract text
            text = extract_field_text(
                src_doc, src_rect, tgt_page_idx,
                sx, sy, dx, dy, src_pages
            )

            if text:
                # Clean: remove leading colon artifacts
                text = re.sub(r'^:\s*', '', text).strip()
                if text:
                    mapped_data[widget.field_name] = text
                    page_mapped += 1

        print(f"  Page {tgt_page_idx + 1}: Mapped {page_mapped} fields.")

    src_doc.close()
    tgt_doc.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapped_data, f, indent=2, ensure_ascii=False)

    missed = total_widgets - len(mapped_data)
    print(f"\n  Result: Mapped {len(mapped_data)} of {total_widgets} fields.")
    if missed:
        print(f"  Missed: {missed} fields (no text found in source).")
    else:
        print("  Perfect: All fields mapped!")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python map_fields.py <source_pdf> <target_pdf> <output_json>")
        sys.exit(1)
    map_pdf_to_pdf(sys.argv[1], sys.argv[2], sys.argv[3])
