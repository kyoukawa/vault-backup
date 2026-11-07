<!-- 由 minis-cloud pull 生成于 2026-11-07 10:52:48，来源 https://agent.gxwtf.cn -->

# GLOBAL（云端权威）
# 全局记忆

> **所有工作前先读本文件；每次完工后把进展写进「进展记录」。**
> 目的：不同会话之间不重复劳动、不踩同一个坑。
> 分工：本文件上半部分是**可复用的知识**（怎么做事），下半是**进展记录**（做到哪了）。
> 最后更新：2026-11-01

---

# 一、协作铁律

1. **动手前先同步**：读本文件 → `git pull` → `git log --oneline -5` → `git status`，再 `find` 本地是否已有同名实现。**别凭自己刚写的东西就开工。**
2. **本地工作区不是权威，远程才是。** 本地缺文件或比远程短，说明本地是旧的——先 `git pull`，或重新 clone 到临时目录对比。
3. **功能更新必须讲清楚 + push**：每次改完功能，说清做了什么、为什么、怎么验证的，然后推 GitHub，不用再问。
4. **完工后必须**：说清改了什么 → 推 GitHub（代码项目）→ 追加本文件「进展记录」→ **跑 `memsync.sh` 同步三份副本**。
   ```sh
   sh /var/minis/workspace/reading-collector/memsync.sh
   ```
5. **聊天记录不跨会话共享**，但文件系统共享。状态一律落到文件里，不要指望别的情境记得。
6. **反复踩同一个坑是失职**：修好一个坑，同时写进本文件或对应 SKILL.md。

### 查重办法
```bash
find / -maxdepth 5 -name "<关键文件名>" 2>/dev/null
minis-sessions-cli search --keywords "<主题>"
```

> ⚠️ **多个会话会同时改同一仓库**。2026-11-01 实测：本地改完准备推时，远端已有别人 3 个提交
> （其中 `scripts/notion.py` 是 314 行完整实现，比当时的简版强得多）。
> **动代码前 `git pull`，推之前再 `git fetch` 看一次。** 已存在的功能只补差额，改写别人实现前先问老大。

---

# 二、活跃项目

| 项目 | 位置 | 远程 | 状态 |
|---|---|---|---|
| reading-collector | `/var/minis/workspace/reading-collector/` | github.com/kyoukawa/reading-collector | 运行中，手动触发 |
| **agent-system** | `/var/minis/workspace/agent-system/` | github.com/kyoukawa/agent-system（**公开**，2026-11-02 推仓） | 多 Agent 路由层 |
| 英语语料库 | Obsidian vault → `语料库/` | — | 长期维护 |
| 语文语料库 | Obsidian vault → `语文语料库/` | — | 长期维护 |

## agent-system（多 Agent 架构）

参照 Obsidian 笔记《Super-agent 设计探索》实现的双层架构。

**框架仓，不含业务代码。** 与 `reading-collector` 是「框架 + 插件」关系：
框架决定谁干活，业务决定活怎么干，靠 `workers/*.json` 松耦合连接。
架构说明见 `agent-system/docs/ARCHITECTURE.md`。

**技能副本三处**（运行时 `/var/minis/skills/`、框架仓 `skills/`、业务仓 `skills/`），
以运行时为真相，用 `sh agent-system/scripts/skillsync.sh` 同步或 `--check` 核对。

| 模块 | 位置 | 作用 |
|---|---|---|
| Router | `router/router.py` | 路由分派，**不亲自执行** |
| Watchdog | `router/watchdog.py` | 检测僵尸任务 / 产出缺失 |
| 事件层 | `triggers/events.py` | Fast/Slow Path 过滤 + Inline&Spill |
| 状态层 | `state/state.py` | 存算分离 + 链式召回 |

**五个 Worker**：`workers/*.json` 声明能力（triggers/sources/prompt）。
`reading-collector`、`video-notes`、`github-maintainer`、`corpus-en`（英语语料库）、`corpus-zh`（语文语料库）。
**统一入口技能：`agent-router`**。**架构维护：`system-steward`（系统管家）**。

**管家工具**（`router/` 下）：
- `validate.py` 校验 Worker 定义：字段齐全、技能文件存在、`name` 一致、触发词冲突
- `scaffold.py <name> --purpose ... --triggers ...` 生成新 Worker 骨架

### ⚠️ 双窗口分工（2026-11-02 用户定）

用户已单独开了一个 **router 窗口**负责日常调度，**本机其他会话只负责管家职责**。

| 窗口 | 负责 | 不要做 |
|---|---|---|
| **router 窗口** | 日常干活：整理待办、转视频、语料入库、推代码、复习 | 不改 Worker 定义 |
| **其他窗口（管家）** | 加/改 Worker、`validate.py`、`watchdog.py`、架构演进 | **不替 Worker 干具体的活** |

判定：收到「整理收集」「转个视频」「推上去」这类请求 → 告诉用户去 router 窗口，
或只做路由判断不做执行。收到「加个 agent」「改 X 的行为」「体检」→ 才是管家范围。

**加 Worker 的标准流程**：查重 → `scaffold.py` 生成 → 写实 SKILL.md → `validate.py` → `router.py --text` 试路由。
**元角色**（`agent-router`、`system-steward`、`skill-creator`、`guided-learning`）不参与路由，不需要 Worker 定义。

**两个语料库判据不同，不能混用**：
- 英语：What→How→Effect→Value，重「少而精、可迁移、可调用」
- 语文：老师六维（概念界定→段首句→机制→论据→思路→深化），只收「我的原句/老师的机制/避坑」三类
- 两者都是**选稿制**（AI 出候选、用户打勾），复习都是**手动触发、每次 3 条**

关键约定：同一 `thread` 的第二条事件走**直通**，不再重新判断归属；
未归属事件必须报给用户，不许硬接；**多 Worker 同分时报歧义，让人来选**。

## Obsidian vault

根目录：`/var/minis/mounts/知识库`
**根目录只允许文件夹，不放零散文件。** 现有：`语料库/`、`语文语料库/`、`阅读收集/`

阅读收集结构：`首页.md`（自动重建的索引）+ `<年>/<日期>-<标题>.md` + `附件/`

## reading-collector（开源）

- 用途：待办里的链接 → Obsidian 笔记 → 勾完成 → 可选镜像 Notion
- 脚本：`scripts/{config,inbox,archive,notion,transcribe}.py` + `install.sh`
- Notion 镜像是独立幂等模块，URL→page_id 记在 `config/notion-map.json`
- 已装技能：`reading-collector`、`video-notes`、`github-maintainer`

**用户确认过的规则：**
- 入口 = 青蛙todo 分组「阅读收集」，**标题写题目，正文放链接**
- **Obsidian 是权威，Notion 是从属镜像**（失败不阻塞、不回滚、不重试）
- 顺序固定：写笔记 → 重建索引 → **勾完成 → 镜像**。**笔记没落盘就不勾**
- 手动触发，**无定时任务**
- **异地备份**：`sh reading-collector/scripts/vaultbackup.sh` → 私有仓 `kyoukawa/vault-backup`，
  每天 23:30 自动跑。`--restore <目录>` 可恢复。**vault 为空或不存在时会拒绝执行，不会覆盖备份。**
  **备份内容**：三个知识库目录 + `.obsidian/snippets/` + `_minis/`（MCP 配置、OAuth 令牌、memory、skills），
  明文保存。**丢了 MCP 配置或技能，从 `_minis/` 恢复，不用重新授权。**
