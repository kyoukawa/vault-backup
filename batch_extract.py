import zlib, sys, os

def extract_pdf_text(pdf_path):
    with open(pdf_path, "rb") as f:
        data = f.read()
    stream_positions = []
    endstream_positions = []
    pos = 0
    while True:
        idx = data.find(b"stream", pos)
        if idx == -1: break
        stream_positions.append(idx)
        pos = idx + 1
    pos = 0
    while True:
        idx = data.find(b"endstream", pos)
        if idx == -1: break
        endstream_positions.append(idx)
        pos = idx + 1
    text_streams = []
    for i in range(min(len(stream_positions), len(endstream_positions))):
        start = stream_positions[i] + 6
        end = endstream_positions[i]
        if end > start:
            stream_data = data[start:end].strip()
            try:
                decompressed = zlib.decompress(stream_data)
                text = decompressed.decode("latin-1", errors="replace")
                if "Tj" in text or "TJ" in text or "BT" in text or "ET" in text:
                    text_streams.append(text)
            except Exception:
                pass
    all_text_items = []
    for text in text_streams:
        pos2 = 0
        while True:
            start_bracket = text.find("[(", pos2)
            if start_bracket == -1: break
            end_pos = text.find(")]", start_bracket + 2)
            if end_pos == -1: break
            after = text[end_pos+2:end_pos+5].strip()
            if after.startswith("TJ"):
                content = text[start_bracket+2:end_pos]
                if content.startswith("<") and content.endswith(">"):
                    hex_str = content[1:-1]
                    try:
                        chars = bytes.fromhex(hex_str).decode("utf-16-be", errors="replace")
                        all_text_items.append(chars)
                    except Exception:
                        all_text_items.append(content)
                else:
                    all_text_items.append(content)
            pos2 = end_pos + 2
    return all_text_items

pdfs = [
    "试卷库\\2026\\一模\\数学\\2026北京西城高三一模数学.pdf",
    "试卷库\\2024\\二模\\数学\\2024北京东城高三二模数学.pdf",
    "试卷库\\2024\\二模\\数学\\2024北京丰台高三二模数学.pdf",
    "试卷库\\2024\\二模\\数学\\2024北京昌平高三二模数学.pdf",
    "试卷库\\2024\\二模\\数学\\2024北京朝阳高三二模数学.pdf",
    "试卷库\\2024\\二模\\数学\\2024北京海淀高三二模数学.pdf",
    "试卷库\\2024\\二模\\数学\\2024北京西城高三二模数学.pdf",
    "试卷库\\2025\\二模\\数学\\2025北京东城高三二模数学.pdf",
    "试卷库\\2025\\二模\\数学\\2025北京丰台高三二模数学.pdf",
    "试卷库\\2025\\二模\\数学\\2025北京昌平高三二模数学.pdf",
    "试卷库\\2025\\二模\\数学\\2025北京朝阳高三二模数学.pdf",
    "试卷库\\2025\\二模\\数学\\2025北京海淀高三二模数学.pdf",
    "试卷库\\2025\\二模\\数学\\2025北京西城高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京东城高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京丰台高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京房山高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京昌平高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京朝阳高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京海淀高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京石景山高三二模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京顺义高三二模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京海淀高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京丰台高三一模数学.pdf",
    "试卷库\\2026\\二模\\数学\\2026北京西城高三二模数学.pdf",
    "试卷库\\2025\\真题\\数学\\2025北京高考真题数学.pdf",
    "试卷库\\2026\\真题\\数学\\2026北京高考真题数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京丰台高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京东城高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京延庆高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京朝阳高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京石景山高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京西城高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京门头沟高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京顺义高三一模数学（第二次统练）.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京丰台高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京东城高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京平谷高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京延庆高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京房山高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京朝阳高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京海淀高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京石景山高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京西城高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京通州高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京顺义高三一模数学.pdf",
    "试卷库\\2025\\一模\\数学\\2025北京门头沟高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京密云高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京东城高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京平谷高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京延庆高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京房山高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京昌平高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京朝阳高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京通州高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京门头沟高三一模数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京顺义高三一模数学.pdf",
    "试卷库\\2024\\真题\\数学\\2024全国甲卷高考真题数学（文科）.pdf",
    "试卷库\\2024\\真题\\数学\\2024北京高考真题数学.pdf",
    "试卷库\\2024\\真题\\数学\\2024新高考II卷高考真题数学.pdf",
    "试卷库\\2024\\真题\\数学\\2024新高考I卷高考真题数学.pdf",
    "试卷库\\2025\\真题\\数学\\2025全国II卷高考真题数学.pdf",
    "试卷库\\2025\\真题\\数学\\2025全国I卷高考真题数学.pdf",
    "试卷库\\2026\\真题\\数学\\2026全国II卷高考真题数学.pdf",
    "试卷库\\2026\\真题\\数学\\2026全国I卷高考真题数学.pdf",
    "试卷库\\2026\\一模\\数学\\2026北京石景山高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京房山高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京海淀高三一模数学.pdf",
    "试卷库\\2024\\一模\\数学\\2024北京通州高三一模数学.pdf",
]

base = r"C:\Users\chuan\Documents\知识库"
out_dir = os.path.join(base, "extracted")
os.makedirs(out_dir, exist_ok=True)

for i, pdf_rel in enumerate(pdfs):
    pdf_path = os.path.join(base, pdf_rel)
    if not os.path.exists(pdf_path):
        print(i+1, "文件不存在:", pdf_path)
        continue
    try:
        items = extract_pdf_text(pdf_path)
        name = os.path.splitext(os.path.basename(pdf_rel))[0]
        out_path = os.path.join(out_dir, name + ".txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(item + "\n")
        print(i+1, "OK", len(items), "项 ->", name)
    except Exception as e:
        print(i+1, "ERROR", pdf_rel, str(e))

print("\n批量提取完成")