"""Python/NumPy mirror of matlab/demo1_ofdm_vs_otfs/run_demo.m.

Purpose: sanity-check the math before the live MATLAB run, and generate the
static figures used on the slides and the backup slide (A1).

Model (mirrors the MATLAB demo exactly):
  * Doubly-selective channel, P discrete paths, integer delay taps l_i,
    Doppler nu_i = fd_max * cos(theta_i), fd_max from v = 500 km/h @ 28 GHz.
  * OTFS frame: M = 32 delay bins x N = 16 Doppler bins, QPSK.
      TX:  x_dd --(ISFFT row/col form: s = (F_N^H kron I_M) x)--> time samples
      channel applied in time domain (cyclic over the frame)
      RX:  y = (F_N kron I_M) r, LMMSE detection with the exact H_eff.
  * OFDM frame: 16 consecutive CP-OFDM symbols, 32 subcarriers, same channel,
      per-subcarrier 1-tap LMMSE equalizer (mid-symbol channel) -> ICI floor.
  * BER vs SNR for both; delay-Doppler channel-magnitude heatmap.

Expected result: OFDM shows an error floor above ~1e-2 at high SNR; OTFS keeps
falling (no floor within the simulated range).
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "figures"))
import matplotlib.pyplot as plt
from talk_style import apply_style, save, C_BLUE, C_ORANGE, INK2

apply_style()
rng = np.random.default_rng(1)

# ----------------------------- parameters (keep in sync with MATLAB) --------
M, N = 32, 16                # delay bins (subcarriers) x Doppler bins (symbols)
df = 60e3                    # subcarrier spacing [Hz]
fc = 28e9                    # carrier [Hz]
v_kmh = 500.0
P = 4                        # channel paths
Lcp = 8                      # OFDM CP length [samples]
SNRS = np.arange(0, 31, 5)   # dB
NFRAMES = 40                 # channel realizations per SNR point

fs = M * df                  # sample rate
Ts = 1 / fs
Tsym = 1 / df                # OFDM useful symbol time
fd_max = v_kmh / 3.6 * fc / 3e8
print(f"fd_max = {fd_max/1e3:.2f} kHz | eps = fd*Tsym = {fd_max*Tsym:.3f} "
      f"| Doppler res = {df/N/1e3:.2f} kHz")

Fn = np.fft.fft(np.eye(N)) / np.sqrt(N)          # unitary DFT (N)


def draw_channel():
    """P paths: integer delays, Jakes-drawn Dopplers, unit average power."""
    delays = np.concatenate([[0], rng.integers(1, 6, P - 1)])
    dopp = fd_max * np.cos(rng.uniform(0, 2 * np.pi, P))
    gains = (rng.standard_normal(P) + 1j * rng.standard_normal(P)) / np.sqrt(2 * P)
    return delays, dopp, gains


def channel_time_matrix(delays, dopp, gains):
    """G: time-domain channel over one OTFS frame, cyclic in the frame."""
    NM = N * M
    n = np.arange(NM)
    G = np.zeros((NM, NM), complex)
    for l, nu, g in zip(delays, dopp, gains):
        ph = g * np.exp(1j * 2 * np.pi * nu * (n - l) * Ts)
        G[n, (n - l) % NM] += ph
    return G


def apply_channel_linear(x, delays, dopp, gains, nstart):
    """Linear (non-cyclic) convolution for the OFDM path; nstart = abs sample idx."""
    y = np.zeros(len(x) + 5, complex)
    n = nstart + np.arange(len(x))
    for l, nu, g in zip(delays, dopp, gains):
        y[l:l + len(x)] += g * np.exp(1j * 2 * np.pi * nu * (n - l) * Ts) * x
    return y[:len(x)]


def qpsk(bits):
    return ((1 - 2 * bits[0::2]) + 1j * (1 - 2 * bits[1::2])) / np.sqrt(2)


def demod(sym):
    b = np.empty(2 * len(sym), int)
    b[0::2] = (sym.real < 0); b[1::2] = (sym.imag < 0)
    return b


# ----------------------------- simulation -----------------------------------
ber_ofdm = np.zeros(len(SNRS)); ber_otfs = np.zeros(len(SNRS))
nbits = 2 * N * M

for f in range(NFRAMES):
    delays, dopp, gains = draw_channel()

    # ---- OTFS: effective DD-domain matrix via the time-domain operator
    G = channel_time_matrix(delays, dopp, gains)
    A = np.kron(Fn.conj().T, np.eye(M))          # DD -> time
    H_eff = A.conj().T @ G @ A                   # DD input-output matrix
    HhH = H_eff.conj().T @ H_eff

    bits_t = rng.integers(0, 2, nbits)
    x_dd = qpsk(bits_t)
    s_time = A @ x_dd
    r_clean = G @ s_time

    # ---- OFDM: 16 symbols with CP through the same physical channel
    bits_o = rng.integers(0, 2, nbits)
    Xf = qpsk(bits_o).reshape(N, M)              # N symbols x M subcarriers
    tx_syms, rx_clean_syms = [], []
    nstart = 0
    for i in range(N):
        xt = np.fft.ifft(Xf[i]) * np.sqrt(M)
        xt_cp = np.concatenate([xt[-Lcp:], xt])
        tx_syms.append(xt_cp)
        rx_clean_syms.append(apply_channel_linear(xt_cp, delays, dopp, gains, nstart))
        nstart += M + Lcp

    for si, snr_db in enumerate(SNRS):
        sigma2 = 10 ** (-snr_db / 10)

        # OTFS LMMSE
        y = r_clean + np.sqrt(sigma2 / 2) * (rng.standard_normal(N * M) +
                                             1j * rng.standard_normal(N * M))
        y_dd = A.conj().T @ y
        x_hat = np.linalg.solve(HhH + sigma2 * np.eye(N * M),
                                H_eff.conj().T @ y_dd)
        ber_otfs[si] += np.mean(demod(x_hat) != bits_t) / NFRAMES

        # OFDM per-symbol 1-tap LMMSE (mid-symbol frequency response)
        errs = 0
        nstart = 0
        for i in range(N):
            r = rx_clean_syms[i] + np.sqrt(sigma2 / 2) * (
                rng.standard_normal(M + Lcp) + 1j * rng.standard_normal(M + Lcp))
            Yf = np.fft.fft(r[Lcp:]) / np.sqrt(M)
            nmid = nstart + Lcp + M // 2
            h_t = np.zeros(M, complex)
            for l, nu, g in zip(delays, dopp, gains):
                h_t[l] += g * np.exp(1j * 2 * np.pi * nu * (nmid - l) * Ts)
            Hf = np.fft.fft(h_t)
            Xhat = Yf * Hf.conj() / (np.abs(Hf) ** 2 + sigma2)
            errs += np.sum(demod(Xhat) != bits_o[2 * M * i:2 * M * (i + 1)])
            nstart += M + Lcp
        ber_ofdm[si] += errs / nbits / NFRAMES

print("SNR(dB):", SNRS)
print("BER OFDM:", np.array2string(ber_ofdm, precision=4))
print("BER OTFS:", np.array2string(ber_otfs, precision=4))

# ----------------------------- figures --------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 6.0))
ax.semilogy(SNRS, ber_ofdm, "-o", color=C_BLUE, label="CP-OFDM, 1-tap LMMSE")
ax.semilogy(SNRS, ber_otfs, "-s", color=C_ORANGE, label="OTFS, LMMSE (DD domain)")
ax.set_xlabel("SNR (dB)"); ax.set_ylabel("BER")
ax.set_ylim(1e-5, 1); ax.legend()
ax.set_title(f"QPSK, 500 km/h @ 28 GHz ($f_d$ = {fd_max/1e3:.1f} kHz), "
             f"{P} paths\nOFDM hits an ICI floor — OTFS keeps falling")
save(fig, "fig_demo1_ber.png")

# DD-domain channel heatmap (quantized Doppler bins) + TF magnitude, side by side
delays, dopp, gains = draw_channel()
Hdd = np.zeros((M, N))
for l, nu, g in zip(delays, dopp, gains):
    k = int(round(nu / (df / N)))       # Doppler bin: resolution = 1/(N T) = df/N
    Hdd[l, (k + N // 2) % N] += np.abs(g)
Htf = np.zeros((M, N))
for i in range(N):
    nmid = i * (M + Lcp) + Lcp + M // 2
    h_t = np.zeros(M, complex)
    for l, nu, g in zip(delays, dopp, gains):
        h_t[l] += g * np.exp(1j * 2 * np.pi * nu * nmid * Ts)
    Htf[:, i] = np.abs(np.fft.fft(h_t))

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))
im0 = axes[0].imshow(Htf, aspect="auto", origin="lower", cmap="Blues",
                     extent=[0, N, 0, M])
axes[0].set_xlabel("OFDM symbol (time)"); axes[0].set_ylabel("subcarrier (freq)")
axes[0].set_title("Time–frequency: |H| fades everywhere")
fig.colorbar(im0, ax=axes[0], shrink=0.85)
im1 = axes[1].imshow(Hdd, aspect="auto", origin="lower", cmap="Blues",
                     extent=[-N // 2, N // 2, 0, M])
axes[1].set_xlabel("Doppler bin"); axes[1].set_ylabel("delay bin")
axes[1].set_title(f"Delay–Doppler: {P} taps, quasi-static")
fig.colorbar(im1, ax=axes[1], shrink=0.85)
for a in axes:
    a.grid(False)
save(fig, "fig_tf_vs_dd.png")

# combined backup figure for slide A1
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "..", "figures", "demo_backups"), exist_ok=True)
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.4))
axes[0].semilogy(SNRS, ber_ofdm, "-o", color=C_BLUE, label="CP-OFDM")
axes[0].semilogy(SNRS, ber_otfs, "-s", color=C_ORANGE, label="OTFS")
axes[0].set_xlabel("SNR (dB)"); axes[0].set_ylabel("BER")
axes[0].set_ylim(1e-5, 1); axes[0].legend()
axes[0].set_title("BER, QPSK, 500 km/h @ 28 GHz")
im = axes[1].imshow(Hdd, aspect="auto", origin="lower", cmap="Blues",
                    extent=[-N // 2, N // 2, 0, M])
axes[1].set_xlabel("Doppler bin"); axes[1].set_ylabel("delay bin")
axes[1].grid(False)
axes[1].set_title("Delay–Doppler channel grid")
fig.colorbar(im, ax=axes[1], shrink=0.85)
save(fig, "backup_demo1.png", subdir="demo_backups")
print("verify_demo1: done")
