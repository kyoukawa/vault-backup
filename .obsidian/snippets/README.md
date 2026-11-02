# 阅读收集 · 样式说明

## 在 Obsidian 里怎么装

### 1. 装主题（Minimal）

设置 → 外观 → 主题 → 管理 → 搜索 `Minimal` → 使用

> Minimal 是 Obsidian 官方「最佳主题」，5.4k stars，桌面/手机/平板通用。
> 仓库：https://github.com/kepano/obsidian-minimal
> 我们只用了它的变量体系，卡片效果由本目录的 snippet 提供。

**建议再装两个配套插件**（社区插件里搜）：

- `Minimal Theme Settings` —— 调颜色、字体、行宽
- `Style Settings` —— 更细的自定义

### 2. 启用 snippet

设置 → 外观 → **CSS 片段** → 刷新 → 打开 `rc-home`

> 文件位置：`.obsidian/snippets/rc-home.css`（已放好）

### 3. 在笔记里启用

首页的 front-matter 已有：

```yaml
cssclasses:
  - rc-home
```

其他笔记想用同样样式，加这两行即可。

---

## 效果

### 桌面

表格变成卡片列表，每行一张卡：

- 标题加粗、整块可点
- 来源、作者弱化
- 日期右对齐、淡色
- 悬停整行变色

### 手机（≤640px）

自动切换成竖排卡片：

```
┌────────────────────────┐
│ 时文三则（2026-10-29）  │  ← 标题大字
│ 第三版：三处不能加速     │
│ WorkBuddy 讲义  11-02   │  ← 来源 + 日期
└────────────────────────┘
```

作者列在手机上隐藏（信息密度太高，读起来反而累）。

### 深色模式

自动跟随系统，不需要额外配置。所有颜色都取自 Minimal 的 CSS 变量。

---

## 为什么这样做

**没有自己写主题。** 三件现成的事直接用：

| 需求 | 用什么 |
|---|---|
| 整体观感 | Minimal 主题（官方最佳主题） |
| 配色跟随深浅色 | Minimal 的 CSS 变量 |
| Dataview 卡片 | Minimal 自带的 `.cards` 类 |

**只补它没做的**：普通 Markdown 表格的卡片化。Minimal 的 `cards` 类只作用于
`.dataview table`，普通表格不在范围内。

---

## 改样式

```bash
# 编辑
vim .obsidian/snippets/rc-home.css

# 预览（本地渲染，不用开 Obsidian）
cd /var/minis/workspace/css-preview
python3 render.py          # 浅色
python3 render.py --dark   # 深色
```

预览页会套上 Minimal 的变量子集，效果接近真实。

---

## 变量参考

改样式时优先复用这些，**不要写死颜色**：

| 变量 | 用途 |
|---|---|
| `--background-primary` | 卡片背景 |
| `--background-secondary` | 页面背景 |
| `--background-secondary-alt` | 悬停背景 |
| `--background-modifier-border` | 卡片边框 |
| `--text-normal` | 标题 |
| `--text-muted` | 来源、作者 |
| `--text-faint` | 日期、表头 |
| `--text-accent` | 悬停时的链接色 |
| `--radius-s` / `--radius-m` | 圆角 |
