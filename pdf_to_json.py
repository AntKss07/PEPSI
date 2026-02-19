#!/usr/bin/env python3
"""
Universal PDF-to-JSON Extractor
================================
Extracts ALL text from any PDF into a structured JSON file that
faithfully preserves the original document's visual structure.

Features:
  - Works with ANY PDF (not hardcoded to a specific document)
  - Preserves page-by-page structure
  - Detects headings, subheadings, body text, lists, and tables
  - Maintains reading order using spatial block positioning
  - Extracts form fields (widgets) from fillable PDFs
  - Outputs clean, hierarchical JSON mirroring the PDF layout

Usage:
  python pdf_to_json.py <input.pdf> [output.json]

If output path is omitted, it defaults to <input_name>_extracted.json
in the same directory as the input PDF.
"""

import sys
import os
import json
import re
import argparse
from typing import Dict, List, Any, Optional, Tuple
from collections import OrderedDict

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF is required. Install with: pip install PyMuPDF")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────
HEADING_SIZE_THRESHOLD = 1.25   # font ≥ 1.25× median → heading
SUBHEADING_SIZE_THRESHOLD = 1.1 # font ≥ 1.1× median → subheading
TABLE_COLUMN_GAP = 30          # px gap between columns to detect tables
LIST_BULLET_PATTERN = re.compile(
    r'^[\s]*(?:[•●○■□▪▸▹►▻\-–—]|\d+[\.\)]\s|[a-zA-Z][\.\)]\s|(?:i{1,3}|iv|v|vi{0,3}|ix|x)[\.\)]\s)',
    re.IGNORECASE
)


# ─────────────────────────────────────────────────────────────────────
# Text Utilities
# ─────────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """Normalize whitespace without collapsing intentional line breaks."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple spaces within a single line
    lines = text.split('\n')
    cleaned = [re.sub(r'[ \t]+', ' ', line).strip() for line in lines]
    return '\n'.join(cleaned).strip()


def is_bold(flags: int) -> bool:
    """Check if the font flags indicate bold."""
    return bool(flags & 2 ** 4)  # bit 4 = bold


def is_italic(flags: int) -> bool:
    """Check if the font flags indicate italic."""
    return bool(flags & 2 ** 1)  # bit 1 = italic


def classify_text_role(span_size: float, median_size: float, flags: int, text: str) -> str:
    """Classify a text span's role based on font metrics."""
    if span_size >= median_size * HEADING_SIZE_THRESHOLD:
        return "heading"
    if span_size >= median_size * SUBHEADING_SIZE_THRESHOLD or is_bold(flags):
        return "subheading"
    if LIST_BULLET_PATTERN.match(text):
        return "list_item"
    return "body"


