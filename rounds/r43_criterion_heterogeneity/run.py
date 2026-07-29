"""r43 (queue item 5) -- criterion-level population heterogeneity.

CLAIM_CARD.md is the contract.  In one line: r42 showed every population
contrast in this package is bounded inside 0.01 accuracy points IN AGGREGATE,
and that is precisely the result that can coexist with real disagreement
underneath.  An aggregate accuracy is blind to groups assigning opposite signs
to the same criterion, to criteria only one group ever raises, and to groups
picking the same response for different reasons.

Three questions, and only the third can change a decision:

  1  sign-reversal rate   -- do groups give the same criterion opposite signs,
                             ABOVE the rate finite samples produce by themselves?
  2  minority-only        -- are there criteria essentially one group raises,
                             above the base rate that group's share implies?
  3  weight specificity   -- do a group's OWN weights predict that group's
                             rankings better than pooled weights, rater-disjoint
                             and size-matched?

1 and 2 can both be true while nothing changes: reversals that cancel leave a
shared rubric optimal for everyone.  3 is the decision.

THE NULL IS NOT OPTIONAL.  With a handful of raters per (prompt, criterion,
group) cell, sign disagreement happens by sampling alone, so a raw reversal rate
is uninterpretable.  The null permutes GROUP LABELS within each (p,c), holding
cell sizes and the rating multiset fixed and destroying only the group
structure.

THE POSITIVE CONTROL IS NOT OPTIONAL EITHER.  A heterogeneity detector that has
never returned "heterogeneous" cannot be believed when it returns
"homogeneous".  A synthetic group with sign-flipped ratings on a random 20% of
criteria is injected, and if the pipeline does not recover it, nothing else in
this round is reported.
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

AXES = ("country", "ai_usage", "age")


def individual_pairs(asm):
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


# ------------------------------------------------------------------ measures
def reversal_rate(prompts, grp, min_cell):
    """Fraction of (p,c) cells rated by >=2 qualifying groups whose signs differ.

    Returns (rate, n_cells).  A cell contributes only if at least two groups
    each have min_cell raters on it -- otherwise the comparison is one rater
    against another and the statistic measures sampling, not populations.
    """
    hits = tot = 0
    for pid, d in prompts.items():
        for ci, rr in d["ratings"].items():
            by = defaultdict(list)
            for r_, v in rr.items():
                g = grp.get(r_)
                if g is not None:
                    by[g].append(v)
            signs = {g: np.sign(np.mean(v)) for g, v in by.items() if len(v) >= min_cell}
            signs = {g: (s if s != 0 else 1.0) for g, s in signs.items()}
            if len(signs) >= 2:
                tot += 1
                hits += int(len(set(signs.values())) > 1)
    return (hits / tot if tot else float("nan")), tot


def reversal_null(prompts, grp, min_cell, reps, rng):
    """Permute group labels WITHIN each (p,c), preserving cell sizes exactly."""
    out = []
    cells = []
    for pid, d in prompts.items():
        for ci, rr in d["ratings"].items():
            lab = [(grp.get(r_), v) for r_, v in rr.items() if grp.get(r_) is not None]
            if len(lab) >= 2 * min_cell:
                cells.append(lab)
    for _ in range(reps):
        hits = tot = 0
        for lab in cells:
            gs = [g for g, _ in lab]
            vs = np.array([v for _, v in lab])
            perm = rng.permutation(len(vs))
            by = defaultdict(list)
            for g, i in zip(gs, perm):
                by[g].append(vs[i])
            signs = {g: np.sign(np.mean(v)) for g, v in by.items() if len(v) >= min_cell}
            signs = {g: (s if s != 0 else 1.0) for g, s in signs.items()}
            if len(signs) >= 2:
                tot += 1
                hits += int(len(set(signs.values())) > 1)
        out.append(hits / tot if tot else np.nan)
    return np.array(out, dtype=float)


def minority_only(prompts, grp, share, conc):
    """Concentration of each (p,c) cell's raters in its single largest group.

    Originally this returned only the fraction of cells at or above `conc`.
    That count came back 0.0000 on two of three axes with a NaN excess: with
    ~10 raters per cell drawn from a mixed pool, 90% concentration essentially
    never occurs, so the thresholded form is INERT -- a measure that cannot
    fire is not evidence of absence.  The distribution is reported instead, and
    the threshold count is kept only so its inertness is visible rather than
    read as "no minority-only criteria found".
    """
    hits = tot = 0
    fracs, excess = [], []
    for pid, d in prompts.items():
        for ci, rr in d["ratings"].items():
            gs = [grp.get(r_) for r_ in rr if grp.get(r_) is not None]
            if len(gs) < 4:
                continue
            tot += 1
            cnt = defaultdict(int)
            for g in gs:
                cnt[g] += 1
            g, c = max(cnt.items(), key=lambda t: t[1])
            frac = c / len(gs)
            fracs.append(frac)
            excess.append(frac - share.get(g, 0.0))
            if frac >= conc:
                hits += 1
    f = np.array(fracs) if fracs else np.array([np.nan])
    e = np.array(excess) if excess else np.array([np.nan])
    return {"threshold_rate": hits / tot if tot else float("nan"),
            "cells": tot, "threshold": conc,
            "threshold_is_inert": bool(hits == 0),
            "max_share_mean": float(np.nanmean(f)),
            "max_share_p95": float(np.nanpercentile(f, 95)),
            "max_share_max": float(np.nanmax(f)),
            "excess_over_base_mean": float(np.nanmean(e)),
            "excess_over_base_p95": float(np.nanpercentile(e, 95))}


def weights_from(ratings, who):
    w = {}
    for ci, rr in ratings.items():
        vals = [v for r_, v in rr.items() if who is None or r_ in who]
        if vals:
            w[ci] = float(np.sign(np.mean(vals))) or 1.0
    return w


def accuracy(prompts, sat, weight_of, test_of):
    """Pairwise agreement with the TEST raters' own rankings, per prompt."""
    acc = {}
    for pid, d in prompts.items():
        test = test_of(pid)
        if not test:
            continue
        w = weight_of(pid, d)
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


