#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSOT & Standard Markdown to Publication-Grade Word (.docx) Compiler
Aligned 1:1 with NCU Typst Dual-Mode Publication Typography System.
Usage:
    python3 md_to_docx.py <input.md> [output.docx] [--header TEXT] [--no-indent]
"""

import argparse
import copy
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from lxml import etree
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

CALLOUT_PALETTE = {
    "NOTE": ("0284C7", "F0F9FF"),
    "INFO": ("2563EB", "F8FAFC"),
    "TIP": ("059669", "F0FDF4"),
    "IMPORTANT": ("7C3AED", "F5F3FF"),
    "WARNING": ("D97706", "FFFBEB"),
    "CAUTION": ("DC2626", "FEF2F2"),
}

KROKI_DIAGRAM_TYPES = {"mermaid", "plantuml", "d2", "graphviz", "dot", "c4plantuml", "excalidraw"}

LATEX_FALLBACK_SYMBOLS = {
    r"\le": "≤",
    r"\leq": "≤",
    r"\ge": "≥",
    r"\geq": "≥",
    r"\neq": "≠",
    r"\ne": "≠",
    r"\approx": "≈",
    r"\equiv": "≡",
    r"\sim": "∼",
    r"\pm": "±",
    r"\times": "×",
    r"\cdot": "·",
    r"\oplus": "⊕",
    r"\otimes": "⊗",
    r"\in": "∈",
    r"\notin": "∉",
    r"\subset": "⊂",
    r"\subseteq": "⊆",
    r"\cup": "∪",
    r"\cap": "∩",
    r"\land": "∧",
    r"\lor": "∨",
    r"\to": "→",
    r"\rightarrow": "→",
    r"\leftarrow": "←",
    r"\Rightarrow": "⇒",
    r"\leftrightarrow": "↔",
    r"\forall": "∀",
    r"\exists": "∃",
    r"\infty": "∞",
    r"\sum": "∑",
    r"\prod": "∏",
    r"\dots": "…",
    r"\cdots": "⋯",
    r"\alpha": "α",
    r"\beta": "β",
    r"\gamma": "γ",
    r"\delta": "δ",
    r"\epsilon": "ϵ",
    r"\varepsilon": "ε",
    r"\zeta": "ζ",
    r"\eta": "η",
    r"\theta": "θ",
    r"\iota": "ι",
    r"\kappa": "κ",
    r"\lambda": "λ",
    r"\mu": "μ",
    r"\nu": "ν",
    r"\xi": "ξ",
    r"\pi": "π",
    r"\rho": "ρ",
    r"\sigma": "σ",
    r"\tau": "τ",
    r"\phi": "ϕ",
    r"\varphi": "φ",
    r"\chi": "χ",
    r"\psi": "ψ",
    r"\omega": "ω",
    r"\Delta": "Δ",
    r"\Gamma": "Γ",
    r"\Lambda": "Λ",
    r"\Omega": "Ω",
    r"\Phi": "Φ",
    r"\Psi": "Ψ",
    r"\Sigma": "Σ",
    r"\Theta": "Θ",
}


def set_east_asian_font(run, ascii_font="Times New Roman", east_asian_font="宋体"):
    run.font.name = ascii_font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), ascii_font)
    rFonts.set(qn("w:hAnsi"), ascii_font)
    rFonts.set(qn("w:eastAsia"), east_asian_font)


def set_run_shading(run, fill_hex="F1F5F9"):
    rPr = run._element.get_or_add_rPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
    rPr.append(shd)


def set_paragraph_border(paragraph, **kwargs):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    for edge, spec in kwargs.items():
        edge_el = pBdr.find(qn(f"w:{edge}"))
        if edge_el is None:
            edge_el = OxmlElement(f"w:{edge}")
            pBdr.append(edge_el)
        edge_el.set(qn("w:val"), spec.get("val", "single"))
        edge_el.set(qn("w:sz"), str(spec.get("sz", 4)))
        edge_el.set(qn("w:space"), str(spec.get("space", 4)))
        edge_el.set(qn("w:color"), spec.get("color", "auto"))


def set_cell_shading(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    old_shd = tcPr.find(qn("w:shd"))
    if old_shd is not None:
        tcPr.remove(old_shd)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=110, bottom=110, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    old_mar = tcPr.find(qn("w:tcMar"))
    if old_mar is not None:
        tcPr.remove(old_mar)
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_borders(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn("w:tcBorders"))
    if tcBorders is not None:
        tcPr.remove(tcBorders)
    tcBorders = OxmlElement("w:tcBorders")
    tcPr.append(tcBorders)
    for edge, spec in kwargs.items():
        edge_el = OxmlElement(f"w:{edge}")
        edge_el.set(qn("w:val"), spec.get("val", "single"))
        edge_el.set(qn("w:sz"), str(spec.get("sz", 4)))
        edge_el.set(qn("w:space"), "0")
        edge_el.set(qn("w:color"), spec.get("color", "auto"))
        tcBorders.append(edge_el)


def set_row_cant_split_and_header(row, is_header=False):
    trPr = row._tr.get_or_add_trPr()
    if is_header:
        trPr.append(OxmlElement("w:tblHeader"))
        trPr.append(OxmlElement("w:cantSplit"))


def enforce_table_fixed_widths(tbl, col_widths_mm):
    """Force Word/WPS to respect exact column widths in mm (1 mm = 56.6929 dxa)."""
    tbl.autofit = False
    tblPr = tbl._tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    total_dxa = int(round(sum(col_widths_mm) * 56.6929))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(total_dxa))
    tblW.set(qn("w:type"), "dxa")

    tblLayout = tblPr.find(qn("w:tblLayout"))
    if tblLayout is None:
        tblLayout = OxmlElement("w:tblLayout")
        tblPr.append(tblLayout)
    tblLayout.set(qn("w:type"), "fixed")

    old_grid = tbl._tbl.find(qn("w:tblGrid"))
    if old_grid is not None:
        tbl._tbl.remove(old_grid)
    tblGrid = OxmlElement("w:tblGrid")
    for w_mm in col_widths_mm:
        gridCol = OxmlElement("w:gridCol")
        gridCol.set(qn("w:w"), str(int(round(w_mm * 56.6929))))
        tblGrid.append(gridCol)
    tblPr.addnext(tblGrid)


def set_cell_exact_width(cell, width_mm):
    dxa = int(round(width_mm * 56.6929))
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn("w:tcW"))
    if tcW is None:
        tcW = OxmlElement("w:tcW")
        tcPr.append(tcW)
    tcW.set(qn("w:w"), str(dxa))
    tcW.set(qn("w:type"), "dxa")


def build_omml_map(md_text: str) -> dict:
    """
    Batch-compile all unique $...$ and $$...$$ LaTeX math expressions into Word OMML (<m:oMath>)
    elements via Pandoc if available.
    """
    if not shutil.which("pandoc"):
        return {}

    block_spans = re.findall(r"\$\$([\s\S]+?)\$\$", md_text)
    inline_spans = re.findall(r"(?<!\$)\$(?!\$)([^$\n]+?)(?<!\$)\$(?!\$)", md_text)
    math_spans = sorted(set(s.strip() for s in (block_spans + inline_spans) if s.strip()))
    if not math_spans:
        return {}

    md_lines = [f"MATHKEY_{i}_END ${m}$" for i, m in enumerate(math_spans)]
    md_payload = "\n\n".join(md_lines)

    omml_map = {}
    try:
        with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
            subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "docx", "-o", tmp.name],
                input=md_payload.encode("utf-8"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with zipfile.ZipFile(tmp.name) as z:
                xml_bytes = z.read("word/document.xml")

        root = etree.fromstring(xml_bytes)
        ns = {"w": W_NS, "m": M_NS}
        for p in root.findall(".//w:body/w:p", ns):
            p_text = "".join(t.text for t in p.findall("w:r/w:t", ns) if t.text)
            m_key = re.search(r"MATHKEY_(\d+)_END", p_text)
            omath = p.find("m:oMath", ns)
            if m_key and omath is not None:
                idx = int(m_key.group(1))
                omml_map[math_spans[idx]] = omath
    except Exception:
        return {}

    return omml_map


def make_styled_omath(omath_template, size_pt=10.5, color_hex="0F172A"):
    """Clone an <m:oMath> element and apply Cambria Math font & target size to all <m:r> runs."""
    omath = copy.deepcopy(omath_template)
    half_pts = str(int(round(size_pt * 2)))
    for mr in omath.findall(f".//{{{M_NS}}}r"):
        rPr = mr.find(f"{{{W_NS}}}rPr")
        if rPr is None:
            rPr = etree.Element(f"{{{W_NS}}}rPr")
            mr.insert(0, rPr)
        rFonts = rPr.find(f"{{{W_NS}}}rFonts")
        if rFonts is None:
            rFonts = etree.SubElement(rPr, f"{{{W_NS}}}rFonts")
        rFonts.set(f"{{{W_NS}}}ascii", "Cambria Math")
        rFonts.set(f"{{{W_NS}}}hAnsi", "Cambria Math")
        rFonts.set(f"{{{W_NS}}}eastAsia", "宋体")

        sz = rPr.find(f"{{{W_NS}}}sz")
        if sz is None:
            sz = etree.SubElement(rPr, f"{{{W_NS}}}sz")
        sz.set(f"{{{W_NS}}}val", half_pts)

        szCs = rPr.find(f"{{{W_NS}}}szCs")
        if szCs is None:
            szCs = etree.SubElement(rPr, f"{{{W_NS}}}szCs")
        szCs.set(f"{{{W_NS}}}val", half_pts)

        color = rPr.find(f"{{{W_NS}}}color")
        if color is None:
            color = etree.SubElement(rPr, f"{{{W_NS}}}color")
        color.set(f"{{{W_NS}}}val", color_hex)
    return omath


def add_fallback_math_runs(paragraph, latex_str, base_size_pt=10.5, base_color=RGBColor(0x0F, 0x17, 0x2A), base_bold=False):
    """Fallback math renderer when Pandoc is unavailable or for custom LaTeX macros."""
    s = latex_str.strip()
    s = re.sub(r"\\(?:text|mathrm|operatorname)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
    for k, v in sorted(LATEX_FALLBACK_SYMBOLS.items(), key=lambda x: -len(x[0])):
        s = s.replace(k, v)
    s = s.replace(r"\{", "{").replace(r"\}", "}")

    pattern = re.compile(r"(_\{[^{}]+\}|_[A-Za-z0-9]+|\^\{[^{}]+\}|\^[A-Za-z0-9]+)")
    pos = 0
    for m in pattern.finditer(s):
        if m.start() > pos:
            r = paragraph.add_run(s[pos : m.start()])
            set_east_asian_font(r, "Cambria Math", "宋体")
            r.font.size = Pt(base_size_pt)
            r.font.color.rgb = base_color
            r.bold = base_bold
        tok = m.group(0)
        is_sub = tok.startswith("_")
        val = tok[2:-1] if tok[1:].startswith("{") else tok[1:]
        r = paragraph.add_run(val)
        set_east_asian_font(r, "Cambria Math", "宋体")
        r.font.size = Pt(base_size_pt)
        r.font.color.rgb = base_color
        r.bold = base_bold
        if is_sub:
            r.font.subscript = True
        else:
            r.font.superscript = True
        pos = m.end()
    if pos < len(s):
        r = paragraph.add_run(s[pos:])
        set_east_asian_font(r, "Cambria Math", "宋体")
        r.font.size = Pt(base_size_pt)
        r.font.color.rgb = base_color
        r.bold = base_bold


def render_diagram_via_kroki(source: str, diagram_type: str, output_dir: str):
    """Render Mermaid/Graphviz/PlantUML/D2 diagram via Kroki to PNG for Word embedding."""
    public_endpoint = "https://kroki.io"
    custom_endpoint = os.getenv("KROKI_ENDPOINT", "").strip().rstrip("/")
    endpoints = (
        [custom_endpoint, public_endpoint]
        if custom_endpoint and custom_endpoint != public_endpoint
        else [public_endpoint]
    )
    content_hash = hashlib.md5(f"{diagram_type}:{source.strip()}".encode("utf-8")).hexdigest()[:12]
    fig_dir = os.path.join(output_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    target_path = os.path.join(fig_dir, f"diagram_{content_hash}.png")

    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        return target_path

    for endpoint in endpoints:
        url = f"{endpoint}/{diagram_type.lower()}/png"
        try:
            req = urllib.request.Request(
                url,
                data=source.strip().encode("utf-8"),
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "User-Agent": "NCU-DOCX-Pipeline/1.2",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                if len(data) > 0:
                    with open(target_path, "wb") as f:
                        f.write(data)
                    return target_path
        except Exception:
            continue
    return None


def add_rich_text(
    paragraph,
    text,
    omml_map=None,
    base_size_pt=10.5,
    east_asian_font="宋体",
    bold_east_asian_font="黑体",
    ascii_font="Times New Roman",
    base_color=RGBColor(0x1E, 0x29, 0x3B),
    bold_color=RGBColor(0x0F, 0x17, 0x2A),
    base_bold=False,
):
    """
    Parse inline **bold**, *italic*, `code`, $math$, [^N] citations, and [label](url) links into Word runs & OMML.
    Supports nested $math$, `code`, and [^N] inside **bold** spans.
    """
    if omml_map is None:
        omml_map = {}

    def repl_link(m):
        label, url = m.group(1), m.group(2)
        if label.strip() == url.strip() or url.startswith("file://"):
            return label.strip()
        return f"{label} ({url})"

    text = re.sub(r"\[([^\^\]]+)\]\(([^)]+)\)", repl_link, text)

    token_pattern = re.compile(
        r"(\*\*(?!\s)[^*\n]+?(?<!\s)\*\*|`+[^`\n]+`+|\$\$[^$\n]+\$\$|(?<!\$)\$(?!\$)[^$\n]+?(?<!\$)\$(?!\$)|\[\^\d+\]|(?<!\*)\*(?!\s|\*)[^*\n]+?(?<!\s|\*)\*(?!\*))"
    )
    pos = 0
    for m in token_pattern.finditer(text):
        if m.start() > pos:
            plain = text[pos : m.start()]
            run = paragraph.add_run(plain)
            set_east_asian_font(
                run,
                ascii_font=ascii_font,
                east_asian_font=bold_east_asian_font if base_bold else east_asian_font,
            )
            run.font.size = Pt(base_size_pt)
            run.font.color.rgb = bold_color if base_bold else base_color
            run.bold = base_bold

        token = m.group(0)
        if token.startswith("**") and token.endswith("**"):
            inner = token[2:-2]
            add_rich_text(
                paragraph,
                inner,
                omml_map=omml_map,
                base_size_pt=base_size_pt,
                east_asian_font=bold_east_asian_font,
                bold_east_asian_font=bold_east_asian_font,
                ascii_font=ascii_font,
                base_color=bold_color,
                bold_color=bold_color,
                base_bold=True,
            )
        elif (token.startswith("$$") and token.endswith("$$")) or (token.startswith("$") and token.endswith("$")):
            latex_inner = token.strip("$").strip()
            if latex_inner in omml_map:
                omath_el = make_styled_omath(omml_map[latex_inner], size_pt=base_size_pt)
                paragraph._p.append(omath_el)
            else:
                add_fallback_math_runs(
                    paragraph,
                    latex_inner,
                    base_size_pt=base_size_pt,
                    base_color=bold_color if base_bold else base_color,
                    base_bold=base_bold,
                )
        elif token.startswith("`") and token.endswith("`"):
            inner = token.strip("`").strip()
            r = paragraph.add_run(inner)
            set_east_asian_font(r, ascii_font="Consolas", east_asian_font=east_asian_font)
            r.font.size = Pt(max(base_size_pt - 0.5, 8.5))
            r.font.color.rgb = RGBColor(0x03, 0x69, 0xA1) if not base_bold else bold_color
            r.bold = base_bold
            set_run_shading(r, "F1F5F9")
        elif token.startswith("[^") and token.endswith("]"):
            num = token[2:-1]
            cite_r = paragraph.add_run(f"[{num}]")
            set_east_asian_font(cite_r, ascii_font=ascii_font, east_asian_font=east_asian_font)
            cite_r.font.size = Pt(base_size_pt - 1)
            cite_r.font.superscript = True
            cite_r.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)
            cite_r.bold = base_bold
        elif token.startswith("*") and token.endswith("*"):
            inner = token[1:-1]
            r = paragraph.add_run(inner)
            set_east_asian_font(r, ascii_font=ascii_font, east_asian_font=east_asian_font)
            r.font.size = Pt(base_size_pt)
            r.font.color.rgb = base_color
            r.italic = True
            r.bold = base_bold
        pos = m.end()

    if pos < len(text):
        plain = text[pos:]
        run = paragraph.add_run(plain)
        set_east_asian_font(
            run,
            ascii_font=ascii_font,
            east_asian_font=bold_east_asian_font if base_bold else east_asian_font,
        )
        run.font.size = Pt(base_size_pt)
        run.font.color.rgb = bold_color if base_bold else base_color
        run.bold = base_bold


def configure_footer_with_page_number(footer):
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    set_paragraph_border(p, top={"val": "single", "sz": 4, "space": 4, "color": "E2E8F0"})

    r1 = p.add_run("— ")
    set_east_asian_font(r1, "Times New Roman", "宋体")
    r1.font.size = Pt(8.5)
    r1.bold = True
    r1.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    fldSimple = OxmlElement("w:fldSimple")
    fldSimple.set(qn("w:instr"), "PAGE")
    p._p.append(fldSimple)

    r2 = p.add_run(" —")
    set_east_asian_font(r2, "Times New Roman", "宋体")
    r2.font.size = Pt(8.5)
    r2.bold = True
    r2.font.color.rgb = RGBColor(0x47, 0x55, 0x69)


def split_md_table_row(line: str) -> list:
    """Split a Markdown table row by '|', ignoring '|' inside $...$ math or `...` code spans."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells = []
    cur = []
    in_math = False
    in_code = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`" and not in_math:
            in_code = not in_code
            cur.append(ch)
        elif ch == "$" and not in_code:
            in_math = not in_math
            cur.append(ch)
        elif ch == "|" and not in_math and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def clean_visual_length(cell_str: str) -> float:
    """Estimate visual text length of a table cell after stripping Markdown/LaTeX markup."""
    s = re.sub(r"<br\s*/?>", " ", cell_str)
    s = re.sub(r"\\(?:text|mathrm|operatorname)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[A-Za-z]+", "M", s)
    s = re.sub(r"[*_`$~{}]", "", s)
    # Count CJK chars as 1.0 and ASCII chars as 0.55
    total = 0.0
    for ch in s:
        total += 1.0 if ord(ch) > 127 else 0.55
    return max(total, 2.0)


