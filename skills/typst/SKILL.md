---
name: typst
description: "【单一事实源出版级编译器】将工程单一事实源基准 (SSOT) Markdown 文档及标准 Markdown 自动化解析并编译为高校纸质教材与工业出版级 Typst 源码与矢量 PDF。复用 NCU 辛苦调优的 A4 双面排版系统 (对称书脊边距、奇偶页动态页眉、科技三线表、高保真代码卡片)，深度集成 4090 Kroki 算力画图与 LaTeX 数学公式引擎。"
metadata:
  version: "1.2.0"
  author: NCU-AI-Educators
---

# 单一事实源 (SSOT) 出版级 Typst/PDF 编译器 (Typst)

本技能将单一事实源基准（`*.ssot.md`）或标准 Markdown 技术文档一键自动化编译为符合高校教材与工业出版级标准的矢量 PDF。

## 1. 触发方式与核心指令
- 命令行直接执行：
  ```bash
  python3 scripts/ssot_to_typst.py <input.ssot.md> [output.pdf]
  ```
- 环境变量配置（支持可选的远程 Kroki 算力服务）：
  ```bash
  export KROKI_ENDPOINT="http://192.168.8.6:8000"
  ```

## 2. 核心排版与编译特性
- **纸张与双面装订边距**: 严格适配 A4 纸张双面印刷，自动生成对称书脊边距 `margin: (inside: 24mm, outside: 20mm, top: 22mm, bottom: 22mm)`；
- **奇偶页动态对称页眉**: 奇数页显示当前章标题与页码；偶数页显示研制机构、受控版本与页码；
- **出版级科技三线表**: 顶线 1.2pt 深黑粗线，栏目线 0.8pt 细线，底线 1.2pt 深黑粗线（严格位于表格最底部），行间辅以 0.5pt 浅灰细线，自动开启 `breakable: false` 杜绝表头被分页拆散孤行；
- **Kroki 统一算力图表集成**: 自动识别 Mermaid、PlantUML、D2、Graphviz 等图表语法，实时渲染并写入 `figures/` 离线缓存；
- **LaTeX 公式智能映射保护**: 严密解决多字母变量双引号包裹（如 $SO(3)$, $RMSE$），自动剥离多余反斜杠并适配微积分算子；
- **告警引用卡片**: 原生转换 GitHub 风格告警提示（`> [!NOTE]`, `> [!WARNING]`, `> [!IMPORTANT]`）为精美圆角卡片。
