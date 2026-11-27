# 2026-11-27 首页重做 + 看板/个人主页合并

## 目标

把 `https://kb.is-a.dev/index.html` 从长列表入口页改成「今天的行动 + 备考进度 + 按用途找 + 在读」的一页式首页，并把原 `dashboard.html` 与个人主页 `kyoukawa.is-a.dev` 的内容并进同一页。

## 断言（已实跑）

| # | 命令 | 期望 | 实测 |
|---|---|---|---|
| 1 | `python .tmp/check_links.py` | 首页所有本地 href 返回 200 | 33 个本地链接全部 200 |
| 2 | `python .tmp/probe_layout.py index.html` 1280 | `overflowX = 0` | `overflowX: 0` |
| 3 | 同上 375 | `overflowX = 0` | `overflowX: 0` |
| 4 | 同上 | `dup = []`（每个目标只出现一次） | `dup: []`，anchor 37 个 |
| 5 | `node tools/check-controls.js` | 6 页全过 | `全部通过：6 个页面` |
| 6 | `python .tmp/probe_error.py` | 数据源 404 时出现兜底文案，不留「加载中」 | `暂时无法获取阅读进度` / `进度数据没读到` / 「今天做什么」改为「先做今天的四道题」 |
| 7 | `python .tmp/check_ids.py` | 用到的 ID 全在 `ids.json` 且文件存在 | 25 个 ID，全部命中 |
| 8 | 对比度脚本 | 正文 ≥ 4.5:1 | 浅色 15.8 / 5.3 / 5.4；深色 14.8 / 6.9 / 6.7 |
| 9 | `python .tmp/probe_md.py view.html?file=home` | front matter 不出现在正文 | `meta-viewport/cssclasses/date:/tags:` 均 False |
| 10 | 首页 `<head>` | 有 viewport 且 width=device-width | 第 5 行 `content="width=device-width, initial-scale=1"` |

## 失败文案（用户实际会看到）

- 进度数据 404：`进度数据没读到（HTTP 404）。这一段的去处在下面「按用途找」里都还在。本机想看完整数据：python tools/dashboard.py --serve。`
- 「今天做什么」数据 404：`今天的进度数据没取到，直接去题页；要看看板就等网络恢复后刷新。`
- 阅读数据 404：`暂时无法获取阅读进度。看上次同步的快照，数据源：weread.json。`
- 待办（非本机）：`待办只在本机可见。…本机打开：python tools/dashboard.py --serve`

## 边界（明确不做 / 基线）

- **隐私条目按用户决定保持原样公开**：学业档案（成绩/赋分/标准分）、学习日志、微信读书在读与时长继续出现在首页，不隐藏、不改可见性。
- 原有 URL 全部保留：`dashboard.html` 改为跳转页（`location.replace` 到 `index.html#progress`，保留 `?theme=`）；`latest.html` / `exam.html` / `goal-board.html` / `view.html?file=` / `sw-*.html` 不动。
- 个人主页 `kyoukawa.github.io` 改为跳转页到 `https://kb.is-a.dev/`，保留查询串。
- 不新增外部依赖；搜索仍走已有 `assets/search-index.json` + `kb-ui.js`。
- 单提交规模：3 个页面 + 1 个 CSS + 2 个工具脚本 + 2 个导航文档。

## 改动清单

| 文件 | 动作 |
|---|---|
| `index.html` | 重写：定位语 + 搜索 + 今天做什么 + 备考进度（KPI/数字化/标准分/活跃度）+ 按用途找（5 组）+ 正在读 + 待办 + 在写的东西 + 页脚折叠技术说明 |
| `assets/home.css` | 新增：首页专属 token 与组件（不写死颜色以外的值） |
| `dashboard.html` | 改为跳转页（保留 URL） |
| `index.md` | 同步网页目录内容 |
| `知识库导航.md` | 「看板」入口改指首页 |
| `tools/dashboard.py` | `--serve` 默认打开 `index.html` |
| `tools/check-controls.js` | 页面清单换掉 dashboard.html；首页按 44px 胶囊单独断言 |
| `kyoukawa.github.io/index.html` | 改为跳转页 |

## 审查（待独立 agent 追加）
