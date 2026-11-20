---
name: textbook-svg
description: >-
  绘制面向高校教材、课程讲义（SSOT Markdown）、深度研究报告与顶会顶刊学术论文（Nature/IEEE/CVPR/arXiv）的高质量矢量配图。内置三轨制（Tri-Track）绘图与出版门禁引擎：（1）Track A 极简纯 SVG 概念图（横向三支柱 pillars、2×2 四象限矩阵 matrix、纵向条件分支 branch、左右正反对比 contrast，700~760px 原生 XML）；（2）Track B 高信息密度写作配图（880px 黄金窄画布大字号体系 + “1 张全景总图 + N 张专题子图”解耦范式 + HTML/CSS 2x Retina PNG 与纯正原生 SVG 双导出，含 html-overview / html-stack / html-primitives / html-matrix / html-infographic 母版）；（3）Track C 顶刊论文机制原理图与模型架构图（Python + Matplotlib 纯矢量几何图元直出 Type 42 PDF/SVG/PNG，内置印刷缩印字号反向预算、与 figures4papers 100% 视觉同源色板、正交跳线白桥与 pdffonts/pdftoppm 印前门禁）。当需要为教材正文、技术报告或学术论文绘制概念图、系统架构图、多维拆解图、论文 Figure 1/2 机制与网络架构图，或解决复杂大图“缩印后字号过小”与 PDF Type 3 字体问题时触发。
---

# Textbook SVG (教材、高密度报告与顶刊论文三轨制矢量配图技能)

## Overview

`textbook-svg` 专为 **高校纸质/电子教材（SSOT Markdown → Typst PDF / Word DOCX）、深度工程研究报告及顶会顶刊学术论文（LaTeX PDF）** 打造。针对从“单一概念示意”、“超复杂多层系统报告”到“顶刊论文机制与模型架构图（Figure 1 / Figure 2）”的不同出版介质需求，提供 **三轨制（Tri-Track）绘图与印刷门禁引擎**：

1. **Track A：轻量极简纯 SVG 概念图（`700px～760px` 原生 `.svg`）**
   - **适用场景**：单概念模型、3～4 节点流程或对比，每张卡片仅需 3～4 条精炼短语（`• 四字粗体锚点 | 8~12字释义`）；
   - **核心优势**：60～95 行纯正原生 SVG XML（4～7 KB），零外部渲染依赖，内置 `lint` 门禁自动拦截乱码字符与文字超框。
2. **Track B：高信息密度“1+N 总分架构图组”（`880px` 黄金窄画布 HTML/CSS → 同时输出 `2x Retina .png` + `纯正原生 .svg`）**
   - **适用场景**：多层复合系统架构（如 `Tier 1~Tier 4` 端云协同）、包含完整技术机制长句（单条 >20 字）、跨项目/多团队落地分流矩阵（如 `1+1+N` 10 队裂变）；
   - **核心优势**：
     - **HTML/CSS 排版爽快感 + 纯正原生 `.svg` 矢量输出**：内置 `DOM-to-Pure-SVG` 矢量编译引擎，在无头浏览器中读取 Flexbox/Grid 自动排版与 `Range.getClientRects()` 逐行折行坐标后，直接编译生成 **100% 纯正的 `<svg>` 矢量图（由原生 `<rect>`、`<line>`、`<linearGradient>`、`<clipPath>` 与 `<text>` 构成，不含 `<foreignObject>`）**，同时自动净化 Emoji 乱码并通过 `lint` 印刷安全门禁，且同步输出 `2x Retina .png`；
     - **严防缩印字小（`880px` 黄金窄画布）**：画布宽度严格锁定 `880px`（与 Markdown/A4 正文版心接近 1:1），配合 `13.5px～19.5px` 大字号层级，彻底根治宽画布（`1300px+`）塞入文档后字号被缩成 `6px` 蚂蚁字的痛点；
     - **“1 张全景总图 + N 张专题子图”解耦范式**：拒绝将过多层级硬塞进单张超长图，通过 1 张总图建立骨架与子图导航索引（`详见图 Xa/Xb/Xc`），配合 3 类大字号专题子图随文就近嵌入。
