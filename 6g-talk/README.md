# 6G Talk — *Signal Processing for Beyond-5G and 6G Communications*

A complete, self-contained package for a **90-minute invited talk**: a Beamer
slide deck, a 1:1 PowerPoint mirror, five live MATLAB demos (with Python
verification mirrors and pre-computed backups), all shared figures, and the
planning documents (slide-by-slide outline + minute-by-minute timing plan). The
talk walks the audience through the 6G physical layer as a sequence of signal
processing problems — new spectrum, waveforms beyond OFDM, ultra-massive MIMO,
RIS, ISAC, AI-native PHY, multiple access, NTN, and the standards roadmap — with
five demos interleaved so each one runs immediately after the section that
motivates it.

---

## Directory map

```
6g-talk/
├── README.md                     ← this file
│
├── outline/
│   ├── outline.md                slide-by-slide script: 70 numbered slides + 5 appendix backups
│   └── timing_plan.md            90-minute timing table, demo placement, contingencies
│
├── beamer/                       Beamer deck — Metropolis theme, pdflatex
│   ├── main.tex                  master file; \input's the 11 sections + appendix
│   ├── main.pdf                  compiled deck (86 pages)
│   ├── main.{aux,log,nav,out,snm,toc}   build artifacts (git-ignored)
│   ├── sections/
│   │   ├── sec01_opening.tex … sec11_closing.tex   (11 section files)
│   │   └── appendix_backups.tex  A1–A5 "pre-computed result" slides (one per demo)
│   ├── tikz/
│   │   ├── otfs_chain.tex         OTFS transceiver block diagram
│   │   ├── hybrid_bf.tex          hybrid analog/digital beamforming
│   │   ├── ris_geometry.tex       BS → RIS → UE geometry
│   │   └── isac_rx.tex            ISAC receiver (comm + sensing branches)
│   └── figures/                  empty — the deck pulls PNGs from ../figures via \graphicspath
│
├── figures/                      shared matplotlib figures (used by BOTH deck and pptx)
│   ├── make_figures.py           regenerates every shared PNG below
│   ├── talk_style.py             palette + Matplotlib rcParams (imported by make_figures)
│   ├── fig_*.png                 ~18 slide figures (timeline, spectrum, PAPR, N² law, …)
│   └── demo_backups/
│       └── backup_demo1.png … backup_demo5.png   images shown on appendix slides A1–A5
│
├── matlab/                       five live, on-stage demos
│   ├── DEMO_GUIDE.md             per-demo runbook: exact commands, narration, expected output, failure fixes
│   ├── demo1_ofdm_vs_otfs/run_demo.m          OFDM vs OTFS at 500 km/h
│   ├── demo2_hybrid_beamforming/run_demo.m    64-element steering slider + hybrid vs digital SE
│   ├── demo3_ris_gain/run_demo.m              RIS N² law, 16 → 1024 elements
│   ├── demo4_isac_range_doppler/run_demo.m    ISAC range–Doppler map from a data frame
│   ├── demo5_dl_channel_estimation/run_demo.m LS vs MMSE vs a small trained NN
│   └── verification/             Python/NumPy mirrors + backup-figure generators
│       ├── verify_demo1_otfs.py  verify_demo3_ris.py  verify_demo4_isac.py
│       └── gen_demo2_backup.py   gen_demo5_backup.py
│
├── pptx/                         PowerPoint mirror of the Beamer deck
│   ├── build_pptx.py             builds 6g_talk.pptx from content.py
│   ├── content.py                slide content + REFERENCES list (single source of truth)
│   ├── latex_render.py           LaTeX → 300-dpi PNG for equations/TikZ (needs pdflatex + ImageMagick)
│   ├── 6g_talk.pptx              compiled deck
│   └── figures/                  rendered eq_*.png + tikz PNGs (render cache)
│
├── handout/                      audience cheat-sheet
│   ├── cheatsheet.tex            2-page A4 source (equations, comparison table, 15 refs)
│   └── cheatsheet.pdf            compiled handout (exactly 2 pages)
│
└── .venv/                        Python virtualenv (git-ignored; recreate — see §4)
```

