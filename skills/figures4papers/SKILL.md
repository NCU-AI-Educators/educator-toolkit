---
name: figures4papers
description: >-
  学术论文顶会顶刊（Nature Machine Intelligence/ICML/NeurIPS/CVPR）定量实验数据科研插图绘制技能。
  专门基于 Python/Matplotlib 绘制定量对比柱状图（Grouped Bars）、消融实验图（Ablations）、超宽横向多指标面板、
  独立图例画板、时序收敛折线图、极坐标雷达图、注意力/相关性热力图（Heatmaps）及 3D 流形散点分布图，
  内置动态 Y 轴紧凑缩放、黑白打印安全区分（Hatch/Border）、学术语义色板与版心反推字号门禁。
  【边界路由】仅用于基于实验数值数据的 Matplotlib 统计与定量制图；若需绘制全场景概念与模型架构框图（极简纯 SVG / 880px 教材 1+N 卡片图 / 顶刊论文 Figure 1 领域机理对比与多轨模型架构矢量图）请调用 textbook-svg，若需绘制软件工程拓扑、API 时序、状态机与网页富交互演进图请调用 archify。
---

# figures4papers 学术论文出版级定量图表绘制指南与范式

本技能封装了耶鲁大学刘晨（Chen Liu）博士开源的顶会 / 顶刊（*Nature Machine Intelligence*, *ICML*, *NeurIPS*, *ECCV* 等）学术论文高清制图 Python 脚本与样式库。专门用于基于实验真实数据（TSV/CSV/JSON），为论文正文、技术报告及学术 PPT 绘制符合顶会审美的 **PDF 矢量图、SVG 或 300+ DPI 高清定量实验图表**。

---

## 一、 适用场景与全局绘图技能分工边界

### 1. 三大绘图技能正交分工路由表

在动手绘图前，请先根据 **“输入是实验数值数据，还是概念文本/系统结构”** 选择正确的技能，严禁混用画布规范：

| 绘图需求类型 | 应调用的技能 | 核心技术栈与画布约束 |
| :--- | :--- | :--- |
| **定量实验数据统计图**<br>（柱状图、消融、折线、雷达、热力、帕累托图） | **`figures4papers`（本技能）** | **Python + Matplotlib**；采用 `figsize=(28, 6)` 等双栏超宽画布或紧凑子图网格 + 大字号（`16~24pt`）+ 黑白打印安全纹理（`hatch`）+ 版心字号门禁 |
| **全场景概念与模型架构框图**<br>（Track A 极简纯 SVG、Track B 880px 教材/报告 `1+N` 卡片图、**Track C 顶刊论文 Figure 1 领域机理对比与多轨模型架构矢量图**） | **`textbook-svg`** | **原生 SVG XML / HTML-to-Pure-SVG**（`svg_tool.py`）；支持 `700~880px` 教材窄画布与顶刊双栏矢量主图（共享学术色板、原生数学公式与 PDF 印刷字号预检） |
| **软件工程拓扑、API 时序、状态机与网页富交互演进图**<br>（微服务拓扑、Sequence 时序、State 状态流转、Web 交互探索） | **`archify`** | **JSON/Mermaid $\rightarrow$ 交互式 HTML + 出版级 Clean SVG** |

### 2. 应当加载本技能的场景
- 需要使用 **Python / Matplotlib** 绘制**学术论文（LaTeX / Typst）定量实验插图、答辩幻灯片或技术报告数据图**，且追求顶会出版级排版审美（去顶/右边框 `spines`、纯正学术配色、独立图例画板）；
- 涉及绘制**定量分组柱状图（Grouped Bars）、超宽横向多指标面板、时序折线图（Trend Lines + 置信带）、多维雷达图（Radar Plots）、热力图（Heatmaps）或 3D 散点/流形分布**；
- 需要输出 **PDF 矢量图、SVG 或 300+ DPI 高清位图**，并严格要求**黑白打印安全（Print-Safe）**（带清晰黑色描边与纹理填充区分）。

### 3. 不应加载本技能的场景
- 绘制不含定量坐标轴的概念模型图、系统架构框图、流程图或时序图（请改用 `textbook-svg` 或 `archify`）；
- Web 交互式仪表盘（如 Plotly, Altair, Bokeh 等前端库）；
- 纯数据探索性（EDA）无需出版级排版雕琢的临时草图。

---

## 二、 八大核心学术绘图设计法则 (Eight Golden Rules)

### 1. 超宽画布比例（Ultra-wide Aspect for Multi-metric Panels）
- 当需要在单行内对比 3~4 个评估指标或大量类别时，切忌使用常规 `4:3` 比例导致柱体与文字挤压。
- **推荐比例**：宽度通常为高度的 3~4 倍，例如 `figsize=(28, 6)`、`figsize=(16, 5)` 或 `figsize=(45, 12)`。
- **价值**：符合从左到右的跨栏阅读习惯，避免 Y 轴标题与图例重叠。

