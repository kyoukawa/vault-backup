import zlib, re, io
from fontTools.ttLib import TTFont

def extract_font_by_obj_num(pdf_path, obj_nums):
    with open(pdf_path, "rb") as f:
        data = f.read()
    fonts = {}
    for obj_num in obj_nums:
        pattern = str(obj_num).encode("latin-1") + b" 0 obj"
        idx = data.find(pattern)
        if idx == -1:
            print("对象" + str(obj_num) + "未找到")
            continue
        stream_start = data.find(b"stream", idx)
        if stream_start == -1:
            print("对象" + str(obj_num) + "无stream")
            continue
        stream_end = data.find(b"endstream", stream_start)
        if stream_end == -1:
            print("对象" + str(obj_num) + "无endstream")
            continue
        stream_data = data[stream_start + 6:stream_end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            fonts[obj_num] = decompressed
            print("对象" + str(obj_num) + ": " + str(len(decompressed)) + " 字节, 签名: " + str(decompressed[:4]))
        except Exception as e:
            print("对象" + str(obj_num) + ": 解压失败 - " + str(e))
    return fonts

def build_glyph_to_unicode(font_data):
    try:
        font = TTFont(io.BytesIO(font_data))
        if "cmap" not in font:
            font.close()
            return None, None
        cmap = font["cmap"]
        unicode_to_glyph = {}
        for table in cmap.tables:
            if hasattr(table, "cmap") and table.cmap:
                if table.platformID == 3 and table.platEncID == 1:
                    unicode_to_glyph = dict(table.cmap)
                    break
        glyph_order = font.getGlyphOrder()
        glyph_to_id = {name: i for i, name in enumerate(glyph_order)}
        glyph_id_to_unicode = {}
        for unicode_val, glyph_name in unicode_to_glyph.items():
            if glyph_name in glyph_to_id:
                glyph_id_to_unicode[glyph_to_id[glyph_name]] = unicode_val
        font.close()
        return glyph_id_to_unicode, len(glyph_order)
    except Exception as e:
        print("  构建映射失败:", e)
        return None, None

pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\初一\数学\2024初一数学期末考试卷.pdf"
fonts = extract_font_by_obj_num(pdf_path, [2536, 2532, 2540, 2556])

for obj_num, font_data in fonts.items():
    glyph_map, total_glyphs = build_glyph_to_unicode(font_data)
    if glyph_map:
        print("对象" + str(obj_num) + ": 总glyph数=" + str(total_glyphs) + ", 映射数=" + str(len(glyph_map)))
        test_cids = [1450, 348, 2230, 1228, 1357, 64086]
        for cid in test_cids:
            if cid in glyph_map:
                ch = chr(glyph_map[cid])
                print("  CID " + str(cid) + " -> U+%04X (%s)" % (glyph_map[cid], ch))
            else:
                print("  CID " + str(cid) + " -> 未找到")
