# Markdown to Reader Converter

**md_to_reader** is a lightweight tool to convert Markdown files into standalone, beautiful, and high-quality HTML reading pages. It focuses on providing comfortable typography and an immersive reading environment, supporting advanced features like GitHub Alerts and Ruby Pinyin.

## 📂 Features

*   **Standalone**: Generates a single `.html` file containing all CSS and Scripts. No server required.
*   **Excellent Reading Experience**: Carefully tuned typography for a clear and comfortable reading experience.
*   **Spacebar Auto-Scroll**: Teleprompter mode for immersive reading or presentations.
*   **Advanced Markdown**: 
    *   GitHub Alerts: `[!NOTE]`, `[!TIP]`, `[!WARNING]`
    *   Ruby Pinyin: `[汉]{py}` -> `<ruby>汉<rt>py</rt></ruby>`

## 🚀 Quick Start

### 1. Generate Reader

Run the python script provided in this directory:

```bash
# Basic usage (Uses default.css)
python generate_reader.py /path/to/your/article.md

# Specify Output path
python generate_reader.py /path/to/article.md -o /path/to/site/article.html

# Use Custom CSS
python generate_reader.py /path/to/article.md /path/to/custom_style.css
```

### 2. Integrate into Webpages

The generated HTML is self-contained. To integrate it into another webpage (like a course platform or blog) without style conflicts, use an `<iframe>`.

**Example Code:**

```html
<!-- Integration using IFrame -->
<div class="reader-wrapper" style="width: 100%; max-width: 500px; margin: 0 auto; height: 80vh; border: 1px solid #ddd; border-radius: 20px; overflow: hidden;">
    <iframe 
        src="./path/to/generated_article.html" 
        style="width: 100%; height: 100%; border: none;"
        title="Reader View"
    ></iframe>
</div>
```

## 🛠 File Structure

*   `generate_reader.py`: The generator script.
*   `template.html`: The HTML skeleton.
*   `default.css`: The built-in style (High-quality reading style).
