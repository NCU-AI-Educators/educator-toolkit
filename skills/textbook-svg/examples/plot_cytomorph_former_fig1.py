#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["matplotlib>=3.7", "numpy>=1.24"]
# ///
"""Canonical Track C Reference Example: Dual-Panel Scientific Paper Figure 1.

Demonstrates Nature Machine Intelligence / arXiv double-column schematic design:
  - Panel a: Domain bottleneck contrast (stylized 14x14 ViT patch grid vs. 100x oil
    cell compartments drawn with pure `matplotlib.patches` vector geometry).
  - Panel b: Dual-track architecture (`CytoMorph-Former` & `MGA-DinoBloom`) with
    state registers, in-loop operator, orthogonal wire corridors, white overpass
    halo bridges, and `sg(·)` stop-gradient isolation.
  - Reverse-budgeted source fonts (>= 12.5 pt on a 13.90 in canvas -> >= 5.7 pt at
    6.37 in arXiv width and >= 6.4 pt at 7.20 in Nature double-column width).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
    Wedge,
)
import numpy as np


PALETTE = {
    "ours_primary": "#0F4D92",      # Yale Deep Blue: CytoMorph-Former
    "ours_secondary": "#3775BA",    # Medium Academic Blue: MGA-DinoBloom
    "positive_teal": "#2A8C82",     # Teal: Anatomical Registers / DML / Dual-Clock
    "positive_green": "#5AA469",    # Sage Green
    "sota_red_dark": "#B64342",     # Deep Crimson: Histopathology ViT / Contamination
    "sota_red_mid": "#D96B52",      # Terracotta
    "sota_coral": "#E5988B",        # Soft Coral
    "baseline_amber": "#D49A35",    # Muted Gold: Stop-Gradient / Halo Bridge
    "ablation_gray": "#A6AEB7",     # Cool Neutral Gray
    "dark_slate": "#4A5568",        # Slate: Frozen Foundation Layers
    "text_dark": "#1A202C",         # Ink Charcoal
    "text_muted": "#334155",        # Muted Slate Text
}


def setup_rcparams() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": 12.5,
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
    zorder: int = 2,
    alpha: float = 1.0,
) -> FancyBboxPatch:
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
    zorder: int = 5,
) -> None:
    patch = FancyArrowPatch(
        start,
        end,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle=style,
        mutation_scale=ms,
        linewidth=lw,
        linestyle=ls,
        color=color,
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(patch)


def ortho_arrow(
    ax: plt.Axes,
    pts: list[tuple[float, float]],
    *,
    color: str = "#334155",
    lw: float = 1.6,
    ls: str = "-",
    ms: float = 11.5,
    zorder: int = 5,
) -> None:
    if len(pts) >= 2:
        xs = [p[0] for p in pts[:-1]]
        ys = [p[1] for p in pts[:-1]]
        if len(pts) > 2:
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
    pad: float = 0.14,
    zorder: int = 7,
) -> None:
    ax.text(
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
            linewidth=1.0,
        ),
        zorder=zorder,
    )


def draw_panel_a(ax: plt.Axes) -> None:
    """Panel a: Nuclei-centric Histopathology ViT vs 100x Oil Cytopathology."""
    ax.text(0.10, 7.22, "a", fontsize=22.5, fontweight="bold", color="#111111", va="center", ha="left")
    ax.text(
        0.40,
        7.23,
        "Nuclei-Centric vs. 100× Cytopathology",
        fontsize=15.0,
        fontweight="bold",
        color=PALETTE["text_dark"],
        va="center",
        ha="left",
    )

    # ------------------------------------------------------------------
    # Top Card: Histopathology ViT
    # ------------------------------------------------------------------
    cx, cy, cw, ch = 0.12, 4.04, 4.34, 2.94
    rounded_box(ax, cx, cy, cw, ch, facecolor="#FFF9F8", edgecolor=PALETTE["sota_red_dark"], lw=1.6, radius=0.10, zorder=1)
    rounded_box(ax, cx + 0.06, cy + ch - 0.44, cw - 0.12, 0.38, facecolor="#FDE8E8", edgecolor="none", radius=0.07, zorder=2)
    ax.text(
        cx + cw / 2,
        cy + ch - 0.25,
        "Histopathology ViT (20×–40×, ≈0.25 μm/px)",
        fontsize=13.5,
        fontweight="bold",
        color="#8B1E1E",
        va="center",
        ha="center",
        zorder=3,
    )
    ax.text(
        cx + cw / 2,
        cy + ch - 0.60,
        "HoVer-Net · CellViT++ · UNI2-h",
        fontsize=12.5,
        fontweight="bold",
        color="#742A2A",
        va="center",
        ha="center",
        zorder=3,
    )

    # Left patch illustration (14x14 coarse stride-14 grid + [CLS] + unmasked attention)
    px, py, pw, ph = cx + 0.14, cy + 0.50, 1.82, 1.66
    ax.add_patch(Rectangle((px, py), pw, ph, facecolor="#F8FAFC", edgecolor="#64748B", lw=1.4, zorder=2))

    # Stylized target cell inside patch
    cell_c = (px + 0.80, py + 0.86)
    ax.add_patch(Ellipse(cell_c, 1.12, 0.94, angle=15, facecolor="#DCE6F5", edgecolor="#64748B", lw=1.2, zorder=3))
    ax.add_patch(Ellipse((cell_c[0] - 0.06, cell_c[1] + 0.04), 0.56, 0.46, angle=-10, facecolor="#6B46C1", edgecolor="#44337A", lw=1.2, zorder=4))
    # Adjacent RBCs crossing patch borders
    ax.add_patch(Circle((px + 1.44, py + 0.38), 0.26, facecolor="#F4A3A0", edgecolor="#B64342", lw=1.1, zorder=3))
    ax.add_patch(Circle((px + 1.44, py + 0.38), 0.11, facecolor="#FDECEC", edgecolor="none", zorder=3))
    ax.add_patch(Circle((px + 0.34, py + 0.34), 0.21, facecolor="#F4A3A0", edgecolor="#B64342", lw=1.1, zorder=3))
    ax.add_patch(Circle((px + 0.34, py + 0.34), 0.09, facecolor="#FDECEC", edgecolor="none", zorder=3))

    # Coarse 14x14 stride-14 grid lines
    n_grid = 4
    for g in range(1, n_grid):
        gx = px + g * (pw / n_grid)
        gy = py + g * (ph / n_grid)
        ax.plot([gx, gx], [py, py + ph], color="#475569", lw=0.95, ls="--", alpha=0.85, zorder=5)
        ax.plot([px, px + pw], [gy, gy], color="#475569", lw=0.95, ls="--", alpha=0.85, zorder=5)

    # Highlight a straddling 14x14 patch crossing boundary
    ax.add_patch(Rectangle((px + 2 * pw / 4, py + ph / 4), pw / 4, ph / 4, facecolor="none", edgecolor=PALETTE["sota_red_dark"], lw=1.8, zorder=6))

    # [CLS] token + unmasked global self-attention arcs mixing RBC -> Cyto/Nuc
    cls_x, cls_y = px + 0.38, py + ph - 0.22
    pill_label(ax, cls_x, cls_y, "[CLS]", color="#FFFFFF", facecolor=PALETTE["sota_red_dark"], edgecolor="#7F1D1D", fontsize=12.5, pad=0.12, zorder=8)
    arrow(ax, (px + 1.44, py + 0.38), (cell_c[0] + 0.15, cell_c[1] - 0.08), color=PALETTE["sota_red_dark"], lw=1.8, style="<->", rad=-0.28, ms=10.5, zorder=7)
    arrow(ax, (px + 1.44, py + 0.52), (cls_x + 0.18, cls_y - 0.06), color=PALETTE["sota_red_mid"], lw=1.5, ls="--", style="<->", rad=0.26, ms=9.5, zorder=7)
    arrow(ax, (px + 0.34, py + 0.44), (cls_x, cls_y - 0.14), color=PALETTE["sota_red_mid"], lw=1.5, ls="--", style="<->", rad=-0.22, ms=9.5, zorder=7)

    ax.text(px + pw / 2, cy + 0.32, "14×14 Stride-14", fontsize=12.5, fontweight="bold", color="#4A5568", ha="center", va="center")
    ax.text(px + pw / 2, cy + 0.12, "Unmasked Global Attn", fontsize=12.5, fontweight="bold", color="#742A2A", ha="center", va="center")

    # Right output schematic in Top Card
    rx, rw = cx + 2.08, 2.12
    rounded_box(ax, rx, cy + 1.28, rw, 0.88, facecolor="#FFFFFF", edgecolor="#CBD5E1", lw=1.2, radius=0.07, zorder=2)
    ax.text(rx + rw / 2, cy + 2.00, "Nuclei-Only Output", fontsize=12.8, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.add_patch(Ellipse((rx + 0.52, cy + 1.56), 0.62, 0.42, facecolor="none", edgecolor="#94A3B8", lw=1.1, ls=":", zorder=3))
    ax.add_patch(Ellipse((rx + 0.49, cy + 1.57), 0.30, 0.24, facecolor="#6B46C1", edgecolor="#44337A", lw=1.1, zorder=4))
    ax.text(rx + 1.44, cy + 1.68, "Cyto & RBC", fontsize=12.5, color="#64748B", ha="center", va="center", zorder=3)
    ax.text(rx + 1.44, cy + 1.44, "Omitted", fontsize=12.5, fontweight="bold", color="#64748B", ha="center", va="center", zorder=3)

    rounded_box(ax, rx, cy + 0.16, rw, 1.00, facecolor="#FEE2E2", edgecolor=PALETTE["sota_red_dark"], lw=1.4, radius=0.08, zorder=2)
    ax.text(rx + rw / 2, cy + 0.94, "Transmembrane", fontsize=12.5, fontweight="bold", color="#7F1D1D", ha="center", va="center", zorder=3)
    ax.text(rx + rw / 2, cy + 0.68, "Entanglement", fontsize=12.5, fontweight="bold", color="#7F1D1D", ha="center", va="center", zorder=3)
    ax.text(rx + rw / 2, cy + 0.37, "50.02% BG Drift", fontsize=13.2, fontweight="bold", color=PALETTE["sota_red_dark"], ha="center", va="center", zorder=3)

    # ------------------------------------------------------------------
    # Bottom Card: 100x Oil-Immersion Cytopathology
    # ------------------------------------------------------------------
    cx2, cy2, cw2, ch2 = 0.12, 0.74, 4.34, 3.16
    rounded_box(ax, cx2, cy2, cw2, ch2, facecolor="#F5FAFF", edgecolor=PALETTE["ours_primary"], lw=1.6, radius=0.10, zorder=1)
    rounded_box(ax, cx2 + 0.06, cy2 + ch2 - 0.44, cw2 - 0.12, 0.38, facecolor="#DBEAFE", edgecolor="none", radius=0.07, zorder=2)
    ax.text(
        cx2 + cw2 / 2,
        cy2 + ch2 - 0.25,
        "100× Oil Cytopathology (≈0.08 μm/px)",
        fontsize=13.5,
        fontweight="bold",
        color=PALETTE["ours_primary"],
        va="center",
        ha="center",
        zorder=3,
    )

    # Left: Detailed Romanowsky Cell Illustration (4 coupled compartments)
    mx, my, mw, mh = cx2 + 0.12, cy2 + 0.12, 1.94, 2.50
    rounded_box(ax, mx, my, mw, mh, facecolor="#FCFDFE", edgecolor="#94A3B8", lw=1.2, radius=0.08, zorder=2)

    # Cytoplasm (basophilic light slate-blue)
    cyto_c = (mx + 0.86, my + 1.54)
    ax.add_patch(Ellipse(cyto_c, 1.28, 1.08, angle=12, facecolor="#C7DDF2", edgecolor=PALETTE["ours_secondary"], lw=1.7, zorder=3))

    # Perinuclear Golgi Halo (pale crescent hugging nuclear indentation)
    ax.add_patch(Wedge((cyto_c[0] + 0.08, cyto_c[1] - 0.04), 0.38, -55, 115, width=0.17, facecolor="#F8FAFC", edgecolor="#93C5FD", lw=0.9, zorder=4))

    # Indented / bean-shaped Nucleus with chromatin clumps
    nuc_poly_pts = np.array([
        [cyto_c[0] - 0.38, cyto_c[1] + 0.15],
        [cyto_c[0] - 0.28, cyto_c[1] + 0.36],
        [cyto_c[0] - 0.04, cyto_c[1] + 0.39],
        [cyto_c[0] + 0.17, cyto_c[1] + 0.25],
        [cyto_c[0] + 0.04, cyto_c[1] + 0.06],
        [cyto_c[0] + 0.02, cyto_c[1] - 0.07],
        [cyto_c[0] + 0.14, cyto_c[1] - 0.25],
        [cyto_c[0] - 0.10, cyto_c[1] - 0.34],
        [cyto_c[0] - 0.32, cyto_c[1] - 0.23],
        [cyto_c[0] - 0.40, cyto_c[1] - 0.04],
    ])
    ax.add_patch(Polygon(nuc_poly_pts, closed=True, facecolor="#4C3B94", edgecolor="#2E1E6B", lw=1.5, zorder=5))
    for dx, dy, rx_c, ry_c in [
        (-0.20, 0.19, 0.085, 0.055),
        (-0.07, 0.25, 0.075, 0.048),
        (-0.22, -0.05, 0.075, 0.065),
        (-0.13, -0.20, 0.085, 0.048),
    ]:
        ax.add_patch(Ellipse((cyto_c[0] + dx, cyto_c[1] + dy), rx_c * 2, ry_c * 2, angle=25, facecolor="#312272", edgecolor="none", alpha=0.85, zorder=6))

    # Cytoplasmic azurophilic granules
    granule_offsets = [
        (0.36, 0.22), (0.44, 0.07), (0.40, -0.10), (0.28, -0.25),
        (0.17, 0.32), (0.33, 0.34), (0.47, -0.02), (0.26, -0.34),
    ]
    for gdx, gdy in granule_offsets:
        ax.add_patch(Circle((cyto_c[0] + gdx, cyto_c[1] + gdy), 0.027, facecolor="#9D174D", edgecolor="none", zorder=6))

    # Companion Mature RBC + 7.2-7.5 um caliper scale ruler
    rbc_c = (mx + 1.42, my + 0.68)
    ax.add_patch(Circle(rbc_c, 0.26, facecolor="#F39F9B", edgecolor="#B64342", lw=1.4, zorder=4))
    ax.add_patch(Circle(rbc_c, 0.11, facecolor="#FCE7E6", edgecolor="none", zorder=4))
    ry_bar = my + 0.34
    ax.plot([rbc_c[0] - 0.26, rbc_c[0] + 0.26], [ry_bar, ry_bar], color=PALETTE["ours_primary"], lw=1.7, zorder=7)
    ax.plot([rbc_c[0] - 0.26, rbc_c[0] - 0.26], [ry_bar - 0.045, ry_bar + 0.045], color=PALETTE["ours_primary"], lw=1.7, zorder=7)
    ax.plot([rbc_c[0] + 0.26, rbc_c[0] + 0.26], [ry_bar - 0.045, ry_bar + 0.045], color=PALETTE["ours_primary"], lw=1.7, zorder=7)

    # 4 clean compartment callout labels (>= 12.5 pt)
    ax.annotate(
        "Chromatin",
        xy=(cyto_c[0] - 0.16, cyto_c[1] + 0.30),
        xytext=(mx + 0.08, my + 2.33),
        fontsize=12.5,
        fontweight="bold",
        color="#2E1E6B",
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="-", lw=1.0, color="#2E1E6B"),
        zorder=8,
    )
    ax.annotate(
        "Golgi Halo",
        xy=(cyto_c[0] + 0.18, cyto_c[1] + 0.08),
        xytext=(mx + mw - 0.08, my + 2.33),
        fontsize=12.5,
        fontweight="bold",
        color=PALETTE["ours_primary"],
        ha="right",
        va="center",
        arrowprops=dict(arrowstyle="-", lw=1.0, color=PALETTE["ours_primary"]),
        zorder=8,
    )
    ax.annotate(
        "Granules",
        xy=(cyto_c[0] + 0.38, cyto_c[1] - 0.12),
        xytext=(mx + 0.50, my + 0.80),
        fontsize=12.5,
        fontweight="bold",
        color="#9D174D",
        ha="center",
        va="center",
        arrowprops=dict(arrowstyle="-", lw=1.0, color="#9D174D"),
        zorder=8,
    )
    ax.text(mx + 0.56, my + 0.52, "RBC Ruler", fontsize=12.5, fontweight="bold", color=PALETTE["sota_red_dark"], ha="center", va="center", zorder=8)
    ax.text(mx + 1.38, my + 0.14, "7.2–7.5 μm", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=8)

    # Right column of Bottom Card: Tri-state Phase Field + MGA + Result
    rx2, rw2 = cx2 + 2.12, 2.10
    rounded_box(ax, rx2, cy2 + 1.78, rw2, 0.84, facecolor="#FFFFFF", edgecolor=PALETTE["ours_secondary"], lw=1.3, radius=0.07, zorder=2)
    ax.text(rx2 + rw2 / 2, cy2 + 2.43, "Tri-State Phase Field", fontsize=12.6, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(
        rx2 + rw2 / 2,
        cy2 + 2.03,
        r"$\mathbf{P}^{(l)}=[P_{\mathrm{bg}}^{(l)},P_{\mathrm{cyto}}^{(l)},P_{\mathrm{nuc}}^{(l)}]$",
        fontsize=12.5,
        color=PALETTE["text_dark"],
        ha="center",
        va="center",
        zorder=3,
    )

    rounded_box(ax, rx2, cy2 + 0.88, rw2, 0.82, facecolor="#FFFFFF", edgecolor=PALETTE["positive_teal"], lw=1.3, radius=0.07, zorder=2)
    ax.text(rx2 + rw2 / 2, cy2 + 1.52, "MGA Boundary Gating", fontsize=12.6, fontweight="bold", color="#1D6F67", ha="center", va="center", zorder=3)
    ax.add_patch(Circle((rx2 + 0.38, cy2 + 1.14), 0.16, facecolor="#4C3B94", edgecolor="#2E1E6B", lw=1.0, zorder=3))
    ax.add_patch(Circle((rx2 + 1.04, cy2 + 1.14), 0.16, facecolor="#93C5FD", edgecolor=PALETTE["ours_primary"], lw=1.0, zorder=3))
    ax.add_patch(Circle((rx2 + 1.72, cy2 + 1.14), 0.16, facecolor="#F39F9B", edgecolor=PALETTE["sota_red_dark"], lw=1.0, zorder=3))
    arrow(ax, (rx2 + 0.56, cy2 + 1.14), (rx2 + 0.86, cy2 + 1.14), color=PALETTE["baseline_amber"], lw=2.0, style="<->", ms=9, zorder=4)
    ax.plot([rx2 + 1.22, rx2 + 1.54], [cy2 + 1.14, cy2 + 1.14], color=PALETTE["sota_red_dark"], lw=1.5, ls=":", zorder=4)
    ax.text(rx2 + 1.38, cy2 + 1.14, "×", fontsize=14.5, fontweight="bold", color=PALETTE["sota_red_dark"], ha="center", va="center", zorder=5)

    rounded_box(ax, rx2, cy2 + 0.12, rw2, 0.68, facecolor="#E6F6F4", edgecolor=PALETTE["positive_teal"], lw=1.5, radius=0.08, zorder=2)
    ax.text(rx2 + rw2 / 2, cy2 + 0.57, "13.18% Drift (−73.7%)", fontsize=12.8, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(rx2 + rw2 / 2, cy2 + 0.28, "[RBC_REF] μm Ruler", fontsize=12.5, fontweight="bold", color="#1D6F67", ha="center", va="center", zorder=3)


def draw_panel_b(ax: plt.Axes) -> None:
    """Panel b: Dual-track CytoMorph-Former (24.41M) & MGA-DinoBloom (37.48M) architecture."""
    ax.text(4.68, 7.22, "b", fontsize=22.5, fontweight="bold", color="#111111", va="center", ha="left")
    ax.text(
        4.98,
        7.23,
        "Dual-Track Domain-Native Architecture",
        fontsize=15.0,
        fontweight="bold",
        color=PALETTE["text_dark"],
        va="center",
        ha="left",
    )

    # ------------------------------------------------------------------
    # Shared 224x224 Input Column (x = 4.68..5.54)
    # ------------------------------------------------------------------
    ix, iy, iw, ih = 4.68, 3.28, 0.86, 2.52
    rounded_box(ax, ix, iy, iw, ih, facecolor="#F8FAFC", edgecolor=PALETTE["dark_slate"], lw=1.5, radius=0.08, zorder=2)
    tx, ty = ix + iw / 2, iy + ih - 0.58
    ax.add_patch(Rectangle((ix + 0.10, iy + ih - 0.98), iw - 0.20, 0.80, facecolor="#FCFDFE", edgecolor="#94A3B8", lw=1.0, zorder=3))
    ax.add_patch(Ellipse((tx - 0.04, ty), 0.40, 0.34, facecolor="#C7DDF2", edgecolor=PALETTE["ours_secondary"], lw=1.0, zorder=4))
    ax.add_patch(Ellipse((tx - 0.08, ty + 0.02), 0.18, 0.15, facecolor="#4C3B94", edgecolor="#2E1E6B", lw=0.8, zorder=5))
    ax.add_patch(Circle((tx + 0.18, ty - 0.16), 0.10, facecolor="#F39F9B", edgecolor="#B64342", lw=0.8, zorder=4))

    ax.text(ix + iw / 2, iy + 1.22, "224×224", fontsize=12.6, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(ix + iw / 2, iy + 0.96, "Input", fontsize=12.6, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(ix + iw / 2, iy + 0.66, "100× Oil", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)
    ax.text(ix + iw / 2, iy + 0.40, "≈0.08", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)
    ax.text(ix + iw / 2, iy + 0.17, "μm/px", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)

    # ------------------------------------------------------------------
    # Track 1 Container: CytoMorph-Former (24.41M, Zero Pretraining)
    # ------------------------------------------------------------------
    t1x, t1y, t1w, t1h = 5.72, 4.80, 3.58, 1.80
    rounded_box(ax, t1x, t1y, t1w, t1h, facecolor="#F2F7FD", edgecolor=PALETTE["ours_primary"], lw=1.6, radius=0.09, zorder=1)
    rounded_box(ax, t1x + 0.05, t1y + t1h - 0.52, t1w - 0.10, 0.46, facecolor=PALETTE["ours_primary"], edgecolor="none", radius=0.06, zorder=2)
    ax.text(t1x + t1w / 2, t1y + t1h - 0.19, "Track 1: CytoMorph-Former (24.41M)", fontsize=13.0, fontweight="bold", color="#FFFFFF", ha="center", va="center", zorder=3)
    ax.text(t1x + t1w / 2, t1y + t1h - 0.40, "Zero External Pretraining", fontsize=12.5, color="#DBEAFE", ha="center", va="center", zorder=3)

    # Track 1 Box A: Full-Res Stain-Wavelet & Polar Stem
    sx, sy, sw, sh = t1x + 0.08, t1y + 0.10, 2.24, 1.10
    rounded_box(ax, sx, sy, sw, sh, facecolor="#FFFFFF", edgecolor=PALETTE["ours_secondary"], lw=1.3, radius=0.07, zorder=2)
    ax.text(sx + sw / 2, sy + 0.92, "Stain-Wavelet & Polar Stem", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(sx + sw / 2, sy + 0.66, "4-Band Beer–Lambert OD", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(sx + sw / 2, sy + 0.41, "Mexican-Hat & Lifting", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(sx + sw / 2, sy + 0.16, r"Polar $(r,\cos\theta,\sin\theta)$", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)

    # Track 1 Box B: Pyramid Stages 1-2
    px2, py2, pw2, ph2 = sx + sw + 0.12, t1y + 0.10, 1.06, 1.10
    rounded_box(ax, px2, py2, pw2, ph2, facecolor="#FFFFFF", edgecolor=PALETTE["ours_secondary"], lw=1.3, radius=0.07, zorder=2)
    ax.text(px2 + pw2 / 2, py2 + 0.88, "Pyramid", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(px2 + pw2 / 2, py2 + 0.66, "Stages 1–2", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(px2 + pw2 / 2, py2 + 0.40, r"$56^2 \to 28^2$", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(px2 + pw2 / 2, py2 + 0.16, "64/128 ch", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    arrow(ax, (sx + sw, sy + sh / 2), (px2, py2 + ph2 / 2), color=PALETTE["ours_primary"], lw=1.5, ms=10, zorder=5)

    # ------------------------------------------------------------------
    # Track 2 Container: MGA-DinoBloom (37.48M total, 8.47M train, -56.7%)
    # ------------------------------------------------------------------
    t2x, t2y, t2w, t2h = 5.72, 2.70, 3.58, 1.94
    rounded_box(ax, t2x, t2y, t2w, t2h, facecolor="#F5FAFF", edgecolor=PALETTE["ours_secondary"], lw=1.6, radius=0.09, zorder=1)
    rounded_box(ax, t2x + 0.05, t2y + t2h - 0.52, t2w - 0.10, 0.46, facecolor=PALETTE["ours_secondary"], edgecolor="none", radius=0.06, zorder=2)
    ax.text(t2x + t2w / 2, t2y + t2h - 0.19, "Track 2: MGA-DinoBloom (37.48M)", fontsize=13.0, fontweight="bold", color="#FFFFFF", ha="center", va="center", zorder=3)
    ax.text(t2x + t2w / 2, t2y + t2h - 0.40, "8.47M Trainable · −56.7% vs. DinoBloom", fontsize=12.5, color="#E0F2FE", ha="center", va="center", zorder=3)

    # Parallel Branch 1: Frozen DinoBloom ViT-B/14 L1-4
    fx, fy, fw, fh = t2x + 0.08, t2y + 0.78, t2w - 0.16, 0.54
    rounded_box(ax, fx, fy, fw, fh, facecolor="#F1F5F9", edgecolor=PALETTE["dark_slate"], lw=1.4, linestyle="--", radius=0.07, zorder=2)
    ax.text(fx + fw / 2, fy + 0.38, "Frozen DinoBloom ViT-B/14", fontsize=12.5, fontweight="bold", color=PALETTE["dark_slate"], ha="center", va="center", zorder=3)
    ax.text(fx + fw / 2, fy + 0.15, "Layers 1–4 (28.5M Frozen)", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)

    ax.text(t2x + t2w / 2, t2y + 0.66, r"$\parallel$", fontsize=13.5, fontweight="bold", color=PALETTE["ours_secondary"], ha="center", va="center", zorder=3)

    # Parallel Branch 2: Compact Stain-Wavelet Stem
    cx_s, cy_s, cw_s, ch_s = t2x + 0.08, t2y + 0.08, t2w - 0.16, 0.52
    rounded_box(ax, cx_s, cy_s, cw_s, ch_s, facecolor="#EBF8FF", edgecolor=PALETTE["ours_secondary"], lw=1.3, radius=0.07, zorder=2)
    ax.text(cx_s + cw_s / 2, cy_s + 0.36, "Compact Stain-Wavelet Stem", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(cx_s + cw_s / 2, cy_s + 0.14, "48 / 96 ch Boundary Prior", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)

    # Fork arrows from Input to Track 1 & Track 2
    ortho_arrow(ax, [(ix + iw, iy + ih - 0.45), (5.62, iy + ih - 0.45), (5.62, sy + sh / 2), (t1x, sy + sh / 2)], color=PALETTE["ours_primary"], lw=1.7, ms=11)
    ortho_arrow(ax, [(ix + iw, iy + 0.65), (5.62, iy + 0.65), (5.62, t2y + 0.72), (t2x, t2y + 0.72)], color=PALETTE["ours_secondary"], lw=1.7, ms=11)

    # ------------------------------------------------------------------
    # Bottom Left of Panel b: 4 State Registers (left) & Zoom: Inside MGA Block (right)
    # ------------------------------------------------------------------
    rx, ry, rw, rh = 4.68, 0.74, 2.20, 1.72
    rounded_box(ax, rx, ry, rw, rh, facecolor="#F0FDFA", edgecolor=PALETTE["positive_teal"], lw=1.5, radius=0.08, zorder=2)
    ax.text(rx + rw / 2, ry + rh - 0.22, "4 State Registers", fontsize=13.0, fontweight="bold", color="#1D6F67", ha="center", va="center", zorder=3)
    reg_items = [
        (rx + 0.10, ry + 0.89, 0.95, 0.34, "[NUC]"),
        (rx + 1.15, ry + 0.89, 0.95, 0.34, "[CYTO]"),
        (rx + 0.10, ry + 0.48, 0.95, 0.34, "[MORPH]"),
        (rx + 1.15, ry + 0.48, 0.95, 0.34, "[RBC_REF]"),
    ]
    for rbx, rby, rbw, rbh, rlbl in reg_items:
        rounded_box(ax, rbx, rby, rbw, rbh, facecolor="#FFFFFF", edgecolor=PALETTE["positive_teal"], lw=1.1, radius=0.05, zorder=3)
        ax.text(rbx + rbw / 2, rby + rbh / 2, rlbl, fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=4)
    ax.text(rx + rw / 2, ry + 0.21, "+ 8D 3-Tier RBC Scale", fontsize=12.5, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)

    mx_b, my_b, mw_b, mh_b = 7.00, 0.74, 2.30, 1.72
    rounded_box(ax, mx_b, my_b, mw_b, mh_b, facecolor="#FFFDF5", edgecolor=PALETTE["baseline_amber"], lw=1.5, radius=0.08, zorder=2)
    ax.text(mx_b + mw_b / 2, my_b + mh_b - 0.22, "Zoom: Inside MGA Block", fontsize=12.6, fontweight="bold", color="#92400E", ha="center", va="center", zorder=3)
    ax.text(mx_b + mw_b / 2, my_b + 1.14, r"$\mathbf{P}^{(l)}$ Tri-State Update", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(mx_b + mw_b / 2, my_b + 0.84, r"$+\gamma_{\mathrm{coh}}\log C_{ij}^{(l)}$", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(mx_b + mw_b / 2, my_b + 0.53, r"$-\gamma_{\mathrm{ins}} M_{ij}^{(l)}$ (Insul.)", fontsize=12.5, fontweight="bold", color=PALETTE["sota_red_dark"], ha="center", va="center", zorder=3)
    ax.text(mx_b + mw_b / 2, my_b + 0.22, r"$+\gamma_{\mathrm{halo}}\mathcal{B}_{\mathrm{halo}}$ Bridge", fontsize=12.5, fontweight="bold", color="#92400E", ha="center", va="center", zorder=3)

    # ------------------------------------------------------------------
    # Column 2: MGA Stages & Mid-Network In-Loop DML (x = 9.78..11.82)
    # ------------------------------------------------------------------
    c2x, c2w = 9.78, 2.04

    # Pre-DML MGA (Track 1)
    b21_y, b21_h = 5.26, 1.18
    rounded_box(ax, c2x, b21_y, c2w, b21_h, facecolor="#EBF4FF", edgecolor=PALETTE["ours_primary"], lw=1.6, radius=0.08, zorder=2)
    ax.text(c2x + c2w / 2, b21_y + 0.94, "Pre-DML MGA", fontsize=13.2, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b21_y + 0.61, r"$L_{\mathrm{pre}}=4\ (16{\times}16\ \mathrm{Grid})$", fontsize=12.5, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b21_y + 0.29, r"$D=384$ (CytoMorph)", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)

    # Replaced L5-12 MGA (Track 2) -> feeds through In-Loop DML -> Post-DML MGA
    b22_y, b22_h = 3.84, 1.18
    rounded_box(ax, c2x, b22_y, c2w, b22_h, facecolor="#EFF6FF", edgecolor=PALETTE["ours_secondary"], lw=1.6, radius=0.08, zorder=2)
    ax.text(c2x + c2w / 2, b22_y + 0.94, "Replaced L5–12 MGA", fontsize=12.8, fontweight="bold", color=PALETTE["ours_secondary"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b22_y + 0.61, r"8 Layers $\cdot$ $D=256$", fontsize=12.5, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b22_y + 0.29, "Split by In-Loop DML", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)

    # Mid-Network In-Loop DML (0 Params)
    b23_y, b23_h = 2.30, 1.30
    rounded_box(ax, c2x, b23_y, c2w, b23_h, facecolor="#E6F6F4", edgecolor=PALETTE["positive_teal"], lw=1.7, radius=0.08, zorder=2)
    ax.text(c2x + c2w / 2, b23_y + 1.09, "In-Loop DML", fontsize=13.2, fontweight="bold", color="#1D6F67", ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b23_y + 0.81, r"0 Params · $|\rho|=0.9835$", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b23_y + 0.50, "Soft Hull · 42-Oct-EDT", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b23_y + 0.20, r"Euler $\chi_8$ · $r_{\mathrm{isthmus}}$", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)

    # Post-DML MGA Blocks (Both tracks steered by DML before Decoder)
    b24_y, b24_h = 0.74, 0.96
    rounded_box(ax, c2x, b24_y, c2w, b24_h, facecolor="#EBF4FF", edgecolor=PALETTE["ours_primary"], lw=1.6, radius=0.08, zorder=2)
    ax.text(c2x + c2w / 2, b24_y + 0.73, "Post-DML MGA", fontsize=13.2, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b24_y + 0.43, r"$L_{\mathrm{post}}=6$ / Late L5–12", fontsize=12.5, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(c2x + c2w / 2, b24_y + 0.16, "Isthmus-Steered Attn", fontsize=12.5, color=PALETTE["text_muted"], ha="center", va="center", zorder=3)

    # Subtle amber zoom flare connecting Post-DML MGA -> Zoom: Inside MGA Block
    zoom_poly = np.array([
        [c2x, b24_y + 0.10],
        [c2x, b24_y + b24_h - 0.10],
        [mx_b + mw_b, my_b + mh_b - 0.08],
        [mx_b + mw_b, my_b + 0.08],
    ])
    ax.add_patch(Polygon(zoom_poly, closed=True, facecolor="#FEF3C7", edgecolor="none", alpha=0.45, zorder=1))
    ax.plot([c2x, mx_b + mw_b], [b24_y + b24_h - 0.10, my_b + mh_b - 0.08], color=PALETTE["baseline_amber"], lw=1.3, ls="--", zorder=4)
    ax.plot([c2x, mx_b + mw_b], [b24_y + 0.10, my_b + 0.08], color=PALETTE["baseline_amber"], lw=1.3, ls="--", zorder=4)

    # Track 1 -> Pre-DML MGA & L5-12 -> In-Loop DML
    arrow(ax, (t1x + t1w, py2 + ph2 / 2), (c2x, b21_y + 0.29), color=PALETTE["ours_primary"], lw=1.7, ms=11)
    arrow(ax, (c2x + c2w / 2, b22_y), (c2x + c2w / 2, b23_y + b23_h), color=PALETTE["positive_teal"], lw=1.6, ms=11)

    # Cleanly separated left gutter wires (>= 0.22 in separation!):
    # Wire 1: 4 State Registers -> y=2.58 corridor -> x=9.64 bus -> In-Loop DML, L5-12 MGA & Pre-DML MGA
    ax.plot([rx + rw - 0.12, rx + rw - 0.12, 9.64], [ry + rh, 2.58, 2.58], color=PALETTE["positive_teal"], lw=1.5, ls="--", zorder=4)
    ax.plot([9.64, 9.64], [2.58, b21_y + 0.24], color=PALETTE["positive_teal"], lw=1.5, ls="--", zorder=4)
    arrow(ax, (9.64, 2.58), (c2x, 2.58), color=PALETTE["positive_teal"], lw=1.5, ls="--", ms=10, zorder=4)
    arrow(ax, (9.64, b22_y + 0.72), (c2x, b22_y + 0.72), color=PALETTE["positive_teal"], lw=1.5, ls="--", ms=10, zorder=4)
    arrow(ax, (9.64, b21_y + 0.24), (c2x, b21_y + 0.24), color=PALETTE["positive_teal"], lw=1.5, ls="--", ms=10, zorder=4)

    # Wire 2: Track 2 -> Replaced L5-12 MGA at x=9.42 (0.22 in clear of x=9.64!) with white overpass halo
    ax.plot([9.52, 9.74], [b22_y + 0.24, b22_y + 0.24], color="#FFFFFF", lw=5.5, zorder=4.5)
    ortho_arrow(ax, [(t2x + t2w, t2y + 0.72), (9.42, t2y + 0.72), (9.42, b22_y + 0.24), (c2x, b22_y + 0.24)], color=PALETTE["ours_secondary"], lw=1.7, ms=11, zorder=5)

    # Pre-DML MGA -> In-Loop DML routed cleanly along RIGHT side x=11.94 (zero crossings!)
    ortho_arrow(ax, [(c2x + c2w, b21_y + 0.42), (11.94, b21_y + 0.42), (11.94, b23_y + 0.72), (c2x + c2w, b23_y + 0.72)], color=PALETTE["positive_teal"], lw=1.6, ms=11, zorder=5)

    # In-Loop DML -> Post-DML MGA with pill cleanly centered at y=2.00 inside 0.60 in gap
    arrow(ax, (c2x + c2w / 2, b23_y), (c2x + c2w / 2, b24_y + b24_h), color=PALETTE["ours_primary"], lw=1.8, ms=12)
    pill_label(
        ax,
        c2x + c2w / 2,
        2.00,
        r"$B_{\mathrm{isthmus}}+\mathbf{s}_{\mathrm{morph}}$",
        color=PALETTE["ours_primary"],
        facecolor="#FFFFFF",
        edgecolor="#90CDF4",
        fontsize=12.5,
        pad=0.09,
        zorder=8,
    )

    # ------------------------------------------------------------------
    # Column 3: Trimap Decoder -> sg(·) -> Orthogonal -> Dual-Clock (x = 12.22..14.24)
    # ------------------------------------------------------------------
    c3x, c3w = 12.22, 2.02

    # 224x224 Tri-State Trimap Decoder
    b31_y, b31_h = 5.14, 1.32
    rounded_box(ax, c3x, b31_y, c3w, b31_h, facecolor="#EBF4FF", edgecolor=PALETTE["ours_primary"], lw=1.6, radius=0.08, zorder=2)
    ax.text(c3x + c3w / 2, b31_y + 1.04, "224×224 Tri-State", fontsize=13.0, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b31_y + 0.76, "Trimap Decoder", fontsize=13.0, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b31_y + 0.34, "Nuc / Cyto / BG+RBC", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)

    # Multi-scale wavelet skip connections across top ceiling corridor
    ortho_arrow(
        ax,
        [(sx + sw / 2, t1y + t1h), (sx + sw / 2, 6.86), (c3x + c3w / 2, 6.86), (c3x + c3w / 2, b31_y + b31_h)],
        color=PALETTE["positive_teal"],
        lw=1.7,
        ls="--",
        ms=11,
        zorder=6,
    )
    pill_label(
        ax,
        10.00,
        6.86,
        "Multi-Scale Wavelet Skips (112²/56²)",
        color="#1D6F67",
        facecolor="#FFFFFF",
        edgecolor=PALETTE["positive_teal"],
        fontsize=12.5,
        pad=0.14,
        zorder=8,
    )

    # Post-DML MGA -> Trimap Decoder via dedicated right riser x=12.09 (0.15 in right of x=11.94!)
    ortho_arrow(ax, [(c2x + c2w, b24_y + 0.48), (12.09, b24_y + 0.48), (12.09, b31_y + 0.54), (c3x, b31_y + 0.54)], color=PALETTE["ours_primary"], lw=1.8, ms=12)

    # sg(·) Stop-Gradient Isolation (Prop. 1)
    b32_y, b32_h = 3.88, 0.96
    rounded_box(ax, c3x, b32_y, c3w, b32_h, facecolor="#FEF3C7", edgecolor=PALETTE["baseline_amber"], lw=1.6, radius=0.08, zorder=2)
    ax.text(c3x + c3w / 2, b32_y + 0.67, r"$\mathrm{sg}(\cdot)$ Stop-Grad", fontsize=13.2, fontweight="bold", color="#92400E", ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b32_y + 0.28, r"Prop. 1: Blocks $\nabla\mathcal{L}_{\mathrm{aux}}$", fontsize=12.5, fontweight="bold", color="#78350F", ha="center", va="center", zorder=3)
    arrow(ax, (c3x + c3w / 2, b31_y), (c3x + c3w / 2, b32_y + b32_h), color=PALETTE["baseline_amber"], lw=1.8, ms=12)

    # Orthogonal Decoupling
    b33_y, b33_h = 2.34, 1.24
    rounded_box(ax, c3x, b33_y, c3w, b33_h, facecolor="#F0FDFA", edgecolor=PALETTE["positive_teal"], lw=1.6, radius=0.08, zorder=2)
    ax.text(c3x + c3w / 2, b33_y + 0.96, "Orthogonal Decoupling", fontsize=13.0, fontweight="bold", color="#1D6F67", ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b33_y + 0.60, r"$\mathbf{h}_{\mathrm{nuc}} \perp \mathbf{h}_{\mathrm{cyto}}$", fontsize=13.0, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b33_y + 0.25, "Cos Residual: 0.00136", fontsize=12.5, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    arrow(ax, (c3x + c3w / 2, b32_y), (c3x + c3w / 2, b33_y + b33_h), color=PALETTE["positive_teal"], lw=1.8, ms=12)

    # Dual-Clock Manifolds
    b34_y, b34_h = 0.74, 1.32
    rounded_box(ax, c3x, b34_y, c3w, b34_h, facecolor="#E6F6F4", edgecolor=PALETTE["ours_primary"], lw=1.7, radius=0.08, zorder=2)
    ax.text(c3x + c3w / 2, b34_y + 1.06, "Dual-Clock Manifolds", fontsize=13.2, fontweight="bold", color=PALETTE["ours_primary"], ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b34_y + 0.74, r"$\tau_{\mathrm{nuc}},\,\tau_{\mathrm{cyto}},\,\Delta\tau$", fontsize=13.0, fontweight="bold", color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b34_y + 0.44, "0.9229 MDS AUC", fontsize=12.6, fontweight="bold", color="#1D6F67", ha="center", va="center", zorder=3)
    ax.text(c3x + c3w / 2, b34_y + 0.17, "Rare-Phenotype Deploy", fontsize=12.5, color=PALETTE["text_dark"], ha="center", va="center", zorder=3)
    arrow(ax, (c3x + c3w / 2, b33_y), (c3x + c3w / 2, b34_y + b34_h), color=PALETTE["ours_primary"], lw=1.8, ms=12)


def draw_bottom_legend(ax: plt.Axes) -> None:
    """Clean semantic bottom legend containing ONLY architectural roles."""
    lx, ly, lw_b, lh_b = 0.12, 0.08, 14.12, 0.48
    rounded_box(ax, lx, ly, lw_b, lh_b, facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=1.2, radius=0.07, zorder=2)

    items = [
        ("#FDE8E8", PALETTE["sota_red_dark"], "-", "Histopathology ViT"),
        ("#EBF4FF", PALETTE["ours_primary"], "-", "CytoMorph-Former"),
        ("#EFF6FF", PALETTE["ours_secondary"], "-", "MGA-DinoBloom"),
        ("#F1F5F9", PALETTE["dark_slate"], "--", "Frozen ViT L1–4"),
        ("#E6F6F4", PALETTE["positive_teal"], "-", "Registers / DML / Clock"),
        ("#FEF3C7", PALETTE["baseline_amber"], "-", r"$\mathrm{sg}(\cdot)$ & Halo Bridge"),
    ]
    xs = [0.30, 2.48, 4.78, 6.84, 9.04, 11.88]
    cy = ly + lh_b / 2
    for x0, (fc, ec, ls, label) in zip(xs, items):
        rounded_box(ax, x0, cy - 0.10, 0.28, 0.20, facecolor=fc, edgecolor=ec, lw=1.4, linestyle=ls, radius=0.04, zorder=3)
        ax.text(x0 + 0.36, cy, label, fontsize=12.5, fontweight="bold", color=PALETTE["text_dark"], ha="left", va="center", zorder=3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render canonical Track C dual-panel Figure 1.")
    parser.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent / "output"),
        help="Directory to write fig1_cytomorph_architecture.{pdf,svg,png}.",
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir).resolve()

    setup_rcparams()
    fig = plt.figure(figsize=(13.90, 7.31), facecolor="white")
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], facecolor="white")
    ax.set_xlim(0.0, 14.30)
    ax.set_ylim(0.0, 7.52)
    ax.set_aspect("equal")
    ax.axis("off")

    draw_panel_a(ax)
    draw_panel_b(ax)
    draw_bottom_legend(ax)

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = "fig1_cytomorph_architecture"
    for ext in ("pdf", "svg", "png"):
        out_path = out_dir / f"{stem}.{ext}"
        dpi = 320 if ext == "png" else None
        fig.savefig(out_path, dpi=dpi, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    print(f"Success! Saved {out_dir / stem}.{{pdf,svg,png}}")


if __name__ == "__main__":
    main()
