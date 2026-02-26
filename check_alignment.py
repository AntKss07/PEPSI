import fitz
import sys

def check_alignment(source, target):
    s_doc = fitz.open(source)
    t_doc = fitz.open(target)
    
    # Check Page 1
    s_page = s_doc[0]
    t_page = t_doc[0]
    
    keywords = ["Name", "Date of birth", "Identification"]
    
    print(f"Checking alignment between:\n  Source: {source}\n  Target: {target}\n")
    
    offsets_x = []
    offsets_y = []
    
    for word in keywords:
        s_rects = s_page.search_for(word)
        t_rects = t_page.search_for(word)
        
        if s_rects and t_rects:
            # Assume first match corresponds
            s_r = s_rects[0]
            t_r = t_rects[0]
            
            dx = t_r.x0 - s_r.x0
            dy = t_r.y0 - s_r.y0
            
            print(f"Keyword '{word}':")
            print(f"  Source: {s_r}")
            print(f"  Target: {t_r}")
            print(f"  Offset: dx={dx:.2f}, dy={dy:.2f}")
            
            offsets_x.append(dx)
            offsets_y.append(dy)
    
    if offsets_x:
        avg_dx = sum(offsets_x) / len(offsets_x)
        avg_dy = sum(offsets_y) / len(offsets_y)
        print(f"\nAverage Offset: dx={avg_dx:.2f}, dy={avg_dy:.2f}")
        return avg_dx, avg_dy
    else:
        print("\nCould not find common keywords to align.")
        return 0, 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python check_alignment.py <source> <target>")
    else:
        check_alignment(sys.argv[1], sys.argv[2])
