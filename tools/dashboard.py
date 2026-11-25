# -*- coding: utf-8 -*-
"""生成知识库看板的数据文件。

用法：
    python tools/dashboard.py            # 只生成 assets/dashboard.json + assets/todos.local.json
    python tools/dashboard.py --serve    # 生成后起本地服务器并打开，待办才看得到

产出：
    assets/dashboard.json     —— 入库，公开（不含待办）
    assets/todos.local.json   —— 不入库（.gitignore），只有本机开服务器才读得到

数据来源全部是仓库内的真实文件 + git 历史；不做推测。
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

MCP_URL = "https://frogtodo.shuge888.com/mcp"
# 备忘分组里是新闻简报等私人内容，不写进任何产出
SKIP_CATEGORIES = {"备忘"}

WEEKDAY_CN = "一二三四五六日"


# ---------------------------------------------------------------- 小工具
def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def split_row(line):
    """按未转义的 | 切表格行。Obsidian 表格里 [[a\\|b]] 用 \\| 转义。"""
    s = line.strip()
    cells, buf, i = [], [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if c == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
        i += 1
    cells.append("".join(buf).strip())
    # 首尾的竖线会切出空串，丢掉
    while cells and cells[0] == "":
        cells.pop(0)
    while cells and cells[-1] == "":
        cells.pop()
    return cells


def md_tables(text):
    """把 Markdown 里所有表格解析成 [[{header:cell}, ...], ...]。"""
    out, cur = [], []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = split_row(s)
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            cur.append(cells)
        else:
            if len(cur) >= 2:
                out.append(cur)
            cur = []
    if len(cur) >= 2:
        out.append(cur)
    return out


def strip_noise(s):
    """去掉 wikilink / markdown 强调，留纯文本。"""
    s = re.sub(r"\[\[([^\]\|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = s.replace("\\|", "|")
    return s.strip()


def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else ""


# ---------------------------------------------------------------- 各数据块
def daily_block():
    d = os.path.join(ROOT, "每日题目")
    days = sorted(
        f[:-5] for f in os.listdir(d)
        if f.endswith(".html") and re.fullmatch(r"\d{4}-\d{2}-\d{2}\.html", f)
    )
    if not days:
        return {"latest": None, "days_ago": None, "count": 0, "total": 0}
    latest = days[-1]
    ago = (date.today() - date.fromisoformat(latest)).days
    return {"latest": latest, "days_ago": ago, "count": 4, "total": len(days)}


def exam_block():
    """试卷数字化：题集笔记数 / 原卷 PDF 数。口径与 goal-board 一致。"""
    root = os.path.join(ROOT, "试卷库")
    skip = {"00-导航.md", "INDEX.md", "做题记录.md", "红楼梦题集.md", "README.md"}
    by_subject = {}
    for sub in sorted(os.listdir(root)):
        p = os.path.join(root, sub)
        if not os.path.isdir(p) or not sub.endswith("题集"):
            continue
        n = 0
        for dp, _dns, fns in os.walk(p):
            if "_待重提取" in dp:
                continue
            n += sum(1 for f in fns if f.endswith(".md") and f not in skip)
        by_subject[sub[:-2]] = n
    pdf = 0
    for dp, _dns, fns in os.walk(root):
        pdf += sum(1 for f in fns if f.lower().endswith(".pdf"))
    done = sum(by_subject.values())
    return {
        "done": done,
        "total": pdf,
        "pct": round(done * 100.0 / pdf, 1) if pdf else 0,
        "by_subject": [{"name": k, "value": v} for k, v in
                       sorted(by_subject.items(), key=lambda x: -x[1])],
    }


def reading_block():
    p = os.path.join(ROOT, "assets", "weread.json")
    if not os.path.exists(p):
        return None
    d = json.loads(read(p))
    t, c = d.get("time", {}), d.get("counts", {})
    return {
        "updated": d.get("updated"),
        "shelf": d.get("shelf", 0),
        "reading": c.get("reading", 0),
        "done": c.get("done", 0),
        "week": t.get("week", 0),
        "week_days": t.get("weekDays", 0),
        "all": t.get("all", 0),
        "books": [{"title": b.get("title"), "author": b.get("author"),
                   "progress": b.get("progress", 0), "minutes": b.get("minutes", 0)}
                  for b in (d.get("reading") or [])[:5]],
    }


def coach_block():
    p = os.path.join(ROOT, "学业档案", "带学", "状态.md")
    if not os.path.exists(p):
        return None
    txt = read(p)
    body = txt.split("## 当前", 1)[-1]
    out = {}
    for line in body.splitlines():
        m = re.match(r"-\s*([^：:]+)[：:]\s*(.+)", line.strip())
        if m:
            out[m.group(1).strip()] = strip_noise(m.group(2))
    return {
        "state": out.get("状态", "—"),
        "subject": out.get("科目 / 考点", "—"),
        "next": out.get("下次", "—"),
        "updated": (re.search(r"^updated:\s*(.+)$", txt, re.M) or [None, ""])[1],
    }


def grades_block():
    """期中考标准分，来自学业档案里的成绩表。"""
    p = os.path.join(ROOT, "学业档案", "2026", "2026-11-期中考（赋分前）.md")
    if not os.path.exists(p):
        return None
    rows = []
    for table in md_tables(read(p)):
        head = [strip_noise(h) for h in table[0]]
        if "标准分" not in head or "得分率" not in head:
            continue
        idx = {h: i for i, h in enumerate(head)}
        for r in table[1:]:
            try:
                name = strip_noise(r[idx["科目"]])
                z = float(strip_noise(r[idx["标准分"]]))
                rows.append({
                    "subject": name,
                    "score": float(strip_noise(r[idx["得分"]])),
                    "full": float(strip_noise(r[idx["满分"]])),
                    "rate": float(strip_noise(r[idx["得分率"]]).rstrip("%")),
                    "z": z,
                })
            except (ValueError, KeyError, IndexError):
                continue
        break
    return {"exam": "2026-11 期中（赋分前）", "rows": rows} if rows else None


def weakness_block():
    p = os.path.join(ROOT, "学业档案", "学习日志.md")
    if not os.path.exists(p):
        return []
    out = []
    for table in md_tables(read(p)):
        head = [strip_noise(h) for h in table[0]]
        if "短板" not in head or "学科" not in head:
            continue
        idx = {h: i for i, h in enumerate(head)}
        for r in table[1:]:
            subject = strip_noise(r[idx["学科"]])
            note = strip_noise(r[idx["短板"]])
            if note in ("—", "-", ""):
                continue
            out.append({"subject": subject, "note": note,
                        "status": strip_noise(r[idx["状态"]])})
        break
    return out


LIBRARIES = [
    ("试卷库", "exam-index", "北京高考/一模/二模/期末原卷（教师版含答案）+ 分题题集"),
    ("化学错题本", "chem-index", "选择题按主题聚类 + 大题按 6 模块"),
    ("语文语料库", "chinese-index", "作文素材、六维判据、整本精读、时文批注"),
    ("英语语料库", "english-index", "作文素材，What → How → Effect → Value"),
    ("数学", "analytic-geometry", "解析几何方法总结与学案"),
    ("阅读收集", "reading-index", "网页 / 公众号 / 视频 → 结构化笔记"),
    ("读书", "reading-home", "微信读书进度追踪，脚本自动生成"),
    ("学业档案", "record", "大考成绩、赋分、标准分与失分分析"),
]


def library_block():
    """每个库的条目数 —— 直接数文件，不抄索引里的话。"""
    def count(sub, exts=(".md",), skip_dirs=(".git", ".obsidian", ".tmp", "assets")):
        base = os.path.join(ROOT, sub)
        if not os.path.isdir(base):
            return 0
        n = 0
        for dp, dns, fns in os.walk(base):
            dns[:] = [x for x in dns if x not in skip_dirs]
            n += sum(1 for f in fns if f.lower().endswith(exts))
        return n

    exams = exam_block()
    spec = {
        "试卷库": (f"{exams['done']} 篇题集 / {exams['total']} 份原卷", ""),
        "化学错题本": (f"{count('化学错题本')} 篇笔记", ""),
        "语文语料库": (f"{count('语文语料库')} 篇笔记", ""),
        "英语语料库": (f"{count('英语语料库')} 篇笔记", ""),
        "数学": (f"{count('数学')} 篇", ""),
        "阅读收集": (f"{count('阅读收集')} 篇笔记", ""),
        "读书": (f"{count('读书')} 份自动生成记录", ""),
        "学业档案": (f"{count('学业档案')} 篇", ""),
    }
    out = []
    for name, link, desc in LIBRARIES:
        size, _ = spec.get(name, ("", ""))
        out.append({"name": name, "href": "view.html?file=" + link,
                    "desc": desc, "size": size})
    return out


def activity_block(weeks=13):
    """vault 活跃度：真编辑提交 + 每日题目 + 日志条目，按天合并。

    排除 obsidian-git 的 "vault backup:" 提交 —— 那是自动同步，不代表人干活。
    """
    counts = {}

    def bump(day, key, n=1):
        counts.setdefault(day, {"commit": 0, "daily": 0, "log": 0})[key] += n

    for line in git("log", "--pretty=format:%ad%x09%s", "--date=short").splitlines():
        if "\t" not in line:
            continue
        day, subj = line.split("\t", 1)
        if subj.startswith("vault backup:"):
            continue
        bump(day, "commit")

    d = os.path.join(ROOT, "每日题目")
    for f in os.listdir(d):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.html", f)
        if m:
            bump(m.group(1), "daily")

    for rel in ("学业档案/学习日志.md", "读书/阅读日志.md"):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        for m in re.finditer(r"^###\s*(\d{4}-\d{2}-\d{2})", read(p), re.M):
            bump(m.group(1), "log")

    today = date.today()
    active = sorted(d for d, c in counts.items() if sum(c.values()) > 0)
    # 固定 10 周窗口（GitHub 贡献图的观感）。仓库 2026-11-02 才开始，
    # 前面几周是空白没关系——那是真实情况，比只画 6 列看着像坏掉强。
    start = today - timedelta(days=today.weekday() + 7 * (weeks - 1))
    start -= timedelta(days=start.weekday())
    days = []
    cur = start
    while cur <= today:
        k = cur.isoformat()
        c = counts.get(k, {"commit": 0, "daily": 0, "log": 0})
        total = c["commit"] + c["daily"] + c["log"]
        days.append({"date": k, "total": total, **c})
        cur += timedelta(days=1)
    return {"start": start.isoformat(), "end": today.isoformat(),
            "first_active": active[0] if active else None, "days": days}


# ---------------------------------------------------------------- 待办（只落本地）
def mcp_call(name, args):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": name, "arguments": args}}
    req = urllib.request.Request(MCP_URL, data=json.dumps(payload, ensure_ascii=False).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    req.add_header("Authorization", "Bearer " + (os.environ.get("TODO_TOKEN") or ""))
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.loads(r.read().decode("utf-8", "replace"))
    return json.loads(body["result"]["content"][0]["text"])


def todos_block():
    token = os.environ.get("TODO_TOKEN")
    if not token:
        return {"ok": False, "error": "没有 TODO_TOKEN 环境变量"}
    try:
        cats = mcp_call("frogtodo_list_categories", {}).get("categories") or []
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    columns = []
    for c in cats:
        title = c.get("title", "")
        if title in SKIP_CATEGORIES or c.get("archived"):
            continue
        try:
            d = mcp_call("frogtodo_search_todos",
                         {"categoryIndexId": c["categoryIndexId"],
                          "includeUndated": True, "limit": 200})
        except Exception:
            continue
        open_items = []
        for t in (d.get("todos") or []):
            if t.get("complete"):
                continue
            due = None
            if t.get("dateYear"):
                due = f'{t["dateYear"]:04d}-{t["dateMonth"]:02d}-{t["dateDay"]:02d}'
                overdue = due < date.today().isoformat()
            else:
                overdue = False
            open_items.append({
                "title": (t.get("title") or "").strip(),
                "due": due,
                "overdue": overdue,
                "important": int(t.get("importantLevel") or 0),
            })
        open_items.sort(key=lambda x: (not x["overdue"], x["due"] or "9999", x["title"]))
        columns.append({"name": title, "items": open_items,
                        "color": "#" + (c.get("color") or "ff888888")[2:]})

    columns.sort(key=lambda x: -len(x["items"]))
    return {"ok": True, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "columns": columns}


# ---------------------------------------------------------------- main
def main():
    data = {
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "today": date.today().isoformat(),
        "daily": daily_block(),
        "exams": exam_block(),
        "reading": reading_block(),
        "coach": coach_block(),
        "grades": grades_block(),
        "weakness": weakness_block(),
        "libraries": library_block(),
        "activity": activity_block(),
    }

    out = os.path.join("assets", "dashboard.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"[ok] {out}  {os.path.getsize(out)} bytes")

    todos = todos_block()
    tp = os.path.join("assets", "todos.local.json")
    if todos.get("ok"):
        with io.open(tp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(todos, f, ensure_ascii=False, indent=1)
        n = sum(len(c["items"]) for c in todos["columns"])
        print(f"[ok] {tp}  {os.path.getsize(tp)} bytes  未完成 {n} 条")
    else:
        print(f"[skip] 待办未取到：{todos.get('error')}")

    print(f"     试卷 {data['exams']['done']}/{data['exams']['total']}"
          f"  · 每日题最新 {data['daily']['latest']}"
          f"  · 活跃天数 {sum(1 for d in data['activity']['days'] if d['total'])}")

    if "--serve" in sys.argv:
        import webbrowser
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        port = 8765
        srv = ThreadingHTTPServer(("127.0.0.1", port),
                                  lambda *a, **k: SimpleHTTPRequestHandler(*a, directory=ROOT, **k))
        url = f"http://127.0.0.1:{port}/dashboard.html"
        print(f"\n  本地预览：{url}\n  Ctrl+C 结束")
        webbrowser.open(url)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\n  已停止")


if __name__ == "__main__":
    main()
