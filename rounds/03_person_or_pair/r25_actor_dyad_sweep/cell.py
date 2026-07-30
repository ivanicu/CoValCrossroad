"""r25 -- One cell of the actor-vs-dyad robustness matrix.

r23 overturned the interpretation the whole r16/r17/r18 arm rests on: most of
r01's cross-prompt persistence is an additive ACTOR effect, and the
pair-specific residual is only 0.034 (z=+4.67).  That verdict currently stands
on ONE cell -- Pearson agreement, majority-shared items, min_overlap 3, one
random split-half, one centring choice.

A residual that small has to be shown stable before it is allowed to carry a
conclusion, and it has to be shown stable in the direction that could kill it:
if the pair-specific component appears only under one agreement metric, it is a
property of the metric, not of the raters.

Axes swept (see run_sweep.sh):
  metric      pearson | spearman | cosine | negl1   -- how "agreement" is defined
  min_overlap 3 | 4 | 5                             -- how many shared items a dyad needs
  thr         majority | 3 | 2                      -- which items count as shared
  standardize on | off                              -- per-rater z within prompt
  centre      on | off                              -- prompt-difficulty removal

Each cell reports the actor/residual split and the residual's z against the
dyad-permutation null, and averages the split-half over many random splits
rather than trusting one, since a single split is itself a coin flip.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"


def load(path: Path, thr_mode: str):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        items = rec.get("coval_full") or []
        raters = {s["annotator_id"] for it in items for s in (it.get("scores") or [])}
        if len(raters) < 4:
            continue
        thr = (max(2, (len(raters) + 1) // 2) if thr_mode == "majority" else int(thr_mode))
        shared = [it for it in items if len(it.get("scores") or []) >= thr]
        if len(shared) < 3:
            continue
        rl = sorted(raters)
        pos = {r: i for i, r in enumerate(rl)}
        m = np.full((len(rl), len(shared)), np.nan)
        for j, it in enumerate(shared):
            for s in it["scores"]:
                m[pos[s["annotator_id"]], j] = float(s["score"])
        out.append({"raters": rl, "m": m})
    return out


def standardize(mat):
    out = mat.copy()
    for i in range(out.shape[0]):
        row, ok = out[i], ~np.isnan(out[i])
        if ok.sum() < 2:
            continue
        mu, sd = row[ok].mean(), row[ok].std()
        out[i, ok] = (row[ok] - mu) / (sd if sd > 1e-9 else 1.0)
    return out


def agree(x, y, metric):
    """Four genuinely different readings of 'these two raters agree'."""
    if metric == "pearson":
        if x.std() < 1e-9 or y.std() < 1e-9:
            return None
        return float(np.corrcoef(x, y)[0, 1])
    if metric == "spearman":
        if len(set(x)) < 2 or len(set(y)) < 2:
            return None
        rx, ry = rankdata(x), rankdata(y)
        return float(np.corrcoef(rx, ry)[0, 1])
    if metric == "cosine":
        nx, ny = np.linalg.norm(x), np.linalg.norm(y)
        if nx < 1e-9 or ny < 1e-9:
            return None
        return float(x @ y / (nx * ny))
    if metric == "negl1":
        # a metric with NO invariance to scale, unlike the other three --
        # included precisely because r01's style control is a no-op under
        # correlation and cannot be under this one
        return float(-np.abs(x - y).mean())
    raise ValueError(metric)


def pair_agreements(mat, raters, metric, min_overlap):
    res = {}
    for i, j in combinations(range(len(raters)), 2):
        a, b = mat[i], mat[j]
        ok = ~np.isnan(a) & ~np.isnan(b)
        if ok.sum() < min_overlap:
            continue
        v = agree(a[ok], b[ok], metric)
        if v is not None and v == v:
            res[(raters[i], raters[j])] = v
    return res


def additive_fit(ag, raters):
    keys = list(ag.keys())
    if len(keys) < 3:
        return None
    pos = {r: i for i, r in enumerate(raters)}
    X = np.zeros((len(keys), len(raters) + 1))
    y = np.zeros(len(keys))
    for k, (u, v) in enumerate(keys):
        X[k, 0] = 1.0
        X[k, pos[u] + 1] += 1.0
        X[k, pos[v] + 1] += 1.0
        y[k] = ag[(u, v)]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(((y - yhat) ** 2).sum()) / ss if ss > 1e-12 else float("nan")
    return dict(zip(keys, yhat)), dict(zip(keys, y - yhat)), r2


def split_half(by_pair, rng, reps):
    """Average over `reps` random splits -- one split is a coin flip."""
    rhos, negs = [], []
    for _ in range(reps):
        xs, ys = [], []
        for vals in by_pair.values():
            if len(vals) < 2:
                continue
            v = np.array(vals)
            idx = rng.permutation(len(v))
            h = len(v) // 2
            xs.append(v[idx[:h]].mean())
            ys.append(v[idx[h:2 * h]].mean())
        if len(xs) < 30:
            continue
        xs, ys = np.array(xs), np.array(ys)
        rhos.append(float(np.corrcoef(xs, ys)[0, 1]))
        negs.append(float(np.mean((xs < 0) & (ys < 0))))
    if not rhos:
        return {"rho": float("nan"), "neg_both": float("nan"), "n_pairs": 0}
    return {"rho": float(np.mean(rhos)), "rho_sd": float(np.std(rhos)),
            "neg_both": float(np.mean(negs)), "n_pairs": len(xs)}


def collect(data, cfg, rng, permute=False):
    raw, act, res, r2s = defaultdict(list), defaultdict(list), defaultdict(list), []
    for rec in data:
        mat = standardize(rec["m"]) if cfg["standardize"] else rec["m"]
        ag = pair_agreements(mat, rec["raters"], cfg["metric"], cfg["min_overlap"])
        if len(ag) < 3:
            continue
        fit = additive_fit(ag, rec["raters"])
        if fit is None:
            continue
        yhat, resid, r2 = fit
        r2s.append(r2)
        mu = float(np.mean(list(ag.values()))) if cfg["centre"] else 0.0
        rv = list(resid.values())
        if permute:
            rv = list(rng.permutation(rv))
        for (k, _), r in zip(resid.items(), rv):
            raw[frozenset(k)].append(ag[k] - mu)
            act[frozenset(k)].append(yhat[k] - mu)
            res[frozenset(k)].append(r)
    return raw, act, res, float(np.mean(r2s)) if r2s else float("nan")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--metric", required=True,
                   choices=["pearson", "spearman", "cosine", "negl1"])
    p.add_argument("--min-overlap", type=int, required=True)
    p.add_argument("--thr", required=True)          # "majority" | "3" | "2"
    p.add_argument("--standardize", type=int, required=True)
    p.add_argument("--centre", type=int, required=True)
    p.add_argument("--splits", type=int, default=25)
    p.add_argument("--null-reps", type=int, default=20)
    # r23 read the sign test as NULL (z=+1.40) using ONE split; r25 averages
    # the observed over 25 and the null over splits//5, so the observed has
    # lower variance than the null it is scored against. That mismatch is
    # conservative for z, but it is still a mismatch, and a test that changes
    # verdict with estimator variance has not been settled by either run.
    # This flag matches them exactly.
    p.add_argument("--null-splits", type=int, default=0)
    a = p.parse_args()

    cfg = {"metric": a.metric, "min_overlap": a.min_overlap, "thr": a.thr,
           "standardize": bool(a.standardize), "centre": bool(a.centre)}
    tag = (f"{a.metric}_ov{a.min_overlap}_thr{a.thr}"
           f"_std{a.standardize}_ctr{a.centre}")
    rng = np.random.default_rng(20260728)
    data = load(a.data, a.thr)

    raw, act, res, r2 = collect(data, cfg, rng)
    s_raw, s_act, s_res = (split_half(raw, rng, a.splits), split_half(act, rng, a.splits),
                           split_half(res, rng, a.splits))
    null = []
    for _ in range(a.null_reps):
        _, _, nres, _ = collect(data, cfg, rng, permute=True)
        null.append(split_half(nres, rng, a.null_splits or max(3, a.splits // 5)))
    nrho = np.array([x["rho"] for x in null if x["rho"] == x["rho"]])
    nneg = np.array([x["neg_both"] for x in null if x["neg_both"] == x["neg_both"]])
    z = float((s_res["rho"] - nrho.mean()) / (nrho.std() + 1e-12)) if len(nrho) else float("nan")
    zneg = float((s_res["neg_both"] - nneg.mean()) / (nneg.std() + 1e-12)) if len(nneg) else float("nan")
    share = s_res["rho"] / s_raw["rho"] if abs(s_raw["rho"]) > 1e-9 else float("nan")

    rec = {"cfg": cfg, "tag": tag, "prompts": len(data), "actor_model_r2": r2,
           "raw_rho": s_raw["rho"], "actor_rho": s_act["rho"], "resid_rho": s_res["rho"],
           "resid_rho_sd": s_res.get("rho_sd"), "n_pairs": s_raw["n_pairs"],
           "resid_z": z, "neg_both": s_res["neg_both"], "neg_both_z": zneg,
           "pair_specific_share": float(share),
           "null_mean": float(nrho.mean()) if len(nrho) else None,
           "null_sd": float(nrho.std()) if len(nrho) else None}
    _RES.mkdir(parents=True, exist_ok=True)
    (_RES / f"cell_{tag}.json").write_text(json.dumps(rec, indent=1))
    print(f"{tag:52s} actorR2={r2:.3f} raw={s_raw['rho']:+.4f} act={s_act['rho']:+.4f} "
          f"res={s_res['rho']:+.4f} z={z:+6.2f} share={share:6.1%} negz={zneg:+.2f}")


if __name__ == "__main__":
    main()
