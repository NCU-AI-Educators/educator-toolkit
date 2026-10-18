# Textbook SVG 高校教材与高密度写作双轨制配图技能

> **面向高校纸质/电子教材（SSOT Markdown → Typst PDF / Word DOCX）与深度研究报告的双轨制高质量配图与印刷门禁引擎**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://www.python.org/)
[![SVG](https://img.shields.io/badge/Output-Pure%20SVG%20%2B%202x%20Retina%20PNG-10B981.svg)](#)
[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](../../LICENSE)

---

## 📖 技能定位

在高校教材编写、课程讲义（SSOT Markdown）沉淀以及深度技术规划报告写作中，配图往往面临两极分化的痛点：
- **简单概念图过重或乱码**：传统绘图工具生成的简单概念图带有沉重的 HTML/JS 外壳，或因包含 Emoji 导致 Typst / LaTeX 编译 PDF 时出现黑框“豆腐块”乱码与文字超框；
- **复杂架构图缩印后“字如蚂蚁”**：多层系统架构图若直接画在 `1300px~1600px` 的宽画布上，嵌入 A4 页面或 Markdown 正文后会被强制缩小至 50%~60%，导致原本 `12px` 的文字缩成无法辨认的 `6px` 蚂蚁字。

**Textbook SVG（`/textbook-svg`）** 提供 **双轨制（Dual-Track）绘图引擎**，兼顾极简概念图的轻量原生矢量与复杂系统图的高信息密度排版，并内置严格的印刷安全与字号门禁。

---

## ✨ 核心特性：双轨制绘图引擎

### 1. Track A：轻量极简纯 SVG 概念图（`700px~760px` 原生 `.svg`）
- **适用场景**：单概念模型、3~4 节点流程或对比（总卡片数 $\le 4$ 张，单行精炼短语 $\le 14\sim20$ 字）；
- **内置四大教材构图母版**：
  - `pillars`：横向三支柱 / 阶段演进图（可选底部虚线反馈回流闭环）
  - `matrix`：2×2 四象限概念矩阵图
  - `branch`：纵向条件分支 / 路由流程图
  - `contrast`：左右二元正反 / 演进对比图
- **零外部依赖与四项印刷门禁（`lint`）**：生成 60~95 行纯正原生 SVG XML（4~7 KB），自动拦截 XML 结构异常、Emoji 豆腐块乱码、文本箭头与矢量路径方向冲突以及卡片文字超框。

### 2. Track B：高信息密度“1+N 总分架构图组”（`880px` 黄金窄画布）
- **适用场景**：跨 3~4 个系统层级的复合架构、包含完整算法/物理机制长句、跨项目/多团队落地分流矩阵；
- **严防缩印字小（`880px` 黄金窄画布 + 大字号体系）**：画布宽度严格锁定 `880px`（与 A4/Markdown 正文版心接近 1:1），配合 `13px~19.5px` 大字号层级，彻底根治宽图缩印后字号过小的痛点；
- **“1 张全景总图 + N 张专题子图”解耦范式**：
  - `html-overview`：总图（全景多层架构骨架与子图纯语义导航索引）
  - `html-stack`：专题子图①（上下游深度堆叠与双向桥接）
  - `html-primitives`：专题子图②（编号工程原语 + 2×2 物理矩阵）
  - `html-matrix`：专题子图③（多通道分流与交付物矩阵）
  - `html-infographic`：数据信息图（KPI 核心指标看板 + 定量阶梯条形图）
- **DOM-to-Pure-SVG 矢量编译 + 2x Retina PNG 双输出（`render-html`）**：利用无头浏览器计算 Flexbox/Grid 自动折行坐标后，一键同步导出 **100% 纯正原生 `<svg>` 矢量图（无 `<foreignObject>`）** 与 **`2x Retina .png` 高清位图**，并实时校验画布宽度、最小字号（$\ge 12\text{px}$）与零水平溢出门禁。

---

## 📂 技能包目录结构

```text
skills/textbook-svg/
├── SKILL.md                             # Agent 技能主定义（双轨制选型决策树、色板预算与红线规范）
├── README.md                            # 本文档（原理、特性与使用说明）
├── references/
│   ├── archetypes.md                    # Track A 四大纯 SVG 构图母版详解
│   ├── high_density_templates.md        # Track B 880px 高密度 1+N 母版详解
│   └── design_tokens.md                 # 六色柔和学术语义色板与字号规范
└── scripts/
    └── svg_tool.py                      # 母版脚手架生成 (scaffold)、SVG 门禁 (lint) 与 HTML 双模渲染 (render-html)
```

---

## 💬 智能体交互指南：自然语言与命令行

### 1. 自然语言直接触发
- **绘制极简概念图（Track A）**：
  > *“请用 textbook-svg 为教材第 2 章画一张横向三支柱概念图，展示感知、决策、控制的闭环关系，并通过印刷门禁校验。”*
- **绘制高密度 1+N 系统架构图组（Track B）**：
  > *“这张端云协同四层架构加 10 支队伍分工图信息量太大，请用 textbook-svg 的 880px 1+N 模式拆分为 1 张全景总图和 3 张专题子图，导出高清 PNG 与纯矢量 SVG 并随文就近嵌入。”*

### 2. 终端命令行直接运行 (`scripts/svg_tool.py`)

```bash
# 【Track A：纯 SVG 极简概念图】
# 1A. 生成纯 SVG 教材构图母版骨架 (pillars / matrix / branch / contrast)
uv run skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype pillars --feedback-loop \
  --output path/to/fig_three_pillars.svg

# 2A. 执行四项印刷安全与排版门禁校验
uv run skills/textbook-svg/scripts/svg_tool.py lint \
  path/to/image_dir/ --output /tmp/svg_lint_report.json

# 【Track B：880px 高信息密度 1+N 架构图组】
# 1B. 生成 880px 高密度 HTML 母版骨架 (html-overview / html-stack / html-primitives / html-matrix / html-infographic)
uv run skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype html-overview \
  --output path/to/assets/fig_overview.html

# 2B. 一键编译导出 2x Retina .png 与纯正原生 .svg，并执行三项排版门禁校验
uv run skills/textbook-svg/scripts/svg_tool.py render-html \
  path/to/assets/ --output /tmp/html_render_report.json
```