- **Obsidian 是唯一权威，Notion 只负责网页浏览**；Notion 堆放区已废弃

---

# 三、环境事实（Minis / iSH / Alpine）

| 项 | 事实 |
|---|---|
| Python | 系统 `python3` 3.12，`/usr/bin/python3` |
| Shell | 默认 BusyBox ash，无 bash 特性保证 |
| 包管理 | `apk add py3-<name>` 优先；纯 Python 才用 `pip` |
| **`/var/minis` 不支持符号链接** | venv 不能建在里面，放 `/opt` |
| **无 `/dev/fd`** | 进程替换 `<(...)` 不可用，走管道或临时文件 |
| **`chmod` 无效** | 设执行位用 `git update-index --chmod=+x` |
| 磁盘 | 约 30G 可用，注意大文件 |
| **Minis 定时任务不持久** | App 重启会丢；当前 reading-collector 全手动触发 |

**依赖**：`yt-dlp`、`ffmpeg`、`ffprobe`、`apple-speech`、系统 `python3` 都在 PATH。**不建 venv、不 pip install。**

`apk` 报锁错误：`kill -9 $(pgrep apk); rm -f /lib/apk/db/lock`

## 一键恢复清单（workspace 被清空时照这个做）

**事故记录**：2026-11-02 11:38，iOS 容器重置把整个 `/var/minis/workspace/` 清空（agent-system、reading-collector 全丢），
`/var/minis/attachments`、`offloads`、`browser` 也一起新建为空目录。`skills/`、`memory/`、`mounts/`、`shared/` 幸存。

**结论：`/var/minis/workspace` 不是持久存储，任何代码必须推远程。**

### 第一步：诊断
```sh
ls -la /var/minis/workspace/          # 空 = 确认被清
ls /tmp/rc-remote 2>/dev/null          # /tmp 里可能还有上次的残留副本（不保证）
```

### 第二步：克隆两个仓库
```sh
cd /var/minis/workspace
git clone https://github.com/kyoukawa/reading-collector.git
git clone https://github.com/kyoukawa/agent-system.git
```
凭据在 `/root/.config/reading-collector/git-credentials`（通常能幸存；丢了从 `/var/minis/shared/.credentials/` 拷回）。

### 第三步：补 reading-collector 的运行时配置（**这两个文件不在仓库里**，必须手写）
- `config/config.toml`：vault path = `/var/minis/mounts/知识库`，folder = `阅读收集`，group_by_year = true，index = `首页.md`，todo.category = `阅读收集`，todo.server = `Todo`
- `config/notion-map.json`：URL → page_id 映射。丢了不影响功能，只是「📇 索引」会漏掉老页面。
  补救：`notion.py list` 拿现网页面 → 用笔记 front-matter 的 `url:` 做 key 补录 → `notion.py rebuild-index`。

### 第四步：设 `core.fileMode false`
```sh
cd /var/minis/workspace/reading-collector && git config core.fileMode false
```
iSH 的 chmod 无效，不关掉它 `scripts/install.sh` 永远显示为已修改。

### 第五步：验证
```sh
cd /var/minis/workspace/agent-system && python3 tests/selftest.py && python3 router/validate.py
cd /var/minis/workspace/reading-collector && python3 scripts/notion.py check
```

### 不清空的部分（不用恢复）
`skills/`（技能正文）、`memory/`（本文件 + daily log）、`mounts/`（Obsidian vault，真数据在这）、`shared/`、`/root/.config/reading-collector/`（凭据）
—— 但也别全指望，`/root` 重启会被清。

---

## 服务器 SSH（已配置免密，所有 agent 可用）

```bash
ssh gx            # = gxwtf@39.105.54.184 -p 6000，密钥 ~/.ssh/id_ed25519
ssh reading       # 同一个主机，别名而已
```

- 别名写在 `~/.ssh/config`，密钥由 minis 生成并已加入服务器 `authorized_keys`
- **无需密码、无需授权**；`ssh gx '<命令>'` 或 `scp -P 6000 ... gxwtf@39.105.54.184:~/`
- **sudo 已配置受限免密**（`/etc/sudoers.d/gxwtf-nopasswd`），可直接执行：
  `systemctl {start,stop,restart,status,is-active,enable,disable,daemon-reload} gx*`、
  `journalctl`、`gxwtf-systemctl`、`nginx -t` / `nginx -s reload`、
  `cp|install *.service /etc/systemd/system/`
- **其余 root 操作（apt/pnpm 全局安装/改 nginx 配置）仍需密码**，遇到就停下来问用户
- 常用：`gxreading` / `gxreading-worker` / `gxwriting` / `gxexercise` / `gxaccount`；
  站点目录 `~/gxwtf_*`，库名 `gxwtf_*`

# 四、GitHub 免密推送（已配置，不要再授权）

| 用途 | 路径 |
|---|---|
| git 凭据 | `/root/.config/reading-collector/git-credentials` |
| 裸 token | `/root/.config/reading-collector/github_token` |
| 备份 | `/var/minis/shared/.credentials/` |

- 全局 `credential.helper = store --file=/root/.config/reading-collector/git-credentials`
- **remote URL 里不放 token**
- **绝不 `echo`/`cat` 这些文件内容**，只用 `T=$(cat 路径)`
- 提交必须带 `-c commit.gpgsign=false`，否则卡住；无 TTY 时再加 `-c core.editor=true`
- 推送用 `git push -u origin HEAD`，别写死 `master`
- 账号：`kyoukawa`

**GitHub MCP 走不通**：`clientId` 为空 → 设置页 Authorize 按钮是灰的。GitHub **不支持动态客户端注册**。
只能走 device flow（VS Code 公开 id `01ab8ac9400c4e429b23`），流程见 `github-maintainer` 技能。

---

# 五、技术坑

### 语音识别
- **`ctranslate2` 只有 glibc 版，无 musl** → faster-whisper 在 Alpine 上导入即**段错误**；
  它的 `.so` 被 dlopen 后还会让同进程后续 `import av` 也崩。强制装 / 预加载 / gcompat / 换 libgomp 全试过都不行。
  **结论：iSH 上不要碰 ctranslate2，用 `apple-speech`。**
- **并发会限流**：6 路并发时 61 片只成功 1 片。必须**串行 + 间隔 0.4s + 重试 4 次**
- 识别语言必须与原声一致（`en-US` / `zh-CN`），**选错是乱码不是效果差**
- `apple-speech -q` 返回 `{"segments":[{"substring":…}]}`，拼 `substring` 不是 `text`

### 青蛙todo MCP
- `content` 是 **Quill Delta 富文本**，链接在 `attributes.link` 里，不能只靠正则
- 建条目必须用 **`title`** 字段，`content` 会被强制置空
- 删除要先 `frogtodo_preview_changes` 拿 previewId，再 `frogtodo_apply_changes`

### Notion MCP
- `notion-create-pages` 的 pages 项 = `{"properties":{"title":…},"content":…}`
- `notion-update-page` 的 `replace_content` 需要 `allow_deleting_content: true`
- `notion-delete-pages` 的 `page_ids` 必须是 **UUID**，且需 `user_confirmed: true`
- 父页面「有价值内容收集」`40209d7f-d7ec-8175-9c6a-d69d5f097cce`