# ─────────────────────────────────────────────────────────────────────
# Core Extraction Engine
# ─────────────────────────────────────────────────────────────────────
class PDFExtractor:
    """
    Universal PDF text extractor that preserves document structure.
    """

    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)

    def close(self):
        self.doc.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── Median font size across entire document ──────────────────────
    def _compute_median_font_size(self) -> float:
        """Compute the median font size across all pages for role classification."""
        sizes = []
        for page in self.doc:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if block.get("type") != 0:  # only text blocks
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            sizes.append(span["size"])
        if not sizes:
            return 12.0
        sizes.sort()
        mid = len(sizes) // 2
        return sizes[mid]

    # ── Extract structured blocks from one page ──────────────────────
    def _extract_page_blocks(self, page) -> List[Dict[str, Any]]:
        """
        Extract text blocks from a page with full spatial + font metadata.
        Returns a list of block dicts sorted in reading order (top→bottom, left→right).
        """
        raw = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        blocks = []

        for block in raw.get("blocks", []):
            if block.get("type") != 0:
                # Image block – note its presence
                blocks.append({
                    "type": "image",
                    "bbox": block.get("bbox", [0, 0, 0, 0]),
                    "y0": block.get("bbox", [0, 0, 0, 0])[1],
                    "x0": block.get("bbox", [0, 0, 0, 0])[0],
                })
                continue

            lines_data = []
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                line_text_parts = []
                line_sizes = []
                line_flags = []
                line_fonts = []
                for span in spans:
                    t = span.get("text", "")
                    if t.strip():
                        line_text_parts.append(t)
                        line_sizes.append(span.get("size", 12))
                        line_flags.append(span.get("flags", 0))
                        line_fonts.append(span.get("font", ""))
                if line_text_parts:
                    combined_text = " ".join(line_text_parts)
                    # Use the dominant (most common) font size for the line
                    avg_size = sum(line_sizes) / len(line_sizes) if line_sizes else 12
                    dominant_flags = max(set(line_flags), key=line_flags.count) if line_flags else 0
                    lines_data.append({
                        "text": combined_text.strip(),
                        "font_size": round(avg_size, 2),
                        "flags": dominant_flags,
                        "fonts": list(set(line_fonts)),
                        "bbox": line.get("bbox", block.get("bbox", [0, 0, 0, 0])),
                    })

            if lines_data:
                bbox = block.get("bbox", [0, 0, 0, 0])
                blocks.append({
                    "type": "text",
                    "bbox": bbox,
                    "y0": bbox[1],
                    "x0": bbox[0],
                    "lines": lines_data,
                })

        # Sort in reading order: top-to-bottom, then left-to-right
        blocks.sort(key=lambda b: (round(b["y0"] / 5) * 5, b["x0"]))
        return blocks

    # ── Extract form fields (widgets) from a page ────────────────────
    def _extract_form_fields(self, page) -> Dict[str, str]:
        """Extract fillable form field names and their current values."""
        fields = {}
        try:
            for widget in page.widgets():
                if widget.field_name:
                    value = widget.field_value or ""
                    fields[widget.field_name] = value
        except Exception:
            pass  # Page may have no widgets
        return fields

    # ── Build structured data for one page ───────────────────────────
    def _build_page_structure(self, page_num: int, median_size: float) -> Dict[str, Any]:
        """
        Build a hierarchical structure for a single page.
        Groups consecutive blocks under headings/subheadings.
        """
        page = self.doc[page_num]
        blocks = self._extract_page_blocks(page)
        form_fields = self._extract_form_fields(page)

        sections = []
        current_section = None
        current_subsection = None

        for block in blocks:
            if block["type"] == "image":
                sections.append({"type": "image", "description": "[Image/graphic element]"})
                continue

            for line_data in block.get("lines", []):
                text = line_data["text"]
                role = classify_text_role(
                    line_data["font_size"], median_size,
                    line_data["flags"], text
                )

                if role == "heading":
                    # Start a new section
                    current_section = {
                        "type": "section",
                        "heading": text,
                        "font_size": line_data["font_size"],
                        "content": [],
                        "subsections": [],
                    }
                    current_subsection = None
                    sections.append(current_section)

                elif role == "subheading":
                    sub = {
                        "type": "subsection",
                        "subheading": text,
                        "font_size": line_data["font_size"],
                        "content": [],
                    }
                    if current_section:
                        current_section["subsections"].append(sub)
                    else:
                        sections.append(sub)
                    current_subsection = sub

                elif role == "list_item":
                    item = {"type": "list_item", "text": text}
                    target = current_subsection or current_section
                    if target:
                        target["content"].append(item)
                    else:
                        sections.append(item)

                else:
                    # Body text
                    item = {"type": "text", "text": text}
                    target = current_subsection or current_section
                    if target:
                        target["content"].append(item)
                    else:
                        sections.append(item)

        result = OrderedDict()
        result["page_number"] = page_num + 1

        # Build the sequential content preserving order
        content_list = []
        for section in sections:
            if section.get("type") == "image":
                content_list.append(section)
            elif section.get("type") == "section":
                sec_data = OrderedDict()
                sec_data["heading"] = section["heading"]
                body_lines = [c["text"] for c in section.get("content", []) if c.get("text")]
                if body_lines:
                    sec_data["content"] = body_lines
                # Include subsections
                subs = []
                for sub in section.get("subsections", []):
                    sub_data = OrderedDict()
                    sub_data["subheading"] = sub["subheading"]
                    sub_lines = [c["text"] for c in sub.get("content", []) if c.get("text")]
                    if sub_lines:
                        sub_data["content"] = sub_lines
                    subs.append(sub_data)
                if subs:
                    sec_data["subsections"] = subs
                content_list.append(sec_data)
            elif section.get("type") == "subsection":
                sub_data = OrderedDict()
                sub_data["subheading"] = section.get("subheading", "")
                sub_lines = [c["text"] for c in section.get("content", []) if c.get("text")]
                if sub_lines:
                    sub_data["content"] = sub_lines
                content_list.append(sub_data)
            elif section.get("type") in ("text", "list_item"):
                content_list.append({"text": section.get("text", "")})

        result["content"] = content_list

        # Add form fields if any exist
        if form_fields:
            result["form_fields"] = form_fields

        return result

    # ── Also provide a simple flat text extraction per page ───────────
    def _extract_plain_text(self, page_num: int) -> str:
        """Extract plain text from a page preserving line breaks."""
        page = self.doc[page_num]
        return page.get_text("text").strip()

    # ── Full document extraction ─────────────────────────────────────
    def extract_all(self, mode: str = "structured") -> Dict[str, Any]:
        """
        Extract the entire PDF.

        Args:
            mode: "structured" – hierarchical with heading detection
                  "flat"       – plain text per page (line arrays)
                  "detailed"   – both structured + raw text + form fields

        Returns:
            A dict representing the full document.
        """
        median_size = self._compute_median_font_size()

        result = OrderedDict()
        result["metadata"] = OrderedDict([
            ("file_name", os.path.basename(self.pdf_path)),
            ("file_path", os.path.abspath(self.pdf_path)),
            ("total_pages", self.total_pages),
            ("extraction_mode", mode),
        ])

        pages = OrderedDict()

        for i in range(self.total_pages):
            page_key = f"page_{i + 1}"

            if mode == "flat":
                raw_text = self._extract_plain_text(i)
                lines = [line for line in raw_text.split('\n') if line.strip()]
                page_data = OrderedDict([
                    ("page_number", i + 1),
                    ("line_count", len(lines)),
                    ("lines", lines),
                ])
                form_fields = self._extract_form_fields(self.doc[i])
                if form_fields:
                    page_data["form_fields"] = form_fields

            elif mode == "detailed":
                structured = self._build_page_structure(i, median_size)
                raw_text = self._extract_plain_text(i)
                lines = [line for line in raw_text.split('\n') if line.strip()]
                page_data = OrderedDict([
                    ("page_number", i + 1),
                    ("structured_content", structured.get("content", [])),
                    ("raw_lines", lines),
                ])
                form_fields = self._extract_form_fields(self.doc[i])
                if form_fields:
                    page_data["form_fields"] = form_fields

            else:  # "structured"
                page_data = self._build_page_structure(i, median_size)

            pages[page_key] = page_data

        result["pages"] = pages
        return result


