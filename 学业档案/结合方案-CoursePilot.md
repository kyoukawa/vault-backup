---
title: CoursePilot × 带学体系 · 结合方案
type: design
updated: 2026-11-26
tags:
  - 学业档案/方案
  - 工具
cssclasses:
  - rc-home
---

↑ [[学业档案/INDEX|学业档案]] · [[知识库导航|总导航]]

# CoursePilot × 带学体系

> **结论：CoursePilot 管「知识进来」，vault 管「分数出去」。**
> 两者不合并、不双向同步、不共用一套复习节奏，只在四个点上握手。
> 强行合并的结果是——翻卡翻得很熟，卷子还是答不对，而且分不清是哪一环出的问题。

## 一、两边各管什么

| | CoursePilot | vault（study-bot / study-coach） |
|---|---|---|
| 输入 | 网课视频（B 站链接、本地录播、网盘） | 真题试卷（PDF → 题集）、用户现场作答 |
| 产出 | 字幕、章节、笔记、脑图、课件 OCR、AI 练习题、FSRS 复习卡、费曼复述 | 错题（六类病灶）、复习队列（D+1/D+3/D+7）、短板雷达、周计划、语料库 |
| 判据 | 「这个知识点记住了吗」——记忆维度 | 「考场上这一分拿到了吗」——采分点、表达、计算维度 |
| 时间尺度 | 看课那几周 | 整个学期 + 大考复盘 |
| 权威性 | 它的 SQLite 是黑盒，重装即丢 | vault 是 git 仓库，跨设备、可搜索、有历史 |

一句话：**CoursePilot 是进货，vault 是出货。** 库存不等于营业额。

## 二、四条结合线

### 线 1：短板 → B 站课 → 结构化笔记（挑科目，别全铺）

短板雷达（[[学业档案/学习日志|学习日志]]）现在是：语文细读、数学「难题无进账」。

**值得上网课的：**

- 数学专题课（圆锥曲线、导数压轴套路）——「会做但难题不进球」正是缺套路，网课给的就是套路
- 文言文实词、古诗鉴赏、背诵篇目串讲——当前带学正在推《赤壁赋》，B 站这类课密度最高
- 化学/英语：强项区，**不加时**，看了也是浪费

**不值得的：** 语文现代文选择题的「细读」。这个东西靠真题讲评 + 当场判分，网课讲的是别人的阅读习惯，迁移率极低。别为了用上工具硬排。

流程：短板 → B 站搜课 → CoursePilot 导入（贴链接即可，它自己下载 + 本地 SenseVoice 转写）→ 出笔记和章节 → **挑一节回带学验证**，答不出来就是没吸收。

### 线 2：错题考点 → 拍题找讲解（回看那几分钟）

CoursePilot 有个「拍题找讲解」：贴一张题图或一段题干，它列出这门课里讲到它的那几段，可以依次播放。

用在错题回炉上很省：[[学业档案/带学/错题|错题]] 里每一条都写了考点（比如「a²+b²−c² ≡ 2ab·cosC」），拿这个考点去库里搜，直接跳回视频那一秒，比重新翻课快得多。

前提是这门课已经导入。所以线 1 导入什么课，决定了线 2 能不能用。

### 线 3：笔记镜像到 vault（单向，带哈希）

CoursePilot 导出的笔记 Markdown 落到：

```
学业档案/网课/<课程名>/<讲次>.md
```

front-matter 带 `source: coursepilot` / `video_id` / `source_hash` / `exported_at`。

**只做单向镜像，vault 里不要改这些文件。** 理由：vault 是唯一能被 `rg` 搜到、被 obsidian-git 备份、被 dashboard 统计的地方；CoursePilot 的库只活在它自己那台机器上。但反过来写回去，就会和 CoursePilot 的笔记版本历史（它自己有 50 版留底）打架，两边都不知道谁是真相。

重跑时比 `source_hash`，一样就跳过。

### 线 4：记忆层 vs 答题层（**分层，不合并**）

这条是整份方案的承重墙。

| | CoursePilot 复习卡 | vault 复习队列 |
|---|---|---|
| 存什么 | 一个知识点（正面问题 / 背面答案） | 一个**采分点**（答题时漏掉的那一点） |
| 谁排期 | FSRS-4.5，天级，自动 | study-coach 手写 D+1 / D+3 / D+7 |
| 算过关 | 翻卡时自己给自己打分 | 换一份卷子的同考点题，**答到了**才算 |
| 失败长什么样 | 忘了 | 答了，但没落到采分点上 |

