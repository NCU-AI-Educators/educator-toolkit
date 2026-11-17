# Track C: Publication-Grade Scientific Paper Schematics & Model Architectures

Track C produces **infinite-resolution vector PDF/SVG schematics** (`Figure 1` conceptual bottleneck contrasts, `Figure 2` neural/physical model architectures, and multi-stage operator diagrams) for top-tier journals and conferences (*Nature Machine Intelligence*, *Nature Communications*, *Science Advances*, *IEEE TPAMI*, *CVPR/ICML/NeurIPS*, and *arXiv*) using pure `Python + Matplotlib` vector patches.

Unlike web/HTML diagrams (`Track B`) or lightweight textbook cards (`Track A`), academic manuscripts embed figures via LaTeX `\includegraphics[width=\textwidth]{fig1.pdf}` and demand:
1. **100% selectable TrueType/CID vector text (`Type 42`)** — zero `Type 3` bitmap fonts, zero unembedded fonts, and zero Ghostscript glyph-to-outline raster traps;
2. **Reverse print-scale typography budgeting** — source `fontsize` calculated backward from the physical journal column width (`3.50 in`–`7.20 in`) so no label shrinks below `5.5–6.0 pt` on paper;
3. **100% visual coherence with `figures4papers`** — identical semantic palette, sans-serif math, and lowercase bold panel letters (`a`, `b`) across qualitative schematics and quantitative data plots.

---

## 1. Reverse Print-Font Budgeting Formula

When a Matplotlib canvas of width $W_{\text{fig}}$ (inches) is scaled into a LaTeX column of width $W_{\text{target}}$ (inches), every font scales by $s = W_{\text{target}} / W_{\text{fig}}$. To guarantee a minimum printed legibility threshold $f_{\text{print,min}}$ (typically `6.0 pt` for Nature/IEEE, `5.5 pt` absolute floor for dense arXiv subscripts):

$$f_{\text{src}} \ge \frac{f_{\text{print,min}}}{W_{\text{target}} / W_{\text{fig}}}$$

| Venue Preset Key | Target Layout | $W_{\text{target}}$ (`in`) | Recommended $W_{\text{fig}}$ (`in`) | Scale $s$ | Safe Source Floor (`6.0 pt` print) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `nature_double` | Nature / NMI full width (`183 mm`) | `7.20` | `14.0` | `0.514` | **`12.1 pt`** |
| `ieee_double` | IEEE Trans. double column | `7.16` | `14.0` | `0.511` | **`12.1 pt`** |
| `cvpr_double` | CVPR / ICCV / ECCV `\textwidth` | `6.875` | `14.0` | `0.491` | **`12.6 pt`** |
| `arxiv_a4` | Standard LaTeX `article` / arXiv | `6.37` | `13.9` | `0.458` | **`13.5 pt`** (`12.5 pt` $\to$ `5.7 pt`) |
| `nature_single` | Nature single column (`89 mm`) | `3.50` | `7.0` | `0.500` | **`12.4 pt`** |

### Recommended 5-Tier Font Hierarchy (`compute_font_budget`)

Always run `paper_schematic_tool.py budget` (or call `paper_primitives.compute_font_budget`) before setting coordinates. It applies a `+3%` safety margin against `bbox_inches="tight"` padding expansion:

| Budget Key | Target Print Size (`pt`) | Role in Schematic |
| :--- | :---: | :--- |
| `min_fine_pt` | `min_print_pt` (`6.0 pt`) | Tensor shapes, parameter counts, pill tags, bottom legend items |
| `body_pt` | `~6.5 pt` | Module internal mechanism lines, equation terms |
| `card_title_pt` | `~7.2 pt` | Bold header inside each module / operator box |
| `panel_header_pt` | `~8.2 pt` | Panel title next to lowercase `a` / `b` (`Nuclei-Centric vs. ...`) |
| `panel_letter_pt` | `~10.5 pt` | Bold lowercase panel index (`a`, `b`, `c`) in `#111111` |

---

## 2. Visual Coherence with `figures4papers`

To make `Fig. 1` (Track C schematic) and `Fig. 3–6` (`figures4papers` quantitative charts) look authored by a single design studio, import `PALETTE` and `setup_publication_rcparams` from `scripts/paper_primitives.py`:

