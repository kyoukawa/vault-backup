---
title: CoursePilot 和带学体系怎么配合
type: design
updated: 2026-11-26
tags:
  - 学业档案/方案
  - 工具
cssclasses:
  - rc-home
---

↑ [[学业档案/INDEX|学业档案]] · [[知识库导航|总导航]]

# CoursePilot 和带学体系怎么配合

> 看网课用一个工具，做题判分用另一套。这份文档说清两边各自管什么，哪几个地方要连起来。

## 一、两边各自管什么

| | CoursePilot | vault（study-bot / study-coach） |
|---|---|---|
| 你要给什么 | 网课视频：B 站链接、下载好的录播、网盘里的课 | 真题试卷（PDF 转成题集）、现场作答 |
| 会生成什么 | 字幕、章节、笔记、脑图、课件文字、练习题、复习卡、复述记录 | 错题（按六类原因记）、复习队列（D+1 / D+3 / D+7）、短板雷达、周计划、语料库 |
| 怎么算学会 | 这个知识点记住了没有 | 考场上这一分拿到了没有 |
| 用多久 | 看课的那几周 | 整个学期，加上每次大考复盘 |
| 数据存在哪 | 本机的一个数据库文件，重装软件就没了 | git 仓库，多台设备都能看，能搜，有历史 |

CoursePilot 认为翻卡时答对了，就算学会。vault 认为换一份卷子还能做出同类题，才算学会。两个标准不一样：混着用，就分不清丢的分是没记住，还是做不出来。

## 二、四个连接点

### 1. 先定科目，再去找课

短板雷达（[[学业档案/学习日志|学习日志]]）现在写的是语文细读和数学「难题没进账」。

值得找课的科目：

- 数学专题课，圆锥曲线、导数压轴这一类。难题拿不到分，多半是手里没有套路，网课给的正好是套路。
- 文言文实词、古诗鉴赏、背诵篇目串讲。带学正在推《赤壁赋》，B 站上这类内容最多。

不值得的科目：

- 语文现代文选择题的细读。网课讲的是讲课人自己的阅读习惯，学过来要很久；真题讲评加当场判分更直接。不要为了用上工具硬排一门课。
- 化学和英语。标准分现在是 0.87 和 1.13（0 分就是年级平均），再加时间也是浪费。

做法：先按短板定科目，再去 B 站搜课，把链接贴进 CoursePilot。它会自己下载视频，用本地的语音转写模型 SenseVoice 生成字幕，再出笔记和章节。然后挑一节回到带学里验证。答不出来，说明这一节没吸收进去。

### 2. 错题里的考点，直接跳回视频那一段

CoursePilot 有个「拍题找讲解」：贴一张题图或一段题干，它会列出这门课里讲到这道题的几段，可以依次播放。

用在错题回炉上省时间。[[学业档案/带学/错题|错题]] 里每一条都写了考点，比如「a²+b²−c² ≡ 2ab·cosC」。拿这个考点去库里搜，直接跳回讲它的那一秒，比重新翻课快很多。

前提是那门课已经导进库里。所以第 1 条导了什么课，决定这一条能不能用上。

### 3. 笔记只往 vault 里放一份

CoursePilot 导出的笔记放在：

```
学业档案/网课/<课程名>/<讲次>.md
```

文件开头记着来源、视频编号、内容指纹和导出时间。

只往一个方向走。vault 能用 `rg` 搜、有 obsidian-git 备份、有 dashboard 统计；CoursePilot 的数据只在装了它的那台机器上。不要反过来往它的库里写：它自己有笔记版本历史（最多留 50 版），两边同时改就分不清哪份是准的。

再导一次时，先比内容指纹（`source_hash`），一样就跳过。

### 4. 复习卡和复习队列分开记

| | CoursePilot 复习卡 | vault 复习队列 |
|---|---|---|
| 一条记什么 | 一个知识点：正面问题，背面答案 | 一个得分点：答题时漏掉的那一点 |
| 谁安排时间 | 按 FSRS-4.5 算法自动排，每天给你一批到期的卡 | study-coach 手写 D+1 / D+3 / D+7 |
| 怎么算过 | 翻卡的时候自己给自己打分 | 换一份卷子的同类题，答到了才算 |
| 没过的样子 | 想不起来 | 答了，但没答到点上 |

