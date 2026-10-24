#!/usr/bin/env python3
"""
Python 包装驱动：一键将 Markdown 编译为微信公众号移动端高审美长文 HTML
用法:
    python3 compile_to_wechat.py -i <path/to/markdown.md> [--output <path/to/output.html>]
    python3 compile_to_wechat.py <path/to/markdown.md>
"""

import argparse
import os
import subprocess
import sys

CANDIDATE_COMPILER_DIRS = [
    "/Users/l.ylive.cn/OneDrive/NCU-AI-Educators/smart-course-platform/md2slide/tools/wechat_compiler",
    os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "wechat_compiler")),
]


def resolve_compiler_dir() -> str:
    for d in CANDIDATE_COMPILER_DIRS:
        if os.path.exists(os.path.join(d, "compile_mp.ts")):
            return d
    raise FileNotFoundError(
        f"未找到 wechat_compiler 引擎目录，已检查: {CANDIDATE_COMPILER_DIRS}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="一键将 Markdown 讲稿/长文编译为微信公众号移动端高审美富文本 HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
    # 基础编译（支持 -i 或直接传入文件路径）
    python3 compile_to_wechat.py -i ./lecture.ssot.md
    python3 compile_to_wechat.py ./lecture.ssot.md

    # 指定输出文件与主题色
    python3 compile_to_wechat.py -i ./lecture.ssot.md -o ./dist/output.html -p "#047857" -f "16px"
""",
    )
    parser.add_argument("pos_input", nargs="?", default=None, help="输入的 Markdown 文件路径 (.md / .ssot.md)")
    parser.add_argument("--input", "-i", default=None, help="输入的 Markdown 文件路径 (.md / .ssot.md)")
    parser.add_argument("--output", "-o", default=None, help="输出的 HTML 预览文件路径 (默认: <input>.mp.html)")
    parser.add_argument("--css", "-c", default=None, help="自定义主题 CSS 样式文件路径")
    parser.add_argument("--primary", "-p", default=None, help="快速指定主题强调色 (如 #0284c7, #047857)")
    parser.add_argument("--font-size", "-f", default=None, help="正文字号大小 (如 15px, 15.5px, 16px)")
    parser.add_argument("--indent", "-t", default=None, help="段落首行缩进大小 (如 2em, 0，默认 2em)")

    args = parser.parse_args()
    raw_input = args.input or args.pos_input
    if not raw_input:
        parser.error("必须提供输入的 Markdown 文件路径（使用 -i <file.md> 或直接传入 <file.md>）")

    input_path = os.path.abspath(raw_input)
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    compiler_dir = resolve_compiler_dir()
    cmd = ["pnpm", "exec", "tsx", "compile_mp.ts", "--input", input_path]
    if args.output:
        cmd.extend(["--output", os.path.abspath(args.output)])
    if args.css:
        cmd.extend(["--css", os.path.abspath(args.css)])
    if args.primary:
        cmd.extend(["--primary", args.primary])
    if args.font_size:
        cmd.extend(["--font-size", args.font_size])
    if args.indent:
        cmd.extend(["--indent", args.indent])

    try:
        subprocess.run(cmd, cwd=compiler_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed with code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
