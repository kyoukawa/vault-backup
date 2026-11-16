import os

decoded_dir = r"C:\Users\chuan\Documents\知识库\decoded"
files = [f for f in os.listdir(decoded_dir) if f.endswith(".txt")]

keywords = ["解析几何", "圆锥曲线", "抛物线", "椭圆", "双曲线", "直线", "圆", "方程", "焦点", "渐近线"]
keyword_results = {kw: [] for kw in keywords}

for f in files:
    path = os.path.join(decoded_dir, f)
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    for kw in keywords:
        if kw in content:
            keyword_results[kw].append(f)

print("=== 关键词统计 ===")
for kw in keywords:
    count = len(keyword_results[kw])
    print(kw + ": " + str(count) + " 个文件")
    if count > 0:
        print("  示例: " + ", ".join(keyword_results[kw][:3]))

print("\n=== 文件列表 (前10个) ===")
for f in files[:10]:
    print(f)
