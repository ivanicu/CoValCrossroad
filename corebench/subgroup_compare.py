#!/usr/bin/env python3
"""
corebench/subgroup_compare.py -- the G family across arms, with intervals.

Row 0 reported worst-subgroup fidelity of 0.0395 for coval_core against 0.0362 for topw_k4 --
THE ONE DIMENSION WHERE THE INCUMBENT LED -- as two point values with no interval. Fidelity is
now settled and this is the only place a competing claim survives, so it gets tested.

⚠ "WORST SUBGROUP" IS A MIN OVER SUBGROUPS, WHICH IS AN EXTREME ORDER STATISTIC. Quoting it
raw is the same failure as quoting a floor as `0.2983 [0.2567, 0.3467]` off min/max of N
draws: with ~20 subgroups the minimum wanders even when nothing differs. So the min is
bootstrapped over subgroups and reported with its own spread, and the primary estimand is the
paired per-subgroup difference rather than the extremum.

ESTIMAND        per subgroup (axis=value, n>=100 annotator-judgements), the A2 difference
                between two arms; the mean over subgroups, the share of subgroups each arm
                wins, and the MIN with a bootstrap interval. Named before the method.
n_eff           SUBGROUPS, not annotators and not prompts. The unit that varies here is the
                subgroup, and there are ~20 of them across 6 demographic axes.
SCOPE           6 axes: age, ai_concern_level, country_of_residence, education_level,
                gender, generative_ai_usage. 1,012 annotators.
KILL            pre-registered: paired-over-subgroups CI on the mean difference. Includes
                zero -> the row-0 lead was noise in an extremum.
POSITIVE CTRL   any competent arm against random must win a large majority of subgroups.
PLACEBO         an arm against itself: exactly 0 in every subgroup.
"""
from __future__ import annotations
import collections, itertools, json, hashlib, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, yvec, cls, DEMO_AXES
PAIRS = list(itertools.combinations(range(4), 2))
L, SEEDS, MINN, NBOOT = "ABCD", [0, 1, 2], 100, 2000


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L: sc[tok] = -lvl
    return [sc[c] for c in L] if len(sc) == 4 else None


def load_by_subgroup():
    demo = {}
    for line in open(ROOT/"data"/"annotators.jsonl", encoding="utf-8"):
        r = json.loads(line); demo[r["annotator_id"]] = r.get("demographics") or {}
    out = collections.defaultdict(list)
    for line in open(ROOT/"data"/"comparisons.jsonl", encoding="utf-8"):
        if not line.strip(): continue
        rec = json.loads(line); pid = rec["prompt_id"]
        for asm in rec.get("metadata", {}).get("assessments", []):
            d = demo.get(asm.get("annotator_id"), {})
            for e in (asm.get("ranking_blocks") or {}).get("world") or []:
                y = parse_ranking(e["ranking"]) if e.get("ranking") else None
                if y:
                    out[pid].append((y, d, asm.get("annotator_id")))
                    ANN[asm.get("annotator_id")] = 1
    return out


ANN = {}


def a2_by_subgroup(sat, tg, keep=None):
    acc = collections.defaultdict(lambda: [0.0, 0])
    for p in sat:
        if p not in tg: continue
        c = cls(yvec(sat[p], sorted({i for i, _ in sat[p]})))
        for y, d, aid in tg[p]:
            if keep is not None and aid not in keep: continue
            h = cls(np.array(y, float))
            v = float(np.mean([c[q] == h[q] for q in range(6)]))
            for ax in DEMO_AXES:
                val = d.get(ax)
                if val is None: continue
                k = f"{ax}={val}"
                acc[k][0] += v; acc[k][1] += 1
    return {k: s/n for k, (s, n) in acc.items() if n >= MINN}


