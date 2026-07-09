"""Evaluation metrics for federated RUL.

  rmse           : standard error.
  cmapss_score   : asymmetric scoring — late predictions (pred < true) are
                   penalized more heavily than early ones, matching maintenance
                   cost asymmetry.
  per-client var : variance of per-client RMSE (fairness: a good fleet average
                   must not hide one abandoned machine).
  retention      : accuracy on the drifted tail relative to the pre-drift head
                   (measured by the caller by comparing across drift segments).
"""
import numpy as np


def rmse(pred, true):
    return float(np.sqrt(np.mean((pred - true) ** 2)))


def cmapss_score(pred, true):
    """Standard C-MAPSS asymmetric score. d = pred - true."""
    d = pred - true
    s = np.where(d < 0, np.exp(-d / 13.0) - 1.0, np.exp(d / 10.0) - 1.0)
    return float(np.sum(s))


def evaluate_clients(clients, global_body):
    """Per-client evaluation using each client's personalized head.

    Returns aggregate dict + list of per-client rmse.
    """
    per_rmse, all_pred, all_true = [], [], []
    for c in clients:
        pred, true = c.evaluate(global_body)
        if len(true) == 0:
            continue
        per_rmse.append(rmse(pred, true))
        all_pred.append(pred)
        all_true.append(true)
    if not all_pred:
        return {
            "rmse": float("nan"),
            "score": float("nan"),
            "per_client_rmse": [],
            "per_client_var": 0.0,
            "worst_client_rmse": 0.0,
        }
    all_pred = np.concatenate(all_pred)
    all_true = np.concatenate(all_true)
    return {
        "rmse": rmse(all_pred, all_true),
        "score": cmapss_score(all_pred, all_true),
        "per_client_rmse": per_rmse,
        "per_client_var": float(np.var(per_rmse)) if per_rmse else 0.0,
        "worst_client_rmse": float(np.max(per_rmse)) if per_rmse else 0.0,
    }


def seen_unseen_rmse(clients, global_body):
    """Mechanism study (evaluation-only): stratify each client's test tail into
    RUL values 'seen' vs 'unseen' relative to that client's own train prefix.

    Because the drift injection sorts windows by RUL into segments and the
    80/20 split is ordered, the train prefix misses a contiguous band of RUL
    values at the drift-segment boundary; exact value-membership against the
    train prefix recovers precisely that band (RULs are integer-valued).
    """
    seen_p, seen_t, unseen_p, unseen_t = [], [], [], []
    per_client = []
    for c in clients:
        pred, true = c.evaluate(global_body)
        if len(true) == 0:
            continue
        train_vals = np.unique(c.train_ds.tensors[1].numpy())
        mask = np.isin(true, train_vals)
        row = {"id": c.id, "n_seen": int(mask.sum()), "n_unseen": int((~mask).sum())}
        if mask.any():
            row["seen_rmse"] = rmse(pred[mask], true[mask])
            seen_p.append(pred[mask])
            seen_t.append(true[mask])
        if (~mask).any():
            row["unseen_rmse"] = rmse(pred[~mask], true[~mask])
            unseen_p.append(pred[~mask])
            unseen_t.append(true[~mask])
        per_client.append(row)
    return {
        "seen_rmse": rmse(np.concatenate(seen_p), np.concatenate(seen_t)) if seen_p else None,
        "unseen_rmse": rmse(np.concatenate(unseen_p), np.concatenate(unseen_t)) if unseen_p else None,
        "n_seen": int(sum(r["n_seen"] for r in per_client)),
        "n_unseen": int(sum(r["n_unseen"] for r in per_client)),
        "per_client": per_client,
    }


def retention_curve(clients, global_body, n_bins=5):
    """RMSE across ordered tail bins (proxy for accuracy retention under drift).

    Splits each client's ordered test tail into `n_bins` sequential bins and
    reports RMSE per bin, pooled across clients. Rising RMSE across bins ->
    accuracy erosion under drift; a flat curve -> good retention.
    """
    bins_pred = [[] for _ in range(n_bins)]
    bins_true = [[] for _ in range(n_bins)]
    for c in clients:
        pred, true = c.evaluate(global_body)
        if len(true) < n_bins:
            continue
        idx = np.array_split(np.arange(len(true)), n_bins)
        for b in range(n_bins):
            bins_pred[b].append(pred[idx[b]])
            bins_true[b].append(true[idx[b]])
    curve = []
    for b in range(n_bins):
        if not bins_pred[b]:
            curve.append(float("nan"))
            continue
        p = np.concatenate(bins_pred[b])
        t = np.concatenate(bins_true[b])
        curve.append(rmse(p, t))
    return curve
