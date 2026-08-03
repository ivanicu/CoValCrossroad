"""r25 -- Collect the 144-cell actor-vs-dyad matrix and read it.

r23 concluded that most of r01's cross-prompt persistence is an additive ACTOR
effect and that only ~23% is pair-specific.  That conclusion decides whether the
r16/r17/r18 arm has a premise.  It stood on one cell.

This reads all 144 and answers three questions:

  1. ROBUSTNESS.  Is the pair-specific residual above its dyad-permutation null
     in every cell, or only under the metric r01 happened to choose?  A residual
     of 0.034 that appears under Pearson and vanishes under Spearman is a
     property of Pearson.

  2. GAUGE (pre-registered before the cells landed).  r01's "response-style
     control" is per-rater z-scoring.  Pearson and Spearman are BOTH invariant
     to it -- Pearson because correlation ignores affine rescaling, Spearman
     because z-scoring is monotone and preserves ranks.  Cosine and negative-L1
     are NOT.  So the `standardize` axis MUST be a no-op for pearson/spearman
     and MUST bite for cosine/negl1.
       * If std moves pearson or spearman -> this sweep has a bug, because that
         is algebraically impossible.
       * If std fails to move cosine or negl1 -> the raters have no style
         variation to remove, and r01's control was vacuous for a second and
         independent reason.
     Either outcome is informative, which is what makes it worth checking.

  3. SIGN.  r23's sharper separator -- an excess of pairs reliably negative in
     BOTH halves, which reliability heterogeneity cannot produce -- read z=+1.40
     at 40 nulls.  Does it stay null across the matrix, or does it appear under
     metrics that keep the sign information Pearson normalises away?
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_RES = _HERE / "results"


def main() -> None:
    cells = []
    for f in sorted(_RES.glob("cell_*.json")):
        try:
            cells.append(json.loads(f.read_text()))
        except Exception:
            pass
    if not cells:
        raise SystemExit("no cells yet")
    ok = [c for c in cells if c["resid_z"] == c["resid_z"] and c["raw_rho"] == c["raw_rho"]]
    print(f"cells: {len(cells)} present, {len(ok)} with a finite residual z\n")

    print("=== 1. ROBUSTNESS: pair-specific residual, by metric ===")
    print(f"{'metric':10s} {'n':>4} {'raw rho':>16} {'actor rho':>16} "
          f"{'resid rho':>16} {'resid z':>14} {'share':>14}")
    by_m = defaultdict(list)
    for c in ok:
        by_m[c["cfg"]["metric"]].append(c)
    for m, cs in sorted(by_m.items()):
        g = lambda k: np.array([x[k] for x in cs])
        rng_ = lambda k: f"{g(k).min():+.3f}..{g(k).max():+.3f}"
        print(f"{m:10s} {len(cs):>4} {rng_('raw_rho'):>16} {rng_('actor_rho'):>16} "
              f"{rng_('resid_rho'):>16} {rng_('resid_z'):>14} "
              f"{f'{g('pair_specific_share').min():.0%}..{g('pair_specific_share').max():.0%}':>14}")
    n_sig = sum(1 for c in ok if c["resid_z"] > 2.0)
    print(f"\n  cells where the pair-specific residual beats its null (z>2): "
          f"{n_sig}/{len(ok)} = {n_sig/len(ok):.1%}")
    shares = np.array([c["pair_specific_share"] for c in ok
                       if 0 < c["pair_specific_share"] < 2])
    print(f"  pair-specific share of the headline, across the matrix: "
          f"median {np.median(shares):.1%}  range {shares.min():.1%}..{shares.max():.1%}")

    print("\n=== 2. GAUGE: does per-rater z-scoring move the number? ===")
    print("    (pre-registered: MUST be zero for pearson/spearman, nonzero for cosine/negl1)")
    pairs = defaultdict(dict)
    for c in ok:
        k = (c["cfg"]["metric"], c["cfg"]["min_overlap"], c["cfg"]["thr"], c["cfg"]["centre"])
        pairs[k][c["cfg"]["standardize"]] = c["raw_rho"]
    deltas = defaultdict(list)
    for (m, *_r), d in pairs.items():
        if True in d and False in d:
            deltas[m].append(abs(d[True] - d[False]))
    print(f"{'metric':10s} {'pairs':>6} {'max |delta raw rho|':>22}   verdict")
    verdicts = {}
    for m, ds in sorted(deltas.items()):
        mx = max(ds)
        invariant = mx < 1e-6
        expected_inv = m in ("pearson", "spearman")
        agree = invariant == expected_inv
        verdicts[m] = {"max_delta": float(mx), "invariant": bool(invariant),
                       "expected_invariant": expected_inv, "as_predicted": bool(agree)}
        note = ("no-op, as predicted -- the control cannot fail here"
                if invariant and expected_inv else
                "bites, as predicted -- this metric CAN see style"
                if not invariant and not expected_inv else
                "*** CONTRADICTS ALGEBRA: sweep bug ***" if not invariant and expected_inv else
                "*** no style variation to remove: r01's control was vacuous twice over ***")
        print(f"{m:10s} {len(ds):>6} {mx:>22.2e}   {note}")

    print("\n=== 3. SIGN: reliably-disagreeing pairs beyond null ===")
    zs = np.array([c["neg_both_z"] for c in ok if c["neg_both_z"] == c["neg_both_z"]])
    by_m_neg = {m: np.array([x["neg_both_z"] for x in cs
                             if x["neg_both_z"] == x["neg_both_z"]]) for m, cs in by_m.items()}
    for m, v in sorted(by_m_neg.items()):
        if len(v):
            print(f"  {m:10s} neg-both z: median {np.median(v):+.2f}  "
                  f"range {v.min():+.2f}..{v.max():+.2f}  "
                  f"cells>2: {int((v > 2).sum())}/{len(v)}")
    print(f"\n  overall: {int((zs > 2).sum())}/{len(zs)} cells show an excess of pairs "
          f"reliably negative in both halves")

    out = {
        "cells": len(cells), "usable": len(ok),
        "resid_z_gt2": n_sig, "resid_z_gt2_frac": n_sig / len(ok),
        "share_median": float(np.median(shares)),
        "share_range": [float(shares.min()), float(shares.max())],
        "gauge": verdicts,
        "neg_both_z_gt2": int((zs > 2).sum()), "neg_both_n": int(len(zs)),
        "by_metric": {m: {"n": len(cs),
                          "resid_rho": [float(min(x["resid_rho"] for x in cs)),
                                        float(max(x["resid_rho"] for x in cs))],
                          "resid_z": [float(min(x["resid_z"] for x in cs)),
                                      float(max(x["resid_z"] for x in cs))]}
                      for m, cs in by_m.items()},
    }
    (_RES / "r25_summary.json").write_text(json.dumps(out, indent=1))
    print(f"\nwrote {_RES / 'r25_summary.json'}")


if __name__ == "__main__":
    main()
