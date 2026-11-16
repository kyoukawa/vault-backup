import os

fonts_dir = r"C:\Users\chuan\Documents\知识库\fonts"
for name in sorted(os.listdir(fonts_dir)):
    path = os.path.join(fonts_dir, name)
    with open(path, "rb") as f:
        sig = f.read(4)
    size = os.path.getsize(path)
    sig_str = sig.hex()
    if sig == b"\x00\x01\x00\x00":
        fmt = "TrueType"
    elif sig == b"ttcf":
        fmt = "TrueType Collection"
    elif sig == b"OTTO":
        fmt = "OpenType/CFF"
    else:
        fmt = "Unknown(" + sig_str + ")"
    print(name, size, "bytes,", fmt)