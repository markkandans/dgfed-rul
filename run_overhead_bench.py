"""Client-side overhead microbenchmark: proposed vs FedAvg, CPU.

20 rounds on FD004-unit. Wall-clock per client-round split into
local training / drift check / compression, measured by monkeypatched
timing wrappers around the frozen federated/ code (no source changes).
"""
import json
import time

from config import Config
from data.cmapss import load_cmapss
from data.partition import make_clients
from federated.client import Client
from federated.compression import Compressor
from federated.server import Server
from main import set_seed, apply_method
import torch

TIMES = {"local_update": [], "drift": [], "compress": []}

_orig_update = Client.local_update
_orig_drift = Client._check_drift
_orig_compress = Compressor.compress


def timed_update(self, *a, **k):
    t0 = time.perf_counter()
    out = _orig_update(self, *a, **k)
    TIMES["local_update"].append(time.perf_counter() - t0)
    return out


def timed_drift(self, *a, **k):
    t0 = time.perf_counter()
    out = _orig_drift(self, *a, **k)
    TIMES["drift"].append(time.perf_counter() - t0)
    return out


def timed_compress(self, *a, **k):
    t0 = time.perf_counter()
    out = _orig_compress(self, *a, **k)
    TIMES["compress"].append(time.perf_counter() - t0)
    return out


Client.local_update = timed_update
Client._check_drift = timed_drift
Compressor.compress = timed_compress


def bench(method):
    for v in TIMES.values():
        v.clear()
    cfg = Config(method="dgfed" if method == "proposed" else "fedavg",
                 subset="FD004", rounds=20, seed=0, run_tag=f"bench_{method}")
    cfg.partition = "unit"
    cfg.device = "cpu"
    if method == "proposed":
        cfg.personalize_head = False
    apply_method(cfg)
    set_seed(cfg.seed)
    device = torch.device("cpu")
    bundle = load_cmapss(cfg)
    raw = make_clients(bundle, cfg)
    clients = [Client(c["id"], c, cfg, bundle["n_features"], device) for c in raw]
    server = Server(clients, cfg, bundle["n_features"], device)
    t0 = time.perf_counter()
    server.train(evaluator=None)
    wall = time.perf_counter() - t0
    n = len(TIMES["local_update"])
    total = sum(TIMES["local_update"]) / n
    drift = sum(TIMES["drift"]) / max(1, len(TIMES["drift"]))
    comp = sum(TIMES["compress"]) / max(1, len(TIMES["compress"]))
    row = {
        "client_rounds": n,
        "mean_s_per_client_round": total,
        "mean_s_drift_check": drift,
        "mean_s_compression": comp,
        "mean_s_local_training": total - drift - comp,
        "total_wall_s_20_rounds": wall,
    }
    print(f"[{method}] client-rounds={n} per-round={total:.3f}s "
          f"(train={row['mean_s_local_training']:.3f} drift={drift:.4f} "
          f"compress={comp:.4f}) wall={wall:.1f}s")
    return row


if __name__ == "__main__":
    out = {m: bench(m) for m in ["proposed", "fedavg"]}
    json.dump(out, open("results/s34/overhead_bench.json", "w"), indent=2)
    print("[saved] results/s34/overhead_bench.json")
