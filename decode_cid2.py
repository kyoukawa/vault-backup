import struct, os

def parse_cmap_table(font_data):
    if font_data[:4] == b"\x00\x01\x00\x00":
        num_tables = struct.unpack(">H", font_data[4:6])[0]
        tables = {}
        offset = 12
        for i in range(num_tables):
            if offset + 16 > len(font_data):
                break
            tag = font_data[offset:offset+4].decode("latin-1")
            offset_val = struct.unpack(">I", font_data[offset+8:offset+12])[0]
            length = struct.unpack(">I", font_data[offset+12:offset+16])[0]
            tables[tag] = (offset_val, length)
            offset += 16
        if "cmap" not in tables:
            return {}
        cmap_offset, cmap_length = tables["cmap"]
        cmap_data = font_data[cmap_offset:cmap_offset+cmap_length]
        if len(cmap_data) < 8:
            return {}
        cmap_version = struct.unpack(">H", cmap_data[0:2])[0]
        cmap_num_tables = struct.unpack(">H", cmap_data[2:4])[0]
        sub_offset = 8
        for i in range(cmap_num_tables):
            if sub_offset + 8 > len(cmap_data):
                break
            platform_id = struct.unpack(">H", cmap_data[sub_offset:sub_offset+2])[0]
            encoding_id = struct.unpack(">H", cmap_data[sub_offset+2:sub_offset+4])[0]
            sub_offset_val = struct.unpack(">I", cmap_data[sub_offset+4:sub_offset+8])[0]
            if (platform_id == 3 and encoding_id == 1) or platform_id == 0:
                return parse_cmap_subtable(cmap_data, sub_offset_val)
            sub_offset += 8
    return {}

def parse_cmap_subtable(cmap_data, sub_offset):
    local = sub_offset
    if local + 2 > len(cmap_data):
        return {}
    format_val = struct.unpack(">H", cmap_data[local:local+2])[0]
    if format_val != 4:
        return {}
    if local + 8 > len(cmap_data):
        return {}
    seg_count_x2 = struct.unpack(">H", cmap_data[local+6:local+8])[0]
    seg_count = seg_count_x2 // 2
    local += 8
    end_counts = []
    for i in range(seg_count):
        if local + 2 > len(cmap_data):
            break
        end_counts.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    local += 2
    start_counts = []
    for i in range(seg_count):
        if local + 2 > len(cmap_data):
            break
        start_counts.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    id_deltas = []
    for i in range(seg_count):
        if local + 2 > len(cmap_data):
            break
        id_deltas.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    id_range_offsets = []
    for i in range(seg_count):
        if local + 2 > len(cmap_data):
            break
        id_range_offsets.append(struct.unpack(">H", cmap_data[local:local+2])[0])
        local += 2
    mapping = {}
    for seg in range(seg_count):
        start = start_counts[seg]
        end = end_counts[seg]
        delta = id_deltas[seg]
        range_offset = id_range_offsets[seg]
        if range_offset == 0:
            for cid in range(start, end + 1):
                uni = (cid + delta) % 65536
                mapping[cid] = uni
        else:
            glyph_index_base = local + (seg - seg_count) * 2 + range_offset
            for j, cid in enumerate(range(start, end + 1)):
                gi_offset = glyph_index_base + j * 2
                if gi_offset + 2 <= len(cmap_data):
                    glyph_id = struct.unpack(">H", cmap_data[gi_offset:gi_offset+2])[0]
                    if glyph_id != 0:
                        uni = (glyph_id + delta) % 65536
                    else:
                        uni = (cid + delta) % 65536
                    mapping[cid] = uni
    return mapping

font_paths = [
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\kaiu.ttf",
]

for fp in font_paths:
    if os.path.exists(fp):
        print("检查字体:", fp)
        with open(fp, "rb") as f:
            data = f.read()
        print("  签名:", data[:4])
        if data[:4] == b"ttcf":
            print("  TrueType Collection，需要分析子字体")
            continue
        mapping = parse_cmap_table(data)
        print("  cmap映射条目数:", len(mapping))
        if mapping:
            items = sorted(mapping.items())[:30]
            for cid, uni in items:
                ch = chr(uni) if uni < 0x110000 else "?"
                print("    CID", cid, "-> U+%04X %s" % (uni, ch))
        print()
    else:
        print("字体不存在:", fp)