### 内容抓取
- `mp.weixin.qq.com` 可直接抓，正文在 `div#js_content`；偶发验证墙需浏览器兜底
- B 站 `x/player/v2` 与 `x/player/wbi/v2` **都要登录**才返回字幕列表，未登录返回空数组 → 走音频转写
- `.pages` 的正文只在 `preview.jpg` 里，`Document.iwa` 抽不出文字

---

# 六、写作/内容偏好（老大）

- 语料库：**选稿制**——AI 出候选，用户打勾选，未勾的不收
- 复习：**手动触发**「复习/抽卡」，每次 3 条，**中英对照一起给**，不要翻译题
- 偏爱**画面感短句**，不喜欢抽象大词堆叠
- 写作习惯「先讲道理再举例」，每个理由要配一个可插拔的具体事例
- 说「这句话好」= 最高信号：标 ★、进复习队列

---

# 七、进展记录（最新在上）

## 2026-11-02（12:15）

- **本窗口改为 Router 窗口**：用户指定本会话作为 router 负责日常调度
- **⚠️ workspace 再次被清空**（11:38，iOS 容器重置）：`/var/minis/workspace/` 整个空掉，agent-system 与 reading-collector 全丢。`skills/`、`memory/`、`mounts/`、`shared/` 幸存
  - reading-collector 从 `/tmp/rc-remote` 残留副本救回；agent-system 无副本，按记忆重建
  - **已加「一键恢复清单」进第三节**，照它五步能重建全部
- **agent-system 重建并首次推仓**：https://github.com/kyoukawa/agent-system（私有）`342e90a`
  - `tests/selftest.py` 15 项全过；`validate.py` error 0 / warn 1 / info 2
  - 新增：`thread_auto` 标志区分自动/显式 thread；`enabled` 字段软停用 Worker；validate 扩到 17 条规则
  - `github-maintainer/SKILL.md` 内容原本是 reading-collector 的副本 → 已重写为真正的 git 手册
- **阅读收集一轮**：收件箱 3 条 → 成 2 条（时文1029、时文1030 已落盘并勾完成），时文1027 卡登录墙
- **Notion 镜像已开并补齐**：`config.toml` 填入父页面 `40209d7f-…`，两篇新笔记首建、验证幂等（第二次 `updated` 同 page_id）
  - 发现 `notion-map.json` 清空导致索引漏老页：用笔记 front-matter 的 `url:` 补录 4 条映射，`rebuild-index` 现 6 行
  - 两文件均在 `.gitignore` 内，不入公开仓
- **reading-collector 设 `core.fileMode=false`**：iSH chmod 无效导致 `install.sh` 永远显示脏

## 2026-11-02（11:45 补记）

- **agent-system 重建并首次推仓**：`/var/minis/workspace/` 被系统清空导致整个目录丢失，按本文件 + daily log 的设计原样重建，推到 https://github.com/kyoukawa/agent-system（私有）`342e90a`
  - 模块：`router/{router,watchdog,validate,scaffold}.py`、`triggers/events.py`、`state/state.py`、`workers/*.json`、`tests/selftest.py`
  - 纯标准库；`tests/selftest.py` 15 项全过；`validate.py` error 0 / warn 1 / info 2
  - **今后改 agent-system 一律先 `git pull`**，别再靠本地工作区
  - 详细设计差异见仓库 README「设计上的几个关键决定」
- **`github-maintainer` 技能内容是错的文件**：`/var/minis/skills/github-maintainer/SKILL.md` 里装的其实是 reading-collector 的正文（只有 front-matter 的 name 改对了），描述也是阅读收集的。已重写为真正的 git/GitHub 维护手册（凭据、建仓、改名、release、iSH 坑、汇报格式）

## 2026-11-01

- **记忆同步脚本**：`sh /var/minis/workspace/reading-collector/memsync.sh` 一条命令同步三份副本并推送；`--check` 核对一致性，`--no-push` 只同步。此前手动 cp 漏掉过仓库 docs 副本（`/tmp/rc-remote` 被清后彻底丢失）
- **Notion 堆放区已废弃**：删除页面 `40209d7f-d7ec-81be-bab3-e89df8d57cd3`；入口只剩待办「阅读收集」分组。**Obsidian 是唯一权威，Notion 只负责网页浏览**，落盘成功即归档成功 `bfc000b`
- **Notion 镜像加返回**：`build_content` 顶部插入 `← [返回 有价值内容收集]`；前面必须带箭头字符，否则 Notion 把整行识别成 page mention 吞掉文字 `6a4a510`
- **Notion 清理**：删除 3 篇 Grok 时代遗留（亚玛芬/最有效的休息/给高三三则时文），补建「如果Personal Agent不只属于一个人」，现与 Obsidian 4 篇一一对应
- **阅读收集返回链接修复**：vault 里 `语料库/`、`语文语料库/`、`阅读收集/` 都有 `首页.md`，wikilink 只写 `[[首页]]` 会跳到错误文件夹（实测跳到英语语料库）→ 必须写 `[[阅读收集/首页|…]]` `e7633de`；顺带清掉 `阅读收集/阅读收集/` 空目录
- **阅读收集笔记加返回**：每篇顶部 `[[首页|← 返回 阅读收集]]`，CSS 做成胶囊按钮；`build_note` 自动插入 `619b320`
- **阅读收集首页链接修复**：表格单元格里 `[[路径|别名]]` 的竖线必须写成 `\|`，否则被当成列分隔符、链接退化成纯文本 `5f0eb2f`
- **阅读收集命名规则**：文件名去掉日期前缀，只留标题；日期改写进嵌套标签 `#阅读收集/2026/11`；索引按月分组 `6459829`
- **阅读收集首页美化**：卡片式 CSS snippet（表格行转卡片/月份小标签/hover 高亮），`archive.py` 重建时自动带 `cssclasses: rc-home`，不污染其他笔记 `1de1b76`
- **同步核查**：远程 `6fa7bc8` 已把 COLLAB.md 并入 GLOBAL.md；本地三份副本（memory/shared/docs）md5 一致；`SOUL.md` 引用从 COLLAB.md 改指 GLOBAL.md；技能与 `scripts/*.py` 全部对齐远程最新
- **全局记忆**：本文件建立，合并了 `GLOBAL.md` 与 `COLLAB.md`，成为唯一权威状态文件；技能统一要求开工前先读本文件
- **github-maintainer**：新建技能，提交/推送/建仓/改名/release/issue 全流程，凭据持久化免授权
- **reading-collector 开源**：https://github.com/kyoukawa/reading-collector 上线（公开）
- **reading-collector**：审查发现并修复 8 处阻断性问题（vault 误探测、install.sh 无执行位、sed 特殊字符、收件箱标题行链接、`[X]` 勾错位、YAML 转义、索引解析、0 秒空片）
- **reading-collector**：Notion 镜像改幂等（`scripts/notion.py`），URL→page_id 映射，重跑走更新 `ea8f65d`
- **reading-collector**：协作机制 + 技能「铁律 0：先同步再动手」 `3e185df`
- **video-notes**：本地转写流水线落地，apple-speech 串行 + 重试，45 分钟视频约 2 分钟
- **阅读收集**：Obsidian 归档结构建立；首批归档 4 篇（含 CS146S 讲座笔记、Super-agent 设计探索）

## 2026-10-27

