#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
SSOT-to-Typst: 单一事实源基准 (SSOT) 编译出版级矢量 PDF 核心转换引擎
==============================================================================
特性融合:
1. 完整继承 NCU 辛苦调优的 A4 双面印刷排版规范 (奇偶对称页眉、内外书脊边距、三线表、show raw 卡片)
2. 深度集成 4090 服务器本地 Kroki 统一图表算力 (Mermaid/PlantUML/D2/Graphviz)
3. 严密解决 LaTeX 数学公式多字母变量引号保护、算子映射与反斜杠剥除
4. 顶级元数据台设计: 标签与内容上下分层、语义智能断句对齐 (杜绝截字断行)
5. 工业级鲁棒性: 列表符号兼容、@ 符号转义、防表头分页断开 (breakable: false)
==============================================================================
"""

import os
import sys
import re
import yaml
import hashlib
import argparse
import subprocess
import urllib.request
from pathlib import Path

# 支持通过 Kroki 自动渲染的图表语言列表
KROKI_DIAGRAM_TYPES = {"mermaid", "plantuml", "d2", "graphviz", "dot", "c4plantuml", "excalidraw"}

# Typst 数学模式内置保留字与符号（不需要且不能包裹双引号）
TYPST_MATH_BUILTINS = {
    "sin", "cos", "tan", "cot", "sec", "csc", "arcsin", "arccos", "arctan",
    "sinh", "cosh", "tanh", "log", "ln", "lg", "exp", "min", "max", "argmin", "argmax",
    "det", "dim", "gcd", "lcm", "ker", "hom", "mod", "lim", "sup", "inf", "root", "sqrt",
    "sum", "prod", "product", "integral", "dif", "partial", "round", "floor", "ceil",
    "bold", "italic", "upright", "underline", "overline", "cal", "bb", "frak", "mono",
    "hat", "tilde", "dot", "ddot", "arrow", "vec", "macron", "top", "accent",
    "in", "notin", "subset", "supset", "approx", "equiv", "propto", "quad",
    "and", "or", "not", "times", "plus", "minus", "div", "star",
    "NN", "ZZ", "QQ", "RR", "CC", "infinity",
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "varkappa", "lambda", "mu", "nu", "xi",
    "omicron", "pi", "varpi", "rho", "varrho", "sigma", "varsigma", "tau", "upsilon",
    "phi", "varphi", "chi", "psi", "omega",
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota",
    "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau",
    "Upsilon", "Phi", "Chi", "Psi", "Omega"
}

def render_diagram_via_kroki(source: str, diagram_type: str, output_dir: str) -> str:
    """通过 4090 服务器上的 Kroki 算力渲染图表并缓存为图片"""
    kroki_endpoint = os.getenv("KROKI_ENDPOINT", "http://192.168.8.6:8000").rstrip("/")
    fmt = "png" if diagram_type.lower() == "mermaid" else "svg"

    content_hash = hashlib.md5(f"{diagram_type}:{source.strip()}".encode('utf-8')).hexdigest()[:12]
    filename = f"diagram_{content_hash}.{fmt}"
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    target_path = os.path.join(fig_dir, filename)

    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        return target_path

    url = f"{kroki_endpoint}/{diagram_type.lower()}/{fmt}"
    try:
        req = urllib.request.Request(
            url,
            data=source.strip().encode('utf-8'),
            headers={
                'Content-Type': 'text/plain; charset=utf-8',
                'User-Agent': 'NCU-Typst-Pipeline/1.0'
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            if len(data) > 0:
                with open(target_path, "wb") as f:
                    f.write(data)
                return target_path
    except Exception as e:
        print(f"⚠️  [Kroki] 图表渲染降级 ({diagram_type}): {e}")
        return None

    return None

def format_org_cell(text: str, max_chars: int = 14) -> str:
    """
    智能优化机构与团队名称在元数据栏中的排版折行：
    如果在 14 字以内，单行展示；
    如果超过 14 字，优先在语义连接词（括号、与、及、/、空格）处自然断行。
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text

    # 优先在中文或英文括号处断行
    if "（" in text:
        parts = text.split("（", 1)
        return parts[0].strip() + " \\ \n（" + parts[1].strip()
    if "(" in text:
        parts = text.split("(", 1)
        return parts[0].strip() + " \\ \n(" + parts[1].strip()

    # 其次在语义连接词处断行
    for conj in ["与", "及", "以及"]:
        if conj in text:
            idx = text.rfind(conj)
            if 6 <= idx <= len(text) - 4:
                return text[:idx].strip() + f" \\ \n{conj}" + text[idx+len(conj):].strip()

    # 再次在空格处断行
    if " " in text:
        spaces = [i for i, c in enumerate(text) if c == ' ']
        mid = len(text) / 2
        best_sp = min(spaces, key=lambda i: abs(i - mid))
        if 6 <= best_sp <= len(text) - 4:
            return text[:best_sp].strip() + " \\ \n" + text[best_sp+1:].strip()

    return text

def quote_math_words(s: str) -> str:
    """自动将公式中未在 Typst 内置白名单中的多字母标识符（如 SO, RMSE, IoU, Hz, cm）加上双引号"""
    def repl(m):
        w = m.group(1)
        if w in TYPST_MATH_BUILTINS:
            return w
        return f'"{w}"'
    
    parts = s.split('"')
    pattern = re.compile(r'(?<![a-zA-Z\.])([A-Za-z]{2,})(?![a-zA-Z\.])')
    for i in range(0, len(parts), 2):
        parts[i] = pattern.sub(repl, parts[i])
    return '"'.join(parts)

