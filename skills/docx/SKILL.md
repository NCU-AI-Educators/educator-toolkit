---
name: docx
description: "【出版级 Word (DOCX) 编译器】将标准 Markdown、Deep Research 清洗报告或工程单一事实源 (SSOT) 文档一键自动化解析并编译为符合高校公文与学术出版规范的 Microsoft Word (.docx) 文档。内置 A4 页面标准边距、动态页眉与页码、Word 原生导航大纲标题 (Heading 1~3)、中文正文首行缩进两字符 (2em)、五种语义配色的 GitHub Callout 卡片 (> [!NOTE] 等)、跨页自动重复表头的科技三线表、图下表上防跨页断行题注，以及 [^N] 蓝色上标引用角标与悬挂缩进参考文献列表。"
metadata:
  version: "1.0.0"
  author: NCU-AI-Educators
---

# 出版级 Markdown 转 Word 编译器 (docx)

本技能将标准 Markdown（`.md`）、Deep Research 清洗报告或单一事实源基准（`*.ssot.md`）一键编译为排版严整、兼容 Microsoft Word 与 WPS Office 的 `.docx` 文档。

## Runtime environment & symlink resolution

- **Installation modes**: Supports project-local installation (`.agents/skills/docx`) and global symlink references (e.g. `~/.gemini/config/skills/docx` linked from `NCU-AI-Educators/educator-toolkit/skills/docx`).
- **Symlink & sandbox contract**:
  - The agent **MUST** dynamically resolve the physical skill directory (via `readlink`, Python `os.path.realpath`, or shell inspection) and execute `scripts/md_to_docx.py` with Python 3.

---

## 1. 触发场景与调用方式 (When to Trigger)

当用户通过以下方式请求导出 Word 文档时，立即调用本技能：
- **斜杠命令触发**：`/docx <path/to/file.md>`
- **自然语言触发**：“导出一份 docx 版本”、“转成 Word 文档”、“生成可编辑的 Word 报告”。

### 标准执行命令
```bash
# 通用跨工作区执行方式（推荐，自动解析软链接物理路径）
python3 "$(python3 -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' ~/.gemini/config/skills/docx/scripts/md_to_docx.py)" "<input.md>" [output.docx]

# 指定输出路径与自定义页眉文本
python3 "$(python3 -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' ~/.gemini/config/skills/docx/scripts/md_to_docx.py)" "<input.md>" "[output.docx]" --header "自定义页眉文本"

# 关闭正文首行缩进（适用于纯英文或西式现代排版文档）
python3 "$(python3 -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' ~/.gemini/config/skills/docx/scripts/md_to_docx.py)" "<input.md>" --no-indent
```

---

## 2. 核心排版与编译规范

1. **A4 页面与页眉页脚**：
   - 标准 A4 幅面（`210mm × 297mm`），四周边距 `25mm`；
   - 页眉自动提取 YAML Frontmatter `title` 或文档 `# H1` 主标题（支持 `--header` 覆盖），右对齐 9pt 灰蓝字体；
   - 页脚居中插入 Word 原生动态 `PAGE` 页码域（`— 1 —`）。
2. **原生大纲层级与中西文字体分离**：
   - `##`、`###`、`####` 严格绑定 Word 原生 `Heading 1`、`Heading 2`、`Heading 3` 样式（中文黑体 + 西文 Times New Roman），支持 Word / WPS 左侧 **导航窗格** 跳转与一键插入自动目录；
   - 正文段落采用 11pt 宋体 + Times New Roman，1.45 倍行距，两端对齐，首行自动缩进 2 字符（`22pt`）。
3. **GitHub 风格告警卡片 (`> [!NOTE]` 等)**：
   - 原生支持 `NOTE`、`INFO`、`TIP`、`IMPORTANT`、`WARNING`、`CAUTION` 语义配色，渲染为带 `24pt` 彩色左边框与浅色底纹的通栏卡片（常用于执行摘要、核心提示与章节导读）。
4. **“图下表上”防断行与科技三线表**：
   - 插图按版心净宽（`158mm`）居中自适应嵌入，并开启 `keep_with_next` 与下方图题强绑定，杜绝图与图题跨页分离；
   - 表格题注开启 `keep_with_next` 与下方表格强绑定；表格采用顶底粗线（`1.5pt #1E3A8A`）、表头底线（`1pt #1E3A8A`）、行间浅灰细线与斑马纹交替底色，自动开启 `tblHeader`（跨页重复表头）与 `cantSplit`（防止单行跨页截断），并根据各列文本长度智能分配列宽。
5. **行内富文本与尾注文献体系**：
   - 完整解析行内 `**加粗**`、`*斜体*`、`` `code` ``（行内代码）、`[链接文本](URL)` 以及 `[^N]` 引用角标（自动渲染为蓝色上标 `[N]`）；
   - 文末 `[^N]: ...` 尾注定义自动转化为 `22pt` 悬挂缩进的规范参考文献条目。
