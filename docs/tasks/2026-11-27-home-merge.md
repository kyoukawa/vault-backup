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

## 审查（独立 agent，2026-11-27）

### 结论：**不通过（附原因）**

Goal 主体成立：一页式首页（今天做什么 / 备考进度 / 按用途找 / 正在读 / 待办 / 在写的东西）已上线，`dashboard.html` 与个人主页都改成了带查询串的跳转，原有 URL 全保留，导航已同步，配色走 home.css 新 token，隐私条目按用户决定保持公开。10 条断言我抽验后均成立（ID 全命中、JSON 合法、静态资源 200、锚点齐全、committed blob == 服务端字节）。

不通过仅在**边界两项**：Goal 自己在代码注释里立的「不让页面挂在半截」（index.html:291）在两种异常数据下被破坏——活跃度空数据会留一整块空白面板、`renderDash` 中途抛异常时错误文案被自己的 `hidden` 遮住。两者在当前真实数据下不触发（生成器固定产出 13 周），但 4 条小改即可补上，属于交付前应修的硬化项，不涉及返工重做。

### 四问逐条

**1. 失败时用户看到什么？——有一条数据路径会留下不可见的错误/空白。**
- `dashboard.json` 整体 404：`.catch`（index.html:316-326）写 `progress-empty` 文案 + `gen-note` + `today-box` 兜底，**有文案**，符合断言 #6。
- ⚠️ **`renderDash` 中途抛异常**：函数开头先 `progress-empty.hidden=true` / `progress-body.hidden=false`（index.html:329-331），之后的 `.catch`（316-319）只往已隐藏的 `progress-empty` 塞文案 → 用户看不到错误，`progress-body` 停在半渲染/空面板。典型触发：`ex.pct` 缺字段（361 `toFixed`）、schema 漂移。**这是静默留白。**
- ⚠️ **`d.activity.days` 为空**：`act=[]`，index.html:427 `if (act.length)` 无 else → 「活跃度」面板只剩 `<h3>`+提示，热力图/月度/合计/最近/表格全空，**没有任何「无数据」文案**。同属静默留白。
- 「正在读」`weread.json` 404：`rl-msg` 兜底（495-497），有文案。`reading:[]` 不报错、汇总行照出。待办非本机/本机无文件都有文案（534-539、557-559）。
- 搜索：`search-index.json` 失败时 kb-ui.js `doRun` 直接 `return`（kb-ui.js:127），输入后无反应——**静默**，但属全站既有问题、本次未改，登记为 out-of-scope（info）。

**2. 边界逐项**
- `d.activity.days` 为空：不抛异常，但活跃度面板空白（见上）。
- `d.grades.rows` 为空 / `grades` 为 null：`if (g && g.rows && g.rows.length)` 走 else 显示「还没有成绩数据。」（422-424），**OK**。
- `weread.json` `reading: []`：`rows=''`，汇总行照常渲染计数，无表无列表，**不抛异常、不空白**，OK。
- 书名超长：`esc(b.title)` 已转义；但 `.kb-reading table.rl{display:table}`（home.css:252）覆盖了 hermes.css:212 的 `table{display:block;overflow-x:auto}`，表格不再横向滚动，而 `td.bk` 未设 `overflow-wrap:anywhere`（对比 footer 有设，home.css:473）。超长无空格串会撑宽而非折行/滚动——**低危，极端输入才会暴露**。
- `dl.days_ago` 为 null：`dl.latest` 存在、`days_ago` 为 null 时，342 用 `days_ago > 1` 判定 → 显示「（就是今天）」，364 显示「最近 X（null 天前）」，**展示 "null" 与错误语义**。当前生成器不会产出该组合，但守卫写得不严（应用 `!= null && days_ago>1`）。
- 非法日期：`new Date('xT00:00:00')` 返回 Invalid Date，`getDay()/getMonth()` 得 NaN，**不抛异常**，热力图降级但不打断 `renderDash`——符合「不把整个 render 打断」的要求。
- 并发：两路 fetch 各自写 `foot-upd`（333 dashboard.generated vs 526 weread.updated），谁后到谁覆盖，「数据更新于」非确定，**低危**（不改）。
- 越权 / 别人的 id：静态公开站，无鉴权、无用户 id，**N/A**；`view.html?file=` 越界属另一个页，本页未引入。

