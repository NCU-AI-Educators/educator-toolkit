# Textbook SVG 四大教材构图母版完整参考模板 (Canonical Archetypes)

本文档提供经过 A4 教材版心实测的四套标准 SVG 母版源码，所有坐标、阴影滤镜、箭头 `marker` 与字号均已调优对齐。

---

## 母版一：横向三支柱 / 三阶段演进与闭环回流图 (`pillars`)

- **无底部回流画布**：`viewBox="0 0 760 212" width="760" height="212"`
- **带底部回流画布**：`viewBox="0 0 760 250" width="760" height="250"`
- **卡片网格坐标**：`x = 11`（第 1 栏）、`x = 274`（第 2 栏）、`x = 537`（第 3 栏），卡片尺寸均为 `width="212" height="172" rx="8"`。

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 250" width="760" height="250" style="background:#FFFFFF;">
  <defs>
    <style>
      text, tspan { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
    </style>
    <filter id="shadow-pillars" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.06"/>
    </filter>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#0284C7"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#9333EA"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#10B981"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#D97706"/>
    </marker>
  </defs>

  <!-- 支柱 1 (天际蓝) -->
  <g transform="translate(11, 16)">
    <rect width="212" height="172" rx="8" ry="8" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.5" filter="url(#shadow-pillars)"/>
    <text x="106" y="28" font-size="15" font-weight="bold" fill="#0369A1" text-anchor="middle">1. 第一阶段标题</text>
    <line x1="12" y1="40" x2="200" y2="40" stroke="#BAE6FD" stroke-width="1"/>
    <text x="12" y="66" font-size="13" fill="#082F49">
      <tspan x="12" dy="0"><tspan font-weight="bold" fill="#0284C7">• 核心职责</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#0284C7">• 关键动作</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#0284C7">• 机制特征</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#0284C7">• 系统定位</tspan> | 简明描述八到十字</tspan>
    </text>
  </g>

  <!-- 过渡箭头 1 -> 2 -->
  <text x="248.5" y="86" font-size="12" font-weight="bold" fill="#0369A1" text-anchor="middle">正向传递</text>
  <line x1="228" y1="102" x2="267" y2="102" stroke="#0284C7" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="248.5" y="122" font-size="12" fill="#64748B" text-anchor="middle">阶段衔接</text>

  <!-- 支柱 2 (皇家紫 或 翡翠绿) -->
  <g transform="translate(274, 16)">
    <rect width="212" height="172" rx="8" ry="8" fill="#FAF5FF" stroke="#A855F7" stroke-width="1.5" filter="url(#shadow-pillars)"/>
    <text x="106" y="28" font-size="15" font-weight="bold" fill="#7E22CE" text-anchor="middle">2. 第二阶段标题</text>
    <line x1="12" y1="40" x2="200" y2="40" stroke="#E9D5FF" stroke-width="1"/>
    <text x="12" y="66" font-size="13" fill="#3B0764">
      <tspan x="12" dy="0"><tspan font-weight="bold" fill="#9333EA">• 核心职责</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#9333EA">• 关键动作</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#9333EA">• 机制特征</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#9333EA">• 系统定位</tspan> | 简明描述八到十字</tspan>
    </text>
  </g>

  <!-- 过渡箭头 2 -> 3 -->
  <text x="511.5" y="86" font-size="12" font-weight="bold" fill="#047857" text-anchor="middle">终审放行</text>
  <line x1="491" y1="102" x2="530" y2="102" stroke="#10B981" stroke-width="2" marker-end="url(#arrow-green)"/>
  <text x="511.5" y="122" font-size="12" fill="#64748B" text-anchor="middle">移交执行</text>

  <!-- 支柱 3 (翡翠绿 或 琥珀金) -->
  <g transform="translate(537, 16)">
    <rect width="212" height="172" rx="8" ry="8" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" filter="url(#shadow-pillars)"/>
    <text x="106" y="28" font-size="15" font-weight="bold" fill="#047857" text-anchor="middle">3. 第三阶段标题</text>
    <line x1="12" y1="40" x2="200" y2="40" stroke="#A7F3D0" stroke-width="1"/>
    <text x="12" y="66" font-size="13" fill="#064E3B">
      <tspan x="12" dy="0"><tspan font-weight="bold" fill="#059669">• 核心职责</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#059669">• 关键动作</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#0284C7">• 机制特征</tspan> | 简明描述八到十字</tspan>
      <tspan x="12" dy="28"><tspan font-weight="bold" fill="#059669">• 系统定位</tspan> | 简明描述八到十字</tspan>
    </text>
  </g>

  <!-- 可选：底部反馈闭环 3 -> 1（注意：路径从右向左，文本内部必须使用 ◀── 与箭头方向保持一致！） -->
  <path d="M 643 188 L 643 224 L 117 224 L 117 194" fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrow-amber)"/>
  <rect x="165" y="210" width="430" height="26" rx="13" ry="13" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1.2"/>
  <text x="380" y="228" font-size="12.5" font-weight="bold" fill="#B45309" text-anchor="middle">左端接收方验收与闭环修正 ◀── 右端执行结果呈现与反馈</text>
</svg>
```

---

## 母版二：2×2 四象限概念矩阵图 (`matrix`)

- **画布尺寸**：`viewBox="0 0 700 360" width="700" height="360"`
- **卡片网格坐标**：左上 `(16, 18)`、右上 `(360, 18)`、左下 `(16, 190)`、右下 `(360, 190)`，卡片尺寸 `width="324" height="152" rx="8"`。

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 360" width="700" height="360" style="background:#FFFFFF;">
  <defs>
    <style>
      text, tspan { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
    </style>
    <filter id="shadow-matrix" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- 象限 1：左上 (天际蓝) -->
  <g transform="translate(16, 18)">
    <rect width="324" height="152" rx="8" ry="8" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.5" filter="url(#shadow-matrix)"/>
    <text x="162" y="29" font-size="15.5" font-weight="bold" fill="#0369A1" text-anchor="middle">1. 第一象限标题</text>
    <line x1="14" y1="41" x2="310" y2="41" stroke="#BAE6FD" stroke-width="1"/>
    <text x="15" y="70" font-size="13.5" fill="#082F49">
      <tspan x="15" dy="0"><tspan font-weight="bold" fill="#0284C7">• 核心定位</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#0284C7">• 关键特征</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#0284C7">• 典型示例</tspan> | 简明描述十二到十五字以内</tspan>
    </text>
  </g>

  <!-- 象限 2：右上 (翡翠绿) -->
  <g transform="translate(360, 18)">
    <rect width="324" height="152" rx="8" ry="8" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" filter="url(#shadow-matrix)"/>
    <text x="162" y="29" font-size="15.5" font-weight="bold" fill="#047857" text-anchor="middle">2. 第二象限标题</text>
    <line x1="14" y1="41" x2="310" y2="41" stroke="#A7F3D0" stroke-width="1"/>
    <text x="15" y="70" font-size="13.5" fill="#064E3B">
      <tspan x="15" dy="0"><tspan font-weight="bold" fill="#059669">• 核心定位</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#059669">• 关键特征</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#059669">• 典型示例</tspan> | 简明描述十二到十五字以内</tspan>
    </text>
  </g>

  <!-- 象限 3：左下 (琥珀金) -->
  <g transform="translate(16, 190)">
    <rect width="324" height="152" rx="8" ry="8" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1.5" filter="url(#shadow-matrix)"/>
    <text x="162" y="29" font-size="15.5" font-weight="bold" fill="#B45309" text-anchor="middle">3. 第三象限标题</text>
    <line x1="14" y1="41" x2="310" y2="41" stroke="#FDE68A" stroke-width="1"/>
    <text x="15" y="70" font-size="13.5" fill="#78350F">
      <tspan x="15" dy="0"><tspan font-weight="bold" fill="#D97706">• 核心定位</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#D97706">• 关键特征</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#D97706">• 典型示例</tspan> | 简明描述十二到十五字以内</tspan>
    </text>
  </g>

  <!-- 象限 4：右下 (皇家紫) -->
  <g transform="translate(360, 190)">
    <rect width="324" height="152" rx="8" ry="8" fill="#FAF5FF" stroke="#A855F7" stroke-width="1.5" filter="url(#shadow-matrix)"/>
    <text x="162" y="29" font-size="15.5" font-weight="bold" fill="#7E22CE" text-anchor="middle">4. 第四象限标题</text>
    <line x1="14" y1="41" x2="310" y2="41" stroke="#E9D5FF" stroke-width="1"/>
    <text x="15" y="70" font-size="13.5" fill="#3B0764">
      <tspan x="15" dy="0"><tspan font-weight="bold" fill="#9333EA">• 核心定位</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#9333EA">• 关键特征</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="29"><tspan font-weight="bold" fill="#9333EA">• 典型示例</tspan> | 简明描述十二到十五字以内</tspan>
    </text>
  </g>
</svg>
```

---

## 母版三：纵向条件分支 / 路由流程图 (`branch`)

- **画布尺寸**：`viewBox="0 0 740 310" width="740" height="310"`

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 310" width="740" height="310" style="background:#FFFFFF;">
  <defs>
    <style>
      text, tspan { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
    </style>
    <filter id="shadow-branch" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.06"/>
    </filter>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#10B981"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#EF4444"/>
    </marker>
    <marker id="arrow-slate" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#475569"/>
    </marker>
  </defs>

  <!-- 顶部标题提示栏 -->
  <rect x="16" y="12" width="708" height="34" rx="6" ry="6" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1"/>
  <text x="370" y="34" font-size="14" font-weight="bold" fill="#1E293B" text-anchor="middle">多路分支判定铁律：自顶向下逐条排查 ──▶ 任意分支命中 (True) 执行后立即短路跳出</text>

  <!-- 第 1 级判定 -->
  <rect x="20" y="64" width="230" height="44" rx="8" ry="8" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="135" y="91" font-size="14" font-weight="bold" fill="#0369A1" text-anchor="middle">1. 条件判定一 (if)</text>
  <text x="285" y="80" font-size="12" font-weight="bold" fill="#059669" text-anchor="middle">True (命中)</text>
  <line x1="250" y1="86" x2="322" y2="86" stroke="#10B981" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="328" y="64" width="250" height="44" rx="8" ry="8" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="453" y="91" font-size="13.5" font-weight="bold" fill="#065F46" text-anchor="middle">执行分支一核心动作</text>
  <line x1="135" y1="108" x2="135" y2="128" stroke="#EF4444" stroke-width="1.8" marker-end="url(#arrow-red)"/>
  <text x="172" y="123" font-size="12" font-weight="bold" fill="#DC2626">False</text>

  <!-- 第 2 级判定 -->
  <rect x="20" y="132" width="230" height="44" rx="8" ry="8" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="135" y="159" font-size="14" font-weight="bold" fill="#0369A1" text-anchor="middle">2. 条件判定二 (elif)</text>
  <text x="285" y="148" font-size="12" font-weight="bold" fill="#059669" text-anchor="middle">True (命中)</text>
  <line x1="250" y1="154" x2="322" y2="154" stroke="#10B981" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="328" y="132" width="250" height="44" rx="8" ry="8" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="453" y="159" font-size="13.5" font-weight="bold" fill="#065F46" text-anchor="middle">执行分支二核心动作</text>
  <line x1="135" y1="176" x2="135" y2="196" stroke="#EF4444" stroke-width="1.8" marker-end="url(#arrow-red)"/>
  <text x="172" y="191" font-size="12" font-weight="bold" fill="#DC2626">False</text>

  <!-- 第 3 级判定 -->
  <rect x="20" y="200" width="230" height="44" rx="8" ry="8" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="135" y="227" font-size="14" font-weight="bold" fill="#0369A1" text-anchor="middle">3. 条件判定三 (elif)</text>
  <text x="285" y="216" font-size="12" font-weight="bold" fill="#059669" text-anchor="middle">True (命中)</text>
  <line x1="250" y1="222" x2="322" y2="222" stroke="#10B981" stroke-width="2" marker-end="url(#arrow-green)"/>
  <rect x="328" y="200" width="250" height="44" rx="8" ry="8" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="453" y="227" font-size="13.5" font-weight="bold" fill="#065F46" text-anchor="middle">执行分支三核心动作</text>

  <!-- 兜底 else -->
  <line x1="135" y1="244" x2="135" y2="277" stroke="#EF4444" stroke-width="1.8"/>
  <line x1="135" y1="277" x2="322" y2="277" stroke="#EF4444" stroke-width="1.8" marker-end="url(#arrow-red)"/>
  <text x="228" y="270" font-size="12" font-weight="bold" fill="#DC2626" text-anchor="middle">4. else: (全未命中兜底)</text>
  <rect x="328" y="255" width="250" height="42" rx="8" ry="8" fill="#FFFBEB" stroke="#F59E0B" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="453" y="281" font-size="13.5" font-weight="bold" fill="#B45309" text-anchor="middle">兜底拦截与默认友好提示</text>

  <!-- 右侧汇总跳出总线 -->
  <line x1="578" y1="86" x2="625" y2="86" stroke="#475569" stroke-width="1.8"/>
  <line x1="578" y1="154" x2="625" y2="154" stroke="#475569" stroke-width="1.8"/>
  <line x1="578" y1="222" x2="625" y2="222" stroke="#475569" stroke-width="1.8"/>
  <line x1="578" y1="276" x2="625" y2="276" stroke="#475569" stroke-width="1.8"/>
  <line x1="625" y1="86" x2="625" y2="276" stroke="#475569" stroke-width="2"/>
  <line x1="625" y1="181" x2="648" y2="181" stroke="#475569" stroke-width="2" marker-end="url(#arrow-slate)"/>

  <!-- 跳出节点 -->
  <rect x="652" y="136" width="72" height="90" rx="8" ry="8" fill="#F1F5F9" stroke="#475569" stroke-width="1.5" filter="url(#shadow-branch)"/>
  <text x="688" y="168" font-size="13.5" font-weight="bold" fill="#1E293B" text-anchor="middle">一击</text>
  <text x="688" y="188" font-size="13.5" font-weight="bold" fill="#1E293B" text-anchor="middle">即走</text>
  <text x="688" y="210" font-size="11.5" fill="#475569" text-anchor="middle">跳出分支</text>
</svg>
```

---

## 母版四：左右二元正反 / 演进对比图 (`contrast`)

- **画布尺寸**：`viewBox="0 0 740 216" width="740" height="216"`
- **卡片网格坐标**：左侧反例/旧方案 `(16, 20)`，右侧正例/新方案 `(404, 20)`，卡片尺寸 `width="320" height="176" rx="8"`。

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 216" width="740" height="216" style="background:#FFFFFF;">
  <defs>
    <style>
      text, tspan { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
    </style>
    <filter id="shadow-contrast" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.06"/>
    </filter>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <polygon points="0,2 7,5 0,8" fill="#10B981"/>
    </marker>
  </defs>

  <!-- 左侧：传统痛点 / 反例模式 (玫瑰红) -->
  <g transform="translate(16, 20)">
    <rect width="320" height="176" rx="8" ry="8" fill="#FEF2F2" stroke="#EF4444" stroke-width="1.5" filter="url(#shadow-contrast)"/>
    <text x="160" y="29" font-size="15.5" font-weight="bold" fill="#B91C1C" text-anchor="middle">传统痛点 / 脆弱反例模式</text>
    <line x1="14" y1="41" x2="306" y2="41" stroke="#FECACA" stroke-width="1"/>
    <text x="15" y="68" font-size="13.5" fill="#7F1D1D">
      <tspan x="15" dy="0"><tspan font-weight="bold" fill="#DC2626">• 结构缺陷</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="28"><tspan font-weight="bold" fill="#DC2626">• 维护代价</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="28"><tspan font-weight="bold" fill="#DC2626">• 典型症状</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="28"><tspan font-weight="bold" fill="#DC2626">• 风险后果</tspan> | 简明描述十二到十五字以内</tspan>
    </text>
  </g>

  <!-- 中间演进箭头 -->
  <text x="370" y="92" font-size="12" font-weight="bold" fill="#047857" text-anchor="middle">架构升级</text>
  <line x1="342" y1="108" x2="396" y2="108" stroke="#10B981" stroke-width="2.2" marker-end="url(#arrow-green)"/>
  <text x="370" y="128" font-size="12" fill="#64748B" text-anchor="middle">解耦重构</text>

  <!-- 右侧：工程最佳实践 / 正例模式 (翡翠绿) -->
  <g transform="translate(404, 20)">
    <rect width="320" height="176" rx="8" ry="8" fill="#ECFDF5" stroke="#10B981" stroke-width="1.5" filter="url(#shadow-contrast)"/>
    <text x="160" y="29" font-size="15.5" font-weight="bold" fill="#047857" text-anchor="middle">工程正例 / 推荐架构设计</text>
    <line x1="14" y1="41" x2="306" y2="41" stroke="#A7F3D0" stroke-width="1"/>
    <text x="15" y="68" font-size="13.5" fill="#064E3B">
      <tspan x="15" dy="0"><tspan font-weight="bold" fill="#059669">• 结构优势</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="28"><tspan font-weight="bold" fill="#059669">• 扩展能力</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="28"><tspan font-weight="bold" fill="#059669">• 核心机制</tspan> | 简明描述十二到十五字以内</tspan>
      <tspan x="15" dy="28"><tspan font-weight="bold" fill="#059669">• 工程收益</tspan> | 简明描述十二到十五字以内</tspan>
    </text>
  </g>
</svg>
```
