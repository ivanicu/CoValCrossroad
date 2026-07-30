"""r93 -- does r90's clustering result transfer to the H_fresh design, and on what?

CLAIM CARD
----------
Claim      PREREGISTRATION.md states H_fresh's power "clustered on prompt" and never
           says why prompt is the right unit. r90 supplies the reason -- on the release,
           prompt clustering dominates and the two-way crossed interval is only 2.0-8.3%
           wider than prompt-only.
Estimand   whether r90's MECHANISM holds under H_fresh's design, and which design
           parameter it depends on.
Target
observed?  YES for the mechanism, which is combinatorial: r90's annotator-clustered
           interval is narrow because an annotator bootstrap still covers ~every
           prompt, so it barely resamples the prompt axis. Coverage is exactly
           computable from the design. NOT observed: the variance components H_fresh
           will actually have, which need its data.
Alternative
worlds     K CROSSING-BOUND  coverage depends on prompts-per-rater k. Then the
                             preregistration must FIX k, because r90's justification
                             holds only above some crossing level.
           F FLOOR-BOUND     coverage is driven by raters-per-prompt, already fixed at
                             >=8. Then the justification transfers at EVERY k, k is
                             free to choose on other grounds, and the preregistration
                             gains a citation rather than a constraint.
Intervention
           none. Exact combinatorics over the design grid.
Null       DEGENERATE CONTROL -- at raters-per-prompt = 1 the miss probability must
           equal the classic 1/e, since a prompt then survives exactly when its single
           rater is drawn. If the formula does not reproduce that, it is wrong.

WHY THIS IS THE STEP
--------------------
Item 7 is preregistration. r90 established that this package's intervals should cluster
on prompt, but a result measured on the RELEASE does not automatically govern a study
with a different shape: the release has ~16 raters per prompt and each annotator spans
~16 prompts. H_fresh fixes >=8 raters per prompt and leaves prompts-per-rater
UNSPECIFIED. If the justification depends on that free parameter, the preregistration
is quietly relying on a value nobody chose.

THE ARITHMETIC, STATED BEFORE THE RUN
--------------------------------------
Draw n raters with replacement. A given rater is missed with probability (1-1/n)^n -> 1/e.
A prompt is lost only if ALL of its raters are missed, so

    P(prompt lost) = [(1-1/n)^n]^RPP  ~  e^-RPP

RPP is raters-per-prompt. k enters only through n, and n cancels in the limit. So the
prediction BEFORE computing is F FLOOR-BOUND -- and the round is written to be able to
return K, by sweeping k over two orders of magnitude.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

R90 = _ROOT / "09_form_donor_draw_and_unit/r90_resampling_unit/results/r90_resampling_unit.json"
PROMPTS = 60          # PREREGISTRATION.md: the r38 frame
RPP = 8               # PREREGISTRATION.md: ">=8 raters per prompt"
KS = (1, 2, 4, 8, 15, 30, 60)


def coverage(n_raters: int, rpp: int) -> float:
    """expected share of prompts surviving a with-replacement draw of n raters."""
    return float(1.0 - ((1.0 - 1.0 / n_raters) ** n_raters) ** rpp)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r93_clustering_unit_transfers.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R90.exists():
        raise SystemExit("REFUSING: r90's artifact is absent. This round transfers r90's result and "
                         "must read it rather than restate it from memory.")
    r90 = json.load(open(R90))

    # ---- degenerate control ------------------------------------------------------
    big = 100_000
    got, want = coverage(big, 1), 1.0 - 1.0 / np.e
    if abs(got - want) > 1e-4:
        raise SystemExit(f"REFUSING: at raters-per-prompt=1 coverage is {got:.6f}, but a prompt then "
                         f"survives exactly when its single rater is drawn, so it must be "
                         f"1-1/e={want:.6f}. The formula is wrong.")
    print(f"degenerate control: RPP=1 gives {got:.6f} == 1-1/e = {want:.6f}  OK\n")

    links = PROMPTS * RPP
    grid = {}
    print(f"H_fresh: {PROMPTS} prompts x {RPP} raters/prompt = {links} rater-prompt links")
    print(f"  {'k (prompts/rater)':>18} {'n raters':>9} {'prompt coverage':>18}")
    for k in KS:
        n = max(1, links // k)
        c = coverage(n, RPP)
        grid[k] = {"n_raters": n, "coverage": c}
        print(f"  {k:>18} {n:>9} {c:>17.4%}")

    cov = [v["coverage"] for v in grid.values()]
    spread = max(cov) - min(cov)
    floor_bound = bool(spread < 0.01)
    world = "F FLOOR-BOUND" if floor_bound else "K CROSSING-BOUND"
    print(f"\n  coverage spread across k spanning {min(KS)}-{max(KS)}: {spread:.2%}")

    # what WOULD make it crossing-bound: a lower raters-per-prompt floor
    sens = {r: coverage(max(1, links // 8), r) for r in (1, 2, 3, 5, 8)}
    print(f"  sensitivity to the floor that actually drives it (at k=8):")
    for r, c in sens.items():
        print(f"    raters/prompt {r} -> coverage {c:.2%}")

    verdict = (
        f"{world}. PREREGISTRATION.md states H_fresh's power 'clustered on prompt' without saying why "
        f"prompt is the right unit; r90 supplies the reason, having measured on the release that "
        f"prompt clustering dominates and that the two-way crossed interval is only "
        f"{(r90['twoway_over_prompt']['attribution'] - 1):.1%} wider than prompt-only on attribution and "
        f"{(r90['twoway_over_prompt']['agreement'] - 1):.1%} on agreement. But r90 measured a study with "
        f"~16 raters per prompt and annotators spanning ~16 prompts, while H_fresh fixes >={RPP} raters "
        f"per prompt and leaves PROMPTS-PER-RATER unspecified -- so the question is whether the "
        f"justification silently depends on a parameter nobody chose. It does not. r90's mechanism is "
        f"that an annotator bootstrap still covers ~every prompt and therefore barely resamples the "
        f"prompt axis, and a prompt is lost only when ALL its raters are missed: P = [(1-1/n)^n]^RPP ~ "
        f"e^-RPP. Across k from {min(KS)} to {max(KS)} -- two orders of magnitude of crossing -- coverage "
        f"moves by {spread:.2%}, from {min(cov):.4%} to {max(cov):.4%}. "
        f"SO THE BINDING PARAMETER IS RATERS-PER-PROMPT, WHICH IS ALREADY FIXED AT >={RPP}, AND NOT THE "
        f"CROSSING. The consequence for item 7 is a freedom rather than a constraint: prompts-per-rater "
        f"may be chosen on fatigue, recruitment cost and order-effect grounds, and clustering on prompt "
        f"stays justified at whatever value is picked. THE SENSITIVITY, so the claim is bounded rather "
        f"than absolute: at k=8 the coverage falls to "
        + ", ".join(f"{c:.1%} at {r} raters/prompt" for r, c in sens.items() if r <= 3)
        + f" -- so a design that dropped the floor to 1 or 2 raters per prompt WOULD become "
        f"crossing-sensitive, and the >={RPP} floor is doing the work. DEGENERATE CONTROL: at one rater "
        f"per prompt the formula returns 1-1/e exactly, since a prompt then survives precisely when its "
        f"single rater is drawn; the round refuses to run otherwise. SCOPE, and it is the limit that "
        f"matters: this transfers r90's MECHANISM, which is combinatorial and design-determined. It does "
        f"NOT transfer r90's variance components -- whether prompt clustering dominates in H_fresh's "
        f"actual data is measurable only from H_fresh's actual data."
    )

    doc = {
        "prompts": PROMPTS, "raters_per_prompt": RPP, "links": links,
        "grid": {str(k): v for k, v in grid.items()},
        "coverage_spread_across_k": float(spread),
        "floor_sensitivity_at_k8": {str(r): c for r, c in sens.items()},
        "degenerate_control": {"rpp_1_coverage": got, "expected_1_minus_1_over_e": float(want)},
        "r90_twoway_over_prompt": r90["twoway_over_prompt"],
        "world": world,
        "outcome_variable_scope": (
            "Expected share of prompts surviving a with-replacement annotator draw, computed exactly "
            "from the design. No data, no judge, no model."),
        "scope": (
            "Transfers r90's MECHANISM, which is combinatorial. It does not transfer r90's variance "
            "components: whether prompt clustering dominates in H_fresh's data is measurable only from "
            "H_fresh's data, and this round does not claim it will."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