两张表**不要合并**，也不要互相导入。理由：合并之后，「卡都翻绿了」会被当成「这科没问题」，而这种错觉正是 [[学业档案/2026/2026-11-期中考（赋分前）|期中]] 暴露的问题——数学 0.04，分数不低，位置普通，说明会做的做完了、难题没进账。

**唯一的联动，一条：**

> 同一张卡在 CoursePilot 里连续答错 ≥ 2 次
> → 在 vault 里记一条「知识缺口候选」，**不直接写进错题.md**
> → 下次带学时，优先出一道这个考点的**真题**（题源走试卷库，不走 AI 出题）
> → 带学现场答对了，才算补上，进复习队列

符合「一次失误不下结论」的既有判据。AI 的卡错两次只说明「可能没记住」，不说明「考场上会丢分」。

## 三、明确不做

1. **不用 CoursePilot 的 AI 练习题判分，也不进错题统计。** AI 出题没有真实评分标准，判分口径会和 study-coach 的采分点拆解直接打架。它的题只做「上课前自测」，判断这节课值不值得看。
2. **不双向同步。** 不往它的 `courseai.db` 写任何东西，只读。
3. **不合并复习节奏。** 见线 4。
4. **不替换 `video-notes` 技能。** 单条视频要个逐字稿 + 一篇笔记，`video-notes` 更快、不占库。CoursePilot 是「跟一整套课、要出题要卡」才用。
5. **不给语文现代文细读排网课。** 见线 1。

## 四、技术接线

### 4.1 数据库位置

Tauri 的 `app_data_dir()`，Windows 上是：

```
C:\Users\chuan\AppData\Roaming\dev.courseai.app\courseai.db
```

（`identifier` 是 `dev.courseai.app`，产品名 `course-ai`。装上后跑一次
`Get-ChildItem $env:APPDATA -Recurse -Filter courseai.db -Depth 3` 确认。）

### 4.2 只读桥接

**别在 app 运行时直接读。** 库开了 WAL，`sqlite3` 只读连接可能读到半写状态。稳妥做法是每次先复制一份到 `.tmp/` 再读：

```python
import shutil, sqlite3, tempfile, os
src = os.path.expandvars(r"%APPDATA%\dev.courseai.app\courseai.db")
tmp = os.path.join(tempfile.mkdtemp(), "cp.db")
shutil.copy2(src, tmp)
for ext in ("-wal", "-shm"):           # WAL 也要一起拷，否则看不到最新数据
    if os.path.exists(src + ext):
        shutil.copy2(src + ext, tmp + ext)
con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
```

### 4.3 要用到的表（已验证的实际 schema）

| 表 | 关键字段 | 用途 |
|---|---|---|
| `courses` | `id, name, root_path, deleted_at` | 课程清单 |
| `videos` | `id, course_id, title, source_uri, order_index, folder_id, deleted_at` | 讲次；`order_index` 是教材顺序 |
| `chapters` | `video_id, title, start_ms, end_ms` | 章节，用于笔记分节 |
| `transcripts` | `video_id, segment_idx, start_ms, end_ms, text` | 字幕 |
| `notes` | `video_id, content_md, ai_generated_at, user_edited_at` | 笔记（`content_md` 是 Markdown，`content_json` 是富文本，用前者） |
| `summaries` | `video_id, content_md` | 整讲概览 |
| `mindmaps` | `video_id, markmap_md` | 脑图大纲 |
| `quizzes` | `video_id, questions_json, generated_at` | 题，JSON 数组；每项 `{type, stem, options, answer, explanation, style}`，`type` ∈ `choice/judge/short/correct/...` |
| `cards` | `id, video_id, course_id, front, back, source_ms` | 复习卡；`source_ms` 是回看时间戳 |
| `card_schedule` | `card_id, due_at, reps, lapses, stability, difficulty` | FSRS 排期（`ease/interval_days` 是旧 SM-2 遗留，别用） |
| `study_events` | `kind, video_id, ts, meta_json` | 流水；`kind='review'` 的 `meta_json` 里有评分 |
| `concepts` | `course_id, name` | 知识点，配合 `concept_occurrences` 定位到视频秒数 |

**到期卡查询：**

