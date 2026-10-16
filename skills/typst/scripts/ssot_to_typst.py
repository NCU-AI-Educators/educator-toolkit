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
    "in", "notin", "subset", "supset", "approx", "equiv", "propto", "quad", "succ", "prec",
    "and", "or", "not", "times", "plus", "minus", "div", "star",
    "NN", "ZZ", "QQ", "RR", "CC", "infinity",
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "varkappa", "lambda", "mu", "nu", "xi",
    "omicron", "pi", "varpi", "rho", "varrho", "sigma", "varsigma", "tau", "upsilon",
    "phi", "varphi", "chi", "psi", "omega",
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota",
    "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau",
    "Upsilon", "Phi", "Chi", "Psi", "Omega",
    "underbrace", "overbrace", "underbracket", "overbracket",
    "forall", "exists", "scripts", "prime", "limits"
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

    # 清除 LaTeX 字号修饰宏（如 \Large, \large, \Huge, \small 等，Typst 数学环境中不适用）
    raw = re.sub(r'\\(?:tiny|scriptsize|footnotesize|small|normalsize|large|Large|LARGE|huge|Huge)\s*', '', raw)

    # 处理多行对齐环境 (aligned, align, split) 与换行符 \\ -> \
    raw = re.sub(r'\\begin\{(?:aligned|align\*?|split)\}', '', raw)
    raw = re.sub(r'\\end\{(?:aligned|align\*?|split)\}', '', raw)
    raw = re.sub(r'\\\\', ' \\ \n', raw)

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
    raw = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', raw)

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
        (r'\\succ(?![a-zA-Z])', 'succ'),
        (r'\\prec(?![a-zA-Z])', 'prec'),
        (r'\\lceil', 'ceil('),
        (r'\\rceil', ')'),
        (r'\\lfloor', 'floor('),
        (r'\\rfloor', ')'),
        (r'\\times(?![a-zA-Z])', 'times'),
        (r'\\cdot(?![a-zA-Z])', 'dot'),
        (r'\\pm(?![a-zA-Z])', 'plus.minus'),
        (r'\\in(?![a-zA-Z])', 'in'),
        (r'\\notin(?![a-zA-Z])', 'not in'),
        (r'\\subset(?![a-zA-Z])', 'subset'),
        (r'\\forall(?![a-zA-Z])', 'forall'),
        (r'\\exists(?![a-zA-Z])', 'exists'),
        (r'\\not\\longrightarrow(?![a-zA-Z])', 'arrow.r.not'),
        (r'\\notlongrightarrow(?![a-zA-Z])', 'arrow.r.not'),
        (r'\\not\\rightarrow(?![a-zA-Z])', 'arrow.r.not'),
        (r'\\not\\to(?![a-zA-Z])', 'arrow.r.not'),
        (r'\\Longleftrightarrow(?![a-zA-Z])', 'arrow.l.r.double'),
        (r'\\longleftrightarrow(?![a-zA-Z])', 'arrow.l.r.long'),
        (r'\\Leftrightarrow(?![a-zA-Z])', 'arrow.l.r.double'),
        (r'\\leftrightarrow(?![a-zA-Z])', 'arrow.l.r'),
        (r'\\iff(?![a-zA-Z])', 'arrow.l.r.double'),
        (r'\\implies(?![a-zA-Z])', 'arrow.r.double'),
        (r'\\impliedby(?![a-zA-Z])', 'arrow.l.double'),
        (r'\\longrightarrow(?![a-zA-Z])', 'arrow.r.long'),
        (r'\\longleftarrow(?![a-zA-Z])', 'arrow.l.long'),
        (r'\\Longrightarrow(?![a-zA-Z])', 'arrow.r.long.double'),
        (r'\\Longleftarrow(?![a-zA-Z])', 'arrow.l.long.double'),
        (r'\\to(?![a-zA-Z])', 'arrow.r'),
        (r'\\rightarrow(?![a-zA-Z])', 'arrow.r'),
        (r'\\leftarrow(?![a-zA-Z])', 'arrow.l'),
        (r'\\Rightarrow(?![a-zA-Z])', 'arrow.r.double'),
        (r'\\Leftarrow(?![a-zA-Z])', 'arrow.l.double'),
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
        (r'\\mid(?![a-zA-Z])', ' | '),
        (r'\\dots(?![a-zA-Z])', ' ... '),
        (r'\\cdots(?![a-zA-Z])', ' ... '),
        (r'\\ldots(?![a-zA-Z])', ' ... '),
        (r'\\oplus(?![a-zA-Z])', 'plus.o'),
        (r'\\otimes(?![a-zA-Z])', 'times.o'),
        (r'\\odot(?![a-zA-Z])', 'dot.o'),
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

    # 递归转换 LaTeX 下大括号/上大括号与脚本标注 \underbrace{A}_{B} / \overbrace{A}^{B} 为 Typst 原生语法
    def parse_under_over_brace(s: str) -> str:
        for cmd, typ_func in [
            (r'\underbrace', 'underbrace'),
            (r'\overbrace', 'overbrace'),
            (r'\underbracket', 'underbracket'),
            (r'\overbracket', 'overbracket')
        ]:
            while True:
                pos = s.find(cmd)
                if pos == -1:
                    break
                p1_start = s.find('{', pos + len(cmd))
                if p1_start == -1 or s[pos + len(cmd):p1_start].strip() != '':
                    break
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
                    break
                
                main_content = s[p1_start+1:p1_end]
                cur_idx = p1_end + 1
                while cur_idx < len(s) and s[cur_idx].isspace():
                    cur_idx += 1
                
                script_part = ""
                if cur_idx < len(s) and s[cur_idx] in ('_', '^'):
                    op = s[cur_idx]
                    p2_start = s.find('{', cur_idx + 1)
                    if p2_start != -1 and s[cur_idx + 1:p2_start].strip() == '':
                        depth = 0
                        p2_end = -1
                        for j in range(p2_start, len(s)):
                            if s[j] == '{': depth += 1
                            elif s[j] == '}':
                                depth -= 1
                                if depth == 0:
                                    p2_end = j
                                    break
                        if p2_end != -1:
                            sub_content = s[p2_start+1:p2_end]
                            script_part = f"{op}({sub_content})"
                            cur_idx = p2_end + 1
                
                if script_part:
                    replacement = f"limits({typ_func}({main_content})){script_part}"
                else:
                    replacement = f"{typ_func}({main_content})"
                s = s[:pos] + replacement + s[cur_idx:]
        return s

    raw = parse_under_over_brace(raw)

    def parse_xrightarrow(s: str) -> str:
        pattern = re.compile(r'\\xrightarrow(?:\[([^\]]*)\])?\{([^}]+)\}')
        def repl(m):
            sub = m.group(1)
            sup = m.group(2)
            if sub:
                return f"arrow.r.long^({sup})_({sub})"
            return f"arrow.r.long^({sup})"
        return pattern.sub(repl, s)

    raw = parse_xrightarrow(raw)
    raw = re.sub(r'\\prime(?![a-zA-Z])', 'prime', raw)
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
    text = text.replace("&nbsp;", "\u00a0")

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

    # 0.5 保护行内图片 ![alt](url) -> 转换为 Typst #image(...)
    inline_images = []
    def save_img(m):
        alt = m.group(1).strip()
        url = m.group(2).strip()
        inline_images.append((alt, url))
        return f"__INLINE_IMG_{len(inline_images)-1}__"
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', save_img, text)

    # 1. 保护行内链接（防止 URL 中的 ~ 或特殊字符被二次转义）
    links = []
    def save_link(m):
        l_text = m.group(1).strip()
        l_url = m.group(2).strip()
        links.append((l_text, l_url))
        return f"__INLINE_LINK_{len(links)-1}__"
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', save_link, text)

    def save_autolink(m):
        raw_url = m.group(1).strip()
        links.append((raw_url, raw_url))
        return f"__INLINE_LINK_{len(links)-1}__"
    text = re.sub(r'<(https?://[^>\s]+)>', save_autolink, text)
    text = re.sub(r'<(mailto:[^>\s]+)>', save_autolink, text)

    # 2. 支持删除线 ~~strike~~ -> #strike[strike]
    text = re.sub(r'~~(.*?)~~', r'#strike[\1]', text)

    # 3. 彻底解决 Typst 吞掉波浪号（~）问题：
    # Typst 在内容标记模式下将未转义半角波浪号 ~ 解释为不换行空格（non-breaking space, U+00A0），
    # 导致所有区间（如 9月15日 ~ 10月15日、10%~100%）、约数（如 ~5%）、编号（如 SRS-01 ~ SRS-10）等处的波浪号被吞掉不可见。
    # 将文本中所有未转义半角波浪号统一转义为 \~，使 Typst 100% 渲染为可见的半角波浪号
    text = re.sub(r'(?<!\\)~', r'\\~', text)

    text = text.replace("@", "\\@")

    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'#strong(emph[\1])', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'#strong[\1]', text)
    text = re.sub(r'\*(.*?)\*', r'#emph[\1]', text)

    # 清洗并转换 HTML 标签，防止 Typst 误识别为 <label>
    text = re.sub(r"<br\s*/?>", r" \\ ", text, flags=re.IGNORECASE)
    text = re.sub(r"<sub>(.*?)</sub>", r"#sub[\1]", text, flags=re.IGNORECASE)
    text = re.sub(r"<sup>(.*?)</sup>", r"#super[\1]", text, flags=re.IGNORECASE)
    text = re.sub(r"<b>(.*?)</b>", r"#strong[\1]", text, flags=re.IGNORECASE)
    text = re.sub(r"<i>(.*?)</i>", r"#emph[\1]", text, flags=re.IGNORECASE)
    text = re.sub(r"</?(?:div|span|p|center|sub|sup|font|em|strong|b|i)[^>]*>", "", text, flags=re.IGNORECASE)

    # 转义孤立的角括号与 HTML 实体，杜绝 Typst 将其误识别为未闭合标签（如 <8h、<10）
    text = text.replace("&lt;", "\\<").replace("&gt;", ">")
    text = re.sub(r"(?<!\\)<", r"\\<", text)

    # 恢复行内数学公式（确保公式内的 < 和数学符号不受文本级转义影响）
    for idx, math_typ in enumerate(maths):
        text = text.replace(f"__INLINE_MATH_{idx}__", f"${math_typ}$")

    # 4.5 支持 Markdown 脚注引用 [^id] -> #super[#link(<fn-id>)[#text(size: 0.82em, fill: rgb("#0369a1"))[[id]]]]
    def _fn_ref_repl(m):
        f_id = m.group(1)
        return f'#link(<fn-{f_id}>)[#super[#text(size: 0.82em, fill: rgb("#0369a1"))[[{f_id}]]]]'
    text = re.sub(r'\[\^([a-zA-Z0-9_\-]+)\]', _fn_ref_repl, text)

    # 4. 还原行内链接
    for idx, (l_text, l_url) in enumerate(links):
        l_text_clean = re.sub(r'(?<!\\)~', r'\\~', l_text)
        if l_url.startswith("http://") or l_url.startswith("https://") or l_url.startswith("mailto:"):
            link_expr = f'#link("{l_url}")[{l_text_clean}]'
        elif l_url.startswith("#"):
            anchor_id = re.sub(r'[^a-zA-Z0-9_\-]', '', l_url[1:])
            link_expr = f'#link(<{anchor_id}>)[{l_text_clean}]' if anchor_id else l_text_clean
        else:
            link_expr = f'#link("{l_url}")[{l_text_clean}]'
        text = text.replace(f"__INLINE_LINK_{idx}__", link_expr)

    for idx, code_str in enumerate(codes):
        text = text.replace(f"__INLINE_CODE_{idx}__", f'`{code_str}`')

    for idx, (alt, url) in enumerate(inline_images):
        img_expr = f'#box(width: 100%, inset: (top: 3pt, bottom: 3pt))[#image("{url}", width: 100%)]'
        text = text.replace(f"__INLINE_IMG_{idx}__", img_expr)

    # 修复加粗超链接嵌套导致的 Typst 语法回退: #strong#link(...) -> #link(...)[#strong[...]]
    text = re.sub(r'#strong#link\((.*?)\)\[\[(.*?)\]\]', r'#link(\1)[#strong[\2]]', text)
    return text