3. **Track C：顶会顶刊学术论文机制原理图与模型架构图（`Python + Matplotlib` 矢量几何图元 → `Type 42 .pdf` + `.svg` + `320 DPI .png`）**
   - **适用场景**：英文/中文学术论文（*Nature Machine Intelligence*、*Nature Communications*、*IEEE*、*CVPR/ICML/NeurIPS*、*arXiv*）的 `Figure 1`（领域痛点机制对比 + 物理/生物几何先验示意）与 `Figure 2`（双轨神经网络、可微物理算子、状态寄存器、`sg(·)` 梯度隔离与正交流形架构图）；
   - **核心优势**：
     - **与 `figures4papers` 100% 视觉同源**：共享完全一致的 12 色学术语义色板（`#0F4D92` 耶鲁深蓝主模型、`#2A8C82` 青绿算子/寄存器、`#B64342` 深红基线痛点、`#D49A35` 琥珀金梯度门控）、`Helvetica` 无衬线字体族、无衬线数学公式（`mathtext.fontset="dejavusans"`）及小写粗体面板标号（`a`, `b`），确保论文中定性架构图与定量实验图浑然一体；
     - **反向印刷字号预算与自动化印前门禁（`paper_schematic_tool.py`）**：基于目标期刊栏宽（`7.20 in` / `6.37 in` / `3.50 in`）反向锁定画布最小字号，自动执行 `pdfinfo` 尺寸缩放比核算、`pdffonts` Type 42 嵌入核查（严厉阻断 Type 3 字体与 0 字体转曲陷阱）、源码 AST `fontsize=` 逐行审计及 `pdftoppm` 200 DPI 视觉碰撞预览。

---

## Dependencies

- **`uv`** (`~/.gemini/config/plugins/science/skills/uv/SKILL.md`)：统一通过 `uv run` 执行本技能的所有 CLI 工具与 Matplotlib 绘图脚本，严禁裸调系统 `python`；
- **`figures4papers`** (`~/.gemini/config/skills/figures4papers/SKILL.md`)：绘制同一篇学术论文中的定量实验对比图（柱状图、消融图、折线图、热力图、3D 流形散点图）；Track C 与其共享色板与字体规范以保障全篇视觉统一；
- **`typst`** (`~/.gemini/config/skills/typst/SKILL.md`)：将包含 `.svg` 或 `2x Retina .png` 插图的 SSOT Markdown 文档编译为 A4 双面印刷级 PDF；
- **`docx`** (`~/.gemini/config/skills/docx/SKILL.md`)：将包含插图的文档编译为出版级 Word 文档；
- **`lecture-ssot-distiller`** (`.agents/skills/lecture-ssot-distiller/SKILL.md`)：在将课件视觉组件或复杂报告提炼为教材插图时调用本技能。

---

## Quick Start

```bash
# 【Track A：纯 SVG 极简概念图】
# 1A. 生成四大纯 SVG 教材构图母版骨架 (pillars / matrix / branch / contrast)
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype pillars --feedback-loop \
  --output path/to/fig_three_pillars.svg

# 2A. 对单个 SVG 或目录执行印刷安全与排版门禁校验
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py lint \
  path/to/image_dir/ --output /tmp/svg_lint_report.json

# 【Track B：880px 高信息密度 1+N 架构图组】
# 1B. 生成 880px 高密度 HTML 母版骨架 (html-overview / html-stack / html-primitives / html-matrix / html-infographic)
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype html-overview \
  --output path/to/assets/fig3_overview.html

# 2B. 一键同时编译导出 2x Retina .png 与纯正原生矢量 .svg，并执行排版与印刷门禁校验
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py render-html \
  path/to/assets/ --output /tmp/html_render_report.json

# 【Track C：顶刊论文机制原理图与模型架构图 (Matplotlib Vector PDF/SVG)】
# 1C. 根据目标期刊栏宽 (如 Nature 双栏 7.20 in / arXiv 6.37 in) 反向核算源字号预算
uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py budget \
  --target-width-in 7.20 --fig-width-in 14.0 --min-print-pt 6.0 \
  --output /tmp/fig1_budget.json

# 2C. 生成 100% 自包含可运行的论文原理图/架构图脚本骨架 (dual-panel / multi-stage) 并渲染
uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py scaffold \
  --layout dual-panel --target-width-in 7.20 \
  --script-out path/to/plot_fig1.py --output /tmp/fig1_scaffold.json
uv run --with matplotlib --with numpy path/to/plot_fig1.py

# 3C. 执行 PDF 印前门禁 (Type 42 字体嵌入 + AST 字号下限 + pdftoppm 200 DPI 预览图导出)
uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py preflight \
  --pdf path/to/plot_fig1.pdf --script path/to/plot_fig1.py \
  --target-width-in 7.20 --min-print-pt 6.0 \
  --preview-dir /tmp/fig1_preview --output /tmp/fig1_preflight.json
```