```sql
SELECT c.front, c.back, c.source_ms, v.title, co.name, s.due_at, s.lapses
FROM cards c
JOIN card_schedule s ON s.card_id = c.id
JOIN videos v ON v.id = c.video_id
JOIN courses co ON co.id = c.course_id
WHERE s.due_at <= ? AND (co.deleted_at IS NULL)
ORDER BY s.due_at;
```

**连错的卡**（线 4 的触发器）：`card_schedule.lapses >= 2`，比解析 `study_events.meta_json` 简单可靠。

### 4.4 镜像出来的笔记长什么样

```markdown
---
title: <讲次标题>
source: coursepilot
video_id: <uuid>
course: <课程名>
source_hash: <sha256(content_md)>
exported_at: 2026-11-26T10:00
---

↑ [[学业档案/网课/<课程名>/INDEX|课程名]]

## 概览
<summaries.content_md>

## 章节笔记
<notes.content_md>

## 脑图
<mindmaps.markmap_md 原样嵌进 ```markmap 代码块>
```

字幕（`transcripts`）**默认不镜像**——几千行，会把 `rg` 检索淹掉。真要查原话，回 CoursePilot 里搜。

### 4.5 桥接脚本的形状（将来写，约 150 行）

```
tools/coursepilot_sync.py
  --courses                列出库里的课程和讲次，先看再决定导什么
  --export <课程名>         把该课程笔记镜像到 学业档案/网课/<课程名>/
  --weak-cards [--days 0]   列出到期卡与连错 ≥2 的卡（只打印，不写 vault）
  --dry-run                默认就是 dry-run，要落盘必须显式 --write
```

放在 `tools/` 下，与 `dashboard.py` 同级，同样只用标准库（`sqlite3` / `shutil` / `hashlib`）。
**不改 vault 里任何现有文件的判分逻辑**，只新增目录和一份候选清单。

## 五、落地顺序

1. **装 Windows 版 v0.4.2**（走代理 `127.0.0.1:7897`，`CoursePilot_0.4.2_windows_x64-setup.exe`，133MB）。
2. **大模型填 DeepSeek**：设置 → 大模型 → OpenAI 兼容，base `https://api.deepseek.com`，key 用现有的。省一笔钱。
3. **导一门课试跑**：一门数学专题课，3–5 讲就够。看它出的笔记、章节、题质量如何。
4. **只看不写**：跑 `--weak-cards` 和 `--courses`，先看数据对不对，再决定要不要写 `--export`。
5. **写线 4 的联动**：`lapses >= 2` → 候选清单 → 带学优先出真题。这一条真正改善分数，但可以最后做。

## 六、坑（先记在这，装的时候会撞上）

| 坑 | 说明 |
|---|---|
| **Windows 只到 v0.4.2** | v0.4.3（2026-11-25 发布）只出了 macOS aarch64 和 Android 包。Windows 最新是 v0.4.2。所以 v0.4.3 的翻卡复习、课桌主页、知识点收集册**在 Windows 上暂时没有**，只有 0.4.2 的能力：脚本化的 FSRS 排期 + 出题 + 笔记 |
| **DeepSeek 不吃图** | 课件 OCR 出来的文字喂给它没问题；但凡是要「AI 看 PPT 截图」的环节，DeepSeek 做不了。好在它的本地 PaddleOCR（PP-OCRv6，30MB）先转文字，所以不装视觉模型也能跑 |
| **首次要下模型** | SenseVoice 240MB；Qwen3-ASR 940MB；PaddleOCR 30MB。走代理，别让它直连 |
| **B 站字幕** | 未登录情况下 `x/player/v2` 返回空字幕数组（CLAUDE.md 记过）。CoursePilot 是自己下音频 + 本地转写，正好绕开，别指望它直接拉字幕 |
| **视频占盘** | 一门课几个 G。可以设「不下载、在线看」，但那样用不了本地转写 |
| **别和 obsidian-git 抢目录** | CoursePilot 的多设备同步走 WebDAV，不要指到 `Documents\知识库` 里，会和 git 打架 |
| **AI 题的质量** | 它的题是「考讲稿」的，不是「考考纲」的。判断标准：题干里出现讲稿原话的比例越高，越只适合做课后自测 |

## 关联

- [[学业档案/INDEX|← 学业档案]]
- [[学业档案/学习日志|学习日志]]（短板雷达，线 1 的起点）
- [[学业档案/带学/错题|错题]] · [[学业档案/带学/复习队列|复习队列]]（线 4 的落点）
- [[学业档案/学习计划|学习计划]]
