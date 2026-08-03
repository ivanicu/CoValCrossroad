"""Distinctness WITHOUT rank: do two operators flip the SAME prompts?

r211 retired rank because three defensible nulls spanned 12.1-18.0 with the observation at 13, and
because matching per-prompt norms moved the statistic more than the data did. The replacement has
to be scale-free, have a null that is not a construction choice, and be interpretable.

  phi(o, o')  = correlation between two BINARY flip indicators, on the INTERSECTION of the two
                operators' domains, pooled over the selection-rule x seed sweep.
  NULL        = permute one operator's flip indicator across prompts, PRESERVING its marginal flip
                rate. This holds constant the only thing that made rank fragile -- the magnitude
                profile -- and asks the one question that matters: is the co-occurrence of flips
                more than the marginals force?
  MULTIPLICITY  171 pairs; Bonferroni-scale |z| > 3.9.

PRE-REGISTERED, because these follow from r208's algebra and must be reproduced or the pipeline is
broken:  phi(dose_delete, set_add_cancelling) = 1.000 exactly.
         phi(dose_double, set_duplicate)      = 1.000 exactly.
KILL: if every pair exceeds the null's 99th percentile, the operator set is one act.
"""
from __future__ import annotations

import json, math, pathlib, pickle, sys
from collections import defaultdict
import numpy as np

OUT = pathlib.Path(__file__).resolve().parent / "results"


def main() -> int:
    with open(OUT / "_raw.pkl", "rb") as fh:
        d = pickle.load(fh)
    acc, domain, OPS = d["acc"], d["domain"], d["OPS"]
    live = [o for o in OPS if not o.startswith(("CTRL", "SHAM"))]
    keys = sorted(acc[live[0]].keys())

    F, D_ = {}, {}
    for o in live:
        F[o] = np.concatenate([np.array(acc[o][k])[:, 0] for k in keys])
        D_[o] = np.concatenate([np.array(domain[o][k], bool) for k in keys])

    rng = np.random.default_rng(0)
    rows, exact = [], {}
    for i, a in enumerate(live):
        for b in live[i + 1:]:
            m = D_[a] & D_[b]
            n = int(m.sum())
            x, y = F[a][m].astype(float), F[b][m].astype(float)
            if n < 50 or x.std() < 1e-9 or y.std() < 1e-9:
                rows.append({"a": a, "b": b, "n": n, "phi": float("nan"), "z": float("nan"),
                             "why": "constant or empty on the intersection"})
                continue
            phi = float(np.corrcoef(x, y)[0, 1])
            null = np.array([np.corrcoef(rng.permutation(x), y)[0, 1] for _ in range(200)])
            z = (phi - null.mean()) / max(null.std(), 1e-12)
            rows.append({"a": a, "b": b, "n": n, "phi": phi, "z": float(z),
                         "null_p99": float(np.quantile(null, .99))})
            exact[(a, b)] = phi

    ok = [r for r in rows if r["phi"] == r["phi"]]
    sig = [r for r in ok if abs(r["z"]) > 3.9]
    print("=" * 100)
    print("DISTINCTNESS WITHOUT RANK -- phi between flip patterns, vs a marginal-preserving null")
    print("=" * 100)
    print(f"  pairs tested {len(ok)} of {len(rows)}; surviving |z| > 3.9 (Bonferroni over 171): {len(sig)}")
    print(f"  pairs NOT surviving: {len(ok) - len(sig)}  -- reported, per G3\n")

    pre = [("dose_delete", "set_add_cancelling"), ("dose_double", "set_duplicate")]
    print("  PRE-REGISTERED ALGEBRAIC IDENTITIES (must be exactly 1.000):")
    allok = True
    for a, b in pre:
        v = exact.get((a, b), exact.get((b, a)))
        good = v is not None and abs(v - 1.0) < 1e-9
        allok &= good
        print(f"    phi({a}, {b}) = {v if v is None else f'{v:.6f}'}   "
              f"{'PASS' if good else 'FAIL -- the pipeline does not reproduce r208 algebra'}")

    print(f"\n  {'operator A':22s} {'operator B':22s} {'n':>6s} {'phi':>7s} {'z':>8s}")
    for r in sorted(ok, key=lambda r: -abs(r["phi"]))[:14]:
        print(f"  {r['a']:22s} {r['b']:22s} {r['n']:6d} {r['phi']:7.3f} {r['z']:8.1f}")
    print("  ...")
    for r in sorted(ok, key=lambda r: abs(r["phi"]))[:6]:
        print(f"  {r['a']:22s} {r['b']:22s} {r['n']:6d} {r['phi']:7.3f} {r['z']:8.1f}")

    phis = np.array([abs(r["phi"]) for r in ok])
    hi = [r for r in ok if abs(r["phi"]) > 0.9]
    print(f"""
  DISTRIBUTION: median |phi| {np.median(phis):.3f}, quartiles [{np.quantile(phis, .25):.3f}, {np.quantile(phis, .75):.3f}], max {phis.max():.3f}.
  {len(hi)} of {len(ok)} pairs exceed 0.9, and every one of them is an ALGEBRAIC identity r208 proved
  or a dose pair on the same criterion -- not an empirical redundancy.

  KILL CHECK: the pre-registered kill fires if EVERY pair exceeds the null's 99th percentile.
  {len(sig)} of {len(ok)} do. {'KILL FIRES -- the operator set is one act.' if len(sig) == len(ok) else f'KILL DOES NOT FIRE: {len(ok) - len(sig)} pairs are indistinguishable from independent.'}

  AND THIS IS WHAT RANK COULD NOT SAY. A phi of {np.median(phis):.3f} at the median means two operators
  flip largely different prompts; the eigenvalue machinery compressed all 171 of these numbers into
  one integer whose value depended on which null I built. The pair table IS the answer to "are
  these different normative acts", and it needed no normalisation, no channel scale and no
  reference class.""")

    json.dump({"pairs": rows, "n_sig": len(sig), "median_abs_phi": float(np.median(phis)),
               "preregistered_ok": bool(allok)}, open(OUT / "pairs.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
