import json
import os
import sys

def extract_letters_recursively(data):
    """
    Recursively finds all strings in a JSON structure and 
    extracts letters word-by-word.
    """
    results = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            # If the user wants to extract from keys as well, uncomment below:
            # results.extend(process_string(key))
            results.extend(extract_letters_recursively(value))
    elif isinstance(data, list):
        for item in data:
            results.extend(extract_letters_recursively(item))
    elif isinstance(data, str):
        results.extend(process_string(data))
    
    return results

def process_string(text):
    """Splits a string into words and then into letters."""
    words = text.split()
    word_list = []
    for word in words:
        word_list.append({
            "word": word,
            "letters": list(word)
        })
    return word_list

def main():
    input_file = "data/Health and wellness guide example_comprehensive.json"
    output_file = "data/comprehensive_word_letters.json"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Processing {input_file}...")
        results = extract_letters_recursively(data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"Success! Extracted {len(results)} words.")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
