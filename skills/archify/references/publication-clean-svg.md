# 出版级纯净矢量 SVG 导出与排版工程规范 (Publication Clean SVG Specification)

本文档定义了将 Archify 交互式 HTML 架构图无损转换为高校教材、学术出版物和技术方案（Typst / LaTeX / PDF）纯净矢量 SVG 的统一标准与几何约束。

---

## 1. 核心定位与设计目标

Archify 默认生成的 HTML 适用于高分屏上的 Web 交互、变焦探索与引导演示。但在纸质出版和 A4 排版场景下，必须满足以下硬性工业标准：

1. **绝对纯净无污染**：剔除所有 Web UI 交互外壳（搜索框、变焦工具栏、章节气泡、探测脉冲层、故事蒙层）；
2. **计算样式强内联**：彻底脱敏 CSS 变量（`var(--...)`），将所有笔触、填充色、字体属性 1:1 计算为纯静态 XML 属性；
3. **字号保底阈值**：在缩放至 A4 版心宽（约 15~16cm）时，所有节点文本依然清晰可辨；
4. **几何吸附与防吞没**：所有连线箭头精准停靠在目标卡片外轮廓，杜绝被卡片遮罩层覆盖；
5. **文字自适应扩容**：动态检测长文字标签，框宽保持充足的呼吸内边距，杜绝文字左右溢出；
6. **同色系高透毛玻璃质感**：告别纯白死板遮罩，统一使用 $14\%\sim 22\%$ 低不透明度的同色系轻微半透明底。

---

## 2. 出版级文字排版基线 (Typography Baseline)

在将矢量图缩放至 A4 版心（常见宽度为 `100%` 或 `16cm`）时，SVG 内各层级文字的绝对字号与字重必须满足以下下限要求：

| 元素角色 (Role) | 语义标签 / 属性选择器 | 出版级字号下限 | 字重 (Weight) | 推荐色值 (Light 模式) |
| :--- | :--- | :--- | :--- | :--- |
| **主节点标题** | `data-node-label`, `.t-primary` | **$\ge 17.5\text{px}$** | `700` (Bold) | `#0f172a` (高对比深深石板) |
| **节点副标题** | `data-detail="context"`, `.t-muted` | **$\ge 14.5\text{px}$** | `600` (SemiBold) | `#334155` (深灰石板，防低对比灰) |
| **技术规格标签** | `data-detail="fine"`, 节点底部小标签 | **$\ge 13.5\text{px}$** | `700` (Bold) | 对应组件特征主题色 |
| **子系统/大区标题** | `data-boundary-label`, 区域小标题 | **$\ge 16.5\text{px}$** | `800` (ExtraBold) | 对应区域主色调 (如暖金 `#b45309`) |
| **泳道阶段小标题** | `data-stage-label`, `.t-dim` 泳道头 | **$\ge 16.0\text{px}$** | `800` (ExtraBold) | 对应管道主色调 (如海军蓝 `#1e40af`) |
| **连线关系标签** | `g[data-edge-id] text` | **$\ge 14.5\text{px}$** | `700` (Bold) | 与连线语义同色系加深色 |

---

## 3. 同色系高透毛玻璃徽章规范 (Translucent Badges)

为防止小标题或连线文字直接穿过网格线或背景连线造成视觉干扰，必须使用带微透底的胶囊徽章（Badge），且**严禁使用纯白死板遮罩（`#ffffff`）**：

- **子系统大区小标题徽章**：
  - `fill="rgba(251, 191, 36, 0.22)"`（暖金高透底，光线穿透率 78%）
  - `stroke="rgba(217, 119, 6, 0.45)"`，`stroke-width="1px"`，`rx="6"`
  - `text-anchor="middle"`，文字严格水平居中对齐矩形中线。
- **泳道阶段小标题徽章**：
  - `fill="rgba(59, 130, 246, 0.14)"`（工业蓝高透底）
  - `stroke="rgba(37, 99, 235, 0.35)"`，`stroke-width="1px"`，`rx="6"`
- **连线关系胶囊标签**：
  - 资产与门禁类（绿）：`fill="rgba(16, 185, 129, 0.14)"`，`stroke="rgba(5, 150, 105, 0.5)"`
  - 核心编排调度类（紫）：`fill="rgba(124, 58, 237, 0.14)"`，`stroke="rgba(124, 58, 237, 0.5)"`
  - 默认数据流通类（石板灰）：`fill="rgba(148, 163, 184, 0.16)"`，`stroke="rgba(100, 116, 139, 0.45)"`

---

## 4. 几何防吞没与文字防溢出约束

### 4.1 连线箭头防吞没规则 (Arrow Boundary Snapping)
- **现象**：当连线路径终点（`d` 属性的最后坐标）深入目标节点内部（如 $+18\text{px}$）时，节点在 SVG DOM 树后方渲染的卡片遮罩层会直接盖在连线上，导致箭头标记（`marker-end`）被完全吞没。
- **约束**：**连线终点坐标必须严格落在目标卡片的最外边界上**。
  - 水平向右连线（进入左侧）：终点 $X = \text{node.x}$；
  - 水平向左连线（进入右侧）：终点 $X = \text{node.x} + \text{node.width}$；
  - 垂直向下连线（进入顶侧）：终点 $Y = \text{node.y}$；
  - 垂直向上连线（进入底侧）：终点 $Y = \text{node.y} + \text{node.height}$。

### 4.2 文字框宽度自适应 (Box Expansion)
- 连线矩形框宽度必须留有至少 $15\text{px} \sim 20\text{px}$ 的内边距。
- 估算公式：$\text{BoxWidth} \ge (\text{CharCount} \times 15\text{px}) + 30\text{px}$。
- 对称坐标：$\text{rect.x} = \text{text.x} - (\text{BoxWidth} / 2)$。

### 4.3 视口裁剪与虚线泳道闭合
- 泳道框底边与 viewBox 底部必须保留 $\ge 20\text{px}$ 的安全呼吸内边距，杜绝底部横虚线和圆角被 viewBox 截断导致的“漏底未闭合”问题。

---

## 5. 快速执行工具命令

在 Archify 项目中，使用配套的无头转换工具直接导出：

```bash
# 单图导出
node .agents/skills/archify/scripts/export-clean-svg.mjs <input.html> <output.clean.svg> [light|dark]

# 自动扫描 docs/figures/ 目录下所有 HTML 并批量导出
node .agents/skills/archify/scripts/export-clean-svg.mjs
```

---

## 6. Typst / LaTeX 出版级嵌入范例

### 6.1 Typst 规范嵌入

```typst
#figure(
  image("figures/archify_fig1_1.clean.svg", width: 100%),
  caption: [首期三大子系统协同架构与数据闭环流向图],
) <fig-arch-overview>
```

若图表横向跨度大（如 5 泳道时序流），可使用横向宽幅页面模式呈现极致视觉冲击：

```typst
#page(flipped: true)[
  #figure(
    image("figures/archify_fig3_1.clean.svg", width: 100%),
    caption: [多级智能路由与高保真合成数据生成治理时序图 (横向巨幕版)],
  ) <fig-seq-overview>
]
```
