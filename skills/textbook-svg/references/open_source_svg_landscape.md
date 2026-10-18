# 高质量 SVG 插图与教材/报告架构配图开源技术路线调研与演进指南

> **文档定位**：面向高校教材编写（SSOT Markdown $\rightarrow$ Typst PDF / Word DOCX）、学术论文插图、深度研究与工程规划报告场景，系统梳理当前开源社区中绘制高质量 SVG 矢量插图与复杂架构图的四大技术路线，并总结 `textbook-svg` 技能的实战沉淀与后续跨项目演进蓝图。

---

## 一、核心痛点：为什么写作场景中的架构配图容易“翻车”？

在编写高校教材、技术白皮书与深度规划报告时，技术配图往往面临四个典型的工程瓶颈：

1. **手写原生 `<svg>` 缺乏现代排版能力**：
   原生 SVG XML 没有 CSS 弹性盒子（Flexbox）或网格布局（Grid），更重要的是 **`<text>` 标签不支持自动换行**。一旦卡片内文字超过 14～20 个汉字，手算坐标极易导致文字刺穿卡片边框或行距失调。
2. **宽画布缩印导致“字如蚂蚁”（Wide-Canvas Shrinkage）**：
   许多绘图工具默认在 `1320px～1600px` 的宽画布上横向铺开 4～6 列内容。虽然在浏览器全屏预览时清晰，但嵌入 A4 教材版心（有效宽度约 `450pt～520pt`）或 Markdown 阅读器（约 `720px～880px`）后，整图被等比缩小至 50%～60%，原本 `12px` 的正文字号缩水为无法辨认的 `6px`。
3. **单图信息过载（Single-Diagram Overload）**：
   试图将“端云三层算法架构 + 底层物理工程原语 + 10 个落地子课题/团队矩阵”全部塞进单张图中，必然陷入“要么字小如蚁、要么图片高度超过两屏”的两难境地。
4. **跨编译链路字体与符号兼容性断裂（Emoji Tofu）**：
   浏览器支持彩色 Emoji（如 `🧠`、`🚀`、`⏱️`），但当 SVG 直接送入 Typst（`usvg`/`resvg`）或 $\LaTeX$ 编译印刷级 PDF 时，中文正文字体（如 PingFang SC、思源宋体）因缺失对应字形，会将其渲染成黑框“豆腐块”乱码。

---

## 二、四大开源高质量 SVG 制图技术路线全景调研

围绕上述痛点，当前 GitHub 开源社区已分化出四条高度互补的技术路线：

### 路线一：HTML/CSS 自动排版转纯正原生 SVG 引擎（DOM/CSS-to-SVG Engines）

**核心思想**：用人类与大模型最擅长的 **HTML + CSS（Flexbox / Grid）** 声明式编写高密度富文本卡片（享受自动折行、圆角、阴影、胶囊徽章与自适应高度），再通过布局计算引擎将其直接编译为 **100% 纯正的原生 `<svg>` 标签树（不含 `<foreignObject>`）**。

