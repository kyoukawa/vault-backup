from fontTools.ttLib import TTFont
import os

font_paths = [
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
]

for fp in font_paths:
    if not os.path.exists(fp):
        print("不存在:", fp)
        continue
    print("=== 分析:", fp, "===")
    try:
        font = TTFont(fp)
        print("  字体表:", list(font.keys()))
        if "cmap" in font:
            cmap = font["cmap"]
            for table in cmap.tables:
                print("  cmap子表: platformID={}, platEncID={}, format={}".format(
                    table.platformID, table.platEncID, table.format))
                if table.format == 4:
                    cmap_dict = table.cmap
                    print("  映射条目数:", len(cmap_dict))
                    items = sorted(cmap_dict.items())[:20]
                    for cid, name in items:
                        try:
                            ch = chr(cid)
                        except:
                            ch = "?"
                        print("    U+%04X -> %s (%s)" % (cid, ch, name))
        font.close()
    except Exception as e:
        print("  错误:", e)
    print()
