#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成全站搜索索引，分两级：

    assets/search-index.json         标题 + 路径 + 摘要（轻，首屏加载）
    assets/search-body/<n>.json      全文分片（重，搜索时才拉）

分片按 8 篇一组，一次只拉需要的几片，避免首屏 4MB。

用法：
    python tools/build_search_index.py
"""

import io
import json
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT = Path(r"C:\Users\chuan\Documents\知识库")
OUT = VAULT / "assets" / "search-index.json"
BODY_DIR = VAULT / "assets" / "search-body"

SKIP_DIRS = {".git", ".obsidian", ".tmp", "_minis", "assets", "node_modules", "tools",
             "docs"}   # docs/ 放开发任务文件，不是笔记，不进全站搜索
CHUNK = 8          # 每片篇数
BODY_CHARS = 4000  # 每篇保留正文字符数


def clean(text):
    if text.startswith("---"):
        m = re.match(r"^---\n.*?\n---\n", text, re.S)
        if m:
            text = text[m.end():]
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[#>*`_~]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def title_of(text, fallback):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    if m:
        return m.group(1).strip().strip('"\'')
    return fallback


def main():
    rows = []
    bodies = []
    for p in VAULT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(VAULT).as_posix()
        try:
            raw = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        body = clean(raw)
        if not body:
            continue
        folder = str(p.relative_to(VAULT).parent.as_posix())
        if folder == ".":
            folder = ""
        rows.append({
            "t": title_of(raw, p.stem),
            "p": rel,
            "f": folder,
            "s": body[:160],
            "c": len(bodies) // CHUNK,      # 属于第几片
        })
        bodies.append(body[:BODY_CHARS])

    rows.sort(key=lambda r: (r["f"], r["t"]))
    # 排序后重新分配分片号
    for i, r in enumerate(rows):
        r["c"] = i // CHUNK

    OUT.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps({"count": len(rows), "chunk": CHUNK, "rows": rows},
                   ensure_ascii=False, separators=(",", ":")))

    # 正文分片：按排序后的顺序写，chunk 号对应 rows 里的 c
    if BODY_DIR.exists():
        shutil.rmtree(BODY_DIR)
    BODY_DIR.mkdir(parents=True)
    n_chunks = (len(rows) + CHUNK - 1) // CHUNK
    for ci in range(n_chunks):
        part = {}
        for r in rows[ci * CHUNK:(ci + 1) * CHUNK]:
            idx = [x["p"] for x in rows].index(r["p"]) if False else None
        # 直接按 rows 顺序取 body（rows 已排序，bodies 未排序 → 用路径重建映射）
    # 重建 path -> body 映射
    path2body = {}
    for p in VAULT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(VAULT).as_posix()
        try:
            raw = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        b = clean(raw)
        if b:
            path2body[rel] = b[:BODY_CHARS]

    for ci in range(n_chunks):
        part = {}
        for r in rows[ci * CHUNK:(ci + 1) * CHUNK]:
            part[r["p"]] = path2body.get(r["p"], "")
        io.open(BODY_DIR / f"{ci}.json", "w", encoding="utf-8", newline="\n").write(
            json.dumps(part, ensure_ascii=False, separators=(",", ":")))

    idx_kb = OUT.stat().st_size / 1024
    body_kb = sum(f.stat().st_size for f in BODY_DIR.glob("*.json")) / 1024
    print(f"收录 {len(rows)} 篇")
    print(f"  主索引 {idx_kb:.0f}KB（首屏加载）")
    print(f"  正文 {n_chunks} 片 / 共 {body_kb:.0f}KB（{body_kb/n_chunks:.0f}KB per 片，按需拉）")

    from collections import Counter
    c = Counter(r["f"].split("/")[0] if r["f"] else "(根)" for r in rows)
    for k, v in c.most_common():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
