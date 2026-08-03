#!/usr/bin/env python3
"""
IS THE BUDGET CEILING A CEILING?  Lambda_budget divides by oracle4, which is a
GREEDY search.  Greedy is not optimal, so oracle4 UNDER-states what a K=4
unit-weight compiler can reach, so Lambda_budget OVER-states the core's budget
efficiency.  The reported 0.43 is therefore an upper bound, and the size of the
bound has to be measured rather than waved at.

Method: on every prompt with n_full <= 14, enumerate ALL C(n,4) subsets and take
the exact maximum.  Compare with greedy on the same prompts.  Report the gap and
the corrected Lambda_budget on that subpopulation, plus the same statistic on the
complementary (larger-rubric) prompts where only greedy is affordable, so that
the extrapolation is visible rather than assumed.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

import run as R

RES = Path(__file__).resolve().parent / "results"


def main():
    joined, _ = R.load_join()
    bundles, _ = R.build(joined, R.load_sat("full"), R.load_sat("core"))
    C_ = R.cache(bundles, "z", "mean")
    rng = np.random.default_rng(11)
    small, large = [], []
    for pid in sorted(bundles):
        b = bundles[pid]
        Zf, Zc, w = C_[pid]
        nc = Zf.shape[0]
        tgt = w @ Zf
        k = min(4, nc)
        g = R.pairwise_conc(R._greedy(Zf, tgt, k, +1), tgt)
        core = R.pairwise_conc(Zc.sum(0), tgt)
        r4 = np.mean([R.pairwise_conc(Zf[rng.choice(nc, size=k, replace=False)].sum(0), tgt)
                      for _ in range(20)])
        if nc <= 14:
            ex = max(R.pairwise_conc(Zf[list(s)].sum(0), tgt)
                     for s in itertools.combinations(range(nc), k))
            small.append((g, ex, core, r4))
        else:
            large.append((g, np.nan, core, r4))
    S = np.array(small)
    L = np.array(large)
    out = {"n_small_exhaustive": len(small), "n_large_greedy_only": len(large),
           "small": dict(greedy=float(S[:, 0].mean()), exact=float(S[:, 1].mean()),
                         core=float(S[:, 2].mean()), random4=float(S[:, 3].mean()),
                         greedy_shortfall=float((S[:, 1] - S[:, 0]).mean()),
                         frac_prompts_greedy_suboptimal=float((S[:, 1] > S[:, 0] + 1e-12).mean())),
           "large": dict(greedy=float(L[:, 0].mean()), core=float(L[:, 2].mean()),
                         random4=float(L[:, 3].mean())) if len(large) else None}
    lb_g = (S[:, 2].mean() - S[:, 3].mean()) / (S[:, 0].mean() - S[:, 3].mean())
    lb_e = (S[:, 2].mean() - S[:, 3].mean()) / (S[:, 1].mean() - S[:, 3].mean())
    out["Lambda_budget_on_small"] = dict(with_greedy_ceiling=float(lb_g),
                                         with_EXACT_ceiling=float(lb_e),
                                         inflation_from_greedy=float(lb_g - lb_e))
    print(json.dumps(out, indent=1))
    (RES / "greedy_bound.json").write_text(json.dumps(out, indent=1, default=float))
    print("wrote results/greedy_bound.json")


if __name__ == "__main__":
    main()