> `__pycache__/` and `.DS_Store` files appear throughout and are git-ignored.

---

## 1. How to compile the Beamer deck

```bash
cd beamer
pdflatex main.tex      # first pass
pdflatex main.tex      # second pass — resolves x/total frame numbers + progress bar
```

Run `pdflatex` **twice**: the Metropolis frame numbering (`numbering=fraction`)
and progress bar need the totals from the first pass.

**LaTeX requirements** (a full TeX Live / MacTeX install has all of these):

- the **`metropolis`** Beamer theme (`\usetheme{metropolis}`)
- **`appendixnumberbeamer`** — keeps the 5 appendix backup frames out of the
  `x / total` count
- `lmodern`, `amsmath`, `amssymb`, `bm`, `booktabs`, `graphicx`, `tikz`
  (with the `arrows.meta, positioning, calc, fit, shapes.geometric,
  decorations.pathmorphing` libraries)

The deck resolves figures through `\graphicspath{{../figures/}{../figures/demo_backups/}}`,
so regenerate the figures (§4) before compiling if any are missing.

**Output:** `beamer/main.pdf` — **86 pages** = 70 numbered content slides
+ title/section-divider/standout frames + the **5 appendix backup slides**
(A1–A5).

> Speaker notes are embedded via `\note{}`. To build a notes-on-second-screen
> version, uncomment line 12 of `main.tex`
> (`\setbeameroption{show notes on second screen=right}`).

---

## 2. Set up the Python environment (needed for §4 and §5)

The figure generator and the PowerPoint builder both run in a local venv:

```bash
python3 -m venv .venv
source .venv/bin/activate                      # zsh/bash; use activate.fish / .csh as needed
pip install numpy matplotlib scipy python-pptx  # python-pptx pulls in Pillow
```

`python-pptx` installs **Pillow** as a dependency (used by `build_pptx.py` to
size images). `scipy` is used by the figure scripts (`scipy.special.j0`).

---

## 3. (Re)generate the shared figures

All slide figures are produced by matplotlib and shared between the Beamer and
PowerPoint decks, so they only need to be built once.

```bash
# from the repo root, with the venv active (or call ../.venv/bin/python directly)
cd figures
python make_figures.py            # writes all fig_*.png at 300 dpi into figures/
```

`make_figures.py` imports `talk_style.py` (palette + presentation-ready
rcParams); keep both in the same directory.

To (re)build the **demo backup images** and cross-check the demo math against the
MATLAB scripts, run the Python verification mirrors:

```bash
cd matlab/verification
python verify_demo1_otfs.py       # writes figures/demo_backups/backup_demo1.png (+ shared figs)
python verify_demo3_ris.py        # → backup_demo3.png
python verify_demo4_isac.py       # → backup_demo4.png
python gen_demo2_backup.py        # → backup_demo2.png
python gen_demo5_backup.py        # → backup_demo5.png
```

(Demos 1/3/4 have full NumPy mirrors; demos 2/5 have backup-figure generators
only, per the plan.) These are what the appendix slides A1–A5 display when a live
demo has to be skipped.

---

## 4. Build the PowerPoint deck and the handout

### PowerPoint (`6g_talk.pptx`)

```bash
cd pptx
python build_pptx.py              # or: ../.venv/bin/python build_pptx.py
```

`build_pptx.py` reads all slide content from `content.py` and mirrors the Beamer
deck 1:1 (16:9, dark title/section/standout slides, light content slides, speaker
notes in the notes pane). Equations and TikZ block diagrams are rendered to
300-dpi transparent PNGs by `latex_render.py` and inserted as images.

**Extra requirements for the PPTX build** (beyond the venv in §2):