两张表不合并，也不互相导入。合并以后，卡片全翻对了，就会被当成这科没问题。期中就是栽在这个误会上的：[[学业档案/2026/2026-11-期中考（赋分前）|数学标准分 0.04]]，分数不低，位置普通，会做的都做完了，难题基本没进账。

只有一处要把两边连起来：

> 同一张卡连着错两次以上
> → 记一条「知识缺口候选」，先不写进错题.md
> → 下次带学，从这个考点出一道真题（用试卷库里的题，不用它出的题）
> → 现场答对，才算补上，再进复习队列

这样才符合「一次失误不下结论」的规矩。卡错两次只能说明可能没记住，不能说明考场上会丢分。

## 三、不做的几件事

1. 不用 CoursePilot 的练习题判分，也不进错题统计。它出的题没有真实评分标准，判分标准会和 study-coach 拆得分点直接冲突。它的题只用来在上课前自测，判断这节课值不值得看。
2. 不往它的数据库里写任何东西，只读。
3. 不合并两套复习时间表，原因见第二节第 4 条。
4. 不替换 `video-notes` 技能。单条视频要一份逐字稿加一篇笔记，`video-notes` 更快，也不占地方。CoursePilot 适合跟一整套课、需要出题和复习卡的时候用。
5. 不给语文现代文细读排网课，原因见第二节第 1 条。

## 四、技术上怎么连

### 4.1 数据文件在哪

Tauri 应用的数据目录，Windows 上是：

```
C:\Users\chuan\AppData\Roaming\dev.courseai.app\courseai.db
```

装上以后跑一次 `Get-ChildItem $env:APPDATA -Recurse -Filter courseai.db -Depth 3` 确认路径。

### 4.2 读之前先复制一份

不要在软件运行的时候直接读。它会边写边存，只读连接可能读到写了一半的内容。先复制到 `.tmp/` 再读：

```python
import shutil, sqlite3, tempfile, os
src = os.path.expandvars(r"%APPDATA%\dev.courseai.app\courseai.db")
tmp = os.path.join(tempfile.mkdtemp(), "cp.db")
shutil.copy2(src, tmp)
for ext in ("-wal", "-shm"):           # 随库一起写的两个文件也要拷，不然看不到最新内容
    if os.path.exists(src + ext):
        shutil.copy2(src + ext, tmp + ext)
con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
```

### 4.3 会用到的几张表

下面是实际字段，不是猜的。

| 表 | 主要字段 | 用途 |
|---|---|---|
| `courses` | `id, name, root_path, deleted_at` | 课程清单 |
| `videos` | `id, course_id, title, source_uri, order_index, folder_id, deleted_at` | 每一讲；`order_index` 是课程里的顺序 |
| `chapters` | `video_id, title, start_ms, end_ms` | 章节，用来给笔记分节 |
| `transcripts` | `video_id, segment_idx, start_ms, end_ms, text` | 字幕 |
| `notes` | `video_id, content_md, ai_generated_at, user_edited_at` | 笔记，用 `content_md`；`content_json` 是带格式的富文本 |
| `summaries` | `video_id, content_md` | 整讲概览 |
| `mindmaps` | `video_id, markmap_md` | 脑图大纲 |
| `quizzes` | `video_id, questions_json, generated_at` | 题目，JSON 数组，每项含 `type`、`stem`、`options`、`answer`、`explanation`、`style` |
| `cards` | `id, video_id, course_id, front, back, source_ms` | 复习卡；`source_ms` 是回看时的时间点 |
| `card_schedule` | `card_id, due_at, reps, lapses, stability, difficulty` | FSRS 排期；`ease` 和 `interval_days` 是旧办法留下的，不要用 |
| `study_events` | `kind, video_id, ts, meta_json` | 学习记录；`kind='review'` 的记录里 `meta_json` 存着评分 |
| `concepts` | `course_id, name` | 知识点，配合 `concept_occurrences` 定位到秒 |

查今天该复习哪些卡：

```sql
SELECT c.front, c.back, c.source_ms, v.title, co.name, s.due_at, s.lapses
FROM cards c
JOIN card_schedule s ON s.card_id = c.id
JOIN videos v ON v.id = c.video_id
JOIN courses co ON co.id = c.course_id
WHERE s.due_at <= ? AND (co.deleted_at IS NULL)
ORDER BY s.due_at;
```