---

## Tri-Track Selection Decision Tree

### 1.1 何时选择 Track A vs Track B vs Track C？（及外部边界路由）

| 决策维度 | **Track A：纯 SVG 极简概念图** | **Track B：`880px` 高密度 `1+N` 图组** | **Track C：顶刊论文机制与模型架构图** |
| :--- | :--- | :--- | :--- |
| **目标出版载体** | 教材章节正文、课程讲义、轻量技术笔记 | 深度研究报告、工程规划书、多团队实施方案 | **SCI/顶会 LaTeX 论文（Nature/IEEE/CVPR/arXiv）** |
| **节点与几何复杂度** | 单层/双层概念卡片，总卡片数 **$\le 4$ 张** | 跨 **3～4 个系统层级**，或总模块/子团队数 **$\ge 6$ 个** | 含 **定制科学几何图元**（细胞核/网格/流形/注意力矩阵）+ **多分支正交算子拓扑** |
| **文本与数学公式** | 每行 **$\le 14\sim20$ 个汉字** 短语，无复杂公式 | 中文长句自动折行（单条 >20 字）、KPI 看板 | **高频 LaTeX 数学符号**（$\mathbf{P}^{(l)}, \mathrm{sg}(\cdot), \mathbf{h}_1\perp\mathbf{h}_2$）+ 精确模块参数量 |
| **核心输出与门禁** | 单张 `.svg`（`700~760px`）+ `svg_tool.py lint` | `1+N` 图组（锁宽 `880px`，`.png` + `.svg`）+ `render-html` | `Type 42 .pdf` + `.svg` + `320 DPI .png` + `paper_schematic_tool.py preflight` |

> **跨技能边界路由提示**：若需基于真实定量实验数值绘制统计柱状图、消融实验图、收敛折线图、热力图或 3D 散点图，请路由至 **`figures4papers`**；若需绘制可交互 HTML 系统拓扑、API 时序图（`sequenceDiagram`）或状态机，请路由至 **`archify`**。

---

### 1.2 Track A：四大纯 SVG 极简教材母版（详见 [`references/archetypes.md`](./references/archetypes.md)）

| 母版代号 | 母版名称 | 推荐画布 (`viewBox`) | 适用教学场景 | 典型布局特征 |
| :---: | :--- | :---: | :--- | :--- |
| **`pillars`** | **横向三支柱 / 阶段演进图**<br>*(可选底部虚线回流闭环)* | `0 0 760 212`<br>*(带回流 `0 0 760 250`)* | 三大支柱、三级演进、人机机三方协同闭环 | 3 张 `212×172` 圆角卡片等距横排，间距 `51px` 容纳水平箭头与上下双标签；底部可加从右向左的虚线反馈回路 |
| **`matrix`** | **2×2 四象限概念矩阵图** | `0 0 700 360` | 四大核心数据类型、四类防御准则、四层架构对比 | 4 张 `324×152` 圆角卡片按 2×2 网格对称排列，四象限分别采用蓝、绿、琥珀、紫四套学术语义配色 |
| **`branch`** | **纵向条件分支 / 路由流程图** | `0 0 740 310` | `if-elif-else` 短路分流、多路指令路由、异常处理流 | 顶部横幅总纲，左侧纵向排列蓝色判定框，向右引出绿色 `True` 执行框，向下引出红色 `False` 箭头，右侧总线汇总跳出 |
| **`contrast`** | **左右二元正反 / 演进对比图** | `0 0 740 216` | 痛点反例 vs 工程正例、散乱变量 vs 字典封装、静态 vs 动态 | 左右 2 张 `320×176` 对称卡片（左侧玫瑰红表示痛点或旧方案，右侧翡翠绿表示推荐方案），中间配演进箭头 |

