"""r30 -- The headline as a grid, with an interval in every cell.

What this replaces
------------------
The repository's headline quantity is the PROMPT-SPECIFIC SHARE: of a rubric's
above-chance ability to predict held-out human rankings, how much comes from
criterion content written for that specific prompt, rather than from generic
response quality any rubric earns for free.

It has been reported three ways, each wrong about its own scope:

    43%        r04, one judge, one floor, no interval
    27%-67%    r19, after the floor turned out to be a CHOICE worth 2.47x --
               but computed on TWO cells whose per-prompt scores were never
               saved, so the range is a spread of point estimates with no
               interval anywhere in it
    13.6%-74%  after r22 showed the JUDGE FAMILY moves it another 2.13x,
               independently -- still point estimates

A statistics review named the defect in the second one exactly: "no prompt-level
bootstrap CI is ever computed for any of real/near/random in r10 or r19", so
"stability" and the "2.47x span" are mean +/- SD of two or three numbers with no
way to tell whether the between-configuration spread exceeds ordinary
prompt-sampling noise.

That could not be fixed after the fact, because r10 and r19 discarded their
per-prompt arrays. r22 now persists them, so it can be.

Estimator
---------
For each (judge, floor) cell, over the prompts that judge scored:

    share = [ mean(own) - mean(floor) ] / [ mean(own) - 0.5 ]

bootstrapped by RESAMPLING PROMPTS, recomputing both means on each draw. This is
a ratio of means, not a mean of ratios -- per prompt the denominator
(own_k - 0.5) is frequently near zero or negative, so a per-prompt ratio has no
finite variance and its mean is not the quantity of interest.

The grid is the deliverable. A single number here is not a property of the
dataset; it is a property of (dataset, floor donor, judge family), and the last
two are analyst choices that the source package does not report and that this
repository's own first fifteen rounds did not report either.

Cells that were never measured are printed as gaps rather than interpolated: the
farthest-donor arm exists only for the Qwen judges, from r10, so no phi cell can
be filled at that floor and the true lower and upper corners of the grid are
unobserved.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
CHANCE = 0.5


def share_ci(own, floor, rng, boot=8000):
    """Ratio of means, resampling PROMPTS jointly for numerator and denominator."""
    m = len(own)
    pt = (own.mean() - floor.mean()) / (own.mean() - CHANCE)
    draws = np.empty(boot)
    for b in range(boot):
        idx = rng.integers(0, m, m)
        o, f = own[idx], floor[idx]
        d = o.mean() - CHANCE
        draws[b] = (o.mean() - f.mean()) / d if abs(d) > 1e-9 else np.nan
    draws = draws[~np.isnan(draws)]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(pt), float(lo), float(hi), int(m)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--per-prompt", type=Path,
                   default=_ROOT / "rounds/02_attribution_under_attack/r22_cross_family/results/r22_cross_family_per_prompt.npz")
    p.add_argument("--summary", type=Path,
                   default=_ROOT / "rounds/02_attribution_under_attack/r22_cross_family/results/r22_cross_family.json")
    p.add_argument("--r19", type=Path,
                   default=_ROOT / "rounds/02_attribution_under_attack/r19_floor_choice/results/r19_floor_choice.json")
    p.add_argument("--out", type=Path, default=_RES / "r30_scope_grid.json")
    p.add_argument("--boot", type=int, default=8000)
    a = p.parse_args()

    if not a.per_prompt.exists():
        raise SystemExit(
            f"missing {a.per_prompt}\n"
            "  r22 must be re-run with the per-prompt persistence patch. Before it,\n"
            "  r22 kept only cell means and their CIs, so no interval can be put on\n"
            "  the SHARE after the fact -- the same defect that left r19's 27%-67%\n"
            "  bracket as a spread of two point estimates.")

    z = np.load(a.per_prompt)
    summ = json.loads(a.summary.read_text())
    fams = summ["judge_families"]
    judges = sorted({k.split("|")[0] for k in z.files})
    arms = sorted({k.split("|")[1] for k in z.files})
    print(f"judges: {len(judges)}   arms: {arms}   floors available: "
          f"{[x for x in arms if x != 'own']}\n")

    grid, rng = {}, np.random.default_rng(20260728)
    print(f"{'judge':24s} {'family':9s} {'floor':8s} {'share':>8} {'95% CI':>20} {'n':>5}")
    for j in judges:
        own = z[f"{j}|own"]
        for arm in arms:
            if arm == "own":
                continue
            pt, lo, hi, m = share_ci(own, z[f"{j}|{arm}"], rng, a.boot)
            grid.setdefault(j, {})[arm] = {"share": pt, "ci": [lo, hi], "prompts": m}
            print(f"{j:24s} {fams.get(j,'?'):9s} {arm:8s} {pt:>8.1%} "
                  f"{f'[{lo:.1%}, {hi:.1%}]':>20} {m:>5}")

    pts = [c["share"] for d in grid.values() for c in d.values()]
    los = [c["ci"][0] for d in grid.values() for c in d.values()]
    his = [c["ci"][1] for d in grid.values() for c in d.values()]
    span_pt = max(pts) / min(pts) if min(pts) > 0 else float("inf")

    print(f"\n  point estimates span      {min(pts):.1%} .. {max(pts):.1%}   = {span_pt:.2f}x")
    print(f"  including sampling error  {min(los):.1%} .. {max(his):.1%}")
    print(f"  -> the DEFENSIBLE statement is the second line, not the first, and not "
          f"any single number inside it.")

    # what the grid does NOT contain
    gaps = []
    if a.r19.exists():
        r19 = json.loads(a.r19.read_text())
        gaps.append(
            f"the farthest-donor floor exists only for Qwen judges (r19, share ~"
            f"{r19['prompt_specific_share']['vs_far']:.0%}); no phi cell was ever "
            f"measured at that floor, so the grid's true upper corner is unobserved")
    gaps.append("internlm2 could not be loaded, so a third family is absent entirely")
    gaps.append("every cell uses the same 300-prompt panel, so the cells are not "
                "independent of one another and the span is not a confidence "
                "statement about a population of judges")
    print("\n  NOT in this grid:")
    for g in gaps:
        print(f"    - {g}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"grid": grid, "judge_families": fams,
         "point_span": [float(min(pts)), float(max(pts))],
         "point_span_ratio": float(span_pt),
         "with_sampling_error": [float(min(los)), float(max(his))],
         "boot": a.boot, "gaps": gaps,
         "note": "replaces 43% / 27-67% / 13.6-74%, all of which were point estimates. "
                 "Ratio-of-means bootstrap resampling prompts jointly across numerator "
                 "and denominator; a per-prompt ratio is undefined because own_k - 0.5 "
                 "is often near zero. The grid is the deliverable: the share is a "
                 "property of (dataset, floor donor, judge family)."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