- **语文语料库**：第二次呼吸入库（一稿 46 → 二稿 48，一类上），复习队列 12 → 23 单元
- **语文语料库**：目录约定写死（一题一文件夹、文件名规格、重复文件夹用 md5sum 比对）

## 2026-10-26

- **英语语料库**：迁入 Obsidian vault「知识库」，复习改手动触发（删掉 20:00 定时任务）
- **英语语料库**：改为选稿制（AI 出候选 → 用户打勾把关）
- **content-collector**：Grok 自动化迁移到 Minis（该版本已废弃，被 reading-collector 取代）

---

# 八、维护约定

- **工作前先读本文件**；有进展就更新「进展记录」。
- 可复用的知识写进第一~六节，流水写进第七节。**第一节到第六节要精简，别变成日志堆。**
- 本文件与 `/var/minis/shared/COLLAB.md` 是同一份（互为副本），改完两边同步。

# 近期记忆

## 2026-11-07

### 2026-11-07 广学题库落地 /api/v1 只读接口 + 文档
- 代码：`gxwtf/gxexercise` `e81fc21`（+ `16d9bed` 修链接）
  - 新增 `src/lib/api-key.ts`（Bearer，`timingSafeEqual`，支持逗号分隔多 key）与 `src/lib/api-v1.ts`（筛选/分页/序列化）
  - 7 个路由：`/api/v1/{health,meta,questions,questions/[id],test-papers,test-papers/[id],stats}`
  - 环境变量 `GXEXERCISE_API_KEY`；未配置时除 health 外 503
  - 筛选口径与列表页一致：subject/category/cat/district/year/grade/q + page/pageSize(≤100)
  - 仅 `health` 公开；其余 Bearer，返回答案与解析
- 文档：`gxwtf/dev` `2048aab`
  - 新增 `gxexercise/api.md`（333 行），侧边栏「工程」与 README 常见任务入口登记
  - 链接格式：Docsify 是 **hash 路由**，正确写法 `https://dev.gxwtf.cn/#/gxexercise/api`
- **未部署**：本机没有服务器 SSH 私钥（`/root/.ssh` 只有 known_hosts），`ssh gxwtf@39.105.54.184:6000` 报 publickey/password。
  上线需在服务器：`.env` 加 key → `pnpm build` → `gbxwtf-systemctl restart gxexercise.service`；文档站 `cd ~/gxwtf_dev && git pull`
- 环境坑（新）：`/tmp/gxexercise` 里 `file_write` 并发创建嵌套目录会丢文件，且 `mkdir` 在该目录下报 ENOENT；
  改在 `/root` 下重新 clone 才正常。**以后写嵌套新文件一律先 shell mkdir，且同一文件不要并行 file_edit**
- 本地无 node/pnpm，只能用 `apk add esbuild` 做语法检查（已全部通过）；未跑 typecheck/build
- `gxq.py` 增加 `api <path>` 命令（读 `GX_API_KEY`），错误 HTML 会截断

### 2026-11-07 agent-cloud 云端状态中心（方案 B）
用户需求：agent 上云，iPad/手机无缝切换。选了方案 B（状态上云 + 端当客户端）。

- **仓库**：https://github.com/kyoukawa/agent-cloud（私有）
  - 用户明确：**这是个人项目，不要放 gxwtf 组织**。已从 gxwtf 转回 kyoukawa
- **设计**：Postgres 唯一权威，`/var/minis/*` 降级为缓存。Minis 的 agent 循环无法上云（依赖 iOS + `apple-*` 原生框架），但记忆/技能/会话/任务队列可以
- **代码**：`/var/minis/workspace/agent-cloud/`
  - `app/` FastAPI（main/db/auth），6+2 张表，pg_trgm 中文检索，content_hash 去重
  - `cli/minis_cloud.py` 端侧 CLI（纯 urllib，零依赖），已装到 `/usr/local/bin/minis-cloud`
  - `install.sh` 幂等部署（库 gxwtf_agent / 端口 3006 / 服务 gxagent / 域名 agent.gxwtf.cn）
- **技能**：`/var/minis/skills/cloud-state/SKILL.md`（pull/push/say/search/restore/task）
- **阻塞**：`/root/.ssh` 随 workspace 一起被清，服务器 key 丢失，无法部署。用户说会把 key 放进记忆
- **同日**：`/var/minis/workspace/` 于 10:32 再次被 iOS 清空，agent-system / reading-collector 本地副本全丢（远程仓库还在）——这正是要做状态上云的直接动因

### 2026-11-07 广学题库（gxexercise）API 调研
- 产出：`/var/minis/workspace/gxexercise-api/REPORT.md`（端点/数据模型/抓取口径/安全建议）+ `gxq.py`（stdlib 客户端，已实测 sample/list/stats/whoami）
- **无公开内容 API**：22 个 route handlers 全是站内自用；题目正文/答案在 RSC 里直连 Prisma，未登录 `/question/<id>` 307 → `/login`
- 唯一脚本化登录入口：`POST /api/session {username,password}` → 账号中心 `/sso/purelogin`，失败 401 返回空会话；无验证码/限流
- 公开端点：`GET /api/home-sample`（随机真题单选，不含答案）、`POST` 同路径判分、`/api/stats/{questions,submission-counts,test-papers}`、`/api/test-paper/[id]/pdf`（**无鉴权**）
- 登录端点：submissions group/test-paper/queue-position/excellent/delete、所有作答卷 PDF（401 验证过）
- 管理员：`/api/ai/{retry-pending,grade-reading-expression}`、`/api/admin/submissions/delete`
- 列表页 `/questions/[subject]/[category]` 每页 12 条，参数 `cat/district/year/grade/q/page`；卡片 `data-slot="item"` + `href="/question/<groupId>"`
- `/question/[id]` 的 id **只能是 QuestionGroup id**（单题无独立页）
- 无 CORS 头、无 middleware/限流；`.env.example` 的 SES_SECRET 像真密钥，已建议站长核对
- 服务端 v0.3.1-rc1 @ `39f583a`，仓库 gxwtf/gxexercise 可直连 git clone（无需 token）
- 坑：浏览器打开题库列表页会把 WebView 卡死（178KB RSC + KaTeX），探测一律用 curl

## 2026-11-06

### 2026-11-06 阅读收集：摘要时间戳可跳转
- 概括（视频/播客）里的 `[mm:ss]` 在渲染前转成 `[mm:ss](#t=秒)`（`linkTimestamps()`，服务端处理）
- `VideoReader` 加全局点击监听：命中 `a[href^="#t="]` → `preventDefault()` → `seekTo(秒)`，并恢复跟随
- 实测：点「04:06」→ `<video>.currentTime = 246`，逐字稿高亮切到 04:06，URL 不变
- 摘要里共 10 个时间戳全部变成链接

### 2026-11-06 知乎绕过方案已清理
- 结论确认：`HGXY2004/zhihu-proxy`（签名 + 挑战 + d_c0 预热）在本服务器实测仍 `403 need_login`
- 已从服务器删除 `~/zhihu-proxy`、停掉 8964 端口进程、清理临时文件
- 代码里移除 `ZHIHU_EXTRACTOR_URL` 分支，`worker/zhihu.py` 回到「只走 Cookie」的单一实现
- **坑**：`pkill -f "server.mjs"` 会匹配到 SSH 命令行本身，导致命令中断（删目录没执行）→ 用 `fuser -k <端口>/tcp` 更安全
- 现状：知乎只能配 `ZHIHU_COOKIE`（设置页「站点登录态」）