---

### 1.3 Track B：四大 `880px` 高信息密度 `1+N` 母版（详见 [`references/high_density_templates.md`](./references/high_density_templates.md)）

当面对复杂架构图（如“端云协同三层系统 + 三大硬件原语 + 10 支队伍分流矩阵”）时，**严禁将所有细节堆砌在一张宽画布大图里**，必须按以下 `1+N` 母版体系解耦并随文就近嵌入：

| 母版代号 | 角色定位 | 画布尺寸 | 适用场景与核心结构特征 |
| :---: | :--- | :---: | :--- |
| **`html-overview`** | **总图 (`Fig X`)：全景多层架构与子图索引** | `width: 880px`<br>*(高约 `950~1150px`)* | **建立全局骨架**：纵向排布 3～4 个语义色带层级（`Tier 1~Tier 4`），每层内部采用等宽 3 栏摘要卡片（仅保留标题 + 2 行核心词 + **`详见图 Xa/Xb/Xc` 导航角标**），层间配胶囊流向条（`flow-bar`）。**嵌入在架构总论开篇处**。 |
| **`html-stack`** | **子图① (`Fig Xa`)：上下游深度堆叠与双向桥接** | `width: 880px`<br>*(高约 `900~1050px`)* | **深度展开核心算法/算力层**：上下两大面板（如 `System 2 云端慢思考` vs `System 1 端侧快思考`），内部采用 **全宽纵向富文本卡片栈（`card-stack`）**，右上角配赋能范围徽章，中间设双栏虚线桥接区（`模型下行 / 数据上行`）。**嵌入在端云算力表格之后**。 |
| **`html-primitives`** | **子图② (`Fig Xb`)：编号工程原语 + 2×2 物理矩阵** | `width: 880px`<br>*(高约 `900~1020px`)* | **深度展开底层物理/硬件防线**：上半部采用琥珀色 **带大号数字徽章（`1/2/3`）的全宽原语卡片**（痛点 → 机制 → 量化指标），下半部采用岩石灰 **`2×2` 网格卡片** 展示 4 类硬件外设或算力卸载方案。**嵌入在工程原语小节末尾**。 |
| **`html-matrix`** | **子图③ (`Fig Xc`)：多通道分流与交付物矩阵** | `width: 880px`<br>*(高约 `900~1050px`)* | **深度展开多课题/多团队落地映射**：按通道/赛道（`通道一 / 通道二 / 通道三`）分组，内部采用双栏或 `1+3` 卡片网格，每张卡片含 **单元名称 + 右侧负责人徽章 + 课题简介 + 底部带左边框高亮的独立交付物栏（`team-deliver`）**。**嵌入在项目/团队分流章节末尾**。 |
| **`html-infographic`** | **数据信息图：KPI 核心指标看板 + 定量阶梯条形图** | `width: 880px`<br>*(高约 `480~560px`)* | **宏观规模与定量漏斗阶梯融合展示**：顶部采用 4 栏大数字 KPI 指标卡（`25px` 粗体数字 + 焦点卡片高亮描边），底部采用带比例背景轨道、圆角彩色柱体、数值占比标签与坐标轴刻度的水平阶梯条形图，无需 `<canvas>` 即可直出纯正矢量 `.svg` 与 `2x .png`。 |

---

### 1.4 Track C：顶刊论文原理图与模型架构规范（详见 [`references/track_c_paper_schematics.md`](./references/track_c_paper_schematics.md) 与 [`examples/plot_cytomorph_former_fig1.py`](./examples/plot_cytomorph_former_fig1.py)）

