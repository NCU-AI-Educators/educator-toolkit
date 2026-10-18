# Textbook SVG 高信息密度写作配图模板库 (880px 1+N Rich HTML/PNG Archetypes)

针对深度研究报告、规划指南、教材核心系统章节等 **高信息密度写作场景**（单图节点 > 6 个、包含完整技术机制长句、或具有“多层架构 + 物理原语 + 落地矩阵”复合维度），若强行塞入单张宽画布（如 `1400px`），嵌入文档版心后字号会被等比缩小近一半。

本模板库采用 **“固定 `880px` 黄金窄画布 + 大字号体系（正文 `13.5px~14px`、标题 `15px~19.5px`）+ 1 张全景总图与 N 张专题子图解耦”** 范式，通过 `svg_tool.py render-html` 导出为 2x Retina 高清 `.png`，在 Markdown、Word（`.docx`）与 Typst（`.pdf`）中均能实现接近 1:1 免缩放直出。

---

## 模板一：全景多层架构与子图导航总图 (`html-overview`)

- **适用场景**：复杂系统的“1+N”总览主图（如端云协同四层架构 + 底部落地分流矩阵），建立全局骨骼并标注各专题子图语义索引（**注意：严禁在图内硬编码“图 1 / 子图 2a”等编号，图号仅在正文题注中体现**）。
- **画布宽度**：`width: 880px`，层间采用横向流向胶囊条（`flow-bar`），层内采用等宽三栏摘要卡片（`grid-template-columns: repeat(3, 1fr)`）。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>全景分层架构总图</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #0f172a;
    padding: 12px;
    display: inline-block;
  }
  .fig-card {
    width: 880px;
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 18px 20px 16px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  }
  .fig-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 12px;
    margin-bottom: 14px;
  }
  .fig-header h1 {
    font-size: 19.5px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.01em;
    line-height: 1.3;
  }
  .fig-header .sub {
    font-size: 13px;
    color: #475569;
    margin-top: 4px;
    font-weight: 500;
  }
  .fig-badge {
    background: #1e293b;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    white-space: nowrap;
  }
  .tier-row {
    border-radius: 12px;
    border: 2px solid;
    padding: 12px 14px;
  }
  .tier-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 7px;
    border-bottom: 1.5px dashed;
  }
  .tier-head-left {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15.5px;
    font-weight: 800;
  }
  .tier-pill {
    font-size: 12.5px;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 6px;
    color: #ffffff;
  }
  .tier-metric {
    font-size: 12.5px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1.5px solid;
  }
  .tier-body {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .node-box {
    background: rgba(255, 255, 255, 0.92);
    border: 1.5px solid;
    border-radius: 9px;
    padding: 9px 11px;
  }
  .node-title {
    font-size: 14.5px;
    font-weight: 800;
    margin-bottom: 4px;
    line-height: 1.3;
  }
  .node-tags {
    font-size: 13px;
    color: #334155;
    line-height: 1.45;
  }
  .node-ref {
    display: inline-block;
    margin-top: 5px;
    font-size: 12px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 5px;
  }
  /* 语义色板：Tier 1 靛紫 / Tier 2 天际蓝 / Tier 3 琥珀金 / Tier 4 翡翠绿 */
  .t1 { background: #f5f3ff; border-color: #8b5cf6; }
  .t1 .tier-head { border-color: #c4b5fd; color: #4c1d95; }
  .t1 .tier-pill { background: #6d28d9; }
  .t1 .tier-metric { background: #ede9fe; border-color: #a78bfa; color: #5b21b6; }
  .t1 .node-box { border-color: #ddd6fe; }
  .t1 .node-title { color: #5b21b6; }
  .t1 .node-ref { background: #ede9fe; color: #6d28d9; }

  .t2 { background: #f0f9ff; border-color: #0284c7; }
  .t2 .tier-head { border-color: #7dd3fc; color: #0c4a6e; }
  .t2 .tier-pill { background: #0369a1; }
  .t2 .tier-metric { background: #e0f2fe; border-color: #38bdf8; color: #0369a1; }
  .t2 .node-box { border-color: #bae6fd; }
  .t2 .node-title { color: #0369a1; }
  .t2 .node-ref { background: #e0f2fe; color: #0369a1; }

  .t3 { background: #fffbeb; border-color: #d97706; }
  .t3 .tier-head { border-color: #fcd34d; color: #78350f; }
  .t3 .tier-pill { background: #b45309; }
  .t3 .tier-metric { background: #fef3c7; border-color: #fbbf24; color: #92400e; }
  .t3 .node-box { border-color: #fde68a; }
  .t3 .node-title { color: #92400e; }
  .t3 .node-ref { background: #fef3c7; color: #b45309; }

  .t4 { background: #ecfdf5; border-color: #059669; }
  .t4 .tier-head { border-color: #6ee7b7; color: #064e3b; }
  .t4 .tier-pill { background: #047857; }
  .t4 .tier-metric { background: #d1fae5; border-color: #34d399; color: #065f46; }
  .t4 .node-box { border-color: #a7f3d0; }
  .t4 .node-title { color: #065f46; }
  .t4 .node-ref { background: #d1fae5; color: #047857; }

  .flow-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin: 7px 0;
  }
  .flow-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #f8fafc;
    border: 1.5px solid #94a3b8;
    color: #1e293b;
    font-size: 12.5px;
    font-weight: 700;
    padding: 3px 12px;
    border-radius: 999px;
  }
  .fig-footer {
    margin-top: 12px;
    padding-top: 9px;
    border-top: 1.5px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #475569;
    font-weight: 600;
  }
</style>
</head>
<body>
<figure class="fig-card" id="capture-target">
  <div class="fig-header">
    <div>
      <h1>系统全景分层架构与多维落地方案总图</h1>
      <div class="sub">上层核心算法底座 ➔ 中层实时策略闭环 ➔ 底层工程原语与分流矩阵（含三大专题子图）</div>
    </div>
    <div class="fig-badge">全景架构总图</div>
  </div>

  <div class="tier-row t1">
    <div class="tier-head">
      <div class="tier-head-left">
        <span class="tier-pill">Tier 1 · 核心层</span>
        <span>上层中枢模块名称与核心定位</span>
      </div>
      <span class="tier-metric">核心性能指标 ｜ 资源配比</span>
    </div>
    <div class="tier-body">
      <div class="node-box">
        <div class="node-title">核心子模块 1.1</div>
        <div class="node-tags">精炼提炼该模块的核心输入、算法机制与输出产物</div>
        <div class="node-ref">关联说明（核心算法专题子图）</div>
      </div>
      <div class="node-box">
        <div class="node-title">核心子模块 1.2</div>
        <div class="node-tags">精炼提炼该模块的核心输入、算法机制与输出产物</div>
        <div class="node-ref">关联说明（核心算法专题子图）</div>
      </div>
      <div class="node-box">
        <div class="node-title">核心子模块 1.3</div>
        <div class="node-tags">精炼提炼该模块的核心输入、算法机制与输出产物</div>
        <div class="node-ref">关联说明（核心算法专题子图）</div>
      </div>
    </div>
  </div>

  <div class="flow-bar">
    <span class="flow-chip">▼ 下行传递机制一</span>
    <span class="flow-chip">▼ 下行传递机制二</span>
    <span class="flow-chip">▲ 上行数据反馈回路</span>
  </div>

  <div class="tier-row t2">
    <div class="tier-head">
      <div class="tier-head-left">
        <span class="tier-pill">Tier 2 · 策略层</span>
        <span>中层实时感知与计算执行闭环</span>
      </div>
      <span class="tier-metric">实时响应指标 ｜ 算力配额</span>
    </div>
    <div class="tier-body">
      <div class="node-box">
        <div class="node-title">策略子模块 2.1</div>
        <div class="node-tags">精炼提炼该模块的核心实时策略与关键约束</div>
        <div class="node-ref">关联说明（核心算法专题子图）</div>
      </div>
      <div class="node-box">
        <div class="node-title">策略子模块 2.2</div>
        <div class="node-tags">精炼提炼该模块的核心实时策略与关键约束</div>
        <div class="node-ref">关联说明（核心算法专题子图）</div>
      </div>
      <div class="node-box">
        <div class="node-title">策略子模块 2.3</div>
        <div class="node-tags">精炼提炼该模块的核心实时策略与关键约束</div>
        <div class="node-ref">关联说明（核心算法专题子图）</div>
      </div>
    </div>
  </div>

  <div class="fig-footer">
    <span><strong>专题子图组成：</strong>核心算法与实时策略子图 ｜ 底层物理工程原语子图 ｜ 应用落地矩阵子图</span>
    <span>架构总览</span>
  </div>
</figure>
</body>
</html>
```

---

## 模板二：上下游双层深度堆叠与双向桥接子图 (`html-stack`)

- **适用场景**：对总图中上下相邻的两个核心层级（如“云端慢思考教师模型层 vs 端侧快思考实时推理层”）进行全宽大字号深度展开，每张卡片支持 2~3 行完整技术机制阐述与右侧角色角标。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>双层深度堆叠子图</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #0f172a;
    padding: 12px;
    display: inline-block;
  }
  .fig-card {
    width: 880px;
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 18px 20px 16px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  }
  .fig-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 12px;
    margin-bottom: 14px;
  }
  .fig-header h1 {
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.3;
  }
  .fig-header .sub {
    font-size: 13.5px;
    color: #475569;
    margin-top: 4px;
    font-weight: 500;
  }
  .fig-badge {
    background: #4c1d95;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    white-space: nowrap;
  }
  .panel {
    border: 2px solid;
    border-radius: 12px;
    padding: 14px 16px;
  }
  .panel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 9px;
    margin-bottom: 12px;
    border-bottom: 1.5px solid;
  }
  .panel-head-left {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
    font-weight: 800;
  }
  .tag-pill {
    font-size: 12.5px;
    font-weight: 800;
    padding: 4px 10px;
    border-radius: 6px;
    color: #ffffff;
  }
  .quota-pill {
    font-size: 13px;
    font-weight: 700;
    padding: 4px 11px;
    border-radius: 999px;
    border: 1.5px solid;
  }
  .card-stack {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .detail-card {
    background: #ffffff;
    border: 1.5px solid;
    border-radius: 10px;
    padding: 11px 14px;
  }
  .detail-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
  }
  .detail-title {
    font-size: 15px;
    font-weight: 800;
  }
  .detail-role {
    font-size: 12.5px;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 6px;
  }
  .detail-desc {
    font-size: 13.5px;
    color: #1e293b;
    line-height: 1.52;
  }
  .detail-desc strong { font-weight: 700; }

  .p-top { background: #f5f3ff; border-color: #8b5cf6; }
  .p-top .panel-head { border-color: #c4b5fd; color: #4c1d95; }
  .p-top .tag-pill { background: #6d28d9; }
  .p-top .quota-pill { background: #ede9fe; border-color: #a78bfa; color: #5b21b6; }
  .p-top .detail-card { border-color: #c4b5fd; }
  .p-top .detail-title { color: #4c1d95; }
  .p-top .detail-role { background: #ede9fe; color: #5b21b6; }
  .p-top .detail-desc strong { color: #5b21b6; }

  .p-bot { background: #f0f9ff; border-color: #0284c7; }
  .p-bot .panel-head { border-color: #7dd3fc; color: #0c4a6e; }
  .p-bot .tag-pill { background: #0369a1; }
  .p-bot .quota-pill { background: #e0f2fe; border-color: #38bdf8; color: #0369a1; }
  .p-bot .detail-card { border-color: #7dd3fc; }
  .p-bot .detail-title { color: #0c4a6e; }
  .p-bot .detail-role { background: #e0f2fe; color: #0369a1; }
  .p-bot .detail-desc strong { color: #0369a1; }

  .bridge-zone {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 10px 0;
  }
  .bridge-item {
    background: #f8fafc;
    border: 1.5px dashed #64748b;
    border-radius: 9px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 700;
    color: #0f172a;
  }
  .bridge-badge {
    background: #334155;
    color: #ffffff;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 5px;
  }
  .fig-footer {
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1.5px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #475569;
    font-weight: 600;
  }
</style>
</head>
<body>
<figure class="fig-card" id="capture-target">
  <div class="fig-header">
    <div>
      <h1>上下游协同机制与技术模块深度展开图</h1>
      <div class="sub">详细展示上层核心底座与下层执行系统的内部技术链路及双向反馈接口</div>
    </div>
    <div class="fig-badge">专题子图 ①</div>
  </div>

  <div class="panel p-top">
    <div class="panel-head">
      <div class="panel-head-left">
        <span class="tag-pill">上层底座</span>
        <span>上层模块名称与核心架构定位</span>
      </div>
      <span class="quota-pill">运行频率 ｜ 资源预算</span>
    </div>
    <div class="card-stack">
      <div class="detail-card">
        <div class="detail-top">
          <div class="detail-title">1. 核心技术模块一标题</div>
          <span class="detail-role">赋能范围 / 接口标签</span>
        </div>
        <div class="detail-desc">在此填写完整的技术机制说明，重点关键词使用 <strong>加粗语义高亮</strong>，支持多行自动折行展示而不必截断核心逻辑。</div>
      </div>
      <div class="detail-card">
        <div class="detail-top">
          <div class="detail-title">2. 核心技术模块二标题</div>
          <span class="detail-role">赋能范围 / 接口标签</span>
        </div>
        <div class="detail-desc">在此填写完整的技术机制说明，重点关键词使用 <strong>加粗语义高亮</strong>，清晰呈现输入输出与算法约束。</div>
      </div>
    </div>
  </div>

  <div class="bridge-zone">
    <div class="bridge-item"><span class="bridge-badge">下行通道</span>▼ 上层向下层下发的核心模型或控制流</div>
    <div class="bridge-item"><span class="bridge-badge">上行通道</span>▲ 下层向上层回传的实时观测或数据流</div>
  </div>

  <div class="panel p-bot">
    <div class="panel-head">
      <div class="panel-head-left">
        <span class="tag-pill">下层闭环</span>
        <span>下层模块名称与实时执行策略</span>
      </div>
      <span class="quota-pill">响应延迟 ｜ 部署形态</span>
    </div>
    <div class="card-stack">
      <div class="detail-card">
        <div class="detail-top">
          <div class="detail-title">1. 实时执行模块一标题</div>
          <span class="detail-role">性能门禁指标</span>
        </div>
        <div class="detail-desc">在此填写下层执行模块的详细机制与 <strong>关键量化参数</strong>，与上层模块形成严密的上下游映射。</div>
      </div>
    </div>
  </div>

  <div class="fig-footer">
    <span><strong>核心纪律：</strong>一句话总结该子图的核心工程调度或协同原则</span>
    <span>专题子图 ①（对应总图 Tier 1 &amp; Tier 2）</span>
  </div>
</figure>
</body>
</html>
```

---

## 模板三：带编号工程原语 + 2×2 硬件/外设矩阵子图 (`html-primitives`)

- **适用场景**：上半部分展示 3 大核心工程原语/算法定理（左侧大号数字徽章 `1/2/3` + 中间痛点与机制详解 + 右侧适用标签），下半部分通过 `2×2` 网格展示 4 类硬件形态或子系统配置。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>工程原语与2x2矩阵子图</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #0f172a;
    padding: 12px;
    display: inline-block;
  }
  .fig-card {
    width: 880px;
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 18px 20px 16px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  }
  .fig-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 12px;
    margin-bottom: 14px;
  }
  .fig-header h1 { font-size: 19px; font-weight: 800; color: #0f172a; line-height: 1.3; }
  .fig-header .sub { font-size: 13.5px; color: #475569; margin-top: 4px; font-weight: 500; }
  .fig-badge {
    background: #b45309;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    white-space: nowrap;
  }
  .section-box {
    border: 2px solid;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
  }
  .sec-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    margin-bottom: 12px;
    border-bottom: 1.5px solid;
  }
  .sec-title { display: flex; align-items: center; gap: 9px; font-size: 16px; font-weight: 800; }
  .sec-pill { font-size: 12.5px; font-weight: 800; padding: 3px 10px; border-radius: 6px; color: #ffffff; }
  .sec-metric { font-size: 12.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px; border: 1.5px solid; }

  .s-amber { background: #fffbeb; border-color: #d97706; }
  .s-amber .sec-head { border-color: #fcd34d; color: #78350f; }
  .s-amber .sec-pill { background: #b45309; }
  .s-amber .sec-metric { background: #fef3c7; border-color: #fbbf24; color: #92400e; }

  .prim-list { display: flex; flex-direction: column; gap: 10px; }
  .prim-card {
    background: #ffffff;
    border: 1.5px solid #fbbf24;
    border-radius: 10px;
    padding: 11px 14px;
    display: grid;
    grid-template-columns: 36px 1fr;
    gap: 12px;
    align-items: start;
  }
  .prim-num {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: #d97706;
    color: #ffffff;
    font-size: 16px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 2px;
  }
  .prim-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .prim-name { font-size: 15px; font-weight: 800; color: #78350f; }
  .prim-target { background: #fef3c7; color: #92400e; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 5px; }
  .prim-desc { font-size: 13.5px; color: #1e293b; line-height: 1.5; }
  .prim-desc strong { color: #92400e; font-weight: 700; }

  .s-slate { background: #f8fafc; border-color: #64748b; margin-bottom: 0; }
  .s-slate .sec-head { border-color: #cbd5e1; color: #0f172a; }
  .s-slate .sec-pill { background: #334155; }
  .s-slate .sec-metric { background: #f1f5f9; border-color: #94a3b8; color: #334155; }

  .grid-2x2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .hw-card { background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 10px; padding: 11px 13px; }
  .hw-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
  .hw-name { font-size: 14.5px; font-weight: 800; color: #0f172a; }
  .hw-tag { background: #e2e8f0; color: #1e293b; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 5px; }
  .hw-desc { font-size: 13px; color: #334155; line-height: 1.48; }
  .hw-desc strong { color: #0f172a; font-weight: 700; }

  .fig-footer {
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1.5px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #475569;
    font-weight: 600;
  }
</style>
</head>
<body>
<figure class="fig-card" id="capture-target">
  <div class="fig-header">
    <div>
      <h1>核心工程原语与底层硬件/子系统配置详图</h1>
      <div class="sub">上半部详解三大底层工程原语机制，下半部展示 2×2 硬件与子系统矩阵</div>
    </div>
    <div class="fig-badge">专题子图 ②</div>
  </div>

  <div class="section-box s-amber">
    <div class="sec-head">
      <div class="sec-title"><span class="sec-pill">核心原语</span><span>底层确定性工程原语与理论防线</span></div>
      <span class="sec-metric">关键性能指标 ｜ 资源占用</span>
    </div>
    <div class="prim-list">
      <div class="prim-card">
        <div class="prim-num">1</div>
        <div>
          <div class="prim-top">
            <div class="prim-name">原语一名称</div>
            <span class="prim-target">适用模块范围</span>
          </div>
          <div class="prim-desc"><strong>痛点与机制：</strong>详细描述工程痛点与核心解决机制，包含 <strong>关键量化指标</strong>。</div>
        </div>
      </div>
      <div class="prim-card">
        <div class="prim-num">2</div>
        <div>
          <div class="prim-top">
            <div class="prim-name">原语二名称</div>
            <span class="prim-target">适用模块范围</span>
          </div>
          <div class="prim-desc"><strong>痛点与机制：</strong>详细描述工程痛点与核心解决机制，包含 <strong>关键量化指标</strong>。</div>
        </div>
      </div>
    </div>
  </div>

  <div class="section-box s-slate">
    <div class="sec-head">
      <div class="sec-title"><span class="sec-pill">子系统矩阵</span><span>2×2 硬件外设或子系统支撑形态</span></div>
      <span class="sec-metric">高可靠 · 易复现</span>
    </div>
    <div class="grid-2x2">
      <div class="hw-card">
        <div class="hw-top"><div class="hw-name">子系统 A</div><span class="hw-tag">定位标签</span></div>
        <div class="hw-desc">描述子系统核心参数与 <strong>工程优势</strong>。</div>
      </div>
      <div class="hw-card">
        <div class="hw-top"><div class="hw-name">子系统 B</div><span class="hw-tag">定位标签</span></div>
        <div class="hw-desc">描述子系统核心参数与 <strong>工程优势</strong>。</div>
      </div>
    </div>
  </div>

  <div class="fig-footer">
    <span><strong>核心结论：</strong>总结底层原语对上层系统的支撑作用</span>
    <span>专题子图 ②（对应总图 Tier 3）</span>
  </div>
</figure>
</body>
</html>
```

---

## 模板四：多通道分流与项目/团队矩阵子图 (`html-matrix`)

- **适用场景**：将多个子课题、产品线或参赛团队按通道/赛道（`ch-1 / ch-2 / ch-3`）分流排布，每张卡片包含 **标题 + 右侧负责人徽章 + 核心研究内容描述 + 底部独立交付物高亮条（`team-deliver`）**。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>多通道分流矩阵子图</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #0f172a;
    padding: 12px;
    display: inline-block;
  }
  .fig-card {
    width: 880px;
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 18px 20px 16px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  }
  .fig-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 12px;
    margin-bottom: 14px;
  }
  .fig-header h1 { font-size: 19px; font-weight: 800; color: #0f172a; line-height: 1.3; }
  .fig-header .sub { font-size: 13.5px; color: #475569; margin-top: 4px; font-weight: 500; }
  .fig-badge {
    background: #047857;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    white-space: nowrap;
  }
  .channel-box {
    border: 2px solid;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
  }
  .channel-box:last-of-type { margin-bottom: 0; }
  .channel-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 8px;
    margin-bottom: 10px;
    border-bottom: 1.5px solid;
    font-size: 15.5px;
    font-weight: 800;
  }
  .ch-tag { font-size: 12.5px; font-weight: 800; padding: 3px 10px; border-radius: 6px; color: #ffffff; margin-right: 8px; }
  .ch-rule { font-size: 12.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px; border: 1.5px solid; }
  .team-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .team-card {
    background: #ffffff;
    border: 1.5px solid;
    border-radius: 9px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .team-top { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 5px; }
  .team-name { font-size: 14.5px; font-weight: 800; }
  .leader-badge { font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 5px; white-space: nowrap; }
  .team-desc { font-size: 13px; color: #1e293b; line-height: 1.46; margin-bottom: 6px; }
  .team-deliver { font-size: 12.5px; font-weight: 700; padding: 4px 8px; border-radius: 6px; border-left: 3px solid; }

  .ch-1 { background: #f0f9ff; border-color: #0284c7; }
  .ch-1 .channel-head { border-color: #7dd3fc; color: #0c4a6e; }
  .ch-1 .ch-tag { background: #0369a1; }
  .ch-1 .ch-rule { background: #e0f2fe; border-color: #38bdf8; color: #0369a1; }
  .ch-1 .team-card { border-color: #7dd3fc; }
  .ch-1 .team-name { color: #0c4a6e; }
  .ch-1 .leader-badge { background: #e0f2fe; color: #0369a1; }
  .ch-1 .team-deliver { background: #f0f9ff; border-color: #0284c7; color: #0369a1; }

  .ch-2 { background: #ecfdf5; border-color: #059669; }
  .ch-2 .channel-head { border-color: #6ee7b7; color: #064e3b; }
  .ch-2 .ch-tag { background: #047857; }
  .ch-2 .ch-rule { background: #d1fae5; border-color: #34d399; color: #065f46; }
  .ch-2 .team-card { border-color: #6ee7b7; }
  .ch-2 .team-name { color: #064e3b; }
  .ch-2 .leader-badge { background: #d1fae5; color: #047857; }
  .ch-2 .team-deliver { background: #ecfdf5; border-color: #059669; color: #065f46; }

  .fig-footer {
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1.5px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #475569;
    font-weight: 600;
  }
</style>
</head>
<body>
<figure class="fig-card" id="capture-target">
  <div class="fig-header">
    <div>
      <h1>多通道分流矩阵与独立交付物映射详图</h1>
      <div class="sub">按赛道/通道属性精准切分任务单元，确保各单元权责清晰、交付物独立闭环</div>
    </div>
    <div class="fig-badge">专题子图 ③</div>
  </div>

  <div class="channel-box ch-1">
    <div class="channel-head">
      <div><span class="ch-tag">通道一</span>第一类核心通道名称与定位</div>
      <span class="ch-rule">核心规则与名额约束</span>
    </div>
    <div class="team-grid-2">
      <div class="team-card">
        <div class="team-top">
          <div class="team-name">单元 1：子课题/模块名称</div>
          <span class="leader-badge">负责人/角色标签</span>
        </div>
        <div class="team-desc">详细说明该单元的核心研究内容、硬件/算法形态与应用场景。</div>
        <div class="team-deliver">交付物：明确列举论文/专利/软著/系统样机等核心产出</div>
      </div>
      <div class="team-card">
        <div class="team-top">
          <div class="team-name">单元 2：子课题/模块名称</div>
          <span class="leader-badge">负责人/角色标签</span>
        </div>
        <div class="team-desc">详细说明该单元的核心研究内容、硬件/算法形态与应用场景。</div>
        <div class="team-deliver">交付物：明确列举论文/专利/软著/系统样机等核心产出</div>
      </div>
    </div>
  </div>

  <div class="fig-footer">
    <span><strong>风控准则：</strong>各单元独立代码仓与独立知识产权闭环</span>
    <span>专题子图 ③（对应总图底层矩阵）</span>
  </div>
</figure>
</body>
</html>
```

---

## 模板五：KPI 核心指标看板与定量阶梯条形信息图 (`html-infographic`)

- **适用场景**：将宏观总体规模（顶部 4 栏大字号 KPI 指标卡，支持高亮重点卡片）与定量分布/漏斗阶梯对比（底部带比例轨道、圆角柱体、数值占比标注与坐标轴刻度的水平条形图）融合为一张 `880px` 信息图。无需依赖 `<canvas>`，可通过 `render-html` 直接编译为 100% 纯正原生 `.svg` 与 `2x Retina .png`。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<title>KPI核心指标与定量阶梯分布信息图</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #0f172a;
    padding: 12px;
    display: inline-block;
  }
  .fig-card {
    width: 880px;
    background: #ffffff;
    border: 2px solid #cbd5e1;
    border-radius: 14px;
    padding: 18px 20px 16px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
  }
  .fig-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 12px;
    margin-bottom: 14px;
    gap: 12px;
  }
  .fig-header h1 { font-size: 19px; font-weight: 800; color: #0f172a; line-height: 1.3; }
  .fig-header .sub { font-size: 13.2px; color: #475569; margin-top: 4px; font-weight: 500; line-height: 1.4; }
  .fig-badge {
    background: #0369a1;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 8px;
    white-space: nowrap;
    flex-shrink: 0;
  }
  /* Top 4 KPI Cards */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
  }
  .kpi-card {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 11px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .kpi-card.highlight {
    background: #f0f9ff;
    border: 2px solid #0284c7;
  }
  .kpi-label {
    font-size: 13.5px;
    font-weight: 700;
    color: #475569;
  }
  .kpi-card.highlight .kpi-label {
    color: #0369a1;
  }
  .kpi-val-row {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin: 2px 0;
  }
  .kpi-num {
    font-size: 25px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
  }
  .kpi-card.highlight .kpi-num {
    color: #0284c7;
  }
  .kpi-unit {
    font-size: 13.5px;
    font-weight: 700;
    color: #475569;
  }
  .kpi-card.highlight .kpi-unit {
    color: #0369a1;
  }
  .kpi-sub {
    font-size: 12.5px;
    font-weight: 600;
    color: #64748b;
  }
  .kpi-card.highlight .kpi-sub {
    color: #0369a1;
    font-weight: 700;
  }
  /* Bottom Horizontal Bar Chart Panel */
  .chart-panel {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 12px;
    padding: 14px 16px;
  }
  .chart-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 10px;
    margin-bottom: 12px;
    border-bottom: 1.5px dashed #cbd5e1;
    gap: 12px;
  }
  .chart-title {
    font-size: 16px;
    font-weight: 800;
    color: #0f172a;
  }
  .chart-sub {
    font-size: 13px;
    color: #475569;
    margin-top: 3px;
    font-weight: 500;
  }
  .legend-row {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-shrink: 0;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12.5px;
    font-weight: 700;
    color: #334155;
  }
  .legend-swatch {
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }
  .bar-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .bar-row {
    display: grid;
    grid-template-columns: 74px 1fr;
    align-items: center;
    gap: 12px;
  }
  .bar-label {
    font-size: 14px;
    font-weight: 800;
    color: #1e293b;
    text-align: right;
  }
  .bar-track {
    height: 32px;
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    padding: 0 10px 0 4px;
  }
  .bar-fill {
    height: 22px;
    border-radius: 5px;
  }
  .bar-val {
    margin-left: 10px;
    font-size: 13.5px;
    font-weight: 800;
    color: #0f172a;
    white-space: nowrap;
  }
  .axis-row {
    display: grid;
    grid-template-columns: 74px 1fr;
    gap: 12px;
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1.5px solid #cbd5e1;
  }
  .axis-label {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    text-align: right;
  }
  .axis-ticks {
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    font-weight: 700;
    color: #475569;
    padding: 0 4px;
  }
  .fig-footer {
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1.5px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    color: #475569;
    font-weight: 600;
  }
</style>
</head>
<body>
<figure class="fig-card" id="capture-target">
  <div class="fig-header">
    <div>
      <h1>总体规模核心指标与全国奖项阶梯分布信息图</h1>
      <div class="sub">顶部展示四大宏观规模指标，底部展示四级阶梯漏斗定量分布与晋级比例</div>
    </div>
    <div class="fig-badge">数据信息图</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">指标维度一</div>
      <div class="kpi-val-row"><span class="kpi-num">2700+</span><span class="kpi-unit">所</span></div>
      <div class="kpi-sub">覆盖范围说明文字</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">指标维度二</div>
      <div class="kpi-val-row"><span class="kpi-num">300+</span><span class="kpi-unit">万名</span></div>
      <div class="kpi-sub">参与群体说明文字</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">指标维度三</div>
      <div class="kpi-val-row"><span class="kpi-num">40+</span><span class="kpi-unit">万件</span></div>
      <div class="kpi-sub">样本基数说明文字</div>
    </div>
    <div class="kpi-card highlight">
      <div class="kpi-label">核心焦点指标</div>
      <div class="kpi-val-row"><span class="kpi-num">96</span><span class="kpi-unit">项</span></div>
      <div class="kpi-sub">核心转化率仅约 0.024%</div>
    </div>
  </div>

  <div class="chart-panel">
    <div class="chart-head">
      <div>
        <div class="chart-title">四级阶梯漏斗定量对比分布</div>
        <div class="chart-sub">呈现严格金字塔筛选结构，顶层要求极高的理论深度与工程闭环</div>
      </div>
      <div class="legend-row">
        <div class="legend-item"><span class="legend-swatch" style="background:#1d4ed8;"></span>第一梯队</div>
        <div class="legend-item"><span class="legend-swatch" style="background:#0284c7;"></span>第二梯队</div>
        <div class="legend-item"><span class="legend-swatch" style="background:#64748b;"></span>第三/四梯队</div>
      </div>
    </div>

    <div class="bar-list">
      <div class="bar-row">
        <div class="bar-label">特等奖</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: 8.0%; background: #1d4ed8;"></div>
          <span class="bar-val" style="color: #1d4ed8;">96 项（占获奖总数 5.8%）</span>
        </div>
      </div>
      <div class="bar-row">
        <div class="bar-label">一等奖</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: 15.6%; background: #0284c7;"></div>
          <span class="bar-val" style="color: #0369a1;">187 项（占获奖总数 11.4%）</span>
        </div>
      </div>
      <div class="bar-row">
        <div class="bar-label">二等奖</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: 30.8%; background: #64748b;"></div>
          <span class="bar-val">369 项（占获奖总数 22.4%）</span>
        </div>
      </div>
      <div class="bar-row">
        <div class="bar-label">三等奖</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: 82.8%; background: #94a3b8;"></div>
          <span class="bar-val">993 项（占获奖总数 60.4%）</span>
        </div>
      </div>
    </div>

    <div class="axis-row">
      <div class="axis-label">数量刻度</div>
      <div class="axis-ticks">
        <span>0</span>
        <span>200</span>
        <span>400</span>
        <span>600</span>
        <span>800</span>
        <span>1,000</span>
        <span>1,200 项</span>
      </div>
    </div>
  </div>

  <div class="fig-footer">
    <span><strong>数据洞察：</strong>一句话总结该定量分布揭示的核心规律</span>
    <span>定量信息图</span>
  </div>
</figure>
</body>
</html>
```
