# Archify 架构与工程可视化技能 (Archify Engineering Visualizer Skill)

> **专为现代软件工程与学术出版打造的系统架构、时序图与数据流图可视化引擎**

[![Archify Version](https://img.shields.io/badge/Archify-v2.18-7952b3.svg)](SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Format](https://img.shields.io/badge/Output-HTML%20%7C%20Clean%20SVG-blue.svg)](scripts/export-clean-svg.mjs)

---

## 📖 技能定位

在复杂系统设计、教学方案与技术论文写作中，传统的绘图工具存在明显痛点：
- **Mermaid 表达上限低**：样式粗糙、空间布局难以细调、无法承载富交互；
- **GUI 绘图软件（Draw.io / Visio）脱离代码**：无法通过声明式 DSL 驱动，难以随代码版本迭代；
- **Web 架构图无法直接印刷**：包含大量操作面板、缩放按钮、深色高对比外壳，直接截图或保存为图片模糊且不合出版规范。

**Archify** 是一款双轨制架构绘图与可视化引擎，既支持在浏览器中进行**高维富交互探索**，又支持一键无损导出**出版级纯净矢量 SVG (Publication-grade Clean SVG)**，完美适配 Typst、LaTeX 及高校教材印刷出版。

---

## ✨ 核心特性

### 1. 五大声明式图表类型 (Declarative Diagram Families)
Archify 支持输入 JSON / DSL 或 Mermaid 语法，自动编译为结构清晰、高审美的工程图表：
- 🏗️ **Architecture（系统架构图）**：多层级系统拓扑、云原生服务集群、技术栈全景图；
- ⏱️ **Sequence（交互时序图）**：API 调用序列、分布式事务、高保真生命周期交互时序；
- 🌊 **Dataflow（数据流与管道图）**：ETL/ELT 管道、大数据清洗、消息队列流向；
- 🔄 **Lifecycle（状态机与生命周期）**：对象状态演进、治理流程、审批流；
- 🔀 **Workflow（工程工作流）**：CI/CD 流水线、多节点决策任务网络。

---

### 2. 独特的“双轨”运行模式

```
                 [声明式 JSON / Mermaid 输入]
                              │
                              ▼
                      [Archify 核心编译器]
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
   【轨道一：Web 富交互探索】           【轨道二：出版级纯净矢量导出】
    • 沉浸式多镜头切换                  • 彻底剥离 UI 交互面板与外壳
    • 关系连线动态高光脉冲              • 自动提升字号 (+2.5px) 确保纸质可读
    • 暗色/亮色主题实时切换              • 同色系半透明标题徽章与居中防溢出
    • 探索雷达与全屏漫游                • 严苛的视口边界重算，保证虚线框闭合
    • 浏览器即开即用独立 HTML           • 100% 独立纯净 SVG，直接嵌入 Typst/LaTeX
```

---

## 🔬 出版级纯净矢量 (Clean SVG) 7 项关键保证

针对学术纸质教材、技术可行性报告与毕业设计排版，Archify 内置了经过南昌大学（NCU）项目团队实战检验的 7 项出版级转换不变量：

1. **零外壳残留 (Zero Chrome Artifacts)**：自动切除所有的工具栏、搜索框、暗色背景卡片、缩放控制键等 Web 交互元素；
2. **自动化字号提升 (Automated Typography Scaling)**：图中小字自动加权提升（+2.5px，正文文字达到 14px~16.5px），防止缩放打印到 A4 纸面时字迹发虚；
3. **半透明同色系徽章 (Translucent Tinted Badges)**：小标题与分组标签背景采用与文字同色系的极浅底色（透明度 0.12~0.15），杜绝纯白硬底遮挡底部流程线；
4. **文字居中与防溢出保护 (Centering & Anti-Overflow)**：小标题框宽度随文字放大自动同步自适应拓宽，文字严格几何居中；
5. **视口边界与虚线框闭合 (Bounds Recalculation)**：视口上下左右智能扩展留白，防止虚线泳道框或容器底部在裁切时被切断；
6. **箭头避让与无损连接 (Arrow Boundary Snapping)**：针对放大的文本框重新计算连接端口锚点，杜绝箭头被变大的文本框边缘“吞没”；
7. **纯内联与跨平台兼容**：样式全部内联，字体回落到标准系统字体，Typst / LaTeX / 浏览器 / 矢量绘图软件均可 100% 真实还原。

---

## 📂 技能包目录结构

```
skills/archify/
├── SKILL.md                 # Agent 技能主定义（提示词指令、设计规范与触发条件）
├── README.md                # 本文档（原理、规格与使用说明）
├── bin/                     # CLI 执行脚本 (archify.mjs 等)
├── scripts/
│   ├── export-clean-svg.mjs # 🌟 核心无头出版级纯净矢量转换引擎 (Puppeteer)
│   ├── render-examples.mjs  # 示例批量渲染脚本
│   └── check-render-output.mjs
├── references/              # 规范参考文献库
│   ├── publication-clean-svg.md  # 🌟 出版级纯净矢量转换规范
│   ├── authoring-contract.md     # 声明式语法契约
│   └── viewer-runtime.md         # 交互查看器运行时
├── schemas/                 # JSON Schema 数据契约校验文件
└── examples/                # 涵盖各图表类型的典型样例
```

---

## 🚀 快速上手

### 1. 独立安装与运行
```bash
cd skills/archify
npm install
```

### 2. 导出出版级纯净 SVG (CLI)
使用内置的无头转换脚本，将 Archify 生成的交互式 HTML 图表无损转为纯净 SVG：
```bash
# 将单个 HTML 转换为出版级 SVG
node skills/archify/scripts/export-clean-svg.mjs diagram.html output-clean.svg

# 针对特定图表类型指定推荐视口预设
node skills/archify/scripts/export-clean-svg.mjs system.html system.svg --diagram-type architecture
```

### 3. 与 Typst 协同工作流
1. 让 AI Agent 调用 `archify` 技能生成目标系统架构图或时序图；
2. 运行 `export-clean-svg.mjs` 得到 `figure-1.svg`；
3. 在 SSOT Markdown 文档中直接引用：
   ```markdown
   ![图 1-1 系统整体架构设计](figures/figure-1.svg)
   ```
4. 使用 `typst` 技能一键编译出排版完美的 A4 双面学术 PDF！

---

## 📜 开源协议

本项目采用 **MIT** 协议。
南昌大学 AI 赋能教学团队 (NCU-AI-Educators) 维护升级。
