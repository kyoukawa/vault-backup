import zlib, re, struct, os

pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\一模\数学\2024北京东城高三一模数学.pdf"
out_dir = r"C:\Users\chuan\Documents\知识库\fonts"
os.makedirs(out_dir, exist_ok=True)

with open(pdf_path, "rb") as f:
    data = f.read()

pos = 0
font_files = []
while True:
    idx = data.find(b"/FontFile2", pos)
    if idx == -1: break
    stream_start = data.find(b"stream", idx)
    if stream_start == -1:
        pos = idx + 1
        continue
    stream_end = data.find(b"endstream", stream_start)
    if stream_end == -1:
        pos = stream_start + 1
        continue
    stream_data = data[stream_start + 6:stream_end].strip()
    try:
        decompressed = zlib.decompress(stream_data)
        font_files.append(decompressed)
        print("提取字体文件:", len(decompressed), "字节")
    except Exception as e:
        print("解压失败:", e)
    pos = stream_end + 1

print("共提取", len(font_files), "个字体文件")

for i, font_data in enumerate(font_files):
    if font_data[:4] in (b"\x00\x01\x00\x00", b"ttcf") or font_data[:4] == b"OTTO":
        ext = ".ttf"
    else:
        ext = ".bin"
    path = os.path.join(out_dir, "font_" + str(i) + ext)
    with open(path, "wb") as f:
        f.write(font_data)
    print("保存:", path)

if font_files:
    fd = font_files[0]
    if fd[:4] == b"\x00\x01\x00\x00":
        num_tables = struct.unpack(">H", fd[4:6])[0]
        print("字体表数量:", num_tables)
        tables = {}
        offset = 12
        for i in range(num_tables):
            tag = fd[offset:offset+4].decode("latin-1")
            checksum = struct.unpack(">I", fd[offset+4:offset+8])[0]
            offset_val = struct.unpack(">I", fd[offset+8:offset+12])[0]
            length = struct.unpack(">I", fd[offset+12:offset+16])[0]
            tables[tag] = (offset_val, length)
            offset += 16
        print("字体表:", list(tables.keys()))
        if "cmap" in tables:
            cmap_offset, cmap_length = tables["cmap"]
            cmap_data = fd[cmap_offset:cmap_offset+cmap_length]
            cmap_version = struct.unpack(">H", cmap_data[0:2])[0]
            cmap_num_tables = struct.unpack(">H", cmap_data[2:4])[0]
            print("cmap版本:", cmap_version, "子表数量:", cmap_num_tables)
            sub_offset = 8
            for i in range(cmap_num_tables):
                platform_id = struct.unpack(">H", cmap_data[sub_offset:sub_offset+2])[0]
                encoding_id = struct.unpack(">H", cmap_data[sub_offset+2:sub_offset+4])[0]
                sub_offset_val = struct.unpack(">I", cmap_data[sub_offset+4:sub_offset+8])[0]
                print("  cmap子表", i, ": platform=", platform_id, " encoding=", encoding_id, " offset=", sub_offset_val)
                sub_offset += 8