def convert_latex_math_to_typst(math_content: str) -> str:
    """将常见 LaTeX 数学公式语法精准转换为 Typst 语法"""
    raw = math_content.strip()

    raw = re.sub(r'\\text\{([^}]+)\}', lambda m: f'"{m.group(1).strip()}"', raw)
    raw = re.sub(r'\\mathrm\{([^}]+)\}', lambda m: f'"{m.group(1).strip()}"', raw)


    raw = re.sub(r'\\mathbf\{([^}]+)\}', r'bold(\1)', raw)
    raw = re.sub(r'\\boldsymbol\{([^}]+)\}', r'bold(\1)', raw)
    raw = re.sub(r'\\mathit\{([^}]+)\}', r'italic(\1)', raw)
    raw = re.sub(r'\\mathbb\{R\}', 'RR', raw)
    raw = re.sub(r'\\mathbb\{N\}', 'NN', raw)
    raw = re.sub(r'\\mathbb\{Z\}', 'ZZ', raw)
    raw = re.sub(r'\\mathbb\{C\}', 'CC', raw)
    raw = re.sub(r'\\mathcal\{([^}]+)\}', r'cal(\1)', raw)

    raw = re.sub(r'\\left\(', '(', raw)
    raw = re.sub(r'\\right\)', ')', raw)
    raw = re.sub(r'\\left\[', '[', raw)
    raw = re.sub(r'\\right\]', ']', raw)
    raw = re.sub(r'\\left\\\{', '{', raw)
    raw = re.sub(r'\\right\\\}', '}', raw)
    raw = raw.replace(r'\{', '{').replace(r'\}', '}')

    raw = re.sub(r'\\quad(?![a-zA-Z])', ' quad ', raw)
    raw = re.sub(r'\\qquad(?![a-zA-Z])', ' quad quad ', raw)
    raw = re.sub(r'\\,(?![a-zA-Z])', ' ', raw)
    raw = re.sub(r'\\;(?![a-zA-Z])', ' ', raw)
    raw = re.sub(r'h\(1em\)', ' quad ', raw)
    raw = re.sub(r'h\(2em\)', ' quad quad ', raw)

    replacements = [
        (r'\\iint(?![a-zA-Z])', 'integral.double'),
        (r'\\iiint(?![a-zA-Z])', 'integral.triple'),
        (r'\\oint(?![a-zA-Z])', 'integral.cont'),
        (r'\\int(?![a-zA-Z])', 'integral'),
        (r'\\partial(?![a-zA-Z])', 'partial'),
        (r'\\sim(?![a-zA-Z])', 'tilde'),
        (r'\\ge(?![a-zA-Z])', '>='),
        (r'\\geq(?![a-zA-Z])', '>='),
        (r'\\le(?![a-zA-Z])', '<='),
        (r'\\leq(?![a-zA-Z])', '<='),
        (r'\\ne(?![a-zA-Z])', '!='),
        (r'\\neq(?![a-zA-Z])', '!='),
        (r'\\approx(?![a-zA-Z])', 'approx'),
        (r'\\equiv(?![a-zA-Z])', 'equiv'),
        (r'\\times(?![a-zA-Z])', 'times'),
        (r'\\cdot(?![a-zA-Z])', 'dot'),
        (r'\\pm(?![a-zA-Z])', 'plus.minus'),
        (r'\\in(?![a-zA-Z])', 'in'),
        (r'\\notin(?![a-zA-Z])', 'not in'),
        (r'\\subset(?![a-zA-Z])', 'subset'),
        (r'\\to(?![a-zA-Z])', 'arrow.r'),
        (r'\\rightarrow(?![a-zA-Z])', 'arrow.r'),
        (r'\\leftarrow(?![a-zA-Z])', 'arrow.l'),
        (r'\\Rightarrow(?![a-zA-Z])', 'arrow.r.double'),
        (r'\\sum(?![a-zA-Z])', 'sum'),
        (r'\\prod(?![a-zA-Z])', 'product'),
        (r'\\infty(?![a-zA-Z])', 'infinity'),
        (r'\\nabla(?![a-zA-Z])', 'nabla'),
        (r'\\alpha(?![a-zA-Z])', 'alpha'),
        (r'\\beta(?![a-zA-Z])', 'beta'),
        (r'\\gamma(?![a-zA-Z])', 'gamma'),
        (r'\\delta(?![a-zA-Z])', 'delta'),
        (r'\\epsilon(?![a-zA-Z])', 'epsilon'),
        (r'\\theta(?![a-zA-Z])', 'theta'),
        (r'\\lambda(?![a-zA-Z])', 'lambda'),
        (r'\\mu(?![a-zA-Z])', 'mu'),
        (r'\\rho(?![a-zA-Z])', 'rho'),
        (r'\\sigma(?![a-zA-Z])', 'sigma'),
        (r'\\omega(?![a-zA-Z])', 'omega'),
        (r'\\Delta(?![a-zA-Z])', 'Delta'),
        (r'\\Omega(?![a-zA-Z])', 'Omega'),
        (r'\\%', '%'),
    ]
    for pattern, repl in replacements:
        raw = re.sub(pattern, repl, raw)

    for fn in ["sin", "cos", "tan", "cot", "log", "ln", "exp", "min", "max", "argmin", "argmax", "det", "dim", "sqrt"]:
        raw = re.sub(r'\\' + fn + r'(?![a-zA-Z])', fn, raw)

    # 递归转换嵌套层级的 LaTeX 分数 \frac{A}{B} 为 Typst (A) / (B)
    def parse_frac(s):
        pos = s.find(r'\frac')
        if pos == -1:
            return s
        p1_start = s.find('{', pos)
        if p1_start == -1:
            return s
        depth = 0
        p1_end = -1
        for j in range(p1_start, len(s)):
            if s[j] == '{': depth += 1
            elif s[j] == '}':
                depth -= 1
                if depth == 0:
                    p1_end = j
                    break
        if p1_end == -1:
            return s
        p2_start = s.find('{', p1_end)
        if p2_start == -1:
            return s
        depth = 0
        p2_end = -1
        for j in range(p2_start, len(s)):
            if s[j] == '{': depth += 1
            elif s[j] == '}':
                depth -= 1
                if depth == 0:
                    p2_end = j
                    break
        if p2_end == -1:
            return s
        num = parse_frac(s[p1_start+1:p1_end])
        den = parse_frac(s[p2_start+1:p2_end])
        return s[:pos] + f"({num}) / ({den})" + parse_frac(s[p2_end+1:])

    raw = parse_frac(raw)
    raw = re.sub(r'\\bar\{([^}]+)\}', r'macron(\1)', raw)
    raw = re.sub(r'\\vec\{([^}]+)\}', r'arrow(\1)', raw)

    raw = re.sub(r'\\([a-zA-Z]+)', r'\1', raw)
    raw = re.sub(r'_\{([^}]+)\}', r'_(\1)', raw)
    raw = re.sub(r'\^\{([^}]+)\}', r'^(\1)', raw)
    raw = quote_math_words(raw)

    return raw

def format_inline_markdown(text: str) -> str:
    """格式化正文行内 Markdown（粗体、斜体、代码、行内公式、特殊字符转义）"""
    text = text.replace("*/", "* /")

    codes = []
    def save_code(m):
        codes.append(m.group(1))
        return f"__INLINE_CODE_{len(codes)-1}__"
    text = re.sub(r'`([^`]+)`', save_code, text)

    maths = []
    def save_math(m):
        maths.append(convert_latex_math_to_typst(m.group(1)))
        return f"__INLINE_MATH_{len(maths)-1}__"
    text = re.sub(r'\$([^\$]+)\$', save_math, text)

    text = text.replace("@", "\\@")

    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'#strong(emph[\1])', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'#strong[\1]', text)
    text = re.sub(r'\*(.*?)\*', r'#emph[\1]', text)

    for idx, math_typ in enumerate(maths):
        text = text.replace(f"__INLINE_MATH_{idx}__", f"${math_typ}$")

    for idx, code_str in enumerate(codes):
        text = text.replace(f"__INLINE_CODE_{idx}__", f'`{code_str}`')

    return text

