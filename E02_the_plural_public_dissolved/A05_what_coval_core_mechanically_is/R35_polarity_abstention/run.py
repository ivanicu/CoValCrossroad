"""r35 (plan item C34) -- Does the concordance depend on forcing weak or contested polarity into a direction?

Why this is not a robustness check
-----------------------------------
r34 established that the post-choice direction transfers across people: 92% of
the polarity gain survives rater-disjoint cross-fitting. So the direction is not
the test rater's own ranking coming back. But "transfers across people" is not
the same as "is a stable value" -- a direction can be reproducibly assigned by a
population and still be an artifact of how it was asked for.

One measured fact makes that concrete. Across all 102,147 criterion ratings in
the release, the value 0 appears EXACTLY ONCE. The scale runs -10..+10 and its
neutral point is, in practice, unavailable: every rater assigned a direction to
every criterion they saw. "This property has no general direction", "it depends",
and "I cannot say without seeing a response" have no representation in this data.

Forced-choice elicitation is known to convert weak or absent preference into
apparently stable preference. If CoVal's concordance depends on criteria whose
raters actually disagreed about direction, then part of what looks like a
population value is the instrument refusing to accept uncertainty.

Design
------
Per prompt-criterion, from the raters' signed ratings:

    p_plus = P(rating > 0)      p_minus = P(rating < 0)
    mu     = mean rating
    H      = -SUM_s p_s log p_s   over s in {-, 0, +}    (sign entropy)

Taxonomy (thresholds fixed before running):

    stable_positive   p_plus  >= 0.90
    stable_negative   p_minus >= 0.90
    leaning           0.60 <= max(p_plus, p_minus) < 0.90
    contested         max(p_plus, p_minus) < 0.60      raters split on direction

Three scoring rules over the SAME satisfaction matrix:

    forced        w = sign(mu)                     every criterion gets a direction
    confident     w = sign(mu) if max(p) >= 0.90   else the criterion ABSTAINS (w=0)
    posterior     w = p_plus - p_minus             continuous; contested shrink to 0

`confident` and `posterior` are the two ways to decline to force a direction --
one discrete, one graded. Coverage is reported for both, because an abstaining
rule that keeps 20% of criteria and matches a forced rule is a different object
from one that keeps 90%.

Everything is run under BOTH evaluation regimes, because r34 showed they differ:

    same-sample   weights from all raters, evaluated on their own rankings
    cross-fit     weights from train-fold raters, evaluated on test-fold raters'
                  INDIVIDUAL rankings

What each outcome means
-----------------------
    confident ~ forced          the forced direction on contested criteria was
                                adding nothing; the signal lives in the criteria
                                where people agree. The stronger result.
    confident << forced         concordance depends on assigning a direction where
                                raters disagreed, i.e. on the instrument's refusal
                                to accept "no direction".
    posterior > forced          contested criteria are actively harmful when
                                forced and helpful when down-weighted.
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
from covalx import load_join, parse_ranking  # noqa: E402

STABLE = 0.90
LEAN = 0.60


def individual_pairs(asm):
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


def polarity_stats(vals):
    v = np.array(vals, dtype=float)
    n = len(v)
    pp = float((v > 0).mean())
    pm = float((v < 0).mean())
    pz = float((v == 0).mean())
    H = -sum(q * np.log(q) for q in (pp, pm, pz) if q > 0)
    m = max(pp, pm)
    cls = ("stable_positive" if pp >= STABLE else
           "stable_negative" if pm >= STABLE else
           "leaning" if m >= LEAN else "contested")
    return {"n": n, "p_plus": pp, "p_minus": pm, "mean": float(v.mean()),
            "entropy": float(H), "class": cls, "confident": m >= STABLE}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r35_polarity_abstention.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--boot", type=int, default=4000)
    a = p.parse_args()

    z = np.load(a.sat, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    prompts = {}
    for pid, comp, rub in load_join(a.comparisons, a.rubrics):
        if pid not in sat:
            continue
        items = rub.get("coval_full") or []
        if not items:
            continue
        raters = {s["annotator_id"] for it in items for s in (it.get("scores") or [])}
        thr = max(2, (len(raters) + 1) // 2)
        ratings = {ci: {s["annotator_id"]: float(s["score"]) for s in (it.get("scores") or [])}
                   for ci, it in enumerate(items) if len(it.get("scores") or []) >= thr}
        if not ratings:
            continue
        byann = {}
        for asm in comp["metadata"]["assessments"]:
            aid, pr = asm.get("annotator_id"), individual_pairs(asm)
            if aid and pr:
                byann[aid] = pr
        if byann:
            prompts[pid] = {"ratings": ratings, "pairs": byann}

    # ---- the taxonomy, on all shared seed criteria -------------------------
    tax = defaultdict(int)
    ent, allstats = [], {}
    for pid, d in prompts.items():
        for ci, rr in d["ratings"].items():
            st = polarity_stats(list(rr.values()))
            allstats[(pid, ci)] = st
            tax[st["class"]] += 1
            ent.append(st["entropy"])
    total = sum(tax.values())
    print(f"shared seed criteria: {total:,}   median raters each: "
          f"{np.median([s['n'] for s in allstats.values()]):.0f}\n")
    print(f"{'polarity class':18s} {'count':>7} {'share':>8}")
    for k in ("stable_positive", "stable_negative", "leaning", "contested"):
        print(f"{k:18s} {tax[k]:>7,} {tax[k]/total:>8.1%}")
    conf_share = sum(1 for s in allstats.values() if s["confident"]) / total
    print(f"\n  criteria a 0.90-confidence rule would KEEP: {conf_share:.1%}")
    print(f"  mean sign entropy: {np.mean(ent):.4f} nats "
          f"(0 = unanimous direction, 0.69 = even split)")

    all_raters = sorted({r for d in prompts.values()
                         for c in d["ratings"].values() for r in c}
                        | {r for d in prompts.values() for r in d["pairs"]})

    def weight(pid, ci, rule, who):
        rr = prompts[pid]["ratings"][ci]
        vals = [v for r, v in rr.items() if who is None or r in who]
        if not vals:
            return 0.0
        st = polarity_stats(vals)
        if rule == "forced":
            return float(np.sign(st["mean"])) or 1.0
        if rule == "confident":
            return (float(np.sign(st["mean"])) or 1.0) if st["confident"] else 0.0
        if rule == "posterior":
            return st["p_plus"] - st["p_minus"]
        if rule == "attribute_only":
            return 1.0
        raise ValueError(rule)

    RULES = ["attribute_only", "forced", "confident", "posterior"]
    out = {}
    for regime in ("same_sample", "crossfit"):
        acc = {r: defaultdict(lambda: [0, 0]) for r in RULES}
        cov = {r: [] for r in RULES}
        for seed in range(a.seeds if regime == "crossfit" else 1):
            rng = np.random.default_rng(20260728 + seed)
            fold = ({r: int(i % a.folds) for i, r in enumerate(rng.permutation(all_raters))}
                    if regime == "crossfit" else None)
            for pid, d in prompts.items():
                ks = range(a.folds) if regime == "crossfit" else [None]
                for k in ks:
                    if k is None:
                        test, who = set(d["pairs"]), None
                    else:
                        test = {r for r in d["pairs"] if fold.get(r) == k}
                        who = {r for c in d["ratings"].values() for r in c
                               if fold.get(r) != k}
                        if not test or len(who) < 2:
                            continue
                        assert who.isdisjoint(test)
                    for rule in RULES:
                        w = {ci: weight(pid, ci, rule, who) for ci in d["ratings"]}
                        w = {ci: v for ci, v in w.items() if abs(v) > 1e-12}
                        if not w:
                            continue
                        cov[rule].append(len(w) / len(d["ratings"]))
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
                            continue
                        for r_ in test:
                            for x, y in d["pairs"].get(r_, []):
                                if x in score and y in score:
                                    acc[rule][pid][1] += 1
                                    acc[rule][pid][0] += int(score[x] > score[y])
        print(f"\n=== {regime} ===")
        print(f"{'rule':16s} {'accuracy':>9} {'coverage':>10} {'prompts':>8}")
        series = {}
        for rule in RULES:
            v = np.array([o / t for o, t in acc[rule].values() if t])
            series[rule] = {p_: o / t for p_, (o, t) in acc[rule].items() if t}
            out.setdefault(regime, {})[rule] = {
                "accuracy": float(v.mean()), "coverage": float(np.mean(cov[rule])),
                "prompts": int(len(v))}
            print(f"{rule:16s} {v.mean():>9.4f} {np.mean(cov[rule]):>10.1%} {len(v):>8}")

        rng2 = np.random.default_rng(7)

        def paired(r1, r2):
            common = sorted(set(series[r1]) & set(series[r2]))
            d_ = np.array([series[r2][p_] - series[r1][p_] for p_ in common])
            bs = np.array([d_[rng2.integers(0, len(d_), len(d_))].mean()
                           for _ in range(a.boot)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            return {"delta": float(d_.mean()), "ci": [float(lo), float(hi)],
                    "excludes_zero": bool(lo > 0 or hi < 0), "prompts": len(common),
                    # see r34 -- the abstention claim is a NULL claim, so it is
                    # exactly the kind that needs an equivalence test to mean
                    # anything, and that needs this vector.
                    "paired_differences": [float(x) for x in d_]}

        cmp_ = {"confident - forced": paired("forced", "confident"),
                "posterior - forced": paired("forced", "posterior"),
                "forced - attribute_only": paired("attribute_only", "forced")}
        out[regime]["comparisons"] = cmp_
        for k, v in cmp_.items():
            print(f"  {k:26s} {v['delta']:>+8.4f} "
                  f"[{v['ci'][0]:+.4f}, {v['ci'][1]:+.4f}]"
                  f"{'' if v['excludes_zero'] else '  (spans zero)'}")

    cf = out["crossfit"]["comparisons"]["confident - forced"]
    verdict = (
        f"ROBUST TO POST-HOC CRITERION ABSTENTION. Abstaining wherever raters split "
        f"on direction changes cross-fitted accuracy by {cf['delta']:+.4f} {cf['ci']}, "
        f"while dropping {1 - out['crossfit']['confident']['coverage']:.0%} of criteria. "
        "The signal lives where people agree, and the forced direction on the rest is "
        "not carrying the aggregate. NOT ESTABLISHED: the absence of a forced-choice "
        "effect. Dropping low-consensus criteria AFTER collection cannot simulate what "
        "a participant would have written had 'no general direction', 'depends on "
        "implementation' or 'cannot judge without seeing a response' been on the "
        "screen. Elicitation format changes the response it elicits, and that is not "
        "recoverable by filtering the responses it already produced -- testing it "
        "needs the option AT ELICITATION TIME."
        if not cf["excludes_zero"] or cf["delta"] >= 0 else
        f"CONCORDANCE DEPENDS ON FORCING A DIRECTION WHERE RATERS DISAGREED. Abstaining on "
        f"contested criteria costs {cf['delta']:+.4f} {cf['ci']}. Part of what reads as a "
        "population value direction is the elicitation refusing to accept 'no direction' -- "
        "a scale on which 0 appears once in 102,147 ratings.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"criteria": total, "taxonomy": dict(tax),
         "taxonomy_share": {k: v / total for k, v in tax.items()},
         "confident_coverage": conf_share, "mean_sign_entropy": float(np.mean(ent)),
         "regimes": out, "verdict": verdict,
         "criterion_population_scope": (
             "CRITERION POPULATION (added 2026-07-28, entry 51): this round keeps on"
             "ly criteria rated by a majority of the prompt's raters, which discards"
             " 9,684 of 15,248 criteria (63.5%). r48 identified what that filter sel"
             "ects: the partition is structural and the surviving class is capped at"
             " exactly six per prompt -- it is the PRE-SEEDED set, shown identically"
             " to every participant. The excluded 63.5% are participant-authored wri"
             "te-ins. r49 tested those separately and found they transfer BETTER acr"
             "oss raters (+0.0777 vs +0.0599, paired gap +0.0172 [+0.0034,+0.0307]),"
             " so the exclusion understates the direction rather than manufacturing "
             "it."),
         "scale_note": "The rating scale runs -10..+10 and the value 0 occurs exactly once "
                       "in 102,147 ratings, so the neutral point is effectively unavailable: "
                       "'no general direction' has no representation in this data.",
         "scope": "Evaluation is against individual rater rankings on the original candidate "
                  "set; internal concordance on the elicitation manifold (entry 36)."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
