# DGFed: Drift-Governed Federated Learning for Industrial Remaining Useful Life Estimation

**Authors:** [TODO: author names, affiliations, ORCIDs, corresponding email]

**Target venue:** IEEE Transactions on Industrial Informatics (regular paper, double column)

---

## Abstract

Data-driven remaining useful life (RUL) estimation underpins predictive maintenance in industrial cyber-physical systems, yet fleet-wide training data is siloed across edge devices whose uplinks are constrained and whose degradation statistics are heterogeneous and non-stationary. While previous federated learning (FL) studies for prognostics have typically addressed heterogeneity, drift, or communication in isolation, there remains a critical need for a design in which these mechanisms are coordinated and their individual contributions are audited. Addressing this gap, the present study introduces DGFed, a drift-governed FL framework in which a per-client Page–Hinkley detector on prediction residuals governs both the communication schedule (event-triggered uploads) and the server aggregation (drift- and staleness-aware weighting with adaptive divergence clipping), combined with error-feedback top-k sparsification and 8-bit quantization. On the C-MAPSS FD004 benchmark under two heterogeneity partitions with injected degradation-stage drift, DGFed matches FedAvg within seed noise (RMSE 21.78 ± 1.16 versus 22.35 ± 0.99 on the 12-client unit-fleet partition) at 8.0× lower uplink volume (24.2 versus 193.5 MB), and the result transfers to held-out FD002 with a frozen configuration. A paired-seed component audit backed by activity diagnostics identifies drift-aware aggregation as the most consistent contributor, shows the event trigger to be accuracy-neutral with negligible bandwidth effect, and establishes a negative result: representation–head personalization degrades accuracy in all six paired seeds (+2.33 RMSE on the unit partition), with three candidate mechanisms excluded by targeted studies. All findings are multi-seed and pinned to released artifacts.

**Index Terms**—Federated learning, remaining useful life, predictive maintenance, concept drift, communication efficiency, industrial edge intelligence, prognostics and health management.

---

## I. Introduction

Unplanned downtime of rotating machinery, propulsion systems, and process equipment remains one of the dominant cost drivers in industrial operations, and remaining useful life (RUL) estimation is the prognostic capability that converts condition-monitoring streams into actionable maintenance schedules [1]–[5]. Modern deployments instrument each asset with an edge device that accumulates vibration, temperature, and operating-condition telemetry; collectively, a fleet holds precisely the run-to-failure diversity that data-driven RUL models need. In practice, however, this data rarely pools: raw telemetry is commercially sensitive, plant uplinks are bandwidth-constrained, and regulatory or contractual boundaries separate operators. Federated learning (FL) [6] offers the natural fit — collaborative model training without raw-data exchange — and has consequently attracted growing attention in prognostics and health management (PHM) [15]–[19].

An industrial federation, however, violates the assumptions of textbook FL in three coupled ways. First, client data is statistically heterogeneous: assets differ in load profile, age, and fault mode, so local distributions diverge (non-IID). Second, degradation is non-stationary: as a component wears, the relationship between sensed features and RUL shifts, so each client experiences concept drift on its own schedule. Third, edge participation is constrained: uplinks are metered and clients drop out or return stale updates. A critical limitation of existing FL-for-PHM approaches is that these three phenomena are treated by separate mechanisms designed in isolation — yet their solutions interfere. Personalization changes what "drift" means per client; drift-triggered retraining generates exactly the traffic that compression suppresses; and straggler-tolerant aggregation can silently absorb stale, drifted updates into the shared model.

This interference motivates the central design idea of this paper: a single per-client drift signal, computed on prediction residuals, that *governs* both the communication schedule and the server-side aggregation weighting, closing the loop between when a client speaks and how much its update counts. We call the resulting framework DGFed (drift-governed federated learning). A second, methodological motivation is independent of the design: component claims in this literature are rarely audited. Ablations are often single-seed, component "activity" (whether a mechanism actually fires at the operating point) is rarely verified, and configurations are tuned and evaluated on the same subset. We therefore commit to a paired-seed audit protocol with per-component activity diagnostics, a development/held-out subset split, and a pinned artifact manifest — and we report what the audit finds even where it contradicts our own initial design, which it does in one important respect.

The main novelty of this work is accordingly twofold: the coordinated drift-governed control loop itself, and the systematic, reproducible audit of which of its components earn their place under which heterogeneity regime. We do not claim a new learning algorithm in each component; detectors, sparsifiers, and weighted aggregation are established primitives. The contribution is their coupling, its evaluation discipline, and the resulting evidence — including a robust negative result on a widely used personalization pattern.

The contributions of this paper are:

- **Proposed DGFed**, a federated RUL framework in which a residual-based Page–Hinkley drift signal jointly governs event-triggered client uploads and drift/staleness-aware server aggregation with adaptive divergence clipping, on top of error-feedback top-k sparsification with 8-bit quantization. On C-MAPSS FD004 (12-client unit-fleet partition), DGFed attains RMSE 21.78 ± 1.16 versus FedAvg's 22.35 ± 0.99 at 8.0× lower uplink (24.2 vs. 193.5 MB), with the pattern replicated on a 6-client operating-regime partition (21.02 ± 1.16 vs. 20.12 ± 2.63 at 10.5 vs. 84.0 MB).
- **Conducted a paired-seed component audit** with activity diagnostics (drift-fire, upload-skip, and clip rates) across both partitions, identifying drift-aware aggregation as the most sign-consistent contributor (removal costs +0.85/+0.66 RMSE; positive in 5 of 6 paired seeds) and demonstrating that the event trigger is accuracy-neutral with negligible (≤0.7%) bandwidth savings — a claim boundary we state explicitly rather than imply.
- **Established and dissected a negative result**: naive joint-trained representation–head personalization degrades RUL accuracy in all 6 paired seeds (+2.33 ± 0.51 RMSE unit; +0.98 ± 0.63 regime), and three candidate mechanisms — unseen-degradation-stage generalization, head–body mismatch under aggregation, and client data scale — are excluded by targeted stratified, counterfactual-body, and regression studies, respectively.
- **Validated transfer on a held-out subset**: the complete frozen configuration, calibrated only on FD004, reproduces the accuracy–communication trade-off on C-MAPSS FD002 without any retuning, and every reported number is pinned to a released artifact via a hash manifest covering 37 result files.

Because this is an empirical systems study, we formalize the evaluation around three hypotheses, each accepted or rejected in Section VI:

