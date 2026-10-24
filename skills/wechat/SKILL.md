---
name: wechat
description: "【微信公众号富文本排版编译器】将标准 Markdown、工程单一事实源 (SSOT) 讲义或深度研究报告一键编译为微信公众号移动端 (677px) 高审美内联样式 HTML (*.mp.html 交互预览页与 *.fragment.html 纯富文本片段)。内置 YAML Frontmatter 杂志级导读卡片、防换行崩溃的 AST 悬挂缩进列表、GitHub 风格三线表、科技蓝/学术绿多主题色定制及外链转尾注机制，支持在浏览器中一键复制并直接粘贴至微信公众号后台 (mp.weixin.qq.com)。"
metadata:
  version: "1.0.0"
  author: NCU-AI-Educators
---

# 微信公众号富文本排版编译器 (WeChat MP Compiler)

本技能负责将输入的 Markdown 文档（`*.md` / `*.ssot.md`）一键编译为适配微信公众号后台（ProseMirror 编辑器）的高审美移动端内联样式 HTML。

## 1. 核心路径与跨工作区调用规范

- **技能包装脚本路径**：`~/.gemini/config/skills/wechat/scripts/compile_to_wechat.py`
- **底层 TypeScript 编译引擎目录**：`/Users/l.ylive.cn/OneDrive/NCU-AI-Educators/smart-course-platform/md2slide/tools/wechat_compiler`

### 推荐执行指令（任意工作目录通用）
```bash
# 基础编译（默认科技蓝 #0284c7，字号 15.5px，段首缩进 2em）
python3 /Users/l.ylive.cn/.gemini/config/skills/wechat/scripts/compile_to_wechat.py -i "<input.md>"

# 自定义输出路径、主题强调色、字号与段首缩进
python3 /Users/l.ylive.cn/.gemini/config/skills/wechat/scripts/compile_to_wechat.py \
  -i "<input.md>" \
  -o "<output.mp.html>" \
  -p "#047857" \
  -f "16px" \
  -t "2em"
```

## 2. 命令行参数详解

| 参数 | 缩写 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | **必填** | 输入的 Markdown 文件路径（`.md` / `.ssot.md`） |
| `--output` | `-o` | `<input>.mp.html` | 输出的交互预览 HTML 文件路径 |
| `--primary` | `-p` | `#0284c7`（科技蓝） | 文章主题强调色（如学术墨绿 `#047857`、深邃紫 `#7c3aed`） |
| `--font-size` | `-f` | `15.5px` | 正文字号大小（如 `15px`, `15.5px`, `16px`） |
| `--indent` | `-t` | `2em` | 正文段落首行缩进（如 `2em` 或 `0`） |
| `--css` | `-c` | 无 | 自定义外部 CSS 样式表路径 |

## 3. 编译产物与微信公众号后台发布流程

编译完成后将在目标目录同步生成两个文件：
1. **`<name>.mp.html`（交互式预览页）**：
   - 采用与微信公众号移动端一致的 **677px** 居中视口容器；
   - 顶部内置控制栏与 **“一键复制为微信富文本”** 按钮。
2. **`<name>.fragment.html`（纯富文本 HTML 片段）**：
   - 仅含全内联样式的正文 HTML 节点，供自动化发布脚本或第三方插件直接注入。

### 公众号后台粘贴步骤
1. 在 Chrome / Edge / Safari 浏览器中打开生成的 `*.mp.html`；
2. 点击页面右上角 **“一键复制为微信富文本”**；
3. 打开微信公众号后台图文编辑器（`https://mp.weixin.qq.com`），按 `Cmd + V`（macOS）或 `Ctrl + V`（Windows）直接粘贴。

## 4. 核心排版特性
- **全属性 100% 内联化（Inline CSS）**：所有字号、行高、颜色、边框与边距全部内联至 HTML 标签 `style` 属性，跨软件复制粘贴零样式丢失。
- **AST 列表重构（防粗体断行）**：将原生 `<ul>/<ol>/<li>` 重构为微信原生 `<section>` 与 `<p style="padding-left: 1.5em; text-indent: -1.5em;">` 悬挂缩进段落，彻底解决微信公众号编辑器将 `<li>` 内粗体强行换行的顽疾。
- **Frontmatter 智能导读卡**：若文档头部包含 `title`、`subtitle`、`author`、`abstract` 等 YAML Frontmatter，自动渲染杂志级页头与“📌【内容导读与核心摘要】”圆角卡片。
- **外链自动转文末尾注**：自动将正文中的外部链接提取为右上角上标 `[N]`，并在文末汇总生成“参考资料与延伸阅读”列表。