| 构图骨架 (`--layout`) | 典型期刊栏宽 ($W_{\text{target}}$) | 推荐画布 ($W_{\text{fig}}\times H_{\text{fig}}$) | 适用论文图表场景与结构特征 |
| :---: | :---: | :---: | :--- |
| **`dual-panel`** | `7.20 in` (*Nature* 双栏)<br>`6.37 in` (*arXiv* A4)<br>`6.875 in` (*CVPR* 双栏) | `14.0 × 7.2 in` | **论文开篇 `Figure 1` 黄金范式**：左侧面板 **`a`** 上下对比传统基线结构瓶颈（深红 `#B64342`）与本工作领域物理/几何先验（耶鲁蓝 `#0F4D92`）；右侧面板 **`b`** 展开双轨/多阶段主干架构、寄存器总线、白桥正交跳线与底部纯语义图例。 |
| **`multi-stage`** | `7.20 in` / `7.16 in` (*IEEE*) / `3.50 in` (单栏) | `14.0 × 7.2 in`<br>*(单栏 `7.0 × 4.6 in`)* | **方法章节 `Figure 2` 算子流水线**：按 **`a` → `b` → `c`** 三阶段横向解耦“物理特征分解 → 受约束注意力/可微算子瓶颈 → 梯度隔离与正交流形预测头”。 |

- **反向字号硬性公式**：画布源字号必须满足 $f_{\text{src}} \ge f_{\text{print,min}} / (W_{\text{target}} / W_{\text{fig}})$（例如 `13.9 in` 画布缩印至 `6.37 in` arXiv 版心时缩放比为 `0.458`，源最小字号 `12.5 pt` 对应印刷 `5.7 pt`；若要求印刷 $\ge 6.0\text{ pt}$，源最小字号须 $\ge 13.5\text{ pt}$）。

---

### 1.5 学术语义色板与字号硬性预算 (Color Palette & Typography Budget)

#### (A) 柔和学术语义色板（Track A & Track B 通用）
严禁使用高饱和度刺眼纯色背景，必须使用经过对比度校验的语义配色（高对比深色文字 + 极浅色卡片底色 + `1.5px~2px` 语义描边）：

| 语义角色 | 卡片/层底色 (`fill`/`bg`) | 描边 (`stroke`/`border`) | 标题与要点粗体色 | 胶囊徽章底色/文字色 | 正文文本色 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. 皇家靛紫 (Indigo/Purple)**<br>*Tier 1 / 云端慢思考 / 高阶抽象* | `#F5F3FF` / `#FAF5FF` | `#8B5CF6` / `#A855F7` | `#4C1D95` / `#6D28D9` | `#EDE9FE` / `#5B21B6` | `#1E293B` |
| **2. 天际蓝 (Sky Blue)**<br>*Tier 2 / 实时感知 / 主干建模* | `#F0F9FF` | `#0284C7` | `#0C4A6E` / `#0369A1` | `#E0F2FE` / `#0369A1` | `#082F49` |
| **3. 琥珀金 (Amber Gold)**<br>*Tier 3 / 物理原语 / 安全联锁* | `#FFFBEB` | `#D97706` / `#F59E0B` | `#78350F` / `#B45309` | `#FEF3C7` / `#92400E` | `#1E293B` |
| **4. 翡翠绿 (Emerald Green)**<br>*Tier 4 / 正例方案 / 专项分流* | `#ECFDF5` | `#059669` / `#10B981` | `#064E3B` / `#047857` | `#D1FAE5` / `#065F46` | `#064E3B` |
| **5. 玫瑰红 (Rose Red)**<br>*痛点反例 / False 未命中 / 风险阻断* | `#FEF2F2` | `#EF4444` | `#B91C1C` / `#DC2626` | `#FEE2E2` / `#991B1B` | `#7F1D1D` |
| **6. 岩石灰 (Slate Neutral)**<br>*硬件外设池 / 顶部横幅 / 桥接总线* | `#F8FAFC` | `#64748B` / `#CBD5E1` | `#0F172A` / `#1E293B` | `#E2E8F0` / `#1E293B` | `#334155` |

