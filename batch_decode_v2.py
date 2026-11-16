import zlib, re, glob, io, os
from fontTools.ttLib import TTFont

OUTPUT_DIR = r"C:\Users\chuan\Documents\知识库\decoded_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_font_objects(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    font_file_refs = re.findall(rb"/FontFile2\s+(\d+)\s+0\s+R", data)
    fonts = {}
    for obj_num in font_file_refs:
        obj_num_str = obj_num.decode("latin-1")
        pattern = obj_num + b" 0 obj"
        idx = data.find(pattern)
        if idx == -1:
            continue
        stream_start = data.find(b"stream", idx)
        if stream_start == -1:
            continue
        stream_end = data.find(b"endstream", stream_start)
        if stream_end == -1:
            continue
        stream_data = data[stream_start + 6:stream_end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            if decompressed[:4] in [b"\x00\x01\x00\x00", b"true", b"typ1", b"OTTO"]:
                fonts[obj_num_str] = decompressed
        except:
            pass
    return fonts

def build_cid_to_unicode(font_data):
    try:
        font = TTFont(io.BytesIO(font_data))
        if "cmap" not in font:
            font.close()
            return None
        cmap = font["cmap"]
        unicode_to_glyph = {}
        for table in cmap.tables:
            if hasattr(table, "cmap") and table.cmap:
                if table.platformID == 3 and table.platEncID == 1:
                    unicode_to_glyph = dict(table.cmap)
                    break
        glyph_order = font.getGlyphOrder()
        glyph_to_id = {name: i for i, name in enumerate(glyph_order)}
        cid_to_unicode = {}
        for unicode_val, glyph_name in unicode_to_glyph.items():
            if glyph_name in glyph_to_id:
                cid_to_unicode[glyph_to_id[glyph_name]] = unicode_val
        font.close()
        return cid_to_unicode
    except:
        return None

def decode_tj_array(tj_content, merged_cmap):
    """解码TJ数组内容，处理十六进制和负数CID码"""
    result = []
    i = 0
    while i < len(tj_content):
        ch = tj_content[i]
        # 十六进制格式 <XXXX>
        if ch == "<":
            end = tj_content.find(">", i + 1)
            if end == -1:
                result.append(ch)
                i += 1
                continue
            hex_str = tj_content[i+1:end]
            # 每两个十六进制字符 = 一个字节 = CID值的一部分
            try:
                raw_bytes = bytes.fromhex(hex_str)
                # 对于CID字体，每两个字节是一个CID值（大端序）
                for j in range(0, len(raw_bytes), 2):
                    if j + 1 < len(raw_bytes):
                        cid = (raw_bytes[j] << 8) | raw_bytes[j+1]
                        if cid in merged_cmap:
                            result.append(chr(merged_cmap[cid]))
                        else:
                            result.append("<%04X>" % cid)
                    else:
                        result.append("<%02X>" % raw_bytes[j])
            except:
                result.append(tj_content[i:end+1])
            i = end + 1
        # 负数CID码 -XXXX
        elif ch == "-" and i + 1 < len(tj_content) and tj_content[i+1].isdigit():
            j = i + 1
            while j < len(tj_content) and tj_content[j].isdigit():
                j += 1
            abs_cid = int(tj_content[i+1:j])
            if abs_cid in merged_cmap:
                result.append(chr(merged_cmap[abs_cid]))
            else:
                result.append(tj_content[i:j])
            i = j
        else:
            result.append(ch)
            i += 1
    return "".join(result)

def decode_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    
    fonts = extract_font_objects(pdf_path)
    cid_maps = {}
    for obj_num, font_data in fonts.items():
        cmap = build_cid_to_unicode(font_data)
        if cmap:
            cid_maps[obj_num] = cmap
    
    if not cid_maps:
        return None, 0
    
    merged = {}
    for cmap in cid_maps.values():
        merged.update(cmap)
    
    stream_positions = []
    endstream_positions = []
    pos = 0
    while True:
        idx = data.find(b"stream", pos)
        if idx == -1: break
        stream_positions.append(idx)
        pos = idx + 1
    pos = 0
    while True:
        idx = data.find(b"endstream", pos)
        if idx == -1: break
        endstream_positions.append(idx)
        pos = idx + 1
    
    all_items = []
    for i in range(min(len(stream_positions), len(endstream_positions))):
        start = stream_positions[i] + 6
        end = endstream_positions[i]
        if end <= start: continue
        stream_data = data[start:end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            text = decompressed.decode("latin-1", errors="replace")
            if "Tj" not in text and "TJ" not in text and "BT" not in text and "ET" not in text:
                continue
        except:
            continue
        pos2 = 0
        while True:
            start_bracket = text.find("[(", pos2)
            if start_bracket == -1: break
            end_pos = text.find(")]", start_bracket + 2)
            if end_pos == -1: break
            after = text[end_pos+2:end_pos+5].strip()
            if after.startswith("TJ"):
                content_text = text[start_bracket+2:end_pos]
                decoded = decode_tj_array(content_text, merged)
                all_items.append(decoded)
            pos2 = end_pos + 2
    
    return "\n".join(all_items), len(merged)

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
log = []
log.append("找到PDF数: " + str(len(pdfs)))

for idx, pdf_path in enumerate(pdfs):
    try:
        decoded_text, map_count = decode_pdf(pdf_path)
        if decoded_text is None:
            log.append("[" + str(idx+1) + "/" + str(len(pdfs)) + "] 跳过 (无字体映射): " + pdf_path)
            continue
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(OUTPUT_DIR, base_name + ".txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(decoded_text)
        log.append("[" + str(idx+1) + "/" + str(len(pdfs)) + "] OK: " + os.path.basename(pdf_path) + " -> " + str(len(decoded_text)) + " 字符, " + str(map_count) + " 个CID映射")
    except Exception as e:
        log.append("[" + str(idx+1) + "/" + str(len(pdfs)) + "] 错误: " + pdf_path + " -> " + str(e))

log.append("\n全部完成! 输出目录: " + OUTPUT_DIR)

with open(os.path.join(OUTPUT_DIR, "decode_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))

print("全部完成! 查看 decode_log.txt 了解详情")
