# Timing Plan — 90-Minute Talk (Interleaved Demos)

**Model:** 70 min slide talk · 15 min live MATLAB demos (interleaved after their home sections) · 5 min Q&A buffer.
Wall-clock column assumes a 0:00 start.

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

**Totals:** 70 slides · 70 min talk + 15 min demos + 5 min Q&A = 90 min.

## Demo logistics (interleaved)

- Keep MATLAB open on a second desktop/monitor all talk; each demo pre-loaded as
  `cd <demo folder>; run_demo` — one command each, typed ahead during the preceding slide.
- Each host section's final slide *is* the transition slide (S20, S29, S35, S42, S50) —
  it states what to watch for before you switch windows.
- After each demo, return to the deck at the next section divider — a natural re-entry point.

## Pacing checkpoints (glance at clock)

- **0:26½** — Demo 1 done. If > 0:29, drop S15 (filtered MC) to a one-liner and trim S25.
- **0:48½** — entering ISAC. If behind by > 3 min, cut Demo 3's narration to 1 min (plot is self-explanatory).
- **1:07½** — Demo 5 is the first candidate to *skip entirely* (show appendix A5 instead, saves 2 min).
- **1:15** — Sections 9–10 are the designed "flex zone": can compress 8 → 5 min by dropping S58/S60 and S64.
- Demos overrun protection: every demo ≤ 60 s compute; if one hangs > 20 s, kill it and jump to its appendix backup slide (A1–A5).

## Contingency

- Hard-stop venue: takeaways slide (S67) is the "land the plane" slide — jump to it from anywhere.
- MATLAB failure: appendix slides A1–A5 carry the exact expected outputs; narrate over them.
- Projector failure of live window: mirror MATLAB figures to the deck laptop beforehand (see README pre-talk checklist).
