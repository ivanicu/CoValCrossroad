#!/usr/bin/env python3
"""R838 -- all 45 adjacent pairs measured, because the filter I built rested on an unmeasured bound.

See PREREGISTRATION.txt, committed before this ran.

ESTIMAND        for every adjacent pair in R835's 46-arm ordering: the TRUE paired MDE and the
                verdict gap > 2*MDE_true. All 45 reported. Named before the method.
⛔ WHY ALL 45   R837 measured three MDEs and I built a filter -- "gap must exceed 2 * 0.0104" --
                that skips 43. It ASSUMES MDE >= 0.0104 everywhere, unmeasured. Two arms differing
                systematically but slightly have a small sd(d), so a small MDE, and could separate
                on a small gap. R836 retracted a null resting on an unmeasured resolution; this is
                the same move one round later, in the opposite direction.
IDENTIFICATION  a recomputation from committed selections and rankings. Nothing re-judged.
WORLDS          W-FILTER-MISSED (a skipped pair separates) vs W-FILTER-WAS-SAFE.
KILL            CONDITIONAL on positive separable, negative sd exactly 0, three seeds identical.
ARTIFACT        results/r838_all_pairs.json -- per pair n, gap, sd, true MDE, R835's MDE, verdict.
"""
from __future__ import annotations
import hashlib, json, math, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
ZEFF = 1.959963984540054
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                                         # noqa: E402
SATD = ROOT / "corebench" / "results"
SEEDS = (0, 1, 2)
FILTER_BOUND = 2 * 0.0104          # the bound the rejected filter would have used


def stable(pid: str) -> int:
    return int(hashlib.sha256(pid.encode()).hexdigest()[:8], 16)


_cache: dict = {}


def per_prompt(arm: str, targets):
    if arm in _cache:
        return _cache[arm]
    sat = SC.load_sat(SATD / f"sat_{arm}.npz")
    out = {}
    for p in sat:
        if p not in targets:
            continue
        y = SC.yvec(sat[p], sorted({i for i, _ in sat[p]}))
        vals = []
        for s in SEEDS:
            rng = np.random.default_rng(1000 * s + stable(p))
            v = targets[p]
            hy = np.array(v[int(rng.integers(len(v)))][0], float)
            vals.append(float(np.mean([a == b for a, b in zip(SC.cls(y), SC.cls(hy))])))
        out[p] = float(np.mean(vals))
    _cache[arm] = out
    return out


def resolve(a: str, c: str, targets):
    pa, pc = per_prompt(a, targets), per_prompt(c, targets)
    common = sorted(set(pa) & set(pc))
    d = np.array([pa[p] - pc[p] for p in common])
    n = len(d)
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    m = ZEFF * sd / math.sqrt(n) if n else float("inf")
    return {"upper": a, "lower": c, "n": n, "gap": float(d.mean()) if n else float("nan"),
            "sd": sd, "mde": m, "separable": bool(n and abs(d.mean()) > 2 * m)}


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R838 · ALL 45 ADJACENT PAIRS, MEASURED\n")
    targets = SC.load_targets()[0]
    pos = resolve("oracle_k4", "generic", targets)
    neg = resolve("generic", "generic", targets)
    pc, nc = pos["separable"], (neg["sd"] == 0.0 and not neg["separable"])
    print(f"  POSITIVE  oracle_k4 vs generic: gap {pos['gap']:+.4f} MDE {pos['mde']:.4f}   "
          f"{'SEPARABLE   PASS' if pc else '⛔ FAIL'}")
    print(f"  NEGATIVE  generic vs itself: sd {neg['sd']:.6f}   "
          f"{'exactly 0   PASS' if nc else '⛔ FAIL'}")

    r835 = json.loads(next(A24.glob("R835_*/results/r835_external_anchor.json")).read_text())
    rows, unrunnable = [], []
    for p in r835["pairs"]:
        try:
            r = resolve(p["upper"], p["lower"], targets)
        except Exception as e:
            unrunnable.append({"upper": p["upper"], "lower": p["lower"],
                               "error": f"{type(e).__name__}: {e}"})
            continue
        r["r835_mde"] = p["mde"]
        r["would_have_been_skipped"] = abs(p["gap"]) <= FILTER_BOUND
        rows.append(r)

    sep = [r for r in rows if r["separable"]]
    missed = [r for r in sep if r["would_have_been_skipped"]]
    mdes = [r["mde"] for r in rows if r["n"]]
    print(f"\n  measured {len(rows)} pairs" + (f", {len(unrunnable)} UNRUNNABLE" if unrunnable else ""))
    print(f"  SEPARABLE at the true MDE: {len(sep)}")
    for r in sep:
        print(f"     {r['upper']:<22}{r['lower']:<22}gap {r['gap']:+.4f}  MDE {r['mde']:.4f}"
              f"  ({r['gap']/r['mde']:.1f}x)" + ("   ⚠ THE FILTER WOULD HAVE SKIPPED THIS"
                                                 if r["would_have_been_skipped"] else ""))
    print(f"\n  smallest measured MDE: {min(mdes):.4f}   "
          f"the rejected filter assumed >= 0.0104 -> "
          f"{'assumption HELD' if min(mdes) >= 0.0104 else '⛔ assumption FALSE'}")

    controls_ok = pc and nc
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; R835 keeps its bounded MDEs"
    elif missed:
        world = "W-FILTER-MISSED"
        verdict = (f"{len(missed)} pair(s) the filter would have skipped ARE separable -- an "
                   f"unmeasured lower bound is not a filter")
    else:
        world = "W-FILTER-WAS-SAFE"
        verdict = ("no skipped pair separates -- the filter was right, and it was right by luck "
                   "rather than by argument, because its bound was never measured")
    print(f"\n  VERDICT: {world} -- {verdict}\n")

    out = {"world": world, "verdict": verdict, "pairs": rows, "unrunnable": unrunnable,
           "n_separable": len(sep), "n_missed_by_filter": len(missed),
           "smallest_measured_mde": min(mdes) if mdes else None,
           "rejected_filter_bound": FILTER_BOUND,
           "controls": {"positive_separable": pc, "negative_sd_zero": nc},
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r838_all_pairs.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r838_all_pairs.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
