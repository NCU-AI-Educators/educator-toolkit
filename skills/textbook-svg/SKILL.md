---
name: textbook-svg
description: >-
  绘制面向高校教材、课程讲义（SSOT Markdown）、深度研究报告与 Typst/Word/PDF 出版的高质量配图。内置双轨制绘图引擎：（1）Track A 极简纯 SVG 概念图（横向三支柱 pillars、2×2 四象限矩阵 matrix、纵向条件分支 branch、左右正反对比 contrast，700~760px 原生 XML）；（2）Track B 高信息密度写作配图（880px 黄金窄画布大字号体系 + “1 张全景总图 + N 张专题子图”解耦范式 + HTML/CSS 2x Retina 高清 PNG 渲染，含 html-overview / html-stack / html-primitives / html-matrix 四大母版）。当需要为教材正文、技术报告或规划文档绘制概念图、系统架构图、多维拆解图，或解决复杂大图“缩印后字号过小”问题时触发。
---

# Textbook SVG (高校教材与高密度写作场景双轨制配图技能)

## Overview

`textbook-svg` 专为 **高校纸质/电子教材（SSOT Markdown $\rightarrow$ Typst PDF / Word DOCX）及深度研究/工程规划报告** 打造。针对写作场景中从“单一概念示意”到“超复杂多层系统架构”的不同信息密度需求，提供 **双轨制（Dual-Track）绘图引擎**：

1. **Track A：轻量极简纯 SVG 概念图（`700px～760px` 原生 `.svg`）**
   - **适用场景**：单概念模型、3～4 节点流程或对比，每张卡片仅需 3～4 条精炼短语（`• 四字粗体锚点 | 8~12字释义`）；
   - **核心优势**：60～95 行纯正原生 SVG XML（4～7 KB），零外部渲染依赖，内置 `lint` 门禁自动拦截乱码字符与文字超框。
2. **Track B：高信息密度“1+N 总分架构图组”（`880px` 黄金窄画布 HTML/CSS $\rightarrow$ 同时输出 `2x Retina .png` + `纯正原生 .svg`）**
   - **适用场景**：多层复合系统架构（如 `Tier 1~Tier 4` 端云协同）、包含完整技术机制长句（单条 >20 字）、跨项目/多团队落地分流矩阵（如 `1+1+N` 10 队裂变）；
   - **核心优势**：
     - **HTML/CSS 排版爽快感 + 纯正原生 `.svg` 矢量输出**：内置 `DOM-to-Pure-SVG` 矢量编译引擎，在无头浏览器中读取 Flexbox/Grid 自动排版与 `Range.getClientRects()` 逐行折行坐标后，直接编译生成 **100% 纯正的 `<svg>` 矢量图（由原生 `<rect>`、`<line>`、`<linearGradient>`、`<clipPath>` 与 `<text>` 构成，不含 `<foreignObject>`）**，同时自动净化 Emoji 乱码并通过 `lint` 印刷安全门禁，且同步输出 `2x Retina .png`；
     - **严防缩印字小（`880px` 黄金窄画布）**：画布宽度严格锁定 `880px`（与 Markdown/A4 正文版心接近 1:1），配合 `13.5px～19.5px` 大字号层级，彻底根治宽画布（`1300px+`）塞入文档后字号被缩成 `6px` 蚂蚁字的痛点；
     - **“1 张全景总图 + N 张专题子图”解耦范式**：拒绝将过多层级硬塞进单张超长图，通过 1 张总图建立骨架与子图导航索引（`详见图 Xa/Xb/Xc`），配合 3 类大字号专题子图随文就近嵌入。

---

## Dependencies

- **`typst`** (`~/.gemini/config/skills/typst/SKILL.md`)：将包含 `.svg` 或 `2x Retina .png` 插图的文档编译为 A4 双面印刷级 PDF；
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
# 1B. 生成 880px 高密度 HTML 母版骨架 (html-overview / html-stack / html-primitives / html-matrix)
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype html-overview \
  --output path/to/assets/fig3_overview.html

