---
name: cloud-state
description: 跨设备状态同步与云端状态查看。当用户提到「另一台设备」「接着上次」「无缝切换」「找回记忆」「云端怎么样了 / 状态 / 健康检查」，或要在 iPad 与手机之间接续同一件事时使用。命令 minis-cloud 是端侧客户端，云端 Postgres 是唯一权威。
---

# cloud-state — 云端状态同步

## 铁律

**`/var/minis/workspace` 会被 iOS 随时清空，`memory/` 也可能丢。云端才是权威。**

- 开工前：`minis-cloud pull`
- 记住一件事：`minis-cloud say "内容" -t "标题"`
- 收尾：`minis-cloud push`
- 本地被清：`minis-cloud restore --force`

## 什么时候必须 pull

1. 用户说「接着上次」「另一台设备」「无缝切换」「你记得吗」
2. 一个任务明显跨越这次会话（多步骤、要过夜、要在两台设备上继续）
3. 用户问起历史项目状态（reading-collector / agent-cloud / 语料库进展）

不是每次都要跑——纯闲聊、一次性查询可跳过，省一次网络往返。

## 先看状态，再动手

**任何云端操作前，先跑这一条。** 它能一次性告诉你服务活着没、数据有多少、有没有积压。

```sh
minis-cloud status
```

```
云端  https://agent.gxwtf.cn  (gpu-server)  v0.1.0
────────────────────────────────────────────────────
记忆    81 条 · 5 天 · 最新 2026-11-07
技能    15 个
任务    排队 0  运行 0  完成 5  失败 3
最近运行 487235e4 done gxwtf_reading 2026-11-07T03:38
最近记忆 2026-11-07 云端优先策略
────────────────────────────────────────────────────
本地    上次推送 2026-11-07T10:52:45
        注入文件 存在（/var/minis/memory/_cloud-inject.md）
```

**怎么读这几个数：**

| 现象 | 含义 | 处理 |
|---|---|---|
| `排队 > 0` 且长时间不动 | runner 卡住 | `ssh gx "systemctl --user restart gxagent"` |
| `运行 > 0` 但 `step` 不涨 | LLM 网关慢/504 | 等；已带 3 次重试 |
| `失败` 持续增加 | 任务太大撞步数上限 | 拆小重派 |
| `最近记忆` 停在几天前 | 端上没 push | 跑 `minis-cloud push` |
| 本地 `上次推送 从未` | 这台设备没接过云端 | 配置 token + url |
| `注入文件 缺失` | 没 pull 过 | `minis-cloud pull` |

要原始数据（脚本用）：`minis-cloud status --json`

## 网页看板

**https://agent.gxwtf.cn/** —— 手机/iPad 打开即用，跟随系统深浅色。

**只读**：网页不再提供派单，下命令一律走 `minis-cloud agent`（CLI / 本地 agent）。

- 顶部：连接状态、身份徽章、版本、最后更新
- 三张统计卡：记忆 / 技能 / 跨度天数
- 任务队列：比例条（运行/排队/完成/失败/暂停）+ 计数
- 最近任务：左侧状态色条、步骤进度条、当前动作、悬停展开时间轴事件流
- 最近记忆：6 条摘要

登录用广学账号 SSO（`/sso/login`）；
管理员判定 = 账号中心 `admin` 为真 或 userId 在 `AGENT_CLOUD_ADMINS` 白名单。
令牌登录保留为备用（页脚「或用令牌」），CLI 全程走 Bearer。

刷新节奏：有任务在跑 4 秒，空闲 15 秒。展开状态跨刷新保留，事件按 seq 增量追加。

## 命令表

| 命令 | 作用 |
|---|---|
| `minis-cloud status` | **状态面板**（记忆/技能/队列/最近活动） |
| `minis-cloud status --json` | 同上，结构化输出 |
| `minis-cloud pull` | 拉近 3 天记忆 + GLOBAL → `/var/minis/memory/_cloud-inject.md` |
| `minis-cloud pull --days 7` | 拉一周 |
| `minis-cloud push` | 上传本地日志增量（内容哈希去重，可重复跑） |
| `minis-cloud say "..." -t "标题"` | 写一条（本地 + 云端） |
| `minis-cloud search "关键词"` | 全文检索云端全部记忆（pg_trgm 中文可用） |
| `minis-cloud global get` / `global push` | 全局记忆读写 |
| `minis-cloud skills push` | 全部技能同步到云端 |
| `minis-cloud skills pull` | 从云端拉技能（默认不覆盖已有，`--force` 覆盖） |
| `minis-cloud skills get <name>` | 打印某个技能正文 |
| `minis-cloud restore` | 设备被清后重建 memory/ 与 skills/（不覆盖已有） |
| `minis-cloud restore --force` | 强制覆盖 |
| `minis-cloud task add <kind> -p k=v` | 派一个跨设备任务 |
| `minis-cloud task list -s pending` | 看队列（另一台设备派的也在这） |
| `minis-cloud task done <id>` | 标记完成 |
| `minis-cloud agent ...` | 云端开发循环，见 `webdev-agent` 技能 |

