"""Fig. 1 (DGFed control loop) — professional redraw.
Every arrow is ONE FancyArrowPatch (straight, or a single Path for elbows),
so all routes are continuous by construction. Colorblind-safe palette
(Dark2 orange for the drift-signal family), grayscale-legible via line
weights. Labels match the paper's notation and equation numbers exactly:
PH (2)-(3), trigger (4), compression (5)-(7), clip (8), aggregation (9).
"""
import os

import matplotlib
matplotlib.use("Agg")

FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latex", "figures")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

# ---- palette ----
SLATE = "#33475B"; INK = "#1A1A1A"; GRAY = "#6B7A89"
ORANGE = "#D95F02"; TINT_O = "#FDEAD7"; TINT_B = "#DDE9F7"
CL_BG = "#F2F5F9"; SV_BG = "#EFECE6"; EDGE = "#8A97A5"

fig, ax = plt.subplots(figsize=(7.16, 2.45))
ax.set_xlim(0, 100); ax.set_ylim(0, 32.5); ax.axis("off")

def box(x, y, w, h, text, fc="#FFFFFF", fs=8.0, ec=SLATE, lw=1.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25",
                                fc=fc, ec=ec, lw=lw, zorder=3,
                                mutation_scale=1.0))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=fs, zorder=4, color="#111111")
    return (x, y, w, h)

def arrow(p, q, color=SLATE, lw=1.4, ls="-", ms=11, z=2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", color=color,
                                 lw=lw, linestyle=ls, mutation_scale=ms,
                                 shrinkA=0, shrinkB=0, zorder=z))

def elbow(pts, color=SLATE, lw=1.4, ls="-", ms=11, z=2):
    """One continuous multi-segment arrow (single patch, single head)."""
    ax.add_patch(FancyArrowPatch(path=Path(pts), arrowstyle="-|>",
                                 color=color, lw=lw, linestyle=ls,
                                 mutation_scale=ms, shrinkA=0, shrinkB=0,
                                 zorder=z))

def note(x, y, text, fs=7.2, color="#222222", frame=False, z=5):
    bbox = dict(fc="white", ec=SLATE if frame else "none",
                lw=0.7, pad=1.8) if frame else dict(fc="white", ec="none", pad=0.9)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            color=color, zorder=z, bbox=bbox)

# ---- containers ----
ax.add_patch(FancyBboxPatch((1, 1), 56, 29.5, boxstyle="round,pad=0.3",
                            fc=CL_BG, ec=EDGE, lw=1.3, zorder=0))
ax.add_patch(FancyBboxPatch((60.5, 1), 38.5, 29.5, boxstyle="round,pad=0.3",
                            fc=SV_BG, ec=EDGE, lw=1.3, zorder=0))
ax.text(3.0, 28.1, "Edge client $k$", fontsize=9, fontweight="bold",
        style="italic", color="#2B3A49", zorder=4)
ax.text(62.5, 28.1, "Server", fontsize=9, fontweight="bold",
        style="italic", color="#2B3A49", zorder=4)

# ---- client blocks ----
A = box(3.0, 19.5, 13.5, 6, "Sensor stream\n(non-stationary)")
B = box(19.5, 19.5, 16.5, 6, "Local training, $E$ epochs\n(full model federated)", fs=7.6)
C = box(40.0, 19.5, 14.5, 6, "Page\u2013Hinkley\ndetector  (2)\u2013(3)", fc=TINT_O)
D = box(39.5, 9.5, 15.5, 6.5,
        "Event trigger  (4)\nskip iff $d_k{=}0 \\wedge \\|\\Delta_k\\|{<}\\gamma H_k$",
        fc=TINT_O, fs=7.2)
E = box(39.5, 1.5, 15.5, 6, "EF top-$k$ + 8-bit\nquant.  (5)\u2013(7)")

# ---- server blocks ----
F = box(63.0, 1.5, 10.5, 6, "Decompress")
G = box(76.5, 1.5, 12.0, 6, "Adaptive clip  (8)\n$c\\cdot\\mathrm{med}\\,\\|\\Delta\\|$", fs=7.4)
H = box(74.0, 11.0, 16.5, 8.5,
        "Staleness/drift-aware\naggregation  (9)\n$w_k{=}\\,n_k\\,\\frac{\\tau_0}{\\tau_0+a_k}\\,\\rho^{\\,d_k}$",
        fc=TINT_O, fs=7.4)
I = box(76.5, 22.5, 12.0, 5.5, "Global model $\\theta$", fc=TINT_B)

# ---- client-side flow ----
arrow((16.5, 22.5), (19.5, 22.5))                              # A -> B
arrow((36.0, 22.5), (40.0, 22.5))                              # B -> C
note(38.0, 26.3, "residuals $r_i$")
arrow((47.2, 19.5), (47.2, 16.0), color=ORANGE, lw=2.4, ms=13) # C -> trigger (d_k)
note(45.4, 17.7, "$d_k$", fs=8, color=ORANGE)
elbow([(26.0, 19.5), (26.0, 13.5), (39.5, 13.5)])              # B -> trigger (Delta)
note(28.4, 15.1, "$\\Delta_k$", fs=8)
elbow([(39.5, 11.0), (22.0, 11.0), (22.0, 19.5)], ls=(0, (4, 3)),
      color=GRAY, lw=1.3)                                      # skip loop
note(30.5, 9.6, "skip (stay silent)", color=GRAY)
arrow((49.0, 9.5), (49.0, 7.5))                                # trigger -> compress
note(51.6, 8.5, "send")

# ---- uplink across the boundary ----
arrow((55.0, 4.5), (63.0, 4.5), color=INK, lw=2.0, ms=13)
note(59.0, 6.1, "$(\\tilde{\\Delta}_k, n_k, d_k, a_k)$", fs=6.6)
note(59.0, 3.0, "uplink, $b_k$ bytes", fs=7.0)

# ---- server-side flow ----
arrow((73.5, 4.5), (76.5, 4.5))                                # F -> G
arrow((82.5, 7.5), (82.5, 11.0))                               # G -> H
arrow((82.5, 19.5), (82.5, 22.5))                              # H -> I
note(85.6, 21.0, "update")

# ---- the loop-closing drift signal (one continuous path) ----
elbow([(54.5, 22.5), (66.0, 22.5), (66.0, 15.2), (74.0, 15.2)],
      color=ORANGE, lw=2.4, ms=13, z=2)
note(66.3, 25.4, "one flag $d_k$ governs\nupload and weight", fs=7.2,
     color=ORANGE, frame=True)

# ---- broadcast (one continuous path) ----
elbow([(82.5, 28.0), (82.5, 29.4), (27.0, 29.4), (27.0, 25.5)],
      color=GRAY, lw=1.5, ls=(0, (5, 3)))
note(52.0, 29.4, "broadcast $\\theta$", color=GRAY)

plt.tight_layout(pad=0.15)
for ext in ("pdf", "png"):
    plt.savefig(os.path.join(FIGDIR, f"fig1_loop.{ext}"), dpi=300, bbox_inches="tight")
print("written")
