"""Extract PDF text word by word with position information"""
import sys
import json
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not installed. Run: pip install PyMuPDF")
    sys.exit(1)

def extract_words(pdf_path):
    """Extract all words from PDF with their positions"""
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return None
    
    doc = fitz.open(pdf_path)
    
    result = {
        "file": os.path.basename(pdf_path),
        "total_pages": len(doc),
        "pages": {}
    }
    
    total_words = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get words with positions: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        words = page.get_text("words")
        
        page_words = []
        for word_data in words:
            x0, y0, x1, y1, word, block_no, line_no, word_no = word_data
            page_words.append({
                "word": word,
                "position": {
                    "x0": round(x0, 2),
                    "y0": round(y0, 2),
                    "x1": round(x1, 2),
                    "y1": round(y1, 2)
                },
                "block": block_no,
                "line": line_no,
                "word_index": word_no
            })
        
        result["pages"][f"page_{page_num + 1}"] = {
            "word_count": len(page_words),
            "words": page_words
        }
        total_words += len(page_words)
    
    result["total_words"] = total_words
    doc.close()
    
    return result

def extract_words_simple(pdf_path):
    """Extract words as a simple list per page"""
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return None
    
    doc = fitz.open(pdf_path)
    
    result = {
        "file": os.path.basename(pdf_path),
        "total_pages": len(doc),
        "pages": {}
    }
    
    total_words = 0
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get words
        words = page.get_text("words")
        word_list = [w[4] for w in words]  # Extract just the word text
        
        result["pages"][f"page_{page_num + 1}"] = word_list
        total_words += len(word_list)
    
    result["total_words"] = total_words
    doc.close()
    
    return result

def extract_words_by_line(pdf_path):
    """Extract words organized by lines"""
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return None
    
    doc = fitz.open(pdf_path)
    
    result = {
        "file": os.path.basename(pdf_path),
        "total_pages": len(doc),
        "pages": {}
    }
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get text as dictionary with lines
        blocks = page.get_text("dict")["blocks"]
        
        page_lines = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_words = []
                    for span in line["spans"]:
                        # Split span text into words
                        words = span["text"].split()
                        line_words.extend(words)
                    if line_words:
                        page_lines.append(line_words)
        
        result["pages"][f"page_{page_num + 1}"] = {
            "line_count": len(page_lines),
            "lines": page_lines
        }
    
    doc.close()
    return result

def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    input_pdf = "data/Health and wellness guide example.pdf"
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
    
    base_name = os.path.splitext(input_pdf)[0]
    
    print(f"Extracting words from: {input_pdf}")
    print("=" * 50)
    
    # Method 1: Simple word list
    print("\n1. Extracting simple word list...")
    simple_data = extract_words_simple(input_pdf)
    if simple_data:
        output_simple = f"{base_name}_words_simple.json"
        save_to_json(simple_data, output_simple)
        print(f"   Total words: {simple_data['total_words']}")
    
    # Method 2: Words with positions
    print("\n2. Extracting words with positions...")
    detailed_data = extract_words(input_pdf)
    if detailed_data:
        output_detailed = f"{base_name}_words_detailed.json"
        save_to_json(detailed_data, output_detailed)
        print(f"   Total words: {detailed_data['total_words']}")
    
    # Method 3: Words by line
    print("\n3. Extracting words by line...")
    line_data = extract_words_by_line(input_pdf)
    if line_data:
        output_lines = f"{base_name}_words_by_line.json"
        save_to_json(line_data, output_lines)
        total_lines = sum(p['line_count'] for p in line_data['pages'].values())
        print(f"   Total lines: {total_lines}")
    
    print("\n" + "=" * 50)
    print("Extraction complete!")
