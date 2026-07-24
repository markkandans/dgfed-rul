"""Python/NumPy mirror of matlab/demo3_ris_gain/run_demo.m.

RIS-aided SISO link, direct path blocked. For each N (16..1024):
  received amplitude = | sum_n |h_n||g_n| e^{j(arg h_n + arg g_n + theta_n)} |
  * optimized phases: theta_n cancels the cascade phase  -> amplitude ~ N,
    power ~ N^2 (each element also collects ~1/N... here normalized per-element
    channels CN(0,1), so absolute scaling is didactic, slope is the point).
  * random phases: 2-D random walk -> power ~ N.
Also shown: analytic mean-power laws
    optimized: E[P] = (N*pi/4)^2 * (1 + (16-pi^2)/(N*pi^2))  ~ (pi^2/16) N^2
    random   : E[P] = N
Expected: two straight lines on log-log with slopes 2 and 1.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "figures"))
import matplotlib.pyplot as plt
from talk_style import apply_style, save, C_BLUE, C_ORANGE, INK2

apply_style()
rng = np.random.default_rng(3)

Ns = 2 ** np.arange(4, 11)          # 16 .. 1024
TRIALS = 400
p_opt = np.zeros(len(Ns)); p_rnd = np.zeros(len(Ns))

for i, Nel in enumerate(Ns):
    h = (rng.standard_normal((TRIALS, Nel)) + 1j * rng.standard_normal((TRIALS, Nel))) / np.sqrt(2)
    g = (rng.standard_normal((TRIALS, Nel)) + 1j * rng.standard_normal((TRIALS, Nel))) / np.sqrt(2)
    casc = h * g                                    # element-wise cascade
    # optimized: co-phase all terms
    p_opt[i] = np.mean(np.abs(np.sum(np.abs(casc), axis=1)) ** 2)
    # random phases
    theta = rng.uniform(0, 2 * np.pi, (TRIALS, Nel))
    p_rnd[i] = np.mean(np.abs(np.sum(casc * np.exp(1j * theta), axis=1)) ** 2)

# analytic references: E|h||g| = pi/4 -> coherent mean amplitude N*pi/4
ana_opt = (Ns * np.pi / 4) ** 2 * (1 + (16 - np.pi ** 2) / (Ns * np.pi ** 2))
ana_rnd = Ns.astype(float)

print(" N    P_opt(sim)  P_opt(ana)   P_rnd(sim)  P_rnd(ana)")
for i, Nel in enumerate(Ns):
    print(f"{Nel:5d}  {p_opt[i]:10.1f}  {ana_opt[i]:10.1f}  "
          f"{p_rnd[i]:10.2f}  {ana_rnd[i]:10.2f}")

slope_opt = np.polyfit(np.log10(Ns), np.log10(p_opt), 1)[0]
slope_rnd = np.polyfit(np.log10(Ns), np.log10(p_rnd), 1)[0]
print(f"fitted log-log slopes: optimized {slope_opt:.3f} (expect ~2), "
      f"random {slope_rnd:.3f} (expect ~1)")

fig, ax = plt.subplots(figsize=(9.5, 6.0))
ax.loglog(Ns, p_opt, "-o", color=C_ORANGE, label="optimized phases (sim)")
ax.loglog(Ns, ana_opt, "--", color=C_ORANGE, lw=2, alpha=0.7,
          label="analytic $\\approx (\\pi^2/16)N^2$")
ax.loglog(Ns, p_rnd, "-s", color=C_BLUE, label="random phases (sim)")
ax.loglog(Ns, ana_rnd, "--", color=C_BLUE, lw=2, alpha=0.7, label="analytic $N$")
ax.set_xlabel("Number of RIS elements  $N$")
ax.set_ylabel("Mean received power (linear, norm.)")
ax.legend(fontsize=13)
ax.set_title("The RIS $N^2$ law: co-phasing turns a random walk\n"
             "into coherent combining (+6 dB per doubling)")
save(fig, "fig_demo3_ris_scaling.png")

# backup copy for slide A3
import shutil
figdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures")
shutil.copy(os.path.join(figdir, "fig_demo3_ris_scaling.png"),
            os.path.join(figdir, "demo_backups", "backup_demo3.png"))
print("verify_demo3: done")
