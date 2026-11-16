import os

base = r"C:\Users\chuan\Documents\知识库\extracted"
files = sorted(os.listdir(base))
for fname in files:
    path = os.path.join(base, fname)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # 打印前30行，看看格式
    print("=== 文件:", fname, "===")
    print("总行数:", len(lines))
    for i, line in enumerate(lines[:30]):
        print(i+1, repr(line[:80]))
    print()
    # 只看前3个文件
    if fname > files[2]:
        break