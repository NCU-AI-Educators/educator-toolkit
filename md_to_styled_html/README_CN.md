# Markdown to Styled HTML

**md_to_styled_html** 是一个轻量级转换工具，旨在将 Markdown 文件转换为**独立、美观且具有高阅读体验**的 HTML 页面。它专注于提供舒适的排版和沉浸式的阅读环境，并支持 GitHub Alerts 和 Ruby 拼音标注等高级特性。

## 📂 功能特性

*   **完全独立**：生成包含所有 CSS 和脚本的单个 `.html` 文件。无需服务器即可直接打开，方便分发。
*   **极致阅读体验**：精心调优的排版样式，提供清晰、专注且舒适的阅读感受。
*   **沉浸式自动滚动**：支持空格键开启提词器/自动滚动模式，适合长文阅读或演讲提示。
*   **高级 Markdown 支持**：
    *   GitHub 警示框 (Alerts)：支持 `[!NOTE]`, `[!TIP]`, `[!WARNING]` 等语法。
    *   Ruby 拼音标注：`[汉]{py}` -> `<ruby>汉<rt>py</rt></ruby>`。

## 🚀 快速上手

### 1. 生成阅读页面

使用该目录下的 Python 脚本进行转换：

```bash
# 基本用法 (使用默认样式 default.css)
python generate_reader.py /path/to/your/article.md

# 指定输出路径
python generate_reader.py /path/to/article.md -o /path/to/site/article.html

# 使用自定义 CSS 样式
python generate_reader.py /path/to/article.md /path/to/custom_style.css
```

### 2. 集成到网页中

生成的 HTML 是自包含的。若要将其集成到其他网页（如课程平台或博客）且不产生样式冲突，建议使用 `<iframe>`。

**示例代码：**

```html
<!-- 使用 IFrame 进行集成 -->
<div class="reader-wrapper" style="width: 100%; max-width: 500px; margin: 0 auto; height: 80vh; border: 1px solid #ddd; border-radius: 20px; overflow: hidden;">
    <iframe 
        src="./path/to/generated_article.html" 
        style="width: 100%; height: 100%; border: none;"
        title="Reader View"
    ></iframe>
</div>
```

## 🛠 文件结构

*   `generate_reader.py`: 核心转换脚本。
*   `template.html`: HTML 模板骨架。
*   `default.css`: 内置样式文件（提供高阅读体验的默认样式）。