def estimate_text_visual_width(text: str) -> int:
    """估算单元格文本的单行最大视觉排版宽度（中文计2，英文数字计1，消除markdown语法与换行干扰）"""
    clean = re.sub(r'\*\*|__|\*|_|`', '', text)
    clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean)
    lines = re.split(r'<br\s*/?>|\n', clean)
    lines = [re.sub(r'<.*?>', ' ', l) for l in lines]
    max_w = 0
    for l in lines:
        w = sum(2 if ord(ch) > 127 else 1 for ch in l.strip())
        if w > max_w:
            max_w = w
    return max(max_w, 1)

def calculate_dynamic_col_spec(content_rows: list) -> str:
    """语义感知与密度自适应列宽分配算法 (智能混合 auto 与加权 fr)"""
    num_cols = len(content_rows[0])
    if num_cols <= 1:
        return "(1fr,)"
    
    col_info = []
    for c in range(num_cols):
        h_text = content_rows[0][c].strip()
        h_w = estimate_text_visual_width(h_text)
        data_cells = [content_rows[r][c].strip() for r in range(1, len(content_rows)) if len(content_rows[r]) > c]
        
        # 单元格单行最大视觉宽度（已按 <br> 切分）
        max_line_w = max([estimate_text_visual_width(cell) for cell in data_cells] + [h_w])
        # 单元格纯文本总字符数最大值（未切分前）
        max_raw_len = max([len(re.sub(r"<.*?>|\*|_|`", "", cell)) for cell in data_cells] + [len(h_text)])
        # 是否包含长叙述段落或标点句号
        has_paragraph = any(len(re.sub(r"<.*?>|\*|_|`", "", cell)) > 35 or "。" in cell for cell in data_cells)
        
        # 明确紧凑型特征：序号、短编号、起止日期、纯金额数字、紧凑标签
        is_index = any(k in h_text for k in ["序号", "编号", "ID", "No"]) or (max_raw_len <= 4 and max_line_w <= 6)
        is_date = any(k in h_text for k in ["起止时间", "时间", "日期"]) and max_line_w <= 20
        is_currency = any(k in h_text for k in ["金额", "资金", "预算"]) and max_line_w <= 14 and not has_paragraph
        is_short_label = max_line_w <= 24 and max_raw_len <= 32 and not has_paragraph
        is_compact = is_index or is_date or is_currency or (is_short_label and not has_paragraph)
        
        col_info.append({
            "col": c,
            "header": h_text,
            "max_line_w": max_line_w,
            "max_raw_len": max_raw_len,
            "has_paragraph": has_paragraph,
            "is_compact": is_compact
        })
    
    compact_count = sum(1 for ci in col_info if ci["is_compact"])
    fluid_count = num_cols - compact_count
    
    # 策略 1: 仅有 1 列长叙述列，其他均为紧凑列（如表 1、表 4、表 6、表 7）
    # 紧凑列全部 auto，唯一的长叙述列独享 1fr，彻底杜绝紧凑列留白浪费与叙述列挤压
    if fluid_count == 1:
        specs = []
        for ci in col_info:
            if ci["is_compact"]:
                specs.append("auto")
            else:
                specs.append("1fr")
        return f"({', '.join(specs)})"
    
    # 策略 2: 存在多个流式列（如表 2、表 3、表 5、表 8）
    # 对于极紧凑列（如序号、单字影响度）依然采用 auto，其余流式列按真实内容体量非线性分配加权 fr
    fr_scores = []
    for ci in col_info:
        if ci["is_compact"] and ci["max_raw_len"] <= 10:
            fr_scores.append(None) # auto
        else:
            c = ci["col"]
            data_widths = [estimate_text_visual_width(content_rows[r][c]) for r in range(1, len(content_rows)) if len(content_rows[r]) > c and content_rows[r][c].strip()]
            avg_w = sum(data_widths) / len(data_widths) if data_widths else ci["max_line_w"]
            score = max(ci["max_line_w"] * 0.8, avg_w * 0.6 + ci["max_raw_len"] * 0.4)
            fr_scores.append(score)
    
    active_scores = [s for s in fr_scores if s is not None]
    if not active_scores:
        return f"({', '.join(['1fr']*num_cols)})"
    
    min_score = min(active_scores)
    smoothed = [((s / min_score) ** 0.55) if s is not None else None for s in fr_scores]
    
    specs = []
    for sm in smoothed:
        if sm is None:
            specs.append("auto")
        else:
            val = round(max(sm, 1.0), 2)
            specs.append(f"{val:g}fr")
            
    return f"({', '.join(specs)})"

