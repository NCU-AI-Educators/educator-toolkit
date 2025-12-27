# Gemini Watermark Remover 工具使用指南

这是一个用于去除 Google Gemini 生成图片水印的 Python 工具。它基于逆向工程原理，通过计算 Alpha 通道还原原始像素，能够高效、无损地去除水印。

## 1. 快速开始

### 依赖安装

在使用前，请确保您的系统已安装 Python 3，并安装了必要的依赖库：

```bash
pip install Pillow numpy
```

### 命令行使用

该脚本可以通过命令行直接调用：

```bash
# 基本用法 (输出文件将自动命名为 <原文件名>_clean.<扩展名>)
python3 Tools/watermark_remover.py path/to/image.png

# 指定输出路径
python3 Tools/watermark_remover.py path/to/image.png path/to/output.png
```

## 2. 集成到 macOS 右键菜单 (快速操作)

为了方便日常使用，您可以利用 macOS 的 **Automator (自动操作)** 将此脚本添加到 Finder 的右键菜单中。

### 步骤指南

1.  **打开 Automator**:
    *   在 Spotlight (聚焦搜索) 中输入 "Automator" 并打开。
    *   点击 "新建文稿" (New Document)。

2.  **选择类型**:
    *   选择 **"快速操作" (Quick Action)**，点击 "选取"。

3.  **配置工作流程**:
    *   在顶部设置栏中：
        *   **工作流程收到当前 (Workflow receives current)**: 选择 **"文件或文件夹" (Files or Folders)**。
        *   **位于 (in)**: 选择 **"访达" (Finder)**。
        *   *(可选) 您可以自定义图标。*

4.  **添加 Shell 脚本**:
    *   在左侧侧边栏的搜索框中输入 "Shell"。
    *   双击或拖拽 **"运行 Shell 脚本" (Run Shell Script)** 到右侧工作区。

5.  **配置脚本参数**:
    *   **Shell**: 选择 `/bin/bash` 或 `/bin/zsh` (默认即可)。
    *   **传递输入 (Pass input)**: **务必选择 "作为自变量" (As arguments)**。*(这一点非常重要，否则脚本无法接收文件路径)*

6.  **编写脚本代码**:
    *   将编辑器中的默认代码替换为以下内容 (请根据您的实际环境修改路径)：

    ```bash
    # 1. 设置 Python 解释器路径
    # 如果您使用系统 Python，通常是 /usr/bin/python3
    # 如果您使用 Homebrew 安装的，通常是 /opt/homebrew/bin/python3
    # 建议在终端输入 `which python3` 确认您的路径
    PYTHON_EXEC="/opt/homebrew/bin/python3" 

    # 2. 设置脚本的绝对路径
    # 请将下面的路径修改为您实际存放 watermark_remover.py 的完整路径
    SCRIPT_PATH="/Users/l.ylive.cn/Library/CloudStorage/OneDrive-个人/Course_SoftwareEngineering/Tools/watermark_remover.py"

    # 3. 执行循环
    for f in "$@"
    do
        "$PYTHON_EXEC" "$SCRIPT_PATH" "$f"
    done
    ```

7.  **保存服务**:
    *   按 `Cmd + S` 保存。
    *   命名为 **"去除 Gemini 水印"** (Remove Gemini Watermark)。

### 如何使用

1.  在 Finder 中找到一张或多张带有 Gemini 水印的图片。
2.  **右键点击** 图片。
3.  在菜单中选择 **"快速操作" (Quick Actions)** -> **"去除 Gemini 水印"**。
4.  脚本将在后台运行，处理后的图片会自动保存在原图片同一目录下，文件名带有 `_clean` 后缀。

## 3. 故障排除

如果右键菜单点击后没有反应，可以尝试以下调试方法：

1.  **检查 Python 路径**: 确保 Automator 脚本中的 `PYTHON_EXEC` 指向了正确的、已安装 `numpy` 和 `Pillow` 的 Python 环境。
2.  **检查脚本路径**: 确保 `SCRIPT_PATH` 准确无误，且路径中没有特殊的转义字符问题。
3.  **查看日志**: 您可以在 Automator 脚本中添加日志输出，将 `stdout` 和 `stderr` 重定向到 `/tmp/log.txt` 来排查错误。
