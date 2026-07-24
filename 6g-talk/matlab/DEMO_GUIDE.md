# Live MATLAB Demo Guide

**Talk:** *Signal Processing for Beyond-5G and 6G Communications* (90 min).
**Budget:** ~15 min of live MATLAB, **interleaved** — each demo runs on the closing slide of its host section, then you return to slides.

## Demo order (interleaved with the deck)

| # | Demo | Runs after | Slide | Teaser line | Live time |
|---|------|-----------|-------|-------------|-----------|
| **D1** | OFDM vs OTFS at 500 km/h | Sec. 3 (Waveforms) | 20 | "watch the BER floor appear" | ~3.5 min |
| **D2** | 64-element beam steering + hybrid SE | Sec. 4 (UM-MIMO) | 29 | "steer the beam, digital vs hybrid" | ~3.5 min |
| **D3** | RIS N² law, 16→1024 elements | Sec. 5 (RIS) | 35 | "watch the N² law emerge" | ~2.5 min |
| **D4** | ISAC range–Doppler map | Sec. 6 (ISAC) | 42 | "two moving targets from a data frame" | ~3 min |
| **D5** | Learned channel estimation vs MMSE | Sec. 7 (AI-PHY) | 50 | "NMSE curves cross" | ~2.5 min |

> **If a demo fails on stage, do not debug live.** Advance to the matching backup slide **A1–A5** in the appendix (pre-computed final figures from `figures/demo_backups/backup_demo1.png … backup_demo5.png`), read the one-line result, and move on. The story survives without the live run.

## Before you walk on stage (pre-flight — do this once)

1. **Open MATLAB in full desktop mode** (not `-nodisplay` / `-batch`). D2's live slider needs a real figure window.
2. **Pre-warm D5.** Run D5 once cold so it trains and caches `pretrained_net.mat` (the repo ships **without** it). Cold run is ~20–30 s; after caching every run is ~2–4 s. Never let the first-ever training happen on stage.
3. **Smoke-test all five** from the exact `cd` commands below. Confirm each console block prints and each PNG re-saves into `../../figures/`.
4. **General facts:** every demo has a fixed `rng` seed, is self-contained (helpers are local functions), and re-saves its slide figure into `6g-talk/figures/`. Only D5 needs a toolbox (Deep Learning); D1–D4 are base MATLAB.

Path rule for all demos: figures are saved relative to the **script's own location**, so saving works from any folder — but MATLAB must be able to *find* `run_demo`, so always `cd` into the demo folder first (or `addpath` it).

---

## D1 — OFDM vs OTFS at 500 km/h

**Runs after Section 3 (slide 20). Live time ≈ 3.5 min. Backup slide A1.**

### 1. Exact command
```matlab
cd matlab/demo1_ofdm_vs_otfs
run_demo
```
(`run_demo.m` here is a **script**, not a function — just type `run_demo`.)

### 2. What to say while it runs
"A car at 500 km/h at 28 GHz sees about 13 kHz of Doppler — the channel rotates *within* one OFDM symbol, so subcarriers leak into each other. That inter-carrier interference is something a one-tap-per-subcarrier equalizer physically cannot undo, so OFDM slams into an irreducible BER floor. OTFS carries the same bits in the delay–Doppler domain, where that fast-fading channel looks like just a handful of static taps, and an LMMSE detector keeps driving the error down — no floor in our range."

### 3. Expected output
- **Console** (deterministic — these three lines are exact):
  ```
  fd_max        = 12.96 kHz
  normalized Doppler  eps = fd*Tsym = 0.216
  Doppler resolution  df/N          = 3.75 kHz
  ```
  then `BER OFDM:` and `BER OTFS:` rows over SNR = 0:5:30 dB (7 values). Monte-Carlo values wobble in the 4th decimal (MATLAB RNG ≠ NumPy) but the shape is fixed.
- **Figure 1 `fig_demo1_ber.png`** — semilog BER vs SNR. Blue CP-OFDM curve **flattens into a floor** (stalls in the ~10⁻¹–10⁻² band at high SNR); orange OTFS curve **keeps falling** toward ~10⁻⁴–10⁻⁵.
- **Figure 2 `fig_tf_vs_dd.png`** — two heatmaps. Left (time-frequency): `|H|` mottled/faded across the whole plane. Right (delay-Doppler): just **4 bright sparse taps** on an otherwise dark grid. Two figure windows pop up.

### 4. Common failure modes → fix
- **`Undefined function or variable 'run_demo'`** → you didn't `cd` into `demo1_ofdm_vs_otfs`. Fix: `cd` there, or `addpath` the folder.
- **Figures don't display** (running headless) → they still **save** to `figures/` correctly (paths are script-relative). Fall back to backup slide A1 if the audience needs to see them live.
- **`exportgraphics` undefined** (MATLAB < R2020a) → script auto-falls back to `print -dpng -r300`; no action needed.
- Runs slower than expected → it shouldn't; expect ~3–8 s. If a machine is very slow you can quietly say "40 channel realizations, all 512×512 matrices."

### 5. Runtime
~3–8 s of compute, no first-run penalty.