def parse_markdown_table_to_typst(table_text: str) -> str:
    """符合调优标准的科技三线表（带表头双线与无缩进单元格）"""
    lines = [l.strip() for l in table_text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return ""

    rows = []
    for line in lines:
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cols = [c.strip() for c in line.split("|")]
        rows.append(cols)

    content_rows = []
    for r in rows:
        if all(re.match(r'^:?-+:?$', c) for c in r):
            continue
        content_rows.append(r)

    if not content_rows:
        return ""

    num_cols = max(len(r) for r in content_rows)
    for r in content_rows:
        while len(r) < num_cols:
            r.append("")

    if num_cols == 2:
        col_spec = "(1.5fr, 4fr)"
    elif num_cols == 3:
        col_spec = "(1.5fr, 2.5fr, 4fr)"
    elif num_cols == 4:
        col_spec = "(1.2fr, 2fr, 3.8fr, 3.8fr)"
    elif num_cols == 5:
        col_spec = "(1fr, 1.4fr, 2fr, 3fr, 3fr)"
    elif num_cols == 6:
        col_spec = "(1fr, 1fr, 1.6fr, 2.8fr, 3fr, 3fr)"
    else:
        col_spec = f"({', '.join(['1fr']*num_cols)})"

    num_rows = len(content_rows)
    if num_rows == 1:
        stroke_code = "    stroke: (x, y) => if y == 0 { (top: 1.2pt + rgb(\"#0f172a\"), bottom: 1.2pt + rgb(\"#0f172a\")) },"
    else:
        stroke_code = f"    stroke: (x, y) => if y == 0 {{ (top: 1.2pt + rgb(\"#0f172a\"), bottom: 0.8pt + rgb(\"#0f172a\")) }} else if y == {num_rows - 1} {{ (bottom: 1.2pt + rgb(\"#0f172a\")) }} else {{ (bottom: 0.5pt + rgb(\"#e2e8f0\")) }},"

    typ_table = [
        "#align(center)[#block(width: 100%)[",
        "  #show table.cell: set par(justify: false, first-line-indent: (amount: 0em, all: true))",
        f"  #table(",
        f"    columns: {col_spec},",
        "    fill: (col, row) => if row == 0 { rgb(\"#f1f5f9\") } else { none },",
        stroke_code,
        "    inset: (x: 7pt, y: 5pt),",
        "    align: (col, row) => if row == 0 { center + horizon } else { left + horizon },",
    ]

    for row_idx, row in enumerate(content_rows):
        typ_table.append(f"    // Row {row_idx}")
        if row_idx == 0:
            typ_table.append("    table.header(")
            for col in row:
                cell_formatted = format_inline_markdown(col)
                cell_formatted = cell_formatted.replace("<br>", "\n").replace("<br/>", "\n")
                typ_table.append(f"      table.cell[#set par(first-line-indent: (amount: 0em, all: true)); #strong[{cell_formatted}]],")
            typ_table.append("    ),")
        else:
            for col in row:
                cell_formatted = format_inline_markdown(col)
                cell_formatted = cell_formatted.replace("<br>", "\n").replace("<br/>", "\n")
                typ_table.append(f"    table.cell[#set par(first-line-indent: (amount: 0em, all: true)); {cell_formatted}],")

    typ_table.append("  )")
    typ_table.append("]]")
    return "\n".join(typ_table)

def convert_ssot_to_typst(md_path: str, mode: str = "book") -> str:
    """核心转换函数：生成符合双面出版级调优规范或移动端自适应长图规范的 Typst 源码"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc_dir = os.path.dirname(os.path.abspath(md_path))

    # 1. 提取 YAML Frontmatter
    metadata = {
        'title': '技术工程设计基准',
        'subtitle': '',
        'document_id': 'SSOT-SPEC-2026-V1.0',
        'classification': '内部受控',
        'author': '系统架构委员会',
        'institution': '南昌大学AI创新应用实验室（AIIA Lab@NCU）',
        'date': '2026年9月',
        'abstract': '',
        'keywords': '',
    }

    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                parsed_yaml = yaml.safe_load(parts[1])
                if isinstance(parsed_yaml, dict):
                    metadata.update(parsed_yaml)
            except Exception as e:
                print(f"Warning: YAML parse error: {e}")
            body = parts[2]

    # 密级保底净化：若包含体裁后缀则自动剔除
    if "/" in str(metadata.get("classification", "")):
        metadata["classification"] = metadata["classification"].split("/")[0].strip()
    body_lines = body.split("\n")
    clean_lines = []
    for l in body_lines:
        if l.strip().startswith("# ") and not l.strip().startswith("## "):
            continue
        clean_lines.append(l)

    # 智能断行处理编制团队与研发机构
    formatted_author = format_org_cell(metadata['author'])
    formatted_inst = format_org_cell(metadata['institution']).replace("@", '#"@"')

    # 2. 构建出版级 Typst 模板头
    typ_lines = []
    if mode == "long":
        # 长图模式：100% 遵循当前出版级排版规范，仅采用连续无缝版心 (height: auto) 并去除页眉页脚
        typ_lines.append(f"""// ==============================================================================
// NCU Smart Platform - 全场景技术文档出版生产线 (自适应无缝长图模式)
// 编译核心: Typst 0.15+ | 算力画图: 4090 Kroki 引擎
// 研制机构: {metadata['institution']}
// ==============================================================================

#set page(
  width: 210mm,
  height: auto,
  margin: (x: 20mm, top: 22mm, bottom: 22mm),
  fill: rgb("#ffffff"),
  header: none,
  footer: none,
)""")
    else:
        # A4 双面印刷出版模式：对称装订边距与奇偶页动态页眉页脚
        typ_lines.append(f"""// ==============================================================================
// NCU Smart Platform - A4 出版级技术规范双面排版系统 (SSOT 调优版)
// 编译核心: Typst 0.15+ | 算力画图: 4090 Kroki 引擎
// 研制机构: {metadata['institution']}
// ==============================================================================

#set page(
  paper: "a4",
  margin: (inside: 24mm, outside: 20mm, top: 22mm, bottom: 22mm),
  header: context {{
    let page_num = counter(page).get().first()
    if page_num > 1 {{
      let is_odd = calc.odd(page_num)
      let left_content = if is_odd {{
        text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{metadata['title']}]
      }} else {{
        text(size: 8.5pt, fill: rgb("#0369a1"), weight: "bold", font: ("PingFang SC", "Heiti SC"))[#page_num]
      }}
      
      let right_content = if is_odd {{
        text(size: 8.5pt, fill: rgb("#0369a1"), weight: "bold", font: ("PingFang SC", "Heiti SC"))[#page_num]
      }} else {{
        text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[受控编号：#text(fill: rgb("#0369a1"), weight: "bold")[#raw("{metadata['document_id']}")]]
      }}

      let header_cols = if is_odd {{ (1fr, auto) }} else {{ (auto, 1fr) }}
      grid(
        columns: header_cols,
        align(left + horizon)[#left_content],
        align(right + horizon)[#right_content]
      )
      v(-2pt)
      line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    }}
  }},
  footer: context {{
    let page_num = counter(page).get().first()
    if page_num > 0 {{
      line(length: 100%, stroke: 0.5pt + rgb("#e2e8f0"))
      v(2pt)
      grid(
        columns: (1fr, auto),
        align(left + horizon)[
          #text(8pt, fill: rgb("#64748b"), font: ("PingFang SC", "Songti SC"))[
            #text("{metadata['institution']}") · #text(fill: rgb("#0f172a"), weight: "medium")[{metadata['classification']}]
          ]
        ],
        align(right + horizon)[
          #text(8.5pt, fill: rgb("#0f172a"), weight: "bold")[— #page_num —]
        ]
      )
    }}
  }}
)""")

    # 两种模式严格共享 100% 一致的正文字体、行距、首行缩进与列表排版规范
    typ_lines.append(f"""
#set text(
  font: ("Times New Roman", "Songti SC", "STSong", "Songti TC", "SimSun"),
  size: 10.5pt,
  lang: "zh"
)

// 中文粗体规范：以黑体字族展现清晰高品质粗体
#show strong: set text(font: ("Times New Roman", "PingFang SC", "Heiti SC", "STHeiti", "SimHei"), weight: "bold", fill: rgb("#0f172a"))

// 中文正文首行缩进两格 (2em) 与呼吸感行距
#set par(
  justify: true,
  leading: 0.82em,
  spacing: 0.85em,
  first-line-indent: (amount: 2em, all: true)
)

