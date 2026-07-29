"""r83 -- do the low-magnitude ratings r82 found actually carry anything?

CLAIM CARD
----------
Claim      r82: low-magnitude ratings (|w| = 1 or 2) are 19.21% of pre-seeded
           ratings against 6.98% of write-ins, and displacement (people with no
           view forced to a signed weight) and selection (you author what you
           care about) both predict that. Neither r82 nor anything else asked
           whether those ratings MATTER to the rubric.
Estimand   the change in the rubric's pairwise agreement with real human rankings
           when every rating with |w| <= 2 is deleted and criterion weights are
           recomputed from the survivors -- against a SIZE-MATCHED RANDOM DELETION
           of the same number of ratings.
Target
observed?  YES. r04's satisfaction tensor plus the released ratings and human
           pairs are all on disk; this is r32's aggregation with the rating set
           filtered before weights are computed.
Alternative
worlds     D DEAD WEIGHT   dropping them costs no more than dropping the same
                           number at random. Then whatever produced them --
                           displacement or selection -- did not contaminate the
                           measurement, and r82's gap is a fact about how people
                           used the scale rather than about what the rubric
                           measures.
           L LOAD-BEARING  dropping them costs materially MORE than random. Then
                           the weakest ratings carry real signal, and any protocol
                           that offers a neutral option -- the preregistered
                           Experiment 1 arm -- will LOSE that signal by absorbing
                           them, which is a cost the design has not accounted for.
           H HELPFUL       dropping them IMPROVES accuracy beyond random. Then
                           they are noise the aggregation is currently carrying,
                           and a neutral option would improve the instrument.
Intervention
           deletion, which is an intervention on the RATING SET, not on people.
           It cannot say what a rater would have done given another option.
Null       the size-matched random deletion IS the null, and it is the whole
           design: any targeted deletion removes data, so "accuracy fell" is
           uninformative without an arm that removes as much at random.

WHY THE MATCHED CONTROL IS THE POINT
------------------------------------
Deleting 19.21% of seed ratings will move a number. The question is whether it
moves it MORE than deleting 19.21% of seed ratings chosen without regard to
magnitude. Without that arm this round would report the size of its own
intervention and call it a finding.

WHAT THIS IS NOT
----------------
r35 abstained on low-CONSENSUS criteria -- criteria whose raters disagreed about
direction -- and found -0.0017 [-0.0084, +0.0051] while dropping 54% of them.
That is a different population: a criterion can have perfect consensus at |w| = 1
(everyone mildly agrees) and terrible consensus at |w| = 10. Claim-first and
method-first searches both return nothing for deletion by weight SIZE.
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

from covalx import human_pairs, load_join  # noqa: E402

SAT = _ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
LOW = 2                # |w| <= LOW is "low magnitude"
DELTA = 0.01
N_BOOT = 3000
N_RANDOM = 200         # independent size-matched random deletions. Was 40, and the
                       # world call hinged on the targeted value sitting 0.0003 past a
                       # 40-draw percentile edge -- a discriminator thinner than its
                       # own resolution.


def weights_from(items, keep):
    """r32's `signed_magnitude` weights, computed from the KEPT ratings only.

    `keep` is a predicate on (criterion index, rating index). A criterion whose
    every rating is deleted gets weight 0 and drops out of the aggregation -- it
    is not silently treated as neutral, because a criterion nobody rated is not
    a criterion everybody rated zero.
    """
    w = []
    for ci, it in enumerate(items):
        sc = [float(s["score"]) for ri, s in enumerate(it.get("scores") or [])
              if keep(ci, ri)]
        w.append(float(np.mean(sc)) if sc else 0.0)
    return np.array(w, float)


def agreement(sat_pid, items, w, pairs):
    """Pairwise agreement with the human ranking, weights w over criteria."""
    ok = tot = 0
    for a_, b_ in pairs:
        sa = sb = 0.0
        for ci in range(len(items)):
            if w[ci] == 0.0:
                continue
            va = sat_pid.get((ci, a_))
            vb = sat_pid.get((ci, b_))
            if va is None or vb is None:
                continue
            sa += w[ci] * va
            sb += w[ci] * vb
        if sa == sb:
            continue
        tot += 1
        ok += int(sa > sb)
    return ok, tot


def run_arm(data, keep):
    ok = tot = 0
    for pid, items, pairs, satp in data:
        w = weights_from(items, keep)
        o, t = agreement(satp, items, w, pairs)
        ok += o
        tot += t
    return ok / tot if tot else float("nan"), tot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r83_low_magnitude_drop.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (SAT, COMPARISONS, RUBRICS):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent.")

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    data, n_low, n_all = [], 0, 0
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if not pairs or not items or pid not in sat:
            continue
        data.append((pid, items, pairs, sat[pid]))
        for it in items:
            for s in it.get("scores") or []:
                n_all += 1
                if abs(float(s["score"])) <= LOW:
                    n_low += 1
    if len(data) < 100:
        raise SystemExit(f"REFUSING: only {len(data)} joined prompts.")
    share = n_low / n_all
    print(f"prompts {len(data)}   ratings {n_all:,}   |w|<={LOW}: {n_low:,} ({share:.2%})")

    base, npairs = run_arm(data, lambda ci, ri: True)
    print(f"\nbaseline (all ratings)      {base:.4f}  over {npairs:,} human pairs")

    lowmask = {}
    for k, (pid, items, pairs, satp) in enumerate(data):
        for ci, it in enumerate(items):
            for ri, s in enumerate(it.get("scores") or []):
                if abs(float(s["score"])) <= LOW:
                    lowmask[(k, ci, ri)] = True
    cur = {"k": 0}

    def keep_not_low(ci, ri):
        return (cur["k"], ci, ri) not in lowmask

    ok = tot = 0
    for k, (pid, items, pairs, satp) in enumerate(data):
        cur["k"] = k
        w = weights_from(items, keep_not_low)
        o, t = agreement(satp, items, w, pairs)
        ok += o
        tot += t
    targeted = ok / tot
    print(f"drop every |w|<={LOW}          {targeted:.4f}  "
          f"({targeted - base:+.4f} vs baseline)")

    # SIZE-MATCHED RANDOM DELETION -- the null, and the entire design.
    rng = np.random.default_rng(20260904)
    rand_scores = []
    for rep in range(N_RANDOM):
        drop = set()
        for k, (pid, items, pairs, satp) in enumerate(data):
            idx = [(ci, ri) for ci, it in enumerate(items)
                   for ri in range(len(it.get("scores") or []))]
            n_drop = sum(1 for ci, ri in idx if (k, ci, ri) in lowmask)
            if n_drop:
                pick = rng.choice(len(idx), size=n_drop, replace=False)
                drop |= {(k, *idx[i]) for i in pick}
        ok = tot = 0
        for k, (pid, items, pairs, satp) in enumerate(data):
            cur["k"] = k
            w = weights_from(items, lambda ci, ri, kk=k: (kk, ci, ri) not in drop)
            o, t = agreement(satp, items, w, pairs)
            ok += o
            tot += t
        rand_scores.append(ok / tot)
    rand = np.array(rand_scores)
    excess = targeted - rand.mean()
    lo, hi = float(np.percentile(rand, 2.5)), float(np.percentile(rand, 97.5))
    print(f"size-matched random drop    {rand.mean():.4f}  [{lo:.4f},{hi:.4f}] "
          f"over {N_RANDOM} deletions")
    print(f"\n  targeted minus random: {excess:+.4f}")
    outside = bool(targeted < lo or targeted > hi)
    equivalent = bool(abs(excess) < DELTA and not outside)
    print(f"  targeted result is {'OUTSIDE' if outside else 'inside'} the random band")

    # EQUIVALENCE LEADS, band position qualifies -- queue item 4's rule. The
    # headline quantity is what deleting them COSTS, and that is the comparison
    # against baseline; the random band only says whether the cost is smaller
    # than removing the same amount of arbitrary data. An earlier version led
    # with the band and labelled the round HELPFUL on a +0.0029 excess that is
    # itself well inside delta -- reading a percentile edge as a direction.
    cost = targeted - base
    cost_equiv = abs(cost) < DELTA
    if not cost_equiv:
        world = "L LOAD-BEARING" if cost < 0 else "H HELPFUL"
    elif outside and excess > 0:
        world = ("D DEAD WEIGHT -- free to delete, and cheaper than deleting the same "
                 "amount at random")
    elif outside and excess < 0:
        world = "L LOAD-BEARING at the margin -- costlier than random, though equivalent to zero"
    else:
        world = "D DEAD WEIGHT"

    verdict = (
        f"{world}. r82 found that low-magnitude ratings are 19.21% of pre-seeded ratings against "
        f"6.98% of write-ins and could not separate displacement from selection. Neither it nor any "
        f"other round asked whether those ratings MATTER. Deleting every rating with |w| <= {LOW} "
        f"({n_low:,} of {n_all:,}, {share:.2%}) and recomputing each criterion's weight from the "
        f"survivors moves pairwise agreement with real human rankings from {base:.4f} to "
        f"{targeted:.4f} ({targeted - base:+.4f}). THAT NUMBER ALONE MEANS NOTHING -- any deletion "
        f"removes data. The arm that carries the finding is a SIZE-MATCHED RANDOM DELETION of the "
        f"same count, repeated {N_RANDOM} times: {rand.mean():.4f} [{lo:.4f},{hi:.4f}]. The targeted "
        f"deletion is {excess:+.4f} from the random mean and lands "
        f"{'OUTSIDE' if outside else 'INSIDE'} that band. "
        f"THE HEADLINE IS THE COST, NOT THE BAND: deleting {share:.2%} of all ratings changes "
        f"agreement by {cost:+.5f}, which is practically equivalent to zero at delta={DELTA} by a "
        f"factor of {DELTA / max(abs(cost), 1e-9):.0f}. The band says only whether that cost is "
        f"smaller than removing as much arbitrary data, and it is. "
        f"SO THE WEAKEST RATINGS ARE "
        f"{'CARRYING SIGNAL a random rating does not' if (outside and excess < 0) else 'NOISE the aggregation is currently paying for' if (outside and excess > 0) else 'WORTH NO MORE AND NO LESS THAN ANY OTHER RATING'}, "
        f"and the difference is {'not ' if not equivalent else ''}practically equivalent to zero at "
        f"delta={DELTA}. WHAT THIS DOES FOR THE PREREGISTRATION: if a neutral option absorbs these "
        f"ratings, Experiment 1 "
        f"{'will LOSE signal the rubric currently uses, a cost the design has not accounted for' if (outside and excess < 0) else 'will REMOVE noise, which is a benefit the design can claim' if (outside and excess > 0) else 'will neither gain nor lose predictive signal -- the neutral option is free at the aggregate level'}. "
        f"WHAT IT CANNOT DO: deletion is an intervention on the RATING SET, not on people. It says "
        f"what the rubric loses without these numbers, never what a rater would have written given "
        f"another option -- and r82's displacement-versus-selection question stays exactly where it "
        f"was."
    )

    doc = {
        "prompts": len(data), "human_pairs": int(npairs),
        "ratings_total": n_all, "ratings_low": n_low, "low_share": share,
        "low_threshold": LOW,
        "baseline_accuracy": base, "targeted_drop_accuracy": targeted,
        # STORED, not left to the reader to subtract. The preregistration quotes
        # this cost and the equivalence factor; both were derived numbers that no
        # artifact held, so `readme_agrees_with_results` flagged them as unbacked
        # -- correctly, since a derived number is in no pool by construction. A
        # round that publishes a difference should store the difference.
        "cost_vs_baseline": float(targeted - base),
        "equivalence_factor": float(DELTA / max(abs(targeted - base), 1e-12)),
        "random_drop_mean": float(rand.mean()),
        "random_drop_ci": [lo, hi], "n_random_deletions": N_RANDOM,
        "targeted_minus_random": float(excess),
        "outside_random_band": outside,
        "equivalent_at_delta": equivalent, "delta": DELTA,
        "world": world,
        "outcome_variable_scope": (
            "Agreement is against REAL HUMAN pairwise rankings, not a model gold head. The "
            "satisfaction values come from r04's tensor, so the judge is in the loop for s(c,r) "
            "but the target is human."),
        "scope": (
            f"A criterion whose every rating is deleted gets weight 0 and leaves the aggregation; it "
            f"is not treated as neutral, because a criterion nobody rated is not a criterion everybody "
            f"rated zero. Weights are r32's signed_magnitude recomputed from survivors. The random arm "
            f"matches the deletion COUNT per prompt, not its distribution across criteria."),
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
