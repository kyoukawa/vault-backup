import zlib, re, glob, io, os, json
from fontTools.ttLib import TTFont

# 输出目录
OUTPUT_DIR = r"C:\Users\chuan\Documents\知识库\decoded"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_font_objects(pdf_path):
    """从PDF提取所有嵌入字体对象"""
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
            # 检查是否是TrueType字体
            if decompressed[:4] in [b"\x00\x01\x00\x00", b"true", b"typ1", b"OTTO"]:
                fonts[obj_num_str] = decompressed
        except:
            pass
    
    return fonts

def build_cid_to_unicode(font_data):
    """从字体数据构建CID到Unicode的映射"""
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

def decode_pdf_text(pdf_path):
    """解码PDF文本，将CID码替换为Unicode字符"""
    with open(pdf_path, "rb") as f:
        data = f.read()
    
    # 提取字体并构建CID映射
    fonts = extract_font_objects(pdf_path)
    cid_maps = {}
    for obj_num, font_data in fonts.items():
        cmap = build_cid_to_unicode(font_data)
        if cmap:
            cid_maps[obj_num] = cmap
    
    if not cid_maps:
        return None, "无可用字体映射"
    
    # 合并所有CID映射
    merged_cmap = {}
    for obj_num, cmap in cid_maps.items():
        merged_cmap.update(cmap)
    
    print("  合并CID映射: " + str(len(merged_cmap)) + " 个条目")
    
    # 提取文本流并解码
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
    
    all_items = []
    for i in range(min(len(stream_positions), len(endstream_positions))):
        start = stream_positions[i] + 6
        end = endstream_positions[i]
        if end <= start:
            continue
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
            if start_bracket == -1:
                break
            end_pos = text.find(")]", start_bracket + 2)
            if end_pos == -1:
                break
            after = text[end_pos+2:end_pos+5].strip()
            if after.startswith("TJ"):
                content_text = text[start_bracket+2:end_pos]
                # 处理十六进制格式 <XXXX>
                if content_text.startswith("<") and content_text.endswith(">"):
                    hex_str = content_text[1:-1]
                    try:
                        raw_bytes = bytes.fromhex(hex_str)
                        # 尝试UTF-16-BE解码
                        try:
                            chars = raw_bytes.decode("utf-16-be", errors="replace")
                            all_items.append(chars)
                        except:
                            all_items.append(content_text)
                    except:
                        all_items.append(content_text)
                else:
                    all_items.append(content_text)
            pos2 = end_pos + 2
    
    return all_items, merged_cmap

def decode_cid_negative_numbers(text, cid_map):
    """将文本中的负数CID码替换为Unicode字符
    格式如: -1450(x), )83(, 等等
    需要识别模式: 负数数字后跟括号或单独出现
    """
    import re as re_module
    
    result = []
    i = 0
    while i < len(text):
        # 检查是否是负数CID码模式
        if text[i] == "-" and i + 1 < len(text) and text[i+1].isdigit():
            # 读取完整的负数
            j = i + 1
            while j < len(text) and text[j].isdigit():
                j += 1
            cid_str = text[i:j]
            cid_val = int(cid_str)
            abs_cid = abs(cid_val)
            
            if abs_cid in cid_map:
                ch = chr(cid_map[abs_cid])
                result.append(ch)
            else:
                result.append(cid_str)
            i = j
        else:
            result.append(text[i])
            i += 1
    
    return "".join(result)

# 主处理函数
pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
print("找到PDF数:", len(pdfs))

for idx, pdf_path in enumerate(pdfs):
    print("\n[" + str(idx+1) + "/" + str(len(pdfs)) + "] 处理: " + pdf_path)
    items, cid_map = decode_pdf_text(pdf_path)
    if items is None:
        print("  跳过: " + str(cid_map))
        continue
    
    # 组合文本
    raw_text = "\n".join(items)
    
    # 解码负数CID码
    decoded_text = decode_cid_negative_numbers(raw_text, cid_map)
    
    # 保存
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(OUTPUT_DIR, base_name + ".txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(decoded_text)
    
    print("  已保存: " + output_path + " (" + str(len(decoded_text)) + " 字符)")

print("\n全部完成! 输出目录: " + OUTPUT_DIR)
