# AI 赋能教育者工具箱 (Educator Toolkit)

![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)

## 项目简介
**Educator Toolkit** 是为 "AI 赋能软件开发" 课程配套的教学工具集。它包含了一系列开箱即用的 Prompt 模板、自动化脚本和 Workflow，旨在赋能教师高效备课、科研与教学。

## 资源目录
*   **🤖 Prompts**: 精选的系统级提示词库 (System Prompts)。
    *   `role-act-as-reviewer`: 模拟严厉的审稿人
    *   `role-socratic-tutor`: 苏格拉底式提问教学助手
*   **⛓️ Workflows**: ComfyUI 与 Dify 的工作流文件 (.json, .yml)。
    *   `text-to-poster`: 一键生成课程海报
    *   `summary-generator`: 课堂录音自动总结摘要
*   **🛠️ Scripts**: Python 效率脚本。
    *   `ppt-to-markdown`: 批量转换课件格式
    *   `canvas-migration`: 其它平台数据迁移工具
    *   `marp_to_multi_formats`: [一键生成备课资源](./marp_to_multi_formats/README.md) (讲义、逐字稿、教案)
    *   `NBP_watermark_remover`: [牛必配水印去除工具](./NBP_watermark_remover/README_Watermark_Remover.md)
    *   `md_to_reader`: [Markdown 阅读体验优化工具](./md_to_reader/README_CN.md) (生成排版精美、支持自动滚动的独立 HTML)

## 贡献指南
欢迎各位老师提交 Pull Request 分享您的教学工具！

## 协议
本项目代码脚本采用 **AGPL v3** 协议。
Prompt 文本与文档内容遵循 **CC BY-NC-SA 4.0** 协议。
