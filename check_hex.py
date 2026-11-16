import os

base = r"C:\Users\chuan\Documents\知识库\extracted"
files = sorted(os.listdir(base))
print("文件列表:", files[:5])
fname = os.path.join(base, files[0])
with open(fname, "r", encoding="utf-8") as f:
    lines = f.readlines()
print("文件:", fname)
print("总行数:", len(lines))
hex_vals = []
for line in lines[:300]:
    line = line.strip()
    if line.startswith("<") and line.endswith(">"):
        hex_vals.append(line[1:-1])
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