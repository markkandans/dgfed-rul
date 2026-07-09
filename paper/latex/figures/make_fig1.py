"""Fig. 1 — DGFed system model / control loop. Grayscale-safe, IEEE double-column width."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(7.16, 3.1))
ax.set_xlim(0, 14.6); ax.set_ylim(0, 6.4); ax.axis("off")

def box(x, y, w, h, text, fc="#ffffff", lw=1.1, fs=8.3, style="round,pad=0.06"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style,
                                fc=fc, ec="black", lw=lw, zorder=2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, zorder=3)

def arrow(p, q, text="", style="-|>", ls="-", lw=1.2, cs="arc3,rad=0", fs=7.6,
          toff=(0, 0.16), color="black"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, ls=ls, lw=lw,
                                 connectionstyle=cs, mutation_scale=11,
                                 color=color, zorder=1))
    if text:
        mx, my = (p[0]+q[0])/2 + toff[0], (p[1]+q[1])/2 + toff[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=fs, zorder=3,
                bbox=dict(fc="white", ec="none", pad=0.5))

# ---- containers ----
ax.add_patch(FancyBboxPatch((0.25, 0.35), 7.0, 5.55, boxstyle="round,pad=0.08",
                            fc="#f4f4f4", ec="black", lw=1.4, zorder=0))
ax.text(0.55, 5.62, "Edge client $k$", fontsize=9.5, fontweight="bold", va="center")
ax.add_patch(FancyBboxPatch((7.95, 0.35), 6.35, 5.55, boxstyle="round,pad=0.08",
                            fc="#e7e7e7", ec="black", lw=1.4, zorder=0))
ax.text(8.25, 5.62, "Server", fontsize=9.5, fontweight="bold", va="center")

# ---- client internals ----
box(0.55, 4.35, 2.55, 0.95, "Non-stationary\nlocal stream")
box(0.55, 2.60, 2.55, 0.95, "Local training\n($E$ epochs)")
box(3.95, 4.35, 2.90, 0.95, "Page–Hinkley on\nresiduals $r_i$  (2)–(3)")
box(3.55, 2.45, 1.85, 1.15, "Upload\ngate  (4)", fc="#ffffff", style="round4,pad=0.06")
box(3.95, 0.70, 2.90, 0.95, "EF top-$k$ + 8-bit\nquantization  (5)--(7)")

arrow((1.82, 4.35), (1.82, 3.55))                                   # stream -> train
arrow((3.10, 3.30), (3.55, 3.10), text="$\\Delta_k$", toff=(-0.05, 0.28))
arrow((3.10, 4.82), (3.95, 4.82), text="residuals", toff=(0, 0.24))
arrow((4.45, 4.35), (4.45, 3.60), lw=2.2)                            # d_k -> gate
ax.text(4.18, 3.95, "$d_k$", fontsize=8.6, fontweight="bold")
arrow((4.45, 2.45), (5.10, 1.65), text="send", toff=(-0.42, 0.05))
arrow((3.55, 2.90), (1.82, 2.60), ls=":", cs="arc3,rad=0.35",
      text="skip (silent)", toff=(0.05, -0.32))

# ---- server internals ----
box(8.25, 3.95, 2.35, 0.95, "Decompress")
box(8.25, 2.30, 2.35, 0.95, "Adaptive clip  (8)")
box(11.15, 2.30, 2.85, 1.55, "Drift/staleness-aware\naggregation  (9)\n$w_k = n_k\\,\\frac{\\tau_0}{\\tau_0+a_k}\\,\\rho^{d_k}$")
box(11.15, 4.45, 2.85, 0.85, "Global model $\\theta$")

arrow((6.85, 1.17), (9.42, 1.17), text="uplink  $b_k$ bytes  (7)", lw=1.6, toff=(0, 0.24))
arrow((9.42, 1.17), (9.42, 2.30))
arrow((9.42, 3.25), (9.42, 3.95))
ax.add_patch(FancyArrowPatch((10.60, 4.42), (11.15, 3.60), arrowstyle="-|>",
                             mutation_scale=11, lw=1.2,
                             connectionstyle="arc3,rad=-0.3"))
arrow((10.60, 2.77), (11.15, 2.77))
arrow((12.57, 3.85), (12.57, 4.45), text="update")
arrow((12.57, 5.30), (1.82, 5.30), ls="--", cs="arc3,rad=0.12",
      text="broadcast $\\theta$ (downlink)", toff=(0, 0.30))

# ---- the loop-closing drift signal ----
ax.add_patch(FancyArrowPatch((6.85, 4.82), (12.57, 3.85), arrowstyle="-|>",
                             mutation_scale=12, lw=2.2,
                             connectionstyle="arc3,rad=-0.18", zorder=1))
ax.text(9.6, 4.85, "drift flag $d_k$ governs both\nupload and weight",
        fontsize=8.0, fontweight="bold", ha="center",
        bbox=dict(fc="white", ec="black", lw=0.6, pad=1.6))

plt.tight_layout(pad=0.2)
for ext in ("pdf", "png"):
    plt.savefig(f"/home/claude/paper/latex/figures/fig1_loop.{ext}",
                dpi=300, bbox_inches="tight")
print("fig1 written")
