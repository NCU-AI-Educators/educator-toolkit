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
- **局部横向页面与小节标题智能吸纳 (Landscape & Auto-Absorb)**:
  - **大图局部横向**: 支持通过 `<!-- landscape -->` 或 `<!-- pagebreak:landscape -->` 将复杂宽幅架构图/时序图/甘特图单独旋转为横向页面（A4 净宽 257mm），避免横向压缩与文字模糊；
  - **超宽表格自动转向**: 自动检测表格列数，凡列数 $\\ge 7$ 的超宽表格（如子系统矩阵）默认自动切换为横向页面舒展排版；同时支持写作者使用 `<!-- table:landscape -->` 或 `<!-- table:portrait -->` 显式强制控制，支持 `:isolated` / `:no-absorb` 禁用吸纳；
  - **前置标题智能吸纳**: 当横向图表前方紧邻 1~2 级小节标题与简短引言（$\\le 120$ 字）时，编译器自动将其回溯提取并吸纳移入横向页面顶部统一渲染，彻底杜绝上一页底部出现孤立标题与空白残页。
- **中文段落首行缩进两格 (2em) 与多层列表对齐规范**:
  - **正文叙述段落首行缩进 (2em)**: 无论正文是否在 Markdown 中带有列表从属缩进，中文叙述段落一律强制保障标准首行缩进两格（`first-line-indent: 2em`），严禁非代码段落被粗暴清零缩进；
  - **多层嵌套列表对齐收敛**: 设定嵌套子列表基准继承规则（`#show enum: set list(indent: 0em)`），子列表项目符号精准对齐到父项文本或段落首行基准线，杜绝第二层列表向右累加缩进漂移；
  - **元数据治理与机构身份隔离**: 严格支持 YAML Frontmatter 自适应元数据台生成；缺失 Frontmatter 时自动触发 H1 下方属性键值行智能识别，杜绝将特定实验室身份静默写死为外部报告的默认兜底；连续键值行与尾随双空格换行获得原子级保护，防止元数据塌陷为连贯大段落。
- **参考文献学术标准排版 (Academic References Alignment)**:
  - **序号右对齐 (Right-Aligned Brackets)**: 基于国标 GB/T 7714 及学术出版规范，采用自适应两列网格（`grid`），序号列统一设为右对齐，确保个位数（如 `[1]`）与多位数（如 `[10]`）的右括号 `]` 严格垂直贯通对齐，个位数序号左侧自适应缩进留白；
  - **块状悬挂缩进 (Block Hanging Indent)**: 文献著录正文在独立右列中自动形成坚固的块状布局，无论著录条目跨越多少行，所有折行文本均严格局限于著录列内部，彻底杜绝文字折行回穿至序号下方的回流破坏；
  - **双向锚点超链贯通**: 序号网格单元自动挂载 `<fn-id>` 原生跳转锚点，与正文引用处的角标链接（`@fn-id`）实现双向高亮跳转。
- **列表从属段落自动解耦与连续编号保障**:
  - **从属叙述段落解耦**: 彻底消除编译输出中 `#par` 的前置多余空格，阻断 Typst 引擎将叙述段落强行吸纳为列表内部挂靠块的行为，确保段落首行缩进两格（2em）且折行文字 100% 顶格左对齐到页面版心边缘；
  - **有序编号显式持久化**: 编译器在转换第一级有序列表时，输出显式数字标记（`1. `、`2. ` 代替 `+ `），确保即使列表间穿插包含顶格正文段落，后续列表项的编号也不会被 Typst 引擎误置重置为 1。
- **独立目录页与层级对比美化 (Independent TOC Page & Hierarchy Styling)**:
  - **独立成页与双向分页保障**: 支持在 Markdown 源码中通过 `<!-- pagebreak --> \n\n ## 目录 \n\n <!-- pagebreak -->` 或 Frontmatter 配置声明独立目录页，前后均由分页符彻底隔离，确保目录作为独立页面整洁呈现；
  - **大章加粗与呼吸感微间距**: 一级章目（Level 1）在目录中自动加重为深黑粗体（`#0f172a`），条目上方自适应注入 `0.45em` 呼吸留白（`v(0.45em, weak: true)`），二级子条目常规字体并保持 `1.5em` 缩进，实现主次分明、疏密有致的学术出版质感；
  - **单页容量优化与点导线对齐**: 默认配置 2 级大纲深度（`depth: 2`），完美收纳申报书、可行性研究报告的章、节层级，点导线均匀贯通，页码右对齐，确保 20~30 个主次条目恰如其分饱满填充单页版心，杜绝溢出残页。

- **列表从属延续段落与多级嵌套列表上下文保护 (List Continuation & Multi-level Hierarchy Protection)**:
  - **从属段落严格挂靠**: 列表项内部的公式后延续说明、补充长段落，必须按其所属层级保持缩进输出为 `prefix + #par(first-line-indent: 0em)[...]`，严禁在顶格（0格）输出非缩进 `#par`，防止 Typst 词法解析器中断父级列表上下文导致后续同级子项被错误提升为第一级大项（圆点 •）；
  - **公式块原生嵌入**: 列表项内部的独立公式块（`$$`）根据其缩进深度（2格或4格）带缩进输出（`    $ ... $`），确保公式块成为列表项的自然内生元素；
  - **三级深层嵌套支持**: 4 格缩进列表项自动映射为三级列表（`    -`），在出版规范中正确渲染为三级横线标记（`–`），彻底避免与二级三角标（`▸`）混淆。

- **有序列表与无序列表首行缩进统一规范 (List & Enum 2em Indent Alignment)**:
  - **首行对齐中文段落两格 (2em)**: 第一级有序列表（`enum`）与第一级无序列表（`list`）全局统一设为 `indent: 2em, body-indent: 0.5em, spacing: 0.85em`，数字编号与项目符号严格在 2em 竖轴基准线上贯通对齐，折行文本自动形成悬挂缩进；
  - **严禁无条件覆盖规则**: 严禁在全局模板中声明 `#show enum: set enum(indent: 0em)`，Typst 原生对嵌套子列表已有自然的从属对齐支持，滥用 show 规则会导致所有顶层有序列表的 2em 缩进被强制清零为顶格。