def weight_specificity(prompts, sat, grp, group, folds, rng, reps):
    """Own-group weights vs SIZE-MATCHED pooled weights, rater-disjoint.

    Size matching matters: a group's own weight set is estimated from fewer
    raters, so an unmatched pooled arm wins on sample size alone and would be
    reported as "a shared rubric is better".  The pooled train set is
    subsampled to the own-group train size, repeated, and averaged.
    """
    members = sorted({r for d in prompts.values() for c in d["ratings"].values()
                      for r in c if grp.get(r) == group}
                     | {r for d in prompts.values() for r in d["pairs"]
                        if grp.get(r) == group})
    if len(members) < 4 * folds:
        return None
    allr = sorted({r for d in prompts.values() for c in d["ratings"].values() for r in c})
    fold = {r: i % folds for i, r in enumerate(members)}
    own_acc, pool_acc = defaultdict(list), defaultdict(list)
    for f in range(folds):
        test = {r for r in members if fold[r] == f}
        tr_own = {r for r in members if fold[r] != f}
        if not test or not tr_own:
            continue
        pool_src = [r for r in allr if r not in test]
        a_own = accuracy(prompts, sat,
                         lambda pid, d: weights_from(d["ratings"], tr_own),
                         lambda pid: test)
        for pid, v in a_own.items():
            own_acc[pid].append(v)
        for _ in range(reps):
            sub = set(rng.choice(pool_src, size=min(len(tr_own), len(pool_src)),
                                 replace=False))
            a_p = accuracy(prompts, sat,
                           lambda pid, d: weights_from(d["ratings"], sub),
                           lambda pid: test)
            for pid, v in a_p.items():
                pool_acc[pid].append(v)
    common = sorted(set(own_acc) & set(pool_acc))
    if len(common) < 30:
        return None
    d = np.array([np.mean(own_acc[p]) - np.mean(pool_acc[p]) for p in common])
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    # Two-sided bootstrap p, so the group tests can be corrected for
    # multiplicity.  Seventeen groups are tested across three axes; at alpha =
    # 0.05 that expects ~0.9 false positives before any real effect exists, and
    # reporting the raw count of "SIG" cells would be reporting that noise.
    p2 = 2 * min(float(np.mean(bs <= 0)), float(np.mean(bs >= 0)))
    return {"group": group, "n_raters": len(members), "prompts": len(common),
            "own_minus_pooled": float(d.mean()), "ci": [float(lo), float(hi)],
            "excludes_zero": bool(lo > 0 or hi < 0), "p_two_sided": min(1.0, p2),
            "paired_differences": [float(x) for x in d]}