第 4 条要的连错卡，用 `card_schedule.lapses >= 2` 就够，不必去解析 `study_events.meta_json`。

### 4.4 导出来的笔记长什么样

```markdown
---
title: <讲次标题>
source: coursepilot
video_id: <uuid>
course: <课程名>
source_hash: <content_md 的 sha256>
exported_at: 2026-11-26T10:00
---

↑ [[学业档案/网课/<课程名>/INDEX|课程名]]

## 概览
<summaries.content_md>

## 章节笔记
<notes.content_md>

## 脑图
<mindmaps.markmap_md 原样放进 ```markmap 代码块>
```

字幕默认不导出。几千行下去，`rg` 搜什么东西都会被这些字幕挤满，要查原话回 CoursePilot 里搜。

### 4.5 脚本大概什么样

将来写，一百五十行左右。

```
tools/coursepilot_sync.py
  --courses                列出库里的课程和讲次，先看再决定导什么
  --export <课程名>         把这门课的笔记导出到 学业档案/网课/<课程名>/
  --weak-cards [--days 0]   列出到期的卡和连错两次以上的卡，只打印，不写 vault
  --dry-run                默认就是 dry-run，真要写入必须显式加 --write
```

放在 `tools/` 下，和 `dashboard.py` 放在一起，同样只用标准库（`sqlite3`、`shutil`、`hashlib`）。不改 vault 里任何现有文件的判分逻辑，只新增一个目录和一份候选清单。

## 五、先做什么后做什么

1. 装 Windows 版 v0.4.2。走代理 `127.0.0.1:7897`，文件是 `CoursePilot_0.4.2_windows_x64-setup.exe`，133MB。
2. 大模型填 DeepSeek。设置 → 大模型 → OpenAI 兼容，地址填 `https://api.deepseek.com`，key 用现有的那个。
3. 导一门课试试。一门数学专题课，三到五讲就够，看看它出的笔记、章节、题怎么样。
4. 先只看不写。跑 `--weak-cards` 和 `--courses`，数据对了再决定要不要开 `--export`。
5. 最后把两边的复习记录连起来（见第二节第 4 条）：`lapses >= 2` 出候选清单，带学优先出真题。这一条对分数影响最大，但可以放在最后做。

## 六、装的时候会遇到的几个问题

| 问题 | 说明 |
|---|---|
| Windows 只到 v0.4.2 | v0.4.3 是 2026-11-25 发的，只出了 macOS（Apple 芯片）和 Android 版本。所以 v0.4.3 的翻卡复习、课桌主页、知识点收集册在 Windows 上暂时用不了。0.4.2 能做的是：按天排复习卡、出题、出笔记 |
| DeepSeek 看不了图片 | 课件识别出来的文字发给它没问题，但让 AI 直接看 PPT 截图，做不到。好在本地 PaddleOCR（PP-OCRv6，30MB）会先把图片转成文字，不装视觉模型也能把课件读下来 |
| 第一次要下模型 | SenseVoice 240MB，Qwen3-ASR 940MB，PaddleOCR 30MB。走代理下载，别让它直连 |
| B 站字幕拿不到 | 没登录时 B 站只返回空字幕，这一点 CLAUDE.md 里记过。CoursePilot 是自己下音频再本地转写，正好绕开，不要指望它直接拉字幕 |
| 视频占空间 | 一门课几个 G。可以设成不下载、在线看，但那样用不了本地转写 |
| 不要和 obsidian-git 用同一个目录 | CoursePilot 的多设备同步走 WebDAV，别指到 `Documents\知识库` 里，会和 git 冲突 |
| 它出的题质量一般 | 它考的是讲稿内容，不是考纲。题干里讲稿原话越多，就越只能当课后自测，代替不了真题 |

## 关联

- [[学业档案/INDEX|← 学业档案]]
- [[学业档案/学习日志|学习日志]]（短板雷达，第 1 条的起点）
- [[学业档案/带学/错题|错题]] · [[学业档案/带学/复习队列|复习队列]]（第 4 条的落点）
- [[学业档案/学习计划|学习计划]]
