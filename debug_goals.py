import fitz
import re
doc = fitz.open("data/Health and wellness guide example.pdf")
all_text = "\n".join([p.get_text() for p in doc])
blocks = re.split(r'Goal #\d+:', all_text)
print(f"Number of goal blocks: {len(blocks) - 1}")
for i, blk in enumerate(blocks[1:], 1):
    print(f"--- GOAL {i} ---")
    print(blk[:100].strip())
doc.close()