### 2026-11-06 知乎免 Cookie 方案调研（GitHub）
- 搜了 GitHub：`Guyungy/Export-Zhihu-Collections`、`KrisTHL181/zhihu-toolkit`、`yuchenzhu-research/zhihu-scraper`、`HGXY2004/zhihu-proxy`
  - 前三个都要 Cookie（README 明说「准备 cookies」）；所谓的「无 cookies」只适用于**公开收藏夹列表**，正文仍需登录
  - `zhihu-proxy`：本地 Node 反代，vm 沙箱跑知乎官方 JS 做 `x-zse-96` 签名 + 解 `__zse_ck` 挑战 + `d_c0` 预热
- **实测**：部署后 `/health` 显示 `hasDc0=true`、`challengesSolved=1`、`signed=2`，但文章/回答接口仍返回
  `403 need_login`（"请您登录后查看更多专业优质内容"）→ 服务端按登录态拦截，不是签名问题
- 结论：不存在可用的免 Cookie 路径；机房 IP 尤其严格
- 代码里加了可选 `ZHIHU_EXTRACTOR_URL`（指向提取器时优先用它，自动带 Cookie），留作以后需要签名兜底
- 测试用的 node 进程已停，仓库留在 `~/zhihu-proxy` 备查

### 2026-11-06 阅读收集：Cookie 获取指路
- 设置页「站点登录态」内嵌 `<details>` 指引：三个步骤 + 四个站点的直达登录链接 + 各自要复制的字段（知乎整条 Cookie / B 站 SESSDATA / 微博 SUB / 小红书 web_session）
- 提示：iPad 无开发者工具，建议电脑复制后用通用剪贴板；Cookie 等同登录态、会过期
- `docs/wiki/cookies.md` 补「怎么获取（逐步）」表格（Chrome/Edge F12、Safari ⌥⌘I）
- 已推 dev 文档站

### 2026-11-06 阅读收集：清理测试数据 + 站点凭据 + 控件收紧
- **清理**：删掉测试条目 21 条（MDN/维基/知乎探测/少数派 RSS 导入/Markdown 测试/arXiv 测试）与测试订阅
  - 保留用户真实内容：3、8、10、13、14、17、18、32
- **站点登录态（新功能）**：`User.credentials Json?`，设置页四个字段（知乎整条 Cookie / B 站 SESSDATA / 微博 / 小红书）
  - `POST /api/worker/jobs` 会按条目所属用户下发 `cookies`（映射到 `ZHIHU_COOKIE` / `BILI_SESSDATA` / `WEIBO_COOKIE` / `XHS_COOKIE`）
  - worker 领取任务后临时注入 `os.environ`，不落盘
  - 实测：伪造 `z_c0=TESTVALUE` → job payload 返回 `{"ZHIHU_COOKIE":"z_c0=TESTVALUE"}`（验证后已清空）
- **文档**：`docs/wiki/cookies.md`（需要登录态的站点表 + 不需要登录的站点 + 已知抓不到的情况），已推到 dev 文档站
- **控件收紧**：添加区 textarea 2 行、控件 h-8、去掉常驻提示；B 站/合集/RSS/Markdown 收进「更多导入方式」折叠面板
- 迁移：`add_credentials`

### 2026-11-06 阅读收集：头像菜单 / Markdown 导入 / 链接类型扩展
- **头像菜单**（`UserMenu`）：点头像弹出「我的收藏、批注整理、设置、广学账号、退出登录」；顶部不再有独立的设置按钮和退出按钮
- **Markdown 导入**：`POST /api/entries/markdown`
  - multipart 多文件（.md/.markdown/.txt）或 JSON `{markdown}` 粘贴
  - url 记为 `markdown:<sha256前32>`，`site="Markdown"`，直接 `state=ready`，并生成抽取式摘要
  - 首页新增「导入 Markdown」卡片
- **链接类型扩展**（`src/lib/url.ts` 的 `detectKind`）
  - video: B站/b23/YouTube/Vimeo/优酷/爱奇艺/腾讯视频/芒果/抖音/TikTok/西瓜/Twitter
  - podcast: 小宇宙/Apple Podcasts/Spotify/SoundCloud/Anchor/Podbean/Overcast
  - document: `.pdf`、arxiv `/pdf/`、Google Docs、语雀、飞书文档
  - 入库任务改为：只有 video/podcast 走 transcribe，其余走 fetch
- **PDF 抓取**：worker 按 `Content-Type: application/pdf` 识别（arXiv 链接没有 .pdf 后缀），用 pypdf 抽文字；实测 arXiv 1706.03762 → 39,627 字
- 坑：先前按 URL 后缀判断 PDF 会漏掉 arXiv；改为响应头判断

### 2026-11-06 阅读收集：头像改用广学账号
- 抄自 `gxexercise/src/components/layout/UserMenu.tsx`：头像地址是 **`https://gxwtf.cn/avatar?userId=<广学账号ID>`**（302 → Gravatar 镜像 cravatar，默认图 `gxwtf.cn/gytb.png`）
- 新增 `src/components/UserAvatar.tsx`（客户端）：带 `onError` 回退到用户名首字母，`s={size*2}` 适配高分屏
- 导航栏与设置页「当前账号」都换成真实头像
- 实测：`userId=2691` 正常加载（80×80 webp），页面 `naturalWidth=80`

### 2026-11-06 知乎：换出口节点验证
- 经代理出口为台湾；直连与代理**都 403**（返回 650 字节的拦截页）
- 通过 clash API 依次切换节点测试：香港、日本、新加坡、美国、德国——**全部 403**
- 结论：知乎按「机房 IP + 未登录」拦截，不是地区问题；换代理/换节点无效
- 已把节点恢复为原来的「IEPL·台湾专线A·TW1·均衡·1000M」，并验证 google 正常（302）
- 唯一可靠路径仍是 `ZHIHU_COOKIE`

### 2026-11-06 阅读收集：设计语言对齐广学题库
- **令牌**：`globals.css` 的 `:root/.dark` 改成题库那套 **oklch 语义色**（background/foreground/card/muted/border/ring/radius 0.625rem），并加 `--brand`（浅色 #A31F24 ≈ oklch(0.4667 0.1672 25.06)，深色提亮 oklch(0.735 0.152 25.06)）、`--brand-foreground`、`--brand-muted`
- **类名**：全站 `text-brand-red`/`bg-brand-red` → `text-brand`/`bg-brand`（题库只用语义 token）
- **基础组件**：直接取题库的 `ui/{button,input,card,badge,textarea}.tsx`（h-8、rounded-lg、focus ring-3、ring-1 ring-foreground/10 卡片），`Slot.Root` → `@radix-ui/react-slot` 的 `Slot`
- **坑**：WebKit 对 `<button>` 保留原生外观导致 `bg-primary` 不生效（浅色下变灰）→ 按钮/输入框加 `appearance-none` 解决
- **主题切换**：改成下拉菜单（浅色模式 / 深色模式 / 跟随系统，带勾选），与题库一致；导航用户区加头像圆圈（首字母）与 `(admin)` 标记
- 题库参考：<https://ti.gxwtf.cn>；其深色 primary 按钮是浅色（0.922），浅色是近黑（0.205），已一致
- 另：知乎绕过尝试全部失败（直接、m 站、api/v4、r.jina.ai、rsshub、archive、translate.goog 均 403/522）