- **`pdflatex`** — `latex_render.py` compiles each equation / TikZ snippet
- **ImageMagick** (`magick` or `convert`) — crops the rendered PDFs to PNG
- rendered images are cached in `pptx/figures/`; delete that folder to force a
  clean re-render

**Output:** `pptx/6g_talk.pptx`.

### Handout (`cheatsheet.pdf`)

A **2-page A4 cheat-sheet** — every key equation grouped by theme, the waveform
comparison table, an AI-native PHY block, a "key numbers" box, the five-demo
summary, and all 15 references. Rebuild with:

```bash
cd handout
pdflatex cheatsheet.tex            # run twice
pdflatex cheatsheet.tex
```

Needs only a standard TeX Live install (`extarticle`, `amsmath`, `booktabs`,
`multicol`, `enumitem`, `titlesec`). Print **double-sided** (2 pages → 1 A4 sheet)
and hand out one per attendee. **Output:** `handout/cheatsheet.pdf` — exactly 2 pages.

> For a printable *slide* handout instead, compile the Beamer deck with the
> `handout` class option (`\documentclass[aspectratio=169,11pt,handout]{beamer}`),
> `pdflatex main.tex` twice, and print 2-up / 4-up.

---

## 5. Demo run order and the 90-minute timing plan

The five MATLAB demos are **interleaved**: each runs on the closing slide of its
host section, then you return to the deck at the next section divider. Full
narration, expected console output, and failure fixes are in
[`matlab/DEMO_GUIDE.md`](matlab/DEMO_GUIDE.md).

| Demo | Runs after | On slide | Command (`cd` first, then run) | Live time |
|------|-----------|:--------:|--------------------------------|:---------:|
| **D1** OFDM vs OTFS @ 500 km/h | Sec. 3 (Waveforms) | 20 | `cd matlab/demo1_ofdm_vs_otfs; run_demo` | ~3.5 min |
| **D2** 64-element steering + hybrid SE | Sec. 4 (UM-MIMO) | 29 | `cd matlab/demo2_hybrid_beamforming; run_demo` | ~3.5 min |
| **D3** RIS N² law (16 → 1024) | Sec. 5 (RIS) | 35 | `cd matlab/demo3_ris_gain; run_demo` | ~2.5 min |
| **D4** ISAC range–Doppler map | Sec. 6 (ISAC) | 42 | `cd matlab/demo4_isac_range_doppler; run_demo` | ~3 min |
| **D5** Learned vs MMSE estimation | Sec. 7 (AI-PHY) | 50 | `cd matlab/demo5_dl_channel_estimation; run_demo` | ~2.5 min |

Each demo is one command, typed ahead during the preceding slide. If a demo
fails on stage, **do not debug live** — advance to the matching backup slide
**A1–A5** (pre-computed figures from `figures/demo_backups/`), read the one-line
result, and move on.

### 90-minute timing table (from `outline/timing_plan.md`)

Model: 70 min slides · 15 min live demos · 5 min Q&A buffer. Wall clock assumes a
0:00 start.

| # | Segment | Slides | Duration | Wall clock |
|---|---------|--------|----------|------------|
| 1 | Opening & motivation | 1–5 | 6 min | 0:00–0:06 |
| 2 | New spectrum frontiers | 6–11 | 7 min | 0:06–0:13 |
| 3 | Waveforms beyond OFDM | 12–20 | 10 min | 0:13–0:23 |
| — | **➤ DEMO 1: OFDM vs OTFS @ 500 km/h** | (live) | 3.5 min | 0:23–0:26½ |
| 4 | Ultra-massive MIMO & beamforming | 21–29 | 10 min | 0:26½–0:36½ |
| — | **➤ DEMO 2: hybrid beamforming + steering slider** | (live) | 3.5 min | 0:36½–0:40 |
| 5 | RIS | 30–35 | 6 min | 0:40–0:46 |
| — | **➤ DEMO 3: RIS N² scaling law** | (live) | 2.5 min | 0:46–0:48½ |
| 6 | ISAC | 36–42 | 8 min | 0:48½–0:56½ |
| — | **➤ DEMO 4: ISAC range–Doppler map** | (live) | 3 min | 0:56½–0:59½ |
| 7 | AI-native physical layer | 43–50 | 8 min | 0:59½–1:07½ |
| — | **➤ DEMO 5: LS vs MMSE vs NN channel estimation** | (live) | 2.5 min | 1:07½–1:10 |
| 8 | Multiple access & sharing | 51–55 | 5 min | 1:10–1:15 |
| 9 | NTN & new media | 56–60 | 4 min | 1:15–1:19 |
| 10 | Energy, standards & roadmap | 61–65 | 4 min | 1:19–1:23 |
| 11 | Demo recap, takeaways, open problems, refs, thanks | 66–70 | 2 min | 1:23–1:25 |
| — | Q&A buffer | — | ~5 min | 1:25–1:30 |