def parse_markdown_table_to_typst(table_text: str, caption: str = None, breakable: bool = None, compact: bool = False) -> str:
    """符合调优标准的科技三线表（带表头双线、无缩进单元格，标题整合于 table.header 彻底杜绝标题分离与伪分页）"""
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

    md_col_align = []
    content_rows = []
    for r in rows:
        if all(re.match(r"^:?-+:?$", c.strip()) for c in r if c.strip()):
            for c in r:
                c_s = c.strip()
                if c_s.startswith(":") and c_s.endswith(":"):
                    md_col_align.append("center")
                elif c_s.endswith(":"):
                    md_col_align.append("right")
                elif c_s.startswith(":"):
                    md_col_align.append("left")
                else:
                    md_col_align.append("auto")
            continue
        content_rows.append(r)

    if not content_rows:
        return ""

    def _get_cell_span(cell_str: str):
        m = re.match(r'^(?:<td\s+colspan=["\']?(\d+)["\']?>|colspan=(\d+):?)\s*(.*?)(?:</td>)?$', cell_str.strip(), re.I | re.S)
        if m:
            return int(m.group(1) or m.group(2)), m.group(3).strip()
        return 1, cell_str.strip()

    num_cols = max(sum(_get_cell_span(c)[0] for c in r) for r in content_rows)
    for r in content_rows:
        cur_span = sum(_get_cell_span(c)[0] for c in r)
        while cur_span < num_cols:
            r.append("")
            cur_span += 1
    while len(md_col_align) < num_cols:
        md_col_align.append("auto")

    # 语义感知与财务规范智能对齐推断
    col_aligns = []
    header_aligns = []
    for c in range(num_cols):
        h_text = content_rows[0][c].strip()
        data_cells = [content_rows[r][c].strip() for r in range(1, len(content_rows)) if len(content_rows[r]) > c and content_rows[r][c].strip()]
        explicit = md_col_align[c]
        
        # 1. 优先遵循 Markdown 显式右对齐
        if explicit == "right":
            col_aligns.append("right")
            header_aligns.append("center")
            continue
            
        # 2. 数字/金额/货币列智能识别 (财务规范：一律右对齐以保持小数点垂直对齐)
        is_pure_num = lambda cell: bool(re.match(r"^[+-]?\s*[\$¥￥]?\s*[\d,]+(?:\.\d+)?%?\s*$", re.sub(r"<.*?>|\*|_|`", "", cell).strip()))
        num_count = sum(1 for cell in data_cells if is_pure_num(cell))
        is_mostly_num = len(data_cells) > 0 and (num_count / len(data_cells) >= 0.6)
        has_currency_kw = any(kw in h_text for kw in ["金额", "资金", "单价", "总价", "支出", "产值"]) and not any(kw in h_text for kw in ["名称", "科目", "类别", "说明", "依据", "渠道"])
        
        if (has_currency_kw and any(is_pure_num(cell) for cell in data_cells)) or is_mostly_num:
            col_aligns.append("right")
            header_aligns.append("center")
            continue
            
        # 3. 序号、纯编码、起止日期、单字标签等居中识别
        is_index = any(kw in h_text for kw in ["序号", "编号", "ID", "No", "阶段"])
        is_date = any(kw in h_text for kw in ["起止时间", "时间", "日期"]) and all(len(re.sub(r"<.*?>|\*|_|`", "", cell)) <= 20 for cell in data_cells)
        is_short_tag = (len(h_text) <= 5) and all(len(re.sub(r"<.*?>|\*|_|`", "", cell)) <= 6 for cell in data_cells) and not any(kw in h_text for kw in ["名称", "要素", "属性", "科目"])
        
        if explicit == "center" or is_index or is_date or is_short_tag:
            col_aligns.append("center")
            header_aligns.append("center")
            continue
            
        # 4. 其余文本一律左对齐
        col_aligns.append("left")
        header_aligns.append("center")

    # 构建 Typst align 规则表达式
    h_branches = "".join([f"if col == {c} {{ {header_aligns[c]} + horizon }} else " for c in range(num_cols) if header_aligns[c] != "center"])
    d_branches = "".join([f"if col == {c} {{ {col_aligns[c]} + horizon }} else " for c in range(num_cols) if col_aligns[c] != "left"])
    h_code = f"{h_branches}{{ center + horizon }}" if h_branches else "center + horizon"
    d_code = f"{d_branches}{{ left + horizon }}" if d_branches else "left + horizon"

    if caption:
        align_code = f"""    align: (col, row) => {{
      if row == 0 {{
        center + horizon
      }} else if row == 1 {{
        {h_code}
      }} else {{
        {d_code}
      }}
    }},"""
    else:
        align_code = f"""    align: (col, row) => {{
      if row == 0 {{
        {h_code}
      }} else {{
        {d_code}
      }}
    }},"""

    # 内容感知自适应列宽分配
    col_spec = calculate_dynamic_col_spec(content_rows)
    num_rows = len(content_rows)

    if caption:
        stroke_code = f"    stroke: (x, y) => if y == 0 {{ none }} else if y == 1 {{ (top: 1.2pt + rgb(\"#0f172a\"), bottom: 0.8pt + rgb(\"#0f172a\")) }} else if y == {num_rows} {{ (bottom: 1.2pt + rgb(\"#0f172a\")) }} else {{ (bottom: 0.5pt + rgb(\"#e2e8f0\")) }},"
        fill_code = "    fill: (col, row) => if row == 1 { rgb(\"#f1f5f9\") } else { none },"
    else:
        if num_rows == 1:
            stroke_code = "    stroke: (x, y) => if y == 0 { (top: 1.2pt + rgb(\"#0f172a\"), bottom: 1.2pt + rgb(\"#0f172a\")) },"
        else:
            stroke_code = f"    stroke: (x, y) => if y == 0 {{ (top: 1.2pt + rgb(\"#0f172a\"), bottom: 0.8pt + rgb(\"#0f172a\")) }} else if y == {num_rows - 1} {{ (bottom: 1.2pt + rgb(\"#0f172a\")) }} else {{ (bottom: 0.5pt + rgb(\"#e2e8f0\")) }},"
        fill_code = "    fill: (col, row) => if row == 0 { rgb(\"#f1f5f9\") } else { none },"
    if compact:
        inset_code = "    inset: (x: 5.5pt, y: 3.2pt),"
    else:
        inset_code = "    inset: (x: 5.5pt, y: 5pt)," if num_cols >= 5 else "    inset: (x: 7pt, y: 5pt),"
    if breakable is not None:
        breakable_val = "true" if breakable else "false"
    else:
        breakable_val = "true"
    typ_table = [
        f"#align(center)[#block(width: 100%, breakable: {breakable_val})[",
        "  #show table.cell: set par(justify: false, first-line-indent: (amount: 0em, all: true))",
    ]
    if compact:
        typ_table.append("  #show table.cell: set text(size: 9.2pt)")
    typ_table.extend([
        f"  #table(",
        f"    columns: {col_spec},",
        fill_code,
        stroke_code,
        inset_code,
        align_code,
        "    table.header(",
    ])

    if caption:
        typ_table.append(f"""      table.cell(colspan: {num_cols}, stroke: none)[
        #v(0.2em)
        #align(center)[#text(font: ("PingFang SC", "Songti SC", "SimSun"), size: 9pt, style: "italic", fill: rgb("#475569"))[{caption}]]
        #v(0.1em)
      ],""")

    for col in content_rows[0]:
        cell_formatted = format_inline_markdown(col)
        cell_formatted = cell_formatted.replace("<br>", " \\\n").replace("<br/>", " \\\n")
        typ_table.append(f"      table.cell[#set par(first-line-indent: (amount: 0em, all: true)); #strong[{cell_formatted}]],")
    typ_table.append("    ),")

    for row_idx, row in enumerate(content_rows[1:], start=1):
        typ_table.append(f"    // Row {row_idx}")
        for col in row:
            span, clean_col = _get_cell_span(col)
            cell_formatted = format_inline_markdown(clean_col)
            cell_formatted = cell_formatted.replace("<br>", " \\\n").replace("<br/>", " \\\n")
            if span > 1:
                typ_table.append(f"    table.cell(colspan: {span})[#set par(first-line-indent: (amount: 0em, all: true)); {cell_formatted}],")
            else:
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
        'document_id': '',
        'classification': '',
        'author': '',
        'institution': '',
        'date': '2026年9月',
        'abstract': '',
        'keywords': '',
    }

    body = content
    has_frontmatter = False
    raw_frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                parsed_yaml = yaml.safe_load(parts[1])
                if isinstance(parsed_yaml, dict):
                    raw_frontmatter = parsed_yaml
                    metadata.update(parsed_yaml)
                    has_frontmatter = True
                    if '摘要' in metadata and not metadata.get('abstract'):
                        metadata['abstract'] = metadata['摘要']
                    if '关键词' in metadata and not metadata.get('keywords'):
                        metadata['keywords'] = metadata['关键词']
            except Exception as e:
                print(f"Warning: YAML parse error: {e}")
            body = parts[2]

    # 密级保底净化：若包含体裁后缀则自动剔除
    if "/" in str(metadata.get("classification", "")):
        metadata["classification"] = metadata["classification"].split("/")[0].strip()
    def is_section_heading(text: str) -> bool:
        t = text.strip()
        if re.match(r'^\d+(?:\.\d+)*[、. ]', t) or re.match(r'^\d+[、. ]', t):
            return True
        if re.match(r'^[一二三四五六七八九十百]+[、. ]', t):
            return True
        if re.match(r'^[（(][一二三四五六七八九十\d]+[)）]', t):
            return True
        if re.match(r'^第[一二三四五六七八九十\d]+[章节条部分篇卷讲课节]', t):
            return True
        if re.match(r'^(?:附录|引言|前言|概述|总结|结语|参考文献)(?:[、. ]|$)', t):
            return True
        return False

    body_lines = body.split("\n")
    clean_lines = []
    has_removed_h1 = False
    has_removed_subtitle = False
    seen_content_after_h1 = False
    in_cb = False
    for l in body_lines:
        stripped = l.strip()
        if stripped.startswith("```"):
            in_cb = not in_cb
        if not in_cb and not has_removed_h1 and stripped.startswith("# ") and not stripped.startswith("## "):
            has_removed_h1 = True
            extracted_title = stripped[2:].strip()
            if extracted_title and (not has_frontmatter or metadata.get('title') in ('', '技术工程设计基准')):
                metadata['title'] = extracted_title
            continue
        # 仅在尚未出现任何正文内容、未提供 Frontmatter 或显式匹配 subtitle，且非章节编号时，才将紧随 H1 的 ## 识别为副标题剥离
        if not in_cb and has_removed_h1 and not has_removed_subtitle and not seen_content_after_h1 and stripped.startswith("## "):
            extracted_sub = stripped[3:].strip()
            if not is_section_heading(extracted_sub) and (extracted_sub == metadata.get("subtitle") or (not has_frontmatter and not metadata.get("subtitle"))):
                has_removed_subtitle = True
                if not metadata.get("subtitle"):
                    metadata["subtitle"] = extracted_sub
                continue
            else:
                seen_content_after_h1 = True
        elif not in_cb and has_removed_h1 and stripped and not stripped.startswith("<!--"):
            seen_content_after_h1 = True

        clean_lines.append(l)

    # 智能启发式元数据提取：当未提供 Frontmatter 时，尝试从 H1 下方的元数据键值行中自适应提取
    preamble_meta = {}
    for l in clean_lines:
        stripped_l = l.strip()
        if not stripped_l:
            continue
        if stripped_l.startswith("## ") or stripped_l.startswith("# ") or stripped_l == "---":
            break
        if stripped_l.startswith(">"):
            stripped_l = stripped_l[1:].strip()
        m_kv = re.match(r'^(?:[-*•]\s*)?\*\*([^\*：:]+)\*\*[：:]\s*(.*)', stripped_l)
        if m_kv:
            k_name = m_kv.group(1).strip()
            v_val = m_kv.group(2).strip()
            preamble_meta[k_name] = v_val

    if preamble_meta:
        if ('所属中心' in preamble_meta or '中心' in preamble_meta) and not metadata.get('institution'):
            metadata['institution'] = preamble_meta.get('所属中心') or preamble_meta.get('中心')
        elif '牵头申报单位' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['牵头申报单位']
        elif '研发机构' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['研发机构']
        elif '编制单位' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['编制单位']
        elif '方案起草' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['方案起草']
        elif '起草单位' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['起草单位']
        elif '指导机构' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['指导机构']
        elif '评阅机构' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['评阅机构']
        elif '研制机构' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['研制机构']
        elif '机构' in preamble_meta and not metadata.get('institution'):
            metadata['institution'] = preamble_meta['机构']

        if '编制日期' in preamble_meta:
            metadata['date'] = preamble_meta['编制日期']
        elif '日期' in preamble_meta:
            metadata['date'] = preamble_meta['日期']

        if '联合申报单位' in preamble_meta and not metadata.get('author'):
            lead = preamble_meta.get('牵头申报单位', '')
            sub = preamble_meta.get('联合申报单位', '')
            metadata['author'] = f'{lead} · {sub}' if lead else sub
        elif '项目负责人' in preamble_meta and not metadata.get('author'):
            metadata['author'] = preamble_meta['项目负责人']
        elif '编制团队' in preamble_meta and not metadata.get('author'):
            metadata['author'] = preamble_meta['编制团队']
        elif '评阅人' in preamble_meta and not metadata.get('author'):
            metadata['author'] = preamble_meta['评阅人']
        elif '指导人' in preamble_meta and not metadata.get('author'):
            metadata['author'] = preamble_meta['指导人']

        if '申报指南' in preamble_meta and not metadata.get('document_id'):
            metadata['document_id'] = preamble_meta['申报指南']
        elif '文档编号' in preamble_meta and not metadata.get('document_id'):
            metadata['document_id'] = preamble_meta['文档编号']
        elif '项目编号' in preamble_meta and not metadata.get('document_id'):
            metadata['document_id'] = preamble_meta['项目编号']

        if '项目类别' in preamble_meta and not metadata.get('classification'):
            metadata['classification'] = preamble_meta['项目类别']
        elif '密级' in preamble_meta and not metadata.get('classification'):
            metadata['classification'] = preamble_meta['密级']

        if '实施周期' in preamble_meta and not metadata.get('date'):
            metadata['date'] = preamble_meta['实施周期'].split('（')[0].strip()

    # --------------------------------------------------------------------------
    # 彻底解耦语义与程序代码：元数据标签支持 Frontmatter 显式定义与体裁自适应体系
    # 优先级 1: Frontmatter 显式自定义标签 (labels 字典 或 label_* 平铺键)
    # 优先级 2: Frontmatter 显式体裁声明 (doc_type / genre)
    # 优先级 3: 精准无歧义的语义启发式回退 (杜绝“实验室”等模糊关键字误判)
    # --------------------------------------------------------------------------
    custom_labels = raw_frontmatter.get("labels", {})
    if not isinstance(custom_labels, dict):
        custom_labels = {}

    # 兼容平铺写法：如 label_author, label_doc_id, label_institution 等
    for k in ["author", "institution", "date", "document_id", "doc_id", "classification"]:
        if f"label_{k}" in raw_frontmatter and k not in custom_labels:
            custom_labels[k] = str(raw_frontmatter[f"label_{k}"])
    if "doc_id" in custom_labels and "document_id" not in custom_labels:
        custom_labels["document_id"] = custom_labels["doc_id"]

    # 预设体裁配置字典
    GENRE_PRESETS = {
        "course": {
            "author": "编 写 团 队",
            "institution": "开 课 单 位",
            "date": "编 制 日 期",
            "document_id": "课程编号",
            "classification": "使用范围",
            "default_author": "《人机协同程序设计》教学团队" if "人机协同" in metadata.get('title', '') else "课程教学团队",
            "default_institution": "南昌大学",
        },
        "spec": {
            "author": "编 制 团 队",
            "institution": "研 发 机 构",
            "date": "编 制 日 期",
            "document_id": "文档编号",
            "classification": "受控密级",
            "default_author": "系统架构委员会",
            "default_institution": "",
        },
        "report": {
            "author": "报 告 团 队",
            "institution": "编 制 单 位",
            "date": "报 告 日 期",
            "document_id": "报告编号",
            "classification": "受控密级",
            "default_author": "项目申报团队",
            "default_institution": "",
        },
    }

    # 获取显式 doc_type / genre
    raw_doc_type = str(raw_frontmatter.get("doc_type") or raw_frontmatter.get("genre") or "").strip().lower()
    if raw_doc_type in ["course", "syllabus", "lecture", "teaching"]:
        matched_genre = "course"
    elif raw_doc_type in ["spec", "srs", "tdd", "specification", "engineering", "tech", "architecture", "standard"]:
        matched_genre = "spec"
    elif raw_doc_type in ["report", "tr", "feasibility", "survey"]:
        matched_genre = "report"
    else:
        # 回退启发式：严谨判断，绝不使用单一模糊词（如“实验”）误判
        title_str = str(metadata.get('title', ''))
        file_base = os.path.basename(md_path)
        
        has_course_prop = "course" in raw_frontmatter
        is_syllabus_or_lecture = (
            any(k in title_str or k in file_base for k in ["教学大纲", "课程大纲", "讲义", "反思日志"]) or
            (file_base.startswith("第") and "讲" in file_base)
        )

        if has_course_prop or is_syllabus_or_lecture:
            matched_genre = "course"
        elif any(k in title_str or k in file_base for k in ["可行性", "论证", "调研", "报告", "-TR-"]):
            matched_genre = "report"
        else:
            matched_genre = "spec"

    preset = GENRE_PRESETS[matched_genre]

    # 解析最终各 Label（Frontmatter 显式定义拥有绝对最高优先级）
    label_author = custom_labels.get("author") or preset["author"]
    label_institution = custom_labels.get("institution") or preset["institution"]
    label_date = custom_labels.get("date") or preset["date"]
    label_doc_id = custom_labels.get("document_id") or preset["document_id"]
    label_classification = custom_labels.get("classification") or preset["classification"]

    # 缺省值填充
    if not metadata.get('author'):
        metadata['author'] = preset["default_author"]
    if not metadata.get('institution'):
        metadata['institution'] = preset["default_institution"]
    if not metadata.get('institution') and ('AIIA_Lab' in os.path.abspath(md_path) or 'AIIA_Lab' in os.getcwd()):
        metadata['institution'] = '南昌大学AI创新应用实验室（AIIA Lab@NCU）' 

    has_doc_id = bool(raw_frontmatter.get("document_id"))
    has_classification = bool(raw_frontmatter.get("classification"))

    # 偶数页右侧页眉与页脚受控信息动态计算
    doc_id_val = metadata.get('document_id', '')
    inst_val = metadata.get('institution', '')
    class_val = metadata.get('classification', '')

    subtitle_val = metadata.get('subtitle', '')
    if subtitle_val:
        even_header_right = f'text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{subtitle_val.replace("@", chr(92) + "@")}]'
    elif has_doc_id:
        even_header_right = f'text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{label_doc_id}：#text(fill: rgb("#0369a1"), weight: "bold")[#raw("{doc_id_val}")]]'
    elif matched_genre == "course":
        course_name = metadata.get("course") or ("《人机协同程序设计》" if "人机协同" in metadata.get('title', '') else "通识课程")
        even_header_right = f'text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[南昌大学 · {course_name}]'
    elif inst_val:
        even_header_right = f'text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{inst_val.replace("@", chr(92) + "@")}]'
    else:
        even_header_right = f'text(size: 8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{metadata.get("title", "").replace("@", chr(92) + "@")}]'

    if has_classification:
        if inst_val:
            footer_left = f'#text("{inst_val}") · #text(fill: rgb("#0f172a"), weight: "medium")[{class_val}]'
        else:
            footer_left = f'#text(fill: rgb("#0f172a"), weight: "medium")[{class_val}]'
    elif matched_genre == "course":
        # 教材/课程模式：页脚严格展示编写团队 (author)，绝不使用开课单位
        author_val = metadata.get('author', '')
        footer_left = f'#text("{author_val}")' if author_val else '#text("")'
    else:
        footer_left = f'#text("{inst_val}")' if inst_val else '#text("")'
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
        {even_header_right}
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
            {footer_left}
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
  full: true,
  numbering: (..args) => {{
    let pos = args.pos()
    if pos.len() == 1 {{
      str(pos.first()) + "."
    }} else {{
      "(" + str(pos.last()) + ")"
    }}
  }}
)
#show list: set block(above: 0.85em, below: 0.85em)
#show enum: set block(above: 0.85em, below: 0.85em)

