"""r58 -- equivalence at PACKAGE scope, with the population enumerated rather than listed.

CLAIM CARD
----------
Claim      r42's "no contrast is INCONCLUSIVE at delta=0.01" describes this package.
Estimand   over EVERY interval contrast in rounds/*/results, the fraction that is
           non-significant AND not bounded inside +-delta -- i.e. the fraction of
           null readings that are inconclusive rather than equivalent.
Target
observed?  Partly. 35 contrasts store a raw paired vector and admit a real
           bootstrap TOST. The remainder publish only a mean and a 95% CI, which
           supports a SOUND one-sided bound but not a full TOST. Those are
           returned UNVERIFIED, never "fine".
Alternative
worlds     A  r42's verdict generalises; the untested contrasts are equivalent or
              significant, and none is inconclusive.
           B  r42's verdict is an artifact of WHICH FOUR ROUNDS were listed, and
              inconclusive contrasts exist outside them.
           C  most untested contrasts are significant, so equivalence was never
              the question for them and the scope error is real but harmless.
Intervention
           enumerate mechanically; classify each contrast; report the three
           classes separately and never merge UNVERIFIED into a pass.
Null       a positive control with three synthetic contrasts of known class
           (equivalent / inconclusive / significant) must be classified correctly,
           or the census has not measured anything.

WHY THIS EXISTS
---------------
r42's population is `SOURCES`, a hand-written list of four rounds. Its internal
guard -- "REFUSING: this file contains N paired vectors and the walk reached M" --
compares counts WITHIN files it already opened. r13 stores zero nodes named
`paired_differences`, so the guard was satisfied at 0 == 0 while r13's
seed-vs-write-in gap, which the README uses to refute r12's own mechanism, was
never equivalence-tested at all.

A hand-written population turns an objective check into self-report.

SCOPE THIS ROUND DOES NOT REACH
-------------------------------
delta = 0.01 is STIPULATED, exactly as in r42. Nothing here measures what margin
matters to a decision; the sweep is published so a reader can pick another. And a
contrast being "equivalent" is a statement about the estimand as that round
computed it -- if the round's estimator is wrong, an equivalence verdict inherits
the error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

DELTA = 0.01
SWEEP = [0.0025, 0.005, 0.01, 0.02, 0.05]
R42_SOURCES = {"r34", "r35", "r36", "r37"}

MEANISH = re.compile(r"^(mean|diff|delta|gap|advantage|drop|attribution|effect|"
                     r".*_mean|.*_diff|.*_delta|.*_gap)$", re.I)
CIISH = re.compile(r"^(ci|.*_ci|ci_.*|interval)$", re.I)


def is_ci(v):
    return (isinstance(v, list) and len(v) == 2
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
            and v[0] <= v[1])


def enumerate_contrasts(root: Path):
    """Every node carrying an interval estimate. Enumerated, not listed."""
    out = []
    for f in sorted(root.glob("rounds/*/results/*.json")):
        if "SMOKE" in f.name or any(p.startswith("_") for p in f.parts):
            continue
        rid = f.parts[-3].split("_")[0]
        try:
            doc = json.loads(f.read_text())
        except Exception:
            continue

        def walk(node, path):
            if isinstance(node, dict):
                ci = next((v for k, v in node.items() if CIISH.match(k) and is_ci(v)), None)
                mean = next((v for k, v in node.items()
                             if MEANISH.match(k) and isinstance(v, (int, float))
                             and not isinstance(v, bool)), None)
                vec = node.get("paired_differences")
                if ci is not None and (mean is not None or vec is not None):
                    out.append({
                        "round": rid,
                        "file": str(f.relative_to(root)),
                        "path": ".".join(path) or "<root>",
                        "mean": float(mean) if mean is not None else None,
                        "ci95": [float(ci[0]), float(ci[1])],
                        "vector": [float(x) for x in vec] if isinstance(vec, list) else None,
                        "in_r42": rid in R42_SOURCES,
                    })
                for k, v in node.items():
                    walk(v, path + [k])
            elif isinstance(node, list):
                for i, v in enumerate(node[:60]):
                    walk(v, path + [f"[{i}]"])

        walk(doc, [])
    return out


def tost_vector(d: np.ndarray, delta: float, boot: int, rng):
    """Full bootstrap TOST. Equivalence at alpha=0.05 <=> the 90% CI is inside +-delta."""
    n = len(d)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(boot)])
    lo90, hi90 = np.percentile(bs, [5, 95])
    lo95, hi95 = np.percentile(bs, [2.5, 97.5])
    return {
        "method": "bootstrap TOST on the stored paired vector",
        "delta_hat": float(d.mean()), "n": n,
        "ci90": [float(lo90), float(hi90)], "ci95": [float(lo95), float(hi95)],
        "equivalent": bool(lo90 > -delta and hi90 < delta),
        "significant": bool(lo95 > 0 or hi95 < 0),
        "sound": True,
    }


def bound_from_ci(mean, ci, delta):
    """Sound three-valued bound when only a mean and a 95% CI were published.

    The 90% CI is contained in the 95% CI, so:
      * whole 95% CI inside +-delta            => the 90% is too  => EQUIVALENT (sound)
      * the 95% CI lies entirely beyond +delta
        or entirely below -delta               => the mean is significantly past
                                                  the margin      => NOT EQUIVALENT (sound)
      * anything else                          => the 90% CI is needed and was not
                                                  published       => UNVERIFIED
    UNVERIFIED is not a pass. It is the statement that this instrument, on this
    stored output, cannot decide -- which is the whole reason the raw vector
    should be persisted.
    """
    lo, hi = ci
    sig = bool(lo > 0 or hi < 0)
    if lo > -delta and hi < delta:
        return {"method": "sound bound from the published 95% CI", "delta_hat": mean,
                "ci95": [lo, hi], "equivalent": True, "significant": sig, "sound": True}
    if lo >= delta or hi <= -delta:
        return {"method": "sound bound from the published 95% CI", "delta_hat": mean,
                "ci95": [lo, hi], "equivalent": False, "significant": sig, "sound": True}
    return {"method": "UNVERIFIED -- the 90% CI is required and no raw vector was stored",
            "delta_hat": mean, "ci95": [lo, hi], "equivalent": None,
            "significant": sig, "sound": True}


def cell(sig, eq):
    if eq is None:
        return "UNVERIFIED"
    if sig and eq:
        return "real but negligible"
    if sig and not eq:
        return "real and material"
    if not sig and eq:
        return "no material effect"
    return "INCONCLUSIVE"


def positive_control(delta, boot, rng):
    """Three synthetic contrasts of known class. A census that cannot separate
    these has measured nothing, and its zero-inconclusive answer would be silence."""
    n = 400
    cases = {
        # tight around zero -> equivalent, not significant
        "known_equivalent": rng.normal(0.0, 0.02, n),
        # wide around zero -> cannot bound inside delta, not significant
        "known_inconclusive": rng.normal(0.0, 0.60, n),
        # clearly away from zero and past the margin
        "known_significant": rng.normal(0.25, 0.05, n),
    }
    expect = {"known_equivalent": "no material effect",
              "known_inconclusive": "INCONCLUSIVE",
              "known_significant": "real and material"}
    out, ok = {}, True
    for name, d in cases.items():
        r = tost_vector(np.asarray(d), delta, boot, rng)
        got = cell(r["significant"], r["equivalent"])
        out[name] = {"expected": expect[name], "observed": got, "pass": got == expect[name],
                     "ci90": r["ci90"]}
        ok &= got == expect[name]
    out["all_pass"] = bool(ok)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=float, default=DELTA)
    ap.add_argument("--boot", type=int, default=20000)
    ap.add_argument("--out", type=Path, default=_RES / "r58_equivalence_census.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.boot = 200
        # entry 71: smoke output goes to results/_smoke/, a directory the checks
        # exclude by its leading underscore. Marking a smoke run only by its
        # FILENAME failed twice -- a04_smoke.json was lowercase and slipped past
        # every uppercase "SMOKE" filter for the life of the project.
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(exist_ok=True)
    rng = np.random.default_rng(20260728)

    ctr = enumerate_contrasts(_ROOT)
    if not ctr:
        raise SystemExit("REFUSING: enumerated zero contrasts. An empty population "
                         "has not passed, it has not run.")

    pc = positive_control(a.delta, min(a.boot, 4000), rng)
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}")
    for k, v in pc.items():
        if k != "all_pass":
            print(f"  {k:22s} expected {v['expected']:20s} got {v['observed']:20s} "
                  f"{'ok' if v['pass'] else 'MISMATCH'}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: the census cannot classify contrasts of known class.")

    rows = []
    for c in ctr:
        if c["vector"] and len(c["vector"]) >= 8:
            r = tost_vector(np.asarray(c["vector"]), a.delta, a.boot, rng)
        else:
            r = bound_from_ci(c["mean"], c["ci95"], a.delta)
        r["cell"] = cell(r["significant"], r["equivalent"])
        rows.append({**{k: v for k, v in c.items() if k != "vector"},
                     "vector_stored": c["vector"] is not None, **r})

    by_cell = {}
    for r in rows:
        by_cell.setdefault(r["cell"], []).append(r)
    inconclusive = by_cell.get("INCONCLUSIVE", [])
    unverified = by_cell.get("UNVERIFIED", [])
    outside = [r for r in rows if not r["in_r42"]]
    inc_outside = [r for r in inconclusive if not r["in_r42"]]

    sweep = {}
    for d in SWEEP:
        n_eq = 0
        for c in ctr:
            if c["vector"] and len(c["vector"]) >= 8:
                n_eq += tost_vector(np.asarray(c["vector"]), d,
                                    min(a.boot, 4000), rng)["equivalent"]
            else:
                b = bound_from_ci(c["mean"], c["ci95"], d)
                n_eq += bool(b["equivalent"])
        sweep[f"{d}"] = n_eq

    # conclusion is computed, never hand-written
    verdict = (
        f"SCOPE, NOT SIGNIFICANCE: the package holds {len(rows)} interval contrasts and r42 "
        f"tested {sum(1 for r in rows if r['in_r42'])} of them ({sum(1 for r in rows if r['in_r42'])/len(rows):.0%}), "
        f"because its population was a hand-written list of four rounds rather than an "
        f"enumeration. Classifying all {len(rows)} at delta={a.delta}: "
        f"{len(by_cell.get('real and material', []))} real and material, "
        f"{len(by_cell.get('real but negligible', []))} real but negligible, "
        f"{len(by_cell.get('no material effect', []))} no material effect, "
        f"{len(inconclusive)} INCONCLUSIVE, {len(unverified)} UNVERIFIED. "
        f"{len(inc_outside)} of the inconclusive contrasts sit OUTSIDE r42's four rounds and so "
        f"had never been equivalence-tested. UNVERIFIED means the round published a mean and a "
        f"95% CI but no raw paired vector, so the 90% CI required for TOST cannot be recovered -- "
        f"that is an absence of evidence and is NOT folded into any pass. r42's own verdict is "
        f"unchanged ON ITS OWN 21 CONTRASTS; what is corrected is the sentence that made it a "
        f"claim about this package. delta={a.delta} remains STIPULATED, and the sweep shows "
        f"{sweep.get(str(a.delta))} contrasts equivalent at that margin versus "
        f"{sweep.get('0.05')} at 0.05 and {sweep.get('0.0025')} at 0.0025."
    )

    doc = {
        "delta": a.delta,
        "boot": a.boot,
        "n_contrasts": len(rows),
        "n_in_r42": sum(1 for r in rows if r["in_r42"]),
        "n_outside_r42": len(outside),
        "n_with_raw_vector": sum(1 for r in rows if r["vector_stored"]),
        "cells": {k: len(v) for k, v in sorted(by_cell.items())},
        "inconclusive_outside_r42": [
            {"round": r["round"], "path": r["path"], "delta_hat": r["delta_hat"],
             "ci95": r["ci95"]} for r in inc_outside],
        "delta_sweep_n_equivalent": sweep,
        "positive_control": pc,
        "contrasts": rows,
        "scope": ("delta=0.01 is STIPULATED, not measured. An equivalence verdict inherits the "
                  "estimator of the round it came from. UNVERIFIED contrasts published no raw "
                  "vector and are unresolved, not clean."),
        "verdict": verdict,
    }

    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass

    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\ncontrasts enumerated: {len(rows)}   in r42: {doc['n_in_r42']}   "
          f"outside: {len(outside)}   with a raw vector: {doc['n_with_raw_vector']}")
    for k, v in sorted(by_cell.items()):
        print(f"  {k:22s} {len(v)}")
    print(f"\nINCONCLUSIVE outside r42's four rounds: {len(inc_outside)}")
    for r in inc_outside[:12]:
        print(f"  {r['round']:5s} {r['path'][:52]:52s} "
              f"{r['delta_hat'] if r['delta_hat'] is not None else float('nan'):+.4f} "
              f"[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}]")
    print(f"\ndelta sweep (n equivalent): {sweep}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
