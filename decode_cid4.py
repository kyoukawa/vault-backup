import zlib, re, glob, io
from fontTools.ttLib import TTFont

def extract_font_by_obj_num(pdf_path, obj_nums):
    with open(pdf_path, "rb") as f:
        data = f.read()
    fonts = {}
    for obj_num in obj_nums:
        pattern = str(obj_num).encode("latin-1") + b" 0 obj"
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
            fonts[obj_num] = zlib.decompress(stream_data)
        except:
            pass
    return fonts

def build_glyph_to_unicode(font_data):
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
        glyph_id_to_unicode = {}
        for unicode_val, glyph_name in unicode_to_glyph.items():
            if glyph_name in glyph_to_id:
                glyph_id_to_unicode[glyph_to_id[glyph_name]] = unicode_val
        font.close()
        return glyph_id_to_unicode
    except:
        return None

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
pdf_path = pdfs[0]
fonts = extract_font_by_obj_num(pdf_path, [2536])
glyph_map = None
for obj_num, font_data in fonts.items():
    glyph_map = build_glyph_to_unicode(font_data)
    break

if glyph_map:
    print("SimSun映射数:", len(glyph_map))
    # 测试提取文件中出现的CID值
    test_cids = [1450, 348, 2230, 1228, 1357, 2057, 2077, 1351, 1521, 1396, 1980, 1581, 761, 1474, 918, 45, 1519, 539, 747, 852, 2395, 37, 881, 1628, 131, 865, 748, 2568, 73, 858, 2380, 149, 869, 751, 3388, 75]
    for cid in test_cids:
        if cid in glyph_map:
            ch = chr(glyph_map[cid])
            print("CID " + str(cid) + " -> U+%04X %s" % (glyph_map[cid], ch))
        else:
            print("CID " + str(cid) + " -> 未找到")