// 列表首行对齐：第一级统一缩进 2em，子列表由 Typst 原生语法自然对齐// 列表首行对齐：第一级统一缩进 2em，子列表由 Typst 原生语法自然对齐""")

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
// 简单朴素出版级目录排版系统 (标准学术规约，端正自然，一级章目加粗与呼吸感微间距)
#set outline(indent: 1.5em)
#show outline.entry.where(level: 1): it => {{
  v(0.85em)
  text(weight: "bold", fill: rgb("#0f172a"))[#it]
}}
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
  #set text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 11pt, weight: "bold", fill: rgb("#0369a1"))
  #it.body
]

#show heading.where(level: 4): it => block(width: 100%, above: 1.0em, below: 0.6em)[
  #set text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 10.5pt, weight: "bold", fill: rgb("#0f172a"))
  #it.body
]

// 5 级标题专用于具名锚点（如参考文献、词条等），不增加额外间距，完全继承正文排版，且不计入目录大纲
#show heading.where(level: 5): it => block(spacing: 0.7em)[#it.body]

// 核心大标题与元数据
#align(center)[
  #block(width: 100%)[
    #text(font: ("PingFang SC", "Heiti SC"), size: 18pt, weight: "bold", fill: rgb("#0f172a"))[{metadata['title']}]
