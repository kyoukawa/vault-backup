#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把两个站里的 github.io 绝对地址改成自定义域名。

用法：
    python retarget_domain.py                       # 只检查，不改
    python retarget_domain.py --home kyoukawa.is-a.dev --vault kb.is-a.dev

改到的东西：
    vault 仓库       index.html / dashboard.html 里指向个人主页的链接
    home 仓库        index.html 里指向知识库的链接 + DATA_URL
    （相对路径不受影响，Assets 全部是相对引用）

CNAME 不在这里写——它必须等域名真正解析成功后再加，
否则 GitHub Pages 会立刻把 github.io redirect 到还没生效的域名，站点 404。
"""

import io
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VAULT = Path(r"C:\Users\chuan\Documents\知识库")
HOME = Path(r"C:\Users\chuan\kyoukawa.github.io")

OLD_HOME = "https://kyoukawa.github.io/vault-backup/"
OLD_ROOT = "https://kyoukawa.github.io/"


def files_to_scan(root):
    out = []
    for p in root.rglob("*.html"):
        if ".git" in p.parts or ".tmp" in p.parts:
            continue
        out.append(p)
    for p in root.rglob("*.js"):
        if ".git" in p.parts or ".tmp" in p.parts:
            continue
        out.append(p)
    return out


def scan(new_home, new_vault, apply=False):
    """new_home / new_vault 形如 'https://xxx/'，注意带结尾斜杠。"""
    changes = []
    for root, label in ((VAULT, "vault"), (HOME, "home")):
        for p in files_to_scan(root):
            t = io.open(p, encoding="utf-8", errors="ignore").read()
            orig = t
            t = t.replace(OLD_HOME, new_vault)
            t = t.replace(OLD_ROOT, new_home)
            if t != orig:
                hits = len(re.findall(re.escape(OLD_HOME), orig)) + \
                       len(re.findall(re.escape(OLD_ROOT), orig))
                changes.append((label, p, hits))
                if apply:
                    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    return changes


def main():
    args = sys.argv[1:]
    home = vault = None
    for i, a in enumerate(args):
        if a == "--home":
            home = args[i + 1]
        elif a == "--vault":
            vault = args[i + 1]
    apply = "--apply" in args

    if not home or not vault:
        # 只检查：列出所有需要改的位置
        allhits = scan(OLD_HOME, OLD_HOME, apply=False)
        print("待改的文件（未指定 --home/--vault，仅检查）：")
        for label, p, n in allhits:
            print(f"  [{label}] {p.relative_to(VAULT if label == 'vault' else HOME)}  {n} 处")
        print("\n改法：")
        print("  python retarget_domain.py --home https://kyoukawa.is-a.dev/ "
              "--vault https://kb.is-a.dev/ --apply")
        return 0

    if not home.startswith("https://"):
        home = "https://" + home
    if not vault.startswith("https://"):
        vault = "https://" + vault
    home = home.rstrip("/") + "/"
    vault = vault.rstrip("/") + "/"

    # 顺序很重要：长的（vault）必须先替换，否则会被短的（root）先吃掉
    changes = []
    for root, label in ((VAULT, "vault"), (HOME, "home")):
        for p in files_to_scan(root):
            t = io.open(p, encoding="utf-8", errors="ignore").read()
            orig = t
            t = t.replace(OLD_HOME, vault)
            t = t.replace(OLD_ROOT, home)
            if t != orig:
                changes.append((label, p, t))
                if apply:
                    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

    for label, p, _ in changes:
        base = VAULT if label == "vault" else HOME
        print(f"{'已改' if apply else '将改'}  [{label}] {p.relative_to(base)}")
    if not changes:
        print("没有发现需要替换的 github.io 绝对地址")
    elif not apply:
        print("\n（加 --apply 才会真的写文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
