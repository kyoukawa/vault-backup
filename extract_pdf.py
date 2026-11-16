import zlib, re, sys, os

def extract_pdf_text(pdf_path):
    """从PDF中提取文本，处理Tj和TJ操作符"""
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

    text_streams = []
    valid = 0
    for i in range(min(len(stream_positions), len(endstream_positions))):
        start = stream_positions[i] + 6
        end = endstream_positions[i]
        if end > start:
            stream_data = data[start:end].strip()
            try:
                decompressed = zlib.decompress(stream_data)
                text = decompressed.decode("latin-1", errors="replace")
                if "Tj" in text or "TJ" in text or "BT" in text or "ET" in text:
                    text_streams.append((i, text))
                valid += 1
            except Exception:
                pass

    all_text_items = []
    for idx, text in text_streams:
        pos2 = 0
        while True:
            start_bracket = text.find("[(", pos2)
            if start_bracket == -1:
                break
            end_pos = text.find(")]", start_bracket + 2)
            if end_pos == -1:
                break
            after = text[end_pos+2:end_pos+5].strip()
            if after.startswith("TJ"):
                content = text[start_bracket+2:end_pos]
                # 处理十六进制编码 <XXXX>
                if content.startswith('<') and content.endswith('>'):
                    hex_str = content[1:-1]
                    try:
                        chars = bytes.fromhex(hex_str).decode('utf-16-be', errors='replace')
                        all_text_items.append(chars)
                    except Exception:
                        all_text_items.append(content)
                else:
                    all_text_items.append(content)
            pos2 = end_pos + 2

    return all_text_items

if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not pdf_path:
        print("用法: python extract_pdf.py <pdf_path> [output_path]")
        sys.exit(1)

    items = extract_pdf_text(pdf_path)
    text = "\n".join(items)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"已保存 {len(items)} 个文本项到 {output_path}")
    else:
        print(text)