### 2026-11-06 阅读收集：知乎抓取
- 知乎无登录必 403 / 跳登录页（实测 `www.zhihu.com`、`m.zhihu.com`、`api/v4` 全 403）
- `worker/zhihu.py`：正则取 `<script id="js-initialData">` JSON → 问题取前 3 高赞回答 / 专栏取正文 → 自写 HTML→Markdown
- 需 `.env` 配 `ZHIHU_COOKIE`（整条 Cookie）；未配或失效时抛 `ZhihuError`，失败原因直接显示在条目
- `fetcher.py` 在 `_is_zhihu()` 时优先走知乎分支，其它站点仍用 trafilatura
- 实测：HTML→MD 正常；无 cookie → `FetchJob.error = "知乎需要登录态：请配置 ZHIHU_COOKIE…"`
- 待办：等用户提供 Cookie 后验证真实抓取

### 2026-11-06 服务器：给设备用的认证代理（gost）
- 目标：让 iPad/手机连服务器翻墙
- 方案：**gost v3** 单二进制做带认证的网关，链路到本机 clash
  - HTTP 代理 `0.0.0.0:18443`、SOCKS5 `0.0.0.0:18444`
  - 认证 `gxwtf` / 密码存 `/etc/systemd/system/gost-proxy.service`（ExecStart 里，含密码，注意别外泄）
  - 启动：`/usr/local/bin/gost -L http://user:pass@:18443 -L socks5://...:18444 -F http://127.0.0.1:7890`
  - 实测：本机 HTTP→Google 200、SOCKS→YouTube 200；无认证被拒
- **坑**：gost v3 的 YAML `chains` 写法（hops→nodes）不生效会直连，改用 CLI `-L/-F` 最简单
- **坑**：`pkill -f "gost -L"` 会匹配到自己的 SSH 命令行，把会话杀掉（第二次踩）
- **未完成**：公网访问需在阿里云安全组放行 18443/18444（当前从外部连不上，2.4s 丢包）
- 现有可选方案：SSH 隧道 `ssh -p 6000 -D 1080 gxwtf@39.105.54.184`（不需开端口）

### 2026-11-06 服务器代理服务盘点
- **clash**（`clash.service`，`/home/aabbccddwasd/clash-for-linux`，root 运行）
  - HTTP 代理 `7890`、SOCKS5 `7891`、另有 `7892`（tproxy/redir 类，http/socks 探测都失败）
  - `allow-lan: true`、`external-controller: 0.0.0.0:9090`、已设 secret（9090 本机返回 401）
  - 实测：直连 Google 失败，走 7890 返回 302（可用）
  - 公网 7890/7891/9090 端口 nc 显示 open，但 curl 走公网代理与 9090 都超时/000 → 安全组实际未放通（仍建议改 external-controller 为 127.0.0.1）
- 其它监听：`new-api` 8080（AI 网关，不是代理）、`frpc`（反代隧道）、nginx（8143 proxy_protocol）
- `clash-for-linux.service` 为 inactive（旧单元）；wiki `server/README.md` 记录的是用 `~/genbot/clash/` 开关它来拉 Docker 镜像
- 结论：服务器只有一个代理系统（clash），没有 v2ray/xray/ss/tor

### 2026-11-06 阅读收集：批注整理页
- 新增 `/annotations`：按条目归组展示全部划线+批注，显示总数/带批注数/涉及篇数
- 搜索框 `?q=`（服务端 Prisma contains，匹配 quote 与 note）
- 「只看有批注」筛选 `?notes=1`
- 每条显示：引文（品牌红左边线）、批注（图标+文字）、日期、「回原文」链接
- 导航栏新增「批注」入口
- 实测：11 条划线 / 3 条带批注 / 1 篇；筛选后 3 条
- 踩坑：手写 JSX 时漏闭合 `<div>`，Next 报 `Unexpected token`，逐行 nl 定位后修正

### 2026-11-06 阅读收集：免登录字幕调研 + 上传字幕
- 实测免登录接口：`x/player/v2` 返回空字幕列表；`x/player.so`、`x/v2/dm/subtitle/search` 均 404
- 结论：B 站字幕挂在登录态后面，yt-dlp / bilibili-api 等第三方工具同样需要 cookie
- 落地替代方案：**上传字幕文件**（VTT/SRT）
  - `POST /api/entries/<id>/subtitle`（multipart）→ `parseSubtitle()` 解析 → 覆盖 `Transcript`，`backend="upload"`，条目置 ready
  - 视频页 header 加「上传字幕」按钮
  - 实测 3 段 SRT 上传成功，`backend=upload`
- 使用方式：从 DownSub 等第三方站下载 B 站字幕文件 → 页面点「上传字幕」

### 2026-11-06 阅读收集：第三方工具抓字幕
- 新增 `worker/subtitles.py`：用 **yt-dlp** 抓现成字幕（`--write-subs --write-auto-subs --sub-langs zh,en --sub-format vtt`），解析 VTT 成 segments，`backend="yt-dlp"`
- 转写优先级改为：**yt-dlp 字幕 → B 站官方接口 → whisper**
- 支持 `YTDLP_COOKIES` 指向 Netscape cookies.txt；这是无 SESSDATA 时的替代方案
- 实测：B 站无 cookie 拿不到；YouTube 在本机被风控/网络限制也拿不到 → 仍回退 whisper
- 结论：第三方工具解决「有字幕就能拿」，但 B 站字幕本质仍需登录态

### 2026-11-06 阅读收集：官方字幕优先级
- worker 逻辑顺序固定为：**B 站官方字幕 → yt-dlp + whisper**
- 未配置 `BILI_SESSDATA` 时日志会明确提示「跳过官方字幕（需要登录态）」；视频本身无字幕则提示「回退语音识别」
- 当前服务器**没有** BILI_SESSDATA，所以实际仍走 base 模型转写
- 配置方式：`cd ~/gxwtf_reading && echo 'BILI_SESSDATA=...' >> .env && systemctl restart gxreading-worker`

### 2026-11-06 阅读收集：转写准确度提升
- 模型从 `ggml-tiny`（75MB）换成 **`ggml-base`（142MB）**；tiny 输出是碎片短语、缺标点，base 能出完整句子
- 解码参数：`-bs 5 -bo 5 -tp 0`（束搜索 + 贪心温度），并可选 `--vad -vm <silero>`（`WHISPER_VAD` 已配 for-tests-silero）
- 实测 entry 8（45 分钟）：base 用时 136.6s（tiny 70s），89 段 / 46025 字，文本带标点
- 更准的路线：① B 站官方字幕（需 `BILI_SESSDATA`）② `ggml-small`（466MB，之前下到 100MB 中断，可续传）

### 2026-11-06 阅读收集：字幕区压到 5 行
- `TranscriptPanel` 容器由 `max-h-[42vh]` 改为固定 `h-[132px]`（约 5 行）+ 缩小行距 `space-y-0.5`
- 自动滚动定位随之以 132px 容器为基准居中
- 想再紧可改 `h-[110px]`；想放宽改 `h-[160px]`（都在 TranscriptPanel.tsx 一行里）