def compute_column_widths_mm(parsed_rows, total_width_mm=168.0):
    """
    Dynamically compute balanced column widths in mm based on visual text density per column,
    preventing short label columns from stealing space from long description columns.
    """
    num_cols = max(len(r) for r in parsed_rows)
    if num_cols <= 1:
        return [total_width_mm]

    body_rows = parsed_rows[1:] if len(parsed_rows) > 1 else parsed_rows
    weights = []
    max_lens = []

    for c in range(num_cols):
        col_lens = [clean_visual_length(r[c]) for r in body_rows if c < len(r)]
        hdr_len = clean_visual_length(parsed_rows[0][c]) if c < len(parsed_rows[0]) else 4.0
        avg_len = sum(col_lens) / max(len(col_lens), 1)
        max_len = max(col_lens + [hdr_len])
        max_lens.append(max_len)
        effective = max(avg_len * 0.85 + hdr_len * 0.15, 3.0)
        weights.append(effective ** 0.58)

    total_w = sum(weights)
    widths = [total_width_mm * w / total_w for w in weights]

    # Clamp minimum width (18mm) and cap very short label columns (e.g., max_len <= 12 chars -> max 28mm)
    min_w = 18.0 if num_cols <= 5 else 14.0
    adjusted = list(widths)
    for c in range(num_cols):
        if max_lens[c] <= 10.0 and adjusted[c] > 25.0:
            adjusted[c] = 25.0
        elif max_lens[c] <= 15.0 and adjusted[c] > 32.0 and num_cols >= 3:
            adjusted[c] = 32.0
        if adjusted[c] < min_w:
            adjusted[c] = min_w

    # Redistribute remaining width to uncapped columns proportionally
    scale = total_width_mm / sum(adjusted)
    return [round(w * scale, 2) for w in adjusted]


