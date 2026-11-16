import zlib, re, os, glob

def extract_font_streams(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    
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
    
    font_streams = []
    for i in range(min(len(stream_positions), len(endstream_positions))):
        start = stream_positions[i] + 6
        end = endstream_positions[i]
        if end > start:
            dict_start = max(0, stream_positions[i] - 3000)
            dict_data = data[dict_start:stream_positions[i]]
            if b"BaseFont" in dict_data or b"FontFile" in dict_data or b"/CIDFont" in dict_data or b"/FontFile2" in dict_data:
                stream_data = data[start:end].strip()
                try:
                    decompressed = zlib.decompress(stream_data)
                    font_streams.append((i, decompressed))
                except:
                    pass
    
    return font_streams

pdfs = glob.glob(r"C:UserschuanDocuments知识库试卷库**数学*.pdf", recursive=True)
if pdfs:
    pdf_path = pdfs[0]
    print("测试PDF:", pdf_path)
    fonts = extract_font_streams(pdf_path)
    print("找到字体流:", len(fonts))
    os.makedirs(r"C:UserschuanDocuments知识库onts", exist_ok=True)
    for i, (idx, font_data) in enumerate(fonts[:10]):
        print(f"  字体{i}: {len(font_data)} 字节, 签名: {font_data[:4]}")
        out_path = r"C:UserschuanDocuments知识库ontsont_%d_%d.bin" % (idx, i)
        with open(out_path, "wb") as f:
            f.write(font_data)
