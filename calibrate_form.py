import fitz
import sys

def calibrate_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    params = set()
    
    for page in doc:
        for widget in page.widgets():
            if widget.field_name:
                # Fill the field with its own name so we can identify it visually
                widget.field_value = widget.field_name
                widget.update()
                params.add(widget.field_name)

    doc.save(output_pdf)
    print(f"Created {output_pdf} with {len(params)} labeled fields.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python calibrate_form.py <input_pdf> <output_pdf>")
    else:
        calibrate_pdf(sys.argv[1], sys.argv[2])
