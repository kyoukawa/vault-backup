from fontTools.ttLib import TTFont
import io, zlib, re

pdf_path = r"C:\Users\chuan\Documents\知识库\试卷库\2024\海淀\2024北京海淀高三一模数学.pdf"

with open(pdf_path, "rb") as f:
    data = f.read()

font_file_refs = re.findall(rb"/FontFile2\s+(\d+)\s+0\s+R", data)
print("字体对象:", font_file_refs[:5], "...
")

for obj_num in font_file_refs[:3]:
    obj_num_str = obj_num.decode("latin-1")
    pattern = obj_num + b" 0 obj"
    idx = data.find(pattern)
    if idx == -1: continue
    stream_start = data.find(b"stream", idx)
    stream_end = data.find(b"endstream", stream_start)
    stream_data = data[stream_start + 6:stream_end].strip()
    try:
        decompressed = zlib.decompress(stream_data)
        print("对象 " + obj_num_str + "，前4字节: " + str(decompressed[:4]))
        
        # 尝试打开字体
        try:
            font = TTFont(io.BytesIO(decompressed))
            print("  表: " + str(list(font.keys())))
            
            # 检查CIDToGIDMap
            if hasattr(font, "getGlyphOrder"):
                glyph_order = font.getGlyphOrder()
                print("  glyph数量: " + str(len(glyph_order)))
                print("  前20个glyph: " + str(glyph_order[:20]))
            
            # 检查cmap
            if "cmap" in font:
                cmap = font["cmap"]
                for table in cmap.tables:
                    if hasattr(table, "platformID"):
                        print("  cmap table: platformID=" + str(table.platformID) + ", platEncID=" + str(table.platEncID) + ", format=" + str(getattr(table, "format", "?")))
            
            font.close()
        except Exception as e:
            print("  无法打开字体: " + str(e))
    except Exception as e:
        print("对象 " + obj_num_str + " 错误: " + str(e))
