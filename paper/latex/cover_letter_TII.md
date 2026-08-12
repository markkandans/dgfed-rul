# Cover Letter — IEEE Transactions on Industrial Informatics

[DATE]

Dear Editor-in-Chief,

I am pleased to submit my manuscript, "DGFed: Drift-Governed Federated
Learning for Industrial Remaining Useful Life Estimation," for consideration
as a regular paper in IEEE Transactions on Industrial Informatics.

Predictive maintenance at the industrial edge faces three coupled obstacles
that prior federated learning (FL) work treats in isolation: statistical
heterogeneity across assets, non-stationary degradation (concept drift), and
constrained, unreliable uplinks. The manuscript proposes DGFed, in which a
single per-client drift signal — a Page–Hinkley detector on prediction
residuals — jointly governs the communication schedule and the server-side
aggregation weighting, on top of error-feedback top-k sparsification with
8-bit quantization. On the C-MAPSS benchmark under two heterogeneity
partitions with injected degradation-stage drift, DGFed reaches FedAvg-level
accuracy at 8.0x lower uplink volume, and the trade-off transfers to a
held-out subset under a completely frozen configuration, with one boundary reported.

Two aspects may particularly interest the TII readership beyond the framework
itself. First, the evaluation discipline: every component claim is backed by five-seed paired statistics and activity diagnostics that verify each mechanism
actually operates at the reported operating point, with configuration
calibrated on a development subset and confirmed on a held-out one. Second,
an audited negative result: the representation–head personalization pattern
common in federated prognostics degrades accuracy in 9 of 10 paired seeds in
this setting, and the finding is dissected until three candidate mechanisms
are excluded — a cautionary, actionable result for practitioners, reported
with its boundary conditions stated.

All reported numbers are pinned to 100 hash-verified artifacts; the code,
result files, and manifest are publicly archived at [ZENODO DOI]. The
C-MAPSS dataset is publicly available from the NASA Prognostics Center of
Excellence.

This manuscript is original, has not been published previously, and is not
under consideration elsewhere. I declare [NO CONFLICTS OF INTEREST / list].
This work received no external funding.

Thank you for your consideration.

Sincerely,

Markkandan S
School of Electronics Engineering,
Vellore Institute of Technology, Chennai, India
ORCID: 0000-0003-3704-4536
E-mail: markkandan.s@vit.ac.in
