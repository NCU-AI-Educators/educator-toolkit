# Material Generator Script (`generate_materials.py`)

这是一个用于自动化构建课程讲义和演示文稿的 Python 脚本。它能够将一份集成了所有信息的“母版” Markdown 文件 (`*.master.md`) 转换为三种不同用途的衍生文件：

1.  **教师用书 (`.teacher.md`)**: 包含教学设计、讲课提示，采用 A4 版式，适合打印或备课阅读。
2.  **学生讲义 (`.handout.md`)**: 包含详细的知识点解释，去除教学设计内容，采用 A4 版式，适合学生课后复习。
3.  **演示幻灯片 (`.slides.md`)**: 仅包含主要视觉内容和演讲者逐字稿，去除大段文字解释，适合课堂演示 (Marp)。

## 使用方法

### 前置要求
- Python 3.x
- 您的系统不需要安装额外的 pip 包，脚本仅使用 Python 标准库 (`re`, `os`, `sys`, `textwrap`)。

### 运行脚本
在终端中运行以下命令，并传入您的 `master.md` 文件路径：

```bash
python generate_materials.py /path/to/your/module_lesson.master.md
```

**示例**:
```bash
python educator-toolkit/marp_to_multi_formats/generate_materials.py content/module1/module1_lesson1.master.md
```

脚本运行成功后，将在同级目录下生成对应的 `*.teacher.md`, `*.handout.md`, 和 `*.slides.md` 文件。

## 母版文件 (`.master.md`) 编写规范

为了让脚本正确地拆分和处理内容，请在 Markdown 文件中使用特定格式的 HTML 注释来编写元数据。

### 1. 逐字稿 (Speaker Notes)
仅出现在幻灯片版本中，作为演讲者备注。

```markdown
<!--
- **类型**: 逐字稿
- **内容**: 各位同学大家好，今天我们来学习...
-->
```

### 2. 解释 (Explanations)
仅出现在 **学生讲义** 和 **教师用书** 中，会以黄色背景的文本框显示。通常用于对 PPT 上的简练观点进行详细阐述。

```markdown
<!--
- **类型**: 解释
- **内容**: 这里详细解释了为什么 AI 在教育中越来越重要...
-->
```

### 3. 教学设计 (Teaching Design)
仅出现在 **教师用书** 中，会以粉色背景的文本框显示。用于提示讲师如何互动、提问或组织课堂活动。

```markdown
<!--
- **类型**: 教学设计
- **内容**: 提问环节：请邀请三位同学分享他们的看法 (5分钟)。
-->
```

### 4. 样式替换 (Style Replacement)
用于在不同版本中调整文本或布局。例如，PPT 上的一行字太长，在 A4 纸上想换行，或者想在 PPT 上隐藏某些字。

```markdown
<!--
- **类型**: 样式替换
- **版本**: [slides]        <-- 仅在 slides 版本生效，留空则所有版本生效
- **查找**: original text   <-- 要查找的文本
- **替换**: new text        <-- 要替换成的文本
- **次数**: 1               <-- (可选) 替换次数，* 代表全部替换
-->
```

### 5. 条件换页 (Conditional Page Break)
用于在特定版本中强制分页 (插入 `---`)。

```markdown
<!--
- **类型**: 换页
- **版本**: [teacher, handout] <-- 仅在教师书和讲义中分页
-->
```

## 输出文件说明

| 文件后缀 | 用途 | 版式 | 包含内容 |
| :--- | :--- | :--- | :--- |
| `.slides.md` | 课堂演示 | Marp Slide (16:9) | 核心内容 + 逐字稿 (隐藏) |
| `.teacher.md` | 教师备课 | A4 文档 | 核心内容 + **教学设计** + **解释** |
| `.handout.md` | 学生复习 | A4 文档 | 核心内容 + **解释** |

## 自定义样式
脚本内置了一套 CSS 样式用于美化 A4 文档中的“解释”和“教学设计”文本框。如果您需要修改样式（如颜色、边距），请直接编辑 `generate_materials.py` 文件顶部的 `STYLE_BLOCK` 常量。
