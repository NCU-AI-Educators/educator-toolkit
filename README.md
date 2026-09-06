# AI 赋能教育者工具箱 (Educator Toolkit)

![License](https://img.shields.io/badge/license-AGPL%20v3-blue.svg)

## 项目简介
**Educator Toolkit** 是为 "AI 赋能软件开发" 课程配套的教学工具集。它包含了一系列开箱即用的 Prompt 模板、自动化脚本和 Workflow，旨在赋能教师高效备课、科研与教学。

## 资源目录
*   **🧩 VS Code Extensions**:
    *   **[Hawk's Styled Markdown Preview](https://marketplace.visualstudio.com/items?itemName=hawklee.md-styled-html-preview)**: 🦅 专为教育者设计的 Markdown 预览插件。支持学术风格排版、MathJax 公式、拼音标注、GitHub 风格提示块以及**提词器模式**。支持一键导出为独立的 HTML 文件。
        [![Version](https://img.shields.io/visual-studio-marketplace/v/hawklee.md-styled-html-preview?style=flat-square&label=VS%20Code%20Marketplace)](https://marketplace.visualstudio.com/items?itemName=hawklee.md-styled-html-preview)
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
    *   `md_to_styled_html`: [Markdown 阅读体验优化工具](./md_to_styled_html/README_CN.md) (生成排版精美、支持自动滚动的独立 HTML)
*   **🧠 Skills**: 专为 AI Coding Agent (Antigravity / Claude Code / Cursor 等) 打造的专业技能包。[查看总览说明](./skills/README.md)
    *   **[archify](./skills/archify/README.md)**: 现代系统架构、时序交互与工程图表可视化引擎。支持高维富交互 Web 探索与出版级纯净矢量（Clean SVG）导出。
    *   **[typst](./skills/typst/README.md)**: 基于单一事实源 (SSOT) 哲学的学术教材与工业出版级 Typst/PDF 编译器。支持 A4 双面印刷装订排版、科技三线表与 Kroki 算力集成。

## 贡献指南
欢迎各位老师提交 Pull Request 分享您的教学工具！

## 关注与交流
欢迎关注南昌大学 AI 创新应用实验室（AIIA Lab@NCU）官方公众号，获取最新 AI 教学实践、工具链更新与前沿动态：

<p align="center">
  <img src="assets/wechat_promo_card.png" alt="南昌大学 AIIA Lab 官方公众号" width="460">
</p>

## 协议
本项目代码脚本采用 **AGPL v3** 协议。
Prompt 文本与文档内容遵循 **CC BY-NC-SA 4.0** 协议。
