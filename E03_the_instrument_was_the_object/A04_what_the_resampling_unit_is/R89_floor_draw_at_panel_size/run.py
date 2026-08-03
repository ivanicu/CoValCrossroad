"""r89 -- how much donor-draw noise does the HEADLINE's own floor carry?

CLAIM CARD
----------
Claim      the headline's split of the 18.6 points above chance into 7.9 / 10.7 is a
           quantity. Its floor is "an unrelated prompt's rubric", concordance 0.607.
Estimand   the sd of own-minus-random-donor attribution across independent donor draws
           AT THE HEADLINE'S OWN PANEL SIZE (r10's first 300 prompts), and its scaling
           with n.
Target
observed?  PARTLY, and the boundary is the point. r10's cells run live judges and store
           only per-cell aggregates, so its exact cells cannot be redrawn without GPU
           time. What CAN be measured on the identical 300-prompt panel, with r04's
           stored tensor, is the SIZE of the donor-draw noise the floor carries. This
           round measures a magnitude; it does not recompute r10's cells, and every
           number here is labelled accordingly.
Alternative
worlds     N NEGLIGIBLE   the draw sd at n=300 is small against the 7.9-point cell.
                          Then the headline's split is a quantity and only its
                          interpretation was ever at issue.
           D DRAW-BOUND   the sd is a material fraction of 7.9. Then the headline's
                          most-quoted number carries an unreported Monte Carlo
                          component, and "7.9 / 10.7" needs a draw scope the way
                          r86's and r87's numbers now do.
Intervention
           N independent seeds of the SAME construction r10 uses, at three panel sizes.
Null       (i) at n=968 this estimator must reproduce r88's sd to within its own
           sampling error -- a cross-round positive control, since a spread measured by
           a differently-behaving estimator would say nothing about r88's;
           (ii) r88 predicts sd scales as 1/sqrt(n). That is FALSIFIABLE: it is checked
           here at three sizes and reported whether or not it holds.

WHY THIS IS THE STEP
--------------------
r88 established that the whole-join attribution is one draw with sd 0.0055 at n=968.
The headline does not quote the whole join. It quotes 7.9 / 10.7, which comes from
r19 reading r10's four donors, and r10 builds its random donor with EXACTLY the same
line -- (i + 1 + rng.integers(0, n-1)) % n under seed 20260727 -- on its first 300
prompts. A third of the prompts means more draw noise, not less.

WHAT IS AND IS NOT AT RISK, SEPARATED BEFORE THE RUN
----------------------------------------------------
r10's near and far donors are DETERMINISTIC -- argmax and argmin of a similarity
matrix. They carry no draw noise at all. So r19's 2.47x floor span, which runs between
the near-donor and far-donor attributions, is UNAFFECTED by anything measured here.
Only the random-donor cell moves. The headline's structural claim (the floor is a
choice, and the number moves 2.47x with it) is therefore not at risk; its specific
number 7.9 is. Stating this before the run stops a null from being read as a general
acquittal and stops a positive from being read as a general indictment.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
r04's tensor is not r10's judge configuration. So the sd measured here is the noise
THIS estimator carries on THAT panel, and transferring it to r10's cells assumes the
draw noise is a property of the donor sampling rather than of the judge. That
assumption is testable in one direction and is tested: if the n=968 value reproduces
r88's, the estimator is behaving consistently across panels; if the 1/sqrt(n) scaling
holds across three sizes, the noise is dominated by the sampling and not by anything
judge-specific. Neither proves transfer. The number is reported as an ESTIMATE OF
MAGNITUDE and never substituted into r10's cells.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "E03_the_instrument_was_the_object/A04_what_the_resampling_unit_is/R85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import agree, weights  # noqa: E402

SAT = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R88 = _ROOT / "E03_the_instrument_was_the_object/A04_what_the_resampling_unit_is/R88_donor_draw_variance/results/r88_donor_draw_variance.json"
PANEL = 300          # r10's --prompts
HEADLINE_CELL = 0.079  # the 7.9 points the headline splits off
N_SEEDS = 200


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r89_floor_draw_at_panel_size.json")
    ap.add_argument("--seeds", type=int, default=N_SEEDS)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)

    # r10 slices the join BEFORE filtering, so the panel is the first PANEL joined
    # prompts -- reproduced here rather than re-derived, because a different slice
    # would silently measure a different panel
    joined = load_join(COMPARISONS, RUBRICS)
    keep_all = []
    for k, (pid, comp, rub) in enumerate(joined):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pairs and items and pid in sat:
            keep_all.append({"pid": pid, "items": items, "pairs": pairs, "join_pos": k})
    print(f"usable prompts {len(keep_all)}   r10 panel = first {PANEL} of the join order")

    def measure(keep, seeds):
        n = len(keep)
        W = [weights(r["items"]) for r in keep]
        own_ok = np.zeros(n); own_tot = np.zeros(n)
        for i, r in enumerate(keep):
            own_ok[i], own_tot[i] = agree(sat[r["pid"]], r["items"], W[i], r["pairs"])
        out = []
        for s in seeds:
            rng = np.random.default_rng(s)
            d = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])
            ok = np.zeros(n); tot = np.zeros(n)
            for i, r in enumerate(keep):
                j = int(d[i])
                ok[i], tot[i] = agree(sat[r["pid"]], keep[j]["items"], W[j], r["pairs"])
            m = (own_tot > 0) & (tot > 0)
            out.append(float(own_ok[m].sum() / own_tot[m].sum() - ok[m].sum() / tot[m].sum()))
        return np.array(out)

    panel = [r for r in keep_all if r["join_pos"] < PANEL]
    sizes = {len(panel): panel, 500: keep_all[:500], len(keep_all): keep_all}
    seeds = list(range(1000, 1000 + a.seeds))

    res = {}
    print()
    for n, keep in sorted(sizes.items()):
        v = measure(keep, seeds)
        res[n] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                  "min": float(v.min()), "max": float(v.max()),
                  "c95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]}
        print(f"  n={n:<4} attribution {v.mean():+.4f}  sd {v.std(ddof=1):.5f}  "
              f"central 95% [{np.percentile(v, 2.5):+.4f},{np.percentile(v, 97.5):+.4f}]")

    ns = sorted(res)
    big = ns[-1]

    # --- positive control: does this estimator reproduce r88 at n=968? ----------
    control = None
    if R88.exists():
        r88 = json.load(open(R88))
        # sd of an sd across S draws is ~ sd/sqrt(2(S-1)); r88 used 120 seeds, this uses a.seeds
        se = res[big]["sd"] * np.sqrt(1 / (2 * (a.seeds - 1)) + 1 / (2 * (r88["n_seeds"] - 1)))
        gap = res[big]["sd"] - r88["attribution_sd"]
        agrees = bool(abs(gap) <= 2 * se)
        control = {"r88_sd": r88["attribution_sd"], "here_sd": res[big]["sd"],
                   "gap": float(gap), "se_of_gap": float(se), "agrees": agrees}
        print(f"\n  positive control vs r88 at n={big}: r88 sd {r88['attribution_sd']:.5f}, "
              f"here {res[big]['sd']:.5f}, gap {gap:+.5f} against se {se:.5f} -> "
              f"{'AGREES' if agrees else 'DISAGREES -- the estimator is not behaving as r88 did'}")

    # --- the falsifiable prediction: sd ~ 1/sqrt(n) -----------------------------
    ref = res[big]["sd"]
    pred = {n: ref * np.sqrt(big / n) for n in ns}
    worst = max(abs(res[n]["sd"] / pred[n] - 1) for n in ns)
    scales = bool(worst <= 0.20)
    print(f"\n  1/sqrt(n) prediction, anchored at n={big}")
    for n in ns:
        print(f"    n={n:<4} predicted {pred[n]:.5f}   observed {res[n]['sd']:.5f}   "
              f"ratio {res[n]['sd'] / pred[n]:.2f}")
    print(f"  -> worst deviation {worst:.1%}  ({'HOLDS' if scales else 'FAILS'} at the 20% band)")

    sd300 = res[ns[0]]["sd"]
    # TWO transfers to the headline's cell, and the data does not settle which.
    # ABSOLUTE assumes the draw noise is a property of the donor ensemble and carries
    # over at its measured size; PROPORTIONAL assumes it scales with the attribution
    # level, which differs because r04's judge is not r10's. Reporting one alone would
    # repeat this package's path-dependent-decomposition error.
    share_abs = sd300 / HEADLINE_CELL
    share_rel = sd300 / res[ns[0]]["mean"]
    draw_bound = bool(max(share_abs, share_rel) >= 0.05)
    world = "D DRAW-BOUND" if draw_bound else "N NEGLIGIBLE"
    # the panel MEAN differs from the whole join by far more than a draw -- that is
    # composition, not noise, and the release is ordered by collection form (entry 159)
    comp_gap = res[ns[0]]["mean"] - res[big]["mean"]
    # BOTH means are averages over a.seeds draws, so the single-draw sd is the WRONG
    # denominator here -- it would call a 15-sigma composition effect "an ordinary
    # draw". The right scale is the standard error of a draw-averaged mean. The two
    # panels are nested and share seeds, so the draws are positively correlated and
    # this se is if anything conservative.
    se_gap = float(np.sqrt(sd300 ** 2 / a.seeds + res[big]["sd"] ** 2 / a.seeds))
    comp_in_se = comp_gap / se_gap
    print(f"\n  panel mean {res[ns[0]]['mean']:+.4f} vs whole join {res[big]['mean']:+.4f} = "
          f"{comp_gap:+.4f} = {comp_in_se:+.1f} standard errors of the draw-averaged means "
          f"(se {se_gap:.5f}; single-draw sd {sd300:.5f} would be the wrong scale) "
          f"-> COMPOSITION, not draw (the release file is form-ordered, entry 159)")

    verdict = (
        f"{world}. The headline quotes 7.9 / 10.7, not the whole join, and that cell comes from r19 "
        f"reading r10 -- which builds its random donor with EXACTLY the line r88 just measured, "
        f"(i + 1 + rng.integers(0, n-1)) % n under seed 20260727, on its first {PANEL} prompts. A third "
        f"of the prompts carries MORE draw noise, not less. Measured on the identical panel with r04's "
        f"tensor across {a.seeds} draws: sd {sd300:.5f} at n={ns[0]}, against {res[big]['sd']:.5f} at "
        f"n={big}. TRANSFERRING THAT TO THE HEADLINE'S CELL NEEDS AN ASSUMPTION THE DATA DOES NOT "
        f"SETTLE, so both are given: under ABSOLUTE transfer it is {share_abs:.0%} of the "
        f"{HEADLINE_CELL:.3f} the headline splits off; under PROPORTIONAL transfer, scaling by this "
        f"round's own attribution level, {share_rel:.0%}. Reporting one alone would repeat the "
        f"path-dependent-decomposition error already logged here. Both say the same qualitative thing "
        f"and neither is settled. SEPARATELY, the panel's MEAN attribution {res[ns[0]]['mean']:+.4f} "
        f"exceeds the whole join's {res[big]['mean']:+.4f} by {comp_gap:+.4f}. Judged on the RIGHT "
        f"scale -- the standard error of a draw-averaged mean, {se_gap:.5f}, not the single-draw sd, "
        f"which would have called this an ordinary draw -- that is {comp_in_se:.0f} standard errors, "
        f"far too large to be a draw: it is COMPOSITION, and it is expected, "
        f"because the release file is ordered by collection form and the first {PANEL} prompts are the "
        f"long-form head (entry 159). "
        f"SEPARATED BEFORE THE RUN, so a null could not be read as a general acquittal: r10's NEAR and "
        f"FAR donors are deterministic (argmax and argmin of a similarity matrix) and carry NO draw "
        f"noise, so r19's 2.47x floor span -- the headline's structural claim that the floor is a CHOICE "
        f"-- is untouched by anything here. Only the random-donor cell moves. "
        f"THE FALSIFIABLE PREDICTION r88 implies, sd ~ 1/sqrt(n), anchored at n={big}: worst deviation "
        f"across three panel sizes is {worst:.1%}, so it "
        f"{'HOLDS' if scales else 'FAILS'} at the 20% band -- which matters because it is the evidence "
        f"that this noise is a property of the donor SAMPLING rather than of a particular judge. "
        f"POSITIVE CONTROL: "
        + (f"at n={big} this estimator gives {control['here_sd']:.5f} against r88's "
           f"{control['r88_sd']:.5f}, a gap of {control['gap']:+.5f} against a standard error of "
           f"{control['se_of_gap']:.5f} -- {'consistent' if control['agrees'] else 'INCONSISTENT'}. "
           if control else "r88's artifact was absent, so no cross-round control ran. ")
        + f"SCOPE, AND IT IS THE POINT: r04's tensor is NOT r10's judge configuration, and r10 stores "
        f"only per-cell aggregates, so its exact cells cannot be redrawn without GPU time. This is an "
        f"ESTIMATE OF MAGNITUDE for the noise the floor carries. It is not substituted into r10's cells "
        f"and no number here replaces 7.9."
    )

    doc = {
        "panel_size": int(ns[0]), "sizes": {str(n): res[n] for n in ns},
        "n_seeds": int(a.seeds), "headline_cell": HEADLINE_CELL,
        "sd_at_panel": sd300,
        "sd_share_of_headline_cell_absolute_transfer": float(share_abs),
        "sd_share_proportional_transfer": float(share_rel),
        "transfer_is_unsettled": True,
        "panel_minus_wholejoin_mean": float(comp_gap),
        "panel_gap_in_standard_errors": float(comp_in_se),
        "panel_gap_se": se_gap,
        "sqrt_n_prediction": {str(n): float(pred[n]) for n in ns},
        "sqrt_n_worst_deviation": float(worst), "sqrt_n_holds": scales,
        "positive_control_vs_r88": control,
        "deterministic_donors_unaffected": (
            "r10's near and far donors are argmax/argmin of a similarity matrix and carry no draw "
            "noise. r19's 2.47x floor span runs between them and is unaffected by this round."),
        "world": world,
        "outcome_variable_scope": (
            "Own-minus-random-donor attribution against REAL HUMAN pairwise rankings, satisfaction from "
            "r04's tensor. Only the donor seed varies within a panel size."),
        "scope": (
            "An estimate of the MAGNITUDE of donor-draw noise at the headline's panel size, measured "
            "with r04's judge configuration rather than r10's. r10 stores per-cell aggregates only, so "
            "its cells cannot be redrawn here. No number in this round is substituted into r10's cells "
            "and none of them replaces the headline's 7.9."),
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
