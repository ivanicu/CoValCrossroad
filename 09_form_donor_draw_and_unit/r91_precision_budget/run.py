"""r91 -- what n would actually reach delta=0.01? The preregistration needs a number.

CLAIM CARD
----------
Claim      queue item 4 fixes a practical margin of delta=0.01. Three consecutive
           rounds could not reach it and fell back to an "answerable margin":
           r86 at 0.026, r87 at 0.0231, r90's two-way crossed interval.
Estimand   for each of the package's live contrasts, the n at which the interval
           half-width would equal delta=0.01 -- and whether that n is collectable.
Target
observed?  YES, and it is arithmetic on measured quantities, not a new measurement.
           Every input is a half-width this package already published.
Alternative
worlds     F FEASIBLE     delta=0.01 is reachable at an n the human protocol could
                          plausibly collect. Then 0.01 is the right margin to
                          preregister and item 7 should size to it.
           I INFEASIBLE   delta=0.01 needs an n far beyond plausible collection.
                          Then 0.01 was the wrong margin to fix in advance, and the
                          preregistration should commit to the margin the design can
                          actually deliver rather than one it will always miss.
Intervention
           none. half-width scales as 1/sqrt(n) for a mean-like statistic over iid
           clusters, so n_required = n_current * (half_current / delta)^2.
Null       (i) POSITIVE CONTROL, and it is r89: the 1/sqrt(n) law is not assumed here,
           it was VERIFIED empirically across three panel sizes (300, 500, 968) with a
           worst deviation of 11.5% inside a 20% band declared in advance;
           (ii) the identity must return n_current when delta equals half_current --
           a degenerate check that catches an inverted exponent.

WHY THIS IS THE STEP
--------------------
The three counterfactuals need human data, so the only sanctioned work is preparation
-- and item 7 is the last unfrozen queue item: freeze C38's prompts and PREREGISTER
the human experiments. A preregistration that fixes delta=0.01 without knowing the n
that delivers it is preregistering a margin the study will miss, which is how a
non-result becomes indistinguishable from an underpowered one. This round turns three
separate "not answerable at 0.01" statements into one design requirement.

It is also only possible now. The required inputs are the variance components measured
in the last three rounds -- r88's donor draw, r89's scaling law, r90's crossed
decomposition. Before those, this arithmetic had nothing to stand on.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
1/sqrt(n) extrapolation assumes new prompts are EXCHANGEABLE with current ones -- same
between-prompt variance. This release is ordered by collection form and the two forms
differ, so prompts collected under a third protocol could carry different variance and
the required n would be wrong. CONTROL IN THE SAME ITERATION: the requirement is
computed separately from each form's own interval where available, and the spread
between them is reported as the sensitivity rather than a single authoritative n.

SECOND, AND IT IS A DESIGN LEVER NOT A CAVEAT
----------------------------------------------
Part of every attribution interval is DONOR-DRAW noise (r88: sd 0.0055 at n=968), and
that component does NOT shrink by collecting more prompts alone if the protocol keeps
using a single donor draw. It shrinks by sqrt(m) if the protocol AVERAGES over m draws
-- which costs compute, not data. So the required n depends on a protocol choice, and
both branches are reported: single-draw and donor-averaged.

SCOPE OF THE EXTRAPOLATION, STATED BEFORE THE NUMBERS
------------------------------------------------------
r89 verified the scaling over 300-968, a range of 3.2x. Any requirement landing beyond
~3100 prompts is an extrapolation past the verified range and is labelled as such in
the output rather than presented with the same confidence as one inside it.
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

DELTA = 0.01
VERIFIED_MAX_N = 968 * 3.2      # r89 verified the law over 300-968; 3.2x is its range

R86 = _ROOT / "09_form_donor_draw_and_unit/r86_attribution_by_form/results/r86_attribution_by_form.json"
R87 = _ROOT / "09_form_donor_draw_and_unit/r87_criterion_count_channel/results/r87_criterion_count_channel.json"
R88 = _ROOT / "09_form_donor_draw_and_unit/r88_donor_draw_variance/results/r88_donor_draw_variance.json"
R89 = _ROOT / "09_form_donor_draw_and_unit/r89_floor_draw_at_panel_size/results/r89_floor_draw_at_panel_size.json"
R90 = _ROOT / "09_form_donor_draw_and_unit/r90_resampling_unit/results/r90_resampling_unit.json"


def need(half: float, n: float, delta: float = DELTA) -> float:
    """n at which the half-width reaches delta, under half ~ 1/sqrt(n)."""
    return float(n * (half / delta) ** 2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r91_precision_budget.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    for f in (R86, R87, R88, R89, R90):
        if not f.exists():
            raise SystemExit(f"REFUSING: {f.name} absent. Every input must be a PUBLISHED "
                             f"half-width from this package, never a value typed in here.")
    r86, r87 = json.load(open(R86)), json.load(open(R87))
    r88, r89, r90 = json.load(open(R88)), json.load(open(R89)), json.load(open(R90))

    # ---- degenerate control: the identity must be an identity --------------------
    probe = need(0.0123, 968, delta=0.0123)
    if abs(probe - 968) > 1e-6:
        raise SystemExit(f"REFUSING: need() returns {probe} when delta equals the current "
                         f"half-width; it must return n. The exponent is inverted.")
    print(f"degenerate control: need(half, n, delta=half) = {probe:.1f} == n  OK")
    print(f"positive control:   the 1/sqrt(n) law is VERIFIED, not assumed -- r89 worst "
          f"deviation {r89['sqrt_n_worst_deviation']:.1%} across 300/500/968\n")

    # ---- the live contrasts, each with its OWN published half-width --------------
    CONTRASTS = [
        ("agreement with human rankings (whole join)",
         r90["designs"]["prompt"]["agreement_half"], r90["n_prompts"], "single quantity"),
        ("agreement, two-way crossed",
         r90["twoway_crossed_half"]["agreement"], r90["n_prompts"], "single quantity"),
        ("attribution (whole join)",
         r90["designs"]["prompt"]["attribution_half"], r90["n_prompts"], "single quantity"),
        ("attribution, two-way crossed",
         r90["twoway_crossed_half"]["attribution"], r90["n_prompts"], "single quantity"),
        ("long-form vs short-form attribution gap",
         r86["answerable_margin"], r86["n_long"], "DIFFERENCE, limited by the smaller arm"),
        ("criterion-count channel bound",
         r87["count_channel_bound"], r87["n_scored_all_arms"], "DIFFERENCE"),
    ]
    rows = []
    print(f"  {'contrast':<44} {'half':>7} {'n now':>7} {'n for d=0.01':>13}  kind")
    for name, half, n, kind in CONTRASTS:
        nr = need(half, n)
        beyond = bool(nr > VERIFIED_MAX_N)
        rows.append({"contrast": name, "half_width": float(half), "n_current": int(n),
                     "n_required": nr, "multiple": nr / n, "kind": kind,
                     "beyond_verified_range": beyond})
        print(f"  {name:<44} {half:7.4f} {n:7d} {nr:13.0f}  {kind}"
              + ("  [EXTRAPOLATED past r89's verified range]" if beyond else ""))

    singles = [r for r in rows if r["kind"] == "single quantity"]
    diffs = [r for r in rows if r["kind"] != "single quantity"]
    worst_single = max(r["n_required"] for r in singles)
    worst_diff = max(r["n_required"] for r in diffs)
    print(f"\n  single quantities reach delta=0.01 by n={worst_single:.0f} "
          f"({worst_single / r90['n_prompts']:.1f}x the current join)")
    print(f"  DIFFERENCES need n={worst_diff:.0f} ({worst_diff / r90['n_prompts']:.1f}x) "
          f"-- a difference costs ~4x a level, because it carries two intervals")

    # ---- the donor-averaging lever ----------------------------------------------
    donor_sd = r88["attribution_sd"]
    att_half = r90["designs"]["prompt"]["attribution_half"]
    donor_share = (donor_sd ** 2) / (att_half ** 2)
    resid = max(att_half ** 2 - donor_sd ** 2, 0.0)
    lever = {}
    for m in (1, 10, 100):
        h = float(np.sqrt(resid + donor_sd ** 2 / m))
        lever[m] = {"half": h, "n_required": need(h, r90["n_prompts"])}
    print(f"\n  DONOR-AVERAGING LEVER (costs compute, not data)")
    print(f"    the donor draw is {donor_share:.0%} of the attribution interval's variance")
    for m, v in lever.items():
        print(f"    m={m:<4} draws -> half {v['half']:.4f}, n for delta=0.01 = {v['n_required']:.0f}")
    saved = lever[1]["n_required"] - lever[100]["n_required"]

    # ---- form sensitivity: is the requirement stable across protocols? -----------
    form = {}
    for k, ci_k, n_k in (("long", "attribution_long_ci", "n_long"),
                         ("short", "attribution_short_ci", "n_short")):
        h = (r86[ci_k][1] - r86[ci_k][0]) / 2
        form[k] = {"half": float(h), "n": int(r86[n_k]), "n_required": need(h, r86[n_k])}
    spread = max(v["n_required"] for v in form.values()) / min(v["n_required"] for v in form.values())
    print(f"\n  FORM SENSITIVITY (the confound written before the run)")
    for k, v in form.items():
        print(f"    {k:<6} half {v['half']:.4f} at n={v['n']:<4} -> n for delta=0.01 = {v['n_required']:.0f}")
    print(f"    spread between forms {spread:.2f}x -> new prompts are "
          f"{'NOT clearly exchangeable; the requirement is protocol-dependent' if spread > 1.5 else 'close enough that the requirement is stable across the two protocols observed'}")

    # The threshold was fixed before the run, but it landed within 3% of the result, and
    # a world label decided by a 3% margin is a coin flip wearing a name. So the margin
    # is reported and a knife-edge outcome is LABELLED as one rather than resolved.
    THRESH = 5000
    feasible = bool(worst_diff <= THRESH)
    margin = abs(worst_diff - THRESH) / THRESH
    knife = bool(margin < 0.20)
    base = "F FEASIBLE" if feasible else "I INFEASIBLE"
    world = (f"{base} -- KNIFE-EDGE, {margin:.0%} from the threshold: the RATIOS are the "
             f"finding, not the side of {THRESH}") if knife else base
    print(f"\n  threshold {THRESH} fixed before the run; result {worst_diff:.0f} sits "
          f"{margin:.0%} from it -> "
          f"{'KNIFE-EDGE, the label is not the finding' if knife else 'clear of it'}")

    verdict = (
        f"{world}. Queue item 4 fixes delta=0.01, and three consecutive rounds could not reach it -- r86 "
        f"fell back to 0.026, r87 to {r87['count_channel_bound']:.4f}, r90 reported a two-way crossed "
        f"width instead. Item 7 asks for a PREREGISTRATION, and preregistering a margin without knowing "
        f"the n that delivers it is how a non-result becomes indistinguishable from an underpowered one. "
        f"Under half ~ 1/sqrt(n), which r89 VERIFIED rather than assumed (worst deviation "
        f"{r89['sqrt_n_worst_deviation']:.1%} across three panel sizes): SINGLE QUANTITIES reach "
        f"delta=0.01 by n={worst_single:.0f}, only {worst_single / r90['n_prompts']:.1f}x the current "
        f"join -- agreement is essentially there already. DIFFERENCES need n={worst_diff:.0f}, "
        f"{worst_diff / r90['n_prompts']:.1f}x, because a difference carries two intervals and therefore "
        f"costs about 4x a level. THE FEASIBILITY LABEL IS KNIFE-EDGE AND MUST NOT BE QUOTED ALONE: "
        f"the threshold of {THRESH} was fixed before the run but the result landed {margin:.0%} from it, "
        f"so which side it falls on is arbitrary. The durable findings are the RATIOS -- "
        f"{worst_single / r90['n_prompts']:.1f}x the current join for a level, "
        f"{worst_diff / r90['n_prompts']:.1f}x for a difference -- and the fact that agreement's interval "
        f"is ALREADY finer than 0.01 at the current n, which is a precision fact and NOT an equivalence "
        f"claim. THE DESIGN LEVER: the donor draw is {donor_share:.0%} of the "
        f"attribution interval's variance and does NOT shrink by collecting prompts if the protocol keeps "
        f"a single draw. Averaging over 100 draws costs compute rather than data and cuts the requirement "
        f"from {lever[1]['n_required']:.0f} to {lever[100]['n_required']:.0f} prompts, a saving of "
        f"{saved:.0f}. THE CONFOUND, WRITTEN BEFORE THE RUN: 1/sqrt(n) assumes new prompts are "
        f"exchangeable, and this release is form-ordered with two protocols that differ. Computed per "
        f"form, the requirement differs by {spread:.2f}x, so the extrapolation is "
        f"{'protocol-dependent and the single number above should not be quoted alone' if spread > 1.5 else 'stable across the two protocols actually observed'}. "
        f"SCOPE OF THE EXTRAPOLATION: r89 verified the law over 300-968, a range of 3.2x. Requirements "
        f"beyond n={VERIFIED_MAX_N:.0f} are extrapolations past that range and are flagged as such per "
        f"row rather than presented with equal confidence. This round measures nothing new -- every input "
        f"is a half-width already published here, and the round refuses to run if any is missing."
    )

    doc = {
        "delta": DELTA, "rows": rows,
        "worst_single_quantity_n": worst_single, "worst_difference_n": worst_diff,
        "feasibility_threshold": THRESH, "margin_from_threshold": float(margin),
        "label_is_knife_edge": knife,
        "ratio_single": float(worst_single / r90["n_prompts"]),
        "ratio_difference": float(worst_diff / r90["n_prompts"]),
        "current_join_n": int(r90["n_prompts"]),
        "donor_share_of_attribution_variance": float(donor_share),
        "donor_averaging_lever": lever, "prompts_saved_by_m100": float(saved),
        "form_sensitivity": form, "form_requirement_spread": float(spread),
        "verified_scaling_range_max_n": float(VERIFIED_MAX_N),
        "sqrt_n_worst_deviation_r89": r89["sqrt_n_worst_deviation"],
        "world": world,
        "outcome_variable_scope": (
            "Interval half-widths already published in this package, extrapolated under a scaling law "
            "verified in r89. No new measurement, no new data, no judge call."),
        "scope": (
            "This sizes PRECISION, not power: it says when an interval reaches +-0.01, not what effect "
            "would be detectable. It also assumes the estimator and protocol stay fixed -- a different "
            "donor construction or judge changes the half-width and therefore the requirement."),
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
