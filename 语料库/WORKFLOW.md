# 英语作文语料库 · 执行手册

> 2026-11-02 重建版。判定标准见 [PROMPT](PROMPT.md)，本文件是操作 SOP。

## 一、目录约定

```
语料库/
├── PROMPT.md               规范（不改）
├── WORKFLOW.md             本文件
├── INDEX.md                总索引
├── corpus/                 语料本体
│   ├── 00-跨主题句式库.md    全局共用：高频句式 + 通用理由
│   ├── 01-科技与城市生活.md
│   └── 02-劳动与社会实践.md
├── proposals/              候选，等你打勾
├── REVIEW/
│   ├── due.sh              列出今天到期的单元
│   └── recall-queue.md     遗忘曲线队列
└── images/                 原始图片、页面图
```

**vault 根目录禁止放任何文件。**

### 投料口

`/var/minis/mounts/Note/En/收集/` —— 新资料丢这里。

处理完把原文件 `mv` 到 `收集/已处理/<材料名>/`，避免重复处理。
只看 `收集/` 根目录与子目录里的新资料，跳过 `已处理/`。

## 二、处理流程

1. **扫投料**：`ls "$INTAKE"`
2. **提取**：版书图片用 `apple-vision ocr` 识别
3. **按 What→How→Effect→Value 提炼**，只挑值得掌握的
4. **写候选**：`proposals/<日期>-<主题>.md`，每条前面留 `- [ ]`
5. **等你打勾** → 只把打勾的并入 `corpus/`
6. **更新一级标题**为该类别最新修改日期，如「科技与城市生活 2026.11.2」
7. **登记复习队列**：`REVIEW/recall-queue.md`

## 三、复习队列格式

**表格结构不能改**，`due.sh` 靠它解析：

```
| unit_id | type | 来源文件 | 单元 | learned | interval | next_recall | last_result | notes |
```

`type` 取值：`example` 事例 · `reason` 理由 · `sentence` 句式 · `error` 避坑

看今天到期：

```bash
TODAY=$(date +%F) sh REVIEW/due.sh
```

## 四、质量线

- **每个单元都要能直接搬进考场作文**，不能只是「知道有这么个说法」
- 一条事例配一条理由，避免只有事例没有论证
- 中文释义给到位，但不要逐字翻译整句
- 同类内容合并，不要拆成多条碎片
