#!/usr/bin/env python3
"""Reusable Python + Matplotlib vector primitives for Track C scientific paper schematics.

Aligned 100% with the `figures4papers` semantic academic color palette and typography
system so qualitative paper schematics (Fig. 1 / Fig. 2) and quantitative plots
(Fig. 3+) share identical visual DNA across Nature/Science/IEEE/CVPR/arXiv venues.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


PALETTE: dict[str, str] = {
    "ours_primary": "#0F4D92",      # Yale Deep Blue: Primary proposed model / path
    "ours_secondary": "#3775BA",    # Medium Academic Blue: Secondary track / module
    "positive_teal": "#2A8C82",     # Teal: Key domain operators / registers / manifolds
    "positive_green": "#5AA469",    # Sage Green: Verified improvement / positive branch
    "sota_red_dark": "#B64342",     # Deep Crimson: Baseline bottleneck / error / drift
    "sota_red_mid": "#D96B52",      # Terracotta: Secondary error / competing path
    "sota_coral": "#E5988B",        # Soft Coral: Subtle negative highlight / fill accent
    "baseline_amber": "#D49A35",    # Muted Gold: Stop-gradient gate / physical bridge
    "ablation_gray": "#A6AEB7",     # Cool Neutral Gray: Omitted / neutral structural items
    "dark_slate": "#4A5568",        # Slate: Frozen foundation layers / shared input frame
    "text_dark": "#1A202C",         # Ink Charcoal: Primary text
    "text_muted": "#334155",        # Muted Slate: Secondary annotations
}

VENUE_WIDTHS_IN: dict[str, float] = {
    "nature_double": 7.20,   # 183 mm full-page width (Nature / NMI / Nat. Commun.)
    "nature_single": 3.50,   # 89 mm single-column width
    "arxiv_a4": 6.37,        # Standard LaTeX article / arXiv textwidth
    "ieee_double": 7.16,     # IEEE Transactions double-column width
    "cvpr_double": 6.875,    # CVPR / ICCV / ECCV double-column textwidth
}


def _ceil_tenth(val: float) -> float:
    return math.ceil((val - 1e-9) * 10.0) / 10.0


def compute_font_budget(
    target_width_in: float,
    fig_width_in: float,
    min_print_pt: float = 6.0,
) -> dict[str, float]:
    """Compute reverse print-scale ratio and minimum source Matplotlib font sizes.

    Applies a +3% safety buffer on recommended source font tiers so minor canvas
    expansion from `bbox_inches="tight", pad_inches=0.04` still satisfies
    `fontsize * actual_scale >= min_print_pt` during PDF preflight checks.
    """
    if target_width_in <= 0 or fig_width_in <= 0 or min_print_pt <= 0:
        raise ValueError("target_width_in, fig_width_in, and min_print_pt must be > 0.")

    scale = target_width_in / fig_width_in
    strict_min_src_pt = _ceil_tenth(min_print_pt / scale)
    pad_factor = 1.03

    min_fine_pt = max(strict_min_src_pt, _ceil_tenth((min_print_pt * pad_factor) / scale))
    body_pt = _ceil_tenth((max(min_print_pt + 0.5, 6.5) * pad_factor) / scale)
    card_title_pt = _ceil_tenth((max(min_print_pt + 1.2, 7.2) * pad_factor) / scale)
    panel_header_pt = _ceil_tenth((max(min_print_pt + 2.2, 8.2) * pad_factor) / scale)
    panel_letter_pt = _ceil_tenth((max(min_print_pt + 4.5, 10.5) * pad_factor) / scale)

    return {
        "target_width_in": round(target_width_in, 4),
        "fig_width_in": round(fig_width_in, 4),
        "min_print_pt": round(min_print_pt, 4),
        "scale": round(scale, 6),
        "strict_min_src_pt": strict_min_src_pt,
        "min_fine_pt": min_fine_pt,
        "body_pt": body_pt,
        "card_title_pt": card_title_pt,
        "panel_header_pt": panel_header_pt,
        "panel_letter_pt": panel_letter_pt,
    }


def setup_publication_rcparams(base_font_pt: float = 12.5) -> None:
    """Configure Matplotlib for editable TrueType PDF (Type 42) and raw-text SVG export."""
    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": base_font_pt,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def rounded_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    facecolor: str = "#FFFFFF",
    edgecolor: str = "#CBD5E1",
    lw: float = 1.4,
    linestyle: str = "-",
    radius: float = 0.08,
    zorder: float = 2,
    alpha: float = 1.0,
) -> FancyBboxPatch:
    """Draw a sharp-edged rounded architectural module or container box."""
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        linestyle=linestyle,
        alpha=alpha,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#334155",
    lw: float = 1.6,
    style: str = "-|>",
    ls: str = "-",
    rad: float = 0.0,
    ms: float = 11.5,
    shrinkA: float = 0.0,
    shrinkB: float = 0.0,
    zorder: float = 5,
) -> FancyArrowPatch:
    """Draw a boundary-snapped vector arrow (`shrinkA=0, shrinkB=0` by default)."""
    patch = FancyArrowPatch(
        start,
        end,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle=style,
        mutation_scale=ms,
        linewidth=lw,
        linestyle=ls,
        color=color,
        shrinkA=shrinkA,
        shrinkB=shrinkB,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def _draw_overpass_halos(
    ax: plt.Axes,
    pts: Sequence[tuple[float, float]],
    overpass_pts: Iterable,
    *,
    overpass_bg: str,
    halo_lw: float,
    half_span: float,
    zorder: float,
) -> None:
    """Render white background bridge gaps along `pts` where crossing wires occur."""
    for item in overpass_pts:
        if (
            isinstance(item, (tuple, list))
            and len(item) == 2
            and isinstance(item[0], (tuple, list))
        ):
            (x1, y1), (x2, y2) = item
            ax.plot(
                [x1, x2],
                [y1, y2],
                color=overpass_bg,
                linewidth=halo_lw,
                solid_capstyle="butt",
                zorder=zorder,
            )
            continue

        cx, cy = float(item[0]), float(item[1])
        drawn = False
        for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
            dx, dy = x2 - x1, y2 - y1
            seg_len = math.hypot(dx, dy)
            if seg_len < 1e-9:
                continue
            ux, uy = dx / seg_len, dy / seg_len
            proj = (cx - x1) * ux + (cy - y1) * uy
            perp = abs((cx - x1) * (-uy) + (cy - y1) * ux)
            if -1e-3 <= proj <= seg_len + 1e-3 and perp <= 0.05:
                s0 = max(0.0, proj - half_span)
                s1 = min(seg_len, proj + half_span)
                ax.plot(
                    [x1 + ux * s0, x1 + ux * s1],
                    [y1 + uy * s0, y1 + uy * s1],
                    color=overpass_bg,
                    linewidth=halo_lw,
                    solid_capstyle="butt",
                    zorder=zorder,
                )
                drawn = True
                break
        if not drawn:
            ax.plot(
                [cx - half_span, cx + half_span],
                [cy, cy],
                color=overpass_bg,
                linewidth=halo_lw,
                solid_capstyle="butt",
                zorder=zorder,
            )


def ortho_arrow(
    ax: plt.Axes,
    pts: Sequence[tuple[float, float]],
    *,
    color: str = "#334155",
    lw: float = 1.6,
    ls: str = "-",
    ms: float = 11.5,
    zorder: float = 5,
    overpass_pts: Iterable | None = None,
    overpass_bg: str = "#FFFFFF",
    overpass_half_span: float = 0.11,
    overpass_lw_scale: float = 3.4,
) -> None:
    """Draw a 90-degree orthogonal polyline arrow with optional white overpass bridges.

    Args:
        pts: Waypoints `[(x0, y0), (x1, y1), ..., (xn, yn)]`.
        overpass_pts: Optional iterable of crossing coordinates `(cx, cy)` or explicit
            segment pairs `((x1, y1), (x2, y2))` where a white halo bridge is drawn
            at `zorder - 0.5` so this wire cleanly crosses over background lines.
        overpass_bg: Halo background color (default `"#FFFFFF"`).
    """
    if len(pts) < 2:
        return

    if overpass_pts:
        _draw_overpass_halos(
            ax,
            pts,
            overpass_pts,
            overpass_bg=overpass_bg,
            halo_lw=lw * overpass_lw_scale,
            half_span=overpass_half_span,
            zorder=zorder - 0.5,
        )

    if len(pts) > 2:
        xs = [p[0] for p in pts[:-1]]
        ys = [p[1] for p in pts[:-1]]
        ax.plot(
            xs,
            ys,
            color=color,
            linewidth=lw,
            linestyle=ls,
            solid_capstyle="round",
            solid_joinstyle="round",
            zorder=zorder,
        )
        arrow(ax, pts[-2], pts[-1], color=color, lw=lw, ls=ls, ms=ms, zorder=zorder)
    else:
        arrow(ax, pts[0], pts[1], color=color, lw=lw, ls=ls, ms=ms, zorder=zorder)


def pill_label(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    *,
    color: str = "#1A202C",
    facecolor: str = "#FFFFFF",
    edgecolor: str = "#CBD5E1",
    fontsize: float = 12.5,
    bold: bool = True,
    pad: float = 0.22,
    lw: float = 1.0,
    zorder: float = 7,
):
    """Draw a rounded pill badge for tensor tags, state registers, or bus annotations."""
    return ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold" if bold else "normal",
        color=color,
        bbox=dict(
            boxstyle=f"round,pad={pad}",
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=lw,
        ),
        zorder=zorder,
    )


def panel_header(
    ax: plt.Axes,
    x: float,
    y: float,
    letter: str,
    title: str,
    *,
    letter_pt: float = 22.0,
    title_pt: float = 15.0,
    letter_dx: float = 0.30,
    letter_color: str = "#111111",
    title_color: str = PALETTE["text_dark"],
    zorder: float = 8,
) -> None:
    """Draw Nature/Science-style bold lowercase panel index (`a`, `b`) + bold title."""
    clean_letter = letter.strip().rstrip(".").rstrip(")").lower()
    ax.text(
        x,
        y,
        clean_letter,
        fontsize=letter_pt,
        fontweight="bold",
        color=letter_color,
        va="center",
        ha="left",
        zorder=zorder,
    )
    ax.text(
        x + letter_dx,
        y + 0.01,
        title,
        fontsize=title_pt,
        fontweight="bold",
        color=title_color,
        va="center",
        ha="left",
        zorder=zorder,
    )


def save_publication_figure(
    fig: plt.Figure,
    out_stem: str | Path,
    *,
    dpi: int = 320,
    formats: Sequence[str] = ("pdf", "svg", "png"),
    pad_inches: float = 0.04,
    close: bool = True,
) -> dict[str, Path]:
    """Save figure in `.pdf`, `.svg`, and `.png` formats with pure white background."""
    stem_path = Path(out_stem)
    stem_path.parent.mkdir(parents=True, exist_ok=True)

    saved: dict[str, Path] = {}
    for ext in formats:
        clean_ext = ext.lstrip(".").lower()
        target = stem_path.with_suffix(f".{clean_ext}")
        export_dpi = dpi if clean_ext in {"png", "jpg", "jpeg", "tif", "tiff"} else None
        fig.savefig(
            target,
            dpi=export_dpi,
            bbox_inches="tight",
            pad_inches=pad_inches,
            facecolor="white",
        )
        saved[clean_ext] = target.resolve()

    if close:
        plt.close(fig)
    return saved