#### (B) Track A & Track B 字号与画布宽度硬性预算（防缩印字小铁律）
1. **Track A（纯 SVG，`width: 700px~760px`）**：
   - 卡片标题 `15px~15.5px`（粗体居中），正文条目 `13px~13.5px`，连线标签 `12px`；
   - 三栏卡片（宽 `212px`）单行严格 $\le 14$ 个汉字；双栏/矩阵卡片（宽 `324px`）单行严格 $\le 20$ 个汉字。
2. **Track B（高密度 HTML/PNG，`width: 880px` 黄金窄画布）**：
   - **严禁将 `.fig-card` 宽度设为 `1100px~1600px`**：画布越宽，嵌入 A4/Markdown 正文时缩放比越小，文字越模糊；必须锁定 **`width: 880px`**！
   - **大字号层级硬性标准（`render-html` 自动校验最小字号 $\ge 12\text{px}$）**：
     - 图表主标题（`.fig-header h1`）：**`19px～19.5px`**（`font-weight: 800`）
     - 图表副标题（`.fig-header .sub`）：**`13px～13.5px`**
     - 分层/面板横幅标题（`.tier-head-left` / `.panel-head-left`）：**`15.5px～16px`**（`font-weight: 800`）
     - 卡片主标题（`.detail-title` / `.prim-name` / `.node-title`）：**`14.5px～15px`**（`font-weight: 800`）
     - 卡片正文描述（`.detail-desc` / `.prim-desc` / `.node-tags`）：**`13px～13.5px`**（行高 `1.46～1.52`，核心术语用 `<strong>` 着色加粗）
     - 胶囊角标与流向标签（`.flow-chip` / `.detail-role` / `.team-deliver`）：**`12px～13px`**（`font-weight: 700`）

#### (C) Track C 顶刊色板（`scripts/paper_primitives.py` `PALETTE`）
与 `figures4papers` 100% 对齐：`ours_primary="#0F4D92"`、`ours_secondary="#3775BA"`、`positive_teal="#2A8C82"`、`positive_green="#5AA469"`、`sota_red_dark="#B64342"`、`sota_red_mid="#D96B52"`、`sota_coral="#E5988B"`、`baseline_amber="#D49A35"`、`ablation_gray="#A6AEB7"`、`dark_slate="#4A5568"`、`text_dark="#1A202C"`、`text_muted="#334155"`。

---

## Utility Scripts

### 1. Track A & Track B 工具链 (`scripts/svg_tool.py`)

#### 1.1 `scaffold`：一键生成双轨母版骨架
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype {pillars,matrix,branch,contrast,html-overview,html-stack,html-primitives,html-matrix} \
  [--feedback-loop] \
  --output path/to/output.{svg,html}
```

#### 1.2 `lint`：对 Track A (`.svg`) 执行四项印刷安全门禁校验
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py lint \
  path/to/file_or_dir \
  --output /tmp/svg_lint_report.json
```
自动检查：(1) XML 结构完整性；(2) 零 Emoji 与生僻符号（防 PDF 豆腐块乱码）；(3) 文本内箭头与矢量路径物理方向一致性；(4) 卡片文字超框预警。

#### 1.3 `render-html`：对 Track B (`.html`) 执行 2x Retina 渲染与三项排版门禁校验
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py render-html \
  path/to/html_file_or_dir \
  [--scale 2] [--max-width 900] [--min-font 12] \
  --output /tmp/html_render_report.json
```
自动完成 `.html` → 同名高清 `.png` 与纯正原生 `.svg` 转换，并在无头浏览器中实时执行三项门禁：
1. **画布宽度防缩印门禁（`canvas_too_wide`）**：若画布宽度超过 `--max-width`（默认 `900px`，推荐 `880px`），立即预警或报错，防止宽图缩印导致字小；
2. **DOM 最小字号门禁（`font_too_small`）**：遍历所有可见文本节点，拦截计算字号 `< 12px` 的微缩文字；
3. **零水平溢出门禁（`horizontal_overflow`）**：检测所有卡片与容器是否存在 `scrollWidth > clientWidth` 截断。

---

### 2. Track C 论文原理图工具链 (`scripts/paper_schematic_tool.py` & `scripts/paper_primitives.py`)

所有子命令均基于 Python 标准库实现（含 PEP 723 元数据，`uv run` 零安装秒启动），强制要求 `--output <json_path>` 写入结构化报告，校验失败时返回退出码 `1`：

#### 2.1 `budget`：印刷栏宽反向字号预算器
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py budget \
  --target-width-in 6.37 --fig-width-in 13.90 --min-print-pt 5.5 \
  --output /tmp/budget.json
```
输出缩放比例 `scale`、五级推荐源字号（`min_fine_pt`、`body_pt`、`card_title_pt`、`panel_header_pt`、`panel_letter_pt`）及主流期刊预设宽度表（`VENUE_WIDTHS_IN`）。

