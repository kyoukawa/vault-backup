import zlib, re, sys

pdf_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\chuan\Documents\知识库\试卷库\2024\一模\数学\2024北京东城高三一模数学.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

stream_positions = []
endstream_positions = []
pos = 0
while True:
    idx = data.find(b"stream", pos)
    if idx == -1:
        break
    stream_positions.append(idx)
    pos = idx + 1

pos = 0
while True:
    idx = data.find(b"endstream", pos)
    if idx == -1:
        break
    endstream_positions.append(idx)
    pos = idx + 1

# 收集包含文本操作符的stream
text_streams = []
valid = 0
for i in range(min(len(stream_positions), len(endstream_positions))):
    start = stream_positions[i] + 6
    end = endstream_positions[i]
    if end > start:
        stream_data = data[start:end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            text = decompressed.decode("latin-1", errors="replace")
            if "Tj" in text or "TJ" in text or "BT" in text or "ET" in text:
                text_streams.append((i, text))
            valid += 1
        except Exception as e:
            pass

print("总stream数:", min(len(stream_positions), len(endstream_positions)))
print("包含文本操作符的stream数:", len(text_streams))
print("可解压stream数:", valid)

# 打印前3个包含文本的stream的开头
for idx, text in text_streams[:3]:
    print("\n=== Stream " + str(idx) + " (长度: " + str(len(text)) + ") ===")
    print(text[:1000])

# 尝试提取 Tj 文本
all_tj = []
for idx, text in text_streams:
    tj_matches = re.findall(r'\(([^)]*)\)\s+Tj', text)
    all_tj.extend(tj_matches)

print("\n=== 所有 Tj 文本 ===")
print("Tj 数量:", len(all_tj))
for t in all_tj[:50]:
    print(repr(t))