## 出问题了怎么查

```sh
# 1. 服务端进程
ssh gx "systemctl --user status gxagent --no-pager | head -8"

# 2. 最近报错
ssh gx "journalctl --user -u gxagent -n 40 --no-pager | grep -A8 -E 'Traceback|Error'"

# 3. 数据库直连
ssh gx 'set -a; . ~/.config/agent-cloud/env; set +a; psql "$DATABASE_URL" -tAc "select count(*) from memories"'

# 4. 重启
ssh gx "systemctl --user restart gxagent && sleep 3 && curl -s http://127.0.0.1:3006/health"
```

常见坑：
- **nginx 502** → 多半是 Python 启动失败（少 import），看 journalctl，不是 nginx 的问题
- **`JSONB` 报 `cannot adapt type dict`** → 参数要包 `Jsonb(...)`
- **多个 `--wait` 进程堆积** → 用 `agent inbox` 替 `--wait`，任务本体在云端

## 服务在哪

| 项 | 值 |
|---|---|
| 地址 | **https://agent.gxwtf.cn** |
| 服务器 | `ssh gx`（39.105.54.184:6000 / `gxwtf`） |
| 目录 | `~/agent-cloud` |
| 库 | PostgreSQL `gxwtf_agent` |
| 配置 | `~/.config/agent-cloud/env`（600，见下） |
| 进程 | **user systemd** `gxagent.service`（:3006，Linger=yes，开机自启） |
| 证书 | acme.sh 签的 `~/agent-cloud/certs/agent.crt`（EC-256，自动续期） |
| 代码 | https://github.com/kyoukawa/agent-cloud（私有，个人项目，**不放 gxwtf 组织**） |

`env` 文件里有四项：`DATABASE_URL`、`AGENT_CLOUD_TOKEN`、`AGENT_CLOUD_BOOTSTRAP_KEY`、`LLM_*`。
**只读变量名，永远不要打印值。**

## 每台设备一次性配置

```sh
mkdir -p /root/.config/agent-cloud
ssh gx 'grep ^AGENT_CLOUD_TOKEN= ~/.config/agent-cloud/env | cut -d= -f2' \
  > /root/.config/agent-cloud/token
chmod 600 /root/.config/agent-cloud/token
echo 'https://agent.gxwtf.cn' > /root/.config/agent-cloud/url
```

token 两端共用一个，**不要写进对话、仓库或日志**。

## CLI 位置与自更新

```sh
/var/minis/workspace/agent-cloud/cli/minis_cloud.py
```

**workspace 被清后 CLI 也没了**。恢复方式（推荐，不需要 git）：

```sh
mkdir -p /var/minis/workspace/agent-cloud/cli
curl -fsSL -H "Authorization: Bearer $(cat /root/.config/agent-cloud/token)" \
  https://agent.gxwtf.cn/v1/cli -o /var/minis/workspace/agent-cloud/cli/minis_cloud.py
printf '#!/bin/sh\nexec python3 /var/minis/workspace/agent-cloud/cli/minis_cloud.py "$@"\n' \
  > /usr/local/bin/minis-cloud
chmod +x /usr/local/bin/minis-cloud
```

**CLI 更新后每台设备都要重跑上面这条 curl**，否则用的是旧命令集。

## 与现有记忆机制的关系

- `memory_write` 工具仍写本地 daily log
- `minis-cloud say` 是「写本地 + 推云端」二合一，**跨设备场景优先用它**
- `minis-cloud push` 可把之前 `memory_write` 写的存量一次性补上云端

## 不做什么

- 不同步 `SOUL.md`（跟设备走，属于 UI 设置）
- 不同步 `attachments` / `offloads`（体积大，另说）
- 不碰 `apple-*` 原生能力（健康、提醒、相册只在端上）
