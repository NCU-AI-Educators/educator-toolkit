# Textbook SVG 教材、高密度报告与顶刊论文三轨制矢量配图技能

> **面向高校纸质/电子教材（SSOT Markdown → Typst PDF / Word DOCX）、深度研究报告与顶会顶刊学术论文（Nature / IEEE / CVPR / arXiv LaTeX PDF）的三轨制矢量配图与印前门禁引擎**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://www.python.org/)
[![Vector Output](https://img.shields.io/badge/Output-Type42%20PDF%20%2B%20Pure%20SVG%20%2B%20Retina%20PNG-10B981.svg)](#)
[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](../../LICENSE)

---

## 📖 技能定位

在高校教材编写、课程讲义（SSOT Markdown）沉淀、深度技术规划报告写作以及 SCI/顶会学术论文投稿中，原理与架构配图往往面临三类典型痛点：
- **简单概念图过重或乱码**：传统绘图工具生成的简单概念图带有沉重的 HTML/JS 外壳，或因包含 Emoji 导致 Typst / LaTeX 编译 PDF 时出现黑框“豆腐块”乱码与文字超框；
- **复杂架构图缩印后“字如蚂蚁”**：多层系统架构图若直接画在 `1300px~1600px` 的宽画布上，嵌入 A4 页面或 Markdown 正文后会被强制缩小至 50%~60%，导致原本 `12px` 的文字缩成无法辨认的 `6px` 蚂蚁字；
- **顶刊论文架构图（Figure 1 / Figure 2）字体拒收与视觉割裂**：学术论文需要嵌入无限清晰的可选中矢量 PDF，但常见绘图方式易混入期刊拒收的 `Type 3` 点阵字体、缩印至 `6.37~7.20 in` 栏宽后数学上下标难以辨认，或与论文后半部分的定量实验图色板风格脱节。

**Textbook SVG（`/textbook-svg`）** 提供 **三轨制（Tri-Track）绘图与出版门禁引擎**，一站式覆盖极简概念图、高信息密度 `1+N` 报告图组与顶刊论文机制/模型架构图，并内置严格的印刷安全、字体嵌入与字号门禁。

---

## ✨ 核心特性：三轨制绘图引擎

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

### 3. Track C：顶刊论文机制原理图与模型架构图（`Python + Matplotlib` 矢量几何图元）
- **适用场景**：*Nature Machine Intelligence*、*Nature Communications*、*IEEE*、*CVPR/ICML/NeurIPS*、*arXiv* 等学术论文的 `Figure 1`（领域瓶颈机制对比 + 跨学科几何先验图元）与 `Figure 2`（双轨神经网络、状态寄存器、可微物理算子、`sg(·)` 梯度隔离与正交流形架构图）；
- **与 `figures4papers` 100% 视觉同源**：共享 12 色顶刊学术语义色板（`#0F4D92` 耶鲁深蓝、`#2A8C82` 青绿算子、`#B64342` 深红基线痛点、`#D49A35` 琥珀金梯度门控）、`Helvetica` 无衬线字体与无衬线数学公式（`mathtext.fontset="dejavusans"`）、粗体小写面板标号 `a, b`；
- **丰富几何图元与正交白桥布线（`paper_primitives.py`）**：提供跨学科 `matplotlib.patches` 几何绘制范式（细胞核/高尔基晕/颗粒/标尺、AMR 多尺度网格/地形断面/通量矢量、寄存器芯片/掩码注意力矩阵/正交子空间），内置 `shrinkA=0, shrinkB=0` 边界紧贴箭头与 `overpass_pts` 白色跨线桥；
- **反向字号预算与四重 PDF 印前门禁（`paper_schematic_tool.py`）**：基于目标期刊栏宽反向核算源字号（$f_{\text{src}} \ge f_{\text{print,min}} / s$），自动执行 `pdfinfo` 缩放比核算、`pdffonts` Type 42 嵌入核查（严禁 `Type 3` 与 `0 fonts` 转曲陷阱）、源码 AST `fontsize=` 逐行审计及 `pdftoppm` 200 DPI 视觉碰撞预览。

---

## 📂 技能包目录结构

```text
skills/textbook-svg/
├── SKILL.md                               # Agent 技能主定义（三轨制选型决策树、色板预算与红线规范）
├── README.md                              # 本文档（原理、特性、使用说明与致谢）
├── examples/
│   └── plot_cytomorph_former_fig1.py      # Track C 顶刊双面板 Figure 1 完整实战脚本参考
├── references/
│   ├── archetypes.md                      # Track A 四大纯 SVG 构图母版详解
│   ├── high_density_templates.md          # Track B 880px 高密度 1+N 母版详解
│   ├── open_source_svg_landscape.md       # 开源矢量图形生态调研参考
│   └── track_c_paper_schematics.md        # Track C 反向字号公式、跨学科几何图元配方与正交跳线指南
└── scripts/
    ├── svg_tool.py                        # Track A/B 母版脚手架 (scaffold)、SVG 门禁 (lint) 与 HTML 渲染 (render-html)
    ├── paper_primitives.py                # Track C 可复用 Matplotlib 矢量图元库、色板与字号预算函数
    └── paper_schematic_tool.py            # Track C 论文原理图字号预算 (budget)、脚手架 (scaffold) 与 PDF 印前门禁 (preflight)
```

---

## 💬 智能体交互指南：自然语言与命令行

### 1. 自然语言直接触发
- **绘制极简概念图（Track A）**：
  > *“请用 textbook-svg 为教材第 2 章画一张横向三支柱概念图，展示感知、决策、控制的闭环关系，并通过印刷门禁校验。”*
- **绘制高密度 1+N 系统架构图组（Track B）**：
  > *“这张端云协同四层架构加 10 支队伍分工图信息量太大，请用 textbook-svg 的 880px 1+N 模式拆分为 1 张全景总图和 3 张专题子图，导出高清 PNG 与纯矢量 SVG 并随文就近嵌入。”*
- **绘制顶刊学术论文 Figure 1 / Figure 2（Track C）**：
  > *“请用 textbook-svg 的 Track C 为我们投往 Nature Machine Intelligence 的论文绘制双栏 Figure 1（目标栏宽 7.20 in，最小印刷字号 6.0 pt）：面板 a 对比传统 ViT 网格跨界泄漏与领域物理先验，面板 b 展示双轨网络与可微算子架构，导出 Type 42 矢量 PDF 并通过 preflight 门禁校验。”*

### 2. 终端命令行直接运行 (`uv run`)

```bash
# 【Track A：纯 SVG 极简概念图】
uv run skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype pillars --feedback-loop \
  --output path/to/fig_three_pillars.svg
uv run skills/textbook-svg/scripts/svg_tool.py lint \
  path/to/image_dir/ --output /tmp/svg_lint_report.json

# 【Track B：880px 高信息密度 1+N 架构图组】
uv run skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype html-overview \
  --output path/to/assets/fig_overview.html
uv run skills/textbook-svg/scripts/svg_tool.py render-html \
  path/to/assets/ --output /tmp/html_render_report.json

# 【Track C：顶刊论文机制原理图与模型架构图】
# 1C. 反向核算源字号预算
uv run skills/textbook-svg/scripts/paper_schematic_tool.py budget \
  --target-width-in 7.20 --fig-width-in 14.0 --min-print-pt 6.0 \
  --output /tmp/fig1_budget.json

# 2C. 生成自包含 Matplotlib 脚本并渲染 PDF/SVG/PNG
uv run skills/textbook-svg/scripts/paper_schematic_tool.py scaffold \
  --layout dual-panel --target-width-in 7.20 \
  --script-out path/to/plot_fig1.py --output /tmp/fig1_scaffold.json
uv run --with matplotlib --with numpy path/to/plot_fig1.py

# 3C. 执行 PDF 印前字体与字号门禁并导出 200 DPI 预览图
uv run skills/textbook-svg/scripts/paper_schematic_tool.py preflight \
  --pdf path/to/plot_fig1.pdf --script path/to/plot_fig1.py \
  --target-width-in 7.20 --min-print-pt 6.0 \
  --preview-dir /tmp/fig1_preview --output /tmp/fig1_preflight.json
```

---

## 🙏 致谢 (Acknowledgements)

**Track C（顶刊论文机制原理图与模型架构图）** 所共享的顶会顶刊学术语义色板（`PALETTE`）、无衬线版式美学与科研图表出版设计原则，致敬并感谢 **耶鲁大学刘晨博士（Dr. Chen Liu, Yale University）** 及其开源项目 **[`figures4papers`](https://github.com/ChenLiu-1996/figures4papers)**（采用 CC BY-NC 4.0 许可协议）。通过与配套技能 `/figures4papers` 保持 100% 色彩与字体同源，`textbook-svg` Track C 让论文开篇的定性架构原理图与后文的定量实验统计图实现了严谨、统一的顶刊出版级视觉语言。