- **H1** (communication–accuracy): H1₀ — DGFed's uplink reduction costs accuracy relative to FedAvg beyond seed noise; H1₁ — DGFed matches FedAvg within seed noise at materially lower uplink.
- **H2** (component non-uniformity): H2₀ — all DGFed components contribute equally; H2₁ — contributions are non-uniform and identifiable by paired-seed deltas.
- **H3** (personalization): H3₀ — a client-local prediction head does not improve accuracy under heterogeneity and drift; H3₁ — it improves accuracy, as commonly assumed in personalized FL for PHM [13], [15], [18].

The remainder of this paper is organized as follows. Section II reviews related work. Section III formalizes the federated RUL problem under drift and communication constraints. Section IV presents DGFed. Section V details the experimental setup, federation construction, and audit protocol. Section VI reports results and adjudicates H1–H3. Section VII discusses implications, Section VIII analyzes threats to validity, and Section IX concludes.

---

## II. Related Work

### A. Federated Learning and Communication Efficiency

FedAvg [6] established the canonical FL round — local SGD epochs followed by data-size-weighted parameter averaging — and FedProx [7] added a proximal term that stabilizes local updates under statistical heterogeneity; both serve as our baselines. Communication reduction has since developed along two largely orthogonal lines. Quantization and sparsification compress each update: QSGD [9] bounds the variance of stochastic quantization, top-k gradient sparsification transmits only the largest-magnitude coordinates [10], and error feedback [11] accumulates the discarded mass locally so that compression bias does not accumulate in the model — the mechanism we adopt. Event-triggered or lazily aggregated schemes instead reduce the *number* of transmissions, uploading only when an update is informative [12]. These lines are typically evaluated on stationary vision or language benchmarks; how a trigger should interact with client-local non-stationarity — where "nothing new to send" and "everything has changed" alternate — is not addressed, and our diagnostics show the interaction is decisive (Section VI-C). Readers are referred to Kairouz et al. [8] for a broad survey of open FL problems.

### B. Personalized Federated Learning

Personalization addresses non-IID data by giving each client model a private component. Representation–head splits such as FedRep [13] federate a shared feature extractor while each client keeps a local prediction head, typically trained with alternating body-freeze/head-tune phases; Ditto [14] instead regularizes a personal model toward the global one. The pattern has been imported into PHM largely as-is: GHDR-FL [15] federates shallow degradation features and attaches a client-unique superstructure for turbofan RUL, and client-personalized aggregation has been proposed for bearing RUL [18]. What is missing is an adversarial test of the pattern under *temporal* distribution shift: personalization is usually evaluated on static non-IID splits, where fitting the local distribution is unambiguously beneficial. Our results show that under degradation-stage drift the naive joint-trained variant of this pattern consistently *hurts* (Section VI-D), and we bound the claim carefully against the alternating-optimization variants.

### C. Federated Learning for Prognostics and RUL

Centralized deep RUL estimation on C-MAPSS is mature — recurrent [2], [3], convolutional [4], and hybrid [5] architectures define the accuracy landscape — and the federated line is growing: beyond GHDR-FL [15], network pruning has been used to shrink federated RUL models [16], collaborative RUL training has been demonstrated across simulated fleets [17], and joint degradation/failure-event modeling has been formulated federatively [19]. Across these works, communication cost is at most a secondary metric, drift is generally absent from the threat model, and component contributions are asserted rather than audited with seed-paired statistics. It is noticeable that none of the previous research couples a drift signal to both the communication schedule and the aggregation rule, nor validates its configuration on a held-out subset. Different from existing works, we present exactly this coupling and this audit.

### D. Concept Drift and Drift-Aware Federation

Sequential change detection is classical: the Page–Hinkley test [20] monitors a cumulative deviation statistic, and ADWIN [21], [22] maintains adaptive windows; Gama et al. [21] survey adaptation strategies. Two design choices distinguish our use. Detection runs on *prediction residuals* rather than raw inputs, so it flags genuine target drift (the model degrading) rather than benign covariate shift; and detection is *client-local*, because degradation regimes shift asynchronously across a fleet — a global detector would be both late and wrong for most clients. To our knowledge, using the resulting flag simultaneously as an upload permission override and an aggregation re-weighting signal has not been evaluated for federated prognostics.

**Positioning.** Table VIII (Section VI) situates our quantitative results against representative prior C-MAPSS studies; because federation construction, splits, and drift protocols differ across papers, our like-for-like evidence is the reproduced FedAvg/FedProx/local/centralized ladder run under an identical protocol, and the cross-paper table is provided for context only.

---

## III. Problem Formulation

Consider a federation of $K$ edge clients, where client $k$ holds a private stream of condition-monitoring windows $x \in \mathbb{R}^{L \times F}$ ($L$ cycles of $F$ standardized sensor and operating-setting channels) with RUL labels $y \in [0, R_{\max}]$ under the standard piecewise-linear cap. Three properties define the setting.

**Heterogeneity.** Local distributions differ: $P_k(x, y) \neq P_j(x, y)$ for $k \neq j$, induced by asset identity (fleet composition, wear state) or operating regime.