""")

    if metadata.get('subtitle'):
        typ_lines.append(f"""    #v(3pt)
    #text(font: ("PingFang SC", "Heiti SC"), size: 11.5pt, fill: rgb("#475569"))[{format_inline_markdown(metadata['subtitle'])}]
""")

    if not has_frontmatter:
        # 无 frontmatter 文档（如随堂练习、学生反思日志、作业模板等）：不渲染工业元数据表格，仅输出雅致底线
        typ_lines.append("""    #v(8pt)
    #line(length: 100%, stroke: 1.2pt + rgb("#0f172a"))
  ]
]
#v(6pt)
""")
    else:
        # 显式声明 frontmatter 的正式规范/大纲/讲义：渲染自适应元数据台
        typ_lines.append(f"""    #v(10pt)
    #line(length: 100%, stroke: 0.8pt + rgb("#cbd5e1"))
    #v(4pt)
    #grid(
      columns: (2.3fr, 2.3fr, 1fr),
      column-gutter: 14pt,
      row-gutter: 5pt,
      align(left)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{label_author}]],
      align(left)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{label_institution}]],
      align(right)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{label_date}]],
      
      align(left)[#text(9pt, weight: "medium", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[{formatted_author}]],
      align(left)[#text(9pt, weight: "medium", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[{formatted_inst}]],
      align(right)[#text(9pt, weight: "medium", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[{metadata['date']}]]
    )
""")
        if has_doc_id and has_classification:
            typ_lines.append(f"""    #v(6pt)
    #grid(
      columns: (1.2fr, 1fr),
      align(left)[#text(8.5pt, fill: rgb("#0369a1"), weight: "bold", font: ("PingFang SC", "Heiti SC"))[{label_doc_id}：#raw("{metadata['document_id']}") ]],
      align(right)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{label_classification}：#text(fill: rgb("#0f172a"), weight: "medium")[{metadata['classification']}]]]
    )
""")
        elif has_doc_id:
            typ_lines.append(f"""    #v(6pt)
    #align(left)[#text(8.5pt, fill: rgb("#0369a1"), weight: "bold", font: ("PingFang SC", "Heiti SC"))[{label_doc_id}：#raw("{metadata['document_id']}") ]]
""")
        elif has_classification:
            typ_lines.append(f"""    #v(6pt)
    #align(right)[#text(8.5pt, fill: rgb("#64748b"), font: ("PingFang SC", "Heiti SC"))[{label_classification}：#text(fill: rgb("#0f172a"), weight: "medium")[{metadata['classification']}]]]
""")
        typ_lines.append("""    #v(6pt)
    #line(length: 100%, stroke: 1.2pt + rgb("#0f172a"))
  ]
]
#v(6pt)

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
  #text(weight: "bold", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[【摘　要】] #text(fill: rgb("#334155"))[{format_inline_markdown(metadata['abstract'])}]
