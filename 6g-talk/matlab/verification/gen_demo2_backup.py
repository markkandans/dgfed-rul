"""Backup-figure generator for Demo 2 (hybrid beamforming).

Not a full verification (only demos 1/3/4 are mirrored per plan) — this
reproduces the two static panels the MATLAB demo shows, using the same math:
  (a) 64-element ULA array factor for three steering angles;
  (b) spectral efficiency: fully digital vs OMP hybrid vs analog-only
      (identical model to figures/make_figures.py::fig_hybrid_se).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "figures"))
import matplotlib.pyplot as plt
from talk_style import apply_style, save, PALETTE, C_BLUE, C_ORANGE, C_AQUA
from make_figures import _sv_channel, _omp_hybrid

apply_style()
rng = np.random.default_rng(2)

Nel = 64
theta = np.linspace(-90, 90, 2001)

fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))

# (a) array factor, three steering angles
for th0, col in zip([-40, 0, 25], [C_AQUA, C_BLUE, C_ORANGE]):
    w = np.exp(1j * np.pi * np.arange(Nel) * np.sin(np.deg2rad(th0))) / Nel
    a = np.exp(1j * np.pi * np.outer(np.arange(Nel), np.sin(np.deg2rad(theta))))
    AF = 20 * np.log10(np.abs(w.conj() @ a) + 1e-9) + 20 * np.log10(Nel)
    axes[0].plot(theta, AF, color=col, label=f"steer {th0}$^\\circ$", lw=2.2)
axes[0].set_ylim(-30, 40); axes[0].set_xlim(-90, 90)
axes[0].set_xlabel("Angle (deg)"); axes[0].set_ylabel("Array gain (dB)")
axes[0].legend(fontsize=12, loc="lower left")
axes[0].set_title(f"{Nel}-element ULA: pencil beams, "
                  f"{20*np.log10(Nel):.0f} dB peak gain")

# (b) SE comparison (same model as fig_hybrid_se, fewer trials for speed)
Nt, Nr, L, Ns, Nrf, trials = 64, 16, 6, 4, 4, 40
snr_db = np.arange(-10, 21, 5)
se = {k: np.zeros(len(snr_db)) for k in ("dig", "hyb", "ana")}
for _ in range(trials):
    H, aod = _sv_channel(Nt, Nr, L, rng)
    U, s, Vh = np.linalg.svd(H)
    Fopt = Vh.conj().T[:, :Ns]
    Frf, Fbb = _omp_hybrid(Fopt, Nrf, Nt)
    Fhyb = Frf @ Fbb
    fana = np.exp(1j * np.pi * np.arange(Nt) * np.sin(aod[0])) / np.sqrt(Nt)
    for i, sdb in enumerate(snr_db):
        rho = 10 ** (sdb / 10)
        for key, F, ns in (("dig", Fopt, Ns), ("hyb", Fhyb, Ns),
                           ("ana", fana[:, None], 1)):
            M = np.eye(Nr) + (rho / ns) * H @ F @ F.conj().T @ H.conj().T
            se[key][i] += np.real(np.log2(np.linalg.det(M))) / trials
axes[1].plot(snr_db, se["dig"], "-o", color=C_BLUE, label="fully digital")
axes[1].plot(snr_db, se["hyb"], "-s", color=C_ORANGE, label="hybrid OMP (4 RF)")
axes[1].plot(snr_db, se["ana"], "-^", color=C_AQUA, label="analog only")
axes[1].set_xlabel("SNR (dB)"); axes[1].set_ylabel("SE (bit/s/Hz)")
axes[1].legend(fontsize=12)
axes[1].set_title("4 RF chains $\\approx$ 64 (in sparse channels)")

save(fig, "backup_demo2.png", subdir="demo_backups")
print("gen_demo2_backup: done")
