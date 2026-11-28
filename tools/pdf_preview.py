#!/usr/bin/env python3
"""把 PDF 逐页渲染成图片版 Markdown，用 Zed 的 Markdown 预览当 PDF 阅读器。

Zed 没有 PDF 渲染器，官方扩展库里也没有 PDF 扩展；但 Markdown 预览能显示
本地图片，所以把每页渲成 PNG/JPG 再拼成一篇 md 即可。

用法：
    python tools/pdf_preview.py                 # 弹文件选择框挑 PDF
    python tools/pdf_preview.py <file.pdf>      # 渲染并打开预览
    python tools/pdf_preview.py <file.pdf> --dpi 200    # 更清晰（更慢、更大）
    python tools/pdf_preview.py <file.pdf> --pages 1-9  # 只渲染部分页
    python tools/pdf_preview.py <file.pdf> --jpg       # JPG（体积小，适合扫描件）
    python tools/pdf_preview.py <file.pdf> --no-open    # 只生成，不调 zed

产物在 .tmp/pdf-preview/<文件名>/（.tmp 已被 .gitignore 忽略），同目录下
<文件名>.md 就是预览入口，在 Zed 里对它执行「Open Markdown Preview」即可通读。
PDF 没变时重跑会直接复用已有图片。
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def parse_pages(spec, total):
    """'1-9' / '3' / '1,4,7-9' / 'all' -> [0-based 索引]"""
    if not spec or spec.strip().lower() in ("all", "1-", ""):
        return list(range(total))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d*)", part)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else total
            out.extend(range(max(1, a), min(total, b) + 1))
        elif part.isdigit():
            out.append(int(part))
        else:
            raise SystemExit(f"看不懂的页码写法：{part}")
    seen, pages = set(), []
    for p in out:
        if 1 <= p <= total and p not in seen:
            seen.add(p)
            out_p = p - 1
            pages.append(out_p)
    return pages


def output_dir(pdf: Path):
    """优先放到 Zed 工作区的 .tmp 下（.gitignore 已忽略），否则就近放 .tmp。"""
    root = os.environ.get("ZED_WORKTREE_ROOT")
    if root and Path(root).is_dir():
        base = Path(root) / ".tmp" / "pdf-preview"
    else:
        d = pdf.parent
        while d != d.parent and not (d / ".git").exists():
            d = d.parent
        base = (d if (d / ".git").exists() else pdf.parent) / ".tmp" / "pdf-preview"
    return base / pdf.stem


def render(pdf: Path, out: Path, pages, dpi, fmt, force):
    import pymupdf

    out.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if fmt == "jpg" else "png"
    doc = pymupdf.open(pdf)
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)

    made = []
    newest_src = pdf.stat().st_mtime
    for pno in pages:
        img = out / f"p{pno + 1:03d}.{ext}"
        made.append(img)
        if not force and img.exists() and img.stat().st_mtime >= newest_src:
            continue
        pix = doc[pno].get_pixmap(matrix=mat, alpha=False)
        if ext == "jpg":
            pix.pil_save(img, quality=82, optimize=True)
        else:
            pix.save(img)
        print(f"  渲染第 {pno + 1} 页 → {img.name}", flush=True)
    return doc.page_count, made, ext


def build_md(pdf: Path, out: Path, ext, total):
    """生成预览用 md，收进目录里已有的全部图片，这样分次渲染也能累积。"""
    pat = re.compile(r"^p(\d+)\." + ext + r"$")
    found = {}
    for f in out.iterdir():
        m = pat.match(f.name)
        if m:
            found[int(m.group(1))] = f
    lines = [
        f"# {pdf.stem}",
        "",
        "> PDF 预览（Zed 无内置 PDF 渲染器，此文件由 `tools/pdf_preview.py` 生成）  ",
        f"> 源文件：`{pdf}`  ·  共 {total} 页  ·  本文件含 {len(found)} 页",
        "",
        "---",
        "",
    ]
    for pno in sorted(found):
        lines += [
            f"## 第 {pno} 页",
            "",
            f"![第 {pno} 页]({found[pno].name})",
            "",
        ]
    md = out / f"{pdf.stem}.md"
    md.write_text("\n".join(lines), encoding="utf-8")
    return md, len(found)


def pick_pdf():
    """没给路径时弹系统文件选择框，默认落在当前工作目录。"""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="选择要预览的 PDF",
        initialdir=os.environ.get("ZED_WORKTREE_ROOT") or os.getcwd(),
        filetypes=[("PDF", "*.pdf"), ("所有文件", "*.*")],
    )
    root.destroy()
    if not path:
        raise SystemExit("没有选择文件")
    return path


def main():
    ap = argparse.ArgumentParser(description="PDF → 图片版 Markdown（Zed 预览）")
    ap.add_argument("pdf", nargs="?", help="PDF 路径；省略则弹文件选择框")
    ap.add_argument("--dpi", type=int, default=150, help="渲染分辨率，默认 150")
    ap.add_argument("--pages", default="", help="页码，如 1-9 或 1,4,7-9，默认全部")
    ap.add_argument("--jpg", action="store_true", help="输出 JPG（体积小，扫描件友好）")
    ap.add_argument("--force", action="store_true", help="强制重新渲染")
    ap.add_argument("--no-open", action="store_true", help="生成后不调用 zed")
    args = ap.parse_args()

    pdf = Path(args.pdf or pick_pdf()).expanduser().resolve()
    if pdf.suffix.lower() != ".pdf":
        raise SystemExit(f"不是 PDF：{pdf}")
    if not pdf.is_file():
        raise SystemExit(f"找不到文件：{pdf}")

    try:
        import pymupdf
    except ImportError:
        raise SystemExit("需要 pymupdf：pip install pymupdf")

    doc = pymupdf.open(pdf)
    total = doc.page_count
    pages = parse_pages(args.pages, total)
    if not pages:
        raise SystemExit("没有可渲染的页")

    out = output_dir(pdf)
    fmt = "jpg" if args.jpg else "png"
    print(f"{pdf.name}：{total} 页，渲染 {len(pages)} 页 @ {args.dpi}dpi → {out}", flush=True)

    _, _, ext = render(pdf, out, pages, args.dpi, fmt, args.force)
    md, npages = build_md(pdf, out, ext, total)

    size = sum(p.stat().st_size for p in out.glob(f"p*.{ext}")) / 1048576
    msg = f"完成：预览含 {npages} 页，图片共 {size:.1f} MB\n预览文件：{md}"
    if npages < total:
        msg += f"\n（PDF 共 {total} 页，还有 {total - npages} 页未渲染；重跑不带 --pages 即可补齐）"
    print(msg, flush=True)

    if not args.no_open:
        zed = os.environ.get("ZED_BIN") or "zed"
        try:
            subprocess.Popen([zed, "--add", str(md)], shell=False)
        except OSError:
            print(f"（没能自动打开，手动在 Zed 里打开：{md}）")


if __name__ == "__main__":
    main()
