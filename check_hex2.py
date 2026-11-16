import os

base = r"C:\Users\chuan\Documents\知识库\extracted"
files = sorted(os.listdir(base))
# 找一个有十六进制值的文件
for fname in files:
    path = os.path.join(base, fname)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("<") and line.endswith(">") and len(line) > 2:
                print("找到文件:", fname)
                hex_vals = []
                with open(path, "r", encoding="utf-8") as f2:
                    for l2 in f2:
                        l2 = l2.strip()
                        if l2.startswith("<") and l2.endswith(">") and len(l2) > 2:
                            hex_vals.append(l2[1:-1])
                print("总行数:", sum(1 for _ in open(path, encoding="utf-8")))
                print("前20个十六进制值:")
                for h in hex_vals[:20]:
                    try:
                        decoded = bytes.fromhex(h).decode("utf-16-be", errors="replace")
                        print(" ", h, "->", repr(decoded))
                    except Exception as e:
                        print(" ", h, "-> (decode fail)", e)
                print()
                print("唯一十六进制值数量:", len(set(hex_vals)))
                for h in hex_vals[:15]:
                    try:
                        val = int(h, 16)
                        print(h, "=", val, "(0x%04X)" % val)
                    except:
                        pass
                raise SystemExit(0)
print("没有找到包含十六进制值的文件")