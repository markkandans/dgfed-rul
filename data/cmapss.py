"""C-MAPSS loading + preprocessing.

Raw C-MAPSS files are space-separated with columns:
    unit, cycle, op_setting_1..3, sensor_1..21
`train_*` runs to failure; `RUL_*` gives the true RUL for the LAST cycle of
each unit in `test_*`.

This module produces, for a chosen subset, windowed feature tensors and
piecewise-linear RUL labels, plus per-window operating-condition ids used for
non-IID client partitioning.
"""
import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

COLS = ["unit", "cycle"] + [f"op{i}" for i in range(1, 4)] + [f"s{i}" for i in range(1, 22)]
SENSOR_COLS = [f"s{i}" for i in range(1, 22)]
OP_COLS = [f"op{i}" for i in range(1, 4)]


def _read_raw(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing C-MAPSS file: {path}\n"
            f"Download the dataset and place train/test/RUL_FD00x.txt under the data root "
            f"(see README)."
        )
    df = pd.read_csv(path, sep=r"\s+", header=None)
    df = df.iloc[:, : len(COLS)]
    df.columns = COLS
    return df


def _piecewise_rul(df: pd.DataFrame, cap: int) -> pd.Series:
    """Standard piecewise-linear RUL: max_cycle - cycle, clipped at `cap`."""
    max_cycle = df.groupby("unit")["cycle"].transform("max")
    rul = (max_cycle - df["cycle"]).clip(upper=cap)
    return rul.astype(np.float32)


def _drop_constant_sensors(train: pd.DataFrame, cols):
    """Remove sensors with ~zero variance on the training set (uninformative)."""
    keep = [c for c in cols if train[c].std() > 1e-6]
    return keep


def _condition_ids(df: pd.DataFrame, n_conditions: int, km: KMeans = None):
    """Cluster the 3 operating settings into discrete regimes.

    For single-condition subsets (FD001/FD003) all points collapse to one
    regime, which is expected.
    """
    X = df[OP_COLS].values
    if km is None:
        n = min(n_conditions, max(1, len(np.unique(np.round(X, 3), axis=0))))
        km = KMeans(n_clusters=n, n_init=10, random_state=0).fit(X)
    return km.predict(X), km


def _make_windows(df: pd.DataFrame, feats, window: int, with_cond=False):
    """Sliding windows per unit. Label = RUL at the window's last cycle."""
    Xs, ys, conds = [], [], []
    for _, g in df.groupby("unit"):
        g = g.sort_values("cycle")
        arr = g[feats].values.astype(np.float32)
        rul = g["rul"].values.astype(np.float32)
        cond = g["cond"].values if with_cond else None
        n = len(g)
        if n < window:
            # left-pad short units by repeating the first row
            pad = np.repeat(arr[:1], window - n, axis=0)
            arr = np.vstack([pad, arr])
            rul = np.concatenate([np.repeat(rul[:1], window - n), rul])
            if with_cond:
                cond = np.concatenate([np.repeat(cond[:1], window - n), cond])
            n = window
        for i in range(n - window + 1):
            Xs.append(arr[i : i + window])
            ys.append(rul[i + window - 1])
            if with_cond:
                conds.append(cond[i + window - 1])
    X = np.stack(Xs)                        # (N, window, F)
    y = np.array(ys, dtype=np.float32)
    c = np.array(conds) if with_cond else None
    return X, y, c


def _test_last_windows(df: pd.DataFrame, feats, window: int, rul_truth: np.ndarray):
    """One window per test unit (its final `window` cycles) with the true RUL."""
    Xs, ys = [], []
    for uid, (_, g) in enumerate(df.groupby("unit")):
        g = g.sort_values("cycle")
        arr = g[feats].values.astype(np.float32)
        if len(arr) < window:
            pad = np.repeat(arr[:1], window - len(arr), axis=0)
            arr = np.vstack([pad, arr])
        Xs.append(arr[-window:])
        ys.append(min(rul_truth[uid], 125))   # test truth is also capped by convention
    return np.stack(Xs), np.array(ys, dtype=np.float32)


def load_cmapss(cfg):
    """Return everything needed by the federation.

    Returns a dict with:
        feats        : list of feature column names actually used
        scaler       : fitted StandardScaler (train stats)
        global_test  : (X_test, y_test) pooled across all units (for centralized eval)
        cond_km      : fitted operating-condition clusterer
        train_df     : preprocessed training frame (with 'rul' and 'cond' columns)
    """
    root, sub, cap = cfg.data_root, cfg.subset, cfg.rul_cap
    train = _read_raw(os.path.join(root, f"train_{sub}.txt"))
    test = _read_raw(os.path.join(root, f"test_{sub}.txt"))
    rul_truth = pd.read_csv(
        os.path.join(root, f"RUL_{sub}.txt"), sep=r"\s+", header=None
    ).iloc[:, 0].values

    # RUL labels
    train["rul"] = _piecewise_rul(train, cap)

    # feature selection + scaling (fit on train only)
    feats = _drop_constant_sensors(train, SENSOR_COLS) + OP_COLS
    scaler = StandardScaler().fit(train[feats].values)
    train[feats] = scaler.transform(train[feats].values)
    test[feats] = scaler.transform(test[feats].values)

    # operating-condition ids (for partitioning)
    cond_tr, km = _condition_ids(train, cfg.n_conditions)
    train["cond"] = cond_tr

    # global pooled test set for centralized evaluation
    Xte, yte = _test_last_windows(test, feats, cfg.window, rul_truth)

    return {
        "feats": feats,
        "scaler": scaler,
        "global_test": (Xte, yte),
        "cond_km": km,
        "train_df": train,
        "n_features": len(feats),
    }