def bh_fdr(pvals, q=0.05):
    """Benjamini-Hochberg: returns a boolean array of survivors."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    if n == 0:
        return np.zeros(0, dtype=bool)
    order = np.argsort(p)
    thresh = q * (np.arange(1, n + 1) / n)
    passed = p[order] <= thresh
    keep = np.zeros(n, dtype=bool)
    if passed.any():
        cut = np.max(np.nonzero(passed)[0])
        keep[order[: cut + 1]] = True
    return keep


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--annotators", type=Path, default=_ROOT / "data/annotators.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r43_criterion_heterogeneity.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--min-cell", type=int, default=3)
    p.add_argument("--min-group", type=int, default=40)
    p.add_argument("--conc", type=float, default=0.9)
    p.add_argument("--null-reps", type=int, default=200)
    p.add_argument("--match-reps", type=int, default=3)
    p.add_argument("--flip", type=float, default=0.20)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        a.null_reps, a.match_reps = 10, 1
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    rng = np.random.default_rng(20260728)

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
        demo[r.get("annotator_id")] = {k: d.get(v) for k, v in
                                       (("country", "country_of_residence"),
                                        ("ai_usage", "generative_ai_usage"),
                                        ("age", "age"))}

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

    allr = sorted({r for d in prompts.values() for c in d["ratings"].values() for r in c}
                  | {r for d in prompts.values() for r in d["pairs"]})
    nodemo = [r for r in allr if r not in demo]
    print(f"prompts {len(prompts):,}   raters {len(allr):,}   "
          f"no annotator record {len(nodemo):,} ({len(nodemo)/len(allr):.1%}) "
          f"-- every statement below is scoped to the remainder\n")

    # ---- POSITIVE CONTROL ------------------------------------------------
    # Inject a synthetic group whose ratings are sign-flipped on a random 20%
    # of criteria.  If the reversal statistic cannot see that, a low reversal
    # rate on the real groups means nothing.
    synth = {r: ("FLIPPED" if i % 2 == 0 else "PLAIN") for i, r in enumerate(allr)}
    flip_ci = {}
    ctrl_prompts = {}
    for pid, d in prompts.items():
        rr2 = {}
        for ci, rr in d["ratings"].items():
            flip = flip_ci.setdefault((pid, ci), rng.random() < a.flip)
            rr2[ci] = {r_: (-v if (flip and synth[r_] == "FLIPPED") else v)
                       for r_, v in rr.items()}
        ctrl_prompts[pid] = {"ratings": rr2, "pairs": d["pairs"]}
    pc_rate, pc_n = reversal_rate(ctrl_prompts, synth, a.min_cell)
    base_rate, base_n = reversal_rate(prompts, synth, a.min_cell)
    pc_passed = bool(np.isfinite(pc_rate) and np.isfinite(base_rate)
                     and pc_rate > base_rate + 0.05)
    print("=== POSITIVE CONTROL (synthetic group, 20% of criteria sign-flipped) ===")
    print(f"  reversal rate with the flip   {pc_rate:.4f}  ({pc_n} cells)")
    print(f"  same split, ratings untouched {base_rate:.4f}  ({base_n} cells)")
    print(f"  -> {'DETECTED' if pc_passed else 'NOT DETECTED'}")
    if not pc_passed:
        raise SystemExit("REFUSING TO REPORT: the reversal statistic cannot recover an "
                         "injected 20% sign flip, so a low rate on the real groups "
                         "would be silence, not homogeneity.")

    # ---- the real axes ---------------------------------------------------
    out = {}
    for axis in AXES:
        grp_all = {r: (demo.get(r) or {}).get(axis) for r in allr}
        cnt = defaultdict(int)
        for r, g in grp_all.items():
            if g is not None:
                cnt[g] += 1
        big = {g for g, c in cnt.items() if c >= a.min_group}
        grp = {r: g for r, g in grp_all.items() if g in big}
        if len(big) < 2:
            out[axis] = {"status": "UNVERIFIED",
                         "why": f"fewer than 2 groups reach {a.min_group} raters"}
            print(f"\n--- {axis}: fewer than 2 qualifying groups -- UNVERIFIED")
            continue
        tot_g = sum(cnt[g] for g in big)
        share = {g: cnt[g] / tot_g for g in big}

        obs, ncell = reversal_rate(prompts, grp, a.min_cell)
        null = reversal_null(prompts, grp, a.min_cell, a.null_reps, rng)
        nmean = float(np.nanmean(null))
        nlo, nhi = np.nanpercentile(null, [2.5, 97.5])
        exceeds = bool(obs > nhi)
        mo = minority_only(prompts, grp, share, a.conc)

        print(f"\n--- {axis}: {len(big)} groups >= {a.min_group} raters {sorted(big)}")
        print(f"  sign-reversal rate      {obs:.4f} over {ncell} cells")
        print(f"  label-permutation null  {nmean:.4f} [{nlo:.4f}, {nhi:.4f}]  "
              f"({a.null_reps} reps)")
        print(f"  observed - null         {obs - nmean:+.4f}  "
              f"-> {'ABOVE the null' if exceeds else 'within the null'}")
        print(f"  largest-group share per cell: mean {mo['max_share_mean']:.3f}  "
              f"p95 {mo['max_share_p95']:.3f}  max {mo['max_share_max']:.3f}")
        print(f"  excess over that group's base share: mean "
              f"{mo['excess_over_base_mean']:+.3f}  p95 {mo['excess_over_base_p95']:+.3f}")
        print(f"  cells >= {a.conc:.0%} one group: {mo['threshold_rate']:.4f} of "
              f"{mo['cells']}"
              + ("   <- INERT: this threshold never fires, so its zero is not evidence"
                 if mo["threshold_is_inert"] else ""))

        specs = []
        for g in sorted(big):
            s = weight_specificity(prompts, sat, grp, g, a.folds, rng, a.match_reps)
            if s:
                specs.append(s)
                print(f"  own-group weights, {g:<28s} {s['own_minus_pooled']:+.4f} "
                      f"[{s['ci'][0]:+.4f},{s['ci'][1]:+.4f}]"
                      f"{'  SIG' if s['excludes_zero'] else ''}")
        better = [s for s in specs if s["excludes_zero"] and s["own_minus_pooled"] > 0]
        out[axis] = {"status": "MEASURED", "groups": sorted(big), "n_groups": len(big),
                     "reversal_rate": obs, "reversal_cells": ncell,
                     "reversal_null_mean": nmean, "reversal_null_ci": [float(nlo), float(nhi)],
                     "reversal_excess": float(obs - nmean),
                     "reversal_above_null": exceeds,
                     "minority_only": mo,
                     "weight_specificity": specs,
                     "n_groups_better_with_own_weights": len(better)}

    # ---- multiplicity, across every group test in the round ---------------
    flat = [(ax, s) for ax, v in out.items() if v.get("status") == "MEASURED"
            for s in v["weight_specificity"]]
    keep = bh_fdr([s["p_two_sided"] for _, s in flat], q=0.05)
    for (ax, s), k in zip(flat, keep):
        s["survives_bh_fdr_5pct"] = bool(k)
    n_pos = sum(1 for _, s in flat if s["excludes_zero"] and s["own_minus_pooled"] > 0)
    n_neg = sum(1 for _, s in flat if s["excludes_zero"] and s["own_minus_pooled"] < 0)
    n_bh = int(keep.sum())
    # A group predicted WORSE by its own weights has no substantive reading --
    # it is what sampling noise looks like.  So the count of significant
    # NEGATIVES is a built-in calibration of the positives: under no
    # heterogeneity the two should be symmetric, and quoting only the positives
    # would be reporting half of a symmetric noise distribution as a finding.
    print(f"\n=== multiplicity across all {len(flat)} group tests ===")
    print(f"  significant at 95% CI: {n_pos} positive, {n_neg} negative "
          f"(negatives are the noise calibration -- 'own weights predict me WORSE' "
          f"has no mechanism)")
    print(f"  surviving Benjamini-Hochberg at q=0.05: {n_bh}")
    for ax, s in flat:
        if s.get("survives_bh_fdr_5pct"):
            print(f"    {ax}/{s['group']}: {s['own_minus_pooled']:+.4f} "
                  f"p={s['p_two_sided']:.4f}")
    for v in out.values():
        if v.get("status") == "MEASURED":
            v["n_groups_better_with_own_weights"] = sum(
                1 for s in v["weight_specificity"]
                if s.get("survives_bh_fdr_5pct") and s["own_minus_pooled"] > 0)

    # ---- verdict, computed ------------------------------------------------
    measured = [v for v in out.values() if v.get("status") == "MEASURED"]
    any_rev = [k for k, v in out.items() if v.get("reversal_above_null")]
    any_bet = [k for k, v in out.items() if v.get("n_groups_better_with_own_weights", 0) > 0]
    if not measured:
        verdict = ("UNVERIFIED: no axis had two groups large enough to compare, so "
                   "nothing about heterogeneity was tested in either direction")
    elif any_bet:
        verdict = (f"HETEROGENEITY THAT MATTERS: on {', '.join(any_bet)} at least one "
                   "group is predicted better by its OWN rater-disjoint, size-matched "
                   f"weights than by pooled ones, surviving Benjamini-Hochberg across "
                   f"all {len(flat)} group tests. A single shared rubric is not optimal "
                   f"for those groups and the aggregation question becomes live. "
                   f"Calibration: {n_pos} positive and {n_neg} negative results were "
                   f"significant before correction, and a negative has no mechanism")
    elif any_rev:
        verdict = (f"CONFLICT WITHOUT CONSEQUENCE: sign reversals exceed the "
                   f"label-permutation null on {', '.join(any_rev)}, but no group is "
                   "predicted better by its own weights. Groups do disagree about "
                   "individual criteria and it does not change which response wins -- "
                   "so the aggregate equivalence in r42 is not hiding a decision")
    else:
        verdict = (f"NO DETECTED HETEROGENEITY: reversal rates sit inside the "
                   f"label-permutation null and no group's own weights beat pooled "
                   f"ones after correcting across {len(flat)} group tests "
                   f"({n_pos} positive and {n_neg} negative survived uncorrected, "
                   f"which is what a symmetric noise distribution looks like). "
                   "Scoped to demographic proxies, to groups above the size "
                   "floor, and to raters with an annotator record -- this is not a "
                   "statement about value constituencies, which this release cannot "
                   "identify")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": len(prompts), "raters": len(allr),
        "raters_without_demographics": len(nodemo),
        "min_cell": a.min_cell, "min_group": a.min_group,
        "concentration_threshold": a.conc, "null_reps": a.null_reps,
        "positive_control": {"flip_fraction": a.flip, "rate_with_flip": pc_rate,
                             "rate_without": base_rate, "passed": pc_passed},
        "axes": out, "verdict": verdict,
        "multiplicity": {
            "n_group_tests": len(flat), "n_significant_positive": n_pos,
            "n_significant_negative": n_neg, "n_surviving_bh_fdr_5pct": n_bh,
            "note": ("A group predicted WORSE by its own weights has no mechanism, so "
                     "the negative count calibrates the positive one: under no "
                     "heterogeneity they are symmetric. BH is applied across every "
                     "group test in the round, not per axis.")},
        "scope": ("Demographic proxies, NOT value constituencies -- r16-r18's latent "
                  "partition was frozen because it named no constituency, and using "
                  "country/age/AI-use instead makes the label honest without making it "
                  "the right object. Scoped to raters with an annotator record "
                  f"({len(allr) - len(nodemo)}/{len(allr)}) and to groups above the "
                  "size floor. The direction tested is itself post-choice: two groups "
                  "agreeing on a sign because the menu made it salient to both is "
                  "recorded here as agreement."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
