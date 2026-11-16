import zlib, re, os, glob

def find_cmaps(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    
    # 查找ToUnicode CMap
    to_unicode_positions = []
    pos = 0
    while True:
        idx = data.find(b"/ToUnicode", pos)
        if idx == -1:
            break
        to_unicode_positions.append(idx)
        pos = idx + 1
    
    # 查找CIDToGIDMap
    cid_to_gid_positions = []
    pos = 0
    while True:
        idx = data.find(b"/CIDToGIDMap", pos)
        if idx == -1:
            break
        cid_to_gid_positions.append(idx)
        pos = idx + 1
    
    # 查找CMap对象
    cmap_positions = []
    pos = 0
    while True:
        idx = data.find(b"/CMap", pos)
        if idx == -1:
            break
        cmap_positions.append(idx)
        pos = idx + 1
    
    print("ToUnicode位置:", len(to_unicode_positions))
    print("CIDToGIDMap位置:", len(cid_to_gid_positions))
    print("CMap位置:", len(cmap_positions))
    
    # 尝试解析ToUnicode流
    for idx in to_unicode_positions[:5]:
        # 找到对应的stream
        stream_start = data.find(b"stream", idx)
        if stream_start == -1:
            continue
        stream_end = data.find(b"endstream", stream_start)
        if stream_end == -1:
            continue
        stream_data = data[stream_start + 6:stream_end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            text = decompressed.decode("latin-1", errors="replace")
            print("\n=== ToUnicode @%d ===" % idx)
            print(text[:2000])
        except Exception as e:
            print("ToUnicode @%d 解压失败: %s" % (idx, e))
    
    # 尝试解析CIDToGIDMap
    for idx in cid_to_gid_positions[:5]:
        stream_start = data.find(b"stream", idx)
        if stream_start == -1:
            continue
        stream_end = data.find(b"endstream", stream_start)
        if stream_end == -1:
            continue
        stream_data = data[stream_start + 6:stream_end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            text = decompressed.decode("latin-1", errors="replace")
            print("\n=== CIDToGIDMap @%d ===" % idx)
            print(text[:2000])
        except Exception as e:
            print("CIDToGIDMap @%d 解压失败: %s" % (idx, e))

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
if pdfs:
    print("测试PDF:", pdfs[0])
    find_cmaps(pdfs[0])
