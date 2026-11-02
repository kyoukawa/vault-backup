---
title: "常驻 Agent 的完整架构（Grok Bot 开发者讲座）"
source: "Bilibili / YouTube"
author: "Lee Robinson（Stanford CS146S）"
url: "https://www.bilibili.com/video/BV1wWJa61Ee3"
collected: "2026-11-01"
tags:
  - 阅读收集
  - 公众号
---

来源：Bilibili / YouTube
作者：Lee Robinson（Stanford CS146S）
链接：[https://www.bilibili.com/video/BV1wWJa61Ee3](https://www.bilibili.com/video/BV1wWJa61Ee3)
收集日期：2026-11-01

---

# 斯坦福 CS146S｜Grok Bot 开发者：常驻 Agent 的完整架构

> 讲者：Lee Robinson（SpaceX AI / Grok） · 课程：Stanford CS146S · 时长 45 分钟

## 一句话结论

常驻 agent 并不改变「模型在循环里调用工具」这个内核，只是把它从笔记本搬到了云端：一个瘦客户端加固定服务器，外面挂上按需唤醒的 Firecracker 机器、可恢复的 Temporal durable workflow、subagent 分身和一堆省 token 的上下文工程手段，让 agent 能在你关掉电脑之后继续跑几周甚至几个月。

## 分章要点

### 00:00 开场

- 讲者先给出对比基线：第一周学员写的 harness 只有三件套——模型、工具、循环。它很强，但缺陷很致命：一合上笔记本，进程就死了（00:00）。
- 他要讲的「常驻（always on）/主动式（proactive）/持久（persistent）agent」与此的差别不在算法，而在部署形态：跑在服务器或云上，可以重启、能扛住崩溃（00:45）。
- 这类 agent 自带一台云端 Linux 电脑：桌面、文件、浏览器，可能还有 3D 应用。它能存文件、逐步理解你的进展、积累关于「你如何跟它协作」的记忆。
- 交互语义也变了：终端 harness 对每条消息都必答；常驻 agent 更像同事，知道什么时候该安静，只在有重要进展时回来找你（01:30）。
- 触发源不止你打字：Slack 消息、邮件、其他事件都能把它叫醒。目标时长从「小时/天」升级到「周/月」，这需要不同的架构。

### 02:35 如何走到今天

- 第一代：从 ChatGPT 复制粘贴代码到编辑器（看着古老，其实只有几年）（02:15）。
- 第二代：上一讲讲的那个简化 harness——改文件、跑命令、终端里一个简单界面。它之所以起飞，是因为模型第一次能「主动」做更多事。
- 第三代：把编码 agent 装进专门的应用，人们开始并行跑很多个，甚至跑在云端；但瓶颈换成了人——每条 shell 命令你都要审（03:00–03:45）。
- 第四代（现在）：常驻 agent 在后台「环境化」地运行，有自己的电脑、自己的记忆、在工作中习得新技能，你睡了它还在跑。
- 交互模式从「排队等审批」变成「方向盘式操控（steer）」：先让它去看某个 thread，紧接着补一句「这事改到周四做」。老模型被这样打断会懵，新模型能像听朋友絮叨一样把两句话串起来（04:30）。
- 安全上引入 auto review：由另一个 AI 模型审查每条将被执行的命令。讲者说盲测下模型审命令常常比人更靠谱——人审几百条 shell 命令会疲劳，「不审」反而比人审更安全（05:15）。
- 为什么这类产品（他们叫 bot）现在扎堆出现：交互被压缩成「发短信」。所有人都会发短信，但这次对面能真的把活干完，而不只是答问题（06:00）。

### 06:13 模型的六个变化

- ① 长程指令遵循：过去一两年模型在长时间跨度上不再跑偏，配合压缩/归并，能稳定跑几小时到几天（06:00）。
- ② subagent：模型可以把活交给「帮手」，帮手有全新的工作记忆，用完只把结论交回主 agent，于是主对话不被填满，近似「无限上下文」（06:45）。
- ③ 工具调用与强工具：几年前模型调工具常幻觉，如今幻觉已基本不再是话题；可以给它跑 shell、读文件、整台 Linux 机、录 demo 视频、像人一样点屏幕（07:30）。
- ④ computer use：任何没提供 API / MCP server 的 SaaS 或网站，都能被自主操作（07:30）。
- ⑤ 文件即记忆：用户的 profile（例如「喜欢全小写文本」）写进每条 prompt；每日工作日志写成文件，问「我上周做了什么」它就去 grep。模型很擅长用 Linux 命令翻文件（08:15–09:00）。
- ⑥ 从演示中固化技能：把某类任务的做事流程写成 markdown skill，生态里已有大量公司/开发者写好的 skill（写邮件、设计 API 等）；Grok Bot 里还有插件体系与 routine（类似 cron job 的定时 prompt）（09:00–09:45）。

### 10:06 常驻 agent 内部

- 状态机从左到右：服务器睡眠 + 那台电脑也睡眠 → 收到消息或某个 trigger → 加载并启动该 agent 的全部状态 → 需要时再启动电脑 → 用完双双 sleep（09:45–10:30）。
- 必须能睡的原因很朴素：全世界没有那么多机器可以让每个人的电脑 7×24 挂着，服务器成本也撑不住。休眠时把对话日志、记忆、routines 持久化进数据库（10:30）。
- 唤醒源越来越有意思：直接 prompt、Slack 私聊、电话/会议。SpaceX 内部已很常见「bot 代替员工进会议记笔记再回来汇报」；也可以是跑了几天才完成的 routine 回来交摘要（11:15）。
- 唤醒后有个 router 决定怎么把这件事塞进对话，并判断「要不要打扰用户」——同事每推进一点就来汇报会很烦，按任务节奏一天一次就够（12:00）。
- 那台电脑是 Firecracker 虚拟机：之所以选它，是因为可以极容易地对整机状态做快照、关掉、再恢复。你可以连进去实时看屏幕、亲手操作；命令跑在隔离环境而不是你私人笔记本；Chrome 可用，还能做虚拟桌面，让 10 个 bot 各自拥有独立的浏览器界面，共用同一批机器资源（12:45）。
- 服务器侧：命令先进队列 → 进入紫色的 agent loop（还是「模型循环调工具」）→ 关闭时把状态写回数据库/存储（13:30）。
- 为什么 agent loop 跑在服务器而不是 VM 上：thin client + fixed server。推更新不用走 App Store；转写、图像生成这类重计算服务器更快；服务器有成熟的弹性扩容方案；最关键的是——loop 若在 VM 里，你就无法在不停机的情况下单独重建 VM（比如打一个 zero-day Linux 补丁）（14:15–15:00）。
- 一致性取舍：客户端发消息要立刻显示已收到，后端用订阅把变更推给客户端，客户端再拉最新数据，还要做去重防止重试造成重复消息（15:45）。
- durable workflow vs job queue：普通队列在第 3 步崩溃后重启要从第 1 步重放；durable workflow 重试时直接从第 3 步接着跑。他们用开源项目 Temporal 实现，不必自己从零搭这套分布式机制（16:30）。
- 消息优先级：你直接发给 agent 的消息能打断 routine、插到最前面；别人的消息排队；同一 agent 短时间内收到三四条会被 batch 成一批再逐 turn 处理（17:15）。

### 18:07 harness 设计

- 与上一周 harness 最大的差别：客户端与服务器之间只有一个工具——send to user。架构因此极简（18:00）。
- 重工具全在服务端：跑 shell、读文件、调用 cloud agent、录屏、做 demo（18:45）。
- 好处：无论客户端是手机 App、桌面端、邮件还是 Slack，都只需实现这一个工具；客户端收到后自行决定如何渲染成最合适的富交互——登录时弹一键登录表单并接入 1Password，付款走 Stripe Link 或 X Money，不可逆动作（发邮件、发 Slack）先给你一份草稿让你编辑批准，不需要说话时只回一个 emoji（19:30）。
- 动态工具发现（dynamic tool discovery，也称 tool search tool）：每个工具的 name + schema 都占 context；装完 Google Drive、Gmail、YouTube 这些 MCP connector 后，窗口大半被工具定义吃掉。于是每条消息里只放工具名，模型要用时再去文件里读完整定义——「一切皆文件」（20:15–21:00）。
- 检索阶梯：先看对话历史里已有的 → 插件/MCP/API（例如用 Plaid 拿银行数据）→ web search → 用浏览器打开网页 → 整台桌面跑脚本构建 → 全失败才去打扰用户请求批准（21:45）。
- 从机器取信息的三种粒度：截屏 > 读 HTML > 读 accessibility tree（token 最省，足够定位按钮和链接）；实在不行再按像素点击，以应对弹窗、验证码、2FA（22:30–23:15）。
- 主 agent 像乐团指挥：对话尽量稀疏，脏活全交给 subagent。subagent 跑一堆 shell 或昂贵工具，最后只回传结果，主上下文不膨胀——「无限上下文」不是真的，是靠这套分工做出来的体感（23:15）。
- 每个 helper 自身也是一个 durable workflow，崩了能接着跑不丢进度；主 agent 维护 to-do，可查看、可发消息、可停掉某个 helper——这套模型照搬自「如何带一支工程师团队解决复杂问题」（24:00–24:45）。
- 工程细节：turn 进行中不要动态增删工具；工具描述/schema 过长既贵又占 window，要狠心裁剪；「一个工具跑 shell 就够」在模型 90% 时间都在跑 shell 时反而不如做一个专用工具——更高效，也更好被 review；给人类写的错误信息请写得具体（点这个链接、下一步做什么），这对 agent 同样有效——agent 也有 DX（25:30–26:15）。
- 安全边界：auto review 审每条 shell 命令；邮件、网页这类不可信输入不能当作用户指令，要防 prompt injection；不可逆动作必须先问用户；用 durable workflow 把密码等敏感信息隔离在模型对话之外（26:15–27:00）。

### 27:26 上下文工程

- 讲者把 context engineering 与 harness engineering 视为同一件事：如何在 harness 里把上下文压到最小，提效降本（27:00）。
- prompt caching：多轮对话里绝大部分 token 本应是 cached token——每次只加一条新消息，却把整段历史重发。缓存 token 折扣极大，所以要想办法让缓存命中（27:45）。
- 做法：工具定义、system prompt 等固定部分尽量保持静态且顺序固定，只在末尾追加新消息，这样每次只为「delta」付未命中价（28:30）。
- 一个缓存 miss 就等于系统 bug。年初 OpenClaw 在订阅套餐里火爆时，这种全天候跑 agent 的用法 providers 从未见过，harness 也没为它优化，导致大量 cache miss，不得不做很多修复（30:00）。
- 技巧：给 prompt 各段做 hash 并固定顺序，做 A/B test 时不要把新 prompt 段插到别人前面而打乱顺序、击穿缓存；用户打开聊天框开始打字时，服务器就提前把 prompt 准备好「预热缓存」——像网页 hover 预取下一页（30:45）。
- 上下文满了必须 compaction：假设 20 万 token 窗口，跑到尽头要总结，而压缩必然有信息损失，算法要做好极难（可写一整个博士论文）（31:30）。
- 实操：缓存窗口只在模型提供方给的「热」时段内有效（可能 10 分钟，可能 60 分钟）。趁缓存还热时就做 compaction，成本低得多；用户 30 分钟后回来时从摘要继续，后续每条消息都更便宜（32:15）。
- 记忆分层：① 关于用户的核心事实（如「一律用小写」），每条 prompt 都带；② 带日期的历史日志；③ 临时便签 scratchpad，只对接下来半小时到一小时相关，之后自然消失；其余全落文件，靠 grep 检索（33:00–33:45）。

### 34:26 未来去向

- 训练飞轮：pre-training 学世界 → SFT 教它扮演 chat assistant 或 agent → RL 教它在环境里「打游戏越打越好」（34:30）。
- 对常驻 agent 而言，SFT 阶段要喂真实 harness 里的例子，让它认识你的工具；RL 阶段训练它在上百个 skill 中选对那个、在浏览器里点对位置（35:15）。
- 推理侧要分级优化：主 agent 交互要求低延迟，秒回；交给 helper 跑长任务时，10 分钟和 12 分钟没差别，可以牺牲速度换质量（35:15）。
- 双环：内环每天做——出错 → 转成 eval → 修 harness/bug/prompt（也可能是推理问题）→ 用 eval 验证 → 发布；外环每几个月一次——用这些失败样本训练新模型，把新模型丢回产品验证全维度提升（36:00–36:45）。
- 新能力会带来新用法（如多 bot 群聊协作），这类场景几乎没有训练数据，而且很容易出事（提到了 multiple / Hugging Face 事故），必须专门训练其在 agent 系统里的行为（36:45）。
- 团队原则是「delete the product」：默认今天的模型是未来最差的，六个月后 UI 可能要重写。所以「今天讲的这些，半年前讲会是完全不同的内容」（37:30）。
- 6–12 个月的判断：agent 从跑几小时/一天变成跑几周/几个月；更好地回忆历史（表示形式可能是 graph、也可能是文件，尚无定论）；给它「一个真人同事会有的全部工具」；界面可能转向 speech-to-speech；在工作中习得技能并落成文件；公司把流程写清楚以便 agent 读取（38:15–39:45）。
- 开放问题：跑一个月的 agent，模型却每月更新——评估怎么做？要么改进 eval，要么放慢发版（40:30）。记忆算法、安全（避免被恶意方接管）、「何时沉默/何时提醒」的分寸（「我看到你昨天缺课，我录了音并整理了笔记」——是帮忙还是烦人）都还没解（41:00–41:15）。
- 趋势押注：一年后世界上的 token 流量会显著增加，因此把推理、模型、harness 的成本压下来会越来越重要（41:15）。
- 类比：2005 年人人都是 server + database + CRUD 界面，被吐槽「都一样」，但那就是新常态；今天每个产品都会有 agent 侧，或者沦为给别的 agent 用的数据（42:00）。
- 每个模块都是独立的大产业：durable workflow、云沙箱、云端电脑、记忆、技能、连接服务、语音、支付、身份、eval、可观测性——每个都对应几十家创业公司，是下一代产品的基础原语（42:45）。

### 43:23 三点建议

- ① 系统设计与架构比以往更重要，因为架构决策会复利。讲者仍坚持读代码——不是别人写的，而是自己写的，尤其是为了理解你要交付的架构（43:30）。
- ② 动手复现：GitHub 上应该已经有类似 Grok Bot 的开源实现，可以配一个 GUI、找个沙箱和 VM 自己搭一遍（44:15）。
- ③ 别怕补一点 LLM 的基础：不必深入 ML 研究，但要知道训练大概在做什么。就像写 web app 要懂数据库——harness 层的很多决策受模型本身影响，有这个直觉会让你在任何岗位上更占优势（44:15–45:00）。

## 关键概念速查

| 概念 | 一句话解释 | 为什么重要 |
| --- | --- | --- |
| always on agent | 跑在云服务器上、可被事件唤醒、可跨周月持续工作的 agent，而非终端里的一次性进程 | 把「模型+工具循环」从单次会话扩展为长期同事 |
| thin client / fixed server | 客户端只负责收发与渲染，agent loop 和重工具全在服务端 | 多端统一、快速发版、服务器可独立重建而不停机 |
| send to user | 客户端与服务器之间唯一的通信工具 | 接口极简，新客户端接入成本几乎为零 |
| Firecracker VM | 轻量虚拟机，支持整机状态快照与快速恢复 | 让「每人都有一台电脑」在成本和隔离上可行 |
| durable workflow / Temporal | 崩溃后从断点（而非第一步）恢复的工作流 | 长任务不丢进度；subagent 也是工作流 |
| router | 收到事件后决定塞进哪个对话、是否打扰用户的调度层 | 决定 agent 像同事而非通知轰炸机 |
| auto review | 用另一个 AI 模型审查每条待执行命令 | 替代人工审批，解决审批疲劳与漏审 |
| subagent / helper | 拥有独立工作记忆的分身，只回传结果 | 主上下文不膨胀，造出「无限上下文」的体感 |
| dynamic tool discovery | 每条消息只放工具名，用到时再读完整 schema | 省 context、省钱，避免 MCP connector 吃满窗口 |
| prompt caching | 固定前缀保持静态、顺序不变，只付新增 token | 缓存未命中＝系统 bug；长对话成本的关键 |
| compaction | 窗口满时把历史总结压缩 | 决定 agent 能跑多久而不降智 |
| 记忆分层 | 核心事实常驻 + 日期日志 + 临时便签 + 文件检索 | 用最少 token 保持长期记忆的召回 |
| delete the product | 假定今天的模型是最差的，为下一代模型设计 | 架构决策会复利，宁可少建也要留出重写空间 |

## 可直接抄的做法（可操作清单）

- 长任务用 durable workflow（Temporal）而非普通 job queue，保证重试从断点继续（16:30）。
- 把 agent loop 放服务端，把重执行环境放可快照的 VM，两者解耦（15:00）。
- 客户端只实现 send to user 一个工具，其余渲染与交互收在客户端（18:45）。
- 每条消息只注入工具名，schema 放文件按需读取（21:00）。
- 检索按成本阶梯走：历史 → 插件/API → web search → 浏览器 → 整机 shell → 问用户（21:45）。
- 读网页优先取 accessibility tree，其次 HTML，最后才截屏/按像素点击（22:30）。
- turn 内不增删工具；裁剪超长的工具描述与 schema（25:30）。
- 把 system prompt / 工具定义做成静态前缀、固定顺序、分段 hash；A/B 测试不要插队打乱顺序（28:30–30:45）。
- 用户开始打字时预热 prompt 缓存（30:45）。
- 在缓存仍热的窗口内主动做 compaction（32:15）。
- 记忆分三层：核心事实 / 日期日志 / 临时便签，其余落文件（33:00）。
- 长输出写文件而不是塞进上下文；昂贵操作（截图、大工具调用）外包给 subagent（29:15）。
- 错误信息写成「给人类看的具体指引」，agent 同样受益（26:15）。
- 不可信输入（邮件、网页）当数据不当指令；不可逆动作先出草稿让人批（27:00）。
- 主 agent 低延迟、helper 高延迟容忍，分别优化推理（35:15）。
- 每个 bug 转成 eval，内环修 harness、外环训模型（36:00）。

## 金句

> "It's not the late that you close your laptop and the process stops… I want to talk about how to extend this to this new type of agent which is always on."
（00:00）你一合上笔记本进程就停了——我要讲的是怎么把它扩展成「常驻」这一类 agent。
"It's actually more secure than the fatigue of having to watch hundreds of shell commands and approve each one."
（05:15）它其实比「盯几百条 shell 命令逐条批准」带来的疲劳更安全。
"So there's one tool that communicates between the client and the server and it's just 'send to user'."
（18:00）客户端和服务器之间只有一个工具在通信，就是「发给用户」。
"If there's a cache miss it's kind of like a bug in the system really."
（29:15）出现一次缓存未命中，本质上就相当于系统里有个 bug。
"You kind of have to internalize and assume that the models today are the worst they'll ever be."
（37:30）你必须内化一个假设：今天的模型，是它们未来最差的样子。
"It's more important than ever to think about the broader system design and the architecture of the code that you're working on because the decisions you make there will really compound."
（43:30）现在比以往任何时候都更要想清楚更大范围的系统设计与架构，因为你在这里做的决策会复利。