**3. 有没有第二处同样的逻辑？**
- `dur()`：grep 全仓 + 个人主页，现在**只有 index.html:285 一处**。本次改动把旧 `dashboard.html`、个人主页里的副本随跳转页一起删掉了——**重复是被消除的，不是新增**，这点合格。
- `esc()`：仍有 3 份——index.html:280、view.html:233、assets/kb-ui.js:26。本次新增第 3 份，属既有小工具重复，可后续收进 kb-ui 全局，**低危**。
- KPI / 热力图 / `.meter` / `.hbars` / `.zrow` 的渲染与 CSS：grep 全仓只命中 index.html 与 assets/home.css；`goal-board.html` 无任何 `heat-cell/meter/kpi/hbar/zplot`。**没有残留在别处**，合格。
- home.css 与 hermes.css 冲突核查：
  - `:root`/`[data-theme]`：home.css 在 hermes.css 之后加载（index.html:8→10），同权重后者生效——**预期就是覆盖 token**；home.css 未重定义 `--ease/--dur/--serif/--radius-*/--ctl-*/--success-bg` 等，依赖 hermes 提供（已加载），无断链。
  - `.kb-search input`：kb-ui.css 后加载但权重低（`.kb-search input` 0,1,1），home.css:118 `body.home .kb-search input`（0,2,2）更高 → 44px 胶囊生效，check-controls 已断言，**无覆盖事故**。
  - `h2::after`：hermes `h2::after`（0,0,2） vs home `.home-h2::after`（0,1,1），home 胜，效果一致，无冲突。
  - `.heat-cell` 的窄屏媒体查询（home.css:393）**写在基础规则（381）之后**——恰好避开了「媒体查询写前面被覆盖」的坑，这一点做对了。
  - 唯一实质冲突是上面的 `table` 滚动（hermes 211-216 vs home 252），见边界。

**4. 改动真的生效了吗？静态站三条可粘贴命令**（无构建产物，等价验证＝committed blob / 服务端字节 / 数据可解析）：
```
# ① 新标记在产物里（index.html 引用了 home.css、含 #progress 锚点、body.home）
curl -s http://127.0.0.1:8099/index.html | grep -cE 'assets/home\.css'; git show HEAD:index.html | grep -c 'id="progress"'   # 期望均 ≥1
# ② 关键地址都 200，dashboard.html 是跳转不是旧看板
for u in index.html dashboard.html assets/home.css; do echo -n "$u "; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8099/$u"; done; curl -s http://127.0.0.1:8099/dashboard.html | grep -c 'location.replace'   # 期望 200/200/200 与 ≥1
# ③ 数据源活着（生成时间可打印即 db up 的等价物）
curl -s http://127.0.0.1:8099/assets/dashboard.json | python -c "import json,sys;print('generated=',json.load(sys.stdin)['generated'])"   # 期望打印 2026-11-25 11:14
```
实测：① 1 / 1；② 200 200 200 与 1；③ `generated= 2026-11-25 11:14`。工作树与个人主页仓库均 clean，改动已提交（KB `8fe1e6a`，个人主页 `31f47c2`）。

