#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
textbook-svg CLI Tool: 双轨制高校教材与高密度写作配图脚手架、渲染与门禁校验器
==============================================================================
子命令:
  1. scaffold    : 一键生成双轨构图母版:
                   - Track A (纯 SVG 极简概念图): pillars / matrix / branch / contrast
                   - Track B (880px 高密度 1+N 图组 HTML): html-overview / html-stack /
                     html-primitives / html-matrix
  2. lint        : 扫描单个 SVG 或目录下所有 SVG，执行四项印刷安全门禁检查:
                   - XML 语法完整性
                   - 零 Emoji / 生僻技术符号 (防止 Typst/LaTeX PDF 出现豆腐块乱码)
                   - 文本内箭头 (──▶ / ◀──) 与底层矢量路径 (<path>/<line>) 方向一致性
                   - 卡片内部单行文本像素宽度防溢出估算
  3. render-html : 将单个或目录下所有高密度 .html 配图同时编译导出为:
                   (a) 2x Retina 高清 .png
                   (b) 100% 纯正原生矢量 .svg (基于 DOM 几何树与 Range 逐行文本提取，
                       支持 Flexbox/Grid、渐变、圆角裁剪与自动折行，并自动通过 SVG lint 门禁)
                   同时在渲染期执行三项写作配图质量门禁:
                   - 画布宽度防缩印门禁 (默认 ≤ 900px，标准推荐 880px)
                   - DOM 节点最小字号门禁 (默认 ≥ 12px，正文推荐 13.5px~14px)
                   - 容器水平溢出/截断检测 (scrollWidth <= clientWidth)