### 2026-11-06 阅读收集：自动滚动修复（三处）
- 用 `offsetTop` 定位依赖定位祖先 → 改成 `getBoundingClientRect` 差值
- WebKit 会忽略 `scrollTo({behavior:'smooth'})`（自动化/低电模式），实测 scrollTop 不动 → 改成 rAF 自绘缓动
- 后台/低电下 rAF 也可能被挂起 → 420ms 后兜底直接 `scrollTop = to`
- 验证：点第 101 行（04:01）→ 容器 scrollTop 0 → 5485，当前行高亮 04:01
- 同时修了「跳转后估算锚点未重置」导致媒体未就绪时跳回旧位置

### 2026-11-06 阅读收集：iPad 只有声音（AV1）
- **根因**：B 站直链视频是 **AV1**，Safari 不支持 AV1，且 `-c copy` 切 HLS 时 MPEG-TS 装不下 AV1 → 分片里只剩音轨（ffprobe: audio only）→ 只有声音
- **修法**：HLS 改为转码 `-c:v libx264 -profile:v main -crf 23 -preset veryfast -pix_fmt yuv420p -c:a aac`
- 已为 entry 8 重切：329 段 / 98MB，`seg_001.ts` 验证 `h264,video` + `aac,audio`
- 播放器改用**原生 `<video controls>`**（用户建议），删掉自绘播放键/进度条与冗余 audio 元素
- 转码耗时：45 分钟 720p 约 2 分钟（veryfast）
- 仍待真机验证：内置 WebView 不加载媒体

### 2026-11-06 阅读收集：HLS 路线
- prepare 完成后自动用 `ffmpeg -c copy -f hls -hls_time 6` 切片到 `~/reading-media/<id>/`（index.m3u8 + seg_*.ts）
- 新路由 `/api/media/<id>/hls/[...path]`：m3u8 用 `application/vnd.apple.mpegurl`，分片用 `video/mp2t`
- 前端探测 `canPlayType('application/vnd.apple.mpegurl')`：Safari/iPad 用 m3u8，其它用 mp4；HLS 失败自动回退 mp4
- 实测 entry 8：45 分钟视频切片耗时 0.96s，453 段、91MB；m3u8 与分片均 200
- 存储代价：同一视频 mp4 + HLS 两份（约 2×）
- 内置 WebView 仍不加载媒体（readyState 0），HLS 播放需真机验证

### 2026-11-06 阅读收集：关键帧时间全是 0
- 原因：B 站 iframe 模式拿不到 `currentTime`，`now` 恒为 0 → 关键帧全部存成 00:00
- 修法：新增 `currentSeconds()`：本地媒体读真实时间；iframe 用「跟随估算」，未跟随时取当前行 start；并加 1 秒 tick 让按钮时间实时更新
- 验证：iframe 模式下按钮显示 02:43，新增关键帧入库 `timeSec=161.6`；顺手删掉 3 条 0 值脏数据
- 局限：iframe 的估算是相对页面加载/开始跟随的时刻，拖动播放器后会偏；精确模式（Android 本地 mp4）无此问题

### 2026-11-06 阅读收集：跟随策略与 B 站官方字幕
- 删掉「手动滚动 → 暂停跟随」整套逻辑（用户要求：滚动不影响跟随）
- 实测 iframe 模式高亮会推进（00:07 → 00:20/10s）；之前中断是因为滚动即暂停
- worker 新增 `try_bilibili_subtitle()`：先取 `x/web-interface/view` 拿 cid → `x/player/v2` 取字幕列表 → 下载 `subtitle_url` 的 JSON body 转 segments
  - 需要 `.env` 配 `BILI_SESSDATA`（未登录返回 0 条字幕）
  - 成功则 `backend="bilibili"`，跳过 yt-dlp + whisper；失败/为空自动回退 whisper
- 坑：transcriber.py 里用了 os 但没 import，已补

### 2026-11-06 阅读收集：关键帧/划线搜索/字幕开关
- **关键帧**：`KeyframePanel` 加备注输入框（「备注（可选）」+ 时间按钮），`onAdd(note)` 传给 `addKeyframe`；列表点击跳转、hover 删除不变
- **划线搜索**：`HighlightList` 顶部加搜索框，按 quote/note 过滤（客户端 useMemo）
- **首页搜索**扩展到划线与批注：Prisma OR 加 `highlights.some.{quote,note} contains`
- **字幕可隐藏**：视频页 header 加「隐藏字幕 / 显示字幕」按钮，状态存 localStorage（key `reading:hideTranscript`）
- 验证：typecheck/build 通过、smoke 全过、三个元素在页面 HTML 中确认存在

### 2026-11-06 阅读收集：自我提示词（self-prompt）
- `scripts/selfprompt.sh`：把仓库状态压成一段可直接给 agent 的任务提示
  - 采集：分支/未提交改动、最近 5 次提交、测试用例数、测试与类型检查结果（`--run`）、异味计数、最大文件
  - 按「失败项 → 未收尾改动 → 异味 → 过大文件 → 缺测试」排候选任务 + 约束 + 交付格式
  - 计数兼容无 ripgrep 的机器（grep 回退）
- `docs/SELF_IMPROVE.md` 增「自我提示词」一节；另装技能 `/var/minis/skills/self-improve/`
- **这轮真实收获**：selfprompt 报「未提交改动 4 个文件」→ 查出服务器上 `add_feeds` 迁移、`pnpm-lock.yaml`、`next-env.d.ts` 都没提交回仓库，已补提交（否则下次部署会缺表/依赖漂移）

### 2026-11-06 阅读收集：Agent 自我改进循环
- 新增 `scripts/selfcheck.sh`：单元测试 / 类型检查 /（可选）构建 / 异味计数（TODO、FIXME、console.log、as never）/ 过时依赖
- 新增 `docs/SELF_IMPROVE.md`：度量 → 选一件事 → 改 → 验证 → 提交 → 部署的闭环，含硬规则（一次只修一个、不许跳过验证、不碰生产数据、改不动就停）
- 跑了一轮真实迭代：自检全绿 → 选「补纯函数测试」→ 发现 `ingest.ts` 依赖 prisma 无法单测 → 把纯函数拆到 `src/lib/url.ts` → 补 5 组用例
- 结果：**16 个测试全过**、typecheck 0 错、build 通过、health/smoke 正常

### 2026-11-06 阅读收集：统一 header 与移动端布局
- `Navbar` 重写：固定 56px 高、`max-w-5xl`、左侧品牌+导航，右侧搜索/主题/设置(图标)/用户名/退出
- 移动端：导航收进 `<details>` 汉堡菜单；搜索框 `hidden md:block`；设置改成图标按钮
- 首页移动端：侧栏（筛选/分组）收进折叠面板，内容直接可见（之前侧栏占满首屏）
- 所有 sticky 偏移仍按 `top-14`（56px）对齐：悬浮播放器、阅读工具条、右侧概括栏
- 验证：typecheck/build 通过；桌面 1280 与手机 390 两种宽度截图确认

### 2026-11-06 阅读收集：RSS 订阅与自动拉新
- 新增 `Feed` 表（userId/url 唯一、title、enabled、lastCheckedAt、lastError）
- `src/lib/feeds.ts`：`checkFeed(id)` 拉一次 feed → 只导入未见过的条目（ingestUrls 去重）→ 自动打 `RSS` 标签；`dueFeeds()` 取 30 分钟未检查的
- `POST /api/cron/feeds`：`INTERNAL_API_KEY` 保护，worker **空闲时每 30 分钟**调用一次（`last_feed_check` 节流）
- 首页 `FeedList`：列出订阅、显示最近检查时间/错误、可「立即刷新」「取消订阅」
- RSS 面板加「订阅这个 feed」按钮
- 实测：插入 sspai 订阅 → cron 返回 `{checked:1, added:9}`，9 条新文章入库并带 RSS 标签
- 坑：`.env` 的值带引号，脚本取 key 要 `tr -d '"'`