| 开源项目 | GitHub 仓库 | 核心技术机制 | 优势与局限 | 适用等级 |
| :--- | :--- | :--- | :--- | :---: |
| **Satori** | [`vercel/satori`](https://github.com/vercel/satori)<br>*(~24k Stars)* | Vercel 出品。底层采用 WebAssembly 运行 Facebook 的 **Yoga（Flexbox 布局引擎）** 与 OpenType 字体度量解析器。无需启动无头浏览器，直接将 HTML/JSX + CSS 子集计算并转换为纯正 `<svg>`（`<rect>`、`<path>`、`<text>`）。配合 [`natemoo-re/satori-html`](https://github.com/natemoo-re/satori-html) 可直接输入标准 HTML 字符串。 | **优势**：极速（毫秒级）、零浏览器依赖、原生支持多行文本自动折行与自定义字体度量。<br>**局限**：仅支持 Flexbox（不支持 CSS Grid），复杂文字可选择转为 `<path>` 或 `<text>`。 | ⭐⭐⭐⭐⭐ |
| **dom-to-svg** | [`felixfbecker/dom-to-svg`](https://github.com/felixfbecker/dom-to-svg)<br>*(~2.5k Stars)* | 在真实 Chromium 浏览器中读取已完成排版的 DOM 树（100% 支持 **CSS Grid + Flexbox**），遍历元素的 `getBoundingClientRect()`、计算样式与文本 `Range.getClientRects()`，原地映射为标准 `<svg>` 矢量节点。 | **优势**：完全复用浏览器顶级排版能力（含 Grid 网格与复杂内联混排），产出的 `.svg` 可直接导入 Figma / Illustrator / Typst。<br>**局限**：需配合 Playwright/Puppeteer 运行。 | ⭐⭐⭐⭐⭐ |
| **layout2vector** | [`node-projects/layout2vector`](https://github.com/node-projects/layout2vector) | 提取实时 DOM 几何属性、计算样式与坐标变换（含 Shadow DOM），支持导出为 SVG、PDF、DXF 等多种工程矢量格式。 | **优势**：适合复杂 Web 组件转工程矢量文档。<br>**局限**：生态相对小众，需二次封装。 | ⭐⭐⭐⭐ |

> **工程启示**：这是解决 **“高信息密度中文架构框图”** 最完美的路线——既彻底摆脱了手算 SVG `<text>` 坐标与无法自动换行的痛苦，又保留了纯正矢量 `.svg` 无限放大不失真的出版品质。

---

### 路线二：现代声明式架构图与教材概念图 DSL（Text-to-SVG Compilers）

**核心思想**：当图表包含 **复杂跨层连线、状态流转、自动避障路由或严格数学几何约束** 时，通过专门设计的领域特定语言（DSL）搭配图论布局算法（ELK / Dagre / 数值优化）直接编译生成 `.svg`。

| 开源项目 | GitHub 仓库 | 核心技术机制 | 优势与局限 | 适用等级 |
| :--- | :--- | :--- | :--- | :---: |
| **D2** | [`terrastruct/d2`](https://github.com/terrastruct/d2)<br>*(~20k Stars)* | Go 语言编写的现代声明式图表语言（单二进制 CLI）。内置 **ELK / Dagre / TALA** 自动布局引擎，原生支持 **`grid-rows` / `grid-columns` 网格卡片矩阵**、多层嵌套容器、Markdown 富文本节点、$\LaTeX$ 公式及 20+ 套现代出版级主题，直接输出高质量 `.svg`。 | **优势**：视觉审美远超传统 Mermaid/Graphviz；原生支持网格布局与容器嵌套。<br>**局限**：对超长中文段落的精细卡片内排版控制不如纯 CSS 灵活。 | ⭐⭐⭐⭐⭐ |
| **Typst CeTZ + Fletcher** | [`cetz-package/cetz`](https://github.com/cetz-package/cetz)<br>[`Jollywatt/typst-fletcher`](https://github.com/Jollywatt/typst-fletcher) | Typst 生态原生的 TikZ 替代方案。`CeTZ` 提供精确坐标系与几何绘图原语；`Fletcher` 构建在 CeTZ 之上，支持用矩阵坐标声明节点并自动计算智能箭头避障路由。可通过 `typst compile --format svg` 毫秒级输出 `.svg`。 | **优势**：**与 Typst 教材编译流水线 100% 同源**，正文字体、数学公式与教材零差异、零乱码。<br>**局限**：需要编写 Typst 绘图语法，适合结构化流程与状态机。 | ⭐⭐⭐⭐⭐ |
| **Penrose** | [`penrose/penrose`](https://github.com/penrose/penrose)<br>*(~5k Stars)* | 卡内基梅隆大学（CMU）开源的科学插图平台。借鉴 Knuth 思想，将图表分离为 `Domain`（领域公理）、`Substance`（逻辑对象关系）和 `Style`（视觉样式），通过数值优化自动求解满足几何约束的最佳布局并导出 `.svg`。 | **优势**：极具学术美感，适合集合论、线性代数、几何光学、物理场与抽象数学概念图。<br>**局限**：不适合绘制大段文字的工程架构框图。 | ⭐⭐⭐⭐ |
| **Pikchr** | [`drhsqlite/pikchr`](https://github.com/drhsqlite/pikchr) | SQLite 作者 Richard Hipp 专为技术文档 Markdown 内嵌配图开发的 C 语言矢量图编译器（改进自经典 `PIC` 语言），对“盒子相对方位（`box; arrow; box below`）”的声明极其精准。 | **优势**：零外部依赖、极度轻量、输出自适应响应式 SVG。<br>**局限**：适合紧凑型协议帧、内存布局、编译原理框图，不适合复杂富文本卡片。 | ⭐⭐⭐⭐ |

---

### 路线三：Python 编程式科学与工程 SVG 制图库（Programmatic Vector Libraries）

**核心思想**：在 Python 脚本中通过面向对象 API 参数化计算坐标并批量生成精确的 SVG 2.0 矢量图。

| 开源项目 | GitHub 仓库 | 核心技术机制与适用场景 | 适用等级 |
| :--- | :--- | :--- | :---: |
| **drawsvg** | [`cduck/drawsvg`](https://github.com/cduck/drawsvg) | 现代 Python 3 原生 SVG 2.0 编程构建库。支持渐变、滤镜、蒙版、箭头 `marker`、自定义坐标系与矢量路径计算，适合编写数据驱动或参数化教材几何/算法图生成脚本。 | ⭐⭐⭐⭐ |
| **Schemdraw** | [`cdelker/schemdraw`](https://github.com/cdelker/schemdraw) | Python 出版级硬件电路原理图、数字逻辑门、信号处理框图（DSP）与流程图绘制库，直接输出无背景高保真 `.svg`，非常适合计算机组成原理、数字逻辑与嵌入式硬件章节配图。 | ⭐⭐⭐⭐⭐ |

---

### 路线四：AI / 多模态大模型驱动的端到端 SVG 生成项目（2025–2026 前沿）

**核心思想**：将 Text-to-SVG 与 Image-to-SVG 建模为多模态大模型（VLM）的结构化代码生成任务，或结合扩散模型进行贝塞尔曲线控制点优化。

| 开源项目 | GitHub / HuggingFace | 核心技术机制 | 适用场景与工程边界评估 |
| :--- | :--- | :--- | :--- |
| **OmniSVG** | [`OmniSVG/OmniSVG`](https://github.com/OmniSVG/OmniSVG)<br>*(复旦大学 & 阶跃星辰)* | 基于 Qwen-VL 底座训练的端到端多模态 SVG 生成大模型，采用结构化基元 Tokenization，支持 Text-to-SVG 与 Image-to-SVG。 | **适合**：生成扁平化矢量插画、设备外观小图标（Icon）、情境装饰元素。<br>**不适合**：直接生成包含大量中文专业术语与严密多层对齐的系统架构图（易出现坐标漂移与文字乱码）。 |
| **StarVector** | [`joanrod/star-vector`](https://github.com/joanrod/star-vector)<br>*(ServiceNow / Mila / Apple)* | 开源 1B / 8B 权重与 `SVG-Bench` 基准，将位图矢量化与文本转 SVG 统一为 `<path>` / `<circle>` / `<polygon>` 代码生成过程。 | **适合**：将位图实验设备图标、拓扑符号转化为干净的原生矢量组件，嵌入到大架构图中。 |
| **Chat2SVG** | `Chat2SVG` | 混合框架：先由 LLM 生成语义级基础几何 SVG 模板，再通过图像扩散模型（ControlNet/SDEdit）执行点级轮廓优化，并支持多轮自然语言局部编辑。 | **适合**：概念徽标、艺术化封面插图与视觉隐喻图形创作。 |

> **关键工程结论**：
> 在学术与教材写作中，应当坚持 **“凯撒的归凯撒”**：
> - 对于 **含密集专业文本与多层逻辑的架构图/概念图**，必须采用 **“LLM 提炼结构化内容 $\rightarrow$ 路线一（HTML/CSS-to-SVG）或路线二（D2 / Typst Fletcher）确定性排版编译”**；
> - 对于 **架构图内部的硬件/设备/学科视觉小图标（Icon）**，可利用 **路线四（OmniSVG / StarVector）** 生成纯矢量 `<path>` 图标库，替代容易引发 PDF 乱码的 Emoji。

---

## 三、已在 `textbook-svg` 技能中落地的核心改进总结

基于本次挑战杯复杂系统规划报告的实战打磨，我们已在本地技能 [`textbook-svg`](file:///Users/l.ylive.cn/.gemini/config/skills/textbook-svg/SKILL.md) 中率先落地了 **“Track A + Track B 双轨制 + DOM-to-Pure-SVG 编译器”**：

1. **双轨制选型架构**：
   - **Track A（极简纯 SVG 轨，`700px～760px`）**：针对 $\le 4$ 个节点、单行 $\le 14\sim20$ 字的轻量概念图，提供 `pillars`（横向三支柱）、`matrix`（2×2 四象限）、`branch`（条件分支）、`contrast`（正反对比）四大原生 SVG 母版（见 [`archetypes.md`](file:///Users/l.ylive.cn/.gemini/config/skills/textbook-svg/references/archetypes.md)）；
   - **Track B（高信息密度 `880px` `1+N` 总分图组轨）**：针对多层复杂架构与多团队/多模块矩阵，提供 `html-overview`（全景分层总图）、`html-stack`（上下游深度堆叠子图）、`html-primitives`（编号工程原语+2×2矩阵子图）、`html-matrix`（多通道分流矩阵子图）四大高密度母版（见 [`high_density_templates.md`](file:///Users/l.ylive.cn/.gemini/config/skills/textbook-svg/references/high_density_templates.md)）。
2. **三大排版黄金法则**：
   - **法则一：`880px` 黄金窄画布与大字号预算（`12.5px～19.5px`）**，从源头杜绝宽画布缩印进 A4/Markdown 后字号变小；
   - **法则二：“1 张总图 + N 张专题子图”解耦与随文就近嵌入（Contextual Co-location）**，总图建骨架并标索引（`详见图 Xa/Xb/Xc`），子图随正文段落与表格就近嵌入；
   - **法则三：双格式同步输出（`2x Retina .png` + `纯正原生 .svg`）与七项自动化门禁联检**，通过 [`svg_tool.py`](file:///Users/l.ylive.cn/.gemini/config/skills/textbook-svg/scripts/svg_tool.py) 的 `render-html` 子命令一键导出 PNG 与纯矢量 SVG，并自动完成画布宽度、最小字号、零水平溢出、XML 语法、零 Emoji 乱码等全套校验。

---

## 四、面向后续项目的进一步演进路线图（Next Steps）

在其他新项目（如新教材编写、国家自然科学基金申请书配图、顶会论文架构图、课程课件自动化流水线）中，可基于本报告在以下四个方向进一步迭代升级：

### 演进方向 1：引入 `Satori` / `resvg` 构建零浏览器极速 SVG 编译管线
- **现状**：当前 `svg_tool.py render-html` 依赖启动 Playwright Chromium 提取 DOM 几何树（单次耗时约 1.5～2 秒）。
- **改进方案**：对于纯 Flexbox 布局的卡片母版，可引入基于 Node/Wasm 的 [`vercel/satori`](https://github.com/vercel/satori) + [`satori-html`](https://github.com/natemoo-re/satori-html) 作为轻量后端，无需启动浏览器即可在 **50ms 内** 将 HTML/CSS 模板直接编译为原生 `.svg`；同时保留 Playwright 通道处理复杂的 CSS Grid 布局。

### 演进方向 2：在 `textbook-svg` 中新增 Track C —— `Typst CeTZ / Fletcher` 原生学术公式与拓扑轨
- **痛点场景**：当教材或论文配图中包含大量 **复杂数学公式（如矩阵运算、概率图模型、神经网络张量维度变换 $X \in \mathbb{R}^{B \times T \times D}$）** 以及 **跨节点曲线连接箭头** 时，HTML/CSS 画跨层斜向/曲线箭头较为繁琐。
- **改进方案**：
  - 在 `textbook-svg` 中增加 `typst-fletcher` 母版库；
  - 直接编写 `.typ` 独立图元源码，调用本地 `typst compile fig.typ fig.svg` 一键生成原生矢量 `.svg`；
  - 完美享受 Typst 原生数学公式渲染与 `Fletcher` 自动连接线避障路由。

### 演进方向 3：融合 `D2` 布局算法与 `880px` 学术语义色板
- **痛点场景**：面对节点连接关系高度非对称的复杂软件工程拓扑图（如状态机转换图、编译器 AST 语法树、微服务调用依赖图），手工编写 CSS Grid 难以表达复杂的有向图边（Edges）。
- **改进方案**：利用 [`terrastruct/d2`](https://github.com/terrastruct/d2) 的 ELK 布局引擎自动计算节点与折线路由，并定制一套与 `textbook-svg` 六色学术语义色板（靛紫、天际蓝、琥珀金、翡翠绿、玫瑰红、岩石灰）及 `PingFang SC` 大字号规范严格对齐的 D2 主题配置文件（`academic-theme.d2`）。

### 演进方向 4：构建印刷安全的纯矢量学术图标库（SVG Icon Asset Pool）替代 Emoji
- **痛点场景**：HTML 卡片标题前的 Emoji（如 `🧠`、`🔬`、`🔒`）在导出纯 `.svg` 时为了防止 Typst PDF 出现豆腐块乱码，目前采取了自动剔除或替换为几何符号 `• / ▼ / ▲` 的策略，少了一点视觉精致感。
- **改进方案**：精选或使用 `OmniSVG` / Lucide Icons 提炼 30～50 个高频计算机与理工科纯矢量单色 `<svg><path d="..."/></svg>` 图标（如芯片、服务器、神经网络、盾牌、显微镜、智能眼镜、数据库、齿轮），内置于 `textbook-svg/resources/icons.json` 中。在 `DOM-to-Pure-SVG` 编译时，自动将文本中的语义标签（如 `:cpu:`、`:cloud:`、`:shield:`）原地替换为内联 `<path>` 矢量图标，实现 **“既有丰富图标视觉锚点，又 100% 纯矢量零乱码”** 的出版级效果。