""")
        if metadata.get('keywords'):
            typ_lines.append(f"""  #v(4pt)
  #text(weight: "bold", fill: rgb("#0f172a"), font: ("PingFang SC", "Heiti SC"))[【关键词】] #text(fill: rgb("#0369a1"))[{format_inline_markdown(metadata['keywords'])}]
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
    next_landscape = False
    next_landscape_isolated = False
    next_table_landscape = False
    next_table_portrait = False
    next_table_breakable = None
    next_table_compact = False
    in_landscape_block = False
    ref_buffer = []

    def flush_references():
        nonlocal ref_buffer
        if not ref_buffer:
            return
        max_len = max(len(id_str) for id_str, _ in ref_buffer)
        col1_w = f"{max(2.2, 1.2 + max_len * 0.55):.1f}em"
        grid_cells = []
        for fn_id, fn_body in ref_buffer:
            grid_cells.append(f'  [#align(right + top)[#text(weight: "bold", fill: rgb("#0369a1"))[[{fn_id}]] <fn-{fn_id}>]], [{fn_body}],')
        cells_str = chr(10).join(grid_cells)
        typ_lines.append(f"""
#v(0.3em)
#grid(
  columns: ({col1_w}, 1fr),
  column-gutter: 0.6em,
  row-gutter: 0.75em,
  align: (right + top, left + top),
{cells_str}
)
#v(0.5em)
""")
        ref_buffer = []

    def try_absorb_preceding_header(buffer):
        """
        智能回溯检查：如果横向图/宽表格紧邻前置内容仅为 1~2 个标题和一段简短图前引言（<= 120字），
        自动将其吸纳合并移入当前横向页顶部展示，彻底消除前一页仅有少量内容的空白残页。
        """
        idx = len(buffer) - 1
        while idx >= 0 and not buffer[idx].strip():
            idx -= 1
        if idx < 0:
            return None

        collected_indices = []

        # 阶段 1：尾部可选的短引导段落（最多 1 个段落，不能是列表、代码、表格）
        curr = idx
        tail_chunk = buffer[curr].strip()
        is_heading = bool(re.match(r"^\s*={1,4}\s+", tail_chunk) or tail_chunk.startswith("#heading"))

        if not is_heading:
            if any(bad in tail_chunk for bad in ["#table", "#figure", "#image", "#block", "```", "- ", "+ ", "#list", "#enum"]):
                return None
            if len(tail_chunk) > 120:
                return None
            collected_indices.append(curr)
            curr -= 1
            while curr >= 0 and not buffer[curr].strip():
                collected_indices.append(curr)
                curr -= 1

        # 阶段 2：向上收集紧邻的 1~2 个小节或大章节标题
        heading_count = 0
        while curr >= 0:
            c = buffer[curr].strip()
            if not c:
                collected_indices.append(curr)
                curr -= 1
                continue
            if re.match(r"^\s*={1,4}\s+", c) or c.startswith("#heading"):
                heading_count += 1
                collected_indices.append(curr)
                curr -= 1
                if heading_count >= 2:
                    break
            else:
                break

        if heading_count == 0:
            return None

        # 阶段 3：如果标题上方紧邻 #pagebreak，则一并清理以彻底消灭前一页残页
        min_idx = min(collected_indices)
        prev = min_idx - 1
        while prev >= 0 and not buffer[prev].strip():
            prev -= 1
        remove_start = min_idx
        if prev >= 0 and ("#pagebreak" in buffer[prev] or buffer[prev].strip().startswith("#pagebreak")):
            remove_start = prev

        extracted_chunks = [buffer[k] for k in sorted(collected_indices) if buffer[k].strip() and not buffer[k].strip().startswith("#pagebreak")]
        del buffer[remove_start:]
        return "\n\n".join(extracted_chunks)

    def flush_table():
        nonlocal in_table, table_buffer, last_table_caption
        nonlocal next_table_landscape, next_table_portrait, next_landscape, next_landscape_isolated, next_table_breakable, next_table_compact
        if not in_table or not table_buffer:
            in_table = False
            table_buffer = []
            return

        table_str = "\n".join(table_buffer)
        tbl_rendered = parse_markdown_table_to_typst(table_str, caption=last_table_caption, breakable=next_table_breakable, compact=next_table_compact)
        if not tbl_rendered:
            in_table = False
            table_buffer = []
            next_table_breakable = None
            next_table_compact = False
            return

        # 计算表格真实最大列数
        num_cols = 0
        for l in table_buffer:
            l_clean = l.strip()
            if l_clean.startswith("|"):
                l_clean = l_clean[1:]
            if l_clean.endswith("|"):
                l_clean = l_clean[:-1]
            cols = [c.strip() for c in l_clean.split("|")]
            if not all(re.match(r'^:?-+:?$', c) for c in cols):
                num_cols = max(num_cols, len(cols))

        is_wide_table = (num_cols >= 7 or next_table_landscape or next_landscape) and not next_table_portrait and mode != "long" and not in_landscape_block

        if is_wide_table:
            absorbed_header = None
            if not next_landscape_isolated:
                absorbed_header = try_absorb_preceding_header(typ_lines)

            header_block = ""
            if absorbed_header:
                header_block = f"  {absorbed_header}\n  #v(0.4em)\n"

            typ_lines.append(f"""
#page(flipped: true)[
  #set align(left + top)
{header_block}  {tbl_rendered}
]
""")
            next_table_landscape = False
            next_table_portrait = False
            next_landscape = False
            next_landscape_isolated = False
            next_table_breakable = None
            next_table_compact = False
        else:
            typ_lines.append(f"\n{tbl_rendered}\n#v(0.4em)\n")
            next_table_landscape = False
            next_table_portrait = False
            next_table_breakable = None
            next_table_compact = False

        last_table_caption = None

        table_buffer = []
        in_table = False

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

                # 原生 Typst 语法直通（仅在显式声明 typst-raw 时才直通执行，普通 typst 渲染为代码卡片）
                if code_lang.lower() in ["typst-raw", "raw-typst"]:
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

                        if next_landscape and mode != "long" and not in_landscape_block:
                            typ_lines.append(f"""
#page(flipped: true)[
  #set align(center + horizon)
  #block(width: 100%, breakable: false)[
    #align(center)[
      #figure(
        image("{rel_img}", width: 100%, height: 132mm, fit: "contain")
      )
    ]
    {caption_snippet}
  ]
]
""")
                            next_landscape = False
                        else:
                            typ_lines.append(f"""
#block(width: 100%, breakable: false)[
  #align(center)[
    #figure(
      image("{rel_img}", width: 100%)
    )
  ]
  {caption_snippet}
]
""")
                        code_buffer = []
                        continue

                # 原生代码块卡片（自适应定界符：若代码包含反引号，动态加长定界符防止 Typst 提前闭合）
                clean_code_lang = code_lang.split('/')[0].split()[0].strip() if code_lang else ""
                longest_ticks = 0
                for tick_match in re.finditer(r'`+', code_text):
                    if len(tick_match.group(0)) > longest_ticks:
                        longest_ticks = len(tick_match.group(0))
                num_ticks = max(3, longest_ticks + 1)
                fence = "`" * num_ticks
                typ_lines.append(f"""{fence}{clean_code_lang}\n{code_text}\n{fence}""")
                code_buffer = []
                i += 1
                continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # 表格前置标题捕获（支持 **表X 名称**、**表X-X 名称**、*表 X 名称* 等学术规范形式）
        table_caption_match = re.match(r'^\s*(?:\*{1,2})?(表\s*\d+(?:[\-\.]\d+)?.*?)(?:\*{1,2})?\s*$', stripped)
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
            flush_table()

        # 空行：参考文献收集期间遇空行暂不断开，等待连续收集
        if not stripped:
            if not ref_buffer:
                typ_lines.append("")
            i += 1
            continue

        # 若当前非空行不是脚注定义，且 ref_buffer 存在内容，则立即冲刷参考文献网格
        if ref_buffer and not re.match(r'^\[\^([a-zA-Z0-9_\-]+)\]:\s*(.*)', stripped):
            flush_references()

        # 显式强制分页标记：<!-- force-pagebreak --> 或 <!-- pagebreak:force -->
        if re.match(r'^<!--\s*(?:force-pagebreak|pagebreak:force|pagebreak:exact)\s*-->$', stripped, re.IGNORECASE):
            typ_lines.append("\n#pagebreak()\n")
            i += 1
            continue

        # 过滤专为 Web/HTML 交互设计的辅助提示（如 "🔗 交互式架构视图：点击可在浏览器中查看..."），杜绝泄露至出版级 PDF/长图
        if (stripped.startswith(">") or stripped.startswith("🔗") or stripped.startswith("-") or stripped.startswith("*")) and ("交互式" in stripped or "浏览器中查看" in stripped) and any(ext in stripped.lower() for ext in [".html", ".htm"]):
            i += 1
            continue

        # 用户明确要求：普通通用分页符不要渲染，无论出现在什么位置
        if re.match(r'^<!--\s*(?:page\s*break|newpage)\s*-->$', stripped, re.IGNORECASE) or stripped in (r"\newpage", r"\pagebreak") or re.match(r'^<div\s+[^>]*(?:page-break-(?:before|after)|break-(?:before|after))\s*:\s*(?:always|page)[^>]*>\s*</div>$', stripped, re.IGNORECASE):
            i += 1
            continue

        # 表格专属版向控制标记：<!-- table:landscape --> 或 <!-- table:portrait -->
        m_tbl_dir = re.match(r'^<!--\s*table:(landscape|portrait)(?::(no-absorb|isolated|exact))?\s*-->$', stripped, re.IGNORECASE)
        if m_tbl_dir:
            direction = m_tbl_dir.group(1).lower()
            if direction == "landscape":
                next_table_landscape = True
                if m_tbl_dir.group(2):
                    next_landscape_isolated = True
            else:
                next_table_portrait = True
            i += 1
            continue

        # 表格专属跨页控制标记：<!-- table:breakable --> 或 <!-- table:unbreakable --> 或 <!-- breakable: true/false -->
        m_tbl_brk = re.match(r'^<!--\s*(?:table\s*:\s*)?(breakable|unbreakable)(?:\s*:\s*(true|false))?\s*-->$', stripped, re.IGNORECASE)
        if m_tbl_brk:
            kind = m_tbl_brk.group(1).lower()
            val = m_tbl_brk.group(2)
            if kind == "breakable":
                next_table_breakable = True if val is None or val.lower() == "true" else False
            else:
                next_table_breakable = False if val is None or val.lower() == "true" else True
            i += 1
            continue

        # 表格紧凑模式标记：<!-- table:compact --> 或 <!-- table: compact -->
        m_tbl_compact = re.match(r'^<!--\s*(?:table\s*:\s*)?(compact|dense)(?:\s*:\s*(true|false))?\s*-->$', stripped, re.IGNORECASE)
        if m_tbl_compact:
            val = m_tbl_compact.group(2)
            next_table_compact = True if val is None or val.lower() == "true" else False
            i += 1
            continue

        # 显式声明横版独立页标记：<!-- landscape --> 或 <!-- pagebreak:landscape --> 或 <!-- page:landscape -->
        # 支持 :no-absorb / :isolated / :exact 强制不自动吸纳前置小节标题，遵从编写者单图独立设计意图
        m_land = re.match(r'^<!--\s*(?:landscape|pagebreak:landscape|page:landscape)(?::(no-absorb|isolated|exact))?\s*-->$', stripped, re.IGNORECASE)
        if m_land:
            next_landscape = True
            next_landscape_isolated = (m_land.group(1) is not None)
            i += 1
            continue

        # 显式声明多块横版区域包裹：<!-- landscape-start --> 与 <!-- landscape-end -->（方案 A 显式块）
        if re.match(r'^<!--\s*(?:landscape:start|landscape-start)\s*-->$', stripped, re.IGNORECASE):
            if mode != "long":
                typ_lines.append("#page(flipped: true)[\n#set align(left + top)")
                in_landscape_block = True
            i += 1
            continue

        if re.match(r'^<!--\s*(?:landscape:end|landscape-end|/landscape)\s*-->$', stripped, re.IGNORECASE):
            if mode != "long" and in_landscape_block:
                typ_lines.append("]")
                in_landscape_block = False
            i += 1
            continue

        # 分隔线 ---
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            section_list_counter = 0
            next_idx = i + 1
            while next_idx < len(clean_lines) and not clean_lines[next_idx].strip():
                next_idx += 1
            if next_idx < len(clean_lines) and clean_lines[next_idx].strip().startswith("#"):
                # 紧邻标题的分割线不画横线，避免产生类似分页符的横道干扰排版
                typ_lines.append("\n#v(0.2em)\n")
            else:
                typ_lines.append("\n#v(0.5em)#line(length: 100%, stroke: 0.5pt + rgb(\"#e2e8f0\"))#v(0.5em)\n")
            i += 1
            continue

        # 目录生成识别：遇到 "## 目录" 自动输出 Typst 原生可点击大纲，并自动消费后续手动目录列表
        if stripped.startswith("## ") and any(stripped[3:].strip() == k for k in ["目录", "目 录", "Table of Contents", "TOC"]):
            section_list_counter = 0
            # 目录前是否分页：检测 Markdown 源码中显式 <!-- pagebreak --> / <!-- force-pagebreak --> 或 Frontmatter 配置
            has_before_pb = False
            if metadata.get('standalone_toc') or metadata.get('toc_pagebreak') or str(metadata.get('toc', '')).lower() in ('standalone', 'pagebreak', 'true'):
                has_before_pb = True
            else:
                idx_prev = i - 1
                while idx_prev >= 0:
                    p_line = clean_lines[idx_prev].strip()
                    if not p_line or re.match(r'^-{3,}$', p_line) or re.match(r'^\*{3,}$', p_line):
                        idx_prev -= 1
                        continue
                    if re.search(r'<!--\s*(?:force-)?pagebreak(?::\w+)?\s*-->', p_line, re.IGNORECASE) or p_line in (r'\newpage', r'\pagebreak'):
                        has_before_pb = True
                    break

            if has_before_pb and mode != "long":
                last_non_empty = next((l.strip() for l in reversed(typ_lines) if l.strip()), "")
                before_pb = "" if last_non_empty.endswith("#pagebreak()") else "#pagebreak()\n"
            else:
                before_pb = ""

            # 目录后是否分页：向前消费手动目录列表并检测后置分页指令
            has_after_pb = False
            if metadata.get('standalone_toc') or metadata.get('toc_pagebreak') or str(metadata.get('toc', '')).lower() in ('standalone', 'pagebreak', 'true'):
                has_after_pb = True

            i += 1
            while i < len(clean_lines):
                nxt = clean_lines[i].strip()
                if re.search(r'<!--\s*(?:force-)?pagebreak(?::\w+)?\s*-->', nxt, re.IGNORECASE) or nxt in (r'\newpage', r'\pagebreak'):
                    has_after_pb = True
                if nxt.startswith("## ") or nxt.startswith("# "):
                    break
                if re.match(r'^-{3,}$', nxt) or re.match(r'^\*{3,}$', nxt):
                    i += 1
                    while i < len(clean_lines) and not clean_lines[i].strip():
                        i += 1
                    if i < len(clean_lines) and (re.search(r'<!--\s*(?:force-)?pagebreak(?::\w+)?\s*-->', clean_lines[i].strip(), re.IGNORECASE) or clean_lines[i].strip() in (r'\newpage', r'\pagebreak')):
                        has_after_pb = True
                        i += 1
                    break
                i += 1

            after_pb = "#pagebreak()\n" if (has_after_pb and mode != "long") else "#v(1.0em)\n"

            typ_lines.append(f"""
{before_pb}#v(0.8em)
#align(center)[#text(font: ("PingFang SC", "Heiti SC", "STHeiti"), size: 16pt, weight: "bold", fill: rgb("#0f172a"), tracking: 0.5em)[目　录]]
#v(1.0em)
#block[
  #set par(leading: 0.68em)
  #outline(
    title: none,
    depth: 2,
  )
]
{after_pb}""")
            continue

        # 章节标题转换（由 Typst block above/below 统一精准控制，小节内列表计数器归零）
        if stripped.startswith("## "):
            section_list_counter = 0
            title_text = stripped[3:].strip()
            formatted_title = format_inline_markdown(title_text)

            # 行政性前置表格（如文档版本与修订记录）不纳入目录大纲
            if any(k in title_text for k in ["文档版本", "修订记录", "版本记录", "变更历史"]):
                typ_lines.append(f"#heading(level: 1, outlined: false)[{formatted_title}]")
                i += 1
                continue

            m_sec = re.match(r'^(\d+(?:\.\d+)*)\s*(.*)', title_text)
            anchor_label = ""
            if m_sec:
                sec_no = m_sec.group(1).replace(".", "-")
                anchor_label = f" <sec-{sec_no}>"

            if "参考文献" in title_text or "References" in title_text:
                typ_lines.append(f"= {formatted_title}{anchor_label}\n#set enum(indent: 0em, body-indent: 0.5em, spacing: 0.7em, numbering: \"[1]\")\n#set list(indent: 0em, body-indent: 0.5em, spacing: 0.7em)\n#set par(first-line-indent: 0em)")
            else:
                typ_lines.append(f"= {formatted_title}{anchor_label}")
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
                    "TIP": ("#16a34a", "#f0fdf4", "💡 操作建议"),
                    "IMPORTANT": ("#7c3aed", "#faf5ff", "📌 关键要点"),
                    "WARNING": ("#d97706", "#fffbeb", "⚠️ 注意事项"),
                    "CAUTION": ("#dc2626", "#fef2f2", "🛑 安全告警"),
                }
                stroke_color, bg_color, default_title = c_configs.get(c_type, ("#0284c7", "#f0f9ff", "提示说明"))
                
                title_line = ""
                content_lines = []
                raw_c_lines = c_body_lines
                if c_body_lines and c_body_lines[0].startswith("**") and c_body_lines[0].endswith("**"):
                    title_line = c_body_lines[0][2:-2].strip()
                    raw_c_lines = c_body_lines[1:]
                else:
                    title_line = default_title
                
                for l in raw_c_lines:
                    l_strip = l.strip()
                    if not l_strip:
                        continue
                    if re.match(r'^[\*\-]\s+', l_strip):
                        item_body = re.sub(r'^[\*\-]\s+', '', l_strip)
                        content_lines.append(f"- {format_inline_markdown(item_body)}")
                    elif re.match(r'^\d+\.\s+', l_strip):
                        m = re.match(r'^\d+\.\s+', l_strip)
                        item_body = l_strip[len(m.group(0)):].strip()
                        content_lines.append(f"+ {format_inline_markdown(item_body)}")
                    else:
                        content_lines.append(format_inline_markdown(l_strip))
                
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
  #set list(indent: 0em, body-indent: 0.5em, spacing: 0.6em)
  #set enum(indent: 0em, body-indent: 0.5em, spacing: 0.6em)
  #text(font: ("PingFang SC", "Heiti SC"), weight: "bold", size: 10pt, fill: rgb("{stroke_color}"))[{title_line}]
  #v(3pt)
  #text(size: 9.5pt)[{body_joined}]
]
""")
                continue

            # 普通引用块
            formatted_quotes = []
            for q in curr_quote:
                q_strip = q.strip()
                if not q_strip:
                    continue
                if re.match(r'^[\*\-]\s+', q_strip):
                    item_body = re.sub(r'^[\*\-]\s+', '', q_strip)
                    formatted_quotes.append(f"- {format_inline_markdown(item_body)}")
                elif re.match(r'^\d+\.\s+', q_strip):
                    m = re.match(r'^\d+\.\s+', q_strip)
                    item_body = q_strip[len(m.group(0)):].strip()
                    formatted_quotes.append(f"+ {format_inline_markdown(item_body)}")
                else:
                    formatted_quotes.append(format_inline_markdown(q_strip))
            joined_quote = "\n\n".join(formatted_quotes)
            is_empty_quote = not joined_quote.strip()
            if quote_indent >= 2:
                above_val = "0.3em" if is_empty_quote else "0.6em"
                below_val = "0.4em" if is_empty_quote else "0.8em"
                inset_y = "4pt" if is_empty_quote else "7pt"
                typ_lines.append(f"""
