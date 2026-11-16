import re, os, glob

def find_fonts(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    
    base_fonts = set()
    pos = 0
    while True:
        idx = data.find(b"/BaseFont", pos)
        if idx == -1:
            break
        after = data[idx:idx+100]
        match = re.search(rb"/BaseFont\s*/([^\s/]+)", after)
        if match:
            base_fonts.add(match.group(1).decode("latin-1", errors="replace"))
        pos = idx + 1
    
    font_names = set()
    pos = 0
    while True:
        idx = data.find(b"/FontName", pos)
        if idx == -1:
            break
        after = data[idx:idx+100]
        match = re.search(rb"/FontName\s*/([^\s/]+)", after)
        if match:
            font_names.add(match.group(1).decode("latin-1", errors="replace"))
        pos = idx + 1
    
    print("BaseFont:", sorted(base_fonts))
    print("FontName:", sorted(font_names))
    
    pos = 0
    while True:
        idx = data.find(b"/CIDSystemInfo", pos)
        if idx == -1:
            break
        after = data[idx:idx+500]
        print("\nCIDSystemInfo @%d:" % idx)
        print(after[:300].decode("latin-1", errors="replace"))
        pos = idx + 1
    
    pos = 0
    while True:
        idx = data.find(b"/FontFile", pos)
        if idx == -1:
            break
        after = data[idx:idx+200]
        print("\nFontFile引用 @%d:" % idx)
        print(after[:200].decode("latin-1", errors="replace"))
        pos = idx + 1

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
if pdfs:
    print("测试PDF:", pdfs[0])
    find_fonts(pdfs[0])
