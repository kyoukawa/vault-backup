---
name: webdev-agent
description: 把网站开发任务交给云端 agent 循环执行。当用户说「让云端改代码」「跑个构建」「部署某站」「批量重构」「检查几个仓库」，或者任务本身是长时间的文件操作/命令执行时使用。日常的记忆与任务同步仍走 cloud-state（方案 B），不要混用。
---

# webdev-agent — 云端开发循环（方案 C）

## 两条路的分工

| | 方案 B（cloud-state） | 方案 C（webdev-agent） |
|---|---|---|
| 跑在哪 | 端上（Minis 里） | 服务器（agent-cloud 常驻） |
| 干什么 | 记忆、技能、任务队列同步 | 改代码、跑构建、部署、批量检查 |
| 谁执行 | 我自己，边说边做 | 服务器上的循环，我只派单、不等待、事后收结果 |
| 适合 | 聊天里顺手记一笔 | 十几步、几分钟、要连续跑 |

**不要用 C 做「一句话就能答」的事**——派单的开销比直接做还大。

## 命令

**默认不等待（铁律）**：派单后立刻返回，继续和用户对话。
任务在云端跑，需要结果时再用 `show` 去收。

```sh
# ✅ 默认：派完就走（0.7 秒返回，打印 run_id 与队列情况）
minis-cloud agent dispatch "任务描述" -p gxwtf_reading

# 带上对话里的约束
minis-cloud agent dispatch "任务描述" -p gxwtf_reading \
  --context "不要改 globals.css；颜色只用语义令牌"

# 收结果（随时，事后也行）
minis-cloud agent show <run_id 前 8 位>

# 看队列与历史
minis-cloud agent ls
minis-cloud agent ls -s running

# 取消
minis-cloud agent cancel <run_id 前 8 位>
```

**什么时候才用 `--wait`**：只有用户明确说「等它跑完」「跑完告诉我结果」，
或者下一步动作在物理上依赖它的产物（比如必须拿到 diff 才能继续改）。
即便如此也优先「派完 → 继续聊 → 用户说好了再 show」，因为 `--wait` 会把整轮对话卡住几十步到几分钟。

`dispatch` 与 `run` 的唯一区别：`dispatch` 会多打印三行（run_id、队列快照、收结果命令），
方便你在回复里把 run_id 告诉用户。两者都不等待。

`-p` 是家目录下的项目名（`gxwtf_reading` → `~/gxwtf_reading`），也可以用 `-c /绝对/路径`。
`--max-steps` **默认 0 = 不限步数**，任务一直跑到自己调 `done`。
只有卡死保护：连续 6 次相同工具+参数会自动停下。
确实想设上限时传正数，到上限会 `paused`，之后可 resume。

## 它能用哪些工具

`ls` `read_file` `write_file` `edit_file` `grep` `run`（shell，≤300s）`git`（status/diff/log/add/commit/checkout/branch/fetch/pull）`done`

**不能** `git push`、不能 sudo、不能碰 `~/.ssh` `~/.config` `.acme.sh`、不能改允许目录之外的任何文件。

## 派单怎么写

好的任务描述有三个特点：**范围明确、验收标准清楚、说清「别做什么」**。

```
❌ 优化一下首页
✅ 修 gxwtf_reading 首页页脚「返回」链接跳到错误文件夹的问题：目标是 <路径>，
   不要动其他文件，改完跑 pnpm build 确认通过，在 done 里说明改了哪几行。
```

```
❌ 看看还有什么问题
✅ 检查 ~/gxwtf_reading 里所有 Server Action 是否都做了登录态校验，
   列出缺失的文件和行号，只读不改。
```

## 收尾规矩

0. **派单当轮就这么回复**：说清派了什么、run_id 前 8 位、去哪看进度。不要卡在工具调用里等。
   用户下一句话里说「好了吗 / 收一下」，再 `agent show`。
1. 任务完成后，云端会自动往 `memories` 写一条「云端 agent：<项目>」——端上 `minis-cloud pull` 就能看到。
2. **不要相信 done 里的话就完事**：要 `minis-cloud agent show <id>` 看工具调用是否符合预期，尤其是有 `run` 的任务。
3. 涉及部署（`pnpm build` + 重启服务）的任务，让 agent 只做构建验证；**重启服务这一步由人决定**，或者单独派一条明确指令。
4. 云端改完的代码要在服务器上 `git diff` 复核，再决定是否提交推送。

## 失败怎么读

| 症状 | 原因 | 处理 |
|---|---|---|
| `status=failed` + 「达到步数上限」 | 任务太大 | 拆成两条，或 `--max-steps 40` |
| 工具结果里 `ERROR: 路径不在允许范围` | 项目不在家目录一层 | 用 `-c` 给绝对路径，或先确认目录存在 |
| `ERROR: 命令被安全策略拒绝` | 命中了黑名单（sudo / 强推 / 写 /etc） | 换个做法，别绕 |
| `status` 一直 `queued` | 执行器串行，前面有任务 | `agent ls -s running` 看排队 |
| 事件里反复 read_file 同一文件 | 模型迷路 | 取消重派，把任务描述写得更具体 |
| `LLMError: HTTP 504` | 网关处理超时（上下文太长/单步太重） | 拆成小任务；已带 3 次重试 |
| grep 结果为空但文件里有 | 服务器无 ripgrep 时回退 grep，正则语法有差异 | 用简单模式，或 `run "grep -rn ..."` |

## 批量检查类任务怎么写（实测有效）

逐个 `read_file` 十几个文件会耗尽步数。正确的写法是**明确要求用 grep 扫描**：

```
❌ 检查所有 API 路由的鉴权
✅ 用 grep 扫描 src/app/api 下所有 route.ts，找出每个文件用到的鉴权方式
   （getSession / verifyWorkerRequest / SECRET_API_KEY / 无），输出表格。只读不改。
```

实测：同样的体检任务，逐个读文件 14 步超限失败；改成 grep 批量扫描后 7 步完成，
并额外发现 4 个真实问题（死 import、非常量时间比对、health 泄漏 DB 错误、quote-card 无鉴权）。
