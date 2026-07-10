"""Generate the paper's five figures from the pinned results JSONs.

Outputs paper/latex/figures/fig{1..5}_*.pdf plus 300-DPI PNG twins.
Grayscale-safe: gray levels + distinct markers/line styles only.
IEEE geometry: 3.5 in single column, 7.16 in double column.
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "paper", "latex", "figures")
os.makedirs(FIGDIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "legend.fontsize": 6.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.0,
    "pdf.fonttype": 42,
})

GRAYS = ["0.0", "0.35", "0.55", "0.7"]


def J(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def save(fig, name):
    for ext, kw in (("pdf", {}), ("png", {"dpi": 300})):
        fig.savefig(os.path.join(FIGDIR, f"{name}.{ext}"), bbox_inches="tight", **kw)
    plt.close(fig)
    print(f"[saved] {name}.pdf/.png")


# ---------------------------------------------------------------- fig 1: loop
def fig1():
    fig, ax = plt.subplots(figsize=(7.16, 2.7))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")

    def box(x, y, w, h, text, fc="1.0", lw=0.8, fs=7, style="round,pad=0.35"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style,
                                    fc=fc, ec="0.0", lw=lw))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    def arrow(x0, y0, x1, y1, dashed=False, lw=0.9, color="0.0"):
        ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(
            arrowstyle="-|>", lw=lw, color=color,
            linestyle="--" if dashed else "-", shrinkA=1, shrinkB=1))

    # client panel
    ax.add_patch(FancyBboxPatch((1, 2), 55, 36, boxstyle="round,pad=0.4",
                                fc="0.97", ec="0.4", lw=0.7, linestyle=":"))
    ax.text(3, 36.2, "Edge client $k$", fontsize=8, style="italic", va="center")
    box(3, 24, 13, 8, "Sensor\nstream")
    box(18, 24, 20, 8, "Local training\n(full model federated)", fc="0.92", fs=6.5)
    box(40, 24, 14, 8, "Prediction\nresiduals")
    box(40, 10, 14, 8, "Page–Hinkley\ndrift detector", fc="0.85")
    box(20, 10, 16, 8, "Event trigger\n$\\|\\Delta_k\\|<\\gamma H_k$ ?", fc="0.92")
    box(3, 10, 13, 8, "EF top-$k$\n+ 8-bit quant")
    arrow(16, 28, 18, 28)
    arrow(38, 28, 40, 28)
    arrow(47, 24, 47, 18)                       # residuals -> PH
    arrow(40, 14, 36, 14, dashed=True)          # drift flag -> trigger
    ax.text(38, 15.6, "$d_k$", fontsize=7, ha="center")
    arrow(28, 24, 28, 18)                       # delta -> trigger
    ax.text(29.5, 20.5, "$\\Delta_k$", fontsize=7)
    arrow(20, 14, 16, 14)                       # trigger -> compress
    ax.text(18, 19.3, "send", fontsize=6, ha="center")

    # server panel
    ax.add_patch(FancyBboxPatch((63, 2), 36, 36, boxstyle="round,pad=0.4",
                                fc="0.97", ec="0.4", lw=0.7, linestyle=":"))
    ax.text(65, 36.2, "Server", fontsize=8, style="italic", va="center")
    box(66, 22, 30, 9, "Decompress; staleness- &\ndrift-aware weights + adaptive\nclip $c\\cdot\\mathrm{med}\\,\\|\\Delta\\|$", fc="0.85", fs=6.5)
    box(66, 8, 30, 8, "Aggregate $\\rightarrow$ new\nglobal model $\\theta$", fc="0.92")
    arrow(81, 22, 81, 16)

    # cross arrows
    arrow(9.5, 10, 9.5, 5); arrow(9.5, 5, 81, 5); arrow(81, 5, 81, 8)
    ax.text(37, 6.5, "upload $(\\Delta_k, n_k, d_k, a_k)$", fontsize=6.5, ha="center")
    arrow(96, 12, 98.5, 12); arrow(98.5, 12, 98.5, 33); arrow(98.5, 33, 36, 33)
    ax.text(50, 34.8, "broadcast global model $\\theta$", fontsize=6.5, ha="center")
    arrow(54, 14, 66, 26.5, dashed=True)        # drift flag -> aggregation
    ax.text(60, 22, "$d_k$", fontsize=7)

    save(fig, "fig1_loop")


# --------------------------------------------- fig 2: communication–accuracy
def fig2():
    fig, axes = plt.subplots(2, 1, figsize=(3.5, 4.15), sharex=True)
    for ax, part in zip(axes, ["unit", "regime"]):
        cal = J(f"results/merged5/FD004_calibrated/ablation_{part}.json")
        reb = J(f"results/merged5/FD004_rebased/ablation_{part}.json")
        pts = []
        for label, src, marker, gray in [
            ("Proposed", cal["no_personal_head"], "o", "0.0"),
            ("DGFed-P (pers. head)", cal["full"], "s", "0.35"),
            ("Proposed, no compr.", reb["proposed_no_compression"], "D", "0.55"),
        ]:
            pts.append((label, src["total_MB_uploaded_mean"],
                        src["rmse_mean"], src["rmse_std"], marker, gray))
        for label, m, marker, gray in [("FedAvg", "fedavg", "^", "0.0"),
                                       ("FedProx", "fedprox", "v", "0.45")]:
            runs = J(f"results/merged5/FD004_{part}/{m}_FD004.json")["runs"]
            r = [x["rmse"] for x in runs]
            pts.append((label, np.mean([x["total_MB_uploaded"] for x in runs]),
                        np.mean(r), np.std(r), marker, gray))
        for label, mb, rm, sd, marker, gray in pts:
            ax.errorbar(mb, rm, yerr=sd, marker=marker, ms=5, color=gray,
                        capsize=2, lw=0.8, ls="none", label=label)
        cen = [x["rmse"] for x in J(f"results/merged5/FD004_{part}/central_FD004.json")["runs"]]
        ax.axhline(np.mean(cen), color="0.0", lw=0.8, ls=":")
        loc = np.mean([x["rmse"] for x in J(f"results/merged5/FD004_{part}/local_FD004.json")["runs"]])
        ax.axhline(loc, color="0.6", lw=0.8, ls="--")
        tx = 0.03 if part == "unit" else 0.45
        ax.text(tx, np.mean(cen), "centralized", fontsize=6, va="bottom",
                ha="left", transform=ax.get_yaxis_transform(), color="0.0")
        ax.text(tx, loc, "local-only", fontsize=6, va="bottom",
                ha="left", transform=ax.get_yaxis_transform(), color="0.45")
        ax.set_xscale("log")
        ax.set_ylabel("RMSE (cycles)")
        ax.set_title(f"FD004, {part} partition "
                     f"({cal['full']['n_clients']} clients)", fontsize=7.5)
        ax.grid(True, which="both", lw=0.3, color="0.9")
    axes[0].legend(loc="center left", frameon=False, handletextpad=0.3)
    axes[1].set_xlabel("Total upload (MB, log scale)")
    fig.tight_layout(h_pad=1.0)
    save(fig, "fig2_comm_accuracy")


# ------------------------------------------------- fig 3: paired seed deltas
def fig3():
    an = J("results/merged5/analysis_paired_seed_FD004.json")["partitions"]
    arms = ["+personal_head", "proposed_no_drift_signal", "proposed_no_event_trigger",
            "proposed_plain_aggregation", "proposed_no_compression"]
    labels = ["+ personal head", "– drift signal", "– event trigger",
              "– drift/stale agg.", "– compression"]
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.6), sharey=True)
    for ax, part in zip(axes, ["unit", "regime"]):
        for i, arm in enumerate(arms):
            d = an[part][arm]["per_seed_delta"]
            y = len(arms) - 1 - i
            ax.plot(d, [y] * len(d), "o", ms=3, mfc="none", mec="0.45", mew=0.8)
            ax.plot(np.mean(d), y, "D", ms=4.5, color="0.0")
        ax.axvline(0, color="0.0", lw=0.7)
        ax.set_yticks(range(len(arms)))
        ax.set_yticklabels(labels[::-1])
        ax.set_title(part, fontsize=7.5)
        ax.grid(True, axis="x", lw=0.3, color="0.9")
        ax.set_xlabel(r"$\Delta$RMSE vs. proposed")
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig3_paired_deltas")


# ---------------------------------------------------------- fig 4: retention
def fig4():
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.9), sharey=True)
    for ax, part in zip(axes, ["unit", "regime"]):
        cal = J(f"results/FD004_calibrated/ablation_{part}.json")
        for src, label, ls, marker, gray in [
            (cal["no_personal_head"], "Proposed", "-", "o", "0.0"),
            (cal["full"], "DGFed-P", "--", "s", "0.5"),
        ]:
            bins = np.array(src["retention_rmse_bins"], dtype=float)
            m, s = bins.mean(axis=0), bins.std(axis=0)
            x = np.arange(1, bins.shape[1] + 1)
            ax.plot(x, m, ls=ls, marker=marker, ms=3, color=gray, label=label)
            ax.fill_between(x, m - s, m + s, color=gray, alpha=0.15, lw=0)
        ax.set_xticks(x)
        ax.set_xlabel("ordered test-tail bin")
        ax.set_title(part, fontsize=7.5)
        ax.grid(True, lw=0.3, color="0.9")
    axes[0].set_ylabel("RMSE (cycles)")
    axes[0].legend(frameon=False, loc="lower left", handlelength=1.6)
    fig.tight_layout(w_pad=0.6)
    save(fig, "fig4_retention")


# ------------------------------------------------------- fig 5: lambda sweep
def fig5():
    sw = J("results/ph_sweep_FD004_unit.json")
    lams = sorted(float(k) for k in sw)
    fire = [sw[f"{l:g}"]["drift_fire_rate"] * 100 for l in lams]
    rmse = [sw[f"{l:g}"]["rmse"] for l in lams]
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    ax.axhspan(3, 8, color="0.9", lw=0)
    ax.text(260, 5.4, "target band", fontsize=6.5, color="0.35", va="center")
    ax.plot(lams, fire, "-o", ms=4, color="0.0", label="drift fire rate")
    ax.axvline(5000, color="0.0", lw=0.7, ls=":")
    # observed transfer points at the chosen lambda (portability limitation)
    for y, lbl, dy in [(19.0, "FD004-regime", 0.6), (14.3, "FD002-regime", 0.6),
                       (6.7, "FD002-unit", -1.9)]:
        ax.plot(5000, y, "o", ms=4, mfc="1.0", mec="0.0", mew=0.9)
        ax.annotate(lbl, (5000, y), xytext=(3550, y + dy), fontsize=5.5,
                    ha="right", color="0.25",
                    arrowprops=dict(arrowstyle="-", lw=0.5, color="0.55"))
    ax.text(4500, 13.5, "chosen $\\lambda$", fontsize=6.5, ha="right",
            rotation=90, va="bottom", color="0.25")
    ax.set_xscale("log")
    ax.set_xticks(lams)
    ax.set_xticklabels([f"{int(l)}" for l in lams])
    ax.minorticks_off()
    ax.set_xlabel(r"Page–Hinkley threshold $\lambda$")
    ax.set_ylabel("drift fire rate (%)")
    ax2 = ax.twinx()
    ax2.plot(lams, rmse, "--s", ms=3.5, color="0.5", label="RMSE (50 rounds)")
    ax2.set_ylabel("RMSE (cycles)", color="0.35")
    ax2.tick_params(axis="y", labelcolor="0.35")
    ax2.minorticks_off()
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, ncols=2,
              loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.grid(True, which="major", lw=0.3, color="0.9")
    fig.tight_layout()
    save(fig, "fig5_lambda_sweep")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
