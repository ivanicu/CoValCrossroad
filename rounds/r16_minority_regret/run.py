"""r16 -- Score aggregation rules by the bloc they leave worst off.

r06 asked which rule best predicts the aggregate human ranking. Utility and
majority rules optimise exactly that, so the contest was rigged in their favour
and conflict-aware's loss there carries no information about its actual claim.

Its claim is about minorities. So the metric here is not average fit but the
satisfaction of the worst-off bloc:

    for each prompt
        split raters into 2 blocs by their signed-rating profiles
        for each rule, build its core
        bloc satisfaction = mean signed rating that bloc gave the core's items,
                            with the core's own direction applied
        regret = best bloc - worst bloc
        report min-bloc satisfaction and regret per rule

Controls, both required:
  RANDOM BLOCS   split raters at random instead of by profile. If profile-based
                 blocs show no more regret than random ones, the "minority" is
                 an artifact of splitting, not a constituency.
  RANDOM CORE    four shared items chosen with no principle, as the floor.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[1])
_RES = str(_HERE / "results")
sys.path.insert(0, _ROOT)
from covalx import make_core  # noqa: E402

RULES = ("utility", "majority", "consensus", "constituency")


def blocs_by_profile(M: np.ndarray, rng, random_split=False):
    """Split raters into two blocs. M is raters x items with NaN."""
    n = M.shape[0]
    if random_split or n < 4:
        idx = rng.permutation(n)
        return idx[: n // 2], idx[n // 2:]
    X = np.nan_to_num(M - np.nanmean(M, axis=1, keepdims=True))
    # first principal direction of the rater-profile matrix
    X = X - X.mean(0)
    try:
        u, s, vt = np.linalg.svd(X, full_matrices=False)
        proj = X @ vt[0]
    except np.linalg.LinAlgError:
        proj = X.sum(1)
    a = np.where(proj >= np.median(proj))[0]
    b = np.where(proj < np.median(proj))[0]
    if len(a) == 0 or len(b) == 0:
        idx = rng.permutation(n)
        return idx[: n // 2], idx[n // 2:]
    return a, b


def bloc_satisfaction(M, core, rows):
    """Mean signed rating this bloc gave the core's items, direction applied."""
    if len(rows) == 0 or not core:
        return np.nan
    vals = []
    for j, d in core:
        col = M[rows, j]
        col = col[~np.isnan(col)]
        if col.size:
            vals.append(d * float(col.mean()))
    return float(np.mean(vals)) if vals else np.nan


def conflict_aware_core(M, k):
    """half consensus, half most-polarized -- the r06 operationalisation."""
    n = M.shape[1]
    cons, pol = [], []
    for j in range(n):
        v = M[:, j]
        v = v[~np.isnan(v)]
        if v.size == 0:
            cons.append((0.0, j, 1)); pol.append((0.0, j, 1)); continue
        lo = float(np.percentile(v, 25))
        cons.append((lo if lo > 0 else 0.0, j, 1 if v.mean() >= 0 else -1))
        p, ng = float((v > 0).mean()), float((v < 0).mean())
        pol.append((4 * p * ng * float(np.mean(np.abs(v))) / 10.0, j,
                    1 if v.mean() >= 0 else -1))
    cons.sort(key=lambda t: (-t[0], t[1])); pol.sort(key=lambda t: (-t[0], t[1]))
    out, seen = [], set()
    for _, j, d in cons[: max(1, k // 2)]:
        out.append((j, d)); seen.add(j)
    for _, j, d in pol:
        if len(out) >= k:
            break
        if j not in seen:
            out.append((j, d)); seen.add(j)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubrics", type=Path, default=Path(_ROOT) / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=Path(_RES) / "r16_minority_regret.json")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--boot", type=int, default=4000)
    a = ap.parse_args()

    rng = np.random.default_rng(20260727)
    mats = []
    for line in open(a.rubrics, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        items = rec.get("coval_full") or []
        raters = sorted({s["annotator_id"] for it in items for s in it.get("scores") or []})
        if len(raters) < 6:
            continue
        thr = max(2, (len(raters) + 1) // 2)
        shared = [it for it in items if len(it.get("scores") or []) >= thr]
        if len(shared) < a.k + 1:
            continue
        pos = {r: i for i, r in enumerate(raters)}
        M = np.full((len(raters), len(shared)), np.nan)
        for j, it in enumerate(shared):
            for s in it["scores"]:
                M[pos[s["annotator_id"]], j] = float(s["score"])
        mats.append(M)
    print(f"prompts with >=6 raters and >{a.k} shared items: {len(mats)}")

    names = list(RULES) + ["conflict_aware", "random_k"]
    out = {}
    for split_kind in ("profile", "random_blocs"):
        rows = {nm: {"min": [], "regret": [], "mean": []} for nm in names}
        for M in mats:
            A, B = blocs_by_profile(M, rng, random_split=(split_kind == "random_blocs"))
            cores = {nm: make_core(M, nm, a.k) for nm in RULES}
            cores["conflict_aware"] = conflict_aware_core(M, a.k)
            idx = rng.permutation(M.shape[1])[: a.k]
            cores["random_k"] = [(int(j), 1 if np.nanmean(M[:, j]) >= 0 else -1) for j in idx]
            for nm, core in cores.items():
                core = [(j, d) for j, d in core]
                sa = bloc_satisfaction(M, core, A)
                sb = bloc_satisfaction(M, core, B)
                if np.isnan(sa) or np.isnan(sb):
                    continue
                rows[nm]["min"].append(min(sa, sb))
                rows[nm]["regret"].append(abs(sa - sb))
                rows[nm]["mean"].append((sa + sb) / 2)
        out[split_kind] = {}
        print(f"\n=== bloc split: {split_kind} ===")
        print(f"{'rule':16s} {'min-bloc':>10} {'95% CI':>20} {'regret':>9} {'mean':>8}")
        for nm in names:
            mn = np.array(rows[nm]["min"]); rg = np.array(rows[nm]["regret"])
            mean = np.array(rows[nm]["mean"])
            bs = np.array([mn[rng.integers(0, len(mn), size=len(mn))].mean()
                           for _ in range(a.boot)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            out[split_kind][nm] = {"min_bloc": float(mn.mean()),
                                   "min_bloc_ci": [float(lo), float(hi)],
                                   "regret": float(rg.mean()),
                                   "mean_bloc": float(mean.mean()),
                                   "prompts": int(len(mn))}
            print(f"{nm:16s} {mn.mean():>10.3f} {f'[{lo:.3f},{hi:.3f}]':>20} "
                  f"{rg.mean():>9.3f} {mean.mean():>8.3f}")

    # CONTROL: is the profile split finding a real constituency?
    pr = np.mean([out["profile"][nm]["regret"] for nm in names])
    rr = np.mean([out["random_blocs"][nm]["regret"] for nm in names])
    print(f"\n  mean regret, profile blocs = {pr:.3f}   random blocs = {rr:.3f}")
    real = pr > rr * 1.15
    print(f"  -> blocs are {'a real constituency' if real else 'INDISTINGUISHABLE from a random split -- no minority to protect'}")

    ca = out["profile"]["conflict_aware"]; co = out["profile"]["consensus"]
    ut = out["profile"]["utility"]
    print(f"\n  conflict_aware min-bloc {ca['min_bloc']:+.3f} vs consensus {co['min_bloc']:+.3f} "
          f"vs utility {ut['min_bloc']:+.3f}")
    out["blocs_are_real"] = bool(real)
    out["regret_profile"] = float(pr)
    out["regret_random"] = float(rr)
    Path(_RES).mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
