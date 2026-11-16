import os, glob

files = glob.glob(r"C:\Users\chuan\Documents\知识库\extracted\*.txt")
print("找到文件数:", len(files))
for f in files[:3]:
    print("\n=== 文件:", f, "===")
    with open(f, "r", encoding="utf-8", errors="replace") as fh:
        content_text = fh.read()
    print("长度:", len(content_text))
    print("前500字符:")
    print(content_text[:500])
