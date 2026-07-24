"""Generate all shared (non-demo) figures for the 6G talk.

Run:  ../.venv/bin/python make_figures.py     (from figures/)
Each figure is presentation-ready (>=14 pt fonts, thick lines) and saved
as 300-dpi PNG into this directory. Physics-accurate where a model is
standard; clearly labeled 'illustrative' where it is conceptual.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy.special import j0
from talk_style import (apply_style, save, PALETTE, C_BLUE, C_ORANGE, C_AQUA,
                        C_YELLOW, C_MAGENTA, ACCENT, INK, INK2, GRID)

apply_style()
rng = np.random.default_rng(6)


# ----------------------------------------------------------------------
# S2 — evolution timeline 1G -> 6G
# ----------------------------------------------------------------------
def fig_evolution_timeline():
    gens = [
        ("1G", 1980, "Analog FM voice\nFDMA"),
        ("2G", 1990, "Digital voice + SMS\nGMSK, TDMA (GSM)"),
        ("3G", 2000, "Mobile data\nCDMA, RAKE RX"),
        ("4G", 2010, "Mobile broadband\nOFDM + MIMO, turbo"),
        ("5G", 2020, "eMBB / URLLC / mMTC\nmMIMO, mmWave, LDPC"),
        ("6G", 2030, "ISAC, AI-native PHY,\nsub-THz, NTN-native"),
    ]
    fig, ax = plt.subplots(figsize=(12.5, 4.6))
    ax.set_xlim(1971, 2041); ax.set_ylim(-2.6, 2.9); ax.axis("off")
    ax.annotate("", xy=(2040, 0), xytext=(1972, 0),
                arrowprops=dict(arrowstyle="-|>", lw=2.5, color=INK2))
    for i, (g, yr, txt) in enumerate(gens):
        up = (i % 2 == 0)
        y = 1.15 if up else -1.15
        col = ACCENT if g == "6G" else C_BLUE
        ax.plot([yr, yr], [0, y * 0.45], color=INK2, lw=1.4)
        ax.plot(yr, 0, "o", ms=10, color=col, zorder=5)
        ax.add_patch(FancyBboxPatch((yr - 6.3, y - (0 if up else 1.15)),
                                    12.6, 1.15,
                                    boxstyle="round,pad=0.12,rounding_size=0.18",
                                    fc="white", ec=col, lw=2.0))
        ax.text(yr, y + (0.58 if up else -0.58), txt, ha="center", va="center",
                fontsize=11.5, color=INK)
        ax.text(yr, 0.42 if up else -0.42, f"{g} · {yr}s", ha="center",
                va="bottom" if up else "top", fontsize=15, fontweight="bold",
                color=col)
    ax.set_title("Every generation is defined by its physical-layer signal processing",
                 pad=14)
    save(fig, "fig_evolution_timeline.png")


# ----------------------------------------------------------------------
# S6 — spectrum landscape
# ----------------------------------------------------------------------
def fig_spectrum_landscape():
    bands = [
        ("Sub-6 GHz\n(coverage workhorse)", 0.6, 7.125, C_BLUE),
        ("FR3 'golden bands'\n7–24 GHz", 7.125, 24.25, C_AQUA),
        ("FR2 mmWave\n24–71 GHz", 24.25, 71, C_ORANGE),
        ("Sub-THz (research)\n100–300 GHz", 100, 300, C_MAGENTA),
        ("THz\n0.3–1 THz", 300, 1000, C_YELLOW),
    ]
    fig, ax = plt.subplots(figsize=(12.5, 3.9))
    ax.set_xscale("log"); ax.set_xlim(0.5, 1100); ax.set_ylim(0, 1.9)
    ax.get_yaxis().set_visible(False)
    for lbl, lo, hi, col in bands:
        ax.axvspan(lo, hi, ymin=0.08, ymax=0.55, color=col, alpha=0.75)
        ax.text(np.sqrt(lo * hi), 1.28, lbl, ha="center", va="center",
                fontsize=12.5, color=INK)
        ax.plot([np.sqrt(lo * hi)] * 2, [0.99, 1.06], color=INK2, lw=1.2,
                clip_on=False)
    ax.set_xlabel("Carrier frequency (GHz)")
    ax.set_xticks([1, 3.5, 7, 15, 28, 60, 100, 300, 1000])
    ax.set_xticklabels(["1", "3.5", "7", "15", "28", "60", "100", "300", "1000"])
    ax.grid(axis="x", which="both", alpha=0.35)
    ax.set_title("6G spectrum landscape: capacity moves up, coverage stays down")
    save(fig, "fig_spectrum_landscape.png")


# ----------------------------------------------------------------------
# S9 — atmospheric absorption vs frequency (illustrative, after ITU-R P.676)
# ----------------------------------------------------------------------
def fig_thz_absorption():
    f = np.linspace(5, 400, 4000)  # GHz
    # Lorentzian lines: (centre GHz, peak dB/km, half-width GHz), values chosen
    # to match well-known sea-level magnitudes (O2: 60, 118.75; H2O: 22.2, 183.3, 325).
    lines = [(22.235, 0.18, 3.0), (60.0, 15.0, 4.5), (118.75, 1.9, 2.5),
             (183.31, 28.0, 3.5), (325.15, 38.0, 4.0)]
    gamma = 0.006 * (f / 10) ** 1.7          # continuum (illustrative)
    for fc, pk, hw in lines:
        gamma = gamma + pk * hw**2 / ((f - fc) ** 2 + hw**2)
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    ax.semilogy(f, gamma, color=C_BLUE, lw=3.0)
    for lo, hi, name in [(75, 110, "W band"), (125, 170, "D band"), (200, 310, "G band")]:
        ax.axvspan(lo, hi, color=C_AQUA, alpha=0.13)
        ax.text((lo + hi) / 2, 0.004, name, ha="center", fontsize=13, color=C_AQUA)
    for fc, pk, _ in lines:
        ax.annotate(f"{fc:.0f}", (fc, pk * 1.25), ha="center", fontsize=12.5,
                    color=C_ORANGE)
    ax.set_xlabel("Frequency (GHz)"); ax.set_ylabel("Specific attenuation (dB/km)")
    ax.set_ylim(2e-3, 200); ax.set_xlim(5, 400)
    ax.set_title("Molecular absorption carves 'transmission windows'\n"
                 "(illustrative, after ITU-R P.676 line data; sea level)")
    save(fig, "fig_thz_absorption.png")


# ----------------------------------------------------------------------
# S10 — Rapp PA AM/AM
# ----------------------------------------------------------------------
def fig_pa_rapp():
    A = np.linspace(0, 2.0, 400); Asat = 1.0
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    for p, col in zip([1, 2, 3], [C_ORANGE, C_AQUA, C_MAGENTA]):
        out = A / (1 + (A / Asat) ** (2 * p)) ** (1 / (2 * p))
        ax.plot(A, out, color=col, label=f"Rapp, p = {p}")
    ax.plot(A, np.minimum(A, Asat), "--", color=INK2, lw=2.0,
            label="ideal limiter")
    ax.plot(A, A, ":", color=INK2, lw=1.6, label="linear")
    ax.axvspan(0, 0.5, color=C_BLUE, alpha=0.10)
    ax.text(0.25, 1.62, "back-off\nregion", ha="center", fontsize=13, color=C_BLUE)
    ax.set_xlabel("Normalized input amplitude"); ax.set_ylabel("Output amplitude")
    ax.set_ylim(0, 1.75); ax.legend(loc="lower right")
    ax.set_title("PA nonlinearity (Rapp model): back-off costs efficiency")
    save(fig, "fig_pa_rapp.png")


# ----------------------------------------------------------------------
# S13 — ICI power vs normalized Doppler
# ----------------------------------------------------------------------
def fig_ici_doppler():
    eps = np.logspace(-3, np.log10(0.4), 300)   # fd * Tsym
    # single Doppler shift (CFO-like): ICI = 1 - sinc^2(eps)
    ici_cfo = 1 - np.sinc(eps) ** 2
    # Jakes spectrum: P_ICI = 1 - 2*int_0^1 (1-x) J0(2 pi eps x) dx
    x = np.linspace(0, 1, 2000)
    ici_jakes = np.array([1 - 2 * np.trapezoid((1 - x) * j0(2 * np.pi * e * x), x)
                          for e in eps])
    bound = (np.pi * eps) ** 2 / 3
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.loglog(eps, ici_cfo, color=C_BLUE, label="single shift: $1-\\mathrm{sinc}^2(\\epsilon)$")
    ax.loglog(eps, ici_jakes, color=C_AQUA, label="Jakes spectrum (numerical)")
    ax.loglog(eps, bound, "--", color=C_ORANGE, label="bound $(\\pi\\epsilon)^2/3$")
    e500 = 0.108
    ax.axvline(e500, color=C_MAGENTA, lw=2, ls=":")
    ax.annotate("500 km/h\n(3.5 GHz/15 kHz or\n28 GHz/120 kHz)",
                (e500, 2e-3), xytext=(0.012, 4e-3), fontsize=12.5,
                color=C_MAGENTA, arrowprops=dict(arrowstyle="->", color=C_MAGENTA))
    ax.set_xlabel("Normalized Doppler  $\\epsilon = f_d T_{sym}$")
    ax.set_ylabel("ICI power (relative)")
    ax.set_ylim(1e-6, 1); ax.legend(loc="upper left", fontsize=12.5)
    ax.set_title("OFDM inter-carrier interference vs Doppler")
    save(fig, "fig_ici_doppler.png")


# ----------------------------------------------------------------------
# S14 — PAPR CCDF: CP-OFDM vs DFT-s-OFDM
# ----------------------------------------------------------------------
def fig_papr_ccdf():
    Nfft, Nact, Nsym, os_f = 2048, 1200, 8000, 2
    qpsk = (rng.choice([-1, 1], (Nsym, Nact)) +
            1j * rng.choice([-1, 1], (Nsym, Nact))) / np.sqrt(2)

    def papr_db(freq_syms):
        X = np.zeros((Nsym, Nfft * os_f), complex)
        k = np.arange(Nact) - Nact // 2
        X[:, k % (Nfft * os_f)] = freq_syms
        xt = np.fft.ifft(X, axis=1)
        p = np.abs(xt) ** 2
        return 10 * np.log10(p.max(1) / p.mean(1))

    papr_ofdm = papr_db(qpsk)
    papr_dfts = papr_db(np.fft.fft(qpsk, axis=1) / np.sqrt(Nact))
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    thr = np.linspace(3, 12.5, 200)
    for papr, col, lbl in [(papr_ofdm, C_BLUE, "CP-OFDM"),
                           (papr_dfts, C_ORANGE, "DFT-s-OFDM")]:
        ccdf = [(papr > t).mean() for t in thr]
        ax.semilogy(thr, ccdf, color=col, label=lbl)
    ax.set_ylim(1e-3, 1); ax.set_xlim(3, 12.5)
    ax.set_xlabel("PAPR$_0$ (dB)"); ax.set_ylabel("Pr(PAPR > PAPR$_0$)")
    ax.legend()
    ax.set_title("PAPR CCDF: DFT spreading buys $\\approx$3 dB of PA headroom\n"
                 f"(QPSK, {Nact} tones, {Nsym} symbols, {os_f}$\\times$ oversampling)")
    save(fig, "fig_papr_ccdf.png")


# ----------------------------------------------------------------------
# S20 — waveform scorecard heat-table
# ----------------------------------------------------------------------
def fig_waveform_scorecard():
    rows = ["CP-OFDM", "DFT-s-OFDM", "SC-FDE", "OTFS", "AFDM"]
    cols = ["Low PAPR", "Doppler\nrobustness", "Low RX\ncomplexity",
            "MIMO\nmaturity", "Standards\nreadiness"]
    S = np.array([[1, 2, 5, 5, 5],
                  [4, 2, 4, 4, 5],
                  [5, 3, 3, 3, 3],
                  [2, 5, 2, 2, 1],
                  [3, 5, 3, 2, 1]], float)
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    im = ax.imshow(S, cmap=plt.cm.Blues, vmin=0, vmax=5.6, aspect="auto")
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            ax.text(j, i, f"{S[i, j]:.0f}", ha="center", va="center",
                    fontsize=16, fontweight="bold",
                    color="white" if S[i, j] >= 4 else INK)
    ax.set_xticks(range(len(cols)), cols, fontsize=13)
    ax.set_yticks(range(len(rows)), rows, fontsize=14)
    ax.grid(False)
    for edge in np.arange(-.5, len(cols)):
        ax.axvline(edge, color="white", lw=2)
    for edge in np.arange(-.5, len(rows)):
        ax.axhline(edge, color="white", lw=2)
    ax.set_title("Waveform scorecard (5 = best; author's assessment)")
    save(fig, "fig_waveform_scorecard.png")


# ----------------------------------------------------------------------
# S24 — hybrid vs digital beamforming spectral efficiency (OMP, SV channel)
# ----------------------------------------------------------------------
def _sv_channel(Nt, Nr, L, rng):
    """Narrowband Saleh–Valenzuela mmWave channel, ULAs, half-wavelength."""
    at = lambda th: np.exp(1j * np.pi * np.arange(Nt) * np.sin(th)) / np.sqrt(Nt)
    ar = lambda th: np.exp(1j * np.pi * np.arange(Nr) * np.sin(th)) / np.sqrt(Nr)
    H = np.zeros((Nr, Nt), complex)
    aod = rng.uniform(-np.pi / 3, np.pi / 3, L)
    aoa = rng.uniform(-np.pi / 3, np.pi / 3, L)
    g = (rng.standard_normal(L) + 1j * rng.standard_normal(L)) / np.sqrt(2)
    for l in range(L):
        H += g[l] * np.outer(ar(aoa[l]), at(aod[l]).conj())
    return H * np.sqrt(Nt * Nr / L), aod

def _omp_hybrid(Fopt, Nrf, Nt):
    """El Ayach spatially-sparse precoding via OMP over a DFT-like dictionary."""
    G = 128
    thetas = np.arcsin(np.linspace(-1, 1, G, endpoint=False) + 1 / G)
    A = np.exp(1j * np.pi * np.outer(np.arange(Nt), np.sin(thetas))) / np.sqrt(Nt)
    Frf = np.zeros((Nt, 0), complex); Fres = Fopt
    for _ in range(Nrf):
        idx = np.argmax(np.sum(np.abs(A.conj().T @ Fres) ** 2, axis=1))
        Frf = np.hstack([Frf, A[:, [idx]]])
        Fbb = np.linalg.lstsq(Frf, Fopt, rcond=None)[0]
        Fres = Fopt - Frf @ Fbb
        n = np.linalg.norm(Fres, "fro")
        if n > 1e-12:
            Fres = Fres / n
    Fbb = np.linalg.lstsq(Frf, Fopt, rcond=None)[0]
    Fbb *= np.linalg.norm(Fopt, "fro") / np.linalg.norm(Frf @ Fbb, "fro")
    return Frf, Fbb

def fig_hybrid_se():
    Nt, Nr, L, Ns, Nrf, trials = 64, 16, 6, 4, 4, 60
    snr_db = np.arange(-10, 21, 5)
    se = {k: np.zeros(len(snr_db)) for k in ("dig", "hyb", "ana")}
    for _ in range(trials):
        H, aod = _sv_channel(Nt, Nr, L, rng)
        U, s, Vh = np.linalg.svd(H)
        Fopt = Vh.conj().T[:, :Ns]
        Frf, Fbb = _omp_hybrid(Fopt, Nrf, Nt)
        Fhyb = Frf @ Fbb
        # analog-only: steer one beam at the strongest path, single stream
        fana = np.exp(1j * np.pi * np.arange(Nt) * np.sin(aod[0])) / np.sqrt(Nt)
        for i, sdb in enumerate(snr_db):
            rho = 10 ** (sdb / 10)
            for key, F, ns in (("dig", Fopt, Ns), ("hyb", Fhyb, Ns),
                               ("ana", fana[:, None], 1)):
                M = np.eye(Nr) + (rho / ns) * H @ F @ F.conj().T @ H.conj().T
                se[key][i] += np.real(np.log2(np.linalg.det(M))) / trials
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.plot(snr_db, se["dig"], "-o", color=C_BLUE, label="fully digital (SVD)")
    ax.plot(snr_db, se["hyb"], "-s", color=C_ORANGE,
            label=f"hybrid OMP ({Nrf} RF chains)")
    ax.plot(snr_db, se["ana"], "-^", color=C_AQUA, label="analog only (1 beam)")
    ax.set_xlabel("SNR (dB)"); ax.set_ylabel("Spectral efficiency (bit/s/Hz)")
    ax.legend()
    ax.set_title(f"{Nt}$\\times${Nr} mmWave MIMO, {L} paths, "
                 f"$N_s$ = {Ns} streams")
    save(fig, "fig_hybrid_se.png")


# ----------------------------------------------------------------------
# S40 — ISAC rate vs ranging-accuracy trade-off (conceptual, CRB-based)
# ----------------------------------------------------------------------
def fig_rate_crb():
    gamma_db, B = 20.0, 100e6
    gamma = 10 ** (gamma_db / 10)
    beta = B / np.sqrt(12)               # RMS bandwidth of flat spectrum
    alpha = np.linspace(0.02, 0.98, 200) # resource share given to sensing
    rate = np.log2(1 + (1 - alpha) * gamma)
    sig_tau = 1 / (2 * np.pi * beta * np.sqrt(2 * alpha * gamma))
    rmse_cm = 3e8 * sig_tau / 2 * 100
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.plot(rmse_cm, rate, color=C_BLUE)
    for a, lbl, dx in [(0.05, "5% to sensing", 0), (0.5, "50/50", 0),
                       (0.95, "95% to sensing", 8)]:
        i = np.argmin(np.abs(alpha - a))
        ax.plot(rmse_cm[i], rate[i], "o", color=C_ORANGE, ms=11)
        ax.annotate(lbl, (rmse_cm[i], rate[i]),
                    xytext=(rmse_cm[i] * 1.15 + dx, rate[i] + 0.25), fontsize=13)
    ax.set_xscale("log")
    ax.set_xlabel("Range RMSE at the CRB (cm)")
    ax.set_ylabel("Comm. rate (bit/s/Hz)")
    ax.set_title("One waveform, two masters: resource split moves you\n"
                 "along the rate–accuracy boundary  (B = 100 MHz, SNR = 20 dB)")
    save(fig, "fig_rate_crb.png")


# ----------------------------------------------------------------------
# S57 — LEO Doppler profile over a pass
# ----------------------------------------------------------------------
def fig_leo_doppler():
    Re, h, fc = 6371e3, 600e3, 2e9
    mu = 3.986004418e14
    r = Re + h
    v = np.sqrt(mu / r); w = v / r
    t = np.linspace(-360, 360, 2000)
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    for el_max, col in [(90, C_BLUE), (30, C_ORANGE)]:
        # ground station at latitude offset so that max elevation = el_max
        # geometry: offset angle phi0 between GS and orbital plane
        el = np.deg2rad(el_max)
        # slant range at closest approach from elevation:
        d0 = -Re * np.sin(el) + np.sqrt((Re * np.sin(el)) ** 2 + h**2 + 2 * Re * h)
        cos_g0 = (Re**2 + r**2 - d0**2) / (2 * Re * r)
        phi0 = np.arccos(np.clip(cos_g0, -1, 1))
        theta = w * t                              # in-plane angle from closest approach
        cos_gam = np.cos(phi0) * np.cos(theta)
        d = np.sqrt(Re**2 + r**2 - 2 * Re * r * cos_gam)
        fd = -np.gradient(d, t) * fc / 3e8
        ax.plot(t / 60, fd / 1e3, color=col,
                label=f"max elevation {el_max}°")
    ax.axhline(0, color=INK2, lw=1)
    ax.set_xlabel("Time from closest approach (min)")
    ax.set_ylabel("Doppler shift (kHz)")
    ax.legend(loc="upper right", fontsize=13)
    ax.set_title("LEO Doppler, 600 km orbit, $f_c$ = 2 GHz:\n"
                 "$\\pm$50 kHz swing, steepest rate at zenith")
    save(fig, "fig_leo_doppler.png")


# ----------------------------------------------------------------------
# S61 — BS power breakdown (illustrative)
# ----------------------------------------------------------------------
def fig_energy_breakdown():
    cats = ["Macro\n3.5 GHz mMIMO", "mmWave\n28 GHz", "Sub-THz\n(projection)"]
    comp = ["PA", "RF chains", "ADC/DAC", "Baseband DSP", "Cooling/other"]
    frac = np.array([[0.55, 0.12, 0.05, 0.13, 0.15],
                     [0.40, 0.22, 0.12, 0.14, 0.12],
                     [0.30, 0.25, 0.22, 0.13, 0.10]])
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    bottom = np.zeros(3)
    for j, (c, col) in enumerate(zip(comp, PALETTE)):
        ax.bar(cats, frac[:, j], 0.55, bottom=bottom, color=col, label=c,
               edgecolor="white", linewidth=2)
        for i in range(3):
            if frac[i, j] >= 0.10:
                ax.text(i, bottom[i] + frac[i, j] / 2, f"{frac[i, j]*100:.0f}%",
                        ha="center", va="center", fontsize=12.5,
                        color="white" if j in (0, 2) else INK)
        bottom += frac[:, j]
    ax.set_ylim(0, 1.18); ax.set_ylabel("Share of BS power (illustrative)")
    ax.legend(ncol=3, loc="upper center", fontsize=12)
    ax.set_title("Where the watts go: ADC/DAC share grows with bandwidth")
    ax.grid(axis="x")
    save(fig, "fig_energy_breakdown.png")


# ----------------------------------------------------------------------
# S62 — 3GPP / ITU timeline
# ----------------------------------------------------------------------
def fig_release_timeline():
    rows = [
        ("Rel-18  (5G-Advanced)", 2022.0, 2024.5, C_BLUE),
        ("Rel-19  (ISAC model, AI/ML)", 2024.0, 2026.5, C_AQUA),
        ("Rel-20  (6G study)", 2025.3, 2027.5, C_ORANGE),
        ("Rel-21  (6G normative)", 2027.3, 2029.5, C_MAGENTA),
        ("ITU IMT-2030 (M.2160 → specs)", 2023.0, 2030.0, C_YELLOW),
    ]
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    for i, (lbl, a, b, col) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, b - a, left=a, height=0.55, color=col, alpha=0.85)
        ax.text(a - 0.12, y, lbl, ha="right", va="center", fontsize=13.5)
    for x, lbl in [(2023.9, "WRC-23"), (2027.9, "WRC-27"), (2029.0, "first 6G spec")]:
        ax.axvline(x, color=INK2, ls=":", lw=1.6)
        ax.text(x, len(rows) - 0.25, lbl, rotation=0, ha="center", fontsize=12,
                color=INK2)
    ax.set_xlim(2016.5, 2030.6); ax.set_ylim(-0.6, len(rows))
    ax.set_xticks(np.arange(2022, 2031)); ax.get_yaxis().set_visible(False)
    ax.grid(axis="y")
    ax.set_title("The road to 6G: 3GPP releases and the ITU process")
    save(fig, "fig_release_timeline.png")


# ----------------------------------------------------------------------
# S5/S65 — talk roadmap as a signal chain
# ----------------------------------------------------------------------
def fig_roadmap():
    boxes = ["Spectrum\n(§2)", "Waveforms\n(§3)", "Ultra-massive\nMIMO (§4)",
             "RIS\n(§5)", "ISAC\n(§6)", "AI-native\nPHY (§7)",
             "Multiple\naccess (§8)", "NTN & new\nmedia (§9)",
             "Energy &\nroadmap (§10)"]
    demo_after = {1: "D1", 2: "D2", 3: "D3", 4: "D4", 5: "D5"}
    fig, ax = plt.subplots(figsize=(13.5, 2.9))
    ax.set_xlim(-0.4, len(boxes) * 1.52); ax.set_ylim(-0.9, 1.35); ax.axis("off")
    for i, b in enumerate(boxes):
        x = i * 1.52
        ax.add_patch(FancyBboxPatch((x, 0), 1.30, 0.85,
                     boxstyle="round,pad=0.06,rounding_size=0.12",
                     fc="#eef4fb", ec=C_BLUE, lw=2))
        ax.text(x + 0.65, 0.425, b, ha="center", va="center", fontsize=10.6)
        if i < len(boxes) - 1:
            ax.add_patch(FancyArrowPatch((x + 1.37, 0.425), (x + 1.50, 0.425),
                         arrowstyle="-|>", mutation_scale=20, color=INK2, lw=2))
        if i in demo_after:
            ax.add_patch(plt.Circle((x + 0.65, -0.45), 0.21, fc=ACCENT, ec="none"))
            ax.text(x + 0.65, -0.45, demo_after[i], ha="center", va="center",
                    fontsize=11.5, color="white", fontweight="bold")
    ax.text(-0.25, -0.45, "live\ndemos:", ha="right", va="center", fontsize=11.5,
            color=ACCENT)
    save(fig, "fig_roadmap.png")


if __name__ == "__main__":
    fig_evolution_timeline()
    fig_spectrum_landscape()
    fig_thz_absorption()
    fig_pa_rapp()
    fig_ici_doppler()
    fig_papr_ccdf()
    fig_waveform_scorecard()
    fig_hybrid_se()
    fig_rate_crb()
    fig_leo_doppler()
    fig_energy_breakdown()
    fig_release_timeline()
    fig_roadmap()
    print("All shared figures done.")