| `PALETTE` Key | Hex | Recommended Card Fill | Architectural / Semantic Role |
| :--- | :---: | :---: | :--- |
| `ours_primary` | `#0F4D92` | `#EBF4FF` / `#F2F7FD` | Primary proposed architecture, core backbone, main flow arrows |
| `ours_secondary` | `#3775BA` | `#EFF6FF` / `#F5FAFF` | Secondary proposed track, multi-scale stem, foundation adapter |
| `positive_teal` | `#2A8C82` | `#E6F6F4` / `#F0FDFA` | State registers, analytical/physical in-loop operators, decoupled manifolds |
| `positive_green` | `#5AA469` | `#ECFDF5` | Verified positive outcome, conservation check |
| `sota_red_dark` | `#B64342` | `#FFF9F8` / `#FEE2E2` | Baseline failure mode, boundary leakage, cross-compartment contamination |
| `sota_red_mid` | `#D96B52` | `#FEF2F2` | Secondary competing error path, spurious global attention arcs |
| `sota_coral` | `#E5988B` | `#FCE7E6` | Soft negative accent, distracting background objects |
| `baseline_amber` | `#D49A35` | `#FEF3C7` / `#FFFDF5` | `sg(·)` stop-gradient gate, halo bridge, zoom callout flare |
| `ablation_gray` | `#A6AEB7` | `#F8FAFC` | Omitted components, inactive cells |
| `dark_slate` | `#4A5568` | `#F1F5F9` (`ls="--"`) | Frozen pretrained ViT layers, shared input frame |
| `text_dark` | `#1A202C` | — | Primary labels and mathematical expressions |
| `text_muted` | `#334155` | — | Secondary annotations, spatial resolution notes |

### Mandatory Typography & Canvas Hygiene
- **Sans-Serif Math**: `setup_publication_rcparams()` sets `"font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]` and `"mathtext.fontset": "dejavusans"`. Never mix default Computer Modern serif math with Helvetica module boxes.
- **Vector Font Embedding**: `"pdf.fonttype": 42`, `"ps.fonttype": 42`, `"svg.fonttype": "none"` ensure selectable TrueType glyphs in PDF and editable `<text>` nodes in SVG.
- **Panel Index Convention**: Use **bold lowercase `a`, `b`, `c`** (`panel_header(ax, x, y, "a", "Title")`), never `(A)`, `A.`, or `[a]`.
- **Pure White Equal-Aspect Canvas**: Initialize `fig = plt.figure(figsize=(W, H), facecolor="white")`, `ax = fig.add_axes([0, 0, 1, 1])`, `ax.set_aspect("equal")`, `ax.axis("off")` — zero spines, zero ticks, zero background grids.

---

## 3. Cross-Disciplinary Geometric Vector Recipes (`matplotlib.patches`)

Prefer crisp `matplotlib.patches` vector geometry (`Circle`, `Ellipse`, `Polygon`, `Rectangle`, `Wedge`, `FancyBboxPatch`) over low-DPI raster screenshots so every zoom level in the published PDF stays razor-sharp.

### 3.1 Computational Pathology & Cell Biology
- **Indented Nucleus, Chromatin Clumps, Golgi Halo & Granules**: Layer an outer cytoplasm `Ellipse`, a pale crescent `Wedge` hugging the nuclear indentation, a closed concave `Polygon` nucleus with darker `Ellipse` heterochromatin clumps, and scattered `Circle` granules:
```python
# Cytoplasm + Golgi halo crescent + bean-shaped nucleus + granules + RBC ruler
ax.add_patch(Ellipse((cx, cy), 1.28, 1.08, angle=12, facecolor="#C7DDF2", edgecolor=PALETTE["ours_secondary"], lw=1.6, zorder=3))
ax.add_patch(Wedge((cx + 0.08, cy - 0.04), 0.38, -55, 115, width=0.17, facecolor="#F8FAFC", edgecolor="#93C5FD", lw=0.9, zorder=4))
ax.add_patch(Polygon(nuc_vertices, closed=True, facecolor="#4C3B94", edgecolor="#2E1E6B", lw=1.5, zorder=5))
for gx, gy in [(0.36, 0.20), (0.42, -0.08), (0.28, -0.24)]:
    ax.add_patch(Circle((cx + gx, cy + gy), 0.027, facecolor="#9D174D", edgecolor="none", zorder=6))

# Companion RBC + 7.2–7.5 μm physical caliper scale bar
ax.add_patch(Circle((rx, ry), 0.26, facecolor="#F39F9B", edgecolor=PALETTE["sota_red_dark"], lw=1.3, zorder=4))
ax.add_patch(Circle((rx, ry), 0.11, facecolor="#FCE7E6", edgecolor="none", zorder=4))
ax.plot([rx - 0.26, rx + 0.26], [ry - 0.34, ry - 0.34], color=PALETTE["ours_primary"], lw=1.7, zorder=7)
```
- **Patch Grid & Straddling Token Entanglement**: Contrast pixel-exact compartments against coarse stride-14 ViT grids by drawing dashed `ax.plot` gridlines over a `Rectangle` frame, highlighting a boundary-straddling patch in `#B64342`, and linking `[CLS]` (`pill_label`) with curved bidirectional `arrow(..., style="<->", rad=-0.26)`.