### 2. 独立图例画板（Dedicated Legend Panel）
- 当对比模型或基线超过 4 个时，图例切忌堆叠在数据子图内部遮挡数据点或柱体。
- **标准做法**：
  ```python
  # 创建额外的子图轴（如网格最后一位），并隐藏其坐标轴
  ax_legend = fig.add_subplot(gs[:, -1])
  ax_legend.set_axis_off()
  # 统一在此轴上渲染全局无边框图例
  ax_legend.legend(handles, labels, loc='center', frameon=False, fontsize=14)
  ```

### 3. 简化类别 X 轴标签（Categorical Bars without X-tick Labels）
- 当不同子图代表不同评估指标，而每组柱子对应的方法顺序完全一致时，X 轴不要重复打印冗长的方法名。
- **标准做法**：使用 `ax.set_xticks([])` 隐藏 X 轴刻度文字，依靠顶部图例或独立图例画板识别方法，保持版面清爽。

### 4. 动态紧凑 Y 轴缩放（Dynamic Y-axis Scaling）
- 严禁机械使用 `0~100` 的生硬 Y 轴范围。若各方法的准确率均集中在 `85% ~ 95%`，全量程会压平显著性能差异。
- **标准做法**：动态将 Y 轴下限设为 `data.min() - margin`，上限设为 `data.max() + margin`（例如 `[80, 100]`），诚实且清晰地展现性能梯度。

### 5. 打印与灰度安全隔离（Bar Edge & Hatch for Print-Safe Separation）
- 顶会论文审稿时常被黑白打印，纯靠颜色亮度区分会导致灰度打印后无法辨识。
- **标准做法**：
  - 强制添加黑色清晰描边：`edgecolor='black'`, `linewidth=1.5 ~ 2.5`；
  - 相同色系或消融实验组配合纹理填充：使用 `hatch='/'`, `hatch='\\'`, `hatch='.'`，实现单色打印下的完全可辨。

### 6. 统一的学术语义配色（Semantic Color Palette）
- **蓝色系（Blues, `#0F4D92` / `#3775BA`）**：优先赋予本论文提出的核心新方法（Proposed / Ours），强化第一视觉锚点；
- **绿色系（Greens, `#8BCF8B` / `#AADCA9`）**：赋予改进变体或正向增益组件；
- **红色/暖色系（Reds, `#B64342` / `#E9A6A1`）**：赋予核心外部 SOTA 对比基线（Baselines）；
- **冷灰/中性色（Neutral, `#CFCECE`）**：赋予朴素基线（Vanilla）或消融实验参照组（Ablations）。

### 7. 版心反推最小印刷字号门禁（Target Column Print-Size Gate）
- 当使用超宽画布（如 `17~28 in`）缩印嵌入论文版心（如 A4 `\textwidth = 6.37 in` 或 Nature 双栏 `7.20 in`）时，必须满足 `min_fontsize_pt * (target_width_in / fig_width_in) >= 5.8~6.0 pt`，严禁出现画布 `26 in` 却配 `8~10 pt` 小字导致印刷退化为 `2~3 pt` 蚂蚁字；
- 导出 PDF 后须用 `pdffonts` 确认 `pdf.fonttype = 42`（零 Type 3 字体）并用 `pdftoppm` 200 DPI 目视消碰。

### 8. 有界物理指标定义域严格截断（Domain-Bounded Spine Truncation）
- 对于准确率、Macro-F1（`<= 100%`）或 ROC-AUC、Dice（`<= 1.00`）等有数学物理上限的指标，若为右侧数值标签留白而放宽 `xlim/ylim`（如 `xlim(0.76, 1.16)`），必须配合 `set_xticks([..., 1.00])` 与 `ax.spines["bottom"].set_bounds(min_val, 1.00)` 截断坐标轴脊线，严禁在图上暴露出 `105%` 或 `1.15` 等越界伪刻度。

---

## 三、 按需读取参考文档路由表 (Progressive Disclosure References)

遵循渐进式上下文披露原则，**请勿一次性预加载所有参考文档**，仅根据当前绘图任务按需读取对应的规范文件：

