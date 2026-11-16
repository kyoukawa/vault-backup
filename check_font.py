import zlib, re, glob, io
from fontTools.ttLib import TTFont
pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
print("找到PDF数:", len(pdfs))
if pdfs:
    print("第一个:", pdfs[0][-50:])

pdf_path = pdfs[0] if pdfs else None
if pdf_path:
    with open(pdf_path, "rb") as f:
        data = f.read()
    font_file_refs = re.findall(rb"/FontFile2\s+(\d+)\s+0\s+R", data)
    print("字体引用总数:", len(font_file_refs))
    for obj_num in font_file_refs[:2]:
        obj_num_str = obj_num.decode("latin-1")
        pattern = obj_num + b" 0 obj"
        idx = data.find(pattern)
        if idx == -1: continue
        stream_start = data.find(b"stream", idx)
        stream_end = data.find(b"endstream", stream_start)
        if stream_start == -1 or stream_end == -1: continue
        stream_data = data[stream_start + 6:stream_end].strip()
        try:
            decompressed = zlib.decompress(stream_data)
            print("\n对象 " + obj_num_str + " 大小:" + str(len(decompressed)))
            font = TTFont(io.BytesIO(decompressed))
            print("  表:" + str(list(font.keys())))
            glyph_order = font.getGlyphOrder()
            print("  glyph数量:" + str(len(glyph_order)))
            print("  前20个glyph:" + str(glyph_order[:20]))
            if "cmap" in font:
                cmap = font["cmap"]
                for table in cmap.tables:
                    if hasattr(table, "platformID"):
                        print("  cmap plat=" + str(table.platformID) + " enc=" + str(table.platEncID) + " fmt=" + str(getattr(table, "format", "?")))
                        if hasattr(table, "cmap") and table.cmap:
                            items = list(table.cmap.items())[:5]
                            print("  示例映射:" + str(items))
            font.close()
        except Exception as e:
            print("对象 " + obj_num_str + " 错误:" + str(e))