// 列表与正文首行严格对齐规范（首行对齐段落首部缩进 2em，项目符号至文字 0.5em，条目间距匀称，二级编号为出版规范模式A）
#set list(indent: 2em, body-indent: 0.5em, spacing: 0.85em)
#set enum(
  indent: 2em,
  body-indent: 0.5em,
  spacing: 0.85em,
  numbering: "(1)"
)
#show list: set block(above: 0.85em, below: 0.85em)
#show enum: set block(above: 0.85em, below: 0.85em)""")

    typ_lines.append(f"""
// 图表原生编号样式优化（去除默认额外 supplement）
#show figure.where(kind: image): set figure(supplement: none, numbering: none)

// 代码块原生高质感卡片样式
#show raw.where(block: true): it => block(
  width: 100%,
  stroke: 0.8pt + rgb("#cbd5e1"),
  fill: rgb("#f8fafc"),
  radius: 4pt,
  inset: (x: 10pt, y: 8pt),
  text(font: ("Menlo", "Monaco", "Courier New"), size: 8.8pt)[#it]
)

// 行内代码原生浅灰边框胶囊
#show raw.where(block: false): it => box(
  fill: rgb("#f1f5f9"),
  inset: (x: 3.5pt, y: 0pt),
  outset: (y: 2pt),
  radius: 3pt,
  stroke: 0.5pt + rgb("#cbd5e1"),
  text(font: ("Menlo", "Monaco", "Courier New"), size: 9pt)[#it]
)

// 引用与重要提示卡片样式
#show quote.where(block: true): it => block(
  width: 100%,
  stroke: (left: 3.5pt + rgb("#0284c7")),
  fill: rgb("#f0f9ff"),
  inset: (x: 12pt, y: 8pt),
  radius: (right: 4pt),
  above: 8pt,
  below: 10pt,
  text(fill: rgb("#0f172a"))[#it.body]
)

// 标题层级体系规范（用户指定精准间距体系）
#show heading.where(level: 1): it => block(width: 100%, above: 1.5em, below: 1.25em)[
  #set align(center)
  #set text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 18pt, weight: "bold", fill: rgb("#0f172a"))
  #it.body
]

#show heading.where(level: 2): it => block(width: 100%, above: 1.25em, below: 1.0em)[
  #set text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 13.5pt, weight: "bold", fill: rgb("#0369a1"))
  #it.body
]

#show heading.where(level: 3): it => block(width: 100%, above: 1.0em, below: 0.8em)[
  #set text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 11pt, weight: "bold", fill: rgb("#1e293b"))
  #it.body
]

#show heading.where(level: 4): it => block(width: 100%, above: 0.8em, below: 0.6em)[
  #set text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 10pt, weight: "bold", fill: rgb("#334155"))
  #it.body
]

// 核心大标题与优雅分层元数据台
#align(center)[
  #block(width: 100%)[
    #text(font: ("PingFang SC", "Heiti SC"), size: 18pt, weight: "bold", fill: rgb("#0f172a"))[{metadata['title']}]
""")

    if metadata.get('subtitle'):
        typ_lines.append(f"""    #v(3pt)
    #text(font: ("PingFang SC", "Heiti SC"), size: 11.5pt, fill: rgb("#475569"))[{metadata['subtitle']}]
""")

    typ_lines.append(f"""    #v(10pt)
    #line(length: 100%, stroke: 0.8pt + rgb("#cbd5e1"))
    #v(4pt)
    #grid(
      columns: (2.3fr, 2.3fr, 1fr),
      column-gutter: 14pt,
      row-gutter: 5pt,
      align(left)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[编 制 团 队]],
      align(left)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[研 发 机 构]],
      align(right)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[发 布 日 期]],
      
      align(left)[#text(9pt, weight: "medium", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[{formatted_author}]],
      align(left)[#text(9pt, weight: "medium", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[{formatted_inst}]],
      align(right)[#text(9pt, weight: "medium", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[{metadata['date']}]]
    )
    #v(6pt)
    #grid(
      columns: (1.2fr, 1fr),
      align(left)[#text(8.5pt, fill: rgb("#0369a1"), weight: "bold", font: ("PingFang SC", "Heiti SC"))[受控编号：#raw("{metadata['document_id']}") ]],
      align(right)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[受控密级：#text(fill: rgb("#0f172a"), weight: "medium")[{metadata['classification']}]]]
    )
    #v(6pt)
    #line(length: 100%, stroke: 1.2pt + rgb("#0f172a"))
  ]
]

// 摘要与关键词卡片
""")

    if metadata.get('abstract'):
        typ_lines.append(f"""#rect(
  width: 100%,
  stroke: (left: 3.5pt + rgb("#0284c7")),
  fill: rgb("#f8fafc"),
  inset: (x: 12pt, y: 10pt),
  radius: (right: 4pt)
)[
  #set par(first-line-indent: (amount: 0em, all: true), leading: 0.7em)
  #text(weight: "bold", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[【摘　要】] #text(fill: rgb("#334155"))[{metadata['abstract']}]
""")
        if metadata.get('keywords'):
            typ_lines.append(f"""  #v(4pt)
  #text(weight: "bold", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[【关键词】] #text(fill: rgb("#0369a1"))[{metadata['keywords']}]
""")
        typ_lines.append("]\n#v(0.6em)\n")

    # 3. 逐行解析正文内容
    i = 0
    in_table = False
    table_buffer = []
    last_table_caption = None
    in_code_block = False
    code_lang = ""
    code_buffer = []
    section_list_counter = 0

    while i < len(clean_lines):
        line = clean_lines[i]
        stripped = line.strip()

        # 代码块处理
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lang = stripped[3:].strip()
                code_buffer = []
                i += 1
                continue
            else:
                in_code_block = False
                code_text = "\n".join(code_buffer)

                # 原生 Typst 语法直通
                if code_lang.lower() == "typst":
                    typ_lines.append(f"\n{code_text}\n")
                    code_buffer = []
                    i += 1
                    continue

                # Kroki 统一算力画图
                if code_lang.lower() in KROKI_DIAGRAM_TYPES:
                    # 前向探测紧随其后的图表题注 *图X-X 名称*，实现图表与题注原子强绑定（严格禁止跨页分离）
                    next_idx = i + 1
                    found_fig_caption = None
                    caption_line_idx = None
                    while next_idx < len(clean_lines):
                        s_next = clean_lines[next_idx].strip()
                        if not s_next:
                            next_idx += 1
                            continue
                        if s_next.startswith("*图") and s_next.endswith("*"):
                            found_fig_caption = s_next[1:-1]
                            caption_line_idx = next_idx
                        break

                    # 针对图 3-1（双轨模板设计与图文分层解耦渲染流水线）工业级复杂架构图，输出真正出版级原生矢量卡片
                    if "Konva" in code_text and ("双轨模板" in code_text or "真实单据种子轨" in code_text):
                        native_pipeline_card = """
#v(0.3em)
#align(center)[#block(
  width: 100%,
  stroke: 1pt + rgb("#cbd5e1"),
  radius: 6pt,
  fill: rgb("#f8fafc"),
  inset: (x: 8pt, y: 8pt)
)[
  #grid(
    columns: (1fr, 14pt, 1.12fr, 14pt, 1.12fr),
    align: (top, horizon, top, horizon, top),
    
    // 阶段一：双轨模板设计
    block(
      width: 100%,
      height: 178pt,
      stroke: 1pt + rgb("#0284c7"),
      fill: rgb("#ffffff"),
      radius: 4pt,
      inset: (x: 6pt, y: 7pt)
    )[
      #align(center)[
        #box(fill: rgb("#e0f2fe"), inset: (x: 7pt, y: 2.5pt), radius: 3pt)[
          #text(weight: "bold", fill: rgb("#0369a1"), size: 9.2pt)[阶段一：双轨模板设计]
        ]
      ]
      #v(5pt)
      #block(width: 100%, stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 3pt, inset: 4.5pt)[
        #text(weight: "bold", size: 8.5pt)[真实单据种子轨]\\
        #v(2pt)
        #text(size: 7.8pt, fill: rgb("#475569"))[真实扫描件 $arrow.r$ Konva 2D 画布标定 (拉框 BBox) $arrow.r$ 真实模板]
      ]
      #v(5pt)
      #block(width: 100%, stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 3pt, inset: 4.5pt)[
        #text(weight: "bold", size: 8.5pt)[虚构单据向导轨]\\
        #v(2pt)
        #text(size: 7.8pt, fill: rgb("#475569"))[向导业务规则库 $arrow.r$ 4步向导生成引擎 $arrow.r$ 虚构模板]
      ]
    ],
    
    // 流向箭头 1 -> 2
    align(center)[#text(size: 13pt, fill: rgb("#0284c7"), weight: "bold")[$arrow.r.double$]],
    
    // 阶段二：解耦渲染流水线
    block(
      width: 100%,
      height: 178pt,
      stroke: 1pt + rgb("#0284c7"),
      fill: rgb("#ffffff"),
      radius: 4pt,
      inset: (x: 6pt, y: 7pt)
    )[
      #align(center)[
        #box(fill: rgb("#e0f2fe"), inset: (x: 7pt, y: 2.5pt), radius: 3pt)[
          #text(weight: "bold", fill: rgb("#0369a1"), size: 9.2pt)[阶段二：解耦渲染与退化]
        ]
      ]
      #v(5pt)
      #block(width: 100%, stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 3pt, inset: 4pt)[
        #align(center)[#text(weight: "bold", size: 8.5pt)[业务字典与 ISO 规范校验]]
      ]
      #v(4pt)
      #grid(
        columns: (1fr, 1fr),
        gutter: 4pt,
        block(stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 2pt, inset: 3.5pt)[
          #text(weight: "bold", size: 8.2pt)[Skia 矢量文字]\\
          #v(1.5pt)
          #text(size: 7.5pt, fill: rgb("#475569"))[透明图层/真实BBox]
        ],
        block(stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 2pt, inset: 3.5pt)[
          #text(weight: "bold", size: 8.2pt)[扩散空白底图]\\
          #v(1.5pt)
          #text(size: 7.5pt, fill: rgb("#475569"))[无文字高质感纸质]
        ]
      )
      #v(4pt)
      #block(width: 100%, stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 3pt, inset: 4pt)[
        #text(size: 8pt)[图层阿尔法混合 $arrow.r$ 复合物理退化]\\
        #v(1.5pt)
        #text(size: 7.2pt, fill: rgb("#64748b"))[(折痕 / 反光 / 脏污 / 倾角扰动)]
      ]
    ],
    
    // 流向箭头 2 -> 3
    align(center)[#text(size: 13pt, fill: rgb("#0284c7"), weight: "bold")[$arrow.r.double$]],
    
    // 阶段三：逆向质检分流
    block(
      width: 100%,
      height: 178pt,
      stroke: 1pt + rgb("#0284c7"),
      fill: rgb("#ffffff"),
      radius: 4pt,
      inset: (x: 6pt, y: 7pt)
    )[
      #align(center)[
        #box(fill: rgb("#e0f2fe"), inset: (x: 7pt, y: 2.5pt), radius: 3pt)[
          #text(weight: "bold", fill: rgb("#0369a1"), size: 9.2pt)[阶段三：逆向闭环质检]
        ]
      ]
      #v(5pt)
      #grid(
        columns: (1fr, 1fr),
        gutter: 4pt,
        block(stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 2pt, inset: 3.5pt)[
          #text(weight: "bold", size: 8.2pt)[Ground-Truth]\\
          #v(1.5pt)
          #text(size: 7.5pt, fill: rgb("#475569"))[真实像素矩阵]
        ],
        block(stroke: 0.8pt + rgb("#cbd5e1"), fill: rgb("#f8fafc"), radius: 2pt, inset: 3.5pt)[
          #text(weight: "bold", size: 8.2pt)[MinerU 逆向]\\
          #v(1.5pt)
          #text(size: 7.5pt, fill: rgb("#475569"))[版面与坐标预测]
        ]
      )
      #v(4pt)
      #block(width: 100%, stroke: 1pt + rgb("#d97706"), fill: rgb("#fef3c7"), radius: 3pt, inset: 4pt)[
        #align(center)[#text(weight: "bold", fill: rgb("#78350f"), size: 8.5pt)[空间交并比校验: $"IoU" >= 98%$]]
      ]
      #v(4pt)
      #grid(
        columns: (1.1fr, 0.9fr),
        gutter: 4pt,
        block(stroke: 1pt + rgb("#059669"), fill: rgb("#ecfdf5"), radius: 2pt, inset: 3.5pt)[
          #align(center)[#text(weight: "bold", fill: rgb("#064e3b"), size: 8pt)[标准合规资产库]]
        ],
        block(stroke: 1pt + rgb("#dc2626"), fill: rgb("#fef2f2"), radius: 2pt, inset: 3.5pt)[
          #align(center)[#text(weight: "bold", fill: rgb("#991b1b"), size: 8pt)[隔离队列重试]]
        ]
      )
    ]
  )
]]
"""
                        caption_snippet = ""
                        if found_fig_caption:
                            caption_snippet = f"""
  #v(-0.2em)
  #align(center)[#text(font: ("PingFang SC", "Songti SC"), size: 9pt, style: "italic", fill: rgb("#475569"))[{found_fig_caption}]]
  #v(0.4em)
"""
                            i = caption_line_idx + 1
                        else:
                            i += 1

                        typ_lines.append(f"""
#block(width: 100%, breakable: false)[
  {native_pipeline_card}
  {caption_snippet}
]
""")
                        code_buffer = []
                        continue

                    img_path = render_diagram_via_kroki(code_text, code_lang, doc_dir)
                    if img_path:
                        rel_img = os.path.relpath(img_path, doc_dir)
                        caption_snippet = ""
                        if found_fig_caption:
                            caption_snippet = f"""
  #v(-0.2em)
  #align(center)[#text(font: ("PingFang SC", "Songti SC"), size: 9pt, style: "italic", fill: rgb("#475569"))[{found_fig_caption}]]
  #v(0.4em)
"""
                            i = caption_line_idx + 1
                        else:
                            i += 1

                        typ_lines.append(f"""
#block(width: 100%, breakable: false)[
  #align(center)[#block(width: 96%)[
    #figure(
      image("{rel_img}", width: 92%)
    )
  ]]
  {caption_snippet}
]
""")
                        code_buffer = []
                        continue

                # 原生代码块卡片
                typ_lines.append(f"""```{code_lang}\n{code_text}\n```""")
                code_buffer = []
                i += 1
                continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # 表格前置标题捕获（支持 **表X-X 名称**、*表 X-X 名称*、表 X-X 名称等学术规范形式）
        table_caption_match = re.match(r'^\s*(?:\*{1,2})?(表\s*\d+[\-\.]\d+.*?)(?:\*{1,2})?\s*$', stripped)
        if table_caption_match:
            last_table_caption = table_caption_match.group(1).strip()
            i += 1
            continue

        # 表格状态机
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_buffer.append(stripped)
            i += 1
            continue
        elif in_table:
            tbl_rendered = parse_markdown_table_to_typst("\n".join(table_buffer))
            if last_table_caption:
                typ_lines.append(f"""
#v(0.2em)
#align(center)[#text(font: ("PingFang SC", "Songti SC", "SimSun"), size: 9pt, style: "italic", fill: rgb("#475569"))[{last_table_caption}]]
#v(-0.1em)
{tbl_rendered}
#v(0.4em)
""")
                last_table_caption = None
            else:
                typ_lines.append(f"\n{tbl_rendered}\n")
            table_buffer = []
            in_table = False

        # 空行
        if not stripped:
            typ_lines.append("")
            i += 1
            continue

        # 分隔线 ---
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            section_list_counter = 0
            typ_lines.append("\n#v(0.5em)#line(length: 100%, stroke: 0.5pt + rgb(\"#e2e8f0\"))#v(0.5em)\n")
            i += 1
            continue

        # 章节标题转换（由 Typst block above/below 统一精准控制，小节内列表计数器归零）
        if stripped.startswith("## "):
            section_list_counter = 0
            title_text = stripped[3:].strip()
            if "参考文献" in title_text or "References" in title_text:
                typ_lines.append(f"#pagebreak(weak: true)\n= {title_text}\n#set enum(indent: 0em, body-indent: 0.5em, spacing: 0.7em, numbering: \"[1]\")\n#set list(indent: 0em, body-indent: 0.5em, spacing: 0.7em)\n#set par(first-line-indent: 0em)")
            else:
                typ_lines.append(f"= {title_text}")
            i += 1
            continue
        
        # 引用块 > 与 GitHub 风格 Callouts
        if stripped.startswith(">"):
            quote_indent = len(line) - len(line.lstrip())
            curr_quote = []
            while i < len(clean_lines) and clean_lines[i].strip().startswith(">"):
                q_line = clean_lines[i].strip()[1:].strip()
                curr_quote.append(q_line)
                i += 1

            # 检查首行是否是 GitHub Callout 标识符 [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION]
            callout_match = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$', curr_quote[0], re.IGNORECASE) if curr_quote else None
            if callout_match:
                c_type = callout_match.group(1).upper()
                c_body_lines = curr_quote[1:]
                
                # 配置各类型的色彩系统
                c_configs = {
                    "NOTE": ("#0284c7", "#f0f9ff", "ℹ️ 提示说明"),
                    "TIP": ("#16a34a", "#f0fdf4", "💡 实践技巧"),
                    "IMPORTANT": ("#7c3aed", "#faf5ff", "📌 关键要点"),
                    "WARNING": ("#d97706", "#fffbeb", "⚠️ 注意事项"),
                    "CAUTION": ("#dc2626", "#fef2f2", "🛑 安全告警"),
                }
                stroke_color, bg_color, default_title = c_configs.get(c_type, ("#0284c7", "#f0f9ff", "提示说明"))
                
                title_line = ""
                content_lines = []
                if c_body_lines and c_body_lines[0].startswith("**") and c_body_lines[0].endswith("**"):
                    title_line = c_body_lines[0][2:-2].strip()
                    content_lines = [format_inline_markdown(l) for l in c_body_lines[1:] if l]
                else:
                    title_line = default_title
                    content_lines = [format_inline_markdown(l) for l in c_body_lines if l]
                
                body_joined = "\n\n".join(content_lines)
                typ_lines.append(f"""
#block(
  width: 100%,
  stroke: (left: 3.5pt + rgb("{stroke_color}")),
  fill: rgb("{bg_color}"),
  inset: (x: 12pt, y: 10pt),
  radius: (right: 4pt),
  above: 8pt,
  below: 10pt
)[
  #set par(first-line-indent: (amount: 0em, all: true), leading: 0.7em)
  #block(width: 100%, below: 0.65em)[
    #text(font: ("PingFang SC", "Heiti SC"), weight: "bold", size: 10pt, fill: rgb("{stroke_color}"))[{title_line}]
  ]
  #text(size: 9.5pt)[{body_joined}]
]
""")
                continue

            # 普通引用块
            formatted_quotes = [format_inline_markdown(q) for q in curr_quote]
            joined_quote = "\n\n".join(formatted_quotes)
            if quote_indent >= 2:
                typ_lines.append(f"""
#pad(left: 2em)[
  #block(
    width: 100%,
    stroke: (left: 2.5pt + rgb("#0284c7")),
    fill: rgb("#f0f9ff"),
    inset: (x: 10pt, y: 7pt),
    radius: (right: 3pt),
    above: 0.6em,
    below: 0.8em
  )[
    #set par(first-line-indent: (amount: 0em, all: true), leading: 0.7em)
    {joined_quote}
  ]
]
""")
            else:
                typ_lines.append(f"""
#block(
  width: 100%,
  stroke: (left: 3.5pt + rgb("#0284c7")),
  fill: rgb("#f0f9ff"),
  inset: (x: 12pt, y: 8pt),
  radius: (right: 4pt),
  above: 8pt,
  below: 10pt
)[
  #set par(first-line-indent: (amount: 0em, all: true), leading: 0.7em)
  {joined_quote}
]
""")
            continue

        if stripped.startswith("### "):
            section_list_counter = 0
            sub_title = stripped[4:].strip()
            if "参考文献" in sub_title or "References" in sub_title:
                typ_lines.append(f"#pagebreak(weak: true)\n== {sub_title}\n#set enum(indent: 0em, body-indent: 0.5em, spacing: 0.7em, numbering: \"[1]\")\n#set list(indent: 0em, body-indent: 0.5em, spacing: 0.7em)\n#set par(first-line-indent: 0em)")
            elif ("3.2" in sub_title and "图文分层解耦渲染" in sub_title) or ("3.3" in sub_title and "业务对话状态机" in sub_title):
                typ_lines.append("#pagebreak(weak: true)")
                typ_lines.append(f"== {sub_title}")
            else:
                typ_lines.append(f"== {sub_title}")
            i += 1
            continue
        elif stripped.startswith("#### "):
            section_list_counter = 0
            h4_title = stripped[5:].strip()
            # 普适语义规则：区分“树状章节编号小节（如 4.1.1）”与“内容段落级小标题（如 第一阶段：...）”
            if re.match(r'^\d+(\.\d+)+\s+', h4_title):
                # 带层级点分编号：作为正式结构小节，左对齐顶格锚定版面
                typ_lines.append(f"=== {h4_title}")
            else:
                # 无点分编号的段落级小标题：首行缩进 2em 对齐正文与列表首部，消除锯齿凹凸
                formatted_h4 = format_inline_markdown(h4_title)
                typ_lines.append(f"""
#pad(left: 2em)[
  #block(width: 100%, above: 1.1em, below: 0.8em)[
    #text(font: ("PingFang SC", "Heiti SC"), size: 11pt, weight: "bold", fill: rgb("#0f172a"))[{formatted_h4}]
  ]
]
""")
            i += 1
            continue
        elif stripped.startswith("##### "):
            section_list_counter = 0
            typ_lines.append(f"==== {stripped[6:].strip()}")
            i += 1
            continue

        # 图表说明文字 *图X-X 名称*
        if stripped.startswith("*图") and stripped.endswith("*"):
            fig_caption = stripped[1:-1]
            typ_lines.append(f"""
#v(-0.2em)
#align(center)[#text(font: ("PingFang SC", "Songti SC"), size: 9pt, style: "italic", fill: rgb("#475569"))[{fig_caption}]]
#v(0.4em)
""")
            i += 1
            continue

        # 独立公式块 $$ ... $$
        if stripped.startswith("$$"):
            math_indent = len(line) - len(line.lstrip())
            math_lines = []
            if stripped.endswith("$$") and len(stripped) > 2:
                math_lines.append(stripped[2:-2])
            else:
                i += 1
                while i < len(clean_lines) and not clean_lines[i].strip().endswith("$$"):
                    math_lines.append(clean_lines[i].strip())
                    i += 1
                if i < len(clean_lines):
                    tail = clean_lines[i].strip()[:-2]
                    if tail:
                        math_lines.append(tail)
            math_text = " ".join(math_lines)
            typ_math = convert_latex_math_to_typst(math_text)
            if math_indent >= 2:
                # 列表项内部的公式块：缩进 2 格输出，归属于当前列表项，避免打断列表
                typ_lines.append(f"  $ {typ_math} $")
            else:
                typ_lines.append(f"\n$ {typ_math} $\n")
            i += 1
            continue


        # 判断行首缩进深度，区分第一级与第二级
        indent = len(line) - len(line.lstrip())

        # =========================================================================
        # 1. 第二级列表与从属文本 (indent >= 2)
        # =========================================================================
        if indent >= 2:
            m_sub_num = re.match(r'^\d+\.\s+', stripped)
            m_sub_bullet = re.match(r'^[\*\-]\s+', stripped)
            if m_sub_num:
                # 第二级有序列表：对齐到段落首部，应用出版规范模式 A (1), (2), (3)
                item_body = stripped[len(m_sub_num.group(0)):].strip()
                # 检查下一行是否是公式块、代码块或更深缩进的子内容，或者是引出词
                next_is_child = (i + 1 < len(clean_lines)) and (
                    clean_lines[i+1].strip().startswith("$$") or 
                    clean_lines[i+1].strip().startswith("```") or
                    (len(clean_lines[i+1]) - len(clean_lines[i+1].lstrip()) > indent)
                )
                if not next_is_child and not re.search(r'(如下|包括|为|即)[：:]\s*$', item_body):
                    item_body = re.sub(r'[：:]\s*$', '', item_body)
                    item_body = re.sub(r'[：:](\*\*|__)\s*$', r'\1', item_body)
                formatted_item = format_inline_markdown(item_body)
                typ_lines.append(f"+ {formatted_item}")
                i += 1
                continue
            elif m_sub_bullet:
                # 第二级无序列表：对齐到段落首部
                item_body = re.sub(r'^[\*\-]\s+', '', stripped)
                next_is_child = (i + 1 < len(clean_lines)) and (
                    clean_lines[i+1].strip().startswith("$$") or 
                    clean_lines[i+1].strip().startswith("```") or
                    (len(clean_lines[i+1]) - len(clean_lines[i+1].lstrip()) > indent)
                )
                if not next_is_child and not re.search(r'(如下|包括|为|即)[：:]\s*$', item_body):
                    item_body = re.sub(r'[：:]\s*$', '', item_body)
                    item_body = re.sub(r'[：:](\*\*|__)\s*$', r'\1', item_body)
                formatted_item = format_inline_markdown(item_body)
                typ_lines.append(f"- {formatted_item}")
                i += 1
                continue
            else:
                # 从属正文段落
                p_formatted = format_inline_markdown(stripped)
                if indent > 2:
                    # 缩进深度大于列表项的文本：属于列表项内部的从属延续段落，首行不缩进，与列表文本垂直齐平对齐
                    typ_lines.append(f"  #par(first-line-indent: 0em)[{p_formatted}]")
                else:
                    # 普通从属正文段落（如成因分析说明或引导语）：作为标准段落渲染
                    typ_lines.append(p_formatted)
                i += 1
                continue

        # =========================================================================
        # =========================================================================
        # 2. 第一级列表 (indent < 2)：
        # =========================================================================
        is_unordered = re.match(r'^[\*\-]\s+', stripped)
        is_ordered = re.match(r'^\d+\.\s+', stripped)
        if is_unordered or is_ordered:
            body = re.sub(r'^([\*\-]|\d+\.)\s+', '', stripped)

            # 匹配加粗格式符、其后冒号与尾部文本
            m_bold = re.match(r'^(.*?)(\*\*|__)(.*?)\2\s*([：:])?\s*(.*)$', body)
            if m_bold:
                # 只有带加粗格式符的一级列表项，才升格为小节内带序号的小标题
                section_list_counter += 1
                num = section_list_counter
                prefix = m_bold.group(1).strip()
                title_core = m_bold.group(3).strip()
                tail = m_bold.group(5).strip()
                title_parts = [prefix, title_core] if prefix else [title_core]
                full_title = " ".join(title_parts)
                full_title = re.sub(r'[：:]\s*$', '', full_title)
                formatted_title = format_inline_markdown(full_title)

                # 第一级小标题：严格按 test_natural_spacing 规范输出独立加粗行与自然分段
                if typ_lines and typ_lines[-1] != "":
                    typ_lines.append("")
                typ_lines.append(f"#text(font: (\"Times New Roman\", \"PingFang SC\", \"Heiti SC\"), weight: \"bold\", fill: rgb(\"#0f172a\"))[{num}\\. {formatted_title}]")
                typ_lines.append("")
                # 加粗后冒号替换为换行，后面文本若非空则另起独立段落
                if tail:
                    typ_lines.append(format_inline_markdown(tail))
                    typ_lines.append("")
            else:
                # 不带加粗的普通列表项：严格保留原生 Markdown / Typst 列表语义
                if typ_lines and typ_lines[-1] != "" and not typ_lines[-1].startswith("- ") and not typ_lines[-1].startswith("+ "):
                    typ_lines.append("")
                if is_unordered:
                    typ_lines.append(f"- {format_inline_markdown(body)}")
                else:
                    typ_lines.append(f"+ {format_inline_markdown(body)}")
            i += 1
            continue

        # =========================================================================
        # 3. 独立 Markdown 图片语法 ![caption](path)
        # =========================================================================
        img_match = re.match(r'^\s*!\[(.*?)\]\((.*?)\)\s*$', stripped)
        if img_match:
            img_caption = img_match.group(1).strip()
            img_path = img_match.group(2).strip()

            # 针对官方微信公众号推介二维码，输出与教材出版流水线 100% 一致的高级出版级封底卡片
            if 'aiia_wechat_mp_qr' in img_path or 'wechat_mp_qr' in img_path:
                if typ_lines and typ_lines[-1].strip().startswith('#block(') and '深入人机协同' in typ_lines[-1]:
                    typ_lines.pop()

                native_promotion_card = f"""
#v(1.2em)
#align(center)[
  #block(
    width: 100%,
    fill: gradient.linear(rgb("#f0fdf4").lighten(70%), rgb("#ffffff"), rgb("#f8fafc"), angle: 135deg),
    radius: 18pt,
    inset: (x: 18pt, y: 26pt),
    stroke: 0.6pt + rgb("#e2e8f0"),
  )[
    // 1. 顶部胶囊药丸徽章
    #box(
      fill: rgb("#ecfdf5"),
      stroke: 0.8pt + rgb("#a7f3d0"),
      radius: 100pt,
      inset: (x: 14pt, y: 4.5pt),
    )[
      #text(font: ("PingFang SC", "Heiti SC"), size: 9pt, weight: "bold", fill: rgb("#059669"))[课外拓展 · 持续进阶]
    ]
    #v(8pt)
    
    // 2. 核心主标题
    #text(font: ("PingFang SC", "Heiti SC"), size: 14pt, weight: "bold", fill: rgb("#0f172a"))[深入人机协同 · 探索智能前沿]
    #v(2pt)
    
    // 3. 副标题 / 导语
    #text(font: ("PingFang SC", "Songti SC"), size: 9.5pt, fill: rgb("#64748b"))[获取最新 AI 动态与使用技巧]
    #v(18pt)
    
    // 4. 中部悬浮白底质感卡片
    #box(
      fill: rgb("#ffffff"),
      radius: 18pt,
      stroke: 0.8pt + rgb("#e2e8f0"),
      inset: (x: 22pt, top: 20pt, bottom: 16pt),
    )[
      // 二维码浅灰内衬
      #box(
        fill: rgb("#f8fafc"),
        radius: 12pt,
        inset: 10pt,
        stroke: 0.6pt + rgb("#f1f5f9"),
      )[
        #image("{img_path}", width: 112pt)
      ]
      #v(12pt)
      #box[
        #text(size: 9.5pt, weight: "bold", fill: rgb("#334155"))[
          #text(fill: rgb("#10b981"), size: 11pt)[●] 微信扫一扫 · 关注公众号
        ]
      ]
    ]
    #v(26pt)
    
    // 5. 底部署名与平台标识
    #grid(
      columns: (1fr, auto, 1fr),
      align: horizon,
      line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1")),
      pad(x: 10pt)[#text(size: 8.5pt, weight: "bold", fill: rgb("#64748b"))[南昌大学 AI 创新应用实验室]],
      line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1")),
    )
    #v(3pt)
    #text(font: ("Times New Roman", "Arial"), size: 7.5pt, tracking: 0.15em, fill: rgb("#94a3b8"))[NCU SMART COURSEWARE PLATFORM]
  ]
]
#v(1.0em)
"""
                typ_lines.append(native_promotion_card)
                i += 1
                continue
            caption_block = ""
            if img_caption:
                caption_block = f"""
  #v(-0.2em)
  #align(center)[#text(font: ("PingFang SC", "Songti SC"), size: 9pt, style: "italic", fill: rgb("#475569"))[{img_caption}]]
  #v(0.4em)
"""
            typ_lines.append(f"""
#block(width: 100%, breakable: false)[
  #align(center)[#block(width: 96%)[
    #figure(
      image("{img_path}", width: 92%)
    )
  ]]
  {caption_block}
]
""")
            i += 1
            continue

        # =========================================================================
        # 4. 普通正文段落
        # =========================================================================
        p_formatted = format_inline_markdown(stripped)
        typ_lines.append(p_formatted)
        i += 1


    if in_table:
        tbl_rendered = parse_markdown_table_to_typst("\n".join(table_buffer))
        if last_table_caption:
            typ_lines.append(f"""
#v(0.2em)
#align(center)[#text(font: ("PingFang SC", "Songti SC", "SimSun"), size: 9pt, style: "italic", fill: rgb("#475569"))[{last_table_caption}]]
#v(-0.1em)
{tbl_rendered}
#v(0.4em)
""")
        else:
            typ_lines.append(f"\n{tbl_rendered}\n")

    return "\n".join(typ_lines)

