# Docx 出版级 Word 编译器技能 (Docx Publication Compiler Skill)

> **基于单一事实源 (SSOT) 与标准 Markdown 的高校公文与学术出版级 Microsoft Word (.docx) 自动化编译器**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://www.python.org/)
[![python-docx](https://img.shields.io/badge/python--docx-1.1+-2B579A.svg)](https://python-docx.readthedocs.io/)
[![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)](../../LICENSE)

---

## 📖 技能定位

在高校教学改革调研、教务政策申报与科研报告协作场景中，最终交付物往往需要提供**可编辑、符合中文公文与学术排版规范的 Word（`.docx`）文档**。然而传统的 Pandoc 或普通 Markdown 导出工具常存在以下痛点：
- **缺乏中文公文与教材排版规范**：正文缺乏标准首行 2 字符（2em）缩进，中英文字体混杂，标题未绑定原生大纲级别；
- **组件样式丢失**：GitHub 风格提示块（`> [!NOTE]` 等）被降级为普通文字，代码块无底纹边框；
- **表格与图表跨页断裂**：表格无标准科技三线表线条、跨页不自动重复表头，图与图题、表题与表格容易跨页撕裂；
- **多次引用尾注错乱**：正文多次引用同一文献 `[^1]` 时容易产生重复编号或丢失上标格式。

**Docx 出版级编译器（`/docx`）**将标准 Markdown、Deep Research 清洗报告或 SSOT 文档一键解析并编译为兼容 **Microsoft Word 与 WPS Office** 的高质量 `.docx` 文档。

---

## ✨ 核心特性

### 1. A4 出版级版面与原生大纲导航
- **标准 A4 页面设置**：四周边距 `25mm`，自动提取 YAML Frontmatter `title` 或 `# H1` 主标题生成右对齐页眉，页脚居中插入 Word 原生动态 `PAGE` 页码域（`— 1 —`）；
- **Word 原生大纲层级绑定**：`##`、`###`、`####` 严格映射至 Word 原生 `Heading 1`、`Heading 2`、`Heading 3` 样式（黑体 + Times New Roman），支持 Word / WPS 左侧**导航窗格（大纲视图）**跳转与一键插入自动目录；
- **中西文字体解耦与 2em 缩进**：正文采用 11pt 宋体（EastAsian）+ Times New Roman（ASCII），1.45 倍行距，两端对齐，首行自动缩进 2 字符（`22pt`，支持 `--no-indent` 切换）。

### 2. GitHub 风格五色告警卡片 (`> [!NOTE]` 等)
- 原生识别 `> [!NOTE]`、`> [!INFO]`、`> [!TIP]`、`> [!IMPORTANT]`、`> [!WARNING]`、`> [!CAUTION]`；
- 自动渲染为带 `24pt` 语义彩色左边框与护眼浅色底纹的通栏卡片（非常适用于报告头部的**执行摘要（Executive Summary）**与章节导读）。

### 3. “图下表上”防断行与自适应科技三线表
- **高清插图自适应与防撕裂**：插图按版心净宽（`158mm`）居中嵌入，自动开启 `keep_with_next` 与下方居中黑体图题强绑定，杜绝图与图题跨页分离；
- **科技三线表与跨页重复表头**：表题居于表格正上方并开启 `keep_with_next`；表格采用深蓝顶底粗线（`1.5pt #1E3A8A`）、表头底线（`1pt #1E3A8A`）、行间浅灰细线与斑马纹交替底色，自动开启 `tblHeader`（跨页自动重复表头）与 `cantSplit`（防止单行跨页截断），并根据各列文本长度智能分配列宽。

### 4. 行内富文本与上标尾注文献体系
- 完整解析行内 `**加粗**`、`*斜体*`、`` `行内代码` ``、`[链接文本](URL)` 以及 `[^N]` 引用角标（自动渲染为蓝色上标 `[N]`）；
- 文末 `[^N]: ...` 尾注定义自动转化为 `22pt` 悬挂缩进的规范参考文献列表。

---

## 📂 技能包目录结构

```text
skills/docx/
├── SKILL.md                 # Agent 技能主定义（YAML Frontmatter + 触发与执行规范）
├── README.md                # 本文档（原理、规格与使用说明）
└── scripts/
    └── md_to_docx.py        # 核心 Markdown/SSOT 转 Word (.docx) 编译脚本
```

---

## 💬 智能体交互指南：自然语言与斜杠命令

### 1. 斜杠命令直接调用 (Slash Commands)

```bash
# 1. 默认编译：在同级目录生成同名 .docx 文档（含 2em 首行缩进与动态页眉）
/docx docs/调研报告.md

# 2. 指定输出路径与自定义页眉
/docx docs/调研报告.md output/调研报告_终稿.docx --header "高校人工智能通识教育改革调研报告"

# 3. 关闭正文首行缩进（适用于西式现代排版）
/docx docs/technical_spec.md --no-indent
```

### 2. 终端命令行直接运行

```bash
python3 skills/docx/scripts/md_to_docx.py <input.md> [output.docx] [--header TEXT] [--no-indent]
```
