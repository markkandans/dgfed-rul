"""Form non-IID clients and (optionally) inject temporal drift.

Three partition strategies:
  - 'condition': group training units by their dominant operating regime, so
    each client sees a different P(x,y) (statistical heterogeneity). Natural for
    FD002/FD004.
  - 'unit': one client per engine-unit group (fallback, also non-IID by age).
  - 'regime': window-level partition — each window is assigned to the client
    for its operating-condition id at the window's last cycle (units are NOT
    the client key). Avoids the dominant-regime collapse on FD002/FD004 where
    every unit shares the same most-visited regime.

Drift injection: within each client, samples are ordered by degradation stage
and concatenated in regime-shifted segments so that P(x,y) is non-stationary in
time. The per-client stream is then split into an ordered train prefix and a
held-out ordered tail used to measure retention under drift.
"""
import numpy as np

from .cmapss import _make_windows


def _order_with_drift(X, y, n_segments, rng):
    """Reorder a client's windows into `n_segments` stationary blocks with shifts.

    We sort by RUL (degradation stage) then rotate segment order so consecutive
    blocks correspond to different operating stages -> abrupt distribution shift
    at segment boundaries, i.e. injected concept drift.
    """
    order = np.argsort(-y)                      # healthy -> degraded
    Xo, yo = X[order], y[order]
    seg = np.array_split(np.arange(len(yo)), n_segments)
    rot = rng.permutation(n_segments)           # shuffle the *order* of stages
    idx = np.concatenate([seg[r] for r in rot])
    return Xo[idx], yo[idx]


def make_clients(bundle, cfg):
    """Return a list of client dicts:
        {id, X_train, y_train, X_test, y_test, n, cond}
    Train/test are ordered (time-like) so drift retention can be measured on the
    tail.
    """
    df = bundle["train_df"]
    feats = bundle["feats"]
    rng = np.random.default_rng(cfg.seed)

    if cfg.partition == "regime":
        # client = operating regime; each window goes to the client for its
        # condition id at the window's last cycle
        X, y, c = _make_windows(df, feats, cfg.window, with_cond=True)
        groups = {int(k): np.where(c == k)[0] for k in np.unique(c)}
        # cap client count (same policy as unit/condition: keep largest groups)
        keys = list(groups.keys())
        if len(keys) > cfg.max_clients:
            keys = sorted(keys, key=lambda k: -len(groups[k]))[: cfg.max_clients]
            groups = {k: groups[k] for k in keys}
        clients = []
        for cid, k in enumerate(sorted(groups.keys())):
            Xk, yk = X[groups[k]], y[groups[k]]
            if len(yk) < 4:
                continue
            if cfg.inject_drift:
                Xk, yk = _order_with_drift(Xk, yk, cfg.drift_segments, rng)
            # ordered split: first 80% train, last 20% test (the drifted tail)
            cut = int(0.8 * len(yk))
            clients.append(
                {
                    "id": cid,
                    "cond": int(k),
                    "X_train": Xk[:cut],
                    "y_train": yk[:cut],
                    "X_test": Xk[cut:],
                    "y_test": yk[cut:],
                    "n": cut,
                }
            )
        if not clients:
            raise RuntimeError("No clients formed — check data / partition settings.")
        return clients

    # assign each unit to a client key
    if cfg.partition == "condition":
        # dominant operating regime per unit
        key = df.groupby("unit")["cond"].agg(lambda s: s.value_counts().idxmax())
        groups = {}
        for unit, k in key.items():
            groups.setdefault(int(k), []).append(unit)
    else:  # 'unit' -> chunk units into max_clients groups
        units = sorted(df["unit"].unique())
        chunks = np.array_split(units, min(cfg.max_clients, len(units)))
        groups = {i: list(c) for i, c in enumerate(chunks)}

    # cap client count by merging smallest groups if needed
    keys = list(groups.keys())
    if len(keys) > cfg.max_clients:
        keys = sorted(keys, key=lambda k: -len(groups[k]))[: cfg.max_clients]
        groups = {k: groups[k] for k in keys}

    clients = []
    for cid, k in enumerate(sorted(groups.keys())):
        sub = df[df["unit"].isin(groups[k])]
        X, y, _ = _make_windows(sub, feats, cfg.window, with_cond=False)
        if len(y) < 4:
            continue
        if cfg.inject_drift:
            X, y = _order_with_drift(X, y, cfg.drift_segments, rng)
        # ordered split: first 80% train, last 20% test (the drifted tail)
        cut = int(0.8 * len(y))
        clients.append(
            {
                "id": cid,
                "cond": int(k),
                "X_train": X[:cut],
                "y_train": y[:cut],
                "X_test": X[cut:],
                "y_test": y[cut:],
                "n": cut,
            }
        )
    if not clients:
        raise RuntimeError("No clients formed — check data / partition settings.")
    return clients
