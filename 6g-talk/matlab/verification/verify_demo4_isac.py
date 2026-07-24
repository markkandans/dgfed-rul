"""Python/NumPy mirror of matlab/demo4_isac_range_doppler/run_demo.m.

OFDM-based ISAC (Sturm & Wiesbeck): the SAME QPSK-modulated OFDM frame that
carries data illuminates two moving targets. Monostatic receiver:

  Y[n,m] = sum_t a_t * X[n,m] * exp(-j2pi n df tau_t) * exp(+j2pi m To fD_t) + W

  D = Y ./ X                (data symbols divide out - "channel sounding for free")
  range profile:  IFFT over subcarriers n  (tau axis)
  Doppler:        FFT  over symbols m      (fD axis)

Resolutions:  dR = c/(2 B),  dv = c/(2 fc M_sym To).
Targets: (40 m, +15 m/s) and (75 m, -25 m/s), SNR 10 dB.
Expected: two clean peaks within one bin of the true (R, v); peak SNR ~ 10 dB
+ 10log10(N*M) processing gain.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "figures"))
import matplotlib.pyplot as plt
from talk_style import apply_style, save, C_ORANGE

apply_style()
rng = np.random.default_rng(4)

# ------------------- parameters (keep in sync with MATLAB) ------------------
c0 = 3e8
fc = 28e9
df = 120e3                   # subcarrier spacing
Nsc = 256                    # subcarriers
Msym = 128                   # OFDM symbols
CP = 0.07                    # CP fraction
To = (1 + CP) / df           # total symbol duration
B = Nsc * df

targets = [dict(R=40.0, v=+15.0, a=1.0),
           dict(R=75.0, v=-25.0, a=0.7)]
snr_db = 10.0

dR = c0 / (2 * B)
dv = c0 / (2 * fc * Msym * To)
Rmax = c0 / (2 * df)
vmax = c0 / (4 * fc * To)
print(f"B = {B/1e6:.1f} MHz | dR = {dR:.2f} m | dv = {dv:.2f} m/s "
      f"| Rmax = {Rmax:.0f} m | vmax = ±{vmax:.0f} m/s")

# ------------------- simulate ----------------------------------------------
bits = rng.integers(0, 2, (Nsc, Msym, 2))
X = ((1 - 2 * bits[..., 0]) + 1j * (1 - 2 * bits[..., 1])) / np.sqrt(2)

n = np.arange(Nsc)[:, None]
m = np.arange(Msym)[None, :]
Y = np.zeros((Nsc, Msym), complex)
for t in targets:
    tau = 2 * t["R"] / c0
    fD = 2 * t["v"] * fc / c0
    Y += t["a"] * X * np.exp(-1j * 2 * np.pi * n * df * tau) \
                   * np.exp(1j * 2 * np.pi * m * To * fD)
sigma = 10 ** (-snr_db / 20)
Y += sigma * (rng.standard_normal(Y.shape) + 1j * rng.standard_normal(Y.shape)) / np.sqrt(2)

# ------------------- range-Doppler processing -------------------------------
D = Y / X                                     # divide out the data
Drd = np.fft.ifft(D, axis=0)                  # range profile per symbol
Drd = np.fft.fft(Drd, axis=1)                 # Doppler across symbols
Drd = np.fft.fftshift(Drd, axes=1)
P = 20 * np.log10(np.abs(Drd) + 1e-12)
P -= P.max()

r_axis = np.arange(Nsc) * dR
v_axis = (np.arange(Msym) - Msym // 2) * dv

# ------------------- peak detection (simple) --------------------------------
half = Nsc // 2                                # only unambiguous positive range
Psub = P[:half]
found = []
Ptmp = Psub.copy()
for _ in range(len(targets)):
    i, j = np.unravel_index(np.argmax(Ptmp), Ptmp.shape)
    found.append((r_axis[i], v_axis[j], Psub[i, j]))
    Ptmp[max(0, i - 4):i + 5, max(0, j - 4):j + 5] = -200   # mask neighborhood
for (R, v, p) in found:
    print(f"detected: R = {R:6.1f} m, v = {v:+6.1f} m/s  ({p:.1f} dB)")
for t in targets:
    ok = any(abs(R - t['R']) <= 2 * dR and abs(v - t['v']) <= 2 * dv
             for (R, v, _) in found)
    print(f"truth   : R = {t['R']:6.1f} m, v = {t['v']:+6.1f} m/s  "
          f"-> {'MATCH' if ok else 'MISS'}")

# ------------------- figure -------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.2))
ext = [v_axis[0], v_axis[-1], r_axis[0], r_axis[half - 1]]
im = ax.imshow(Psub, aspect="auto", origin="lower", extent=ext,
               cmap="viridis", vmin=-40, vmax=0)
ax.grid(False)
fig.colorbar(im, ax=ax, label="relative power (dB)")
for (R, v, _) in found:
    ax.plot(v, R, "o", ms=18, mfc="none", mec=C_ORANGE, mew=3)
    ax.annotate(f"{R:.0f} m, {v:+.0f} m/s", (v, R), xytext=(v + 8, R + 6),
                color="white", fontsize=14)
ax.set_xlabel("Radial velocity (m/s)"); ax.set_ylabel("Range (m)")
ax.set_xlim(-60, 60); ax.set_ylim(0, 150)
ax.set_title("Range–Doppler map from a data-carrying OFDM frame\n"
             f"({Nsc} subcarriers $\\times$ {Msym} symbols, "
             f"$\\Delta R$ = {dR:.1f} m, $\\Delta v$ = {dv:.1f} m/s)")
save(fig, "fig_demo4_rd_map.png")

import shutil
figdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "figures")
shutil.copy(os.path.join(figdir, "fig_demo4_rd_map.png"),
            os.path.join(figdir, "demo_backups", "backup_demo4.png"))
print("verify_demo4: done")