if __name__ == "__main__":
    A, B = sys.argv[1], sys.argv[2]
    tg = load_by_subgroup()
    SA = load_sat(ROOT/"corebench"/"results"/f"sat_{A}.npz")
    SB = load_sat(ROOT/"corebench"/"results"/f"sat_{B}.npz")
    sa, sb = a2_by_subgroup(SA, tg), a2_by_subgroup(SB, tg)
    sr = a2_by_subgroup(load_sat(ROOT/"corebench"/"results"/"sat_random_k4_s0.npz"), tg)
    ks = sorted(set(sa) & set(sb) & set(sr))
    d = np.array([sa[k] - sb[k] for k in ks])
    # ⚠ THE FIRST VERSION RESAMPLED SUBGROUPS AND ITS INTERVAL WAS FAR TOO NARROW.
    # The 36 subgroups are 6 AXES x ~6 values, and EVERY judgement appears in all six axes --
    # `age=25-34` and `gender=Female` are overlapping views of the same 18,384 rows, not
    # independent units. Resampling them treats one dataset as six. It is the n_eff error
    # this project already has a rule for, made one level up: the unit that varies is the
    # ANNOTATOR, and there are 1,012 of them, so the bootstrap resamples annotators and
    # recomputes every subgroup mean from the resample.
    #
    # The AXIS is also reported, because within one axis the subgroups ARE disjoint, so a
    # per-axis sign is a real replication and six of them is the honest replication breadth.
    rng = np.random.default_rng(0)
    aids = sorted(ANN)
    bm, bmin = [], []
    for _ in range(400):
        pick = set(aids[i] for i in rng.integers(0, len(aids), len(aids)))
        A2a = a2_by_subgroup(SA, tg, keep=pick); A2b = a2_by_subgroup(SB, tg, keep=pick)
        kk = sorted(set(A2a) & set(A2b))
        if not kk: continue
        dd = np.array([A2a[k] - A2b[k] for k in kk])
        bm.append(dd.mean()); bmin.append(dd.min())
    bm, bmin = np.array(bm), np.array(bmin)

    print(f"\n  SUBGROUP COMPARISON  {A} - {B}   (n_eff = {len(ks)} SUBGROUPS, 6 axes)\n")
    pl = np.array([sa[k] - sa[k] for k in ks])
    print(f"    [{'PASS' if np.all(pl == 0) else 'FAIL'}] PLACEBO arm vs itself is exactly 0 "
          f"in every subgroup")
    wr = np.mean([sa[k] > sr[k] for k in ks])
    print(f"    [{'PASS' if wr > 0.8 else 'FAIL'}] POSITIVE {A} beats random in "
          f"{wr:.1%} of subgroups")
    per_axis = {}
    for ax in DEMO_AXES:
        kk = [k for k in ks if k.startswith(ax + "=")]
        if kk: per_axis[ax] = float(np.mean([sa[k] - sb[k] for k in kk]))
    print(f"\n    per-AXIS mean difference (within an axis the subgroups ARE disjoint):")
    for ax, v_ in per_axis.items(): print(f"      {ax:<24}{v_:+.4f}")
    print(f"      -> same sign on {sum(1 for v_ in per_axis.values() if v_>0)} of "
          f"{len(per_axis)} axes")
    print(f"\n    mean over subgroups   {d.mean():+.4f}   95% CI "
          f"[{np.percentile(bm,2.5):+.4f}, {np.percentile(bm,97.5):+.4f}]")
    print(f"    {A} wins              {np.mean(d>0):.1%} of subgroups")
    print(f"    worst subgroup diff   {d.min():+.4f}   bootstrap CI "
          f"[{np.percentile(bmin,2.5):+.4f}, {np.percentile(bmin,97.5):+.4f}]"
          f"   <- an EXTREMUM, bracketed not quoted")
    lo, hi = np.percentile(bm, 2.5), np.percentile(bm, 97.5)
    v = ("SEPARABLE" if lo > 0 or hi < 0 else
         "NOT separable -- the row-0 worst-subgroup lead was noise in an extremum")
    print(f"\n    VERDICT: {v}\n")
    (ROOT/"corebench"/"results"/f"subgroup_{A}_vs_{B}.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "n_subgroups": len(ks), "mean": float(d.mean()), "ci": [float(lo), float(hi)],
         "min": float(d.min()), "min_ci": [float(np.percentile(bmin,2.5)),
         float(np.percentile(bmin,97.5))], "win_rate": float(np.mean(d>0)), "verdict": v},
        indent=2, sort_keys=True))
