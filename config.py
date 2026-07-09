"""Central experiment configuration.

All hyperparameters live here so experiments are reproducible from a single
object. `main.py` overrides fields from the command line.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Config:
    # ---- data ----
    data_root: str = "./datasets/CMAPSS"
    subset: str = "FD004"          # FD001..FD004
    window: int = 30               # sliding-window length (cycles)
    rul_cap: int = 125             # piecewise-linear RUL clip
    n_conditions: int = 6          # operating regimes to cluster into (multi-condition subsets)
    partition: str = "condition"   # 'condition' | 'unit'  -> how clients are formed
    max_clients: int = 12          # cap number of simulated clients
    inject_drift: bool = True      # order local samples to create regime shifts (drift)
    drift_segments: int = 3        # number of stationary segments per client stream

    # ---- model ----
    n_body_filters: int = 32
    lstm_hidden: int = 64
    latent_dim: int = 64
    head_hidden: int = 32
    dropout: float = 0.2

    # ---- federated core ----
    method: str = "dgfed"          # dgfed | fedavg | fedprox | local | central
    rounds: int = 200
    clients_per_round: float = 0.6 # fraction sampled each round
    local_epochs: int = 1
    batch_size: int = 128
    lr: float = 1e-3
    fedprox_mu: float = 0.01
    central_epochs: int = 30       # epochs for central / local-only baselines

    # personalization (rep-head split): keep head params local
    personalize_head: bool = True

    # ---- drift detection (Page-Hinkley on residual stream) ----
    use_drift_detector: bool = True
    ph_delta: float = 0.005        # tolerance
    ph_lambda: float = 5000.0      # detection threshold (calibrated: ~5.7% fire rate on FD004/unit; 50.0 fired on ~42% of client-rounds)
    ph_alpha: float = 0.9999       # forgetting factor

    # ---- event-triggered communication ----
    event_trigger: bool = True
    trigger_alpha: float = 0.3     # skip upload if ||body delta|| < alpha * running median of the client's own past delta norms AND not drifting (first upload always sends)

    # ---- compression (error-feedback top-k + optional quantization) ----
    compress: bool = True
    topk_ratio: float = 0.1        # keep top 10% of body-delta entries by magnitude
    quant_bits: Optional[int] = 8  # None disables quantization; else bits per kept value
    sensitivity_weighting: bool = True  # allocate k per layer by RUL-sensitivity proxy

    # ---- staleness / drift-aware aggregation ----
    staleness_aware: bool = True
    drift_aware_agg: bool = True
    stale_tau0: float = 2.0        # staleness discount:  w *= tau0/(tau0 + age)
    drift_boost: float = 1.5       # up-weight a freshly-drifted client's update
    clip_factor: float = 2.0       # clip body-delta L2 norm to clip_factor * median(current round's delta norms)
    straggler_rate: float = 0.1    # fraction of sampled clients that drop each round

    # ---- misc ----
    run_tag: str = ""              # optional label distinguishing runs (e.g. ablation variant) in diagnostics filenames
    seed: int = 0
    device: str = "cuda"           # falls back to cpu automatically if unavailable
    results_dir: str = "./results"

    def to_dict(self):
        return asdict(self)
