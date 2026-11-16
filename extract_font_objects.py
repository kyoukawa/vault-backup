import zlib, re, os, glob, io
from fontTools.ttLib import TTFont

def extract_font_objects(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    font_file_refs = re.findall(rb"/FontFile2\s+(\d+)\s+0\s+R", data)
    print("找到FontFile2引用:", font_file_refs)
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
            fonts[obj_num_str] = decompressed
            print("  对象" + obj_num_str + ": " + str(len(decompressed)) + " 字节, 签名: " + str(decompressed[:4]))
        except Exception as e:
            print("  对象" + obj_num_str + ": 解压失败 - " + str(e))
    return fonts

def parse_font_cmap(font_data):
    try:
        font = TTFont(io.BytesIO(font_data))
        if "cmap" not in font:
            font.close()
            return None
        cmap = font["cmap"]
        result = {}
        for table in cmap.tables:
            if hasattr(table, "cmap") and table.cmap:
                if table.platformID == 3 and table.platEncID == 1:
                    result = dict(table.cmap)
                    break
                elif table.platformID == 0 and table.platEncID == 3:
                    if not result:
                        result = dict(table.cmap)
        font.close()
        return result
    except Exception as e:
        print("  解析cmap失败:", e)
        return None

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
if pdfs:
    print("测试PDF:", pdfs[0])
    fonts = extract_font_objects(pdfs[0])
    print("\n解析字体cmap:")
    for obj_num, font_data in fonts.items():
        cmap = parse_font_cmap(font_data)
        if cmap:
            cjk = [(cid, name) for cid, name in sorted(cmap.items()) if 0x4E00 <= cid <= 0x9FFF]
            print("  对象" + obj_num + ": " + str(len(cmap)) + " 个映射, CJK字符: " + str(len(cjk)))
            if cjk:
                print("    示例: " + str(cjk[:5]))
        else:
            print("  对象" + obj_num + ": 无cmap")