def populate_table_cell(cell, raw_cell_text, omml_map, is_header=False, is_first_col=False):
    """Split <br> into multi-paragraph cells with hanging indent for list items."""
    segments = [seg.strip() for seg in re.split(r"<br\s*/?>", raw_cell_text) if seg.strip()]
    if not segments:
        segments = [""]

    for s_idx, seg in enumerate(segments):
        cp = cell.paragraphs[0] if s_idx == 0 else cell.add_paragraph()
        cp.paragraph_format.space_before = Pt(2 if s_idx > 0 else 1)
        cp.paragraph_format.space_after = Pt(2)
        cp.paragraph_format.line_spacing = 1.28
        cp.paragraph_format.first_line_indent = Pt(0)

        if is_header:
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_rich_text(
                cp,
                seg,
                omml_map=omml_map,
                base_size_pt=9.5,
                east_asian_font="黑体",
                bold_east_asian_font="黑体",
                base_color=RGBColor(0x0F, 0x17, 0x2A),
                bold_color=RGBColor(0x0F, 0x17, 0x2A),
                base_bold=True,
            )
        else:
            cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if re.match(r"^(\d+\.|•)\s*", seg):
                cp.paragraph_format.left_indent = Pt(12)
                cp.paragraph_format.first_line_indent = Pt(-12)
            add_rich_text(
                cp,
                seg,
                omml_map=omml_map,
                base_size_pt=9.2,
                east_asian_font="宋体",
                bold_east_asian_font="黑体",
                base_color=RGBColor(0x1E, 0x29, 0x3B),
                bold_color=RGBColor(0x0F, 0x17, 0x2A),
                base_bold=False,
            )


