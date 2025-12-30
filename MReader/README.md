# Hawk MReader Component

**MReader** (Markdown Reader) is a lightweight tool to convert Markdown files into standalone, beautiful HTML readers. It is designed to mimic the "WeChat Official Account" aesthetic and supports advanced features like GitHub Alerts and Ruby Pinyin.

## 📂 Features

*   **Standalone**: Generates a single `.html` file containing all CSS and Scripts. No server required.
*   **WeChat Style**: Built-in default styling that mimics WeChat articles.
*   **Spacebar Auto-Scroll**: Teleprompter mode for immersive reading/presentation.
*   **Advanced Markdown**: 
    *   GitHub Alerts: `[!NOTE]`, `[!TIP]`, `[!WARNING]`
    *   Ruby Pinyin: `[汉]{py}` -> `<ruby>汉<rt>py</rt></ruby>`

## 🚀 Quick Start

### 1. Generate Reader

Run the python script provided in this directory:

```bash
# Basic usage (Uses default.css)
python mreader.py /path/to/your/article.md

# Specify Output path
python mreader.py /path/to/article.md -o /path/to/site/article.html

# Use Custom CSS
python mreader.py /path/to/article.md /path/to/custom_style.css
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
        title="Hawk Reader"
    ></iframe>
</div>
```

## 🛠 File Structure

*   `mreader.py`: The generator script.
*   `template.html`: The HTML skeleton.
*   `default.css`: The built-in style (WeChat aesthetic).