**Drift.** Each local distribution is non-stationary, $P_k^{(t)}(x, y) \neq P_k^{(t')}(x, y)$, as the asset traverses degradation stages; shifts occur asynchronously across clients.

**Communication and participation constraints.** In each round $t$, a fraction $C$ of clients is sampled, a fraction $\rho_s$ of those drops out (stragglers), and each upload of client $k$ costs $b_k^{(t)}$ bytes.

Given a model $f_\theta$ with loss $\ell$, the design goal is

$$\min_{\theta}\; \frac{1}{K} \sum_{k=1}^{K} \mathbb{E}_{(x,y) \sim P_k^{(t)}} \big[ \ell(f_\theta(x), y) \big] \quad \text{s.t.} \quad \sum_{t} \sum_{k} b_k^{(t)} \leq B, \tag{1}$$

where $B$ is the total uplink budget. We report the empirical Pareto point each method reaches — RMSE against total uplink megabytes — rather than fixing $B$ a priori, together with the fleet-fairness statistics defined in Section V-E. Stating the objective as accuracy *subject to* a byte budget, rather than as a single scalar, is what makes the compression and trigger components separately measurable.

---

## IV. Proposed Method: DGFed

### A. Overview

[Fig. 1: DGFed control loop. Left: client k — local training on its stream; Page–Hinkley detector on prediction residuals emits drift flag d_k; flag and relative delta-norm rule decide upload; error-feedback top-k + 8-bit compression. Right: server — decompression; adaptive divergence clipping; aggregation weighted by data size, staleness, and drift flag; broadcast. One signal (d_k) feeds both the upload decision and the aggregation weight, closing the loop.]

Each round proceeds as follows. The server broadcasts the shared parameters $\theta$ to a sampled client subset. Each participating client trains locally for $E$ epochs, evaluates its detector on fresh residuals, and then makes an *upload decision*: a client that is quiescent (small parameter delta) and not drifting stays silent. Clients that do upload send a compressed delta. The server decompresses, clips each delta adaptively, and aggregates with weights that discount staleness and boost freshly drifted clients. Fig. 1 summarizes the loop; Algorithm 1 gives the procedure. The design decision that Section VI-D justifies empirically: *all* parameters, including the prediction head, are federated. A client-local head is evaluated as a design axis (arm DGFed-P) and rejected by the audit.

### B. Residual-Based Local Drift Detection

Client $k$ maintains a Page–Hinkley (PH) statistic over the stream of absolute prediction residuals $r_i = |f_\theta(x_i) - y_i|$ computed on its held-out ordered tail after each local training phase. With forgetting factor $\alpha$, tolerance $\delta$, and threshold $\lambda$:

$$m_i = \alpha\, m_{i-1} + (1-\alpha)\, r_i, \tag{2}$$
$$g_i = \alpha\, g_{i-1} + (r_i - m_i - \delta), \qquad G_i = \min(G_{i-1}, g_i), \tag{3}$$

and a drift flag $d_k = 1$ is raised when $g_i - G_i > \lambda$, upon which the statistic resets. In (2)–(3), $m_i$ is the forgetting running mean of residuals and $g_i - G_i$ measures sustained upward deviation. Two choices matter. Detecting on residuals rather than inputs flags *target* drift — the model actually degrading — and ignores benign covariate wander. Keeping detection local matches the asynchronous nature of degradation: one asset enters a new wear regime while its peers remain stable. The threshold $\lambda$ is the only tuned detector parameter; Section V-C gives its calibration protocol and Section VI-E its cross-partition portability, which is a stated limitation.

### C. Event-Triggered Uploads

Let $\Delta_k = \theta_k^{\text{after}} - \theta$ be the local parameter delta and $H_k$ the running median of client $k$'s own past delta norms. The client skips its upload iff

$$d_k = 0 \;\wedge\; \lVert \Delta_k \rVert_2 < \gamma \cdot H_k, \tag{4}$$

with $\gamma = 0.3$; a client's first update is always sent. The rule is deliberately *relative*: an absolute threshold is either inert or destructive depending on model scale (our diagnostics confirmed an earlier absolute variant never fired at realistic delta norms), whereas (4) adapts to each client's own optimization dynamics. The drift flag overrides the trigger — a drifting client always speaks — which couples this component to Section IV-B and, as the audit shows, bounds how much bandwidth the trigger can save when drift is frequent.

### D. Error-Feedback Compression With Sensitivity-Weighted Budgets

Uploads are compressed in three steps. First, error feedback [11] adds the residual $e_k$ of previously discarded mass: $\tilde{\Delta}_k = \Delta_k + e_k$. Second, a global keep-budget of ratio $\kappa$ is allocated across layers proportionally to each layer's delta energy $\lVert \tilde{\Delta}_{k,l} \rVert_2$ — a cheap proxy for task sensitivity that concentrates bits where the update carries signal — and the top-$k_l$ coordinates per layer are retained. Third, retained values are quantized with an 8-bit affine quantizer (per-tensor scale and zero point). The feedback memory is then updated:

$$e_k \leftarrow \tilde{\Delta}_k - \mathcal{D}\big(\mathcal{C}(\tilde{\Delta}_k)\big), \tag{5}$$

where $\mathcal{C}$/$\mathcal{D}$ denote compression/decompression. Reported uplink bytes count retained values at 8 bits, 4-byte coordinate indices, and per-tensor quantizer constants; uncompressed baselines are charged 4 bytes per parameter. With $\kappa = 0.1$, the measured end-to-end reduction versus FedAvg is 8.0× (Section VI-A).

### E. Drift- and Staleness-Aware Aggregation With Adaptive Clipping

Let $a_k$ be the number of rounds since client $k$ last synchronized and $n_k$ its sample count. Each received delta is first clipped to a round-adaptive bound,

$$\hat{\Delta}_k = \Delta_k \cdot \min\!\Big(1,\; \frac{c \cdot \operatorname{med}_j \lVert \Delta_j \rVert_2}{\lVert \Delta_k \rVert_2}\Big), \tag{6}$$

with $c = 2$, protecting the shared model from stale or anomalous outliers while — unlike an absolute bound — never throttling healthy early-training dynamics. Aggregation weights combine three factors:

$$w_k = n_k \cdot \frac{\tau_0}{\tau_0 + a_k} \cdot \rho^{\,d_k}, \qquad \theta \leftarrow \theta + \sum_{k \in \mathcal{U}_t} \frac{w_k}{\sum_j w_j}\, \hat{\Delta}_k, \tag{7}$$

where $\tau_0 = 2$ discounts staleness, $\rho = 1.5$ up-weights a freshly drifted client's update as carrying new regime information, and $\mathcal{U}_t$ is the set of received uploads. When the staleness and drift factors are disabled, (7) reduces exactly to FedAvg's data-size weighting, which is how the plain-aggregation ablation arm is instantiated. This is the second consumer of the drift flag: the same signal that forces a drifting client to upload also amplifies how much that upload counts.

### F. Algorithm

**Algorithm 1 — DGFed (one round $t$)**

```
Input: shared params θ; clients K; participation C; straggler rate ρ_s
Output: updated θ
 1: S_t ← sample ⌈C·K⌉ clients; drop each with prob. ρ_s
 2: for each client k ∈ S_t in parallel:
 3:     load θ; train E local epochs on own stream            ▷ Sec. IV-A
 4:     d_k ← PH update on fresh residuals                    ▷ Eq. (2)–(3)
 5:     Δ_k ← θ_k − θ;  if d_k = 0 and ‖Δ_k‖ < γ·H_k: skip    ▷ Eq. (4)
 6:     upload C(Δ_k + e_k); update e_k                       ▷ Eq. (5)
 7: server: decompress; clip each Δ_k                         ▷ Eq. (6)
 8: server: θ ← θ + Σ_k (w_k/Σ_j w_j)·Δ̂_k                    ▷ Eq. (7)
```

Per-round client overhead beyond FedAvg is one forward pass over the held-out tail (drift check), an $O(|\theta|)$ top-k selection, and $O(|\theta|)$ feedback memory; the server adds one median computation per round. No second optimization loop, dual variables, or control state beyond $\{H_k, e_k, a_k\}$ is required, keeping the scheme deployable on constrained edge hardware.

### G. Personalization as an Audited Design Axis

The representation–head split — federating the feature extractor while each client keeps a private RUL head — is the standard personalization pattern in this literature [13], [15], [18]. Rather than adopting or dismissing it a priori, we instantiate it as arm **DGFed-P** (identical to DGFed except the head parameters never leave the client, trained jointly with the body each round) and subject it to the same paired-seed audit as every other component. Section VI-D reports the outcome — a consistent accuracy penalty — together with a three-way mechanism exclusion study, and bounds the finding: it concerns *naive joint-trained* local heads under stage drift, not alternating-optimization personalization such as FedRep's original procedure, which remains future work.

---

## V. Experimental Setup

### A. Dataset and Preprocessing

We use the NASA C-MAPSS turbofan degradation benchmark [1], the standard public run-to-failure corpus for RUL research. Two multi-operating-condition subsets are employed: **FD004** (249 training units, six operating conditions, two fault modes — the hardest subset and our *development* set) and **FD002** (six operating conditions, one fault mode — our *held-out confirmation* set; Section V-C). Each record carries three operating settings and 21 sensor channels. Near-constant sensors are removed by a variance threshold fit on training data only; remaining channels plus the three settings are z-score standardized with training-set statistics reused on all evaluation data. Inputs are sliding windows of $L = 30$ cycles; labels use the standard piecewise-linear RUL cap $R_{\max} = 125$ [2]. Operating regimes are recovered by k-means clustering of the three settings into six conditions, matching the documented regime structure. The official per-unit test split (last window per test unit against the ground-truth RUL file) is additionally reported for the centralized baseline to anchor our model family against the literature.

### B. Federation Construction and Drift Injection

**Partitions.** Two client constructions probe different heterogeneity regimes. The **unit-fleet partition** assigns disjoint groups of engine units to $K = 12$ clients — the natural industrial setting of separate fleets, with mild non-IID induced by unit wear diversity and FD004's two fault modes. The **operating-regime partition** assigns each *window* to the client matching its operating condition at the window's final cycle, yielding $K = 6$ clients with severe feature-skew non-IID; here a client models an operating site or regime rather than a machine. We note for reproducibility that a third, seemingly natural construction — assigning each *unit* to its dominant operating condition — is degenerate on FD004 and FD002: because conditions vary cycle-to-cycle and every unit visits all six regimes with near-identical time shares, all units share one dominant regime and the federation collapses to a single client. This is why regime heterogeneity must be constructed at window level, and our pipeline hard-fails any federated run that forms fewer than two clients.

**Drift injection.** Real degradation drift on C-MAPSS is entangled with unit identity, so we inject controlled stage drift: each client's windows are sorted by descending RUL (healthy → degraded) and split into $S = 3$ equal blocks whose order is permuted per client with a seeded RNG, producing abrupt distribution shifts at block boundaries that arrive asynchronously across clients. Each client's stream is then split *in order* into an 80% training prefix and a 20% held-out tail; federated accuracy is evaluated on these tails. A consequence used by the mechanism study of Section VI-D: a client's tail contains RUL bands absent from its own prefix, operationalizing "unseen degradation stages." We state the assumption–limitation–mitigation triad plainly: injected block drift is a controlled proxy, it may differ in smoothness from natural wear progressions, and validating against naturally drifting streams (e.g., FEMTO bearings) is planned future work.

### C. Protocol: Development, Calibration, and Held-Out Confirmation

All design decisions and all hyperparameter selection were performed on FD004 exclusively. The single tuned detector parameter, $\lambda$, was calibrated by a sweep over $\{250, 500, 1000, 2500, 5000\}$ using 50-round single-seed runs on the FD004 unit partition, selecting the smallest value whose drift-fire rate lands in a 3–8% target band; only $\lambda = 5000$ qualified (fire rates 22.2%, 20.3%, 14.9%, 9.5%, 5.7% respectively). All remaining parameters are fixed defaults with stated rationale (Table I); results were not tuned against them. The complete frozen configuration was then applied to FD002 — both partitions — with *no retuning of any kind*; FD002 fire rates are reported as observed. Main comparisons use 3 seeds (0–2); an 8-seed extension supports the divergence analysis of Section VI-E. Ablation variants share seeds with the base configuration, enabling the paired-seed deltas of Section VI-C.

### D. Baselines and Variants

The comparison ladder isolates each question. **Centralized** (pooled training, 30 epochs) upper-bounds accuracy with no privacy or bandwidth constraint; **local-only** (per-client training, 30 epochs) lower-bounds it under isolation; **FedAvg** [6] and **FedProx** [7] ($\mu = 0.01$, the authors' commonly used small value, fixed not tuned) are the standard-FL baselines, sharing the full model uncompressed every round with data-size aggregation. **DGFed** is the proposed method; **DGFed-P** is the personalized-head arm (Section IV-G). Component ablations remove exactly one mechanism from DGFed: the drift signal, the event trigger, the drift/staleness aggregation (reducing (7) to FedAvg weighting), or compression. All methods share the identical backbone — Conv1d(F→32, k=5) → Conv1d(32, k=3) → LSTM(64) → FC(64) feature extractor with an FC(32)→1 regression head, dropout 0.2 — optimizer, seeds, and evaluation code.

### E. Metrics

**RMSE** on the pooled client tails is the primary error metric. The **asymmetric C-MAPSS score** [1], $s = \sum_i \phi(d_i)$ with $d_i = \hat{y}_i - y_i$, $\phi(d) = e^{-d/13} - 1$ for $d < 0$ and $e^{d/10} - 1$ otherwise, penalizes late predictions more heavily, matching maintenance cost asymmetry; being exponential, it is meaningful only once RMSE is in a converged range and we interpret it accordingly. **Uplink volume** (MB) is the total measured upload cost under the byte accounting of Section IV-D. Fleet fairness is captured by the **per-client RMSE variance** and the **worst-client RMSE**, so a good average cannot hide an abandoned client. **Retention bins** split each tail into five sequential segments and report per-bin RMSE, exposing erosion under drift. **Seen/unseen strata** partition tail windows by whether their RUL value occurs in the client's own training prefix. Lower is better for all metrics except none.

### F. Implementation and Reproducibility

**TABLE I — Hyperparameters (fixed unless noted)**

| Group | Parameter | Value | Rationale |
|---|---|---|---|
| Data | window $L$ / cap $R_{\max}$ / drift blocks $S$ | 30 / 125 / 3 | standard [2] / standard / controlled shifts |
| Model | conv filters / LSTM / latent / head / dropout | 32 / 64 / 64 / 32 / 0.2 | compact edge-scale backbone |
| Training | optimizer / LR / batch / local epochs $E$ / rounds | Adam / 1e-3 / 128 / 1 / 200 | common FL defaults |
| Federation | participation $C$ / straggler $\rho_s$ / clients $K$ | 0.6 / 0.1 / 12 (unit), 6 (regime) | partial, unreliable participation |
| Detector | $\delta$ / $\alpha$ / $\lambda$ | 0.005 / 0.9999 / **5000 (calibrated)** | Sec. V-C sweep |
| Trigger | $\gamma$ | 0.3 | relative rule, Sec. IV-C |
| Compression | keep ratio $\kappa$ / quantizer | 0.10 / 8-bit affine | Sec. IV-D |
| Aggregation | $\tau_0$ / $\rho$ / clip $c$ | 2 / 1.5 / 2×round-median | Sec. IV-E |
| Baselines | FedProx $\mu$ / central & local epochs | 0.01 / 30 | fixed, stated |

Experiments ran in PyTorch on Apple-silicon GPU (MPS backend) after a CPU-parity check (5-round RMSE within ~1.4%, no NaNs); repeated runs on the same machine reproduced per-seed RMSEs exactly, which the counterfactual study of Section VI-D exploits. The C-MAPSS data is publicly available from the NASA Prognostics Center of Excellence. Code, the federation-construction pipeline, all result JSONs, and a manifest pinning the 37 artifact files behind every reported table via content hashes accompany the paper [TODO: repository URL / supplementary link].

---

## VI. Results and Analysis

### A. Main Comparison on the Development Set (FD004)

**TABLE II — FD004 main results (3 seeds, mean ± std; MB = total uplink; Var/Worst = per-client fairness)**

*Unit-fleet partition (12 clients):*

| Method | RMSE | Score | MB | Var | Worst |
|---|---|---|---|---|---|
| Centralized (upper bd.) | 20.71 ± 1.46 | 160K ± 47K | n/a | 26.5 | 28.3 |
| Local-only (lower bd.) | 36.61 | 4.68M | 0 | 226.6 | 80.6 |
| FedAvg | 22.35 ± 0.99 | 220K ± 104K | 193.5 | 45.5 | 31.5 |
| FedProx | 23.09 ± 0.67 | 388K ± 260K | 193.5 | 44.0 | 31.6 |
| **DGFed (ours)** | **21.78 ± 1.16** | [TODO: results/FD004_calibrated ablation_unit.json, no_personal_head score] | **24.2** | 33.6 | 30.6 |
| DGFed-P (personal head) | 24.11 ± 0.66 | [TODO: same file, full arm] | 22.8 | 29.8 | 31.9 |

*Operating-regime partition (6 clients):*

| Method | RMSE | Score | MB | Var | Worst |
|---|---|---|---|---|---|
| Centralized | 20.93 ± 2.08 | 94K ± 13K | n/a | 35.1 | 25.4 |
| Local-only | 23.36 | 129K | 0 | 5.8 | 25.2 |
| FedAvg | 20.12 ± 2.63 | 88K ± 31K | 84.0 | 46.0 | 24.7 |
| FedProx | 20.46 ± 2.13 | 104K ± 22K | 84.0 | 56.8 | 24.8 |
| **DGFed (ours)** | 21.02 ± 1.16 | [TODO: ablation_regime.json] | **10.5** | 51.4 | 26.0 |
| DGFed-P | 22.00 ± 0.96 | [TODO: same] | 9.9 | 35.5 | 26.4 |

Three observations. First, federation is decisively worth having where clients are weak: on the unit partition, local-only training leaves the worst client at RMSE 80.6, which every federated method roughly halves — the fairness variance drops from 226.6 to ≤ 51. Second, DGFed reaches FedAvg-level accuracy at 8.0× lower uplink on both partitions (24.2 vs. 193.5 MB; 10.5 vs. 84.0 MB); on the unit partition its mean RMSE is nominally *better* than FedAvg's (21.78 vs. 22.35), though within seed noise, and on the regime partition it trails by 0.9 RMSE, also within noise. Third, the regime partition weakens the case for federation itself: six large single-regime clients make local-only competitive (23.36), and FedAvg slightly *outperforms* the centralized model (20.12 vs. 20.93) — a pattern that recurs on FD002 and is discussed in Section VII. [Fig. 2: communication–accuracy plane; x = total uplink MB (log), y = RMSE; both partitions; DGFed sits far left at FedAvg-level height.]

### B. Held-Out Confirmation (FD002, frozen configuration)

**TABLE III — FD002 held-out results (3 seeds; no retuning)**

*Unit partition (12 clients):*

| Method | RMSE | Score | MB | Var | Worst |
|---|---|---|---|---|---|
| Centralized | 19.83 ± 2.03 | 99K ± 34K | n/a | 50.6 | 29.2 |
| Local-only | 39.04 | 4.31M | 0 | 251.9 | 80.6 |
| FedAvg | 20.24 ± 2.20 | 104K ± 30K | 193.5 | 63.7 | 29.2 |
| FedProx | 21.33 ± 1.00 | 119K ± 12K | 193.5 | 53.6 | 29.9 |
| **DGFed (ours)** | 23.33 ± 2.40 | 298K ± 149K | **24.2** | 43.3 | 31.4 |

*Regime partition (6 clients):*

| Method | RMSE | Score | MB | Var | Worst |
|---|---|---|---|---|---|
| Centralized | 23.76 ± 4.11 | 150K ± 63K | n/a | 28.8 | 28.9 |
| Local-only | 30.06 | 232K | 0 | 1.8 | 31.7 |
| FedAvg | 20.46 ± 3.92 | 100K ± 50K | 84.0 | 44.6 | 24.2 |
| FedProx | 20.64 ± 4.09 | 107K ± 62K | 84.0 | 50.4 | 25.0 |
| **DGFed (ours)** | 21.21 ± 3.31 | 107K ± 43K | **10.5** | 45.7 | 25.4 |

The frozen configuration transfers. The qualitative structure replicates — federation rescues weak clients (unit local-only 39.04 → 23.33), the 8× uplink reduction is identical by construction, and DGFed lands at FedAvg level on the regime partition (21.21 vs. 20.46, well within the large shared seed spread). The one place the picture weakens, which we report rather than smooth over: on the FD002 unit partition DGFed trails FedAvg by 3.1 RMSE (23.33 ± 2.40 vs. 20.24 ± 2.20) — overlapping ± std intervals at $n = 3$, and driven largely by one weak seed (per-seed retention in the artifacts), but a wider gap than anywhere on FD004. Detector activity also shifts as predicted for a threshold calibrated on another subset: fire rates 6.7% (unit) and 14.3% (regime) against FD004's 7.9%/19.0% — conservative in this instance, but direction is not guaranteed, and Section VIII lists threshold portability as a limitation. Diagnostics: skip 0.37%/0.12%, clip 1.06%/0.18%; seen/unseen strata 18.29 ± 0.97 / 24.96 ± 2.20 (unit) and 12.83 ± 0.96 / 22.99 ± 3.67 (regime), matching FD004's shape.

### C. Component Audit: Paired-Seed Ablation With Activity Diagnostics

Ablations use the proposed (shared-head) configuration as base, remove one component per arm, and share seeds with the base, so each arm yields three *paired* deltas per partition. Table IV reports both the marginal statistics and the paired evidence; because $n = 3$ underpowers formal tests, we report paired mean ± std and sign consistency and interpret conservatively.

**TABLE IV — FD004 rebased ablation (3 seeds) with paired-seed deltas (Δ = arm − DGFed; positive = removal hurts)**

*Unit partition:*

| Arm | RMSE | MB | Δ paired | Sign |
|---|---|---|---|---|
| **DGFed (base)** | 21.78 ± 1.16 | 24.2 | — | — |
| − drift signal | 22.11 ± 1.38 | 24.1 | +0.33 ± 0.53 | 2/3 + |
| − event trigger | 22.36 ± 1.27 | 24.2 | +0.58 ± 0.63 | 2/3 + |
| − drift/stale aggregation | 22.63 ± 1.74 | 24.2 | +0.85 ± 0.59 | **3/3 +** |
| − compression | 21.15 ± 1.95 | 193.0 | −0.63 ± 1.92 | 1/3 + |
| + personal head (DGFed-P) | 24.11 ± 0.66 | 22.8 | +2.33 ± 0.51 | **3/3 +** |

*Regime partition:*

| Arm | RMSE | MB | Δ paired | Sign |
|---|---|---|---|---|
| **DGFed (base)** | 21.02 ± 1.16 | 10.5 | — | — |
| − drift signal | 21.48 ± 0.71 | 10.5 | +0.46 ± 0.50 | 2/3 + |
| − event trigger | 21.00 ± 1.19 | 10.5 | −0.02 ± 0.02 | 0/3 + |
| − drift/stale aggregation | 21.67 ± 0.16 | 10.5 | +0.66 ± 1.23 | 2/3 + |
| − compression | 19.68 ± 2.32 | 83.6 | −1.34 ± 1.39 | 1/3 + |
| + personal head (DGFed-P) | 22.00 ± 0.96 | 9.9 | +0.98 ± 0.63 | **3/3 +** |

Activity diagnostics for the base configuration confirm every retained mechanism actually operates at the reported operating point: drift fires on 8.1%/18.9% of client-rounds (unit/regime), the trigger skips 0.2%/0.2% of uploads, and the clip engages on 0.1%/1.0% with mean scale ≈ 0.93–0.94 when active. Interpretation, component by component. **Drift/staleness aggregation** is the most consistent contributor: its removal costs +0.85/+0.66 RMSE with the best sign pattern (5/6 paired seeds positive) — the single clearest algorithmic gain of the drift-governed loop. **The drift signal** feeding it is directionally positive on both partitions (+0.33/+0.46, 4/6) but within noise at $n = 3$. **The event trigger** deserves the bluntest sentence in the paper: it saves ≤ 0.7% of bytes (top-k compression removes the traffic the trigger would otherwise skip, and drifting clients may never skip), it is a literal no-op on the regime partition (Δ = −0.02 ± 0.02), and an 8-seed extension found no stability effect either (Section VI-E). We retain it because it is free and directionally positive on unit, and we claim nothing more for it. **Compression** is the honest trade the framework is built around: 8× fewer bytes for a within-noise 0.6 (unit) to a real 1.3 (regime) RMSE cost. [Fig. 3: per-seed paired-delta strip plot across arms and partitions; Fig. 4: retention curves (5 tail bins) for base vs. selected arms, both partitions — flat-to-mild on unit, consistently rising on regime.]

### D. The Personalization Negative Result and Mechanism Exclusion

The single most consistent effect in Table IV is not a component gain but a penalty: the client-local head hurts in all six paired seeds (+2.33 ± 0.51 unit; +0.98 ± 0.63 regime), a pattern that held across every configuration generation of this study. Because the representation–head split is the default personalization pattern in federated PHM [13], [15], [18], we dissected the mechanism with three targeted studies rather than leaving an unexplained anomaly.

**TABLE V — Seen/unseen RUL strata (RMSE, 3 seeds)**

| Setting / arm | Seen | Unseen | Gap |
|---|---|---|---|
| Unit, DGFed-P | 21.77 ± 3.13 | 24.76 ± 1.70 | +2.98 |
| Unit, DGFed | 16.46 ± 1.29 | 23.77 ± 0.74 | +7.31 |
| Regime, DGFed-P | 12.59 ± 0.42 | 24.49 ± 0.54 | +11.89 |
| Regime, DGFed | 10.09 ± 2.11 | 23.60 ± 1.67 | +13.51 |

**Hypothesis M1 — selective failure on unseen degradation stages: rejected.** If local heads overfit the stages a client has seen, DGFed-P's seen→unseen gap should exceed DGFed's. Table V shows the opposite: DGFed-P's gap is *smaller*, because it is worse on *both* strata — including a 5.3-RMSE deficit on the client's own seen distribution (21.77 vs. 16.46, unit). The personalized head does not even exploit the local data it was meant to fit.

**TABLE VI — Counterfactual-body evaluation of DGFed-P (3 seeds)**

| Setting | Global body + local head | Own final local body + local head |
|---|---|---|
| Unit | **24.11 ± 0.66** (seen 21.77) | 27.91 ± 2.27 (seen 22.52) |
| Regime | **22.00 ± 0.96** (seen 12.59) | 23.92 ± 0.78 (seen 15.49) |

**Hypothesis M2 — head–body mismatch under aggregation: rejected.** If each head were mis-paired with a global body it was not trained against, pairing it with the client's *own* final local body should help. Exploiting on-machine run determinism, we retrained the arm identically (reproducing its per-seed RMSEs exactly) while preserving each client's final local body, then evaluated both pairings. Own-body pairing is *worse* in all six runs (Table VI) — heads benefit from the aggregated representation.

**Hypothesis M3 — client data scale: unsupported.** Regressing each client's head penalty (DGFed-P minus DGFed per-client RMSE) on its training-window count yields no meaningful correlation on the unit partition (Pearson −0.09, Spearman +0.06, $n = 12$; penalty positive for all 12 clients, range +0.14 to +6.70) and nothing interpretable on regime ($n = 6$, dominated by one large client). A stated caveat bounds this test: client sizes span a narrow range (≈3.1–4.0k windows on unit), leaving little leverage to detect a size effect; within that range the penalty is roughly uniform.

What survives is a deliberately modest conclusion: under these conditions a jointly trained local head is *uniformly* weaker than a federated head — across clients, RUL strata, and body pairings — rather than selectively fragile. The claim boundary matters: this indicts the naive joint-training instantiation common in applied FL-PHM, not personalization per se; alternating-optimization schemes [13] with explicit head-fitting phases may behave differently and are the direct follow-up. For practitioners the actionable reading is that on C-MAPSS-scale industrial clients, head personalization should be treated as a hypothesis to test, not a default to adopt.

### E. Robustness, Calibration Transfer, and Hypothesis Verdicts

An 8-seed extension on the unit partition (DGFed and its no-trigger arm) found zero divergent runs in 16 (all RMSE ≤ 35, no delta-norm collapse), retiring an earlier single-seed instability observed under the over-firing pre-calibration detector and denying the trigger a stability claim. The λ sweep of Section V-C doubles as a sensitivity analysis: fire rate falls monotonically from 22.2% (λ=250) to 5.7% (λ=5000), and only the calibrated value lands in the target band; on the regime partition the same λ fires at ~19%, so the threshold is partition-calibrated, not universal — a residual-scale normalization is the identified fix. [Fig. 5: λ vs. fire rate, both partitions.]

**Verdicts.** **H1 accepted with one stated boundary:** DGFed matches FedAvg within seed noise at 8.0× lower uplink in three of four dataset×partition settings; on FD002-unit it trails by 3.1 RMSE with overlapping ± std. **H2 accepted:** contributions are non-uniform — drift/staleness aggregation is the most consistent gain (5/6), the trigger is null-to-marginal, compression is a quantified trade. **H3 rejected** in its personalization-helps form, in all six paired seeds, with three mechanisms excluded.

**TABLE VII — Context: representative C-MAPSS studies (protocols differ; not like-for-like — see Sec. II)**

| Ref | Year | Approach | Setting | Headline result |
|---|---|---|---|---|
| [3] | 2017 | LSTM (centralized) | FD001–FD004 official test | RMSE ≈ 16–28 across subsets |
| [5] | 2022 | Preprocessing + deep LSTM (centralized) | FD001–FD004 official test | improved RMSE/score vs. prior LSTM |
| [15] | 2023 | FL, shared shallow features + personal superstructure | C-MAPSS federation (own protocol) | personalized FL feasibility |
| [17] | 2024 | FL collaborative RUL | simulated fleets | collaborative ≈ centralized feasibility |
| **Ours** | — | Drift-governed FL, shared head, compressed | FD004/FD002, 2 partitions, injected drift, client tails | FedAvg-level RMSE at 8.0× lower uplink; audited components |

Cross-paper numbers are not comparable (different splits, labels, federations); our centralized baseline's official-test anchor (FD004: 23.16 RMSE / 7468 score; FD002: 18.13 / 2468) places the shared backbone in the credible range of the deep-RUL literature [3], [5], which is its only role here.

---

## VII. Discussion

**Where the drift-governed loop pays, and where it does not.** The audit's clearest lesson is architectural: of the two consumers of the drift signal, the *aggregation-side* consumer earns its place (5/6 paired seeds, both partitions) while the *communication-side* consumer does not — top-k compression already removes the traffic an event trigger would suppress, and the override that forces drifting clients to upload caps the trigger's reach precisely when drift is common. For designers this inverts a common intuition: under aggressive update compression, the marginal value of transmission gating is small, and drift signals are better spent re-weighting trust in what arrives than deciding whether it arrives.

**The personalization result in context.** That a client-local head consistently hurts will read as surprising against the personalized-FL literature [13]–[15], [18], and the mechanism study is what makes the result useful rather than merely contrarian: the penalty is uniform across clients, strata, and body pairings, which is the signature of an under-trained component, not of a distribution-fit trade-off. Two boundary conditions frame generality. Our clients are C-MAPSS-scale (thousands of windows) with a compact backbone; larger local datasets or higher-capacity heads may cross the threshold where local fitting wins. And the finding targets *joint* head training inside the federated round; alternating schemes that freeze the body and fit the head to convergence [13] are structurally protected from the failure mode observed here and remain untested in this setting.

**The regime-partition inversion.** On both datasets' regime partitions, FedAvg slightly outperforms the pooled centralized model (FD004: 20.12 vs. 20.93; FD002: 20.46 vs. 23.76). We flag this as an observation with a plausible reading — with six large, internally homogeneous shards, partial participation plus averaging acts as an implicit regularizer that pooled training lacks — and resist a stronger claim; at $n = 3$ with ±2–4 seed spreads, the inversion is directional, not established. It does, however, reinforce a practical point: regime-partitioned federations are where local-only training is most competitive and federation's marginal value is thinnest, so fleet topology should inform whether FL is worth its coordination cost.

**Deployment path.** The simulation makes three simplifications a deployment would revisit: synchronous-ish rounds with a straggler model rather than true asynchrony, injected rather than natural drift, and byte accounting that excludes protocol overhead. None touches the algorithm: the client and server procedures map directly onto standard FL frameworks' client/strategy abstractions, and the control state per client is three scalars plus the feedback memory.

## VIII. Threats to Validity

**Internal.** Fixed hyperparameters (Table I) were not adversarially tuned per method; FedProx's μ in particular is a stated default, so its gap to FedAvg should not be over-read. The MPS backend introduced ~1.4% cross-backend numeric deviation versus CPU in a parity check; on-machine determinism was verified and exploited, but cross-hardware bit-reproducibility is not claimed. The λ calibration used single-seed 50-round probes; the 3–8% target band, while pre-registered before the final suites, is itself a design choice.

**External.** Evidence comes from one benchmark family (C-MAPSS FD004/FD002) — simulated turbofans — under injected block drift; natural degradation drift, other asset classes (bearings, pumps), and larger federations are untested. The two partitions probe fleet-style and regime-style heterogeneity but not label-skew or quantity-skew extremes. Threshold portability is a demonstrated limitation: λ calibrated to a 5.7% fire rate on FD004-unit fires at ~19% on regime partitions.

**Construct.** Injected stage drift is a proxy whose abruptness may overstate natural wear transitions. The seen/unseen operationalization (RUL-value coverage in the client's own prefix) captures stage novelty but not sensor-pattern novelty. Uplink bytes measure payload only; per-message protocol overhead would slightly compress the 8× ratio in practice.

**Conclusion validity.** Main comparisons use 3 seeds; we therefore lean on paired-seed deltas and sign consistency rather than formal tests, bold no per-cell "wins," and state explicitly which effects sit within noise (drift signal, trigger, unit-partition compression cost). The divergence analysis's 0/16 outcome bounds, but does not exclude, rare instabilities. Exceptions to the headline are listed, not smoothed: DGFed trails FedAvg by 3.1 RMSE on FD002-unit, and compression's accuracy cost on regime (−1.34 paired) is real.

## IX. Conclusion

This paper asked whether the three coupled obstacles to federated RUL estimation at the industrial edge — heterogeneity, drift, and communication constraints — are better served by one coordinating signal than by three isolated mechanisms, and answered with a framework and an audit. DGFed's drift-governed loop delivers FedAvg-level accuracy at 8.0× lower uplink on C-MAPSS FD004 (21.78 ± 1.16 RMSE at 24.2 MB vs. 22.35 ± 0.99 at 193.5 MB), transfers to held-out FD002 without retuning, and decomposes cleanly under paired-seed analysis: drift-aware aggregation is the component that earns its place, the event trigger is retained only because it is free, and — against the field's default — client-local prediction heads degrade accuracy in every paired seed, a result we dissected until three candidate mechanisms were excluded. Future work follows directly: replacing the partition-calibrated detector threshold with residual-normalized detection; testing alternating-optimization personalization where joint training failed; and confronting the framework with naturally drifting run-to-failure streams and a real distributed deployment. More broadly, we hope the audit protocol — paired seeds, activity diagnostics, held-out configuration transfer, pinned artifacts — travels beyond this paper, because in federated PHM the scarce resource is not another component but calibrated evidence about the ones we have.

---

## References

[1] A. Saxena, K. Goebel, D. Simon, and N. Eklund, "Damage propagation modeling for aircraft engine run-to-failure simulation," in *Proc. Int. Conf. Prognostics Health Manage. (PHM)*, Denver, CO, USA, 2008, pp. 1–9.

[2] F. O. Heimes, "Recurrent neural networks for remaining useful life estimation," in *Proc. Int. Conf. Prognostics Health Manage. (PHM)*, Denver, CO, USA, 2008, pp. 1–6.

[3] S. Zheng, K. Ristovski, A. Farahat, and C. Gupta, "Long short-term memory network for remaining useful life estimation," in *Proc. IEEE Int. Conf. Prognostics Health Manage. (ICPHM)*, Dallas, TX, USA, 2017, pp. 88–95.

[4] X. Li, Q. Ding, and J.-Q. Sun, "Remaining useful life estimation in prognostics using deep convolution neural networks," *Rel. Eng. Syst. Saf.*, vol. 172, pp. 1–11, Apr. 2018.

[5] O. Asif, S. A. Haider, S. R. Naqvi, J. F. W. Zaki, K.-S. Kwak, and S. M. R. Islam, "A deep learning model for remaining useful life prediction of aircraft turbofan engine on C-MAPSS dataset," *IEEE Access*, vol. 10, pp. 95425–95440, 2022.

[6] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. Agüera y Arcas, "Communication-efficient learning of deep networks from decentralized data," in *Proc. 20th Int. Conf. Artif. Intell. Statist. (AISTATS)*, 2017, pp. 1273–1282.

[7] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith, "Federated optimization in heterogeneous networks," in *Proc. Mach. Learn. Syst. (MLSys)*, vol. 2, 2020, pp. 429–450.

[8] P. Kairouz et al., "Advances and open problems in federated learning," *Found. Trends Mach. Learn.*, vol. 14, no. 1–2, pp. 1–210, 2021.

[9] D. Alistarh, D. Grubic, J. Li, R. Tomioka, and M. Vojnovic, "QSGD: Communication-efficient SGD via gradient quantization and encoding," in *Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2017, pp. 1709–1720.

[10] A. F. Aji and K. Heafield, "Sparse communication for distributed gradient descent," in *Proc. Conf. Empirical Methods Natural Lang. Process. (EMNLP)*, 2017, pp. 440–445.

[11] S. P. Karimireddy, Q. Rebjock, S. U. Stich, and M. Jaggi, "Error feedback fixes SignSGD and other gradient compression schemes," in *Proc. 36th Int. Conf. Mach. Learn. (ICML)*, 2019, pp. 3252–3261.

[12] T. Chen, G. Giannakis, T. Sun, and W. Yin, "LAG: Lazily aggregated gradient for communication-efficient distributed learning," in *Proc. Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2018, pp. 5050–5060.

[13] L. Collins, H. Hassani, A. Mokhtari, and S. Shakkottai, "Exploiting shared representations for personalized federated learning," in *Proc. 38th Int. Conf. Mach. Learn. (ICML)*, 2021, pp. 2089–2099.

[14] T. Li, S. Hu, A. Beirami, and V. Smith, "Ditto: Fair and robust federated learning through personalization," in *Proc. 38th Int. Conf. Mach. Learn. (ICML)*, 2021, pp. 6357–6368.

[15] X. Chen, H. Wang, S. Lu, J. Xu, and R. Yan, "Remaining useful life prediction of turbofan engine using global health degradation representation in federated learning," *Rel. Eng. Syst. Saf.*, vol. 239, Art. no. 109511, Nov. 2023.

[16] X. Chen, X. Chen, H. Wang, S. Lu, and R. Yan, "Federated learning with network pruning and rebirth for remaining useful life prediction of engineering systems," *Manuf. Lett.*, vol. 35, pp. 965–972, 2023.

[17] W. Söderkvist Vermelin, M. Mishra, M. P. Eng, D. Andersson, and K. Kyprianidis, "Collaborative training of data-driven remaining useful life prediction models using federated learning," *Int. J. Prognostics Health Manage.*, vol. 15, no. 2, 2024.

[18] X. Chen, S. Lu, H. Wang, and R. Yan, "Bearing remaining useful life prediction using client selection and personalized aggregation enhancement in federated learning," *IEEE Internet Things J.*, 2024 [TODO: volume/issue/pages — verify on IEEE Xplore].

[19] C. Jeong, X. Yue, and S. Chung, "Fed-Joint: Joint modeling of nonlinear degradation signals and failure events for remaining useful life prediction using federated learning," arXiv preprint arXiv:2503.13404, 2025.

[20] E. S. Page, "Continuous inspection schemes," *Biometrika*, vol. 41, no. 1/2, pp. 100–115, 1954.

[21] J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy, and A. Bouchachia, "A survey on concept drift adaptation," *ACM Comput. Surv.*, vol. 46, no. 4, pp. 1–37, 2014.

[22] A. Bifet and R. Gavaldà, "Learning from time-changing data with adaptive windowing," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2007, pp. 443–448.

[TODO — references pass before submission: expand to 30+ per venue norms with 2024–2026 FL-PHM and drift-aware-FL additions; verify [18] bibliographic details; add DOIs throughout; renumber to order of first appearance after final edits.]
