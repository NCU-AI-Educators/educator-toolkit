---
name: markdown-cjk-spacer
description: >-
  Search for inline Markdown formatting spans (such as bold **“...”**, **...**, `code`, *italic*, ~~strike~~) that are
  directly adjacent to Chinese characters on both sides, and format them by adding whitespace padding before and after.
  Trigger when the user asks in natural language to find and add spaces around Markdown format strings surrounded
  by Chinese characters, pad CJK markdown bold spacing, or format adjacent Chinese-Markdown formatting spans
  (e.g., "查找类似**“急用先行”**前后都有中文字符的格式串并加上空格", "中文字符加粗前后加空格", "格式化Markdown加粗与行内代码间距",
  "为所有Markdown中紧贴中文的加粗和代码块补空格").
---

# Markdown CJK Formatting Spacer (中文字符与行内格式串空格补全技能)

用于自动化扫描工作区内所有或指定的 Markdown 文件，精准定位所有**前后紧贴中文字符的行内格式串**（如 `**“...”**`、`**...**`、`` `...` `` 等），并在格式串前后分别补上对称空格，优化排版视觉体验，解决因格式标记粘连中文导致的解析器渲染异常。

---

## 1. 触发场景与自然语言指令 (When to Trigger)

当用户在对话中提出以下类似请求时，智能体应立即加载并执行本技能：
* **针对特定样式的空格补全**：“查找类似 `**“急用先行、敏捷迭代”**` 前后都有中文字符的格式串，前后加上空格分割”、“给所有前后紧挨着中文的加粗词组两边加上空格”。
* **全局排版规范化**：“格式化项目中所有 Markdown 里的加粗和代码块间距”、“为所有文档的中英混排和加粗做盘古之白空格处理”。
* **单文件精准处理**：“把当前文件里粘连在中文里的 `**加粗**` 前后都加上空格”。

---

## 2. 自动化执行工作流 (Workflow Steps)

### 步骤 1：明确目标范围与操作模式
1. **范围确定**：
   * 若用户指定了特定文件或目录（如 `@docs/方案.md`），将该路径作为输入目标；
   * 若用户要求“在所有 Markdown 中查找”或未指定路径，默认以当前工作区根目录（`.`）为目标，递归扫描所有 `.md` 文件。
2. **模式推断**：
   * **预览/检查模式**：用户询问“有哪些地方没加空格”、“先查一下”，运行不带 `-i` 的默认预览检查；
   * **就地保存模式**：用户要求“加上空格”、“修改”、“替换”、“格式化”，带上 `-i`（或 `--inplace`）参数直接写盘保存。

### 步骤 2：执行底层清洗引擎
根据当前环境（全局调用或当前工作区本地调用）执行随技能打包的高精度 Token 脚本：

```bash
# 通用跨工作区全局执行方式（推荐，适用于任意项目与工作目录）：
python3 ~/.gemini/config/skills/markdown-cjk-spacer/scripts/spacer.py [目标路径]

# 若当前工作区根目录下已包含本地副本，亦可直接调用：
python3 .agents/skills/markdown-cjk-spacer/scripts/spacer.py [目标路径]

# 常用操作范例（以全局路径为例）：
# 1. 预览检查模式（不修改文件，输出统计与行号明细）
python3 ~/.gemini/config/skills/markdown-cjk-spacer/scripts/spacer.py [目标路径]

# 2. 针对指定文件直接执行就地修改
python3 ~/.gemini/config/skills/markdown-cjk-spacer/scripts/spacer.py path/to/document.md -i

# 3. 针对全项目所有 Markdown 批量就地修复
python3 ~/.gemini/config/skills/markdown-cjk-spacer/scripts/spacer.py . -i
```

### 步骤 3：解析结果并向用户反馈
脚本会输出清晰的处理清单与统计指标：
* 命中的文件列表与每个文件的修改处数；
* 具体修改示例（展示行号、修改前与修改后文本对比）；
* 最终执行汇总（共处理几个文件、补全几处空格）。

---

## 3. 核心匹配规则与边界防护机制

| 匹配模式 | 原文示例 | 自动补全后效果 |
| :--- | :--- | :--- |
| **加粗内嵌引号** | `采取**“急用先行”**的策略` | `采取 **“急用先行”** 的策略` |
| **标准加粗** | `出**多源异构**的特征` | `出 **多源异构** 的特征` |
| **行内代码** | `使用`readsb`进行解调` | `使用 `readsb` 进行解调` |
| **引号外嵌加粗** | `向“**自主研判**”的演进` | `向 “**自主研判**” 的演进` |

### 安全与防误伤准则：
1. **围栏代码块完全免疫**：被 ` ``` ` 或 `~~~` 包裹的多行代码块严格保持原状，绝不侵入修改。
2. **数学公式块完全免疫**：被 `$$` 包裹的多行公式块严格原样保留。
3. **彻底杜绝跨加粗倒置误伤**：采用词法 Token 判定机制，对于 `**概述**：本方案立足于**现实**` 这类两个独立加粗段落之间的文字，严格识别其内部标点属性，绝不发生跨段落误拼接。
4. **防重复空格**：如果前后已有空格或标点，则不会多加空格。

---

## 4. 辅助脚本位置 (Helper Script)
* 全局脚本路径：`~/.gemini/config/skills/markdown-cjk-spacer/scripts/spacer.py`
* 技能包内相对路径：`scripts/spacer.py`