def main():
    parser = argparse.ArgumentParser(
        description="【单一事实源 (SSOT) 出版级 Typst/PDF 编译器】支持 A4 双面印刷册与自适应高清长图双模输出",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input", help="输入 SSOT Markdown 文件路径 (*.ssot.md 或 *.md)")
    parser.add_argument("output", nargs="?", default=None, help="目标输出文件路径 (.pdf, .typ, .png)")
    parser.add_argument("--mode", "-m", choices=["book", "long"], default=None, help="排版模式:\n  book: A4 双面印刷册 (默认)\n  long: 移动端自适应无缝高清长图")
    parser.add_argument("--long", "-l", action="store_true", help="快捷开关: 直接启用移动端自适应长图模式")
    parser.add_argument("--ppi", type=int, default=200, help="输出长图或预览图片的渲染像素密度 (默认: 200 PPI)")

    args = parser.parse_args()

    in_md = os.path.abspath(args.input)
    if not os.path.exists(in_md):
        print(f"❌ 错误: 找不到输入文件 {in_md}")
        sys.exit(1)

    # 确定编译模式
    mode = args.mode
    if args.long:
        mode = "long"
    elif mode is None:
        if args.output and args.output.lower().endswith(".png"):
            mode = "long"
        else:
            mode = "book"

    # 确定输出目标路径
    if args.output:
        out_target = os.path.abspath(args.output)
    else:
        if mode == "long":
            out_target = in_md.replace(".ssot.md", ".png").replace(".md", ".png")
        else:
            out_target = in_md.replace(".ssot.md", ".pdf").replace(".md", ".pdf")

    # 派生 typ 路径
    if out_target.endswith(".typ"):
        out_typ = out_target
    elif out_target.endswith(".pdf"):
        out_typ = out_target[:-4] + ".typ"
    elif out_target.endswith(".png"):
        out_typ = out_target[:-4] + ".typ"
    else:
        out_typ = out_target + ".typ"

    mode_label = "自适应无缝长图 (PNG)" if mode == "long" else "A4 双面出版册 (PDF)"
    print(f"📄 [SSOT-to-Typst] 正在解析: {in_md} (模式: {mode_label}) ...")
    typst_code = convert_ssot_to_typst(in_md, mode=mode)

    with open(out_typ, "w", encoding="utf-8") as f:
        f.write(typst_code)
    print(f"✍️  [SSOT-to-Typst] 已生成 Typst 源码: {out_typ}")

    try:
        root_dir = os.path.commonpath([os.path.abspath(out_typ), os.getcwd()])
    except Exception:
        root_dir = os.path.dirname(os.path.abspath(out_typ))

    if mode == "long":
        out_png = out_target if out_target.endswith(".png") else out_typ[:-4] + ".png"
        print(f"⚡ [SSOT-to-Typst] 正在调用 Typst 0.15 渲染自适应高清长图 ({args.ppi} PPI) ...")
        cmd = f"typst compile --root \"{root_dir}\" \"{out_typ}\" \"{out_png}\" --ppi {args.ppi}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if res.returncode != 0:
            print(f"❌ 渲染长图失败:\n{res.stderr}")
            sys.exit(1)

        file_size_kb = round(os.path.getsize(out_png) / 1024, 1)
        print(f"✅ [SSOT-to-Typst] 自适应无缝高清长图编译成功！")
        print(f"📦 产物路径: {out_png} ({file_size_kb} KB)")
    else:
        out_pdf = out_target if out_target.endswith(".pdf") else out_typ[:-4] + ".pdf"
        print(f"⚡ [SSOT-to-Typst] 正在调用 Typst 0.15 编译矢量 PDF ...")
        cmd = f"typst compile --root \"{root_dir}\" \"{out_typ}\" \"{out_pdf}\""
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if res.returncode != 0:
            print(f"❌ 编译失败:\n{res.stderr}")
            sys.exit(1)

        file_size_kb = round(os.path.getsize(out_pdf) / 1024, 1)
        print(f"✅ [SSOT-to-Typst] 出版级双面教材规范编译成功！")
        print(f"📦 产物路径: {out_pdf} ({file_size_kb} KB)")

if __name__ == "__main__":
    main()
