import os

base = r"C:\Users\chuan\Documents\知识库\extracted"
files = sorted(os.listdir(base))
print("共", len(files), "个文件")
# 找几个有内容的文件查看
for fname in files[:5]:
    path = os.path.join(base, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print("\n=== 文件:", fname, "===")
    print("长度:", len(content))
    print("前500字符:")
    print(content[:500])
