"""Non-federated baselines.

  central : one model trained on all clients' pooled training windows —
            the accuracy *upper bound* (no privacy, unlimited bandwidth).
            Also reports the official C-MAPSS test-set metrics.
  local   : each client trains alone on its own data — the *lower bound*
            showing what isolation costs (esp. small / drifted clients).
"""
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader

from models.model import RULNet
from metrics import rmse, cmapss_score


def _fit(net, X, y, cfg, device, epochs):
    ds = TensorDataset(
        torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
    )
    loader = DataLoader(ds, batch_size=cfg.batch_size, shuffle=True)
    opt = torch.optim.Adam(net.parameters(), lr=cfg.lr)
    net.train()
    for _ in range(epochs):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = torch.nn.functional.mse_loss(net(xb), yb)
            loss.backward()
            opt.step()
    return net


@torch.no_grad()
def _pred(net, X, device, bs=1024):
    net.eval()
    out = []
    for i in range(0, len(X), bs):
        xb = torch.tensor(X[i : i + bs], dtype=torch.float32).to(device)
        out.append(net(xb).cpu().numpy())
    return np.concatenate(out) if out else np.zeros(0, dtype=np.float32)


def _client_metrics(preds_trues):
    pairs = [(p, t) for p, t in preds_trues if len(t)]
    if not pairs:
        return {"rmse": float("nan"), "score": float("nan"),
                "per_client_rmse": [], "per_client_var": 0.0,
                "worst_client_rmse": 0.0}
    per = [rmse(p, t) for p, t in pairs]
    ap = np.concatenate([p for p, _ in pairs])
    at = np.concatenate([t for _, t in pairs])
    return {
        "rmse": rmse(ap, at),
        "score": cmapss_score(ap, at),
        "per_client_rmse": per,
        "per_client_var": float(np.var(per)),
        "worst_client_rmse": float(np.max(per)),
    }


def run_central(raw_clients, bundle, cfg, device):
    X = np.concatenate([c["X_train"] for c in raw_clients])
    y = np.concatenate([c["y_train"] for c in raw_clients])
    net = RULNet(cfg, bundle["n_features"]).to(device)
    _fit(net, X, y, cfg, device, cfg.central_epochs)

    res = _client_metrics(
        [(_pred(net, c["X_test"], device), c["y_test"]) for c in raw_clients]
    )
    Xg, yg = bundle["global_test"]
    pg = _pred(net, Xg, device)
    res["official_test_rmse"] = rmse(pg, yg)
    res["official_test_score"] = cmapss_score(pg, yg)
    res["method"] = "central"
    res["total_MB_uploaded"] = None  # not applicable
    return res


def run_local(raw_clients, bundle, cfg, device):
    outs = []
    for c in raw_clients:
        net = RULNet(cfg, bundle["n_features"]).to(device)
        _fit(net, c["X_train"], c["y_train"], cfg, device, cfg.central_epochs)
        outs.append((_pred(net, c["X_test"], device), c["y_test"]))
    res = _client_metrics(outs)
    res["method"] = "local"
    res["total_MB_uploaded"] = 0.0
    return res
