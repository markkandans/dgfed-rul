# Figure Specifications & Remaining TODOs

Hand this file to Claude Code in the project session — it knows the exact JSON
schemas in `results/` and can generate every figure and fill every TODO.

## Figures (target: PDF/PNG ≥300 DPI, readable in grayscale, IEEE column widths 3.5"/7.16")

**Fig. 1 — DONE (generated: latex/figures/fig1_loop.pdf via make_fig1.py).** Block diagram per the caption
in Sec. IV-A: client block (local training → PH detector on residuals → upload
decision → EF top-k + 8-bit) and server block (decompress → adaptive clip →
weighted aggregation → broadcast), with the drift flag d_k drawn as ONE signal
feeding BOTH the upload gate and the aggregation weight. Tools: draw.io/TikZ.

**Fig. 2 — Communication–accuracy plane.**
Source: `results/FD004_{unit,regime}/` method JSONs + calibrated proposed.
x = total uplink MB (log scale), y = RMSE (mean, ±std error bars). Points:
FedAvg, FedProx, DGFed(proposed), DGFed-P; local at x→0 marker; centralized as
horizontal dashed line. Two panels (unit | regime). Takeaway visible: DGFed far
left at FedAvg height.

**Fig. 3 — Paired-seed delta strip plot.**
Source: `results/analysis_paired_seed_FD004.json`.
For each arm (−drift, −trigger, −aggregation, −compression, +personal_head):
three per-seed Δ points vs. proposed, unit and regime side by side, zero line,
mean marker. Shows sign consistency at a glance (personal head 6/6 above zero).

**Fig. 4 — Retention curves.**
Source: per-seed `retention_rmse_bins` in `results/FD004_{calibrated,rebased}/`.
x = tail bin 1..5, y = RMSE. Panels: unit | regime. Series: DGFed(proposed) and
DGFed-P (mean across seeds, ±std band). Regime panel should show the rising
erosion; unit flat-to-mild.

**Fig. 5 — λ calibration sweep.**
Source: `results/ph_sweep_FD004_unit.json` + observed fire rates (unit 7.9→8.1%,
regime 19% at λ=5000; FD002 6.7%/14.3% as annotated points).
x = λ (log), y = drift-fire rate %, shaded 3–8% target band, chosen λ=5000
marked; annotate regime/FD002 transfer points to visualize the portability
limitation.

## Numeric TODOs in manuscript.md (grep "TODO")

1. DONE (inserted in main.tex from Claude Code's extraction). ~~Table II Score cells~~ — pull `score` per seed from
   `results/FD004_calibrated/ablation_{unit,regime}.json` (no_personal_head and
   full arms), report mean±std.
2. Ref [18] volume/issue/pages — verify on IEEE Xplore.
3. Repository/supplementary URL in Sec. V-F once the repo is public.
4. Author block.
5. References pass: expand to 30+, add DOIs, renumber by first appearance.

## Prompt to paste into Claude Code

"Read paper/figure_specs_and_todos.md. Generate Figs. 2–5 as 300-DPI PDFs+PNGs
into paper/figures/ from the referenced results JSONs (grayscale-safe palettes,
IEEE column widths), extract the Table II score cells it lists (mean±std across
seeds) and print them, and verify every number already present in
paper/manuscript.md Tables II–VII against the pinned artifacts in
results_manifest.json, reporting any mismatch without editing the manuscript."
