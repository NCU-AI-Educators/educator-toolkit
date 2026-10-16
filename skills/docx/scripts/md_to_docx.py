#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSOT & Standard Markdown to Publication-Grade Word (.docx) Compiler
Usage:
    python3 md_to_docx.py <input.md> [output.docx] [--header TEXT] [--no-indent]
"""

import argparse
import os
import re
import sys
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls


CALLOUT_PALETTE = {
    "NOTE": ("2563EB", "F8FAFC"),
    "INFO": ("2563EB", "F8FAFC"),
    "TIP": ("059669", "F0FDF4"),
    "IMPORTANT": ("7C3AED", "F5F3FF"),
    "WARNING": ("D97706", "FFFBEB"),
    "CAUTION": ("DC2626", "FEF2F2"),
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


def set_cell_shading(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
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
    if tcBorders is None:
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
    trPr.append(OxmlElement("w:cantSplit"))
    if is_header:
        trPr.append(OxmlElement("w:tblHeader"))


def add_rich_text(
    paragraph,
    text,
    base_size_pt=11,
    east_asian_font="宋体",
    ascii_font="Times New Roman",
    base_color=RGBColor(0x1E, 0x29, 0x3B),
    base_bold=False,
):
    """
    Parse inline **bold**, *italic*, `code`, [^N] citations, and [label](url) links into Word runs.
    """
    def repl_link(m):
        label, url = m.group(1), m.group(2)
        if label.strip() == url.strip():
            return url.strip()
        return f"{label} ({url})"

    text = re.sub(r"\[([^\^\]]+)\]\(([^)]+)\)", repl_link, text)

    token_pattern = re.compile(
        r"(\*\*(?!\s)[^*\n]+?(?<!\s)\*\*|`[^`\n]+`|\[\^\d+\]|(?<!\*)\*(?!\s|\*)[^*\n]+?(?<!\s|\*)\*(?!\*))"
    )
    pos = 0
    for m in token_pattern.finditer(text):
        if m.start() > pos:
            plain = text[pos : m.start()]
            run = paragraph.add_run(plain)
            set_east_asian_font(run, ascii_font=ascii_font, east_asian_font=east_asian_font)
            run.font.size = Pt(base_size_pt)
            run.font.color.rgb = base_color
            run.bold = base_bold

        token = m.group(0)
        if token.startswith("**") and token.endswith("**"):
            inner = token[2:-2]
            sub_pos = 0
            for sm in re.finditer(r"\[\^(\d+)\]", inner):
                if sm.start() > sub_pos:
                    r = paragraph.add_run(inner[sub_pos : sm.start()])
                    set_east_asian_font(r, ascii_font=ascii_font, east_asian_font=east_asian_font)
                    r.font.size = Pt(base_size_pt)
                    r.font.color.rgb = base_color
                    r.bold = True
                cite_r = paragraph.add_run(f"[{sm.group(1)}]")
                set_east_asian_font(cite_r, ascii_font=ascii_font, east_asian_font=east_asian_font)
                cite_r.font.size = Pt(base_size_pt - 1)
                cite_r.font.superscript = True
                cite_r.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
                cite_r.bold = True
                sub_pos = sm.end()
            if sub_pos < len(inner):
                r = paragraph.add_run(inner[sub_pos:])
                set_east_asian_font(r, ascii_font=ascii_font, east_asian_font=east_asian_font)
                r.font.size = Pt(base_size_pt)
                r.font.color.rgb = base_color
                r.bold = True
        elif token.startswith("`") and token.endswith("`"):
            inner = token[1:-1]
            r = paragraph.add_run(inner)
            set_east_asian_font(r, ascii_font="Menlo", east_asian_font=east_asian_font)
            r.font.size = Pt(base_size_pt - 0.5)
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            r.bold = base_bold
        elif token.startswith("[^") and token.endswith("]"):
            num = token[2:-1]
            cite_r = paragraph.add_run(f"[{num}]")
            set_east_asian_font(cite_r, ascii_font=ascii_font, east_asian_font=east_asian_font)
            cite_r.font.size = Pt(base_size_pt - 1)
            cite_r.font.superscript = True
            cite_r.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)
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
        set_east_asian_font(run, ascii_font=ascii_font, east_asian_font=east_asian_font)
        run.font.size = Pt(base_size_pt)
        run.font.color.rgb = base_color
        run.bold = base_bold


def add_page_number_to_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("— ")
    set_east_asian_font(r1, "Times New Roman", "宋体")
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    fldSimple = OxmlElement("w:fldSimple")
    fldSimple.set(qn("w:instr"), "PAGE")
    p._p.append(fldSimple)

    r2 = p.add_run(" —")
    set_east_asian_font(r2, "Times New Roman", "宋体")
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)


def compute_column_widths_mm(parsed_rows, total_width_mm=160.0):
    num_cols = max(len(r) for r in parsed_rows)
    if num_cols <= 1:
        return [Mm(total_width_mm)]
    if num_cols == 4:
        return [Mm(32), Mm(56), Mm(36), Mm(36)]
    # Weight by average square-root of cell text length
    weights = []
    for c in range(num_cols):
        lengths = [max(len(r[c]), 4) for r in parsed_rows if c < len(r)]
        avg_len = sum(lengths) / max(len(lengths), 1)
        weights.append(max(avg_len ** 0.55, 2.5))
    total_w = sum(weights)
    return [Mm(total_width_mm * w / total_w) for w in weights]


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

    lines = [line.rstrip("\n") for line in raw_content.splitlines()]

    # Detect document title for running header
    doc_title = frontmatter_title
    for ln in lines:
        if ln.strip().startswith("# "):
            doc_title = ln.strip()[2:].strip()
            break

    doc = Document()

    # Configure base styles for Word / WPS compatibility
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(11)
    normal_rPr = normal_style.element.get_or_add_rPr()
    normal_rFonts = normal_rPr.find(qn("w:rFonts"))
    if normal_rFonts is None:
        normal_rFonts = OxmlElement("w:rFonts")
        normal_rPr.append(normal_rFonts)
    normal_rFonts.set(qn("w:ascii"), "Times New Roman")
    normal_rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal_rFonts.set(qn("w:eastAsia"), "宋体")

    for h_name, h_size, h_color in [
        ("Heading 1", 14, RGBColor(0x1E, 0x3A, 0x8A)),
        ("Heading 2", 12, RGBColor(0x1E, 0x29, 0x3B)),
        ("Heading 3", 11, RGBColor(0x33, 0x41, 0x55)),
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

    # Configure A4 page & margins
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(25)
    section.bottom_margin = Mm(25)
    section.left_margin = Mm(25)
    section.right_margin = Mm(25)

    # Header & Footer
    header_text = custom_header or (doc_title if doc_title else os.path.splitext(os.path.basename(md_path))[0])
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run(header_text[:48])
    set_east_asian_font(hr, "Times New Roman", "宋体")
    hr.font.size = Pt(9)
    hr.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    add_page_number_to_footer(section)

    i = 0
    n = len(lines)
    while i < n:
        raw_line = lines[i]
        line = raw_line.strip()
        if not line or line.startswith("<!--"):
            i += 1
            continue

        # 1. Fenced Code Block (``` or ~~~)
        if line.startswith("```") or line.startswith("~~~"):
            fence = line[:3]
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith(fence):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence

            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = tbl.cell(0, 0)
            cell.width = Mm(160)
            set_cell_shading(cell, "F8FAFC")
            set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
            set_cell_borders(
                cell,
                left={"val": "single", "sz": 12, "color": "64748B"},
                top={"val": "single", "sz": 4, "color": "CBD5E1"},
                right={"val": "single", "sz": 4, "color": "CBD5E1"},
                bottom={"val": "single", "sz": 4, "color": "CBD5E1"},
            )
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(0)
            cp.paragraph_format.space_after = Pt(0)
            cp.paragraph_format.line_spacing = 1.2
            cr = cp.add_run("\n".join(code_lines))
            set_east_asian_font(cr, "Menlo", "宋体")
            cr.font.size = Pt(9)
            cr.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

            sp = doc.add_paragraph()
            sp.paragraph_format.space_after = Pt(4)
            continue

        # 2. Document Title (# H1)
        if line.startswith("# "):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(16)
            p.paragraph_format.line_spacing = 1.25
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

            border_hex, bg_hex = CALLOUT_PALETTE.get(callout_type, ("2563EB", "F8FAFC"))
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = tbl.cell(0, 0)
            cell.width = Mm(160)
            set_cell_shading(cell, bg_hex)
            set_cell_margins(cell, top=160, bottom=160, left=220, right=200)
            set_cell_borders(
                cell,
                left={"val": "single", "sz": 24, "color": border_hex},
                top={"val": "single", "sz": 4, "color": "CBD5E1"},
                right={"val": "single", "sz": 4, "color": "CBD5E1"},
                bottom={"val": "single", "sz": 4, "color": "CBD5E1"},
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
                if re.match(r"^\d+\.\s", ql):
                    cp.paragraph_format.left_indent = Pt(14)
                    cp.paragraph_format.first_line_indent = Pt(-14)
                add_rich_text(
                    cp,
                    ql,
                    base_size_pt=10,
                    east_asian_font="宋体",
                    base_color=RGBColor(0x1E, 0x29, 0x3B),
                )

            sp = doc.add_paragraph()
            sp.paragraph_format.space_before = Pt(0)
            sp.paragraph_format.space_after = Pt(6)
            continue

        # 4. Headings (## H2, ### H3, #### H4)
        if line.startswith("## "):
            h2_text = line[3:].strip()
            p = doc.add_heading(level=1)
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.keep_with_next = True
            r = p.add_run(h2_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(14)
            r.bold = True
            r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            i += 1
            continue

        if line.startswith("### "):
            h3_text = line[4:].strip()
            p = doc.add_heading(level=2)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.keep_with_next = True
            r = p.add_run(h3_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(12)
            r.bold = True
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            i += 1
            continue

        if line.startswith("#### "):
            h4_text = line[5:].strip()
            p = doc.add_heading(level=3)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.keep_with_next = True
            r = p.add_run(h4_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(11)
            r.bold = True
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
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
        cap_match = re.match(r"^(?:\*\*|\*)((?:图|表)\s*[\d\-]+[^*]+)(?:\*\*|\*)$", line)
        if cap_match:
            cap_text = cap_match.group(1).strip()
            is_table_cap = cap_text.startswith("表")
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10 if is_table_cap else 2)
            p.paragraph_format.space_after = Pt(4 if is_table_cap else 10)
            if is_table_cap:
                p.paragraph_format.keep_with_next = True
            r = p.add_run(cap_text)
            set_east_asian_font(r, "Times New Roman", "黑体")
            r.font.size = Pt(10)
            r.bold = True
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
            i += 1
            continue

        # 7. Markdown Table (| ... |)
        if line.startswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            parsed_rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in cells):
                    continue
                parsed_rows.append(cells)

            if parsed_rows:
                num_cols = max(len(r) for r in parsed_rows)
                tbl = doc.add_table(rows=len(parsed_rows), cols=num_cols)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                col_widths = compute_column_widths_mm(parsed_rows, 160.0)

                for r_idx, row_data in enumerate(parsed_rows):
                    row = tbl.rows[r_idx]
                    is_header = r_idx == 0
                    is_last = r_idx == len(parsed_rows) - 1
                    set_row_cant_split_and_header(row, is_header=is_header)

                    for c_idx in range(num_cols):
                        cell_text = row_data[c_idx] if c_idx < len(row_data) else ""
                        cell = row.cells[c_idx]
                        cell.width = col_widths[c_idx]
                        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                        set_cell_margins(cell, top=100, bottom=100, left=110, right=110)

                        if is_header:
                            set_cell_shading(cell, "EFF6FF")
                            set_cell_borders(
                                cell,
                                top={"val": "single", "sz": 12, "color": "1E3A8A"},
                                bottom={"val": "single", "sz": 8, "color": "1E3A8A"},
                                left={"val": "none"},
                                right={"val": "none"},
                            )
                        else:
                            if r_idx % 2 == 0:
                                set_cell_shading(cell, "F8FAFC")
                            set_cell_borders(
                                cell,
                                top={"val": "single", "sz": 4, "color": "E2E8F0"},
                                bottom={
                                    "val": "single",
                                    "sz": 12 if is_last else 4,
                                    "color": "1E3A8A" if is_last else "E2E8F0",
                                },
                                left={"val": "none"},
                                right={"val": "none"},
                            )

                        cp = cell.paragraphs[0]
                        cp.paragraph_format.space_before = Pt(2)
                        cp.paragraph_format.space_after = Pt(2)
                        cp.paragraph_format.line_spacing = 1.25
                        if is_header:
                            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            add_rich_text(
                                cp,
                                cell_text,
                                base_size_pt=9.5,
                                east_asian_font="黑体",
                                base_color=RGBColor(0x1E, 0x3A, 0x8A),
                                base_bold=True,
                            )
                        else:
                            add_rich_text(
                                cp,
                                cell_text,
                                base_size_pt=9,
                                east_asian_font="宋体",
                                base_color=RGBColor(0x1E, 0x29, 0x3B),
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
            p.paragraph_format.left_indent = Pt(22)
            p.paragraph_format.first_line_indent = Pt(-22)

            r_num = p.add_run(f"[{ref_num}] ")
            set_east_asian_font(r_num, "Times New Roman", "宋体")
            r_num.font.size = Pt(9.5)
            r_num.bold = True
            r_num.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

            add_rich_text(
                p,
                ref_body,
                base_size_pt=9.5,
                east_asian_font="宋体",
                base_color=RGBColor(0x47, 0x55, 0x69),
            )
            i += 1
            continue

        # 9. Unordered or Ordered List Items (- ..., * ..., 1. ...)
        list_match = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.+)$", raw_line)
        if list_match:
            indent_spaces = len(list_match.group(1))
            marker = list_match.group(2)
            item_body = list_match.group(3).strip()
            level_offset = (indent_spaces // 2) * 14
            bullet_prefix = "• " if marker in ("-", "*", "+") else f"{marker} "

            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.4
            p.paragraph_format.left_indent = Pt(22 + level_offset)
            p.paragraph_format.first_line_indent = Pt(-14)

            rm = p.add_run(bullet_prefix)
            set_east_asian_font(rm, "Times New Roman", "宋体")
            rm.font.size = Pt(11)
            rm.bold = not marker.startswith(("-", "*", "+"))
            rm.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

            add_rich_text(
                p,
                item_body,
                base_size_pt=11,
                east_asian_font="宋体",
                base_color=RGBColor(0x1E, 0x29, 0x3B),
            )
            i += 1
            continue

        # 10. Standard Body Paragraph
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.45
        p.paragraph_format.first_line_indent = Pt(22 if indent_body else 0)
        add_rich_text(
            p,
            line,
            base_size_pt=11,
            east_asian_font="宋体",
            base_color=RGBColor(0x1E, 0x29, 0x3B),
        )
        i += 1

    doc.save(docx_path)
    print(f"📄 [MD-to-DOCX] 已解析: {md_path}")
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
