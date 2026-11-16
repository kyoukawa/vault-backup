import struct, os

def parse_cmap_table(font_data):
    """解析TrueType字体的cmap表，返回cid->unicode映射"""
    if font_data[:4] == b"\x00\x01\x00\x00":
        num_tables = struct.unpack(">H", font_data[4:6])[0]
        tables = {}
        offset = 12
        for i in range(num_tables):
            tag = font_data[offset:offset+4].decode("latin-1")
            offset_val = struct.unpack(">I", font_data[offset+8:offset+12])[0]
            length = struct.unpack(">I", font_data[offset+12:offset+16])[0]
            tables[tag] = (offset_val, length)
            offset += 16
        if "cmap" not in tables:
            return {}
        cmap_offset, cmap_length = tables["cmap"]
        cmap_data = font_data[cmap_offset:cmap_offset+cmap_length]
        cmap_version = struct.unpack(">H", cmap_data[0:2])[0]
        cmap_num_tables = struct.unpack(">H", cmap_data[2:4])[0]
        sub_offset = 8
        for i in range(cmap_num_tables):
            platform_id = struct.unpack(">H", cmap_data[sub_offset:sub_offset+2])[0]
            encoding_id = struct.unpack(">H", cmap_data[sub_offset+2:sub_offset+4])[0]
            sub_offset_val = struct.unpack(">I", cmap_data[sub_offset+4:sub_offset+8])[0]
            # platform 3 = Windows, encoding 1 = Unicode BMP (平台特定)
            # platform 0 = Unicode
            if (platform_id == 3 and encoding_id == 1) or platform_id == 0:
                return parse_cmap_subtable(cmap_data, sub_offset_val)
            sub_offset += 8
    return {}

def parse_cmap_subtable(cmap_data, sub_offset):
    """解析cmap子表（格式4，分段映射）"""
    local = sub_offset
    format_val = struct.unpack(">H", cmap_data[local:local+2])[0]
    if format_val != 4:
        return {}
    seg_count = struct.unpack(">H", cmap_data[local+6:local+8])[0] // 2
    # 跳过到endCount
    local += 8
    end_counts = []
    for i in range(seg_count):
        end_counts.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    local += 2  # skip reservedPad
    start_counts = []
    for i in range(seg_count):
        start_counts.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    id_deltas = []
    for i in range(seg_count):
        id_deltas.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    id_range_offsets = []
    for i in range(seg_count):
        id_range_offsets.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    glyph_ids = []
    while local < len(cmap_data):
        glyph_ids.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    mapping = {}
    for seg in range(seg_count):
        start = start_counts[seg]
        end = end_counts[seg]
        delta = id_deltas[seg]
        range_offset = id_range_offsets[seg]
        for cid in range(start, end + 1):
            if range_offset == 0:
                uni = (cid + delta) % 65536
            else:
                # 计算glyph id索引
                pass
            mapping[cid] = uni
    return mapping

# 测试系统字体
font_paths = [
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\kaiu.ttf",
]

for fp in font_paths:
    if os.path.exists(fp):
        print("检查字体:", fp)
        with open(fp, "rb") as f:
            data = f.read()
        print("  签名:", data[:4])
        # ttc集合需要特殊处理
        if data[:4] == b"ttcf":
            print("  TrueType Collection，跳过")
            continue
        mapping = parse_cmap_table(data)
        print("  cmap映射条目数:", len(mapping))
        if mapping:
            # 打印前20个映射
            items = sorted(mapping.items())[:20]
            for cid, uni in items:
                print("    CID", cid, "-> U+%04X" % uni, chr(uni) if uni < 0x110000 else "?")
        print()
    else:
        print("字体不存在:", fp)