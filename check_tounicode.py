import zlib, re

pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\海淀\2024北京海淀高三一模数学.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

to_unicode_refs = re.findall(rb"/ToUnicode\s+(\d+)\s+0\s+R", data)
print("ToUnicode引用:", to_unicode_refs[:20], "... 总数:", len(to_unicode_refs))

cid_to_gid_refs = re.findall(rb"/CIDToGIDMap\s+(\d+)\s+0\s+R", data)
print("CIDToGIDMap引用:", cid_to_gid_refs[:20], "... 总数:", len(cid_to_gid_refs))

cmap_refs = re.findall(rb"/CMap\s+(\d+)\s+0\s+R", data)
print("CMap引用:", cmap_refs[:20], "... 总数:", len(cmap_refs))

for obj_num in to_unicode_refs[:5]:
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
        print("\n对象 " + obj_num_str + " 内容 (前500字符):")
        print(text[:500])
    except:
        pass