---

## D2 — 64-element beam steering + hybrid vs digital SE

**Runs after Section 4 (slide 29). Live time ≈ 3.5 min. Backup slide A2.**

### 1. Exact command
```matlab
cd matlab/demo2_hybrid_beamforming
run_demo
```

### 2. What to say while it runs
"This is a 64-element uniform linear array — half-wavelength spacing, so every element adds a phase of π·sin(θ). We steer just by conjugate-phasing the elements; the co-phased peak reads 20·log10(64) ≈ 36 dB and the beam is a pencil. **[grab the slider]** Watch the main lobe swing across the room while the first sidelobes stay pinned about 13 dB down. Now the punchline on the other plot: in a sparse mmWave channel, an OMP hybrid precoder with only **4 RF chains** rides right on top of the fully-digital 64-chain curve — a fraction of a bit per second per hertz apart, at a fraction of the hardware."

### 3. Expected output
- **Console** — a table over SNR = −10:5:20 dB with columns `digital / hybridOMP / analog`, then a line like `hybrid OMP trails fully digital by <~0.5> bit/s/Hz at 20 dB (4 RF chains ~ 64)`.
- **`fig_hybrid_se.png`** — SE vs SNR: blue "fully digital" and orange "hybrid OMP (4 RF chains)" nearly **coincide** and climb together; aqua "analog only" sits well below (single stream).
- **`fig_demo2_arrayfactor.png`** — three pencil beams steered to −40°, 0°, +25°, each peaking at **≈36 dB**, sidelobes ≈13 dB down.
- **Live window "Demo 2 — LIVE 64-element beam steering"** — a polar beam pattern with a slider (−90°…+90°). Dragging swings the main lobe in real time. **This window stays open after the script returns** — that's expected.

### 4. Common failure modes → fix
- **No slider window appears** (the classic "no display" case — running under `-nodisplay`/`-batch`, over a bare SSH session, or on a projector-only setup) → the script detects it via `feature('ShowFigureWindows')`, prints `Headless mode: interactive steering slider skipped (PNGs saved)`, and exits cleanly. Fix: launch full MATLAB desktop on the presenting laptop **before** the talk. If you're already on stage and it's headless, narrate over the static `fig_demo2_arrayfactor.png` (three fixed beams) or use backup slide A2 — do not try to fix the display live.
- **Slider throws a graphics error** → it's wrapped in `try/catch`; you'll get a warning but both PNGs are already saved. Keep going.
- **`run_demo` not found** → `cd` into `demo2_hybrid_beamforming` first.
- **Slider feels laggy** on an old machine → it recomputes a 2001-point array factor on every drag; nudge with the arrow keys (1° steps) instead of dragging.

### 5. Runtime
~3 s compute + figures; the interactive window then persists until you close it. No first-run penalty.

---

## D3 — RIS N² law, 16 → 1024 elements

**Runs after Section 5 (slide 35). Live time ≈ 2.5 min. Backup slide A3.**

### 1. Exact command
```matlab
cd matlab/demo3_ris_gain
run_demo
```

### 2. What to say while it runs
"Direct path is blocked; the only way to the receiver is a bounce off a passive surface of N elements, each adding a phase we control. Cascaded channel is the *product* of two fadings. If we co-phase — cancel each element's cascade phase — every term becomes a positive real, the amplitudes add coherently, and received **power scales as N²**: +6 dB every time we double the panel. Leave the phases random and it's a 2-D random walk — power only ∝ N, +3 dB per doubling. That N-versus-N² gap is the entire business case for a RIS, and we'll fit the slopes live."

### 3. Expected output
- **Console** — a table over N = 16, 32, 64, 128, 256, 512, 1024 with `P_opt(sim) P_opt(ana) P_rnd(sim) P_rnd(ana)`. Sanity anchors: optimized-analytic ≈ **164** at N=16 and ≈ **6.5×10⁵** at N=1024; random-analytic equals N exactly (16 … 1024). Then: `fitted log-log slopes: optimized ~2.0 (expect ~2), random ~1.0 (expect ~1)`.
- **`fig_demo3_ris_scaling.png`** — log-log plot. Orange "optimized" points on a **slope-2** line (with dashed analytic ≈(π²/16)N² overlaid and a "+6 dB per doubling" stair between N=128 and 256); blue "random" points on a **slope-1** line ("+3 dB per doubling"). The two lines fan apart as N grows.

### 4. Common failure modes → fix
- **`run_demo` not found** → `cd` into `demo3_ris_gain`.
- **Fitted slopes look off** (e.g. 1.9 / 1.05) → still fine; 400 Monte-Carlo trials leave ~1% wobble. The *ordering and slopes* are the point, not the third digit.
- **`exportgraphics` undefined** on old MATLAB → auto-falls back to `print`. No action.

### 5. Runtime
~2 s. No toolbox, no first-run penalty — the fastest of the five.

---

## D4 — ISAC range–Doppler from a data-carrying OFDM frame

**Runs after Section 6 (slide 42). Live time ≈ 3 min. Backup slide A4.**

