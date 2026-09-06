# Typst 出版级编译器技能 (Typst Publication Compiler Skill)

> **基于单一事实源 (SSOT) 哲学的学术教材与工业出版级 Typst/PDF 自动化编译器**

[![Typst](https://img.shields.io/badge/Typst-v0.12+-239dad.svg)](https://typst.app/)
[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](LICENSE)

---

## 📖 技能定位

在现代教育与科研场景中，技术文档和讲义常因工具割裂面临以下痛点：
- **Markdown 表现力有限**：缺乏严谨的出版级页面控制、书脊装订边距、奇偶页眉及高密度科技排版规范；
- **LaTeX 门槛与维护成本高**：语法繁琐、编译缓慢、协作不易；
- **排版反复排版调整**：图表、公式、代码卡片和三线表无法自动化保持版面一致。

**Typst 出版级编译器**作为 AI Agent 技能（Skill），将标准的 **SSOT Markdown 文档**一键解析并编译为**高校纸质教材与工业规范出版级**的 Typst 源码与矢量 PDF。该编译器深度沉淀并复用了南昌大学（NCU）团队辛苦调优的 A4 双面排版系统与图表处理引擎。

---

## ✨ 核心特性

### 1. 经典 A4 双面印刷排版系统
- **对称书脊边距**：遵循印刷装订工业标准，内侧留足装订裕量（内侧 `2.5cm`，外侧 `2.0cm`，上下 `2.5cm`）；
- **动态奇偶页眉**：奇数页显示当前节标题并右对齐，偶数页显示文档总标题并左对齐，页脚统一显示动态页码 `页码 / 总页数`；
- **高密度学术正文风格**：默认配置标准思源宋体/思源黑体（兼容 Noto Serif CJK SC / Noto Sans CJK SC），字号 10.5pt（五号字），1.5 倍行距，段首缩进两字符。

### 2. 科技论文三线表排版引擎
- 自动将 Markdown 管道表格转换为具有严格视觉层级的**科技学术三线表**；
- 顶线与底线加粗（`1.2pt` 墨色），栏目线轻量化（`0.6pt`），自动交替斑马纹背景；
- 单元格文字智能对齐与自动换行，避免宽表溢出纸张。

### 3. LaTeX 公式精准保护与符号转义
- 自动解析 `$...$` 行内公式与 `$$...$$` 独立块级公式；
- **LaTeX 变量双引号保护**：有效解决 Typst 将 LaTeX 变量（如 `$E_{"sub"}$`）误解析为纯文本字符串的关键痛点，智能剥离非预期双引号，还原真实数学排版；
- 完美转义转置符号（如 `\top`、`\intercal` 转为 `top`）、逻辑符号与希腊字母。

### 4. 4090 Kroki 算力与原生矢量图集成
- **Kroki 统一算力图表**：自动捕获 Markdown 中的 `mermaid`、`plantuml`、`d2`、`graphviz` 代码块，优先调用本地 GPU / Kroki 算力服务离线编译为矢量 SVG 嵌入；
- **无损原生矢量嵌入**：无缝支持嵌入 **Archify 出版级纯净 SVG**，实现高清晰度、无交互外壳残留的工业级系统架构与时序图排版。

### 5. 醒目的代码卡片与告警提示块 (Callouts)
- 语法高亮代码块：左侧高亮引导边框，背景采用冷灰护眼底色；
- GitHub 风格告警支持：`[!NOTE]`、`[!TIP]`、`[!IMPORTANT]`、`[!WARNING]`、`[!CAUTION]` 自动转换为带彩色图标与背景微强调的现代学术边框卡片。

---

## 📂 技能包目录结构

```
skills/typst/
├── SKILL.md                 # Agent 技能主定义（YAML Frontmatter + 提示词规则）
├── README.md                # 本文档（原理、规格与使用说明）
└── scripts/
    └── ssot_to_typst.py     # 46KB 工业级鲁棒的核心解析与转换脚本
```

---

## 🚀 快速上手

### 1. 环境准备
确保机器已安装 `Python 3.10+` 以及 `Typst` CLI：
```bash
# macOS (Homebrew)
brew install typst

# Linux / Windows (Cargo 或二进制包)
cargo install --locked typst-cli
```

### 2. 命令行执行

运行转换脚本将 SSOT Markdown 转换为 Typst 源码：
```bash
python3 skills/typst/scripts/ssot_to_typst.py input.ssot.md output.typ
```

使用 Typst 编译器一键生成高质量矢量 PDF：
```bash
typst compile output.typ output.pdf
```

### 3. 与 Agent 协同
将本技能目录配置于 AI Agent（如 Antigravity IDE、Claude Code 或 Cursor）的技能根路径中。在与 Agent 对话时直接呼叫：
> *"请使用 typst 技能，将当前的 `docs/方案设计.ssot.md` 转换为符合 A4 双面印刷标准的 PDF。"*

---

## 🛠️ 高级参数配置

转换脚本内置支持以下控制参数：
- `--clean-svg-dir`：指定 Archify / Kroki 生成的本地 SVG 缓存目录；
- `--kroki-url`：指定 Kroki 服务端点（默认为 `http://localhost:8000` 或本地容器）；
- `--margin-inner` / `--margin-outer`：动态定制装订线边距；
- `--font-serif` / `--font-sans`：指定系统已安装的中文字体族名称。

---

## 📜 开源协议

本项目脚本部分采用 **AGPL v3** 协议，技能文档遵循 **CC BY-NC-SA 4.0** 协议。
南昌大学 AI 赋能教学团队 (NCU-AI-Educators) 出品。
