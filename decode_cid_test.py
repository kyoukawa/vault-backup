import zlib, re, os, glob, io
from fontTools.ttLib import TTFont

def extract_font_by_name(pdf_path, font_name_prefix):
    """按名称提取字体"""
    with open(pdf_path, "rb") as f:
        data = f.read()
    
    # 查找FontFile2引用及其对应的BaseFont
    font_file_refs = re.findall(rb"/FontFile2\s+(\d+)\s+0\s+R", data)
    fonts = {}
    
    for obj_num in font_file_refs:
        obj_num_str = obj_num.decode("latin-1")
        pattern = obj_num + b" 0 obj"
        idx = data.find(pattern)
        if idx == -1:
            continue
        # 查找这个对象所属的字体名称
        # 查找最近的BaseFont
        search_start = max(0, idx - 5000)
        before_data = data[search_start:idx]
        base_font_matches = re.findall(rb"/BaseFont\s*/([^\s/]+)", before_data)
        if base_font_matches:
            bf = base_font_matches[-1].decode("latin-1", errors="replace")
            if font_name_prefix in bf:
                stream_start = data.find(b"stream", idx)
                stream_end = data.find(b"endstream", stream_start)
                if stream_start != -1 and stream_end != -1:
                    stream_data = data[stream_start + 6:stream_end].strip()
                    try:
                        decompressed = zlib.decompress(stream_data)
                        fonts[obj_num_str] = decompressed
                        print("找到字体对象" + obj_num_str + " (" + bf + "): " + str(len(decompressed)) + " 字节")
                    except:
                        pass
    
    return fonts

def build_glyph_to_unicode(font_data):
    """构建glyph ID -> Unicode的反向映射"""
    try:
        font = TTFont(io.BytesIO(font_data))
        if "cmap" not in font:
            font.close()
            return None, None
        
        cmap = font["cmap"]
        # 收集所有Unicode -> glyph_name 映射
        unicode_to_glyph = {}
        for table in cmap.tables:
            if hasattr(table, "cmap") and table.cmap:
                if table.platformID == 3 and table.platEncID == 1:
                    unicode_to_glyph = dict(table.cmap)
                    break
        
        # 构建glyph_name -> glyph_id
        glyph_order = font.getGlyphOrder()
        glyph_to_id = {name: i for i, name in enumerate(glyph_order)}
        
        # 构建glyph_id -> unicode
        glyph_id_to_unicode = {}
        for unicode_val, glyph_name in unicode_to_glyph.items():
            if glyph_name in glyph_to_id:
                glyph_id_to_unicode[glyph_to_id[glyph_name]] = unicode_val
        
        font.close()
        return glyph_id_to_unicode, len(glyph_order)
    except Exception as e:
        print("  构建映射失败:", e)
        return None, None

# 测试
pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
if pdfs:
    print("测试PDF:", pdfs[0])
    
    # 提取SimSun字体
    simsun_fonts = extract_font_by_name(pdfs[0], "SimSun")
    print("\nSimSun字体数:", len(simsun_fonts))
    
    for obj_num, font_data in simsun_fonts.items():
        glyph_map, total_glyphs = build_glyph_to_unicode(font_data)
        if glyph_map:
            print("  对象" + obj_num + ": 总glyph数=" + str(total_glyphs) + ", 映射数=" + str(len(glyph_map)))
            # 测试几个CID值
            test_cids = [1450, 348, 2230, 64086, 65188, 63306]
            for cid in test_cids:
                if cid in glyph_map:
                    ch = chr(glyph_map[cid])
                    print("    CID " + str(cid) + " -> U+%04X (%s)" % (glyph_map[cid], ch))
                else:
                    print("    CID " + str(cid) + " -> 未找到")
