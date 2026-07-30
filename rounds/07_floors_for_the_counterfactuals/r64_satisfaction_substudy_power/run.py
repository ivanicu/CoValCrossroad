"""r64 -- sizing Experiment 2's satisfaction sub-study, and finding it needs a second arm.

CLAIM CARD
----------
Claim      the satisfaction sub-study as written can decide whether H_fresh's
           transport failure is a rubric property or a judge artifact.
Estimand   Delta_sat = human-judge satisfaction agreement on ORIGINAL
           (criterion, response) pairs MINUS the same on FRESH pairs. The n
           required to detect a Delta_sat worth acting on, swept over the base
           agreement rate, which nobody has measured.
Target
observed?  NO, and that is the finding. The release ships **no satisfaction
           labels at all** -- rebuilding them is why r04 exists -- so there is no
           human-judge agreement rate for ORIGINAL responses either. A single
           fresh-arm number would have nothing to be compared against.
Alternative
worlds     1ARM  a fresh-arm agreement rate is interpretable on its own against
                 some external standard. Requires a standard; none exists.
           2ARM  only the ORIGINAL-minus-FRESH difference is interpretable,
                 because the judge's absolute agreement with humans is unknown
                 everywhere and cancels in the difference.
Intervention
           none. A power calculation over an unmeasured base rate.
Null       n/a -- this sizes a study, it does not test a hypothesis. Its positive
           control is that a zero effect must demand infinite n and a maximal
           effect a trivial one.

WHY THIS EXISTS
---------------
`ADVERSARY_FORECAST.md` objection 4, P=0.70: the sub-study is specified as *"if
that sub-study is not run, the primary result is reported as human rankings
against a model-scored rubric"* -- **no n, no power, no sampling frame** -- so it
can be skipped and the headline merely reworded. That is a caveat wearing the
costume of a commitment, which this project has an entry (79) about.

SCOPE
-----
The base agreement rate is UNMEASURED and is swept, never assumed. The design
effect is carried over from r61's rater ICC on the same population and is a
different quantity from criterion-within-prompt clustering; it is used as an
order-of-magnitude correction and labelled as such.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

BASE_SWEEP = [0.60, 0.70, 0.80, 0.90]
DELTA_SWEEP = [0.05, 0.10, 0.15]
DEFF = 1.37          # r61, at 5 items per participant
Z_A, Z_B = 1.96, 0.84       # alpha=0.05 two-sided, power 0.80


def n_per_arm(p: float, d: float, deff: float = DEFF) -> int:
    """Pairs per arm to detect a difference d between two proportions near p."""
    p1, p2 = p, max(1e-6, min(1 - 1e-6, p - d))
    pbar = (p1 + p2) / 2
    num = (Z_A * np.sqrt(2 * pbar * (1 - pbar)) + Z_B * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return int(np.ceil(num / d ** 2 * deff))


def positive_control() -> dict:
    """A vanishing effect must demand a huge n; a large one a small n."""
    tiny = n_per_arm(0.80, 0.01)
    big = n_per_arm(0.80, 0.30)
    return {"n_for_d=0.01": tiny, "n_for_d=0.30": big,
            "all_pass": bool(tiny > 10000 and big < 100 and tiny > big)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r64_satisfaction_substudy_power.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    pc = positive_control()
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}  {pc}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: the power function is not monotone in the effect size.")

    grid = {}
    print(f"\npairs per arm (alpha=0.05, power=0.80, design effect {DEFF}):")
    print(f"{'base':>6}" + "".join(f"{'d=' + str(d):>10}" for d in DELTA_SWEEP))
    for p in BASE_SWEEP:
        row = {str(d): n_per_arm(p, d) for d in DELTA_SWEEP}
        grid[str(p)] = row
        print(f"{p:>6.2f}" + "".join(f"{row[str(d)]:>10,}" for d in DELTA_SWEEP))

    plan_p, plan_d = 0.80, 0.10
    n_plan = grid[str(plan_p)][str(plan_d)]
    total = 2 * n_plan

    verdict = (
        f"TWO ARMS OR NOTHING, AND THE SIZE IS {total:,} ADJUDICATIONS. The sub-study was specified "
        f"as a single fresh-response arm, and a single fresh-arm agreement rate has NOTHING TO BE "
        f"COMPARED AGAINST: the release ships no satisfaction labels at all -- rebuilding them is why "
        f"r04 exists -- so the judge's agreement with humans is unmeasured on ORIGINAL responses too. "
        f"The interpretable estimand is therefore Delta_sat = agreement on ORIGINAL minus agreement "
        f"on FRESH, in which the judge's unknown absolute accuracy cancels. At a base rate of "
        f"{plan_p:.2f} and a difference of {plan_d:.2f}, that needs {n_plan:,} adjudicated "
        f"(criterion, response) pairs PER ARM, {total:,} in total, at alpha=0.05 and power 0.80 with "
        f"a design effect of {DEFF} carried over from r61. THE BASE RATE IS UNMEASURED and is swept "
        f"across {BASE_SWEEP[0]:.2f}-{BASE_SWEEP[-1]:.2f}: the requirement ranges from "
        f"{min(grid[str(p)][str(plan_d)] for p in BASE_SWEEP):,} to "
        f"{max(grid[str(p)][str(plan_d)] for p in BASE_SWEEP):,} per arm across that sweep, so the "
        f"pilot must estimate it before n is fixed. INVALIDATION RULE, committed: if Delta_sat is "
        f"significantly positive AND its magnitude exceeds the observed change in the own-minus-"
        f"reference gap, the transport failure is attributable to the satisfaction layer and H_fresh's "
        f"primary result is reported UNVERIFIED for transport -- not annotated, not reworded."
    )

    doc = {
        "n_per_arm_grid": grid,
        "planning_base_rate": plan_p,
        "planning_difference": plan_d,
        "n_per_arm_planned": n_plan,
        "n_total_planned": total,
        "design_effect_from_r61": DEFF,
        "alpha": 0.05,
        "power": 0.80,
        "arms_required": 2,
        "positive_control": pc,
        "scope": ("The base agreement rate is UNMEASURED -- the release ships no satisfaction labels "
                  "-- and is swept, never assumed. The design effect is r61's rater ICC on the same "
                  "population; criterion-within-prompt clustering is a different quantity and this "
                  "is an order-of-magnitude correction, labelled as such. This round sizes a study "
                  "and tests no hypothesis."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  planned: base {plan_p:.2f}, d {plan_d:.2f} -> {n_plan:,} per arm, {total:,} total")
    print(f"  across the base sweep at d={plan_d:.2f}: "
          f"{min(grid[str(p)][str(plan_d)] for p in BASE_SWEEP):,}"
          f"-{max(grid[str(p)][str(plan_d)] for p in BASE_SWEEP):,} per arm")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
