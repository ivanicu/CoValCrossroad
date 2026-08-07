#!/usr/bin/env python3
"""BUDGET DOSE-RESPONSE -- what is the shipped core WORTH, in criteria?

Lambda_budget answers "did it use its four slots well" on an internal target.
This answers the same question on the leakage-free human target, in units a
reader can hold: sweep K = 1..10 for the card's own selection rule (top-K by
population mean weight, unit weights) and read off the K at which the mechanical
compiler's human-ranking accuracy crosses the core's.  That K is the core's
EFFECTIVE CRITERION COUNT.

Positive control built in: the curve must be monotone-ish and must approach
full_unit as K -> n.  A flat curve would mean the ranking of criteria by weight
carries no information and the crossing point would be meaningless."""
import json
from pathlib import Path
import numpy as np
import run as R

rng = np.random.default_rng(11)
joined, _ = R.load_join()
bundles, _ = R.build(joined, R.load_sat("full"), R.load_sat("core"))
C_ = R.cache(bundles, "z", "mean")
KS = list(range(1, 11))
res = {}
for rk in ("world", "personal"):
    tot = {f"top{k}_pos": 0.0 for k in KS}
    tot["core"] = 0.0; tot["full_signed"] = 0.0; tot["full_unit"] = 0.0
    npairs = 0
    per = {k: [] for k in tot}
    for pid in sorted(bundles):
        b = bundles[pid]
        pairs = R.human_pairs(b, rk)
        if not pairs:
            continue
        Zf, Zc, w = C_[pid]
        order = np.argsort(-w)
        cand = {f"top{k}_pos": Zf[order[:min(k, Zf.shape[0])]].sum(0) for k in KS}
        cand["core"] = Zc.sum(0)
        cand["full_signed"] = w @ Zf
        cand["full_unit"] = Zf.sum(0)
        npairs += len(pairs)
        for nm, s in cand.items():
            v = sum(1.0 if s[i]-s[j] > 1e-12 else (0.5 if abs(s[i]-s[j]) <= 1e-12 else 0.0)
                    for _a, i, j in pairs)
            tot[nm] += v; per[nm].append((v, len(pairs)))
    acc = {nm: tot[nm]/npairs for nm in tot}
    # bootstrap CI on (topK - core) clustered by prompt
    P = {nm: np.array(per[nm]) for nm in per}
    n = len(P["core"]); idx = rng.integers(0, n, size=(2000, n))
    ci = {}
    for nm in tot:
        bs = (P[nm][idx, 0].sum(1) - P["core"][idx, 0].sum(1)) / P["core"][idx, 1].sum(1)
        ci[nm] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    cross = None
    for k in KS:
        if acc[f"top{k}_pos"] >= acc["core"]:
            cross = k; break
    res[rk] = dict(acc=acc, ci_vs_core=ci, crossing_K=cross, n_pairs=int(npairs),
                   n_prompts=int(n))
    print(rk, "crossing K =", cross)
    for k in KS:
        print("   top%-2d = %.4f  (vs core %+.4f  CI[%+.4f,%+.4f])" % (
            k, acc[f"top{k}_pos"], acc[f"top{k}_pos"]-acc["core"],
            ci[f"top{k}_pos"][0], ci[f"top{k}_pos"][1]))
    print("   core = %.4f   full_signed = %.4f   full_unit = %.4f" % (
        acc["core"], acc["full_signed"], acc["full_unit"]))
Path("results/budget_curve.json").write_text(json.dumps(res, indent=1, default=float))