# 2B. 一键同时编译导出 2x Retina .png 与纯正原生矢量 .svg，并执行排版与印刷门禁校验
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py render-html \
  path/to/assets/ --output /tmp/html_render_report.json
```

---

## 1. 双轨选型决策树与构图母版指南 (Dual-Track Selection & Archetypes)

### 1.1 何时选择 Track A（单张纯 SVG）vs Track B（`880px` 高密度 `1+N` 图组）？

| 决策维度 | 选择 **Track A：纯 SVG 极简概念图** | 选择 **Track B：`880px` 高密度 `1+N` 图组** |
| :--- | :--- | :--- |
| **节点与层级数量** | 单层或简单双层，总卡片数 **$\le 4$ 张** | 跨 **3～4 个系统层级**，或总模块/子团队数 **$\ge 6$ 个** |
| **单卡文本容量** | 每行可浓缩为 **$\le 14\sim20$ 个汉字** 的短语 | 含完整算法/物理机制长句、硬件型号、量化指标与交付物映射（需多行自动折行） |
| **复合维度** | 单一逻辑关系（并列、四象限、分支、对比） | 同时包含 **“端云架构层 + 底层工程原语 + 多项目/团队分流矩阵”** |
| **推荐处理方式** | 单张 `.svg`（`700px～760px`） | **拆分为 1 张总图（`Fig X`）+ 2～3 张专题子图（`Fig Xa/Xb/Xc`）**，固定 `880px` 宽 |

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
| **`html-primitives`** | **子图② (`Fig Xb`)：编号工程原语 + 2×2 物理矩阵** | `width: 880px`<br>*(高约 `900~1020px`)* | **深度展开底层物理/硬件防线**：上半部采用琥珀色 **带大号数字徽章（`1/2/3`）的全宽原语卡片**（痛点 $\rightarrow$ 机制 $\rightarrow$ 量化指标），下半部采用岩石灰 **`2×2` 网格卡片** 展示 4 类硬件外设或算力卸载方案。**嵌入在工程原语小节末尾**。 |
| **`html-matrix`** | **子图③ (`Fig Xc`)：多通道分流与交付物矩阵** | `width: 880px`<br>*(高约 `900~1050px`)* | **深度展开多课题/多团队落地映射**：按通道/赛道（`通道一 / 通道二 / 通道三`）分组，内部采用双栏或 `1+3` 卡片网格，每张卡片含 **单元名称 + 右侧负责人徽章 + 课题简介 + 底部带左边框高亮的独立交付物栏（`team-deliver`）**。**嵌入在项目/团队分流章节末尾**。 |
| **`html-infographic`** | **数据信息图：KPI 核心指标看板 + 定量阶梯条形图** | `width: 880px`<br>*(高约 `480~560px`)* | **宏观规模与定量漏斗阶梯融合展示**：顶部采用 4 栏大数字 KPI 指标卡（`25px` 粗体数字 + 焦点卡片高亮描边），底部采用带比例背景轨道、圆角彩色柱体、数值占比标签与坐标轴刻度的水平阶梯条形图，无需 `<canvas>` 即可直出纯正矢量 `.svg` 与 `2x .png`。 |

---

## 2. 学术语义色板与字号硬性预算 (Color Palette & Typography Budget)

### 2.1 柔和学术语义色板（Track A & Track B 通用）
严禁使用高饱和度刺眼纯色背景，必须使用经过对比度校验的语义配色（高对比深色文字 + 极浅色卡片底色 + `1.5px~2px` 语义描边）：

| 语义角色 | 卡片/层底色 (`fill`/`bg`) | 描边 (`stroke`/`border`) | 标题与要点粗体色 | 胶囊徽章底色/文字色 | 正文文本色 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. 皇家靛紫 (Indigo/Purple)**<br>*Tier 1 / 云端慢思考 / 高阶抽象* | `#F5F3FF` / `#FAF5FF` | `#8B5CF6` / `#A855F7` | `#4C1D95` / `#6D28D9` | `#EDE9FE` / `#5B21B6` | `#1E293B` |
| **2. 天际蓝 (Sky Blue)**<br>*Tier 2 / 实时感知 / 主干建模* | `#F0F9FF` | `#0284C7` | `#0C4A6E` / `#0369A1` | `#E0F2FE` / `#0369A1` | `#082F49` |
| **3. 琥珀金 (Amber Gold)**<br>*Tier 3 / 物理原语 / 安全联锁* | `#FFFBEB` | `#D97706` / `#F59E0B` | `#78350F` / `#B45309` | `#FEF3C7` / `#92400E` | `#1E293B` |
| **4. 翡翠绿 (Emerald Green)**<br>*Tier 4 / 正例方案 / 专项分流* | `#ECFDF5` | `#059669` / `#10B981` | `#064E3B` / `#047857` | `#D1FAE5` / `#065F46` | `#064E3B` |
| **5. 玫瑰红 (Rose Red)**<br>*痛点反例 / False 未命中 / 风险阻断* | `#FEF2F2` | `#EF4444` | `#B91C1C` / `#DC2626` | `#FEE2E2` / `#991B1B` | `#7F1D1D` |
| **6. 岩石灰 (Slate Neutral)**<br>*硬件外设池 / 顶部横幅 / 桥接总线* | `#F8FAFC` | `#64748B` / `#CBD5E1` | `#0F172A` / `#1E293B` | `#E2E8F0` / `#1E293B` | `#334155` |

