# Hawk Styled Preview 功能测试 🦅

这是一个用于测试 **Hawk's Styled Markdown Preview** 插件功能的示例文件。

## 🎨 1. 基础样式 (Basic Styling)

- **加粗测试**：这里是 **加粗文字 (Bold)**，应该显示为主题色（深蓝色）。
- *斜体测试*：这里是 *斜体文字 (Italic)*。
- ~~删除线~~：这里是 ~~删除线 (Strikethrough)~~。

## ⚗️ 2. 数学公式 (Scientific Math)

支持 MathJax 渲染，适合理科教师使用。

- **行内公式 (Inline)**：质能方程 $E = mc^2$。
- **块级公式 (Block)**：
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$

## 🧧 3. 拼音/注音支持 (Pinyin/Ruby)

专为语言教学设计，使用 `[汉字]{pinyin}` 语法。

- **示例**：[中文]{zhong wen} 学习很[有趣]{you qu}。
- **古诗演示**：
  - [床]{chuang} [前]{qian} [明]{ming} [月]{yue} [光]{guang}
  - [疑]{yi} [是]{shi} [地]{di} [上]{shang} [霜]{shuang}

## 📢 4. 提示块 (GitHub-Style Alerts)

使用引用块语法，自动渲染为醒目的提示框。

> [!NOTE]
> **注意**：这是一个普通通知 (Note)，用于提示一般信息。

> [!TIP]
> **技巧**：这是一个小技巧 (Tip)，背景通常是绿色的。

> [!WARNING]
> **警告**：这是一个警告 (Warning)，用于提醒重要风险。

## 💻 5. 代码高亮 (Code Blocks)

```python
def hello_hawk():
    # 这是一个测试函数
    message = "Hello, Hawk's Styled Preview!"
    print(message)
    return True
```

## 📜 6. 自动滚动 (Teleprompter)

在预览窗口中点击一下，然后按 **`空格键`**。
页面应该会自动缓慢向下滚动，再次按 **`空格键`** 停止。

---
感谢使用 **Hawk's Styled Markdown Preview**！
