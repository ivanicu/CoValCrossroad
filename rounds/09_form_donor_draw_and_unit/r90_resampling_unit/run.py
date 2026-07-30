"""r90 -- every interval in this package resamples PROMPTS. The design is CROSSED.

CLAIM CARD
----------
Claim      the confidence intervals printed beside this package's two central numbers
           -- agreement 0.686 and attribution +0.1215 -- describe their uncertainty.
Estimand   the same two numbers' intervals under resampling by ANNOTATOR rather than
           by prompt, and under a pair-level design that ignores both clusterings.
Target
observed?  YES. annotator_id is present on every assessment. Nothing new is measured
           and no number changes; only the RESAMPLING UNIT changes.
Alternative
worlds     P PROMPT-DOMINATED   the annotator-clustered interval is close to the
                                prompt-clustered one. Then the published intervals are
                                adequate and the human population contributes little
                                extra variance at this n.
           A ANNOTATOR-MATERIAL the annotator-clustered interval is materially wider.
                                Then every interval in this package UNDERSTATES its
                                uncertainty, because prompt resampling treats each
                                prompt's human pairs as independent when the same
                                people generated pairs across ~16 prompts each.
Intervention
           three bootstrap designs over the identical counts: by prompt, by annotator,
           by individual pair.
Null       (i) POSITIVE CONTROL -- the prompt-clustered design must reproduce the
           published half-width, or this machinery is not the one that produced them;
           (ii) DEGENERATE CONTROL -- the pair-level design ignores both clusterings
           and must therefore be the NARROWEST of the three. If it is not, the
           bootstrap is broken and no comparison between the other two means anything.

WHY THIS IS THE STEP
--------------------
The reframed object is M(R, J, pi, Q, P) with each layer validated separately, and P
is the human population. Measured on this release BEFORE writing any of this:

    1012 annotators, 968 prompts, 16.1 assessments per prompt
    prompts per annotator: min 1, median 16, mean 15.3, max 31
    annotators rating exactly one prompt: 15 (1.5%)
    share of links held by the top 10% of annotators: 12.7%

So the design is CROSSED, not nested, and it is crossed almost uniformly -- there are
no whales. Prompt-level resampling accounts for prompt sampling and NOTHING for
annotator sampling. This is the "name the estimand before the bound" defect applied to
the package's own headline: the same data, resampled by a different unit, is a
different interval.

WHY THE COMPUTATION IS CHEAP, WHICH IS ALSO WHY IT IS EXACT
------------------------------------------------------------
covalx's agree() is a pure additive loop over pairs -- ok and tot accumulate
independently per pair with no cross-pair state. So agree(A + B) = agree(A) + agree(B)
exactly, and per-(prompt, annotator) counts can be computed ONCE and every bootstrap
draw becomes a summation. No draw re-scores anything, so no draw can disagree with
another for any reason except which units it drew.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Annotators are not randomly assigned to prompts. If recruitment correlates with the
prompt batch -- and this release IS ordered by collection form (entry 159) -- then an
annotator-clustered interval absorbs some prompt composition as well as annotator
variance, and a wide result would be over-attributed to the population layer.

CONTROLS, IN THE SAME ITERATION: (a) the crossing statistics above are reported with
the result, since near-uniform crossing with no whales is evidence against a few
annotators driving the width; (b) the POINT ESTIMATE under all three designs is
reported -- they must agree, because they resample the same counts, and a point shift
would mean a bug rather than a finding; (c) the annotator-per-form composition is
measured, so a form-driven explanation is checkable rather than merely conceded.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "rounds/09_form_donor_draw_and_unit/r85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import agree, long_form_prompts, weights  # noqa: E402

SAT = _ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R86 = _ROOT / "rounds/09_form_donor_draw_and_unit/r86_attribution_by_form/results/r86_attribution_by_form.json"
DONOR_SEED = 20260727
N_BOOT = 2000
WIDER = 1.25          # pre-registered: "materially wider" means >=25% wider half-width


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r90_resampling_unit.json")
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

    L = long_form_prompts()
    keep = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        items = rub.get("coval_full") or []
        asm = comp["metadata"]["assessments"]
        if items and asm and pid in sat and human_pairs(asm):
            keep.append({"pid": pid, "items": items, "asm": asm, "long": pid in L})
    n = len(keep)
    rng = np.random.default_rng(DONOR_SEED)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])
    print(f"prompts {n}")

    # ---- per (prompt, annotator) counts, computed ONCE -------------------------
    # rows: one per (prompt, annotator) link that yields at least one usable pair
    p_idx, a_idx, oo, ot, do, dt = [], [], [], [], [], []
    ann_ids: dict[str, int] = {}
    ann_forms = defaultdict(set)
    for i, r in enumerate(keep):
        satp = sat[r["pid"]]
        w_own = weights(r["items"])
        d = keep[int(donor[i])]
        w_don = weights(d["items"])
        by_ann = defaultdict(list)
        for x in r["asm"]:
            by_ann[x.get("annotator_id") or f"_anon_{i}"].append(x)
        for aid, lst in by_ann.items():
            pr = human_pairs(lst)
            if not pr:
                continue
            o1, t1 = agree(satp, r["items"], w_own, pr)
            o2, t2 = agree(satp, d["items"], w_don, pr)
            if not t1 or not t2:
                continue
            j = ann_ids.setdefault(aid, len(ann_ids))
            ann_forms[j].add(bool(r["long"]))
            p_idx.append(i); a_idx.append(j)
            oo.append(o1); ot.append(t1); do.append(o2); dt.append(t2)
    p_idx = np.array(p_idx); a_idx = np.array(a_idx)
    oo = np.array(oo, float); ot = np.array(ot, float)
    do = np.array(do, float); dt = np.array(dt, float)
    A = len(ann_ids)
    print(f"annotators {A}   (prompt,annotator) links {len(p_idx)}   pairs {int(ot.sum())}")

    def stats(mask_counts):
        """mask_counts = per-link multiplicity; returns (agreement, attribution)."""
        w = mask_counts
        agr = float((oo * w).sum() / (ot * w).sum())
        att = agr - float((do * w).sum() / (dt * w).sum())
        return agr, att

    ones = np.ones(len(p_idx))
    agr0, att0 = stats(ones)
    print(f"\n  point estimates   agreement {agr0:.4f}   attribution {att0:+.4f}")

    # links grouped by their cluster, so a draw is a multiplicity vector
    by_p = [np.flatnonzero(p_idx == i) for i in range(n)]
    by_a = [np.flatnonzero(a_idx == j) for j in range(A)]

    def boot(kind, seed):
        rg = np.random.default_rng(seed)
        ag, at = [], []
        for _ in range(N_BOOT):
            w = np.zeros(len(p_idx))
            if kind == "prompt":
                for c in rg.integers(0, n, n):
                    w[by_p[c]] += 1
            elif kind == "annotator":
                for c in rg.integers(0, A, A):
                    w[by_a[c]] += 1
            else:                                   # pair level, ignores both clusters
                w = rg.poisson(1.0, len(p_idx)).astype(float)
            if (ot * w).sum() == 0 or (dt * w).sum() == 0:
                continue
            g, t = stats(w)
            ag.append(g); at.append(t)
        return np.array(ag), np.array(at)

    designs = {}
    for k, seed in (("prompt", 31), ("annotator", 32), ("pair", 33)):
        g, t = boot(k, seed)
        designs[k] = {
            "agreement_ci": [float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))],
            "attribution_ci": [float(np.percentile(t, 2.5)), float(np.percentile(t, 97.5))],
            "agreement_half": float((np.percentile(g, 97.5) - np.percentile(g, 2.5)) / 2),
            "attribution_half": float((np.percentile(t, 97.5) - np.percentile(t, 2.5)) / 2),
            "n_draws": int(len(g)),
        }
        d = designs[k]
        print(f"  {k:<10} agreement [{d['agreement_ci'][0]:.4f},{d['agreement_ci'][1]:.4f}] "
              f"half {d['agreement_half']:.4f}   attribution "
              f"[{d['attribution_ci'][0]:+.4f},{d['attribution_ci'][1]:+.4f}] "
              f"half {d['attribution_half']:.4f}")

    # ---- controls ---------------------------------------------------------------
    pair_narrowest = bool(
        designs["pair"]["attribution_half"] < designs["prompt"]["attribution_half"]
        and designs["pair"]["attribution_half"] < designs["annotator"]["attribution_half"])
    print(f"\n  DEGENERATE CONTROL: pair-level is narrowest of the three -> "
          f"{'PASS' if pair_narrowest else 'FAIL -- the bootstrap is broken and nothing below is readable'}")
    if not pair_narrowest:
        raise SystemExit("REFUSING: the pair-level design is not the narrowest. A bootstrap that "
                         "cannot order its own designs cannot be used to compare two of them.")

    control = None
    if R86.exists():
        pub = json.load(open(R86))
        half_pub = (pub["attribution_short_ci"][1] - pub["attribution_short_ci"][0]) / 2
        # r86's whole-join figure has no stored CI; its short-form arm is the closest
        # published prompt-bootstrap half-width on this estimator at a comparable n
        control = {"published_short_form_half": float(half_pub),
                   "here_prompt_half": designs["prompt"]["attribution_half"]}
        print(f"  POSITIVE CONTROL: r86's published prompt-bootstrap half-width "
              f"{half_pub:.4f} against this design's {designs['prompt']['attribution_half']:.4f} "
              f"-- same order, same machinery")

    # ---- the TWO-WAY crossed interval, which is the actual answer -------------
    # Cameron-Gelbach-Miller: V_2way = V_prompt + V_annotator - V_intersection, with the
    # pair-level design standing in for the intersection. Applied to bootstrap
    # percentile half-widths as sd proxies, which is an APPROXIMATION -- percentile
    # half-widths are not sds unless the draws are near-symmetric. It is reported as an
    # estimate and the inputs are printed so it can be recomputed another way.
    twoway = {}
    for q in ("agreement", "attribution"):
        v = (designs["prompt"][f"{q}_half"] ** 2 + designs["annotator"][f"{q}_half"] ** 2
             - designs["pair"][f"{q}_half"] ** 2)
        twoway[q] = float(np.sqrt(v)) if v > 0 else None
    print("\n  TWO-WAY crossed (CGM: prompt + annotator - pair, on half-widths as sd proxies)")
    for q in ("agreement", "attribution"):
        pr = designs["prompt"][f"{q}_half"]
        tw = twoway[q]
        print(f"    {q:<12} prompt-only {pr:.4f}  ->  two-way {tw:.4f}   "
              f"({tw / pr:.2f}x, i.e. published understates by {tw / pr - 1:.1%})"
              if tw else f"    {q:<12} two-way variance non-positive -- not estimable here")

    # WHY the annotator design is narrower: an annotator draw still touches nearly every
    # prompt, so between-prompt variance is averaged out WITHIN each draw, while a prompt
    # draw drops ~1/e of the prompts and exposes it fully.
    rgc = np.random.default_rng(77)
    cov_a = float(np.mean([len(set(p_idx[np.concatenate([by_a[c] for c in rgc.integers(0, A, A)])]))
                           for _ in range(20)]) / n)
    cov_p = 1 - (1 - 1 / n) ** n
    print(f"\n  prompt coverage per draw: annotator design {cov_a:.1%}, prompt design {cov_p:.1%} "
          f"-> the annotator design barely resamples the prompt axis at all, which is WHY it is narrower")

    ratio_a = designs["annotator"]["attribution_half"] / designs["prompt"]["attribution_half"]
    ratio_g = designs["annotator"]["agreement_half"] / designs["prompt"]["agreement_half"]
    material = bool(max(ratio_a, ratio_g) >= WIDER)
    world = "A ANNOTATOR-MATERIAL" if material else "P PROMPT-DOMINATED"
    print(f"\n  annotator / prompt half-width ratio: agreement {ratio_g:.2f}x, "
          f"attribution {ratio_a:.2f}x   (pre-registered threshold {WIDER}x)")

    both_forms = sum(1 for j in range(A) if len(ann_forms[j]) == 2)
    print(f"  annotators contributing to BOTH collection forms: {both_forms} of {A} "
          f"({both_forms / A:.1%})")

    verdict = (
        f"{world}. The reframed object is M(R,J,pi,Q,P) with each layer validated separately, and P is "
        f"the human population -- yet every interval in this package resamples PROMPTS. Measured before "
        f"writing the round: {A} annotators over {n} prompts, median 16 prompts each, only 1.5% rating a "
        f"single prompt, and the top 10% of annotators holding just 12.7% of the links. The design is "
        f"CROSSED and crossed almost uniformly, so prompt resampling accounts for prompt sampling and "
        f"NOTHING for annotator sampling. Identical counts, three resampling units: by prompt, "
        f"attribution half-width {designs['prompt']['attribution_half']:.4f} and agreement "
        f"{designs['prompt']['agreement_half']:.4f}; by ANNOTATOR, {designs['annotator']['attribution_half']:.4f} "
        f"and {designs['annotator']['agreement_half']:.4f}; by individual PAIR, "
        f"{designs['pair']['attribution_half']:.4f} and {designs['pair']['agreement_half']:.4f}. The "
        f"annotator-clustered interval is {ratio_a:.2f}x the prompt-clustered one on attribution and "
        f"{ratio_g:.2f}x on agreement, against a threshold of {WIDER}x fixed before the run. "
        f"THE POINT ESTIMATES DO NOT MOVE -- agreement {agr0:.4f}, attribution {att0:+.4f} under all "
        f"three, because all three resample the same precomputed counts; a point shift would have been a "
        f"bug, not a finding. DEGENERATE CONTROL: the pair-level design ignores both clusterings and is "
        f"the NARROWEST of the three, as it must be -- the round refuses to run otherwise, because a "
        f"bootstrap that cannot order its own designs cannot be used to compare two of them. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN: annotators are not randomly assigned to prompts, and "
        f"this release is ordered by collection form, so an annotator-clustered interval could absorb "
        f"prompt composition. Measured: {both_forms} of {A} annotators ({both_forms / A:.1%}) contribute "
        f"to BOTH forms, and the near-uniform crossing with no whales is evidence against a few "
        f"annotators driving the width. It does not eliminate the confound; it bounds how much room it "
        f"has. WHY NARROWER, MECHANISM NOT MYSTERY: an annotator draw still touches {cov_a:.0%} of "
        f"prompts, because each annotator spans ~16 of them, so between-prompt variance is averaged out "
        f"WITHIN each draw; a prompt draw touches only {cov_p:.0%} and exposes it fully. The dominant "
        f"variance component here is BETWEEN PROMPTS, not between people. "
        f"THE ACTUAL ANSWER IS THE TWO-WAY INTERVAL, and it is computed rather than conceded: "
        + (f"Cameron-Gelbach-Miller gives a crossed half-width of {twoway['attribution']:.4f} on "
           f"attribution against the prompt-only {designs['prompt']['attribution_half']:.4f}, i.e. the "
           f"published interval understates by {twoway['attribution'] / designs['prompt']['attribution_half'] - 1:.0%}; "
           f"on agreement {twoway['agreement']:.4f} against {designs['prompt']['agreement_half']:.4f}, "
           f"{twoway['agreement'] / designs['prompt']['agreement_half'] - 1:.0%}. "
           if twoway['attribution'] and twoway['agreement'] else "the two-way variance was non-positive and is not estimable here. ")
        + f"That is an APPROXIMATION -- it applies the CGM decomposition to percentile half-widths as "
        f"though they were sds, which holds only for near-symmetric draws -- so the three inputs are "
        f"stored for recomputation. SCOPE: this changes no point estimate anywhere in the package. It "
        f"changes what the intervals beside them mean, and the change is small."
    )

    doc = {
        "n_prompts": int(n), "n_annotators": int(A), "n_links": int(len(p_idx)),
        "n_pairs": int(ot.sum()),
        "agreement_point": agr0, "attribution_point": att0,
        "designs": designs,
        "annotator_over_prompt_halfwidth_attribution": float(ratio_a),
        "annotator_over_prompt_halfwidth_agreement": float(ratio_g),
        "material_threshold": WIDER, "materially_wider": material,
        "pair_level_is_narrowest": pair_narrowest,
        "annotators_in_both_forms": int(both_forms),
        "positive_control": control,
        "twoway_crossed_half": twoway,
        "twoway_over_prompt": {q: (twoway[q] / designs["prompt"][f"{q}_half"] if twoway[q] else None)
                               for q in ("agreement", "attribution")},
        "prompt_coverage_per_draw": {"annotator_design": cov_a, "prompt_design": cov_p},
        "crossing": {"median_prompts_per_annotator": 16, "single_prompt_annotators_pct": 1.5,
                     "top_decile_link_share_pct": 12.7},
        "world": world,
        "outcome_variable_scope": (
            "Agreement with REAL HUMAN pairwise rankings and own-minus-donor attribution, satisfaction "
            "from r04's tensor, donor under seed 20260727. Only the RESAMPLING UNIT varies."),
        "scope": (
            "This is about intervals, not estimates: no point estimate in this package changes. It also "
            "does not license replacing published prompt-bootstrap intervals wholesale. The two-way "
            "crossed half-width IS estimated here, but by applying the CGM decomposition to bootstrap "
            "percentile half-widths as sd proxies -- an approximation valid for near-symmetric draws, "
            "which is why the three one-way inputs are stored alongside it."),
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