| 参考文档（相对路径） | 何时按需打开 (Open When) |
| :--- | :--- |
| [`scientific-figure-making/references/tutorials.md`](./scientific-figure-making/references/tutorials.md) | 需要查看分组柱状图、多面板共享图例折线图、热力图的**端到端分步实现代码与 Checklist** 时 |
| [`scientific-figure-making/references/api.md`](./scientific-figure-making/references/api.md) | 需要复用标准配色字典 `PALETTE`、`FigureStyle`、`apply_publication_style`、`make_grouped_bar`、`finalize_figure` 等**标准辅助函数签名与参数约定**时 |
| [`scientific-figure-making/references/common-patterns.md`](./scientific-figure-making/references/common-patterns.md) | 需要查阅**超宽画布比例、独立图例轴、无 X 轴刻度柱状图、动态 Y 轴、黑白安全纹理**五大模式的代码片段时 |
| [`scientific-figure-making/references/design-theory.md`](./scientific-figure-making/references/design-theory.md) | 需要深入调整 **`rcParams` 字体层级（Helvetica/Arial）、坐标轴线宽（`axes.linewidth`）、矢量导出参数（PDF/SVG/300 DPI）** 时 |
| [`scientific-figure-making/references/demos.md`](./scientific-figure-making/references/demos.md) | 需要快速检索各顶会真实论文图表 Demo 的分类索引时 |

---

## 四、 本地顶会真实论文代码模版索引 (Canonical Figure Demos)

本技能目录内已完整包含 8 篇顶会/顶刊论文插图的真实 Python 源码，编写绘图脚本前可直接读取对应目录下的 `.py` 源码作为 Few-Shot 模版：

| 图表类型 | 本地目录与核心脚本（相对路径） | 核心特征与技术实现 |
| :--- | :--- | :--- |
| **定量对比柱状图** | [`figure_ImmunoStruct/plot_bars.py`](./figure_ImmunoStruct/plot_bars.py)<br>（数据：[`raw_data.py`](./figure_ImmunoStruct/raw_data.py)） | 多指标横向平铺、独立图例轴、置信区间误差棒（Error Bar）与黑白纹理填充 |
| **分组对比与消融柱状图** | [`figure_CellSpliceNet/plot_comparison.py`](./figure_CellSpliceNet/plot_comparison.py)<br>[`figure_CellSpliceNet/plot_ablation.py`](./figure_CellSpliceNet/plot_ablation.py) | 主实验 SOTA 对比 + 关键模块消融柱状图、显著性标记 |
| **成分分解与分类正确率柱状图** | [`figure_Brainteaser/plot_correctness_by_category.py`](./figure_Brainteaser/plot_correctness_by_category.py)<br>[`figure_Brainteaser/plot_rewriting.py`](./figure_Brainteaser/plot_rewriting.py) | 堆叠/分组条形图、类别细分对比、百分比数值顶标、渐进式色彩层级 |
| **多维雷达图与后训练收敛折线** | [`figure_VIGIL/plot_comparison_radar.py`](./figure_VIGIL/plot_comparison_radar.py)<br>[`figure_VIGIL/plot_posttraining.py`](./figure_VIGIL/plot_posttraining.py)<br>[`figure_VIGIL/plot_ablation.py`](./figure_VIGIL/plot_ablation.py) | 极坐标多维能力雷达图、Post-training 多轮收敛折线、多子图混排 |
| **时序演变趋势与置信带** | [`figure_ophthal_review/plot_trend.py`](./figure_ophthal_review/plot_trend.py)<br>[`figure_ophthal_review/plot_composition.py`](./figure_ophthal_review/plot_composition.py) | 平滑时间序列曲线、阴影置信带（`fill_between`）、年度构成演变 |
| **流形热力图与参数扫描** | [`figure_RNAGenScape/plot_manifold.py`](./figure_RNAGenScape/plot_manifold.py)<br>[`figure_RNAGenScape/plot_hole_manifold.py`](./figure_RNAGenScape/plot_hole_manifold.py)<br>[`figure_RNAGenScape/plot_sweep.py`](./figure_RNAGenScape/plot_sweep.py) | 2D 嵌入流形热力图（Heatmap）、超参数敏感度扫描曲线 |
| **3D 球面流形与散点投影** | [`figure_Dispersion/plot_illustration.py`](./figure_Dispersion/plot_illustration.py)<br>[`figure_Dispersion/plot_idea.py`](./figure_Dispersion/plot_idea.py) | 3D 球体光照渲染投影、特征空间分散度（Dispersion）流形展示、Alpha 透明度混合 |
| **扩散轨迹与基因调控对比** | [`figure_Cflows/plot_comparison_Trajectory.py`](./figure_Cflows/plot_comparison_Trajectory.py)<br>[`figure_Cflows/plot_comparison_Ablation.py`](./figure_Cflows/plot_comparison_Ablation.py)<br>[`figure_Cflows/diffusion_swiss_roll.py`](./figure_Cflows/diffusion_swiss_roll.py) | 动态演化轨迹流图、Swiss Roll 扩散过程可视化、多维消融对比 |