def build_docx(md_path: str, docx_path: str, custom_header: str = None, indent_body: bool = True):
    base_dir = os.path.dirname(os.path.abspath(md_path))
    with open(md_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # Strip optional YAML frontmatter while extracting title if present
    frontmatter_title = None
    if raw_content.startswith("---\n"):
        end_fm = raw_content.find("\n---\n", 4)
        if end_fm != -1:
            fm_block = raw_content[4:end_fm]
            tm = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", fm_block, re.MULTILINE)
            if tm:
                frontmatter_title = tm.group(1).strip()
            raw_content = raw_content[end_fm + 5 :]

    omml_map = build_omml_map(raw_content)

    lines = [line.rstrip("\n") for line in raw_content.splitlines()]

    # Detect document title for running header
    doc_title = frontmatter_title
    for ln in lines:
        if ln.strip().startswith("# "):
            doc_title = ln.strip()[2:].strip()
            break

    doc = Document()

    # Configure base styles aligned with Typst 10.5pt (五号字) & #0369a1 headings
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(10.5)
    normal_rPr = normal_style.element.get_or_add_rPr()
    normal_rFonts = normal_rPr.find(qn("w:rFonts"))
    if normal_rFonts is None:
        normal_rFonts = OxmlElement("w:rFonts")
        normal_rPr.append(normal_rFonts)
    normal_rFonts.set(qn("w:ascii"), "Times New Roman")
    normal_rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal_rFonts.set(qn("w:eastAsia"), "宋体")

    for h_name, h_size, h_color in [
        ("Heading 1", 13.5, RGBColor(0x1E, 0x3A, 0x8A)),
        ("Heading 2", 11.5, RGBColor(0x03, 0x69, 0xA1)),
        ("Heading 3", 10.5, RGBColor(0x0F, 0x17, 0x2A)),
    ]:
        st = doc.styles[h_name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(h_size)
        st.font.bold = True
        st.font.color.rgb = h_color
        st.paragraph_format.first_line_indent = Pt(0)
        st.paragraph_format.left_indent = Pt(0)
        rPr = st.element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn("w:ascii"), "Times New Roman")
        rFonts.set(qn("w:hAnsi"), "Times New Roman")
        rFonts.set(qn("w:eastAsia"), "黑体")

    # Configure A4 page & margins (top/bottom 22mm, left 21mm, right 21mm -> 168mm net width)
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(22)
    section.bottom_margin = Mm(22)
    section.left_margin = Mm(21)
    section.right_margin = Mm(21)
    section.different_first_page_header_footer = True
    net_width_mm = 168.0

    # Running Header (Page 2+) & Footer (All pages)
    header_text = custom_header or (doc_title if doc_title else os.path.splitext(os.path.basename(md_path))[0])
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(4)
    set_paragraph_border(hp, bottom={"val": "single", "sz": 4, "space": 4, "color": "CBD5E1"})
    hr = hp.add_run(header_text[:58])
    set_east_asian_font(hr, "Times New Roman", "黑体")
    hr.font.size = Pt(8.5)
    hr.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    configure_footer_with_page_number(section.footer)
    configure_footer_with_page_number(section.first_page_footer)

    i = 0
    n = len(lines)
    sub_enum_counter = 0

    while i < n:
        raw_line = lines[i]
        line = raw_line.strip()
        if not line or line.startswith("<!--"):
            i += 1
            continue

        # 0. Skip Markdown horizontal rules (---, ***, ___)
        if re.match(r"^[-*_]{3,}$", line):
            i += 1
            continue

        # 0.5 Display Math Block ($$ ... $$)
        if line.startswith("$$"):
            if line.endswith("$$") and len(line) > 4:
                math_expr = line[2:-2].strip()
                i += 1
            else:
                i += 1
                math_lines = []
                while i < n and not lines[i].strip().endswith("$$"):
                    math_lines.append(lines[i])
                    i += 1
                if i < n:
                    last_l = lines[i].strip()[:-2].strip()
                    if last_l:
                        math_lines.append(last_l)
                    i += 1
                math_expr = "\n".join(math_lines).strip()

            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.first_line_indent = Pt(0)
            if math_expr in omml_map:
                omath_el = make_styled_omath(omml_map[math_expr], size_pt=11.0)
                p._p.append(omath_el)
            else:
                add_fallback_math_runs(p, math_expr, base_size_pt=11.0)
            continue

        # 1. Fenced Code Block or Kroki Diagram (``` or ~~~)
        if line.startswith("```") or line.startswith("~~~"):
            fence = line[:3]
            lang = line[3:].strip().lower()
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith(fence):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence

            code_source = "\n".join(code_lines)
            if lang in KROKI_DIAGRAM_TYPES:
                img_path = render_diagram_via_kroki(code_source, lang, base_dir)
                if img_path and os.path.exists(img_path):
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(8)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.keep_with_next = True
                    run = p.add_run()
                    run.add_picture(img_path, width=Mm(158))
                    continue

            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            enforce_table_fixed_widths(tbl, [net_width_mm])
            cell = tbl.cell(0, 0)
            set_cell_exact_width(cell, net_width_mm)
            set_cell_shading(cell, "F8FAFC")
            set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
            set_cell_borders(
                cell,
                left={"val": "single", "sz": 6, "color": "CBD5E1"},
                top={"val": "single", "sz": 6, "color": "CBD5E1"},
                right={"val": "single", "sz": 6, "color": "CBD5E1"},
                bottom={"val": "single", "sz": 6, "color": "CBD5E1"},
            )
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(0)
            cp.paragraph_format.space_after = Pt(0)
            cp.paragraph_format.line_spacing = 1.25
            cr = cp.add_run(code_source)
            set_east_asian_font(cr, "Menlo", "宋体")
            cr.font.size = Pt(8.8)
            cr.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

            sp = doc.add_paragraph()
            sp.paragraph_format.space_after = Pt(4)
            continue

        # 2. Document Title (# H1) with Typst 1.2pt bottom rule
        if line.startswith("# "):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.line_spacing = 1.25
            set_paragraph_border(p, bottom={"val": "single", "sz": 12, "space": 8, "color": "1E3A8A"})
            r = p.add_run(title_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(17)
            r.bold = True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            i += 1
            continue

        # 3. Blockquote / Callout (> [!NOTE])
        if line.startswith(">"):
            quote_lines = []
            callout_type = "NOTE"
            while i < n and lines[i].strip().startswith(">"):
                ql = re.sub(r"^>\s?", "", lines[i].strip())
                m_callout = re.match(r"^\[!([A-Za-z]+)\]\s*(.*)$", ql)
                if m_callout:
                    callout_type = m_callout.group(1).upper()
                    remainder = m_callout.group(2).strip()
                    if remainder:
                        quote_lines.append(remainder)
                    i += 1
                    continue
                quote_lines.append(ql)
                i += 1

            border_hex, bg_hex = CALLOUT_PALETTE.get(callout_type, ("0284C7", "F0F9FF"))
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            enforce_table_fixed_widths(tbl, [net_width_mm])
            cell = tbl.cell(0, 0)
            set_cell_exact_width(cell, net_width_mm)
            set_cell_shading(cell, bg_hex)
            set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
            set_cell_borders(
                cell,
                left={"val": "single", "sz": 24, "color": border_hex},
                top={"val": "single", "sz": 4, "color": "E2E8F0"},
                right={"val": "single", "sz": 4, "color": "E2E8F0"},
                bottom={"val": "single", "sz": 4, "color": "E2E8F0"},
            )

            first_p = True
            for ql in quote_lines:
                if not ql:
                    continue
                cp = cell.paragraphs[0] if first_p else cell.add_paragraph()
                first_p = False
                cp.paragraph_format.space_before = Pt(2)
                cp.paragraph_format.space_after = Pt(4)
                cp.paragraph_format.line_spacing = 1.35
                cp.paragraph_format.first_line_indent = Pt(0)
                if re.match(r"^\d+\.\s", ql):
                    cp.paragraph_format.left_indent = Pt(14)
                    cp.paragraph_format.first_line_indent = Pt(-14)
                elif re.match(r"^-\s", ql):
                    ql = "• " + ql[2:].strip()
                    cp.paragraph_format.left_indent = Pt(24)
                    cp.paragraph_format.first_line_indent = Pt(-10)
                add_rich_text(
                    cp,
                    ql,
                    omml_map=omml_map,
                    base_size_pt=10.0,
                    east_asian_font="宋体",
                    base_color=RGBColor(0x0F, 0x17, 0x2A),
                )

            sp = doc.add_paragraph()
            sp.paragraph_format.space_before = Pt(0)
            sp.paragraph_format.space_after = Pt(6)
            continue

        # 4. Headings (## H2, ### H3, #### H4) & Standalone Bold Section Pseudo-Headings
        bold_h1_match = re.match(r"^\*\*([一二三四五六七八九十]+[、.．]\s*[^*]+)\*\*$", line)
        if line.startswith("## ") or bold_h1_match:
            h2_text = bold_h1_match.group(1).strip() if bold_h1_match else line[3:].strip()
            p = doc.add_heading(level=1)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.keep_with_next = True
            set_paragraph_border(p, bottom={"val": "single", "sz": 6, "space": 3, "color": "CBD5E1"})
            r = p.add_run(h2_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(13.5)
            r.bold = True
            r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            i += 1
            continue

        if line.startswith("### "):
            h3_text = line[4:].strip()
            p = doc.add_heading(level=2)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.keep_with_next = True
            r = p.add_run(h3_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(11.5)
            r.bold = True
            r.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)
            i += 1
            continue

        bold_sub_match = re.match(r"^\*\*([^*]{2,28})\*\*([：:]?)$", line)
        if line.startswith("#### ") or bold_sub_match:
            h4_text = (
                f"{bold_sub_match.group(1).strip()}{bold_sub_match.group(2)}"
                if bold_sub_match
                else line[5:].strip()
            )
            p = doc.add_heading(level=3)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.keep_with_next = True
            r = p.add_run(h4_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(10.5)
            r.bold = True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            i += 1
            continue

        # 5. Image (![alt](path))
        img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line)
        if img_match:
            img_rel_path = img_match.group(2)
            img_abs_path = os.path.join(base_dir, img_rel_path)
            if os.path.exists(img_abs_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                run = p.add_run()
                run.add_picture(img_abs_path, width=Mm(158))
            i += 1
            continue

        # 6. Figure or Table Caption (**图 X ...** / *图 X ...* / **表 X ...**)
        cap_match = re.match(r"^(?:\*\*|\*)?((?:图|表)\s*[\d\-]+[^*]+?)(?:\*\*|\*)?$", line)
        if cap_match and len(line) <= 72:
            cap_text = cap_match.group(1).strip()
            is_table_cap = cap_text.startswith("表")
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10 if is_table_cap else 2)
            p.paragraph_format.space_after = Pt(4 if is_table_cap else 10)
            if is_table_cap:
                p.paragraph_format.keep_with_next = True
            r = p.add_run(cap_text)
            set_east_asian_font(r, "Times New Roman", "黑体" if is_table_cap else "宋体")
            r.font.size = Pt(9.8)
            r.bold = is_table_cap
            r.italic = not is_table_cap
            r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) if is_table_cap else RGBColor(0x47, 0x55, 0x69)
            i += 1
            continue

        # 7. Markdown Table (| ... |) - Publication Three-Line Table with Fixed Grid & Multi-Paragraph Cells
        if line.startswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            parsed_rows = []
            for tl in table_lines:
                cells = split_md_table_row(tl)
                if all(re.match(r"^:?-+:?$", c) for c in cells):
                    continue
                parsed_rows.append(cells)

            if parsed_rows:
                num_cols = max(len(r) for r in parsed_rows)
                col_widths_mm = compute_column_widths_mm(parsed_rows, net_width_mm)
                tbl = doc.add_table(rows=len(parsed_rows), cols=num_cols)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                enforce_table_fixed_widths(tbl, col_widths_mm)

                for r_idx, row_data in enumerate(parsed_rows):
                    row = tbl.rows[r_idx]
                    is_header = r_idx == 0
                    is_last = r_idx == len(parsed_rows) - 1
                    set_row_cant_split_and_header(row, is_header=is_header)
                    row_bg = "EFF6FF" if is_header else ("FFFFFF" if r_idx % 2 == 1 else "F8FAFC")

                    for c_idx in range(num_cols):
                        cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
                        cell = row.cells[c_idx]
                        set_cell_exact_width(cell, col_widths_mm[c_idx])
                        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER if is_header else WD_ALIGN_VERTICAL.TOP
                        set_cell_margins(cell, top=110, bottom=110, left=120, right=120)
                        set_cell_shading(cell, row_bg)

                        if is_header:
                            set_cell_borders(
                                cell,
                                top={"val": "single", "sz": 12, "color": "1E3A8A"},
                                bottom={"val": "single", "sz": 8, "color": "1E3A8A"},
                                left={"val": "single", "sz": 4, "color": "CBD5E1"} if c_idx > 0 else {"val": "none"},
                                right={"val": "single", "sz": 4, "color": "CBD5E1"} if c_idx < num_cols - 1 else {"val": "none"},
                            )
                        else:
                            set_cell_borders(
                                cell,
                                top={"val": "single", "sz": 4, "color": "CBD5E1"},
                                bottom={
                                    "val": "single",
                                    "sz": 12 if is_last else 4,
                                    "color": "1E3A8A" if is_last else "CBD5E1",
                                },
                                left={"val": "single", "sz": 4, "color": "E2E8F0"} if c_idx > 0 else {"val": "none"},
                                right={"val": "single", "sz": 4, "color": "E2E8F0"} if c_idx < num_cols - 1 else {"val": "none"},
                            )

                        populate_table_cell(
                            cell,
                            cell_text,
                            omml_map,
                            is_header=is_header,
                            is_first_col=(c_idx == 0),
                        )

                sp = doc.add_paragraph()
                sp.paragraph_format.space_before = Pt(0)
                sp.paragraph_format.space_after = Pt(6)
            continue

        # 8. Footnote / Reference Definition ([^N]: ...)
        ref_match = re.match(r"^\[\^(\d+)\]:\s*(.+)$", line)
        if ref_match:
            ref_num = ref_match.group(1)
            ref_body = ref_match.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.left_indent = Pt(21)
            p.paragraph_format.first_line_indent = Pt(-21)

            r_num = p.add_run(f"[{ref_num}] ")
            set_east_asian_font(r_num, "Times New Roman", "宋体")
            r_num.font.size = Pt(9.5)
            r_num.bold = True
            r_num.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)

            add_rich_text(
                p,
                ref_body,
                omml_map=omml_map,
                base_size_pt=9.5,
                east_asian_font="宋体",
                base_color=RGBColor(0x47, 0x55, 0x69),
            )
            i += 1
            continue

        # 9. Unordered or Ordered List Items (- ..., * ..., 1. ...) & Task Checkboxes (- [ ] / - [x])
        list_match = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.+)$", raw_line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            marker = list_match.group(2)
            item_body = list_match.group(3).strip()
            nest_level = indent_spaces // 2

            is_unordered = marker in ("-", "*", "+")
            m_task = re.match(r"^(?:\[([ xX])\]|([☐☑]))\s+(.*)$", item_body)
            if m_task:
                sub_enum_counter = 0
                checked = (m_task.group(1) and m_task.group(1).lower() == "x") or m_task.group(2) == "☑"
                bullet_prefix = "☑  " if checked else "☐  "
                item_body = m_task.group(3).strip()
            elif is_unordered:
                sub_enum_counter = 0
                if nest_level == 0:
                    bullet_prefix = "•  "
                elif nest_level == 1:
                    bullet_prefix = "▸  "
                else:
                    bullet_prefix = "–  "
            else:
                if nest_level == 0:
                    sub_enum_counter = 0
                    bullet_prefix = f"{marker} "
                else:
                    sub_enum_counter += 1
                    num_str = marker.rstrip(".")
                    bullet_prefix = f"({num_str}) "

            hanging_pt = 14 if is_unordered else 16
            left_indent_pt = 18 + hanging_pt + (nest_level * 14)

            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.40
            p.paragraph_format.left_indent = Pt(left_indent_pt)
            p.paragraph_format.first_line_indent = Pt(-hanging_pt)

            rm = p.add_run(bullet_prefix)
            set_east_asian_font(rm, "Times New Roman", "黑体" if not is_unordered else "宋体")
            rm.font.size = Pt(10.5)
            rm.bold = not is_unordered
            rm.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

            add_rich_text(
                p,
                item_body,
                omml_map=omml_map,
                base_size_pt=10.5,
                east_asian_font="宋体",
                base_color=RGBColor(0x1E, 0x29, 0x3B),
            )
            i += 1
            continue

        # 10. Standard Body Paragraph (10.5pt 五号宋体, 2em = 21pt first-line indent)
        sub_enum_counter = 0
        is_no_indent_lead = bool(
            re.match(
                r"^(?:\*\*(\d+\.|评审|对照|日期|申请人|发明人|参考|表\s*\d+|图\s*\d+)|\*\*[^*]{1,20}\*\*\s*[：:]|\*\*[^*]{1,20}[：:]\*\*)",
                line,
            )
        )
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if is_no_indent_lead else WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(3 if is_no_indent_lead else 0)
        p.paragraph_format.space_after = Pt(5 if is_no_indent_lead else 6)
        p.paragraph_format.line_spacing = 1.42
        p.paragraph_format.first_line_indent = Pt(0 if (not indent_body or is_no_indent_lead) else 21)
        add_rich_text(
            p,
            line,
            omml_map=omml_map,
            base_size_pt=10.5,
            east_asian_font="宋体",
            base_color=RGBColor(0x1E, 0x29, 0x3B),
        )
        i += 1

    doc.save(docx_path)
    print(f"📄 [MD-to-DOCX] 已解析: {md_path} (含 {len(omml_map)} 个原生 OMML 公式)")
    print(f"✅ [MD-to-DOCX] 出版级 Word 文档导出成功！")
    print(f"📦 产物路径: {docx_path} ({os.path.getsize(docx_path) / 1024:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Compile Markdown / SSOT document to publication-grade Word (.docx)")
    parser.add_argument("input", help="Input Markdown file path (.md)")
    parser.add_argument("output", nargs="?", help="Optional output Word file path (.docx)")
    parser.add_argument("--header", default=None, help="Custom running header text")
    parser.add_argument("--no-indent", action="store_true", help="Disable 2em first-line indentation on body paragraphs")
    args = parser.parse_args()

    md_path = os.path.abspath(args.input)
    if not os.path.exists(md_path):
        print(f"Error: Input file not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        docx_path = os.path.abspath(args.output)
    else:
        docx_path = os.path.splitext(md_path)[0] + ".docx"

    build_docx(md_path, docx_path, custom_header=args.header, indent_body=not args.no_indent)


if __name__ == "__main__":
    main()
