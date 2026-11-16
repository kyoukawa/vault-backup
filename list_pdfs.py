import os, glob

base = r"C:\Users\chuan\Documents\知识库\试卷库"
pdfs = glob.glob(os.path.join(base, "**", "数学", "*.pdf"), recursive=True)
print("找到", len(pdfs), "个数学PDF")
for p in sorted(pdfs)[:20]:
    print(p)
print("...")
for p in sorted(pdfs)[-5:]:
    print(p)