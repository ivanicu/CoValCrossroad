"""r37 (plan item C36) -- Leakage as a decay curve over isolation strength, not one bias number.

The point
---------
r34 answered "is the polarity signal same-sample leakage?" with a single
comparison and got no. That is one rung of a ladder. What matters for anyone
reusing this rubric is HOW the signal decays as the people supplying the
direction are moved further from the people whose choices are predicted.

    A0  same participants        weights from everyone, evaluated on everyone
    A1  leave-one-rater-out      weights from everyone except the target rater
    A2  held-out rater folds     global 5-fold; a person is in exactly one fold
    A3  held-out country         weights from every OTHER country, evaluated on
                                 raters in the held-out one
    A4  response-blind humans     NOT AVAILABLE -- nobody in this release rated a
                                 criterion without first seeing four candidates

    L(k) = A0 - Ak

Where the drop happens is the diagnosis:

    A0 -> A1   individual circularity: the target rater's own rating returning
    A1 -> A2   small-sample group fitting
    A2 -> A3   population dependence: direction is country-conditional
    A3 -> A4   seeing the responses at all changed the direction

The last rung cannot be climbed with this data, and saying so precisely is the
point of drawing the ladder: L(3) is the largest isolation this release permits,
and it is not the isolation the question actually needs.

Secondary strata
----------------
Country is the plan's named axis. Generative-AI usage and age are run alongside
because they are free and answer a different question: is the direction
conditional on WHO, in ways other than nationality? These are transport checks,
not claims that any stratum is a value bloc -- entry 21 records what happened
last time a partition got called a constituency.

Scope that limits the country arm specifically
-----------------------------------------------
148 of the 1,160 criterion-scoring raters (12.8%) appear in no annotator record
and therefore have no country (entry 22). They can contribute WEIGHTS but can
never be a held-out test stratum, so A3 is computed over 87.2% of the rater pool
and the excluded eighth is not random with respect to anything known.
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
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--annotators", type=Path, default=_ROOT / "data/annotators.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r37_leakage_topology.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seeds", type=int, default=8)
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--min-stratum", type=int, default=40)
    a = p.parse_args()

    z = np.load(a.sat, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    demo = {}
    for line in open(a.annotators, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        d = r.get("demographics") or {}
        demo[r.get("annotator_id")] = {
            "country": d.get("country_of_residence"),
            "ai_usage": d.get("generative_ai_usage"),
            "age": d.get("age"),
        }

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
    no_demo = [r for r in all_raters if r not in demo]
    print(f"prompts {len(prompts):,}   raters {len(all_raters):,}   "
          f"without demographics {len(no_demo):,} ({len(no_demo)/len(all_raters):.1%})\n")

    def run(who_of, test_of):
        """who_of(pid)->train rater set or None(all); test_of(pid)->test raters."""
        acc = {}
        for pid, d in prompts.items():
            test = test_of(pid)
            if not test:
                continue
            who = who_of(pid)
            w = {}
            for ci, rr in d["ratings"].items():
                vals = [v for r, v in rr.items() if who is None or r in who]
                if not vals:
                    continue
                mu = float(np.mean(vals))
                sg = float(np.sign(mu)) or 1.0
                w[ci] = sg
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
                for x, y in d["pairs"].get(r_, []):
                    if x in score and y in score:
                        tot += 1
                        ok += int(score[x] > score[y])
            if tot:
                acc[pid] = ok / tot
        return acc

    levels = {}
    # A0 -- same participants
    levels["A0_same_participants"] = run(lambda pid: None,
                                         lambda pid: set(prompts[pid]["pairs"]))
    # A1 -- leave-one-rater-out (weights exclude the evaluated rater)
    a1 = defaultdict(lambda: [0.0, 0])
    for pid, d in prompts.items():
        for tgt in d["pairs"]:
            who = {r for c in d["ratings"].values() for r in c} - {tgt}
            got = run(lambda pid_, who=who: who, lambda pid_, t=tgt: {t} if pid_ == pid else set())
            if pid in got:
                a1[pid][0] += got[pid]
                a1[pid][1] += 1
    levels["A1_leave_one_rater_out"] = {p_: s / n for p_, (s, n) in a1.items() if n}
    # A2 -- global rater folds
    a2 = defaultdict(lambda: [0.0, 0])
    for seed in range(a.seeds):
        rng = np.random.default_rng(20260728 + seed)
        fold = {r: int(i % a.folds) for i, r in enumerate(rng.permutation(all_raters))}
        for k in range(a.folds):
            who = {r for r in all_raters if fold.get(r) != k}
            got = run(lambda pid: who,
                      lambda pid: {r for r in prompts[pid]["pairs"] if fold.get(r) == k})
            for pid, v in got.items():
                a2[pid][0] += v
                a2[pid][1] += 1
    levels["A2_held_out_rater_folds"] = {p_: s / n for p_, (s, n) in a2.items() if n}

    # A3 -- held-out stratum (country primary; ai_usage and age secondary)
    strata_out = {}
    for key in ("country", "ai_usage", "age"):
        groups = defaultdict(set)
        for r in all_raters:
            g = (demo.get(r) or {}).get(key)
            if g is not None:
                groups[str(g)].add(r)
        big = [g for g, rs in groups.items() if len(rs) >= a.min_stratum]
        agg = defaultdict(lambda: [0.0, 0])
        for g in big:
            held = groups[g]
            who = {r for r in all_raters if r not in held}
            got = run(lambda pid: who,
                      lambda pid: {r for r in prompts[pid]["pairs"] if r in held})
            for pid, v in got.items():
                agg[pid][0] += v
                agg[pid][1] += 1
        strata_out[key] = {"groups": big, "n_groups": len(big),
                           "series": {p_: s / n for p_, (s, n) in agg.items() if n}}
        print(f"  {key:9s}: {len(big)} strata with >= {a.min_stratum} raters -> {big}")
    levels["A3_held_out_country"] = strata_out["country"]["series"]

    rng = np.random.default_rng(3)
    base = levels["A0_same_participants"]

    def gap(other):
        common = sorted(set(base) & set(other))
        d = np.array([base[p_] - other[p_] for p_ in common])
        bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return {"L": float(d.mean()), "ci": [float(lo), float(hi)],
                "prompts": len(common), "excludes_zero": bool(lo > 0 or hi < 0),
                # see r34.  The held-out-country rung is the load-bearing "no
                # population dependence" number in the whole package.
                "paired_differences": [float(x) for x in d]}

    print(f"\n{'isolation level':26s} {'accuracy':>9} {'L(k) = A0 - Ak':>28}")
    out = {}
    for name, ser in levels.items():
        v = np.array(list(ser.values()))
        g = gap(ser) if name != "A0_same_participants" else {"L": 0.0, "ci": [0.0, 0.0],
                                                             "prompts": len(v),
                                                             "excludes_zero": False}
        out[name] = {"accuracy": float(v.mean()), **g}
        gs = ("--" if name == "A0_same_participants"
              else f"{g['L']:+.4f} [{g['ci'][0]:+.4f}, {g['ci'][1]:+.4f}]"
                   f"{'' if g['excludes_zero'] else '  (ns)'}")
        print(f"{name:26s} {v.mean():>9.4f} {gs:>28}")

    for key in ("ai_usage", "age"):
        ser = strata_out[key]["series"]
        if ser:
            v = np.array(list(ser.values()))
            g = gap(ser)
            out[f"A3_held_out_{key}"] = {"accuracy": float(v.mean()), **g}
            print(f"{'A3_held_out_'+key:26s} {v.mean():>9.4f} "
                  f"{f'{g[chr(76)]:+.4f} [{g[chr(99)+chr(105)][0]:+.4f}, {g[chr(99)+chr(105)][1]:+.4f}]':>28}"
                  f"{'' if g['excludes_zero'] else '  (ns)'}")

    l1 = out["A1_leave_one_rater_out"]["L"]
    l3 = out["A3_held_out_country"]["L"]
    biggest = max(("A1", l1), ("A2", out["A2_held_out_rater_folds"]["L"]),
                  ("A3", l3), key=lambda t: t[1])
    verdict = (
        f"THE DECAY IS FLAT WITHIN THE TESTED SPLITS. Moving from same-participant "
        f"weights all the way to cross-country weights costs {l3:+.4f}, and the largest "
        f"single rung is {biggest[0]} at {biggest[1]:+.4f}. Every rung is bounded inside "
        "0.01 accuracy points by an equivalence test at that margin (r42), so this is a "
        "BOUND, not a non-detection -- but the margin is a stipulation and the same rungs "
        "are NOT equivalent at 0.0025. NOT ESTABLISHED: population invariance. Aggregate "
        "accuracy can conceal criterion-level sign reversals, minority-only criteria, and "
        "groups choosing alike for different reasons; none of those are tested here. And "
        "the rung that matters most cannot be climbed at all: NOBODY in this dataset rated "
        "a criterion without first seeing four candidate responses, so L(4) -- the cost of "
        "response-blind elicitation -- is undefined, not zero."
        if max(abs(l1), abs(l3)) < 0.02 else
        f"THE DECAY IS STRUCTURED. L(1)={l1:+.4f} individual, L(3)={l3:+.4f} cross-country; "
        f"the largest rung is {biggest[0]}. Read the rung, not the total: where the drop "
        "happens names which dependence is operating.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts": len(prompts), "raters": len(all_raters),
         "raters_without_demographics": len(no_demo), "levels": out,
         "strata": {k: v["groups"] for k, v in strata_out.items()},
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
         "A4_note": "A4 (response-blind humans) is UNDEFINED in this release: every rater "
                    "saw four candidates before rating any criterion. L(3) is the largest "
                    "isolation the data permits and is not the isolation the question needs.",
         "scope": "148/1160 criterion raters (12.8%) have no annotator record and hence no "
                  "country, so they can supply WEIGHTS but never be a held-out stratum "
                  "(entry 22). Sign weighting throughout, evaluated on individual rankings."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
