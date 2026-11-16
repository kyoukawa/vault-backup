import zlib, re, glob, io

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
pdf_path = pdfs[0] if pdfs else None
print("PDF:", pdf_path)

with open(pdf_path, "rb") as f:
    data = f.read()

tu_refs = re.findall(rb"/ToUnicode\s+(\d+)\s+0\s+R", data)
print("ToUnicode引用数:", len(tu_refs))

# 提取所有ToUnicode CMap内容并合并映射
all_mappings = {}

for obj_num in tu_refs:
    obj_num_str = obj_num.decode("latin-1")
    pattern = obj_num + b" 0 obj"
    idx = data.find(pattern)
    if idx == -1:
        continue
    stream_start = data.find(b"stream", idx)
    stream_end = data.find(b"endstream", stream_start)
    if stream_start == -1 or stream_end == -1:
        continue
    stream_data = data[stream_start + 6:stream_end].strip()
    try:
        decompressed = zlib.decompress(stream_data)
        text = decompressed.decode("latin-1", errors="replace")
        # 解析beginbfchar
        for m in re.finditer(r"beginbfchar(.*?)endbfchar", text, re.DOTALL):
            block = m.group(1)
            for pair in re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", block):
                cid = int(pair[0], 16)
                unicode_val = int(pair[1], 16)
                all_mappings[cid] = chr(unicode_val)
        # 解析beginbfrange
        for m in re.finditer(r"beginbfrange(.*?)endbfrange", text, re.DOTALL):
            block = m.group(1)
            for rng in re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>", block):
                start = int(rng[0], 16)
                end = int(rng[1], 16)
                base = int(rng[2], 16)
                for i in range(start, end + 1):
                    all_mappings[i] = chr(base + (i - start))
            # 也可能是两列格式: <start> <end> <char>  (没有第三个参数时不同)
            for rng2 in re.findall(r"<([0-9A-Fa-f]+)>\s+<([0-9A-Fa-f]+)>\s*\[([0-9A-Fa-f\s]+)\]", block):
                start = int(rng2[0], 16)
                end = int(rng2[1], 16)
                chars = rng2[2].split()
                for j, ch in enumerate(chars):
                    if start + j <= end:
                        all_mappings[start + j] = chr(int(ch, 16))
    except Exception as e:
        pass

print("总映射数:", len(all_mappings))
print("前30个映射:", sorted(all_mappings.items())[:30])
# 检查中文映射
cn_mappings = {k: v for k, v in all_mappings.items() if ord(v) > 127}
print("中文字符映射数:", len(cn_mappings))
if cn_mappings:
    items = sorted(cn_mappings.items())[:20]
    print("前20个中文映射:", items)