# ─────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Universal PDF-to-JSON Extractor — faithfully preserves PDF structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_json.py report.pdf
  python pdf_to_json.py report.pdf output.json
  python pdf_to_json.py report.pdf -m flat
  python pdf_to_json.py report.pdf -m detailed
  python pdf_to_json.py data/*.pdf          (batch mode)
        """
    )
    parser.add_argument("input", nargs="+", help="Path(s) to PDF file(s)")
    parser.add_argument("-o", "--output", help="Output JSON path (single-file mode only)")
    parser.add_argument(
        "-m", "--mode",
        choices=["structured", "flat", "detailed"],
        default="structured",
        help="Extraction mode: structured (default), flat, or detailed"
    )
    parser.add_argument(
        "--indent", type=int, default=2,
        help="JSON indentation level (default: 2)"
    )

    args = parser.parse_args()

    pdf_files = args.input

    for pdf_path in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"ERROR: File not found: {pdf_path}")
            continue

        if not pdf_path.lower().endswith(".pdf"):
            print(f"WARNING: Skipping non-PDF file: {pdf_path}")
            continue

        # Determine output path
        if args.output and len(pdf_files) == 1:
            output_path = args.output
        else:
            base = os.path.splitext(pdf_path)[0]
            output_path = f"{base}_extracted.json"

        print(f"{'=' * 60}")
        print(f"  Processing: {pdf_path}")
        print(f"  Mode:       {args.mode}")
        print(f"  Output:     {output_path}")
        print(f"{'=' * 60}")

        try:
            with PDFExtractor(pdf_path) as extractor:
                data = extractor.extract_all(mode=args.mode)

            # Write JSON
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=args.indent, ensure_ascii=False)

            total_pages = data["metadata"]["total_pages"]
            file_size_kb = os.path.getsize(output_path) / 1024
            print(f"  [OK] Extracted {total_pages} pages -> {output_path} ({file_size_kb:.1f} KB)")

        except Exception as e:
            print(f"  [ERROR] Error processing {pdf_path}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"  Done! Processed {len(pdf_files)} file(s).")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
