import glob, os

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
print("找到PDF数:", len(pdfs))
for i, p in enumerate(pdfs[:10]):
    print(i, repr(p))
print("...")
for i, p in enumerate(pdfs[-5:]):
    print(len(pdfs)-5+i, repr(p))
