from fontTools.ttLib import TTFont
import zlib, os, glob, io

def extract_all_streams(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    streams = []
    pos = 0
    while True:
        idx = data.find(b"stream", pos)
        if idx == -1:
            break
        end_idx = data.find(b"endstream", idx)
        if end_idx == -1:
            break
        stream_data = data[idx + 6:end_idx].strip()
        dict_start = max(0, idx - 5000)
        dict_data = data[dict_start:idx]
        streams.append((idx, stream_data, dict_data))
        pos = end_idx + 1
    return streams

def try_fonts(pdf_path):
    streams = extract_all_streams(pdf_path)
    print("总流数:", len(streams))
    font_count = 0
    for idx, stream_data, dict_data in streams:
        is_font = (b"/FontFile2" in dict_data or b"/FontFile3" in dict_data or
                   b"/BaseFont" in dict_data or b"/CIDToGIDMap" in dict_data or
                   b"/ToUnicode" in dict_data or b"/CIDFont" in dict_data)
        if not is_font:
            continue
        try:
            decompressed = zlib.decompress(stream_data)
        except:
            continue
        try:
            font = TTFont(io.BytesIO(decompressed))
            tables = list(font.keys())
            font_count += 1
            print("  字体流@%d: %d 字节, 表: %s..." % (idx, len(decompressed), tables[:8]))
            if "cmap" in font:
                cmap = font["cmap"]
                for table in cmap.tables:
                    if hasattr(table, "cmap") and table.cmap:
                        print("    cmap: platform=%d, enc=%d, format=%d, 条目数=%d" % (
                            table.platformID, table.platEncID, table.format, len(table.cmap)))
                        items = sorted(table.cmap.items())
                        cjk = [(cid, name) for cid, name in items if 0x4E00 <= cid <= 0x9FFF]
                        if cjk:
                            print("    CJK示例: %s" % cjk[:5])
            font.close()
        except Exception as e:
            pass
    print("有效字体数:", font_count)

pdfs = glob.glob(r"C:\Users\chuan\Documents\知识库\试卷库\**\数学\*.pdf", recursive=True)
if pdfs:
    print("测试PDF:", pdfs[0])
    try_fonts(pdfs[0])
