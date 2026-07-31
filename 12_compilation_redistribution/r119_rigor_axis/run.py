"""r119 -- the RIGOR AXIS. The standards are not a checklist; they are another dimension of the grid.

Ivan, 2026-07-30, correcting my reading: the campaign is

    sacrifice x bearer x definition x baseline x threshold x null x scale x RIGOR-CRITERION x loop

so each of the ~55 criteria does not get ticked -- it VARIES the whole 628-cell grid, and a finding is
characterised by the number of criteria it survives. The deliverable is therefore not a verdict but a
SURVIVAL DEPTH per cell, and a register in which every criterion is either implemented, applicable but
unrun, or STRUCTURALLY IMPOSSIBLE ON THIS SITE with the reason stated.

WHY A REGISTER AND NOT A CLAIM OF COMPLIANCE
--------------------------------------------
Six of the criteria cannot be met on CoVal at all -- one dataset, no model in the loop, no timestamps.
Writing "cross-model: planned" would be the same defect this project has retracted fourteen times: an
unavailability claim stated without checking, except in the flattering direction. Each impossible
criterion is named with what would be required, so the register doubles as the specification for the
next site.

WHAT A VARIATION IS
-------------------
A rigor criterion is IMPLEMENTED when it re-runs the grid under a defensible alternative and the two
survivor sets can be compared. Not every criterion has that form: `preregisterable` is a property of
the protocol, `falsification-oriented` of the reporting. Those are marked PROPERTY, not run, and not
counted as survived -- a criterion you cannot fail is not a test.

SURVIVAL DEPTH is deliberately unweighted. A cell surviving 10 of 13 variations is reported as 10/13;
no criterion is worth more than another here, because weighting them would be a taste judgement
smuggled into a count.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "12_compilation_redistribution/r118_sacrifice_factorial"))

from covalx.stamp import stamp  # noqa: E402

R118 = _ROOT / "12_compilation_redistribution/r118_sacrifice_factorial"
BH_Q = 0.05

# ---------------------------------------------------------------- the register
# status: RUN (varies the grid, comparable), PROPERTY (of protocol/reporting, cannot be "survived"),
#         IMPOSSIBLE (structurally unavailable on this release, with what it would require)
REGISTER = [
    ("full-scale",                  "RUN",      "15,202 cells / 80,521 decisions, the whole release"),
    ("large-sample",                "RUN",      "same"),
    ("multi-seed",                  "RUN",      "4 independent seeds of the whole grid"),
    ("seed-robust",                 "RUN",      "survivor-set Jaccard across those seeds"),
    ("multi-run",                   "RUN",      "same four runs"),
    ("independently-replicated",    "IMPOSSIBLE", "requires a second team or a second release"),
    ("effect-size-powered",         "RUN",      "planted-effect sweep gives an MDE per bearer"),
    ("uncertainty-quantified",      "RUN",      "permutation p per cell, 20,000 draws"),
    ("distribution-complete",       "RUN",      "full percentile profile, never a mean alone"),
    ("hierarchically-modelled",     "RUN",      "per-unit means vs shrunk (James-Stein) means"),
    ("multiplicity-controlled",     "PROPERTY", "BH over the whole grid at once"),
    ("preregisterable",             "PROPERTY", "thresholds and kills written before the run"),
    ("confirmatory",                "RUN",      "held-out prompt half confirms the discovery half"),
    ("causally-identified",         "IMPOSSIBLE", "no intervention on the compiler exists; observational contrast only"),
    ("interventionally-validated",  "IMPOSSIBLE", "would require re-running the human protocol under a modified compiler"),
    ("counterfactually-grounded",   "RUN",      "non-compiled arms are the counterfactual rule"),
    ("mechanistically-diagnostic",  "RUN",      "the r115 purge separates geometry from mechanism"),
    ("necessity-and-sufficiency",   "RUN",      "remove the arm gap (necessity); plant it alone (sufficiency)"),
    ("dose-response",               "RUN",      "planted effect swept over a grid of sizes"),
    ("temporally-resolved",         "IMPOSSIBLE", "the release carries NO timestamps on any assessment"),
    ("control-saturated",           "RUN",      "positive, negative, sham and random-baseline per bearer"),
    ("sham-controlled",             "RUN",      "a sham compiler: same criterion COUNT, no compilation"),
    ("placebo-controlled",          "RUN",      "arm pairs where no effect should exist"),
    ("nuisance-matched",            "RUN",      "units matched on workload and own-error"),
    ("norm-matched",                "RUN",      "arms scored at identical equal weights"),
    ("compute-matched",             "RUN",      "arms matched on criterion count (rand4/first4 vs core)"),
    ("positive-control-calibrated", "RUN",      "planted effect must be recovered per bearer"),
    ("negative-control-calibrated", "RUN",      "per-bearer permutation floor"),
    ("random-baseline-calibrated",  "RUN",      "rand4 arm"),
    ("measurement-calibrated",      "RUN",      "replicate cells give the within-cell floor directly"),
    ("instrument-validated",        "RUN",      "each statistic shown to move on a planted effect"),
    ("construct-validated",         "IMPOSSIBLE", "no external criterion for 'good response' exists here"),
    ("criterion-validated",         "IMPOSSIBLE", "same: no gold standard outside the raters themselves"),
    ("measurement-error-aware",     "RUN",      "deconvolution using the replicate variance"),
    ("noise-floor-calibrated",      "RUN",      "95 replicated cells, 99 df"),
    ("judge-audited",               "RUN",      "satisfaction tensor held fixed; arms differ only in criteria"),
    ("leakage-audited",             "RUN",      "oracle selected on odd raters, evaluated on even"),
    ("contamination-audited",       "RUN",      "selection and evaluation rater sets are disjoint by construction"),
    ("shortcut-resistant",          "RUN",      "length and label shortcuts tested as separate bearers"),
    ("artifact-resistant",          "RUN",      "every cell computed raw AND purged of the r115 line"),
    ("counterbalanced",             "RUN",      "label permutation within prompt"),
    ("position-randomized",         "IMPOSSIBLE", "no presentation-order field exists to randomise against"),
    ("label-randomized",            "RUN",      "the U5 null"),
    ("benchmark-degeneracy-audited","RUN",      "contest bins expose where both arms sit at chance"),
    ("specification-robust",        "RUN",      "this IS a specification curve: 628 specifications"),
    ("implementation-robust",       "RUN",      "statistics recomputed by a second implementation"),
    ("estimator-robust",            "RUN",      "6 statistics per bearer"),
    ("metric-robust",               "RUN",      "pairwise discordance vs top-1 disagreement"),
    ("prompt-robust",               "RUN",      "leave-one-prompt-fold-out, 5 folds"),
    ("perturbation-robust",         "RUN",      "satisfaction scores jittered"),
    ("cross-model",                 "IMPOSSIBLE", "no model in the loop for this measurement"),
    ("cross-scale",                 "RUN",      "grid re-run at 50% and 25% subsamples"),
    ("cross-architecture",          "IMPOSSIBLE", "same as cross-model"),
    ("cross-dataset",               "IMPOSSIBLE", "one release; DICES is published on this estimand, PRISM cannot form it"),
    ("cross-task",                  "IMPOSSIBLE", "one task"),
    ("cross-domain",                "IMPOSSIBLE", "one domain"),
    ("out-of-distribution-tested",  "RUN",      "world-only stratum vs both-forms stratum, disjoint"),
    ("adversarially-stress-tested", "PROPERTY", "independent navigator dispatched per iteration"),
    ("falsification-oriented",      "PROPERTY", "502 of 628 cells reported as non-survivors"),
    ("hostile-peer-review-ready",   "PROPERTY", "every non-survivor and every impossible criterion named"),
]


def key(g):
    return (g["block"], g["bearer"], g["arms"], g["stat"], str(g["eps"]), g["purge"])


def survivors(obj):
    return {key(g) for g in obj["grid"] if g.get("bh") and g.get("purge")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="", help="comma-separated name=path of grid variants")
    ap.add_argument("--out", default=str(_RES / "r119_rigor_axis.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)

    base_p = R118 / "results/r118_sacrifice_factorial.json"
    if not base_p.exists():
        print(f"REFUSING: base grid {base_p} absent. Exits 2, never 0.", file=sys.stderr)
        return 2
    base = json.loads(base_p.read_text())
    base_surv = survivors(base)

    variants = {}
    for spec in filter(None, (s.strip() for s in args.variants.split(","))):
        name, _, path = spec.partition("=")
        p = Path(path)
        if p.exists():
            variants[name] = survivors(json.loads(p.read_text()))
        else:
            print(f"  variant {name}: file absent, NOT counted as survived", file=sys.stderr)

    n_run = sum(1 for _n, s, _w in REGISTER if s == "RUN")
    n_prop = sum(1 for _n, s, _w in REGISTER if s == "PROPERTY")
    n_imp = sum(1 for _n, s, _w in REGISTER if s == "IMPOSSIBLE")
    print(f"RIGOR REGISTER: {len(REGISTER)} criteria -- {n_run} varying the grid, {n_prop} properties "
          f"of protocol or reporting, {n_imp} STRUCTURALLY IMPOSSIBLE on this release")
    print(f"\n  IMPOSSIBLE, named with what each would require:")
    for n, s, why in REGISTER:
        if s == "IMPOSSIBLE":
            print(f"    {n:<28} {why}")

    print(f"\n  VARIATIONS ACTUALLY EXECUTED: {len(variants)} of the {n_run} that could vary the grid")
    if not variants:
        print("  REFUSING to report a survival depth: no variant grids supplied, so depth would be "
              "1/1 for every cell -- a compliance claim dressed as a measurement.", file=sys.stderr)
        Path(args.out).write_text(json.dumps(
            {"register": [{"criterion": n, "status": s, "note": w} for n, s, w in REGISTER],
             "n_run": n_run, "n_property": n_prop, "n_impossible": n_imp,
             "n_variants_executed": 0, "base_survivors": len(base_surv),
             "refused": "no variant grids supplied", **stamp(__file__)}, indent=1, sort_keys=True))
        return 2

    depth = {c: 0 for c in base_surv}
    per_variant = {}
    for name, sv in variants.items():
        keep = base_surv & sv
        per_variant[name] = {"variant_survivors": len(sv), "kept_from_base": len(keep),
                             "jaccard": len(keep) / max(len(base_surv | sv), 1)}
        for c in keep:
            depth[c] += 1
    print(f"\n  {'variation':<22}{'its survivors':>15}{'kept from base':>16}{'Jaccard':>10}")
    for n, v in sorted(per_variant.items(), key=lambda kv: -kv[1]["jaccard"]):
        print(f"  {n:<22}{v['variant_survivors']:>15}{v['kept_from_base']:>16}{v['jaccard']:>10.4f}")

    dist = defaultdict(int)
    for c, d in depth.items():
        dist[d] += 1
    V = len(variants)
    print(f"\n  SURVIVAL DEPTH over {V} executed variations (unweighted, deliberately):")
    for d in range(V, -1, -1):
        if dist[d]:
            print(f"    depth {d}/{V}: {dist[d]:>4} cells")
    full = [c for c, d in depth.items() if d == V]
    print(f"\n  {len(full)} of {len(base_surv)} base survivors hold at FULL depth {V}/{V}")
    by_bearer = defaultdict(int)
    for c in full:
        by_bearer[c[1]] += 1
    for b, n in sorted(by_bearer.items(), key=lambda kv: -kv[1]):
        print(f"    {b:<14}{n:>4}")

    conclusion = (
        f"The rigor criteria are an AXIS, not a checklist: {len(REGISTER)} criteria, of which {n_run} "
        f"can vary the grid, {n_prop} are properties of protocol or reporting and cannot be survived, "
        f"and {n_imp} are STRUCTURALLY IMPOSSIBLE on this release -- one dataset, no model in the "
        f"loop, no timestamps, no presentation-order field, no external criterion. {len(variants)} "
        f"variations were executed and every base survivor carries a survival depth over them. "
        f"{len(full)} of {len(base_surv)} purged base survivors hold at full depth {V}/{V}, "
        f"concentrated on {', '.join(f'{b} ({n})' for b, n in sorted(by_bearer.items(), key=lambda kv: -kv[1]))}. "
        f"Depth is unweighted on purpose: weighting the criteria would smuggle a taste judgement into "
        f"a count."
    )
    print(f"\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"register": [{"criterion": n, "status": s, "note": w} for n, s, w in REGISTER],
         "n_run": n_run, "n_property": n_prop, "n_impossible": n_imp,
         "n_variants_executed": len(variants), "per_variant": per_variant,
         "base_survivors": len(base_surv), "depth_distribution": dict(dist),
         "full_depth_cells": [list(c) for c in sorted(full)],
         "full_depth_by_bearer": dict(by_bearer),
         "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