#### 2.2 `scaffold`：自包含 Matplotlib 矢量原理图脚手架生成器
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py scaffold \
  --layout {dual-panel,multi-stage} \
  --target-width-in 7.20 [--fig-width-in 14.0] [--fig-height-in 7.2] [--min-print-pt 6.0] \
  --script-out path/to/plot_fig1.py \
  --output /tmp/scaffold_receipt.json
```
在 `--script-out` 生成 100% 自包含可运行脚本（内联 `PALETTE`、`Type 42` 字体配置、`rounded_box`、`arrow`、带白色跨线桥 `overpass_pts` 的 `ortho_arrow`、`pill_label`、预计算字号常量与 `.pdf/.svg/.png` 三格式导出）；高级定制亦可直接导入 `scripts/paper_primitives.py`。

#### 2.3 `preflight`：PDF 矢量字体嵌入、AST 字号审计与 200 DPI 视觉碰撞预览
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py preflight \
  --pdf path/to/fig1.pdf [--script path/to/plot_fig1.py] \
  --target-width-in 6.37 --min-print-pt 5.5 [--dpi 200] \
  --preview-dir /tmp/fig1_preview \
  --output /tmp/preflight_report.json
```
自动执行四重门禁：(1) 检查 Poppler (`pdfinfo`, `pdffonts`, `pdftoppm`) 环境；(2) 解析 PDF 物理尺寸与真实缩放比 `scale`；(3) 解析 `pdffonts`，若存在 `Type 3` 字体、`0` 字体（Ghostscript 转曲/光栅化陷阱）或未嵌入字体（`emb == no`）立即报错并给出修复方案；(4) AST 静态扫描 `--script` 中所有 `fontsize=` 调用（支持常量、简单算式与字典解析），精确定位缩印后低于 `--min-print-pt` 的源码行号，并通过 `pdftoppm` 渲染高清 PNG 供智能体视觉巡检。

---

## Workflow

1. **评估目标出版载体并选定轨道**：
   - **单一概念/四象限/简单对比（节点 $\le 4$、短语 $\le 15$ 字）** → 进入 **Track A（纯 SVG）**；
   - **多层复杂系统报告、含长句机制说明或多团队/多模块分流矩阵** → 进入 **Track B（`880px` 高密度 `1+N` 图组）**；
   - **SCI/顶会论文机制原理图与网络/物理架构图（LaTeX `Figure 1` / `Figure 2`）** → 先阅读 [`references/track_c_paper_schematics.md`](./references/track_c_paper_schematics.md)，进入 **Track C（Matplotlib Vector PDF/SVG）**。
2. **生成母版骨架并填入精炼内容**：
   - Track A：调用 `svg_tool.py scaffold --archetype {pillars,matrix,branch,contrast}` 生成 `.svg`；
   - Track B：按 **“1 张全景总图（`html-overview`）+ N 张专题子图（`html-stack` / `html-primitives` / `html-matrix` / `html-infographic`）”** 规划图组；**图内标题、徽章与子图索引一律使用纯语义名称（如 `主体赛专题`、`端云算力专题子图`），绝不写入 `图 1`、`子图 2a` 等编号**；
   - Track C：先运行 `paper_schematic_tool.py budget` 锁定五级字号下限，再用 `scaffold`（或参考 [`examples/plot_cytomorph_former_fig1.py`](./examples/plot_cytomorph_former_fig1.py) 及 `paper_primitives.py`）编写绘图脚本，使用小写粗体面板标号 `a`, `b`、正交走廊布线及 `overpass_pts` 白色跨线桥，同步导出 `.pdf`, `.svg`, `.png`。