### 2.2 字号与画布宽度硬性预算（防缩印字小铁律）

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

---

## 3. Utility Scripts (`scripts/svg_tool.py`)

### 3.1 `scaffold`：一键生成双轨母版骨架
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py scaffold \
  --archetype {pillars,matrix,branch,contrast,html-overview,html-stack,html-primitives,html-matrix} \
  [--feedback-loop] \
  --output path/to/output.{svg,html}
```

### 3.2 `lint`：对 Track A (`.svg`) 执行四项印刷安全门禁校验
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py lint \
  path/to/file_or_dir \
  --output /tmp/svg_lint_report.json
```
自动检查：(1) XML 结构完整性；(2) 零 Emoji 与生僻符号（防 PDF 豆腐块乱码）；(3) 文本内箭头与矢量路径物理方向一致性；(4) 卡片文字超框预警。

### 3.3 `render-html`：对 Track B (`.html`) 执行 2x Retina 渲染与三项排版门禁校验
```bash
uv run ~/.gemini/config/skills/textbook-svg/scripts/svg_tool.py render-html \
  path/to/html_file_or_dir \
  [--scale 2] [--max-width 900] [--min-font 12] \
  --output /tmp/html_render_report.json
```
自动完成 `.html` $\rightarrow$ 同名高清 `.png` 转换，并在无头浏览器中实时执行三项门禁：
1. **画布宽度防缩印门禁（`canvas_too_wide`）**：若画布宽度超过 `--max-width`（默认 `900px`，推荐 `880px`），立即预警或报错，防止宽图缩印导致字小；
2. **DOM 最小字号门禁（`font_too_small`）**：遍历所有可见文本节点，拦截计算字号 `< 12px` 的微缩文字；
3. **零水平溢出门禁（`horizontal_overflow`）**：检测所有卡片与容器是否存在 `scrollWidth > clientWidth` 截断。

---

## 4. Workflow (双轨制标准制图工作流)

1. **评估信息密度并选定轨道**：
   - 若为 **单一概念/四象限/简单对比（节点 $\le 4$、短语 $\le 15$ 字）** $\rightarrow$ 进入 **Track A（纯 SVG）**；
   - 若为 **多层复杂架构、含长句机制说明或多团队/多模块分流矩阵** $\rightarrow$ 进入 **Track B（`880px` 高密度 `1+N` 图组）**。