### 3.2 Hydro-Geomorphology & Physics PDEs
- **Multi-Scale AMR Grids, Terrain Cross-Sections, Flux Vectors & Conservation Walls**:
```python
# 1) Adaptive Mesh Refinement (AMR): coarse cell + 2x2 refined shock sub-cells
ax.add_patch(Rectangle((gx, gy), 1.2, 1.2, fill=False, edgecolor="#64748B", lw=1.2, zorder=3))
for i in range(2):
    for j in range(2):
        ax.add_patch(Rectangle((gx + 0.6 + 0.3 * i, gy + 0.3 * j), 0.3, 0.3, fill=False, edgecolor=PALETTE["ours_primary"], lw=1.3, zorder=4))

# 2) Terrain bedrock cross-section z_b(x) + translucent free-surface water column eta(x)
ax.add_patch(Polygon(bedrock_pts, closed=True, facecolor="#E2E8F0", edgecolor="#475569", lw=1.4, zorder=3))
ax.add_patch(Polygon(water_pts, closed=True, facecolor="#DBEAFE", edgecolor=PALETTE["ours_primary"], lw=1.5, alpha=0.85, zorder=2))

# 3) Conservative interface flux vector F_{i+1/2} & no-flux wall hatch boundary
arrow(ax, (x_face, y_mid), (x_face + 0.38, y_mid), color=PALETTE["positive_teal"], lw=1.8, zorder=6)
ax.plot([x_wall, x_wall], [y0, y1], color=PALETTE["dark_slate"], lw=2.2, zorder=5)
for hy in np.linspace(y0, y1 - 0.12, 6):
    ax.plot([x_wall - 0.10, x_wall], [hy, hy + 0.10], color=PALETTE["dark_slate"], lw=1.0, zorder=5)
```

### 3.3 Foundation Models & Transformers
- **Register Token Banks, Masked Attention Matrices, `sg(·)` Gates & Orthogonal Subspaces**:
```python
# 1) Register tokens ([CLS] / [NUC] / [MORPH]) inside a teal bank
rounded_box(ax, rx, ry, 2.20, 1.40, facecolor="#F0FDFA", edgecolor=PALETTE["positive_teal"], lw=1.5)
for bx, lbl in [(rx + 0.58, "[NUC]"), (rx + 1.62, "[CYTO]")]:
    pill_label(ax, bx, ry + 0.62, lbl, color=PALETTE["ours_primary"], edgecolor=PALETTE["positive_teal"], fontsize=FS_FINE)

# 2) 3x3 Block-Masked Attention Matrix (diagonal allowed, off-diagonal insulated with ×)
for r in range(3):
    for c in range(3):
        allowed = (r == c)
        fc = "#DBEAFE" if allowed else "#FEE2E2"
        ax.add_patch(Rectangle((mx + c * 0.28, my + (2 - r) * 0.28), 0.28, 0.28, facecolor=fc, edgecolor="#94A3B8", lw=0.9, zorder=3))
        if not allowed:
            ax.text(mx + (c + 0.5) * 0.28, my + (2.5 - r) * 0.28, "×", fontsize=FS_FINE, color=PALETTE["sota_red_dark"], ha="center", va="center", zorder=4)

# 3) sg(·) Stop-Gradient Gate + Orthogonal Subspace Manifold (h_1 ⊥ h_2)
rounded_box(ax, sx, sy, 1.90, 0.92, facecolor="#FEF3C7", edgecolor=PALETTE["baseline_amber"], lw=1.6)
ax.text(sx + 0.95, sy + 0.46, r"$\mathrm{sg}(\cdot)$ Blocks $\nabla\mathcal{L}_{\mathrm{aux}}$", fontsize=FS_FINE, fontweight="bold", color="#92400E", ha="center", va="center")
arrow(ax, (ox, oy), (ox + 0.62, oy), color=PALETTE["ours_primary"], lw=1.7)
arrow(ax, (ox, oy), (ox, oy + 0.62), color=PALETTE["positive_teal"], lw=1.7)
ax.add_patch(Rectangle((ox, oy), 0.12, 0.12, facecolor="none", edgecolor=PALETTE["dark_slate"], lw=1.0))
```

---

## 4. Orthogonal Routing, Overpass Bridges & Mandatory `pdftoppm` Loop