3. **运行自动化门禁校验与视觉巡检**：
   - Track A：运行 `svg_tool.py lint` 确保 0 Error；
   - Track B：运行 `svg_tool.py render-html` 导出 2x Retina `.png` 与纯矢量 `.svg` 并确保 `issues: 0`，再用 `read_file` 目视抽检 PNG；
   - Track C：运行 `paper_schematic_tool.py preflight` 确保退出码为 `0`（0 Type 3 字体、0 字号违规），随后 **必须对 `preview_images` 中的每一张 200 DPI PNG 调用 `read_file` 目视检查**，彻底消除文字压框、上下标裁切或跳线歧义。
4. **随文就近嵌入与图号解耦（Contextual Co-location）**：
   - Track A/B：切忌将 `1+N` 全部图片连续堆叠在同一段落，应将总图置于总论段末，各专题子图分别嵌入对应章节之后，仅在正文题注中赋予图号（如 `**图 2 ...**`）；
   - Track C：在 LaTeX 中使用 `\includegraphics[width=\textwidth]{figures/fig1.pdf}` 嵌入矢量 PDF，并确保图内模块名称、参数量及数学符号与 `methods.tex` / `results.tex` 100% 一致。
5. **内容同步维护纪律**：
   - 当正文或论文手稿发生术语、指标或参数微调时，**必须同步更新 `.svg` / `.html` / `plot_fig*.py` 源码并重跑门禁刷新导出产物**，严禁出现“正文已改、配图停留在旧版本”的图文割裂。

---

## Common Mistakes

1. **【红线一：宽画布缩印导致字如蚂蚁】严禁在 Track B 复杂架构图中使用超过 `900px` 的宽画布，或跳过 Track C 反向字号预算**：
   Track B 若在 `1320px～1600px` 宽画布上排 4～6 列卡片，嵌入 A4 后 `12px` 文字会缩成无法辨认的 `6px`（务必锁定 `width: 880px` 并拆分子图）；Track C 若直接在 `14 in` 画布上写 `fontsize=8` 或 `9`，缩印至 `6.37 in` 论文版心后仅剩 `3.6~4.1 pt`，必然被审稿人或编辑退回（务必先跑 `budget` 与 `preflight`）。
2. **【红线二：单图过载】严禁把超过 3 个维度的架构与 10 个落地子项硬塞进单张图，或在 Track C 底部图例中堆砌实验数值表**：
   Track B 复杂系统必须拆解为 **1 张总图 + 2～3 张大字号专题子图**；Track C 底部图例仅允许标注模块架构语义角色（5～6 项），定量对比请交由 `figures4papers` 独立成图。
3. **【红线三：纯 SVG 乱码与 PDF Type 3 / 0 字体转曲陷阱】**：
   Track A 纯 SVG 严禁使用 Emoji 及超长句子（三栏单行 $\le 14$ 汉字）；Track C 严禁漏设 `pdf.fonttype = 42` 与 `mathtext.fontset = "dejavusans"`（否则会产生出版系统拒收的 `Type 3` 点阵字体或衬线/无衬线混排），且严禁用 Ghostscript `-dNoOutputFonts` 将文字转曲成 `0 fonts` 死路径。
4. **【红线四：箭头方向反转、悬空断触与无桥十字交叉】**：
   Track A 绘制从右向左的反馈回路时，文字标签箭头须写为 `左端接收方 ◀── 右端发起方`；Track C 连线必须设置 `shrinkA=0, shrinkB=0` 紧贴模块边界，不可避免的正交跨线必须传入 `overpass_pts` 生成白色跨线桥，且严禁不看 `pdftoppm` 预览图盲交结果。
5. **【红线五：严禁图内硬编码图编号】严禁在画布标题、角标或节点引用中写入 `图 1`、`图 2a`、`子图 3b`、`Fig. 1` 等编号**：
   图片编号属于正文排版层的动态序号（Track C 仅允许顶刊标准面板字母 `a`, `b`, `c`，绝不写 `Figure 1a`），图号统一交由 Markdown / Word / Typst / LaTeX 的 `\caption{...}` 管理。