==============================================================================
"""

import argparse
import asyncio
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# 允许在教材 SVG 中安全使用的几何符号白名单
SAFE_SYMBOLS = {
    "\u2022",  # • BULLET
    "\u2500",  # ─ BOX DRAWINGS LIGHT HORIZONTAL
    "\u25b6",  # ▶ BLACK RIGHT-POINTING TRIANGLE
    "\u25c0",  # ◀ BLACK LEFT-POINTING TRIANGLE
    "\u25b2",  # ▲ BLACK UP-POINTING TRIANGLE
    "\u25bc",  # ▼ BLACK DOWN-POINTING TRIANGLE
    "\u2713",  # ✓ CHECK MARK
    "\u2717",  # ✗ BALLOT X
    "\u00d7",  # × MULTIPLICATION SIGN
    "\u00b1",  # ± PLUS-MINUS SIGN
    "\u2264",  # ≤ LESS-THAN OR EQUAL TO
    "\u2265",  # ≥ GREATER-THAN OR EQUAL TO
    "\u2260",  # ≠ NOT EQUAL TO
    "\u2208",  # ∈ ELEMENT OF
}

SVG_ARCHETYPES = ["pillars", "matrix", "branch", "contrast"]
HTML_ARCHETYPES = [
    "html-overview",
    "html-stack",
    "html-primitives",
    "html-matrix",
    "html-infographic",
]


def is_unsafe_symbol(ch: str) -> Optional[str]:
    """检查字符是否属于容易在 Typst/LaTeX PDF 中引起缺失乱码的 Emoji 或特殊符号"""
    if ch in SAFE_SYMBOLS:
        return None
    cp = ord(ch)
    if cp >= 0x1F000:
        return f"Emoji 字符 U+{cp:04X} ({ch})"
    if 0x2300 <= cp <= 0x23FF:
        return f"杂项技术符号 U+{cp:04X} ({ch})，正文字体常缺失字形"
    if 0x2600 <= cp <= 0x27BF:
        return f"装饰符号/Dingbat U+{cp:04X} ({ch})"
    if 0x2B00 <= cp <= 0x2BFF:
        return f"扩展箭头/几何符号 U+{cp:04X} ({ch})"
    if cp in (0x200D, 0xFE0E, 0xFE0F):
        return f"零宽连字符/变体选择符 U+{cp:04X}"
    return None


def estimate_text_px(text: str, font_size: float) -> float:
    """估算中英文混排单行文本的渲染像素宽度"""
    width = 0.0
    for ch in text:
        cp = ord(ch)
        if (
            0x4E00 <= cp <= 0x9FFF
            or 0x3000 <= cp <= 0x303F
            or 0xFF00 <= cp <= 0xFFEF
        ):
            width += font_size * 1.0
        elif ch == " ":
            width += font_size * 0.28
        elif ch in ("|", "(", ")", "[", "]", ".", ",", ":", ";", "/", "'", '"'):
            width += font_size * 0.35
        elif ch in ("•", "▶", "◀", "▲", "▼", "─"):
            width += font_size * 0.55
        else:
            width += font_size * 0.56
    return width


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def extract_horizontal_flows(root: ET.Element) -> List[Tuple[float, float, float]]:
    """
    提取画布中具有明显水平跨度 (>100px) 的 <line> 或 <path> 线段:
    返回列表 [(y_level, x_start, x_end), ...]
    """
    flows: List[Tuple[float, float, float]] = []
    for elem in root.iter():
        tag = strip_ns(elem.tag)
        if tag == "line":
            try:
                x1 = float(elem.attrib.get("x1", "0"))
                y1 = float(elem.attrib.get("y1", "0"))
                x2 = float(elem.attrib.get("x2", "0"))
                y2 = float(elem.attrib.get("y2", "0"))
                if abs(y1 - y2) <= 10 and abs(x2 - x1) >= 100:
                    flows.append(((y1 + y2) / 2.0, x1, x2))
            except ValueError:
                pass
        elif tag == "path":
            d = elem.attrib.get("d", "")
            pts = re.findall(r"[ML]\s*(-?\d+(?:\.\d+)?)[,\s]+(-?\d+(?:\.\d+)?)", d)
            coords = [(float(x), float(y)) for x, y in pts]
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                if abs(y1 - y2) <= 10 and abs(x2 - x1) >= 100:
                    flows.append(((y1 + y2) / 2.0, x1, x2))
    return flows


def lint_single_svg(svg_path: Path) -> Dict[str, Any]:
    """对单个 SVG 文件执行四项印刷安全门禁检查"""
    issues: List[Dict[str, Any]] = []
    try:
        raw_text = svg_path.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "file": str(svg_path),
            "valid": False,
            "issues": [{"type": "encoding_error", "severity": "error", "message": str(e)}],
        }

    # 1. 扫描非法 Emoji 与特殊 Unicode 符号
    for line_no, line in enumerate(raw_text.splitlines(), start=1):
        for ch in line:
            reason = is_unsafe_symbol(ch)
            if reason:
                issues.append({
                    "type": "unsafe_unicode",
                    "severity": "error",
                    "line": line_no,
                    "message": f"检测到不安全字符: {reason}，可能导致 PDF 编译乱码或豆腐块",
                })

    # 2. XML 语法解析
    try:
        root = ET.fromstring(raw_text)
    except ET.ParseError as e:
        issues.append({
            "type": "xml_parse_error",
            "severity": "error",
            "message": f"SVG XML 解析失败: {e}",
        })
        return {"file": str(svg_path), "valid": False, "issues": issues}

    # 3. 检查文本内嵌箭头方向是否与同高度矢量路径方向冲突，并检查是否存在图内硬编码图编号
    fig_num_re = re.compile(
        r"(?:^|[\s(（【\[|｜·:：见])"
        r"((?:子)?图\s*(?:[0-9]+(?:\.[0-9]+)?[a-zA-Z]?|X[a-zA-Z]?)|Fig(?:ure)?\.?\s*[0-9]+[a-zA-Z]?)"
        r"(?=$|[\s)）】\]|｜·:：、，。~～\-—])"
    )
    flows = extract_horizontal_flows(root)
    for elem in root.iter():
        if strip_ns(elem.tag) == "text":
            full_text = "".join(elem.itertext()).strip()
            m_fig = fig_num_re.search(full_text)
            if m_fig:
                issues.append({
                    "type": "hardcoded_figure_number",
                    "severity": "warning",
                    "message": (
                        f"检测到图内硬编码图编号 '{m_fig.group(1)}' (文本: '{full_text[:36]}'): "
                        f"图编号应由正文题注控制，请移除图内编号以免正文调整顺序时重绘"
                    ),
                })
            try:
                y_text = float(elem.attrib.get("y", "-999"))
            except ValueError:
                continue
            for y_flow, x_start, x_end in flows:
                if abs(y_text - y_flow) <= 22:
                    if x_start > x_end and ("▶" in full_text or "->" in full_text or "→" in full_text):
                        issues.append({
                            "type": "arrow_direction_conflict",
                            "severity": "error",
                            "message": (
                                f"方向冲突: 矢量路径在 y={y_flow:.0f} 处从右向左 ({x_start:.0f} -> {x_end:.0f})，"
                                f"但关联文本却使用了向右箭头: '{full_text}'（应翻转使用 ◀──）"
                            ),
                        })
                    elif x_end > x_start and ("◀" in full_text or "<-" in full_text or "←" in full_text):
                        issues.append({
                            "type": "arrow_direction_conflict",
                            "severity": "error",
                            "message": (
                                f"方向冲突: 矢量路径在 y={y_flow:.0f} 处从左向右 ({x_start:.0f} -> {x_end:.0f})，"
                                f"但关联文本却使用了向左箭头: '{full_text}'"
                            ),
                        })

    # 4. 检查手工 SVG 卡片 (<g> 内含 <rect>) 内部单行文本像素宽度是否超框
    # 注：由 DOM-to-SVG 引擎自动折行导出的 SVG 带有 data-generator="textbook-svg-dom2svg"，已在 DOM 阶段完成像素级溢出校验
    if root.attrib.get("data-generator") != "textbook-svg-dom2svg":
        for g in root.iter():
            if strip_ns(g.tag) != "g":
                continue
            rects = [c for c in g if strip_ns(c.tag) == "rect"]
            if not rects:
                continue
            try:
                card_width = float(rects[0].attrib.get("width", "0"))
            except ValueError:
                continue
            if card_width <= 0:
                continue

            for t in g:
                if strip_ns(t.tag) != "text":
                    continue
                try:
                    fs = float(t.attrib.get("font-size", "13").replace("px", ""))
                    x_pad = float(t.attrib.get("x", "12"))
                except ValueError:
                    fs, x_pad = 13.0, 12.0
                anchor = t.attrib.get("text-anchor", "start")

                tspans = [c for c in t if strip_ns(c.tag) == "tspan" and "x" in c.attrib]
                if tspans:
                    for ts in tspans:
                        line_str = "".join(ts.itertext()).strip()
                        est_w = estimate_text_px(line_str, fs)
                        avail_w = card_width if anchor == "middle" else (card_width - x_pad - 6)
                        if est_w > avail_w:
                            issues.append({
                                "type": "text_overflow_risk",
                                "severity": "warning",
                                "message": (
                                    f"文本超框预警: '{line_str}' 估算宽度 {est_w:.1f}px "
                                    f"超出卡片可用宽度 {avail_w:.1f}px (卡片宽 {card_width:.0f}px)"
                                ),
                            })
                else:
                    line_str = "".join(t.itertext()).strip()
                    est_w = estimate_text_px(line_str, fs)
                    avail_w = (card_width - 10) if anchor == "middle" else (card_width - x_pad - 6)
                    if est_w > avail_w:
                        issues.append({
                            "type": "text_overflow_risk",
                            "severity": "warning",
                            "message": (
                                f"标题/文本超框预警: '{line_str}' 估算宽度 {est_w:.1f}px "
                                f"超出卡片可用宽度 {avail_w:.1f}px (卡片宽 {card_width:.0f}px)"
                            ),
                        })

    has_error = any(i["severity"] == "error" for i in issues)
    return {
        "file": str(svg_path),
        "valid": not has_error,
        "issue_count": len(issues),
        "issues": issues,
    }


def extract_archetype_code(archetype: str, feedback_loop: bool = False) -> str:
    """从 references/ 提取对应 SVG 或高密度 HTML 母版源码"""
    ref_dir = Path(__file__).resolve().parent.parent / "references"
    if archetype in SVG_ARCHETYPES:
        ref_path = ref_dir / "archetypes.md"
        content = ref_path.read_text(encoding="utf-8")
        blocks = re.findall(r"```xml\n(<svg[\s\S]*?</svg>)\n```", content)
        idx_map = {"pillars": 0, "matrix": 1, "branch": 2, "contrast": 3}
        svg_code = blocks[idx_map[archetype]]

        if archetype == "pillars" and not feedback_loop:
            svg_code = svg_code.replace(
                'viewBox="0 0 760 250" width="760" height="250"',
                'viewBox="0 0 760 212" width="760" height="212"',
            )
            svg_code = re.sub(r"\n  <!-- 可选：底部反馈闭环[\s\S]*?(?=</svg>)", "\n", svg_code)
        return svg_code + "\n"
    else:
        ref_path = ref_dir / "high_density_templates.md"
        content = ref_path.read_text(encoding="utf-8")
        blocks = re.findall(r"```html\n(<!DOCTYPE html>[\s\S]*?</html>)\n```", content)
        idx_map = {
            "html-overview": 0,
            "html-stack": 1,
            "html-primitives": 2,
            "html-matrix": 3,
            "html-infographic": 4,
        }
        return blocks[idx_map[archetype]] + "\n"


DOM_TO_SVG_JS = r"""
() => {
  const root = document.querySelector('#capture-target') || document.querySelector('figure') || document.body;

  // 1. 净化文本节点中的 Emoji 与非常规箭头符号，保证导出的 SVG 100% 兼容 Typst/LaTeX 印刷字体并重新触发浏览器精确排版
  const REPLACE_MAP = {
    '⬇': '▼',
    '⬆': '▲',
    '⬅': '◀',
    '➡': '▶',
    '➔': '▶',
    '➜': '▶',
    '→': '▶',
    '←': '◀',
    '①': '(1)',
    '②': '(2)',
    '③': '(3)',
    '④': '(4)',
    '⑤': '(5)',
    '⑥': '(6)'
  };

  function sanitizeText(str) {
    let out = '';
    for (const ch of str) {
      if (REPLACE_MAP[ch]) {
        out += REPLACE_MAP[ch];
        continue;
      }
      const cp = ch.codePointAt(0);
      // 过滤 Emoji、Dingbats、杂项技术符号与变体选择符
      if (
        cp >= 0x1F000 ||
        (cp >= 0x2300 && cp <= 0x23FF) ||
        (cp >= 0x2600 && cp <= 0x27BF) ||
        (cp >= 0x2B00 && cp <= 0x2BFF) ||
        cp === 0x200D || cp === 0xFE0E || cp === 0xFE0F
      ) {
        continue;
      }
      out += ch;
    }
    // 清理因移除行首 Emoji 留下的多余前导空格
    return out.replace(/^\s+/, (m) => m.length > 0 ? '' : '');
  }

  const textWalker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  let tn = textWalker.nextNode();
  while (tn) {
    textNodes.push(tn);
    tn = textWalker.nextNode();
  }
  for (const node of textNodes) {
    if (node.nodeValue && node.nodeValue.trim().length > 0) {
      const hasPrevInline = node.previousSibling && node.previousSibling.nodeType === Node.ELEMENT_NODE;
      let cleaned = node.nodeValue;
      for (const [k, v] of Object.entries(REPLACE_MAP)) {
        cleaned = cleaned.split(k).join(v);
      }
      let res = '';
      for (const ch of cleaned) {
        const cp = ch.codePointAt(0);
        if (
          cp >= 0x1F000 ||
          (cp >= 0x2300 && cp <= 0x23FF) ||
          (cp >= 0x2600 && cp <= 0x27BF) ||
          (cp >= 0x2B00 && cp <= 0x2BFF) ||
          cp === 0x200D || cp === 0xFE0E || cp === 0xFE0F
        ) {
          continue;
        }
        res += ch;
      }
      if (!hasPrevInline) {
        res = res.replace(/^ +/, '');
      }
      node.nodeValue = res;
    }
  }

  const rootRect = root.getBoundingClientRect();
  const W = Math.round(rootRect.width * 10) / 10;
  const H = Math.round(rootRect.height * 10) / 10;

  function parseColor(cssColor) {
    if (!cssColor || cssColor === 'transparent' || cssColor === 'rgba(0, 0, 0, 0)') {
      return null;
    }
    const m = cssColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!m) return { hex: cssColor, opacity: 1.0 };
    const r = parseInt(m[1], 10).toString(16).padStart(2, '0');
    const g = parseInt(m[2], 10).toString(16).padStart(2, '0');
    const b = parseInt(m[3], 10).toString(16).padStart(2, '0');
    const a = m[4] !== undefined ? parseFloat(m[4]) : 1.0;
    if (a <= 0.01) return null;
    return { hex: `#${r}${g}${b}`.toUpperCase(), opacity: Math.round(a * 100) / 100 };
  }

  function parseGradient(bgImage) {
    if (!bgImage || !bgImage.includes('linear-gradient')) return null;
    const rgbMatches = [...bgImage.matchAll(/rgba?\(\d+,\s*\d+,\s*\d+(?:,\s*[\d.]+)?\)/g)];
    if (rgbMatches.length >= 2) {
      const c1 = parseColor(rgbMatches[0][0]);
      const c2 = parseColor(rgbMatches[rgbMatches.length - 1][0]);
      if (c1 && c2) return [c1.hex, c2.hex];
    }
    return null;
  }

  function extractTextSegments(textNode, parentStyle) {
    const raw = textNode.nodeValue;
    if (!raw || raw.trim().length === 0) return [];
    const range = document.createRange();
    range.selectNodeContents(textNode);
    const rects = range.getClientRects();
    if (rects.length === 0) return [];

    const fs = parseFloat(parentStyle.fontSize) || 13;
    const fw = parentStyle.fontWeight || '400';
    const col = parseColor(parentStyle.color) || { hex: '#0F172A', opacity: 1.0 };

    // 单行无折行文本节点
    if (rects.length === 1) {
      const r = rects[0];
      const trimmed = raw.replace(/\s+/g, ' ');
      if (!trimmed.trim()) return [];
      // 若左侧存在前导空格，测量首个非空字符的精确起点 x
      let firstNonSpace = 0;
      while (firstNonSpace < raw.length && /\s/.test(raw[firstNonSpace])) firstNonSpace++;
      let xStart = r.left;
      if (firstNonSpace > 0 && firstNonSpace < raw.length) {
        const cr = document.createRange();
        cr.setStart(textNode, firstNonSpace);
        cr.setEnd(textNode, raw.length);
        const cRect = cr.getBoundingClientRect();
        if (cRect.width > 0) xStart = cRect.left;
      }
      return [{
        text: trimmed.trim(),
        x: Math.round((xStart - rootRect.left) * 10) / 10,
        y: Math.round((r.top - rootRect.top + r.height * 0.5 + fs * 0.33) * 10) / 10,
        fontSize: fs,
        fontWeight: fw,
        color: col.hex
      }];
    }

    // 多行自动折行文本节点：逐字符测量其所属行顶坐标并聚合为独立行片段
    const lines = [];
    const charRange = document.createRange();
    for (let i = 0; i < raw.length; i++) {
      const ch = raw[i];
      if (ch === '\n' || ch === '\r') continue;
      charRange.setStart(textNode, i);
      charRange.setEnd(textNode, i + 1);
      const cr = charRange.getBoundingClientRect();
      if (cr.width === 0 && cr.height === 0) continue;

      let curLine = lines.length > 0 ? lines[lines.length - 1] : null;
      if (!curLine || Math.abs(cr.top - curLine.top) > 4.5) {
        if (/\s/.test(ch)) continue;
        lines.push({
          chars: ch,
          left: cr.left,
          top: cr.top,
          height: cr.height
        });
      } else {
        curLine.chars += ch;
      }
    }

    return lines
      .map(ln => ({
        text: ln.chars.replace(/\s+/g, ' ').trim(),
        x: Math.round((ln.left - rootRect.left) * 10) / 10,
        y: Math.round((ln.top - rootRect.top + ln.height * 0.5 + fs * 0.33) * 10) / 10,
        fontSize: fs,
        fontWeight: fw,
        color: col.hex
      }))
      .filter(s => s.text.length > 0);
  }

  function serializeElement(el) {
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) {
      return null;
    }
    const r = el.getBoundingClientRect();
    const x = Math.round((r.left - rootRect.left) * 10) / 10;
    const y = Math.round((r.top - rootRect.top) * 10) / 10;
    const w = Math.round(r.width * 10) / 10;
    const h = Math.round(r.height * 10) / 10;

    const bg = parseColor(style.backgroundColor);
    const grad = parseGradient(style.backgroundImage);
    const rxRaw = parseFloat(style.borderTopLeftRadius) || 0;
    const rx = Math.min(Math.round(rxRaw * 10) / 10, Math.round(Math.min(w, h) / 2 * 10) / 10);

    const bt = parseFloat(style.borderTopWidth) || 0;
    const br = parseFloat(style.borderRightWidth) || 0;
    const bb = parseFloat(style.borderBottomWidth) || 0;
    const bl = parseFloat(style.borderLeftWidth) || 0;

    const borders = {
      top: bt > 0 ? { width: bt, style: style.borderTopStyle, color: parseColor(style.borderTopColor) } : null,
      right: br > 0 ? { width: br, style: style.borderRightStyle, color: parseColor(style.borderRightColor) } : null,
      bottom: bb > 0 ? { width: bb, style: style.borderBottomStyle, color: parseColor(style.borderBottomColor) } : null,
      left: bl > 0 ? { width: bl, style: style.borderLeftStyle, color: parseColor(style.borderLeftColor) } : null,
    };

    const clip = (style.overflow === 'hidden' || style.overflowX === 'hidden') && rx > 0;
    const children = [];

    for (const child of el.childNodes) {
      if (child.nodeType === Node.ELEMENT_NODE) {
        const cNode = serializeElement(child);
        if (cNode) children.push({ type: 'element', data: cNode });
      } else if (child.nodeType === Node.TEXT_NODE) {
        const segs = extractTextSegments(child, style);
        for (const s of segs) {
          children.push({ type: 'text', data: s });
        }
      }
    }

    return { x, y, w, h, rx, bg, grad, borders, clip, children };
  }

  return {
    width: W,
    height: H,
    tree: serializeElement(root)
  };
}
"""


def compile_dom_tree_to_svg(dom_data: Dict[str, Any]) -> str:
    """将浏览器提取的精确 DOM 几何与文本树编译为纯正原生 SVG XML"""
    w = dom_data["width"]
    h = dom_data["height"]
    tree = dom_data["tree"]

    defs_list: List[str] = [
        "    <style>",
        "      text { font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', -apple-system, sans-serif; }",
        "    </style>",
    ]
    body_lines: List[str] = []
    grad_counter = 0
    clip_counter = 0

    def render_node(node: Dict[str, Any], indent: str = "  ") -> None:
        nonlocal grad_counter, clip_counter
        x, y, nw, nh, rx = node["x"], node["y"], node["w"], node["h"], node["rx"]
        if nw <= 0 or nh <= 0:
            return

        # 1. 绘制背景填充或渐变
        fill_attr = None
        opacity_attr = ""
        if node["grad"]:
            grad_counter += 1
            gid = f"grad-{grad_counter}"
            c1, c2 = node["grad"]
            defs_list.append(
                f'    <linearGradient id="{gid}" x1="0%" y1="0%" x2="100%" y2="0%">'
                f'<stop offset="0%" stop-color="{c1}"/><stop offset="100%" stop-color="{c2}"/>'
                f"</linearGradient>"
            )
            fill_attr = f"url(#{gid})"
        elif node["bg"]:
            fill_attr = node["bg"]["hex"]
            if node["bg"]["opacity"] < 1.0:
                opacity_attr = f' fill-opacity="{node["bg"]["opacity"]}"'

        b_top = node["borders"]["top"]
        b_right = node["borders"]["right"]
        b_bottom = node["borders"]["bottom"]
        b_left = node["borders"]["left"]

        uniform_border = (
            b_top
            and b_right
            and b_bottom
            and b_left
            and b_top["width"] == b_right["width"] == b_bottom["width"] == b_left["width"]
            and b_top["color"]
            and b_right["color"]
            and b_bottom["color"]
            and b_left["color"]
            and b_top["color"]["hex"] == b_right["color"]["hex"] == b_bottom["color"]["hex"] == b_left["color"]["hex"]
        )

        rx_str = f' rx="{rx}" ry="{rx}"' if rx > 0 else ""

        if fill_attr:
            body_lines.append(
                f'{indent}<rect x="{x}" y="{y}" width="{nw}" height="{nh}"{rx_str} '
                f'fill="{fill_attr}"{opacity_attr}/>'
            )

        # 2. 若容器具有圆角裁剪 (overflow: hidden)，为子元素创建 clipPath
        child_indent = indent
        if node["clip"] and node["children"]:
            clip_counter += 1
            cid = f"clip-{clip_counter}"
            defs_list.append(
                f'    <clipPath id="{cid}">'
                f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}"{rx_str}/>'
                f"</clipPath>"
            )
            body_lines.append(f'{indent}<g clip-path="url(#{cid})">')
            child_indent = indent + "  "

        # 3. 递归绘制子节点与文本行
        for ch in node["children"]:
            if ch["type"] == "element":
                render_node(ch["data"], child_indent)
            elif ch["type"] == "text":
                t = ch["data"]
                escaped = html.escape(t["text"], quote=False)
                fw_val = str(t["fontWeight"])
                fw_attr = ' font-weight="bold"' if fw_val in ("bold", "600", "700", "800", "900") else ""
                body_lines.append(
                    f'{child_indent}<text x="{t["x"]}" y="{t["y"]}" '
                    f'font-size="{t["fontSize"]}"{fw_attr} fill="{t["color"]}">{escaped}</text>'
                )

        if node["clip"] and node["children"]:
            body_lines.append(f"{indent}</g>")

        # 4. 在顶层绘制边框（保证圆角描边不被内部顶栏背景遮盖）
        if uniform_border:
            bw = b_top["width"]
            bcol = b_top["color"]["hex"]
            dash = ' stroke-dasharray="5,3"' if b_top["style"] == "dashed" else ""
            half = round(bw / 2.0, 2)
            bx = round(x + half, 2)
            by = round(y + half, 2)
            bw_rect = round(max(0.0, nw - bw), 2)
            bh_rect = round(max(0.0, nh - bw), 2)
            brx = round(max(0.0, rx - half), 2)
            brx_str = f' rx="{brx}" ry="{brx}"' if brx > 0 else ""
            body_lines.append(
                f'{indent}<rect x="{bx}" y="{by}" width="{bw_rect}" height="{bh_rect}"{brx_str} '
                f'fill="none" stroke="{bcol}" stroke-width="{bw}"{dash}/>'
            )
        else:
            if b_top and b_top["color"]:
                bw = b_top["width"]
                bcol = b_top["color"]["hex"]
                dash = ' stroke-dasharray="5,3"' if b_top["style"] == "dashed" else ""
                ly = round(y + bw / 2.0, 2)
                body_lines.append(
                    f'{indent}<line x1="{x}" y1="{ly}" x2="{round(x + nw, 2)}" y2="{ly}" '
                    f'stroke="{bcol}" stroke-width="{bw}"{dash}/>'
                )
            if b_bottom and b_bottom["color"]:
                bw = b_bottom["width"]
                bcol = b_bottom["color"]["hex"]
                dash = ' stroke-dasharray="5,3"' if b_bottom["style"] == "dashed" else ""
                ly = round(y + nh - bw / 2.0, 2)
                body_lines.append(
                    f'{indent}<line x1="{x}" y1="{ly}" x2="{round(x + nw, 2)}" y2="{ly}" '
                    f'stroke="{bcol}" stroke-width="{bw}"{dash}/>'
                )
            if b_left and b_left["color"]:
                bw = b_left["width"]
                bcol = b_left["color"]["hex"]
                dash = ' stroke-dasharray="5,3"' if b_left["style"] == "dashed" else ""
                lx = round(x + bw / 2.0, 2)
                body_lines.append(
                    f'{indent}<line x1="{lx}" y1="{y}" x2="{lx}" y2="{round(y + nh, 2)}" '
                    f'stroke="{bcol}" stroke-width="{bw}"{dash}/>'
                )
            if b_right and b_right["color"]:
                bw = b_right["width"]
                bcol = b_right["color"]["hex"]
                dash = ' stroke-dasharray="5,3"' if b_right["style"] == "dashed" else ""
                lx = round(x + nw - bw / 2.0, 2)
                body_lines.append(
                    f'{indent}<line x1="{lx}" y1="{y}" x2="{lx}" y2="{round(y + nh, 2)}" '
                    f'stroke="{bcol}" stroke-width="{bw}"{dash}/>'
                )

    if tree:
        render_node(tree, "  ")

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'data-generator="textbook-svg-dom2svg" style="background:#FFFFFF;">',
        "  <defs>",
        *defs_list,
        "  </defs>",
        *body_lines,
        "</svg>",
        "",
    ]
    return "\n".join(svg_lines)


async def render_and_check_html_files(
    html_files: List[Path],
    scale: int = 2,
    max_width: float = 900.0,
    min_font: float = 12.0,
    export_svg: bool = True,
) -> List[Dict[str, Any]]:
    """使用 Playwright 渲染 HTML 为 2x Retina PNG 与纯正原生矢量 SVG，并执行排版门禁检查"""
    from playwright.async_api import async_playwright

    results: List[Dict[str, Any]] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1100, "height": 1800},
            device_scale_factor=scale,
        )
        for hp in html_files:
            issues: List[Dict[str, Any]] = []
            png_path = hp.with_suffix(".png")
            svg_path = hp.with_suffix(".svg")
            await page.goto(f"file://{hp.resolve()}", wait_until="networkidle")
            await page.wait_for_timeout(180)

            el = await page.query_selector("#capture-target")
            if not el:
                el = await page.query_selector("figure")
            if not el:
                el = await page.query_selector("body")

            box = await el.bounding_box()
            w = box["width"] if box else 0.0
            h = box["height"] if box else 0.0

            # 门禁 1: 画布宽度检查（严防过宽画布导致嵌入正文后缩印字小）
            if w > max_width + 120:
                issues.append({
                    "type": "canvas_too_wide",
                    "severity": "error",
                    "message": (
                        f"画布宽度过宽 ({w:.0f}px > {max_width:.0f}px)，嵌入 A4/Markdown 正文后"
                        f"会导致字号严重缩水！请固定画布宽度为 880px 或拆分为 1+N 子图。"
                    ),
                })
            elif w > max_width:
                issues.append({
                    "type": "canvas_width_warning",
                    "severity": "warning",
                    "message": f"画布宽度 ({w:.0f}px) 略超推荐值 {max_width:.0f}px，建议锁定 880px。",
                })

            # 门禁 2 & 3: 最小字号检查与水平溢出截断检查
            dom_audit = await page.evaluate(
                """(minFont) => {
                    const root = document.querySelector('#capture-target') || document.querySelector('figure') || document.body;
                    const smallFonts = [];
                    const overflows = [];
                    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
                    let node = walker.currentNode;
                    while (node) {
                        const style = window.getComputedStyle(node);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            const hasDirectText = Array.from(node.childNodes).some(
                                c => c.nodeType === Node.TEXT_NODE && c.textContent.trim().length > 0
                            );
                            if (hasDirectText) {
                                const fs = parseFloat(style.fontSize);
                                if (fs < minFont) {
                                    smallFonts.push({
                                        tag: node.tagName.toLowerCase(),
                                        fontSize: fs,
                                        text: node.textContent.trim().slice(0, 36)
                                    });
                                }
                            }
                            if (node.clientWidth > 20 && node.scrollWidth > node.clientWidth + 3) {
                                overflows.push({
                                    tag: node.tagName.toLowerCase(),
                                    className: node.className || '',
                                    clientWidth: node.clientWidth,
                                    scrollWidth: node.scrollWidth,
                                    text: node.textContent.trim().slice(0, 36)
                                });
                            }
                        }
                        node = walker.nextNode();
                    }
                    return { smallFonts, overflows };
                }""",
                min_font,
            )

            for sf in dom_audit["smallFonts"][:5]:
                issues.append({
                    "type": "font_too_small",
                    "severity": "warning",
                    "message": (
                        f"检测到过小字号 ({sf['fontSize']}px < {min_font}px): "
                        f"<{sf['tag']}> '{sf['text']}'"
                    ),
                })

            for ov in dom_audit["overflows"][:5]:
                issues.append({
                    "type": "horizontal_overflow",
                    "severity": "error",
                    "message": (
                        f"检测到容器水平溢出 ({ov['scrollWidth']}px > {ov['clientWidth']}px): "
                        f"<{ov['tag']} class='{ov['className']}'> '{ov['text']}'"
                    ),
                })

            # 1. 先导出 2x Retina PNG
            await el.screenshot(path=str(png_path))

            # 2. 提取 DOM 几何树并编译为纯正原生矢量 SVG，随后执行 SVG 印刷安全校验
            svg_out_str: Optional[str] = None
            if export_svg:
                dom_data = await page.evaluate(DOM_TO_SVG_JS)
                svg_xml = compile_dom_tree_to_svg(dom_data)
                svg_path.write_text(svg_xml, encoding="utf-8")
                svg_out_str = str(svg_path)
                svg_lint = lint_single_svg(svg_path)
                for s_iss in svg_lint["issues"]:
                    issues.append(s_iss)

            has_error = any(i["severity"] == "error" for i in issues)
            results.append({
                "html_file": str(hp),
                "png_file": str(png_path),
                "svg_file": svg_out_str,
                "css_width": round(w, 1),
                "css_height": round(h, 1),
                "scale": scale,
                "valid": not has_error,
                "issues": issues,
            })
        await browser.close()
    return results


def cmd_lint(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    if not target.exists():
        sys.stderr.write(f"Error: 目标路径不存在: {target}\n")
        return 1

    svg_files = [target] if target.is_file() else sorted(target.rglob("*.svg"))
    results = [lint_single_svg(f) for f in svg_files]
    total_errors = sum(
        sum(1 for i in r["issues"] if i["severity"] == "error") for r in results
    )
    total_warnings = sum(
        sum(1 for i in r["issues"] if i["severity"] == "warning") for r in results
    )

    report = {
        "target": str(target),
        "files_checked": len(results),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "all_valid": total_errors == 0,
        "results": results,
    }

    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(
        f"[textbook-svg lint] 已检查 {len(results)} 个 SVG 文件 | "
        f"错误: {total_errors} | 预警: {total_warnings} | 报告已写入: {out_path}"
    )
    return 1 if total_errors > 0 else 0


def cmd_scaffold(args: argparse.Namespace) -> int:
    code = extract_archetype_code(args.archetype, args.feedback_loop)
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(code, encoding="utf-8")
    print(f"[textbook-svg scaffold] 已生成 '{args.archetype}' 母版骨架: {out_path}")
    return 0


def cmd_render_html(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    if not target.exists():
        sys.stderr.write(f"Error: 目标路径不存在: {target}\n")
        return 1

    html_files = [target] if target.is_file() else sorted(target.rglob("*.html"))
    if not html_files:
        sys.stderr.write(f"Error: 未找到任何 .html 文件: {target}\n")
        return 1

    results = asyncio.run(
        render_and_check_html_files(
            html_files,
            scale=args.scale,
            max_width=args.max_width,
            min_font=args.min_font,
            export_svg=not args.no_svg,
        )
    )
    total_errors = sum(
        sum(1 for i in r["issues"] if i["severity"] == "error") for r in results
    )
    total_warnings = sum(
        sum(1 for i in r["issues"] if i["severity"] == "warning") for r in results
    )

    for r in results:
        status = "PASS" if r["valid"] else "FAIL"
        svg_note = f" + {Path(r['svg_file']).name}" if r.get("svg_file") else ""
        print(
            f"[render-html {status}] {Path(r['png_file']).name}{svg_note} "
            f"({r['css_width']}x{r['css_height']} CSS px @{r['scale']}x) | "
            f"issues: {len(r['issues'])}"
        )
        for iss in r["issues"]:
            print(f"   - [{iss['severity'].upper()}] {iss['message']}")

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "target": str(target),
            "files_rendered": len(results),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "all_valid": total_errors == 0,
            "results": results,
        }
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[textbook-svg render-html] 门禁报告已写入: {out_path}")

    return 1 if total_errors > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="textbook-svg: 双轨制高校教材与高密度写作配图脚手架、渲染与门禁校验工具"
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    p_lint = subparsers.add_parser("lint", help="对 SVG 文件或目录执行印刷安全与排版门禁校验")
    p_lint.add_argument("target", help="要检查的 .svg 文件或目录路径")
    p_lint.add_argument("--output", required=True, help="校验结果 JSON 报告输出路径")

    p_scaf = subparsers.add_parser(
        "scaffold",
        help="生成双轨构图母版骨架 (SVG 极简母版 或 880px 高密度 HTML 母版)",
    )
    p_scaf.add_argument(
        "--archetype",
        choices=SVG_ARCHETYPES + HTML_ARCHETYPES,
        required=True,
        help=(
            "母版类型: "
            "SVG 轨 [pillars, matrix, branch, contrast] | "
            "880px 高密度 HTML 轨 [html-overview, html-stack, html-primitives, html-matrix]"
        ),
    )
    p_scaf.add_argument(
        "--feedback-loop",
        action="store_true",
        help="仅对 pillars 母版生效：附加底部从右向左的虚线验收闭环回路",
    )
    p_scaf.add_argument("--output", required=True, help="生成的 .svg 或 .html 文件输出路径")

    p_render = subparsers.add_parser(
        "render-html",
        help="将高密度 .html 配图同时编译为 2x Retina .png 与纯正原生矢量 .svg，并执行门禁校验",
    )
    p_render.add_argument("target", help="要渲染的 .html 文件或目录路径")
    p_render.add_argument("--scale", type=int, default=2, help="PNG 设备像素缩放倍率 (默认 2x Retina)")
    p_render.add_argument(
        "--max-width",
        type=float,
        default=900.0,
        help="画布最大允许 CSS 宽度 (默认 900px，标准推荐 880px，防缩印字小)",
    )
    p_render.add_argument(
        "--min-font",
        type=float,
        default=12.0,
        help="允许的最小文本字号 (默认 12px，正文推荐 13.5px~14px)",
    )
    p_render.add_argument(
        "--no-svg",
        action="store_true",
        help="仅导出 2x .png，跳过同步生成纯矢量 .svg",
    )
    p_render.add_argument("--output", help="可选：渲染门禁校验 JSON 报告输出路径")

    args = parser.parse_args()
    if args.subcommand == "lint":
        return cmd_lint(args)
    elif args.subcommand == "scaffold":
        return cmd_scaffold(args)
    elif args.subcommand == "render-html":
        return cmd_render_html(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
