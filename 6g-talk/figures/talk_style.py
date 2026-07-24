"""Shared matplotlib style for all talk figures.

Palette: validated categorical set (dataviz reference palette, fixed order).
Slides are projected, so fonts and line widths run heavier than web defaults.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Fixed categorical order — never cycle or reorder per-figure.
C_BLUE   = "#2a78d6"   # slot 1
C_ORANGE = "#eb6834"   # slot 2
C_AQUA   = "#1baf7a"   # slot 3
C_YELLOW = "#eda100"   # slot 4
C_MAGENTA= "#e87ba4"   # slot 5
PALETTE  = [C_BLUE, C_ORANGE, C_AQUA, C_YELLOW, C_MAGENTA]

ACCENT   = "#0F7173"   # deck accent (petrol) — decorative use only, not a series color
INK      = "#0b0b0b"
INK2     = "#52514e"
GRID     = "#d8d7d2"

FIGDIR = os.path.dirname(os.path.abspath(__file__))

def apply_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 15,
        "axes.titlesize": 17,
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 14,
        "axes.linewidth": 1.2,
        "lines.linewidth": 2.8,
        "lines.markersize": 9,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "legend.framealpha": 0.95,
        "legend.edgecolor": GRID,
    })

def save(fig, name, subdir=None):
    """Save into figures/ (or figures/<subdir>/) at 300 dpi, tight bbox."""
    out = FIGDIR if subdir is None else os.path.join(FIGDIR, subdir)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("saved:", os.path.relpath(path, os.path.dirname(FIGDIR)))
    return path