2. **生成母版骨架并填入精炼内容（严禁图内硬编码图编号）**：
   - Track A：调用 `svg_tool.py scaffold --archetype {pillars,matrix,branch,contrast}` 生成 `.svg`；
   - Track B：按 **“1 张全景总图（`html-overview`）+ N 张专题子图（`html-stack` / `html-primitives` / `html-matrix` / `html-infographic`）”** 规划图组；**图内标题、徽章与子图索引一律使用纯语义名称（如 `主体赛专题`、`端云算力专题子图`），绝不写入 `图 1`、`子图 2a` 等编号**。
3. **运行自动化门禁校验与渲染**：
   - Track A：运行 `svg_tool.py lint` 确保 0 Error；
   - Track B：运行 `svg_tool.py render-html` 导出 2x Retina `.png` 与纯矢量 `.svg` 并确保 `issues: 0`（再用 `view_file` 目视抽检渲染后的 PNG 图片）。
4. **随文就近嵌入 Markdown（Contextual Co-location）**：
   - **切忌将 `1+N` 全部图片连续堆叠在同一段落**！应将总图置于总论段末，各专题子图分别嵌入在各自对应的深度展开小节或表格之后，**仅在 Markdown/Word/Typst 正文题注（Caption）中赋予图号（如 `**图 2 ...**`、`**图 2a ...**`）**，确保未来正文增删插图调整编号时无需重绘图片。
5. **内容同步维护纪律**：
   - 当正文发生术语或团队表述微调（如算力修饰词调整、本硕团队角色微调）时，**必须同步检索并更新 `assets/*.html` 或 `*.svg` 源码，并重新运行 `render-html` / `lint` 刷新图片**，严禁出现“正文已改、配图仍停留在旧版本”的图文割裂。

---

## Common Mistakes (常见踩坑与红线警告)

1. **【红线一：宽画布缩印导致字如蚂蚁】严禁在复杂架构图中使用超过 `900px` 的宽画布**：
   在 `1320px～1600px` 宽画布上排 4～6 列卡片，虽然在浏览器全屏看尚可，但嵌入 A4 页面或 Markdown 阅读器后会被强制缩小至 50%～60%，原本 `12px` 的文字会变成无法辨认的 `6px`。务必固定 `width: 880px` 并采用 `1+N` 纵向展开或拆分子图。
2. **【红线二：单图过载】严禁把超过 3 个维度的架构与 10 个落地子项硬塞进单张图**：
   既想画清端云三层算法细节，又想画清底层物理原语，还想列出 10 支参赛队伍，塞进一张图必然导致要么字小如蚁、要么图片高度超过两屏。必须拆解为 **1 张总图（建立骨骼与索引）+ 2～3 张大字号专题子图**。
3. **【红线三：纯 SVG 乱码与超框】在 Track A 纯 SVG 中严禁使用 Emoji 及超长句子**：
   Typst/LaTeX 编译原生 `.svg` 时不支持 Emoji（会渲染成黑框豆腐块），且 `<text>` 不会自动换行，三栏卡片每行严禁超过 14 个汉字。若确需使用丰富图标或长句自动换行，请切换至 Track B（HTML 渲染 2x PNG + DOM-to-SVG）。
4. **【红线四：箭头方向反转】严禁文本内箭头 `──▶` 与底层矢量路径 `<path>` 方向相反**：
   绘制从右向左的底部反馈回路时，文字标签中的箭头必须与物理路径一致写为 `左端接收方 ◀── 右端发起方`。
5. **【红线五：严禁图内硬编码图编号】严禁在画布标题、角标或节点引用中写入 `图 1`、`图 2a`、`子图 3b`、`Fig. 1` 等编号**：
   图片编号属于正文排版层的动态序号，若硬编码进图片内部，一旦正文前插或删减配图导致编号顺延，所有图片都将被迫重绘。图内标题与子图交叉索引必须采用 **纯语义标签**（如 `全景架构总图`、`主体赛专题子图`、`端云算力子图`），图号统一交由正文下方的图题注（`**图 2 ...**`）管理。