1. **Boundary Snapping (`shrinkA=0, shrinkB=0`)**: Always connect arrows to exact box edges `(x + w, y + h / 2)` with `shrinkA=0, shrinkB=0` (default in `paper_primitives.arrow`) so arrowheads touch borders crisply without floating gaps.
2. **Parallel Gutter Separation & Zoom Callout Flares**: Separate parallel vertical buses in the same gutter by `>= 0.18–0.22 in` so lines remain distinct at `0.45×` print scale. To show internal block equations without crowding the main column, place a dedicated zoom box in a quiet corner and link it with a translucent amber `Polygon(..., facecolor="#FEF3C7", alpha=0.45, zorder=1)` plus dashed `baseline_amber` boundary lines (see `examples/plot_cytomorph_former_fig1.py`).
3. **White Halo Overpass Bridges (`overpass_pts`)**: Eliminate crossings first by routing skip connections along outer ceiling/right corridors. Where an orthogonal wire must cross a background bus at `(cx, cy)`, call:
   ```python
   ortho_arrow(ax, pts, color=PALETTE["ours_secondary"], lw=1.7, zorder=6, overpass_pts=[(cx, cy)])
   ```
   `ortho_arrow` automatically draws a `lw * 3.4` `#FFFFFF` bridge along the active segment at `zorder - 0.5`, creating an unambiguous architectural overpass.
4. **Mandatory `preflight` + 200 DPI Visual-Collision Inspection**:
   Run `paper_schematic_tool.py preflight` on every exported PDF:
   ```bash
   uv run ~/.gemini/config/skills/textbook-svg/scripts/paper_schematic_tool.py preflight \
     --pdf path/to/fig1.pdf --script path/to/plot_fig1.py \
     --target-width-in 6.37 --min-print-pt 5.5 \
     --preview-dir /tmp/fig1_preview --output /tmp/fig1_preflight.json
   ```
   | Preflight Failure | Root Cause | Fix |
   | :--- | :--- | :--- |
   | `Type 3` font detected | Default Matplotlib Type 3 PDF output | Set `pdf.fonttype = 42`, `ps.fonttype = 42`, `mathtext.fontset = "dejavusans"` |
   | `0` fonts detected | Ghostscript `-dNoOutputFonts` outline conversion or raster save | Export directly from Matplotlib `.savefig("fig1.pdf")` |
   | `Undersized source fontsize` | `fontsize * (W_target / W_pdf) < min_print_pt` | Raise flagged `fontsize=` lines to `>= min_required_source_pt` |

   Finally, **always call `read_file` on every PNG listed in `preview_images`** (`200 DPI` `pdftoppm` render) to catch visual defects invisible to static AST checks (overlapping labels, arrows piercing text, or clipped subscripts) and iterate until 100% clean.

---

## 5. `paper_primitives.py` Quick API & Coordinate Grid Reference

When building custom multi-panel schematics from scratch rather than modifying `scaffold`, import `scripts/paper_primitives.py` directly:

```python
from paper_primitives import (
    PALETTE,
    VENUE_WIDTHS_IN,
    arrow,
    compute_font_budget,
    ortho_arrow,
    panel_header,
    pill_label,
    rounded_box,
    save_publication_figure,
    setup_publication_rcparams,
)

budget = compute_font_budget(VENUE_WIDTHS_IN["nature_double"], fig_width_in=14.0, min_print_pt=6.0)
setup_publication_rcparams(base_font_pt=budget["min_fine_pt"])
```

### Canonical `14.0 × 7.2 in` Double-Column Coordinate Partition

| Region | X-Span (`in`) | Y-Span (`in`) | Recommended Allocation |
| :--- | :---: | :---: | :--- |
| **Bottom Semantic Legend** | `0.15 .. 13.85` | `0.10 .. 0.58` | 5–6 architectural role swatches (`0.28×0.20` rounded boxes), zero benchmark numbers |
| **Panel `a` (Contrast)** | `0.15 .. 4.45` | `0.74 .. 6.65` | Top negative baseline card (`y = 3.82..6.54`) vs. bottom domain prior card (`y = 0.74..3.60`) |
| **Panel `b` Col 1 (Tracks)** | `4.70 .. 9.10` | `0.74 .. 6.65` | Shared input (`x = 4.70..5.75`), Track 1 (`y = 4.76..6.54`), Track 2 (`y = 2.66..4.44`), Registers (`y = 0.74..2.30`) |
| **Panel `b` Col 2 (Operator)** | `9.55 .. 11.60` | `0.74 .. 6.65` | Guided attention stages + zero-parameter differentiable physical/geometric operator |
| **Panel `b` Col 3 (Heads)** | `11.95 .. 13.85` | `0.74 .. 6.65` | `sg(·)` stop-gradient gate (`y = 4.60..6.50`) + orthogonal manifold / prediction head (`y = 0.74..4.00`) |
| **Panel Headers (`a`, `b`)** | `0.15`, `4.70` | `6.85 .. 7.10` | Bold lowercase letter (`panel_letter_pt`) + concise title (`panel_header_pt`) |