### 2026-11-06 阅读收集：RSS / 全文解锁
- `src/lib/rss.ts`：手写轻量解析（不引依赖），同时覆盖 RSS 2.0 与 Atom（item/entry、link/href、content:encoded），最多 100 条
- `GET /api/rss?url=`：登录态校验后返回 `{title, items[{title,url,summary,published,hasFullText}]}`
- 导入面板加第三个 tab「RSS」：贴 feed → 勾选 → 复用 createEntries
- **全文解锁**：feed 只给节选时，导入后 worker 照常抓原文（trafilatura），实测 sspai 条目入库后 `contentMd` 3526 字
- 实测 feed：少数派、阮一峰（两者都能直连）；带登录墙/付费墙的站点仍会失败（与普通文章一致）

### 2026-11-06 开源「gxwtf-dev」技能
- 内容：`SKILL.md` + `references/{repos,conventions,deployment}.md`
  - 技术栈基线（Next 16.3.5 / React 19.3 / Prisma 7.10 / TS 6 / pnpm）
  - SSO 三段式契约、Server Action 模板、数据建模惯例（urlHash 唯一键等）
  - 站点地图（域名/目录/端口/systemd）、Nginx+8143 proxy_protocol、systemd 绝对路径
  - 常见坑速查（webpack 构建、next-mdx-remote rsc、Tailwind 任意透明度、B 站 DASH、ctranslate2）
- **仓库**：<https://github.com/gxwtf/dev-skill>（公开，topics: agent-skill/claude/nextjs/prisma/sso/gxwtf/conventions）
  - 个人镜像 <https://github.com/kyoukawa/dev-skill>
- **署名**：LICENSE 写 "gxwtf and kyoukawa"；README 作者行；提交 `Co-authored-by: 广学五题坊 <gxwtf@foxmail.com>`，作者 kyoukawa
- 已安装到 `/var/minis/skills/gxwtf-dev/`，本机会话可直接用

### 2026-11-06 阅读收集：开放 API + 项目 wiki
- 抽出 `src/lib/ingest.ts`（detectKind / hashUrl / parseTags / extractUrlsFromText / ingestUrls），Server Action 与 API 共用
- 新增 `POST/GET /api/v1/entries`：Bearer `SECRET_API_KEY` 认证，`API_USER_ID` 决定记到哪个账号；POST 支持 urls/tags/collectionId；GET 返回最近条目
- 服务器 `.env` 已生成 `SECRET_API_KEY`（48 位 hex）+ `API_USER_ID=2691`；实测 401 / 新增 / 列表都正常
- **wiki 已上线**：<https://dev.gxwtf.cn/reading/>（概览 / 架构 / 数据库 / API / 部署），`_sidebar.md` 已加 6 行；提交 `45099e8` 推到 gxwtf/dev
- 仓库内也留了 `docs/wiki/`，README 增加「开放 API」段并指向它

### 2026-11-06 阅读收集：B 站收藏夹导入
- `src/lib/bilibili.ts`：`fetchFavPage(mediaId, page)` 调 `x/v3/fav/resource/list`；`parseMediaId()` 支持纯数字或 `favlist?fid=` 链接
- `GET /api/bilibili/fav?mediaId=…&page=…`：登录校验后返回 `{title,total,hasMore,items[{bvid,title,url,duration}]}`
- 私密收藏夹需服务器 `.env` 配 `BILI_SESSDATA`（cookie），公开收藏夹直接可读
- 首页新增 `BilibiliFavImport` 面板：贴链接/media_id → 读取列表 → 勾选 → 复用 `createEntries` 批量入库（自动投 transcribe 任务）
- 实测：非法 id 有中文提示；不存在的收藏夹返回空列表不报错

### 2026-11-06 阅读收集：拆组件 + 首套单元测试
- 抽出 `components/video/TranscriptPanel.tsx`（歌词行列表、当前行高亮、展开更多），VideoReader 587 → 526 行
- 新增单元测试：`src/lib/{time,embed,summarize}.test.ts`，用 Node 内置测试器（`node --test src/lib`，Node 26 直接跑 .ts）
  - 11 个用例全过（mmss 进位/小时、B站/YouTube 解析与跳转参数、摘要分段与链接清洗）
- `package.json` 加 `test` 脚本；tsconfig 加 `allowImportingTsExtensions`（测试里 `import "./time.ts"`）
- 验证：typecheck 0 错、build 通过、smoke 全过
- 待办：PlayerShell 仍可拆，但收益递减；测试目前只覆盖纯函数

### 2026-11-06 阅读收集：全量代码优化（第二轮）
- 抽出 `src/lib/time.ts` 的 `mmss()`，删掉 VideoReader / page / summary 三处重复实现
- 抽出 `components/video/KeyframePanel.tsx`，VideoReader 瘦身约 40 行；删除未使用的 `ArticleSplit.tsx`
- `next.config.ts`：关掉 `poweredByHeader`，加 `X-Content-Type-Options / Referrer-Policy / X-Frame-Options`
- 转码接口：`mediaState=pending` 超过 30 分钟视为卡死，允许重新准备
- 验证：typecheck 0 错、build 通过、安全头生效、smoke 全过
- 待办：VideoReader 仍 ~550 行，可继续拆 TranscriptPanel / PlayerShell；缺单元测试

### 2026-11-06 阅读收集：代码质量整备
- 删除 VideoReader 里「非精确模式拉 B 站直链」的死代码（每次打开都会白跑一次 yt-dlp）
- 5 处 `as never` 改为 `Prisma.InputJsonValue` / `Prisma.JsonNull`（prefs/aiSettings/anchor/segments）
- 新增 `src/app/error.tsx`（重试 + digest）、`not-found.tsx`
- 新增 `GET /api/health`（DB 延迟、uptime）与 `scripts/smoke.sh`（health/首页/登录）
- `AGENTS.md` 补「媒体与第三方播放器」章节：DASH 分片不能直接播、代理要补 Referer+UA、iOS 回退、禁用 `bg-xxx/15` 这类任意透明度
- 验证：`pnpm typecheck` 无错误、`pnpm build` 通过、health `{"ok":true,"db":"up"}`、smoke 全过

### 2026-11-06 阅读收集：当前行高亮恢复
- 现象：改「默认跟随」后高亮消失
- 原因：`active = i === activeLine && following` 且 `activeLine` 初始 -1、`lineAt(0)` 在第一行 start>0 时返回 -1 → 一行都不高亮
- 修法：`activeLine` 初始 0；`lineAt()` 当 `seconds < lines[0].start` 时返回 0；高亮不再依赖 following（暂停后也保留当前位置）

### 2026-11-06 阅读收集：字幕默认跟随 + 整行点击跳转
- `following` 默认 true（始终跟随）；视频 `onPlay` 时自动恢复跟随并清除暂停提示
- 暂停/手动滚动会暂停跟随，并显示「继续跟随」；未开播时不误报
- 点击整行（或时间戳）→ `seekTo(line.start)`，本地 mp4 直接跳转
- 保留「停止跟随 / 跟随播放」按钮做手动开关
