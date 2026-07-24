"""Backup-figure generator for Demo 5 (learned channel estimation).

The MATLAB demo trains a small feed-forward NN (Deep Learning Toolbox).
This Python stand-in uses a *learned linear* estimator (ridge regression on
training data) — the estimator a linear NN converges to. Expected ordering,
which the live NN should reproduce:
    LS worst everywhere; ideal MMSE best; learned estimator ~ MMSE without
    needing the channel statistics (it learns them from data).
NMSE is averaged over test channels; channel: 64-subcarrier OFDM, exponential
power-delay profile (frequency-correlated Rayleigh).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "figures"))
import matplotlib.pyplot as plt
from talk_style import apply_style, save, C_BLUE, C_ORANGE, C_AQUA

apply_style()
rng = np.random.default_rng(5)

Nsc, Ltap = 64, 8
NTRAIN, NTEST = 4000, 2000
SNRS = np.arange(0, 26, 5)

# frequency-domain channel covariance from exponential PDP
p = np.exp(-np.arange(Ltap) / 3.0); p /= p.sum()
F = np.exp(-2j * np.pi * np.outer(np.arange(Nsc), np.arange(Ltap)) / Nsc)
Rh = F @ np.diag(p) @ F.conj().T                      # exact covariance

def draw_H(n):
    g = (rng.standard_normal((n, Ltap)) + 1j * rng.standard_normal((n, Ltap)))
    g *= np.sqrt(p / 2)
    return g @ F.T                                    # (n, Nsc)

H_tr, H_te = draw_H(NTRAIN), draw_H(NTEST)
nmse = {"LS": [], "MMSE": [], "learned": []}

for snr_db in SNRS:
    s2 = 10 ** (-snr_db / 10)
    noise = lambda H: H + np.sqrt(s2 / 2) * (rng.standard_normal(H.shape) +
                                             1j * rng.standard_normal(H.shape))
    Yls_tr, Yls_te = noise(H_tr), noise(H_te)         # pilot X=1 -> LS = Y

    # LS
    nmse["LS"].append(np.mean(np.abs(Yls_te - H_te) ** 2) /
                      np.mean(np.abs(H_te) ** 2))
    # ideal MMSE (knows Rh and sigma^2)
    W = Rh @ np.linalg.inv(Rh + s2 * np.eye(Nsc))
    Hm = Yls_te @ W.T
    nmse["MMSE"].append(np.mean(np.abs(Hm - H_te) ** 2) /
                        np.mean(np.abs(H_te) ** 2))
    # learned linear estimator (ridge on training data; no stats knowledge)
    A = Yls_tr.conj().T @ Yls_tr / NTRAIN + 1e-6 * np.eye(Nsc)
    B = Yls_tr.conj().T @ H_tr / NTRAIN
    Wl = np.linalg.solve(A, B)
    Hl = Yls_te @ Wl
    nmse["learned"].append(np.mean(np.abs(Hl - H_te) ** 2) /
                           np.mean(np.abs(H_te) ** 2))

for k in nmse:
    print(k, ["%.2f dB" % (10 * np.log10(v)) for v in nmse[k]])

fig, ax = plt.subplots(figsize=(9.5, 6.0))
ax.plot(SNRS, 10 * np.log10(nmse["LS"]), "-o", color=C_BLUE, label="LS")
ax.plot(SNRS, 10 * np.log10(nmse["MMSE"]), "-s", color=C_ORANGE,
        label="ideal MMSE (knows $R_h$, $\\sigma^2$)")
ax.plot(SNRS, 10 * np.log10(nmse["learned"]), "-^", color=C_AQUA,
        label="learned from data (no statistics)")
ax.set_xlabel("SNR (dB)"); ax.set_ylabel("NMSE (dB)")
ax.legend(fontsize=13)
ax.set_title("OFDM channel estimation, 64 subcarriers, exp. PDP\n"
             "(backup: Python learned-linear stand-in for the MATLAB NN)")
save(fig, "backup_demo5.png", subdir="demo_backups")
print("gen_demo5_backup: done")