**Pacing checkpoints / cuts** (see `timing_plan.md` for detail): at 0:26½ drop
S15 to a one-liner if behind; at 1:07½ D5 is the first demo to skip (show A5
instead); Sections 9–10 are the designed "flex zone" (compress 8 → 5 min by
dropping S58/S60/S64). Hard-stop escape hatch: jump to the takeaways slide (S67)
from anywhere. Every demo is ≤ 60 s of compute — if one hangs > 20 s, kill it and
jump to its appendix backup.

---

## 6. Pre-talk checklist

- [ ] **Fonts embedded in the PDF.** Verify with `pdffonts beamer/main.pdf` —
      every font should read `emb = yes` (the deck uses `lmodern`, which embeds
      Type 1 fonts). Do the same for any exported PPTX/PDF.
- [ ] **PDF tested on the venue laptop / projector** at the actual resolution and
      aspect ratio (16:9). Open in the presentation software you will actually
      use; confirm the progress bar, colors, and TikZ diagrams render.
- [ ] **MATLAB path set** — `addpath` the repo or plan to `cd` into each demo
      folder (scripts save figures relative to their own location, but MATLAB
      must be able to *find* `run_demo`).
- [ ] **Toolboxes present.** On a comms-lab machine, confirm **Signal
      Processing**, **Communications**, and **Deep Learning** toolboxes are
      licensed. Reality check from `DEMO_GUIDE.md`: **D1–D4 use base MATLAB
      only**; **only D5 requires the Deep Learning Toolbox** (it degrades
      gracefully to a learned-linear estimator if absent, but the NN story lands
      better with it installed).
- [ ] **Backup figures ready.** Confirm all five `figures/demo_backups/backup_demo*.png`
      exist and that appendix slides A1–A5 display them (they are your fallback
      if a live demo fails).
- [ ] **D5 `pretrained_net.mat` generated ahead of time.** The repo ships
      **without** it. Run D5 once cold during pre-flight so it trains and caches
      the file (~20–30 s cold; ~2–4 s every run after). **Never let first-ever
      training happen on stage.**
- [ ] **Slider demo needs a display.** Open MATLAB in **full desktop mode** (not
      `-nodisplay` / `-batch`) — D2's live steering slider needs a real figure
      window.
- [ ] **Smoke-test all five demos** from the exact `cd` commands in §5, confirm
      each console block prints and each PNG re-saves into `figures/`.
- [ ] **Projector-failure fallback:** mirror the MATLAB figure windows to the
      deck laptop beforehand in case the live window can't be projected.
- [ ] **Handout printed.** `handout/cheatsheet.pdf` (2 pages) printed
      double-sided, one per attendee.

---

## 7. A note on the references

The 15 IEEE-style references (in `pptx/content.py::REFERENCES`, on
`beamer/sections/sec11_closing.tex` slide 69, and in `handout/cheatsheet.tex`)
were **compiled from memory** and have **not
been verified against the original sources**. Spot-check every author list,
title, venue, volume/issue, and year — and confirm the ITU-R M.2160 and 3GPP
release details — before presenting or distributing the deck.
