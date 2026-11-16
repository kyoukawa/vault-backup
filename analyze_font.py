import zlib, re, sys

pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\一模\数学\2024北京东城高三一模数学.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

# 查找 ToUnicode CMap
to_unicode_positions = []
pos = 0
while True:
    idx = data.find(b"/ToUnicode", pos)
    if idx == -1:
        break
    to_unicode_positions.append(idx)
    pos = idx + 1

print("找到 /ToUnicode 数量:", len(to_unicode_positions))

# 查找 CMap 相关内容
cmap_positions = []
pos = 0
while True:
    idx = data.find(b"CMap", pos)
    if idx == -1:
        break
    cmap_positions.append(idx)
    pos = idx + 1

print("找到 CMap 数量:", len(cmap_positions))

# 查找 beginbfchar / beginbfrange (ToUnicode 映射)
bfchar_positions = []
pos = 0
while True:
    idx = data.find(b"beginbfchar", pos)
    if idx == -1:
        break
    bfchar_positions.append(idx)
    pos = idx + 1

print("找到 beginbfchar 数量:", len(bfchar_positions))

bfrange_positions = []
pos = 0
while True:
    idx = data.find(b"beginbfrange", pos)
    if idx == -1:
        break
    bfrange_positions.append(idx)
    pos = idx + 1

print("找到 beginbfrange 数量:", len(bfrange_positions))

# 如果有 ToUnicode，尝试提取并解析
if bfchar_positions or bfrange_positions:
    # 提取第一个 ToUnicode 块的内容
    start = min([p for p in bfchar_positions + bfrange_positions if p > 0])
    # 向前找到 stream
    stream_start = data.rfind(b"stream", 0, start)
    if stream_start != -1:
        stream_end = data.find(b"endstream", start)
        if stream_end != -1:
            stream_data = data[stream_start + 6:stream_end].strip()
            try:
                decompressed = zlib.decompress(stream_data)
                text = decompressed.decode("latin-1", errors="replace")
                print("\n=== ToUnicode CMap 内容 (前2000字符) ===")
                print(text[:2000])
            except Exception as e:
                print("解压失败:", e)

# 查找字体字典
font_positions = []
pos = 0
while True:
    idx = data.find(b"/Font", pos)
    if idx == -1:
        break
    font_positions.append(idx)
    pos = idx + 1

print("\n找到 /Font 数量:", len(font_positions))

# 查找 /CIDToGIDMap
cid_positions = []
pos = 0
while True:
    idx = data.find(b"/CIDToGIDMap", pos)
    if idx == -1:
        break
    cid_positions.append(idx)
    pos = idx + 1

print("找到 /CIDToGIDMap 数量:", len(cid_positions))

# 查找 /Differences
diff_positions = []
pos = 0
while True:
    idx = data.find(b"/Differences", pos)
    if idx == -1:
        break
    diff_positions.append(idx)
    pos = idx + 1

print("找到 /Differences 数量:", len(diff_positions))