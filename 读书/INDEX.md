---
cssclasses:
  - rc-home
---

↑ [[知识库导航|总导航]]

# 读书 · 导航

> 微信读书进度追踪。数据由 `weread_sync.py` 拉取，**笔记是自动生成的**，手改会被覆盖。

| 页面 | 用途 |
|---|---|
| [[读书/阅读进度\|阅读进度]] | 当前快照：在读、读完、未开始、本周/本月/累计时长 |
| [[读书/阅读日志\|阅读日志]] | 每次同步的变化流水，看趋势 |

## 怎么更新

说「同步读书」或「看看我读到哪了」→ 跑一次同步，刷新上面两页。

- 脚本：`C:\Users\chuan\minis\shared\weread\weread_sync.py`
- 快照：`C:\Users\chuan\minis\shared\weread\snapshots\<日期>.json`
- 密钥：环境变量 `WEREAD_API_KEY`，不进 vault、不进日志