#pad(left: 2em)[
  #block(
    width: 100%,
    stroke: (left: 2.5pt + rgb("#0284c7")),
    fill: rgb("#f0f9ff"),
    inset: (x: 10pt, y: {inset_y}),
    radius: (right: 3pt),
    above: {above_val},
    below: {below_val}
  )[
    #set par(first-line-indent: (amount: 0em, all: true), leading: 0.7em)
    #set list(indent: 0em, body-indent: 0.5em, spacing: 0.6em)
    #set enum(indent: 0em, body-indent: 0.5em, spacing: 0.6em)
    {joined_quote}
  ]
]
""")
            else:
                above_val = "4pt" if is_empty_quote else "8pt"
                below_val = "5pt" if is_empty_quote else "10pt"
                inset_y = "5pt" if is_empty_quote else "8pt"
                typ_lines.append(f"""
#block(
  width: 100%,
  stroke: (left: 3.5pt + rgb("#0284c7")),
  fill: rgb("#f0f9ff"),
  inset: (x: 12pt, y: {inset_y}),
  radius: (right: 4pt),
  above: {above_val},
  below: {below_val}
)[
  #set par(first-line-indent: (amount: 0em, all: true), leading: 0.7em)
  #set list(indent: 0em, body-indent: 0.5em, spacing: 0.6em)
  #set enum(indent: 0em, body-indent: 0.5em, spacing: 0.6em)
  {joined_quote}
]
""")
            continue

        if stripped.startswith("### "):
            section_list_counter = 0
            sub_title = stripped[4:].strip()
            formatted_sub = format_inline_markdown(sub_title)
            if "参考文献" in sub_title or "References" in sub_title:
                typ_lines.append(f"== {formatted_sub}\n#set enum(indent: 0em, body-indent: 0.5em, spacing: 0.7em, numbering: \"[1]\")\n#set list(indent: 0em, body-indent: 0.5em, spacing: 0.7em)\n#set par(first-line-indent: 0em)")
            else:
                typ_lines.append(f"== {formatted_sub}")
            i += 1
            continue
        elif stripped.startswith("#### "):
            section_list_counter = 0
            h4_title = stripped[5:].strip()
            formatted_h4 = format_inline_markdown(h4_title)
            typ_lines.append(f"=== {formatted_h4}")
            i += 1
            continue
        elif stripped.startswith("##### "):
            section_list_counter = 0
            typ_lines.append(f"==== {format_inline_markdown(stripped[6:].strip())}")
            i += 1
            continue
        elif stripped.startswith("###### "):
            section_list_counter = 0
            typ_lines.append(f"#block(above: 0.9em, below: 0.6em, sticky: true)[#set par(first-line-indent: (amount: 0em, all: true)); #text(font: (\"Times New Roman\", \"PingFang SC\", \"Heiti SC\", \"STHeiti\", \"SimHei\"), weight: \"bold\", size: 10.5pt, fill: rgb(\"#0f172a\"))[{format_inline_markdown(stripped[7:].strip())}]]")
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
            math_text = "\n".join(math_lines)
            typ_math = convert_latex_math_to_typst(math_text)
            if math_indent >= 4:
                # 深层列表项内部的公式块：缩进 4 格输出，归属于当前二级/三级列表项
                typ_lines.append(f"    $ {typ_math} $")
            elif math_indent >= 2:
                # 列表项内部的公式块：缩进 2 格输出，归属于当前列表项，避免打断列表
                typ_lines.append(f"  $ {typ_math} $")
            else:
                typ_lines.append(f"\n$ {typ_math} $\n")
            i += 1
            continue


        # =========================================================================
        # 3. 容器标签过滤与多模图片语法 (Markdown ![alt](path) & HTML <img>)
        # =========================================================================
        if re.match(r'^\s*</?(?:div|center|p)\b[^>]*>\s*$', stripped, re.IGNORECASE) or re.match(r'^\s*<br\s*/?>\s*$', stripped, re.IGNORECASE):
            i += 1
            continue

        html_img_match = re.search(r'''<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>''', stripped, re.IGNORECASE)
        img_match = re.match(r'^\s*!\[(.*?)\]\((.*?)\)\s*(?:\{([^}]+)\})?\s*$', stripped)

        if img_match or html_img_match:
            custom_width = "100%"
            if img_match:
                img_caption = img_match.group(1).strip()
                img_path = img_match.group(2).strip()
                props = img_match.group(3) or ""
                m_w = re.search(r'width[:=]\s*([0-9]+%|[0-9.]+(?:mm|cm|pt|em)?)', props, re.IGNORECASE)
                if m_w:
                    w_val = m_w.group(1)
                    custom_width = w_val if any(w_val.endswith(u) for u in ['%', 'mm', 'cm', 'pt', 'em']) else f"{w_val}%"
                else:
                    # 原生支持 Marp 语法: ![width:60% 图...](path) 或 ![w:450px 图...](path)
                    marp_pat = re.compile(r'(?:^|\s)(?:w|width)[:=]\s*([0-9]+(?:%|px|mm|cm|pt|em)?)(?=\s|$)', re.IGNORECASE)
                    marp_m = marp_pat.search(img_caption)
                    if marp_m:
                        w_val = marp_m.group(1)
                        if w_val.endswith('%') or any(w_val.endswith(u) for u in ['mm', 'cm', 'pt', 'em']):
                            custom_width = w_val
                        elif w_val.endswith('px'):
                            px_num = float(w_val[:-2])
                            pct = min(100, max(20, round(px_num / 720 * 100)))
                            custom_width = f"{pct}%"
                        else:
                            custom_width = f"{w_val}%"
                        img_caption = marp_pat.sub('', img_caption).strip()
            else:
                img_path = html_img_match.group(1).strip()
                alt_m = re.search(r'''alt=["\']([^"\']+)["\']''', stripped, re.IGNORECASE)
                img_caption = alt_m.group(1).strip() if alt_m else ""
                w_m = re.search(r'''width=["\']?(\d+(?:%|mm|cm|pt|em)?)["\']?''', stripped, re.IGNORECASE)
                if w_m:
                    w_val = w_m.group(1)
                    custom_width = w_val if any(w_val.endswith(u) for u in ['%', 'mm', 'cm', 'pt', 'em']) else f"{w_val}%"

            # 智能消费随后的题注行（兼容 <sub><b>图...</b></sub>、*图...*、纯文本题注）
            while i + 1 < len(clean_lines):
                next_raw = clean_lines[i + 1].strip()
                if not next_raw or re.match(r'^\s*</?(?:div|center|p)\b[^>]*>\s*$', next_raw, re.IGNORECASE) or re.match(r'^\s*<br\s*/?>\s*$', next_raw, re.IGNORECASE):
                    i += 1
                    continue
                m_sub = re.search(r'<sub>\s*(?:<b>)?(.*?)(?:</b>)?\s*</sub>', next_raw, re.IGNORECASE)
                if m_sub:
                    img_caption = re.sub(r'</?[^>]+>', '', m_sub.group(1)).strip()
                    i += 1
                    break
                if (next_raw.startswith("*") and next_raw.endswith("*") and len(next_raw) > 2) or \
                   (next_raw.startswith("_") and next_raw.endswith("_") and len(next_raw) > 2) or \
                   next_raw.startswith("图 ") or next_raw.startswith("图") or "Fig" in next_raw:
                    clean_cap = next_raw.strip("*_ ")
                    if not img_caption or (img_caption in clean_cap) or (clean_cap in img_caption) or ("图" in clean_cap or "Fig" in clean_cap):
                        img_caption = clean_cap
                    i += 1
                    break
                break

            while i + 1 < len(clean_lines) and re.match(r'^\s*</?(?:div|center|p)\b[^>]*>\s*$', clean_lines[i+1].strip(), re.IGNORECASE):
                i += 1

            caption_block = ""
            if img_caption:
                img_caption = re.sub(r'</?[^>]+>', '', img_caption)
                caption_block = f"""
  #v(-0.2em)
  #align(center)[#text(font: ("PingFang SC", "Songti SC"), size: 9pt, style: "italic", fill: rgb("#475569"))[{img_caption}]]
  #v(0.4em)
