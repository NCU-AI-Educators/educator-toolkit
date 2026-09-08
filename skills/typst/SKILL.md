---
name: typst
description: "【单一事实源出版级编译器】将工程单一事实源基准 (SSOT) Markdown 文档及标准 Markdown 自动化解析并编译为高校纸质教材与工业出版级 Typst 源码与矢量 PDF，或一键输出适合移动端自适应无缝阅读的高清长图 (PNG)。双模原生复用 NCU 辛苦调优的 A4 双面排版系统 (对称书脊边距、奇偶动态页眉、科技三线表、高保真代码卡片) 与移动端连续版心，深度集成 4090 Kroki 算力画图与 LaTeX 数学公式引擎。"
metadata:
  version: "1.3.0"
  author: NCU-AI-Educators
---

# 单一事实源 (SSOT) 出版级 Typst 编译器 (Typst)

本技能将单一事实源基准（`*.ssot.md`）或标准 Markdown 技术文档一键自动化编译为：
1. 符合高校教材与工业出版级标准的 A4 双面矢量 PDF；
2. 适合移动端无缝阅读、微信沟通与技术长图分享的高清连续长图 PNG。

## Runtime environment & symlink resolution

- **Installation modes**: Supports project-local installation (`.agents/skills/typst`) and global symlink references (e.g. `~/.agent/skills/typst` or `~/.gemini/config/skills/typst` linked from a central repository).
- **Symlink & sandbox contract**:
  - When invoked from a workspace different from the physical installation directory, host IDE file-viewing tools may restrict cross-workspace traversal. The agent **MUST NOT** degrade to manual unvalidated approximations or standard markdown renderers.
  - The agent **MUST** dynamically resolve the physical skill directory (via `readlink`, Python `os.path.realpath`, or shell inspection) and execute the packaged compiler script directly with Python 3.
  - Never execute `python3 scripts/ssot_to_typst.py` assuming the current working directory is the skill directory. Always resolve the physical path of `scripts/ssot_to_typst.py` before execution.

## 1. 触发方式与核心指令
- **通用跨工作区执行方式 (推荐)**：
  ```bash
  # 动态解析真实物理路径执行（适用于任何当前工作目录）
  python3 "$(python3 -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' ~/.gemini/config/skills/typst/scripts/ssot_to_typst.py)" <input.md> [output.pdf]
  
  # 移动端自适应高清长图模式 (PNG)
  python3 "$(python3 -c 'import os, sys; print(os.path.realpath(os.path.expanduser(sys.argv[1])))' ~/.gemini/config/skills/typst/scripts/ssot_to_typst.py)" <input.md> [output.png] --long --ppi 200
  ```
- **技能包本地调试方式**：
- **A4 纸质教材 / 双面出版模式 (默认)**：
  ```bash
  python3 scripts/ssot_to_typst.py <input.ssot.md> [output.pdf]
  ```
- **移动端自适应无缝长图模式 (Long Image)**：
  ```bash
  # 自动根据 .png 后缀识别长图模式，一键输出连续高清长图
  python3 scripts/ssot_to_typst.py <input.ssot.md> [output.png]
  
  # 或显式传入 --long / -l 开关与清晰度参数 (--ppi 200/300)
  python3 scripts/ssot_to_typst.py <input.ssot.md> [output.png] --long --ppi 200
  ```
- **智能体自然语言意图识别**：
  - 当用户提出“**排版为教材**”、“**生成 PDF**”、“**双面印刷**”时，启用 `book` 模式；
  - 当用户提出“**转长图**”、“**生成长图**”、“**转为 PNG**”、“**移动端分享长图**”时，自动启用 `--long` 模式并将目标扩展名设为 `.png`。
- 环境变量配置（支持可选的远程 Kroki 算力服务）：
  ```bash
  export KROKI_ENDPOINT="http://192.168.8.6:8000"
  ```

## 2. 核心排版与编译特性
- **双模自适应排版体系 (Dual-Mode Layout)**:
  - **A4 印刷双面模式 (`book`)**: 严格适配 A4 纸张双面印刷，生成对称书脊边距 `margin: (inside: 24mm, outside: 20mm, top: 22mm, bottom: 22mm)`，奇偶页动态对称页眉（奇数页章标题，偶数页研制机构与受控版本），双面交替页码（`— 当前页 —`）；
  - **自适应无缝长图模式 (`long`)**: **100% 完整遵循当前出版级排版规范**（宋体衬线字族、10.5pt 标准五号字、段首缩进两字符 2em、两端对齐 `justify: true`、科技三线表及公式保护系统完全一致），**仅做纯粹的版面形态切换：去除页眉与页脚（`header: none, footer: none`），高度自适应（`height: auto`）**，彻底消除物理跨页断层；
- **出版级科技三线表**: 严格遵循学术出版规范**“图下表上”**（表题必须居于表格正上方，采用 9pt 斜体沉稳灰；严禁出现无表名裸表）。结构上采用顶线 1.2pt 深黑粗线，栏目线 0.8pt 细线，底线 1.2pt 深黑粗线（严格位于表格最底部），行间辅以 0.5pt 浅灰细线，自动开启 `breakable: false` 杜绝表头被分页拆散孤行；
- **图表题注强绑定规范**: 插图题注居于图件正下方（如 `*图 1-1 架构链路*`），表格题注居于表格正上方（如 `**表 1-1 选型矩阵**` 或 `表 1-1 选型矩阵`），编译器执行原子级位置强绑定，严禁跨页撕裂；
- **Kroki 统一算力图表集成**: 自动识别 Mermaid、PlantUML、D2、Graphviz 等图表语法，实时渲染并写入 `figures/` 离线缓存；长图与 PDF 模式均完美支持矢量无损缩放；
- **LaTeX 公式智能映射保护**: 严密解决多字母变量双引号包裹（如 $SO(3)$, $RMSE$），自动剥离多余反斜杠并适配微积分算子；
- **告警引用卡片**: 原生转换 GitHub 风格告警提示（`> [!NOTE]`, `> [!WARNING]`, `> [!IMPORTANT]`）为精美圆角卡片。
