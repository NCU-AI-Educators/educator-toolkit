#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Markdown CJK Formatting Spacer
用于自动化扫描 Markdown 文件，识别前后紧贴中文字符的行内格式串（加粗、行内代码、删除线等），
并在格式串前后智能补入对称或单侧空格，实现符合盘古之白规范的排版。
"""

import argparse
import os
import re
import sys
from typing import List, Tuple


class MarkdownCJKSpacer:
    # 纯汉字 Unicode 匹配正则
    CJK_REGEX = re.compile(r"[\u4e00-\u9fa5]")

    # 识别合法的行内格式串 Token
    # 支持加粗、行内代码、删除线、斜体以及内外嵌引号（“...”或"..."）
    TOKEN_REGEX = re.compile(
        r'([“"‘\']?(?:'
        r'\*\*\*(?!\s)[^\*\n]+?(?<!\s)\*\*\*'  # 粗斜体 ***...***
        r'|\*\*(?!\s)[^\*\n]+?(?<!\s)\*\*'     # 加粗 **...**
        r'|``[^\n]+?``'                         # 双反引号行内代码 ``...``
        r'|(?<!`)`[^`\n]+?`(?!`)'               # 单反引号行内代码 `...`
        r'|~~(?!\s)[^~\n]+?(?<!\s)~~'          # 删除线 ~~...~~
        r'|(?<!\*)\*(?!\s|\*)[^\*\n]+?(?<!\s|\*)\*(?!\*)'  # 斜体 *...*
        r')[”"’\']?)'
    )

    def process_content(self, content: str) -> Tuple[str, List[Tuple[str, str, int]]]:
        """
        逐行扫描并处理内容，保护代码块并执行精准空格补全。
        返回: (更新后的文本内容, 变更记录清单[(原文片段, 替换后片段, 行号)])
        """
        lines = content.splitlines(keepends=True)
        in_code_block = False
        code_fence_marker = ""
        in_math_block = False

        modified_lines = []
        changes = []

        for line_idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # 1. 围栏代码块状态切换 (``` 或 ~~~)
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                if not in_code_block:
                    in_code_block = True
                    code_fence_marker = fence
                elif fence == code_fence_marker:
                    in_code_block = False
                    code_fence_marker = ""
                modified_lines.append(line)
                continue

            # 2. 数学公式块状态切换 ($$)
            if stripped.startswith("$$"):
                # 防御单行自闭合公式块（如 "$$formula$$"），避免将后续全文误判为数学块
                if stripped.endswith("$$") and len(stripped) > 2:
                    modified_lines.append(line)
                    continue
                in_math_block = not in_math_block
                modified_lines.append(line)
                continue

            # 若在代码块或多行公式块内，原样保留
            if in_code_block or in_math_block:
                modified_lines.append(line)
                continue

            # 3. 在普通文本行中查找并替换与中文字符紧贴的格式串
            cur_line = line
            line_changes = []
            
            result_segments = []
            last_idx = 0
            line_modified = False

            for m in self.TOKEN_REGEX.finditer(cur_line):
                start, end = m.span()
                token = m.group(0)

                # 排除倒置虚假匹配（如从前一个加粗结尾的**跨越标点到后一个加粗开头的**）
                inner = token.strip('“"‘\'”')
                if inner.startswith("**") and inner.endswith("**"):
                    core = inner[2:-2]
                    # 若加粗内部紧随中英文标点开头，说明是跨闭合与开启标签的误匹配
                    if core.startswith(("：", "，", "。", "；", "、", " ", ":", ",", ".")):
                        continue

                # 检查前置字符是否为中文汉字（若为汉字则需前置空格）
                need_space_before = False
                if start > 0:
                    char_before = cur_line[start - 1]
                    if self.CJK_REGEX.match(char_before):
                        need_space_before = True

                # 检查后置字符是否为中文汉字（若为汉字则需后置空格）
                need_space_after = False
                if end < len(cur_line):
                    char_after = cur_line[end]
                    if self.CJK_REGEX.match(char_after):
                        need_space_after = True

                # 若前置或后置需要补空格，按需单侧或双侧补入
                if need_space_before or need_space_after:
                    line_modified = True
                    result_segments.append(cur_line[last_idx:start])
                    
                    prefix = " " if need_space_before else ""
                    suffix = " " if need_space_after else ""
                    result_segments.append(f"{prefix}{token}{suffix}")

                    before_snip = cur_line[max(0, start - 1) : min(len(cur_line), end + 1)].strip()
                    after_snip = f"{cur_line[start-1] if need_space_before else ''}{prefix}{token}{suffix}{cur_line[end] if need_space_after else ''}".strip()
                    line_changes.append((before_snip, after_snip, line_idx))

                    last_idx = end

            if line_modified:
                result_segments.append(cur_line[last_idx:])
                new_line = "".join(result_segments)
                modified_lines.append(new_line)
                changes.extend(line_changes)
            else:
                modified_lines.append(line)

        return "".join(modified_lines), changes


def process_file(file_path: str, inplace: bool = False) -> Tuple[int, List[Tuple[str, str, int]]]:
    """处理指定文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    spacer = MarkdownCJKSpacer()
    new_content, changes = spacer.process_content(content)

    if changes and inplace:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return len(changes), changes


