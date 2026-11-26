#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描试卷库，生成 exam-index.json，供 exam.html 做搜索/筛选。

用法：
    python tools/build_exam_index.py

产出两个地方：
    知识库/assets/exam-index.json    线上用（PDF 链接指向 github 仓库，静态站打不开）
    知识库/assets/exam-index.local.json  本地用（PDF 用 file:// 链接，双击能开）

字段设计见文件末尾注释。
"""

import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT = Path(r"C:\Users\chuan\Documents\知识库")
EXAM = VAULT / "试卷库"
OUT_WEB = VAULT / "assets" / "exam-index.json"
OUT_LOCAL = VAULT / "assets" / "exam-index.local.json"

SUBJECTS = ["语文", "数学", "英语", "物理", "化学", "地理", "生物", "历史", "政治"]
DISTRICTS = ["东城", "西城", "朝阳", "海淀", "丰台", "石景山", "通州", "昌平",
             "大兴", "房山", "门头沟", "怀柔", "密云", "平谷", "顺义", "延庆", "燕山"]
KINDS = ["一模", "二模", "期中", "期末", "真题"]


def parse_name(stem):
    """从卷名解析出 年/区县/卷别/学科。如 2026北京东城高三一模语文"""
    year = None
    m = re.match(r"^(20\d{2})", stem)
    if m:
        year = int(m.group(1))

    district = None
    if "全国" in stem or "北京" not in stem:
        district = "全国" if ("全国" in stem or "新高考" in stem) else None
    for d in DISTRICTS:
        if d in stem:
            district = d
            break
    if district is None and "北京" in stem and "高考真题" in stem:
        district = "北京"

    kind = None
    for k in KINDS:
        if k in stem:
            kind = k
            break

    subject = None
    for s in SUBJECTS:
        if s in stem:
            subject = s
            break

    extra = ""
    if "文" in stem and "文科" in stem:
        extra = "文科"
    elif "理" in stem and "理科" in stem:
        extra = "理科"

    return year, district, kind, subject, extra


def scan():
    """遍历 试卷库/<年>/<卷别>/<学科>/*.pdf"""
    rows = []
    for pdf in EXAM.rglob("*.pdf"):
        rel = pdf.relative_to(EXAM)
        parts = rel.parts
        if len(parts) < 4:
            continue
        y_dir, kind_dir, subj_dir = parts[0], parts[1], parts[2]
        if not re.match(r"^20\d{2}$", y_dir):
            continue
        stem = pdf.stem
        year, district, kind, subject, extra = parse_name(stem)
        rows.append({
            "year": int(y_dir),
            "kind": kind or kind_dir,
            "subject": subject or subj_dir,
            "district": district or "",
            "extra": extra,
            "title": stem,
            "path": "/".join(parts),                    # 试卷库/2026/一模/语文/xxx.pdf
            "tiji": has_tiji(subj_dir, stem),           # 有没有分题题集
        })
    rows.sort(key=lambda r: (-r["year"], KINDS.index(r["kind"]) if r["kind"] in KINDS else 9,
                             r["subject"], r["district"]))
    return rows


_tiji_cache = {}


def has_tiji(subj_dir, stem):
    """题集目录里有同名 .md 就算有。数学题集是 OCR 全文，标注出来。"""
    if subj_dir not in _tiji_cache:
        d = EXAM / f"{subj_dir}题集"
        names = set()
        if d.exists():
            for p in d.rglob("*.md"):
                names.add(p.stem)
        _tiji_cache[subj_dir] = names
    return stem in _tiji_cache[subj_dir]


def main():
    rows = scan()
    if not rows:
        print("没扫到任何 PDF，检查路径", file=sys.stderr)
        return 1

    meta = {
        "generated": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(rows),
        "years": sorted({r["year"] for r in rows}, reverse=True),
        "kinds": [k for k in KINDS if any(r["kind"] == k for r in rows)],
        "subjects": [s for s in SUBJECTS if any(r["subject"] == s for r in rows)],
        "districts": sorted({r["district"] for r in rows if r["district"]}),
        "rows": rows,
    }

    OUT_WEB.parent.mkdir(parents=True, exist_ok=True)
    io.open(OUT_WEB, "w", encoding="utf-8", newline="\n").write(
        json.dumps(meta, ensure_ascii=False, separators=(",", ":")))

    # 本地版：把 path 换成 file:// 绝对路径
    local = json.loads(json.dumps(meta))
    for r in local["rows"]:
        abs_path = (EXAM / r["path"]).as_posix()
        r["fileUrl"] = "file:///" + abs_path
    local["local"] = True
    io.open(OUT_LOCAL, "w", encoding="utf-8", newline="\n").write(
        json.dumps(local, ensure_ascii=False, separators=(",", ":")))

    print(f"共 {len(rows)} 份")
    print(f"  年: {meta['years']}")
    print(f"  卷别: {meta['kinds']}")
    print(f"  学科: {meta['subjects']}")
    print(f"  区县: {len(meta['districts'])} 个")
    print(f"  有分题题集: {sum(1 for r in rows if r['tiji'])} 份")
    print(f"写出: {OUT_WEB.name} ({OUT_WEB.stat().st_size/1024:.0f}KB)")
    print(f"      {OUT_LOCAL.name} ({OUT_LOCAL.stat().st_size/1024:.0f}KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