"""
            if next_landscape and mode != "long" and not in_landscape_block:
                absorbed_header = None
                if not next_landscape_isolated:
                    absorbed_header = try_absorb_preceding_header(typ_lines)

                if absorbed_header:
                    typ_lines.append(f"""
#page(flipped: true)[
  #set align(left + top)
  {absorbed_header}
  #v(0.3em)
  #align(center)[
    #figure(
      image("{img_path}", width: 100%, height: 110mm, fit: "contain")
    )
  ]
  {caption_block}
]
""")
                else:
                    typ_lines.append(f"""
#page(flipped: true)[
  #set align(center + horizon)
  #block(width: 100%, breakable: false)[
    #align(center)[
      #figure(
        image("{img_path}", width: 100%, height: 132mm, fit: "contain")
      )
    ]
    {caption_block}
  ]
]
""")
                next_landscape = False
                next_landscape_isolated = False
            elif in_landscape_block and mode != "long":
                typ_lines.append(f"""
#block(width: 100%, breakable: false)[
  #align(center)[
    #figure(
      image("{img_path}", width: 100%, height: 115mm, fit: "contain")
    )
  ]
  {caption_block}
]
""")
            else:
                typ_lines.append(f"""
#block(width: 100%, breakable: false)[
  #align(center)[
    #figure(
      image("{img_path}", width: {custom_width})
    )
  ]
  {caption_block}
]
""")
            i += 1
            continue

        
        # 判断行首缩进深度，区分第一级与第二级
        indent = len(line) - len(line.lstrip())

        # =========================================================================
        # 1. 第二级与深层嵌套列表与从属文本 (indent >= 2) - 原生流式语法映射
        # =========================================================================
        if indent >= 2:
            m_sub_num = re.match(r'^\d+\.\s+', stripped)
            m_sub_bullet = re.match(r'^[\*\-]\s+', stripped)
            prefix = "    " if indent >= 4 else "  "
            if m_sub_num:
                item_body = stripped[len(m_sub_num.group(0)):].strip()
                typ_lines.append(f"{prefix}+ {format_inline_markdown(item_body)}")
                i += 1
                continue
            elif m_sub_bullet:
                item_body = re.sub(r'^[\*\-]\s+', '', stripped)
                typ_lines.append(f"{prefix}- {format_inline_markdown(item_body)}")
                i += 1
                continue
            else:
                # 嵌套从属正文/代码：按标准段落输出，绝不包裹 block 或清零缩进
                typ_lines.append(format_inline_markdown(stripped))
                i += 1
                continue
        # 2. 第一级列表 (indent < 2)：原生流式排版，保留粗体行内语义，严禁强加换行
        # =========================================================================
        is_unordered = re.match(r'^[\*\-]\s+', stripped)
        m_ordered = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if is_unordered or m_ordered:
            if is_unordered:
                body = re.sub(r'^[\*\-]\s+', '', stripped)
                formatted_body = format_inline_markdown(body)
                if typ_lines and typ_lines[-1] != "" and not typ_lines[-1].startswith("- ") and not re.match(r'^\d+\.\s+', typ_lines[-1]):
                    typ_lines.append("")
                typ_lines.append(f"- {formatted_body}")
            else:
                num = m_ordered.group(1)
                body = m_ordered.group(2).strip()
                formatted_body = format_inline_markdown(body)
                if typ_lines and typ_lines[-1] != "" and not typ_lines[-1].startswith("- ") and not re.match(r'^\d+\.\s+', typ_lines[-1]):
                    typ_lines.append("")
                typ_lines.append(f"{num}. {formatted_body}")
            i += 1
            continue

        # =========================================================================
        # 3.5 Markdown 脚注/参考文献定义行: [^id]: content（缓冲并生成两列对齐学术网格）
        # =========================================================================
        m_fn_def = re.match(r'^\[\^([a-zA-Z0-9_\-]+)\]:\s*(.*)', stripped)
        if m_fn_def:
            fn_id = m_fn_def.group(1)
            fn_body = m_fn_def.group(2).strip()
            fn_body_formatted = format_inline_markdown(fn_body)
            ref_buffer.append((fn_id, fn_body_formatted))
            i += 1
            continue

        # =========================================================================
        # =========================================================================
        # 4. 普通正文段落（标准流式段落，支持 Markdown 行尾双空格硬换行条目组）
        # =========================================================================
        raw_line = clean_lines[i]
        line_no_nl = raw_line[:-1] if raw_line.endswith(chr(10)) else raw_line
        if line_no_nl.endswith(chr(13)): line_no_nl = line_no_nl[:-1]
        has_hard_break = line_no_nl.endswith("  ") or line_no_nl.endswith(chr(92))

        if has_hard_break:
            # 连续硬换行构成的条目组：保持整组左侧完全平齐，消除首行2em与后续行顶格的错位
            block_items = []
            curr_i = i
            while curr_i < len(clean_lines):
                c_line = clean_lines[curr_i]
                c_stripped = c_line.strip()
                if not c_stripped:
                    break
                c_no_nl = c_line[:-1] if c_line.endswith(chr(10)) else c_line
                if c_no_nl.endswith(chr(13)): c_no_nl = c_no_nl[:-1]
                c_has_hb = c_no_nl.endswith("  ") or c_no_nl.endswith(chr(92))
                
                c_fmt = format_inline_markdown(c_stripped)
                block_items.append((c_fmt, c_has_hb))
                curr_i += 1
                if not c_has_hb:
                    break

            if len(block_items) > 1:
                joined_block = []
                for idx_b, (fmt_text, _) in enumerate(block_items):
                    if idx_b < len(block_items) - 1:
                        joined_block.append(f"{fmt_text} " + chr(92))
                    else:
                        joined_block.append(fmt_text)
                typ_lines.append("#par(first-line-indent: 0em)[")
                typ_lines.extend(joined_block)
                typ_lines.append("]")
                i = curr_i
                continue
            else:
                typ_lines.append(block_items[0][0])
                i = curr_i
                continue
        else:
            p_formatted = format_inline_markdown(stripped)
            typ_lines.append(p_formatted)
            i += 1


    if in_table:
        flush_table()

    if ref_buffer:
        flush_references()

    if in_landscape_block and mode != "long":
        typ_lines.append("]")
        in_landscape_block = False

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
            if in_md.endswith(".ssot.md"):
                out_target = in_md[:-8] + ".ssot.long.png"
            else:
                out_target = in_md.replace(".md", ".png")
        else:
            if in_md.endswith(".ssot.md"):
                out_target = in_md[:-8] + ".ssot.a4.pdf"
            else:
                out_target = in_md.replace(".md", ".pdf")

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