def collect_markdown_files(target_paths: List[str]) -> List[str]:
    """收集所有目标 Markdown 文件的绝对路径"""
    collected = []
    for p in target_paths:
        if os.path.isfile(p):
            if p.lower().endswith(".md") or p.lower().endswith(".markdown"):
                collected.append(os.path.abspath(p))
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                # 过滤 .git、node_modules、.agents 等配置目录
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
                for f in files:
                    if f.lower().endswith(".md") or f.lower().endswith(".markdown"):
                        collected.append(os.path.abspath(os.path.join(root, f)))
    return sorted(list(set(collected)))


def main():
    parser = argparse.ArgumentParser(
        description="Markdown CJK Formatting Spacer - 中文字符与行内格式串空格补全工具"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="待处理的文件或目录路径（默认当前工作区目录）",
    )
    parser.add_argument(
        "-i",
        "--inplace",
        action="store_true",
        help="直接就地修改并保存文件（缺省时仅执行安全预览）",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="显示所有命中的具体行号与改动文本片段",
    )

    args = parser.parse_args()

    files = collect_markdown_files(args.paths)
    if not files:
        print("未检索到任何符合条件的 Markdown 文件。")
        sys.exit(0)

    total_files_matched = 0
    total_spans_spaced = 0

    mode_label = "【就地修改保存模式】" if args.inplace else "【安全预览/检查模式 (未写盘)】"
    print(f"[*] 开始扫描 {len(files)} 个 Markdown 文档... {mode_label}\n")

    for fpath in files:
        count, changes = process_file(fpath, inplace=args.inplace)
        if count > 0:
            total_files_matched += 1
            total_spans_spaced += count
            rel_path = os.path.relpath(fpath, os.getcwd())
            print(f"  • {rel_path} -> 命中并补全 {count} 处格式串空格")
            if args.verbose or not args.inplace:
                for before, after, line_idx in changes[:10]:
                    print(f"      [第 {line_idx} 行] {before}  ==>  {after}")
                if len(changes) > 10:
                    print(f"      ... 其余 {len(changes) - 10} 处变动已略去")

    print("\n" + "=" * 60)
    if args.inplace:
        print(f"[✓] 批量处理成功！共修改 {total_files_matched} 个文件，成功补全 {total_spans_spaced} 处中文字符行内格式串空格。")
    else:
        print(f"[!] 预览检查完毕：共在 {total_files_matched} 个文件中检测到 {total_spans_spaced} 处待补全格式串。")
        print("    提示：若要将以上改动直接写入文件，请增加 `-i` 或 `--inplace` 参数重新执行。")


if __name__ == "__main__":
    main()