### 问题清单（按严重度）
1. **[中] `renderDash` 中途抛异常 → 错误文案被隐藏、面板半渲染**：index.html:329-331 先置 `progress-empty.hidden=true`，316-319 的 catch 再往里写文案就看不见。修法：把 catch 改成先 `$('progress-empty').hidden=false; $('progress-body').hidden=true; $('kpis').hidden=true;` 再写文案。
2. **[中] `d.activity.days` 为空 → 活跃度面板空白无提示**：index.html:427 `if (act.length)` 补 else，往 `heat`/`heat-recent` 或面板里放一句「最近没有活动记录」。
3. **[低] `dl.days_ago` 为 null 时显示「null 天前」/「（就是今天）」**：index.html:342、364 守卫改为 `dl.days_ago != null && dl.days_ago > 1`，null 时走「还没有出题」或中性文案。
4. **[低] 阅读表超长书名可能撑宽**：home.css:252 `display:table` 与 264 `td.bk` 加 `overflow-wrap:anywhere`（或保留 hermes 的横向滚动），避免极端长串溢出。
5. **[低] 页脚「数据更新于」竞态**：index.html:333 与 526 两处写 `foot-upd`，以谁后到为准；建议以 `dashboard.generated` 为准、weread 只在 dashboard 缺席时补。
6. **[低/既有] `esc()` 三份**：index.html:280 / view.html:233 / kb-ui.js:26，后续可收敛到 kb-ui 全局。
7. **[信息/out-of-scope] 搜索静默失败**：kb-ui.js:127 在 `SEARCH=null` 时直接返回，输入无反馈；全站既有，本次未改。

> 备注：以上 1–2 为「不通过」的直接依据，均为数行改动、无行为面重构；修完可直接转「通过」。3–5 建议同批带上。隐私公开一项按用户明确决定，不列为缺陷。

### 修复记录（2026-11-27，审查后同一会话）

| # | 处理 | 改动位置 | 复测 |
|---|---|---|---|
| 1 | **已修** | `index.html`：`.then` 里 `try/catch` 包住 `renderDash`，新增 `showDashError()`，进入时先复位 `progress-body/kpis` 的 `hidden` 再把 `progress-empty` 显示出来 | 缺 `exams` 字段时不再 white-out，显示「试卷数字化 0 % 0 / 0 份」，无 `undefined` |
| 2 | **已修** | `index.html`：活跃度改 `if (!act.length) { ... } else { ... }`，空数据渲染「最近还没有活动记录。」并清空月份刻度与合计 | `activity.days=[]` → 该句出现，页面不空白 |
| 3 | **已修** | `index.html`：引入 `gap`（`days_ago == null → null`），两处展示与警告态都走 `gap != null` | `days_ago=null` → 显示「每日一题停在 2026-11-22 · 」，无 `null` 字样 |
| 4 | **已修** | `home.css`：`.kb-reading table.rl` 加 `table-layout:fixed`，`td/th` 加 `overflow-wrap:anywhere` | 超长书名 + 40 字符无空格作者 → `scrollWidth 1239 ≤ innerWidth 1254` |
| 5 | **已修** | `index.html`：新增 `FOOT_FROM_DASH`，`renderDash` 写 `foot-upd` 后置位；`renderReading` 只在未置位时补 | 两路先后到，「数据更新于」始终是 dashboard 的生成时间 |
| 6 | **不改** | `esc()` 三份是既有小工具重复，收敛到 kb-ui 属跨页重构，另开任务 | — |
| 7 | **out-of-scope** | 搜索索引失败静默是 `kb-ui.js` 全站既有行为，本次未触及 | — |

**复跑结果**：`node tools/check-controls.js` 6 页全过；`check_links.py` 失败 0；`probe_layout.py` 1280/375 均 `overflowX: 0`、`dup: []`；`probe_error.py` 三路 404 兜底文案齐全；`probe_edge.py` 四个边界（空活跃度 / 缺 exams / null days_ago / 超长书名）全部通过。

### 复审结论（同一会话，修复后）

**通过（附条件）**：上述 1–5 全部修复并复测通过，6–7 明确登记为不在本次范围。第 6 条（`esc()` 三份）建议另起任务收敛，不影响本次交付。


