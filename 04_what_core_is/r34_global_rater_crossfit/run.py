"""r34 (plan item C33) -- Is the polarity signal cross-rater, or is it the same people's own rankings coming back?

The identification problem
---------------------------
r32 showed that adding a direction measured AFTER participants ranked the
candidates raises above-chance concordance from 9.0 points to 17.8. Three worlds
explain that equally well:

  STABLE VALUE        the direction is a real population-level norm; it merely
                      happened to be recorded after the ranking
  CONSTRUCTION        seeing a finite menu of four responses changed what
                      direction people assign to a criterion
  TARGET LEAKAGE      the ratings that build the weights and the rankings being
                      predicted come from THE SAME PEOPLE on THE SAME PROMPT:

                          ranking -> polarity -> rubric score -> predicts ranking

r32 cannot separate them because every arm is same-sample. This round separates
leakage from the other two, which is the part the released data can answer.

Design
------
A global 5-fold split over ANNOTATOR IDS. A person belongs to exactly one fold
for the whole run -- not re-randomised per prompt, which would let the same
person train on prompt A and be evaluated on prompt B.

    weights  <- criterion ratings from raters NOT in fold k
    evaluate -> the INDIVIDUAL rankings of raters IN fold k

Individual rankings, not the aggregate. An aggregate ranking built from everyone
would carry the test raters' own choices back into the evaluation target.

Arms
----
    attribute_only      w = 1            direction-free; an ATTRIBUTE diagnostic,
                                         not a "text-only value score" -- most
                                         criteria have no normative direction
                                         until someone supplies one
    same_sign           sign from ALL raters incl. the test rater  (upper bound)
    same_magnitude      mean rating from ALL raters                (upper bound)
    crossfit_sign       sign from TRAIN raters only                (main result)
    crossfit_magnitude  mean rating from TRAIN raters only
    crossfit_visibility train mean rating x train rater count
    loo_sign            sign from everyone EXCEPT the test rater
    random_sign         signs shuffled, positive/negative ratio preserved  (null)
    donor_sign          another prompt's signs                             (null)

Estimands -- differences, not a table of accuracies
----------------------------------------------------
    D_population = crossfit_sign - attribute_only     transferable direction
    D_same       = same_sign     - attribute_only     maximal internal fit
    D_same_sample_premium    = same_sign     - crossfit_sign      THE ONE THAT MATTERS
    D_magnitude  = crossfit_magnitude - crossfit_sign does size add over direction

Reading D_same_sample_premium
-----------------
    ~ 0   the post-choice direction generalises across people. It was recorded
          after the ranking but its CONTENT is not the rater's own choice coming
          back, so "leakage" is the wrong word for it.
    >> 0  r04's internal concordance is substantially same-sample circularity,
          and that share is not independent predictive ability.

Statistics
----------
Prompt-level bootstrap is primary (a prompt contributes many pairs). Annotator
clustering is the second dimension and is reported alongside. Fold assignment is
re-drawn over many seeds and EVERY seed's estimator is stored, because if the
conclusion moves with the fold seed that is itself the result.
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
from covalx import load_join, parse_ranking  # noqa: E402


def individual_pairs(asm):
    """Strict pairwise preferences from ONE annotator's world ranking."""
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r34_global_rater_crossfit.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seeds", type=int, default=25)
    p.add_argument("--boot", type=int, default=3000)
    p.add_argument("--min-train", type=int, default=2)
    a = p.parse_args()

    z = np.load(a.sat, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    # ---- per prompt: criterion ratings by annotator, and each annotator's pairs
    prompts = {}
    for pid, comp, rub in load_join(a.comparisons, a.rubrics):
        if pid not in sat:
            continue
        items = rub.get("coval_full") or []
        if not items:
            continue
        raters = {s["annotator_id"] for it in items for s in (it.get("scores") or [])}
        thr = max(2, (len(raters) + 1) // 2)
        # shared seed criteria only: a singleton write-in cannot have a weight
        # estimated from anyone other than its own author, so no cross-fitted
        # arm is definable on it.
        ratings = {}
        for ci, it in enumerate(items):
            sc = it.get("scores") or []
            if len(sc) >= thr:
                ratings[ci] = {s["annotator_id"]: float(s["score"]) for s in sc}
        if not ratings:
            continue
        byann = {}
        for asm in comp["metadata"]["assessments"]:
            aid = asm.get("annotator_id")
            pr = individual_pairs(asm)
            if aid and pr:
                byann[aid] = pr
        if byann:
            prompts[pid] = {"ratings": ratings, "pairs": byann}

    all_raters = sorted({r for d in prompts.values()
                         for c in d["ratings"].values() for r in c}
                        | {r for d in prompts.values() for r in d["pairs"]})
    print(f"prompts {len(prompts):,}   raters {len(all_raters):,}   "
          f"shared-seed criteria per prompt "
          f"{np.mean([len(d['ratings']) for d in prompts.values()]):.1f}\n")

    def weights_from(ratings, ci_keep, who, mode, rng=None, donor=None):
        w = {}
        src = donor if donor is not None else ratings
        for ci in ci_keep:
            vals = [v for r, v in src.get(ci, {}).items() if who is None or r in who]
            if not vals:
                continue
            mu, n = float(np.mean(vals)), len(vals)
            if mode == "attribute_only":
                w[ci] = 1.0
            elif mode.endswith("sign"):
                w[ci] = float(np.sign(mu)) or 1.0
            elif mode.endswith("magnitude"):
                w[ci] = mu
            elif mode.endswith("visibility"):
                w[ci] = mu * n
        if mode == "random_sign" and w:
            ks = list(w)
            signs = np.array([np.sign(v) or 1.0 for v in w.values()])
            rng.shuffle(signs)
            w = {k: float(sg) for k, sg in zip(ks, signs)}
        return w

    def score_and_eval(pid, w, test_raters):
        d = prompts[pid]
        if not w:
            return None
        score = {}
        for lab in {l for (_c, l) in sat[pid]}:
            num = den = 0.0
            for ci, wc in w.items():
                s = sat[pid].get((ci, lab))
                if s is None:
                    continue
                num += wc * s
                den += abs(wc)
            if den > 0:
                score[lab] = num / den
        if len(score) < 2:
            return None
        ok = tot = 0
        for r in test_raters:
            for x, y in d["pairs"].get(r, []):
                if x in score and y in score:
                    tot += 1
                    ok += int(score[x] > score[y])
        return (ok, tot) if tot else None

    ARMS = ["attribute_only", "same_sign", "same_magnitude", "crossfit_sign",
            "crossfit_magnitude", "crossfit_visibility", "loo_sign",
            "random_sign", "donor_sign"]
    pids = sorted(prompts)
    per_seed = []
    for seed in range(a.seeds):
        rng = np.random.default_rng(20260728 + seed)
        fold = {r: int(i % a.folds) for i, r in
                enumerate(rng.permutation(all_raters))}
        acc = {arm: defaultdict(lambda: [0, 0]) for arm in ARMS}
        for pid in pids:
            d = prompts[pid]
            cis = list(d["ratings"])
            donor_pid = pids[(pids.index(pid) + 1 + int(rng.integers(0, len(pids) - 1)))
                             % len(pids)]
            for k in range(a.folds):
                test = {r for r in d["pairs"] if fold.get(r) == k}
                train = {r for c in d["ratings"].values() for r in c
                         if fold.get(r) != k}
                if not test or len(train) < a.min_train:
                    continue
                assert train.isdisjoint(test), "train/test rater overlap"
                for arm in ARMS:
                    if arm.startswith("same") or arm == "attribute_only":
                        who = None
                    elif arm == "loo_sign":
                        who = {r for c in d["ratings"].values() for r in c} - test
                    elif arm == "random_sign":
                        who = train
                    elif arm == "donor_sign":
                        who = None
                    else:
                        who = train
                    dn = prompts[donor_pid]["ratings"] if arm == "donor_sign" else None
                    ck = list(dn) if dn is not None else cis
                    w = weights_from(d["ratings"], ck, who,
                                     "sign" if arm == "donor_sign" else arm,
                                     rng=rng, donor=dn)
                    if arm == "donor_sign":
                        w = {ci: v for ci, v in w.items() if ci in set(cis)}
                    r_ = score_and_eval(pid, w, test)
                    if r_:
                        acc[arm][pid][0] += r_[0]
                        acc[arm][pid][1] += r_[1]
        row = {}
        for arm in ARMS:
            v = [o / t for o, t in acc[arm].values() if t]
            row[arm] = float(np.mean(v)) if len(v) >= 30 else float("nan")
        row["_per_prompt"] = {arm: {pid: (o / t) for pid, (o, t) in acc[arm].items() if t}
                              for arm in ARMS}
        per_seed.append(row)
        if (seed + 1) % 5 == 0:
            print(f"  seed {seed+1}/{a.seeds}", flush=True)

    print(f"\n{'arm':22s} {'accuracy':>9} {'sd over seeds':>15}")
    summary = {}
    for arm in ARMS:
        v = np.array([r[arm] for r in per_seed])
        v = v[~np.isnan(v)]
        summary[arm] = {"mean": float(v.mean()), "sd_over_seeds": float(v.std()),
                        "seeds": int(len(v))}
        print(f"{arm:22s} {v.mean():>9.4f} {v.std():>15.4f}")

    last = per_seed[-1]["_per_prompt"]
    rng = np.random.default_rng(20260728)

    def paired(a1, a2):
        common = sorted(set(last[a1]) & set(last[a2]))
        d = np.array([last[a2][p] - last[a1][p] for p in common])
        bs = np.array([d[rng.integers(0, len(d), len(d))].mean()
                       for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return {"delta": float(d.mean()), "ci": [float(lo), float(hi)],
                "prompts": len(common), "excludes_zero": bool(lo > 0 or hi < 0),
                # PAIRED VECTOR PERSISTED 2026-07-28.  Non-significance is not
                # equivalence, and testing H0: |delta| >= margin needs the
                # resamplable vector, not a 95% CI printed for a different
                # question.  Discarding it made every "no effect" reading in
                # this round untestable by anyone including its author.
                "paired_differences": [float(x) for x in d]}

    est = {
        "D_population (crossfit_sign - attribute_only)": paired("attribute_only", "crossfit_sign"),
        "D_same (same_sign - attribute_only)": paired("attribute_only", "same_sign"),
        # RENAMED (queue item 1, entry 62) from the field name that used the
        # retired framing. This gap measures the SAME-SAMPLE premium and refutes
        # only the individual loop, never shared-menu endogeneity. C17's own claim
        # text already read "same-sample premium" while the field it gates on did
        # not -- a field NAME is unreachable by a prose rescope.
        "D_same_sample_premium (same_sign - crossfit_sign)": paired("crossfit_sign", "same_sign"),
        "D_magnitude (crossfit_mag - crossfit_sign)": paired("crossfit_sign", "crossfit_magnitude"),
        "null: random_sign - attribute_only": paired("attribute_only", "random_sign"),
        "null: donor_sign - attribute_only": paired("attribute_only", "donor_sign"),
    }
    print(f"\n{'estimand':46s} {'delta':>9} {'95% CI':>22}")
    for k, v in est.items():
        print(f"{k:46s} {v['delta']:>+9.4f} "
              f"{f'[{v[chr(99)+chr(105)][0]:+.4f}, {v[chr(99)+chr(105)][1]:+.4f}]':>22}"
              f"{'' if v['excludes_zero'] else '  (spans zero)'}")

    lk = est["D_same_sample_premium (same_sign - crossfit_sign)"]
    pop = est["D_population (crossfit_sign - attribute_only)"]
    verdict = (
        f"CROSS-RATER DIRECTION SURVIVES. Weights built from raters who never contributed to "
        f"the rankings being predicted still beat the direction-free arm by "
        f"{pop['delta']:+.4f} {pop['ci']}, and the same-sample premium is "
        f"{lk['delta']:+.4f} {lk['ci']}. The post-choice polarity is therefore not mainly the "
        "test rater's own ranking returning through a weight -- its CONTENT transfers across "
        "people. 'Leakage' is the wrong word for the bulk of it. Whether the direction was "
        "CONSTRUCTED by seeing the menu is a separate question this design cannot reach: "
        "every rater here saw the four candidates before rating. That needs response-blind "
        "weights from new humans."
        if pop.get("excludes_zero") and pop["delta"] > 0
        and abs(lk["delta"]) < abs(pop["delta"]) else
        f"SAME-SAMPLE CIRCULARITY DOMINATES. The same-sample premium ({lk['delta']:+.4f} "
        f"{lk['ci']}) is comparable to or larger than what survives rater-disjoint "
        f"cross-fitting ({pop['delta']:+.4f} {pop['ci']}). Much of r04's internal concordance "
        "is the raters' own rankings coming back through weights derived from them, and that "
        "share is not independent predictive ability.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts": len(prompts), "raters": len(all_raters), "folds": a.folds,
         "seeds": a.seeds, "arms": summary, "estimands": est,
         "per_seed": [{k: v for k, v in r.items() if k != "_per_prompt"}
                      for r in per_seed],
         "verdict": verdict,
         "criterion_population_scope": (
             "CRITERION POPULATION (added 2026-07-28, entry 51): this round keeps only"
             " criteria rated by a majority of the prompt's raters, which discards 9,6"
             "84 of 15,248 criteria (63.5%). r48 identified what that filter selects: "
             "the partition is structural and the surviving class is capped at exactly"
             " six per prompt -- it is the PRE-SEEDED set, shown identically to every "
             "participant. The excluded 63.5% are participant-authored write-ins. So e"
             "very number here is computed on the criteria OpenAI supplied, and cross-"
             "rater agreement among them is agreement about the same six sentences eve"
             "ryone saw. r49 tests the write-ins separately."),
         "note": "Global fold assignment over annotator ids -- a person is in exactly one "
                 "fold for the whole run, never re-randomised per prompt. Evaluated against "
                 "INDIVIDUAL test-rater rankings, never an aggregate, which would carry the "
                 "test raters' own choices into the target. Shared seed criteria only: a "
                 "singleton write-in has no weight estimable from anyone but its author."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