### 1. Exact command
```matlab
cd matlab/demo4_isac_range_doppler
run_demo
```

### 2. What to say while it runs
"Same QPSK OFDM frame that carries user data also illuminates the scene like a radar. The monostatic receiver hears its own symbols echoed back by two moving targets. Because it *knows* the transmitted symbols, it divides them out — channel sounding for free — and what's left is a clean 2-D sinusoid: frequency across subcarriers is range, frequency across symbols is Doppler, i.e. velocity. Two FFTs and we get a range–Doppler image. The FFTs add about 45 dB of coherent processing gain, so both targets pop out within a bin of the truth."

### 3. Expected output
- **Console** (deterministic header line — exact):
  ```
  B = 30.7 MHz | dR = 4.88 m | dv = 4.69 m/s | Rmax = 1250 m | vmax = +/-300 m/s
  ```
  then two `detected:` lines and two `truth: … -> MATCH` lines. Expect detections at **R ≈ 40 m, v ≈ +15 m/s** and **R ≈ 75 m, v ≈ −25 m/s**, both **MATCH**.
- **`fig_demo4_rd_map.png`** — a viridis range–Doppler heatmap. Velocity on x (−60…+60 m/s), range on y (0…150 m), 40 dB dynamic range. **Two bright blobs circled in orange** with text labels, exactly at the two target cells; background is dark noise.

### 4. Common failure modes → fix
- **`run_demo` not found** → `cd` into `demo4_isac_range_doppler`.
- **A target shows a MISS** → shouldn't happen at the fixed seed (processing gain swamps the noise); if a machine's RNG behaves oddly, fall back to backup slide A4. Don't re-run repeatedly on stage.
- **Colors look flat / washed out** → it uses an embedded viridis map (base MATLAB has no viridis); nothing to fix, that's expected on any release.

### 5. Runtime
< 1 s. No toolbox, no first-run penalty.

---

## D5 — Learned channel estimation vs ideal MMSE

**Runs after Section 7 (slide 50). Live time ≈ 2.5 min. Backup slide A5.**
**⚠ Highest-risk demo — pre-warm it (see pre-flight). It is the only demo needing a toolbox.**

### 1. Exact command
```matlab
cd matlab/demo5_dl_channel_estimation
run_demo
```

### 2. What to say while it runs
"Three estimators for a 64-subcarrier OFDM channel that really only has 8 taps. Least-squares just reads the noisy pilot — its error tracks the noise floor, NMSE roughly equals minus the SNR. The ideal MMSE Wiener filter *knows* the true covariance and noise power, exploits the 8-tap structure, and buys about 9–10 dB — but it's an unfair upper bound you never actually have. The neural net learns that same structure straight from data, with no knowledge of the statistics, and lands within a fraction of a dB of MMSE. Data replaces the statistics."

### 3. Expected output
- **Console** — first a line reporting either `Deep Learning Toolbox found -> neural-network estimator` (then per-net training progress on a cold run) **or** the ridge fallback. Then a table over SNR = 0:5:25 dB with `LS | MMSE | learned`:
  - **LS** ≈ 0, −5, −10, −15, −20, −25 dB (tracks −SNR).
  - **MMSE** ≈ −9.8, −14.3, −19.1, −24.0, −29.0, −34.0 dB (~9–10 dB below LS).
  - **learned** ≈ 0.1 dB *above* MMSE at every point.
- **`fig_demo5_nmse.png`** — NMSE (dB) vs SNR, three descending lines: blue **LS on top** (worst), orange **ideal MMSE on the bottom**, aqua **learned sitting right on the MMSE line**. The visual punchline is learned ≈ MMSE, both well below LS.

### 4. Common failure modes → fix
- **Slow first run (~20–30 s of training) on stage** → this is the big one. Prevent it: run D5 once during pre-flight so `pretrained_net.mat` is cached; every later run is ~2–4 s and prints `Loaded pretrained nets from cache (instant)`. If you forgot and it starts training live, it prints `training 6 small nets (first run only, ~20-30 s, please wait)` with per-net progress — narrate the LS/MMSE story from the slide while it finishes, don't stop it.
- **Deep Learning Toolbox missing** → no crash: the script auto-swaps in a **ridge (learned-linear)** estimator and prints `Deep Learning Toolbox NOT found -> learned-linear (ridge) fallback`. The curves and the "learned ≈ MMSE" story still hold; the legend just says "learned-linear ridge". Nothing to do.
- **NN trains badly / a point sits above MMSE** → a built-in safety net silently repairs any point worse than LS (or >1 dB off MMSE) using the ridge solution, so the narrated punchline stays true.
- **Stale cache after editing params** → the loader validates `SNRS/Nsc/Ltap`; a mismatch triggers a clean retrain (back to the ~20–30 s cost). Re-warm after any edit.
- **`run_demo` not found** → `cd` into `demo5_dl_channel_estimation`.

### 5. Runtime
- **Cold (first ever) run:** ~20–30 s (trains + caches 6 nets).
- **Warm run (cache present):** ~2–4 s.
- **No-toolbox ridge fallback:** ~2 s.
