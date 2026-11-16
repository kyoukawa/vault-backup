import zlib, re

pdf_path = "C:\\Users\\chuan\\Documents\\知识库\\试卷库\\2024\\一模\\数学\\2024北京东城高三一模数学.pdf"
with open(pdf_path, "rb") as f:
    data = f.read()

print("FontFile:", data.count(b"/FontFile"))
for marker in [b"/TrueType", b"/Type1", b"/CIDFont", b"/CIDFontType0", b"/CIDFontType2"]:
    print(marker.decode(), ":", data.count(marker))
print("BaseFont:", data.count(b"/BaseFont"))
print("CIDToGIDMap:", data.count(b"/CIDToGIDMap"))

pos = 0
fonts = []
for i in range(30):
    idx = data.find(b"/BaseFont", pos)
    if idx == -1: break
    after = data[idx:idx+100]
    m = re.search(rb"/BaseFont\s*/([^\s]+)", after)
    if m:
        fonts.append(m.group(1).decode("latin-1", errors="replace"))
    pos = idx + 1
print("前30个BaseFont:")
for f in fonts:
    print(" ", f)