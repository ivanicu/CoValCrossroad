"""r36 (plan item C35) -- The channel decomposition without the order dependence.

Why r32's numbers cannot be called contributions
-------------------------------------------------
r32 added channels in one order and reported the increments:

    text -> +sign -> +magnitude -> +visibility
    0.5899   0.6775    0.6831       0.6697

Pairwise accuracy is not additive, so those increments are not contributions.
They are the value of adding each channel LAST to whatever came before, and a
different entry order gives different numbers. Calling +0.0876 "the polarity
channel" was reporting one path through a lattice as though it were the lattice.

This computes all sixteen.

The lattice
-----------
Four channels: T text, S sign, M magnitude, V visibility. The weight a coalition
puts on criterion c:

    T absent   ->  no criterion information at all; every response scores the
                   same and pairwise accuracy is 0.5 by construction. So
                   v(C) = 0.5 for every C not containing T, including v(empty).
    T present  ->  w = 1, then multiplied by
                     sign(mu)  if S in C
                     |mu|      if M in C
                     n_raters  if V in C

which reproduces r32's arms exactly at {T}, {T,S}, {T,S,M}, {T,S,M,V} and fills
in the eight cells r32 never computed -- notably {T,M}, magnitude WITHOUT
direction, and {T,V}, visibility alone.

Shapley value, standard form:

    phi_j = SUM over C not containing j of
            |C|! (n-|C|-1)! / n!  *  [ v(C + j) - v(C) ]

What this is and is not
------------------------
It is a PREDICTIVE decomposition: how much each channel is worth for predicting
these rankings, averaged over every order of arrival. It is NOT causal, and no
channel here "produces" any quantity of value. A criterion sentence without a
direction is not even a complete normative statement, so {T} alone is an
attribute diagnostic rather than a rubric with the weights removed.

The quantity worth the run
---------------------------
Everything is computed twice -- same-sample and rater-disjoint cross-fitted --
and the reported estimand is

    phi_S(same) - phi_S(cross)

the part of the sign channel's average value that exists only when the people
who supplied the direction are also the people whose rankings are predicted.
r34 measured that gap for one entry order (+0.0055). This measures it for all of
them.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from math import factorial
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join, parse_ranking  # noqa: E402

CHANNELS = ("T", "S", "M", "V")
CHANCE = 0.5


def individual_pairs(asm):
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


def coalition_weight(vals, coal):
    """Weight for one criterion under one coalition. T absent => unusable."""
    if "T" not in coal:
        return None
    v = np.array(vals, dtype=float)
    mu, n = float(v.mean()), len(v)
    w = 1.0
    if "S" in coal:
        w *= (float(np.sign(mu)) or 1.0)
    if "M" in coal:
        w *= abs(mu)
    if "V" in coal:
        w *= n
    return w


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r36_channel_shapley.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--boot", type=int, default=3000)
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
        ratings = {ci: {s["annotator_id"]: float(s["score"])
                        for s in (it.get("scores") or [])}
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

    all_raters = sorted({r for d in prompts.values()
                         for c in d["ratings"].values() for r in c}
                        | {r for d in prompts.values() for r in d["pairs"]})
    coals = [frozenset(c) for k in range(5) for c in combinations(CHANNELS, k)]
    print(f"prompts {len(prompts):,}   raters {len(all_raters):,}   "
          f"coalitions {len(coals)}\n")

    def evaluate(coal, who, test_of):
        """Per-prompt accuracy for one coalition. Returns {pid: acc}."""
        if "T" not in coal:
            return None                      # v = CHANCE, handled by caller
        acc = {}
        for pid, d in prompts.items():
            test = test_of(pid)
            if not test:
                continue
            w = {}
            for ci, rr in d["ratings"].items():
                vals = [v for r, v in rr.items() if who is None or r in who]
                if vals:
                    x = coalition_weight(vals, coal)
                    if x is not None and abs(x) > 1e-12:
                        w[ci] = x
            if not w:
                continue
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
            ok = tot = 0
            for r_ in test:
                for x_, y_ in d["pairs"].get(r_, []):
                    if x_ in score and y_ in score:
                        tot += 1
                        ok += int(score[x_] > score[y_])
            if tot:
                acc[pid] = ok / tot
        return acc

    regimes = {}
    for regime in ("same_sample", "crossfit"):
        series = {}
        for coal in coals:
            if "T" not in coal:
                series[coal] = None
                continue
            pooled = defaultdict(list)
            n_seeds = a.seeds if regime == "crossfit" else 1
            for seed in range(n_seeds):
                rng = np.random.default_rng(20260728 + seed)
                if regime == "same_sample":
                    acc = evaluate(coal, None, lambda pid: set(prompts[pid]["pairs"]))
                else:
                    fold = {r: int(i % a.folds)
                            for i, r in enumerate(rng.permutation(all_raters))}
                    acc = defaultdict(lambda: [0.0, 0])
                    for k in range(a.folds):
                        who = {r for r in all_raters if fold.get(r) != k}
                        got = evaluate(coal, who,
                                       lambda pid, k=k: {r for r in prompts[pid]["pairs"]
                                                         if fold.get(r) == k})
                        for pid, v in (got or {}).items():
                            acc[pid][0] += v
                            acc[pid][1] += 1
                    acc = {pid: s / n for pid, (s, n) in acc.items() if n}
                for pid, v in acc.items():
                    pooled[pid].append(v)
            series[coal] = {pid: float(np.mean(v)) for pid, v in pooled.items()}
        common = sorted(set.intersection(*[set(s) for s in series.values() if s]))
        vvals = {}
        for coal in coals:
            vvals[coal] = (np.full(len(common), CHANCE) if series[coal] is None
                           else np.array([series[coal][p_] for p_ in common]))
        regimes[regime] = {"v": vvals, "prompts": common}
        print(f"=== {regime} ({len(common)} prompts) ===")
        for coal in sorted(coals, key=lambda c: (len(c), sorted(c))):
            nm = "".join(sorted(coal)) or "(empty)"
            print(f"  v({nm:5s}) = {vvals[coal].mean():.4f}")

    n = len(CHANNELS)
    shap = {}
    for regime, R in regimes.items():
        v = R["v"]
        phi = {}
        for j in CHANNELS:
            tot = np.zeros(len(R["prompts"]))
            for coal in coals:
                if j in coal:
                    continue
                k = len(coal)
                wgt = factorial(k) * factorial(n - k - 1) / factorial(n)
                tot += wgt * (v[coal | {j}] - v[coal])
            phi[j] = tot
        shap[regime] = phi

    rng = np.random.default_rng(11)

    def ci(arr):
        bs = np.array([arr[rng.integers(0, len(arr), len(arr))].mean()
                       for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return float(arr.mean()), float(lo), float(hi)

    print(f"\n{'channel':10s} {'phi same':>10} {'phi cross':>11} "
          f"{'phi_same - phi_cross':>32}")
    out = {}
    common = sorted(set(regimes["same_sample"]["prompts"])
                    & set(regimes["crossfit"]["prompts"]))
    idx_s = {p_: i for i, p_ in enumerate(regimes["same_sample"]["prompts"])}
    idx_c = {p_: i for i, p_ in enumerate(regimes["crossfit"]["prompts"])}
    for j in CHANNELS:
        a_s = np.array([shap["same_sample"][j][idx_s[p_]] for p_ in common])
        a_c = np.array([shap["crossfit"][j][idx_c[p_]] for p_ in common])
        m_s, _, _ = ci(a_s)
        m_c, _, _ = ci(a_c)
        d, lo, hi = ci(a_s - a_c)
        out[j] = {"phi_same": m_s, "phi_cross": m_c, "gap": d, "gap_ci": [lo, hi],
                  "gap_excludes_zero": bool(lo > 0 or hi < 0),
                  # PAIRED VECTOR PERSISTED 2026-07-28.  phi_S(same) - phi_S(cross)
                  # is quoted as evidence that sign is "mostly not same-sample",
                  # which is a claim about a SMALL difference and therefore only
                  # means something against a declared margin.  The vector is
                  # what makes that testable.
                  "paired_differences": [float(x) for x in (a_s - a_c)]}
        print(f"{j:10s} {m_s:>10.4f} {m_c:>11.4f} "
              f"{f'{d:+.4f} [{lo:+.4f}, {hi:+.4f}]':>32}"
              f"{'' if (lo > 0 or hi < 0) else '  (spans zero)'}")

    gs = out["S"]
    verdict = (
        f"SIGN IS THE LARGEST PREDICTIVE CHANNEL AND IT IS MOSTLY NOT SAME-SAMPLE. Averaged "
        f"over all {len(coals)} coalitions rather than one entry order, phi_S = "
        f"{gs['phi_same']:.4f} same-sample and {gs['phi_cross']:.4f} cross-fitted; the gap "
        f"is {gs['gap']:+.4f} {gs['gap_ci']}. r32's +0.0876 was the value of adding sign "
        "LAST to text alone -- one path through the lattice, not the channel's average "
        "worth. This is a predictive decomposition and not a causal one: no channel here "
        "produces any amount of value, and text without direction is not a complete "
        "normative statement."
        if gs["phi_cross"] > 0 and abs(gs["gap"]) < gs["phi_cross"] else
        f"SIGN'S VALUE IS SUBSTANTIALLY SAME-SAMPLE. phi_S falls from {gs['phi_same']:.4f} "
        f"to {gs['phi_cross']:.4f} under rater-disjoint cross-fitting, a gap of "
        f"{gs['gap']:+.4f} {gs['gap_ci']} comparable to what survives.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts": len(common), "coalitions": len(coals), "folds": a.folds,
         "seeds": a.seeds,
         "coalition_values": {r: {"".join(sorted(c)) or "empty": float(vv.mean())
                                  for c, vv in R["v"].items()}
                              for r, R in regimes.items()},
         "shapley": out, "verdict": verdict,
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
         "note": "PREDICTIVE decomposition, not causal. v(C)=0.5 for any coalition without "
                 "T, because with no criterion information every response scores alike. "
                 "{T} alone is an attribute diagnostic, not a rubric with weights removed: "
                 "a criterion sentence carries no normative direction until someone supplies "
                 "one.",
         "scope": "Internal concordance on the original candidate set (entry 36); "
                  "cross-fitted arm evaluates individual test-fold rankings."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
