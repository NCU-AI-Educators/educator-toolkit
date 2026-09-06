# AI 教育者 Agent 技能集 (Educator Toolkit Skills)

欢迎来到 **Educator Toolkit Skills**！这里汇集了专为 AI Coding Agent（如 Google Antigravity、Claude Code、Cursor、Windsurf 等）定制的专业级自动化技能包。

通过引入标准化的 Agent 技能，AI 助手不再只是通用的文本生成器，而是具备**符合教育学规范、出版级排版精度和工程制图水准**的专业助教。

---

## 🧭 技能清单 (Skills Catalog)

| 技能名称 | 目录 | 核心定位 | 关键能力 |
| :--- | :--- | :--- | :--- |
| **Archify** | [`skills/archify/`](./archify/) | 架构与工程可视化引擎 | <ul><li>支持架构图、时序图、数据流图、状态机等 5 大图表族</li><li>双轨模式：浏览器富交互探索 + 出版级纯净矢量（Clean SVG）导出</li><li>自动字号优化、半透明同色系徽章、无交互外壳残留</li></ul> |
| **Typst** | [`skills/typst/`](./typst/) | 单一事实源 (SSOT) 出版级编译器 | <ul><li>A4 双面印刷排版（对称书脊装订边距、奇偶动态页眉）</li><li>科技论文三线表排版引擎</li><li>LaTeX 数学公式与变量双引号保护</li><li>集成 4090 Kroki 算力与原生矢量图嵌入</li></ul> |

---

## ⚡ 核心联动工作流：出版级学术材料生产线

`Archify` 与 `Typst` 构成了强大的学术级出版生产流水线，彻底打破了“画图模糊、排版错位、格式割裂”的长期痛点：

```
                      [课程教案 / 软件需求 / 架构方案 SSOT Markdown]
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         [调用 Archify 技能]                              [编写方案与数学公式]
                    │                                               │
         生成交互式工程图表                                规范化 Markdown 文本
                    │                                               │
         [执行 export-clean-svg]                                    │
                    │                                               │
         导出出版级纯净 SVG (无外壳、字号加权、清晰可读)                  │
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            ▼
                                   [调用 Typst 技能]
                                            │
                             ┌──────────────┴──────────────┐
                             │ • 解析 SSOT Markdown        │
                             │ • 嵌入 Archify 纯净矢量图   │
                             │ • 生成规范科技三线表        │
                             │ • 编译 A4 双面印刷排版      │
                             └──────────────┬──────────────┘
                                            ▼
                               [学术出版级矢量 PDF 成果物]
```

---

## 🛠️ 如何在您的 AI Agent 中使用

### 1. Google Antigravity / Gemini CLI
将技能目录克隆或软链接至 Agent 技能根目录：
- **全局生效**：放入 `~/.gemini/config/skills/`
- **项目级生效**：放入项目根目录下的 `.agents/skills/`

例如：
```bash
# 在您的项目工程根目录下
mkdir -p .agents/skills
cp -r path/to/educator-toolkit/skills/* .agents/skills/
```

### 2. Cursor / Windsurf / Claude Code
将对应的 `SKILL.md` 内容作为 System Instructions 或 Custom Rules 引入，或者通过项目提示词规则文件（如 `.cursorrules`、`CLAUDE.md`）显式引用该目录下的执行脚本：
```markdown
When generating architecture diagrams or exporting figures for documents, reference `skills/archify/SKILL.md`.
When compiling SSOT Markdown into publication-grade documents, use `python3 skills/typst/scripts/ssot_to_typst.py`.
```

---

## 🤝 贡献与反馈

欢迎各位教育同行与开发者提交新的 Agent 技能或改进现有技能！
如遇问题或建议，欢迎在 GitHub 仓库提交 Issue 或 Pull Request。
