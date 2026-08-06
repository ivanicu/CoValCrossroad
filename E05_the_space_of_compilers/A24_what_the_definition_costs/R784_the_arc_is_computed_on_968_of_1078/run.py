#!/usr/bin/env python3
"""R784 · every number in this arc is computed on 968 of 1078 ranked prompts.

CHECK #386 killed R783's NEXT on arithmetic before writing it -- an 18-vs-968 comparison has an MDE of
~0.66 SD (D1), so its null would be manufactured by the design -- and then found the drop that
matters: `load_targets()` returns 1078 prompts with parsed rankings, `core_full.json` covers 968, and
the `>=2 rankings` filter drops 0. **110 ranked prompts, 10.20%, have no rubric.**

ESTIMAND        E1 the population decomposition and the cause of each drop · E2 whether the 110 differ
                from the 968 on rankings-per-prompt and unacceptable flags, by RANK statistic ·
                E3 the MDE for mean and rank · E4 the bias's direction and bound
IDENTIFICATION  E1-E3 exact; E4 STRUCTURALLY UNIDENTIFIED -- no rubric means no arm has criteria
                there, so nothing can be scored; checked against R468, there is no key to recover
DERIVED FIRST   D1 an 18-vs-968 MDE is ~0.66 SD · D2 the mean is inadmissible (SD 95.05 vs 4.78, one
                prompt with 1012 rankings) so the estimand is fixed on MEDIANS and a rank statistic
                BEFORE the statistic runs · D3 a group-label permutation IS valid here, unlike the
                paired-mean permutations of ledger 1125 and 1129, and its world is built synthetically
WORLDS          A structured · B incidental · C underpowered
CONTROLS        OBJECT · PLACEBO · g=0 (200 random subsets) · POSITIVE (swept, band computed) ·
                NEGATIVE (group-label permutation, valid) · CONFOUND (flag rate) · ROBUST (3 estimators)
"""
import collections
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets                      # noqa: E402

RES = ROOT / "corebench/results"
ZEFF = 1.959964 + 0.841621
NDRAW = 200
SEED = 31337
Q = 0.05

INSTRUMENT_UNIT = "a parsed ranking record"
CLAIM_UNIT = "a prompt"


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def rank_stat(a, b):
    """Mann-Whitney U as a normalised rank-biserial in [-1, 1]. Sign: b above a."""
    x = np.concatenate([a, b])
    r = np.argsort(np.argsort(x, kind="mergesort"), kind="mergesort").astype(float) + 1.0
    # average ties
    order = np.argsort(x, kind="mergesort")
    xs = x[order]
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = r[order[i:j + 1]].mean()
        i = j + 1
    rb = r[len(a):].sum() - len(b) * (len(b) + 1) / 2.0
    u = rb / (len(a) * len(b))
    return 2.0 * u - 1.0


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT}
    rng = np.random.default_rng(SEED)

    # ================= E1 · the decomposition, and the CAUSE of each drop =========================
    print("  E1 - POPULATION DECOMPOSITION, AND WHICH FILTER PRODUCES EACH DROP")
    targets, unacc = load_targets()
    full = json.loads((RES / "core_full.json").read_text())
    sat = load_sat(RES / "sat_random_k4_s0.npz")
    ranked, rubricked = set(targets), set(full)
    missing = sorted(ranked - rubricked)
    scored = sorted({p for p in sat if p in targets and len(targets[p]) >= 2})
    nrel = sum(1 for line in open(ROOT / "data/conversation_rubrics.jsonl", encoding="utf-8")
               if line.strip())
    print(f"     ranked (parsed human rankings)      {len(ranked)}")
    print(f"     rubricked (`core_full.json`)        {len(rubricked)}")
    print(f"     scored (this arc's population)      {len(scored)}")
    print(f"     released conversations              {nrel}")
    print(f"     ⭐ ranked WITHOUT a rubric           {len(missing)}   ({len(missing)/len(ranked):.2%})")
    print(f"     rubricked without rankings          {len(rubricked - ranked)}")
    print(f"     dropped by the `>=2 rankings` rule  "
          f"{sum(1 for p in sat if p in targets and len(targets[p]) < 2)}")
    print(f"     dropped by absence from the sat file{len(rubricked - set(sat)):>4}")
    print(f"     released but never scored           {nrel - len(scored)}   (R783: identified)")
    ok_obj = (len(ranked) == len(rubricked) + len(missing) and len(scored) == len(rubricked)
              and len(missing) > 0)
    if not ok_obj:
        print("  UNRUNNABLE: the set differences do not reconcile. Exit 2, never 0.")
        return 2
    out["e1"] = {"ranked": len(ranked), "rubricked": len(rubricked), "scored": len(scored),
                 "released": nrel, "missing_rubric": len(missing),
                 "released_unscored": nrel - len(scored)}

    # ================= the two axes ===============================================================
    def axes(ps):
        n = np.array([float(len(targets[p])) for p in ps])
        f = np.array([float(len(unacc.get(p, []))) for p in ps])
        return {"rankings": n, "flags": f, "flag_rate": f / np.maximum(n, 1.0)}

    A, B = axes(scored), axes(missing)

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    plac = rank_stat(A["rankings"], A["rankings"])
    print(f"     PLACEBO    the 968 against itself: rank statistic {plac:+.6f}  "
          f"{'PASS' if abs(plac) < 1e-9 else 'FAIL'}")
    # g=0 : 200 random 110-subsets of the scored group against their complements
    g0 = {}
    for k in ("rankings", "flags", "flag_rate"):
        draws = []
        for _ in range(NDRAW):
            idx = rng.permutation(len(scored))
            draws.append(rank_stat(A[k][idx[len(missing):]], A[k][idx[:len(missing)]]))
        g0[k] = (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5)))
        print(f"     g=0        random 110-subset, {k:<10} null band "
              f"[{g0[k][0]:+.4f}, {g0[k][1]:+.4f}]  over {NDRAW} draws")
    # POSITIVE : plant a location shift into a synthetic subgroup
    dose, okp = {}, True
    sd_ref = float(A["rankings"].std(ddof=1))
    for g in (0.0, 0.25, 0.5, 1.0):
        idx = rng.permutation(len(scored))
        sub = A["rankings"][idx[:len(missing)]] + g * sd_ref
        rest = A["rankings"][idx[len(missing):]]
        s = rank_stat(rest, sub)
        res = not (g0["rankings"][0] <= s <= g0["rankings"][1])
        dose[str(g)] = {"stat": s, "resolves": res}
        print(f"     POSITIVE   plant {g:>4.2f} SD   rank {s:+.4f}   "
              f"{'RESOLVES' if res else 'inside the null band'}")
        if g == 0.0 and res:
            okp = False
        if g == 1.0 and not res:
            okp = False
    print(f"                band COMPUTED: floor g=0 must not resolve, ceiling g=1.0 must   "
          f"POSITIVE {'PASS' if okp else 'FAIL'}")
    # NEGATIVE : group-label permutation -- VALID here (D3), unlike ledger 1125/1129
    negs = {}
    both = {k: np.concatenate([A[k], B[k]]) for k in A}
    for k in A:
        d = []
        for _ in range(NDRAW):
            idx = rng.permutation(len(both[k]))
            d.append(rank_stat(both[k][idx[len(missing):]], both[k][idx[:len(missing)]]))
        negs[k] = (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)))
    print(f"     NEGATIVE   group-label permutation, {NDRAW} draws -- VALID here (D3): destroys the "
          f"grouping, preserves both marginals")
    for k in negs:
        print(f"                {k:<10} [{negs[k][0]:+.4f}, {negs[k][1]:+.4f}]")
    gate = abs(plac) < 1e-9 and okp
    out["controls"] = {"placebo": plac, "g0": g0, "dose": dose, "negative": negs, "gate": gate}

    # ================= E2 / E3 · the comparison, three estimators ==================================
    print("\n  E2/E3 - THE 110 AGAINST THE 968, THREE ESTIMATORS, MULTIPLICITY OVER THE GRID")
    print(f"     {'axis':<12}{'mean 968':>10}{'mean 110':>10}{'med 968':>9}{'med 110':>9}"
          f"{'var ratio':>11}{'rank':>9}   verdict")
    rows, cells = {}, []
    for k in ("rankings", "flags", "flag_rate"):
        a, b = A[k], B[k]
        s = rank_stat(a, b)
        lo, hi = negs[k]
        res = not (lo <= s <= hi)
        vr = float(b.var(ddof=1) / max(a.var(ddof=1), 1e-12))
        se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        mde_mean = ZEFF * se
        # rank-statistic MDE: the half-width of its own null band
        mde_rank = (hi - lo) / 2.0
        rows[k] = {"mean_a": float(a.mean()), "mean_b": float(b.mean()),
                   "med_a": float(np.median(a)), "med_b": float(np.median(b)),
                   "var_ratio": vr, "rank": s, "resolves": res,
                   "mde_mean": mde_mean, "mde_rank": mde_rank}
        cells.append((k, res))
        print(f"     {k:<12}{a.mean():>10.3f}{b.mean():>10.3f}{np.median(a):>9.1f}"
              f"{np.median(b):>9.1f}{vr:>11.2f}{s:>+9.4f}   "
              f"{'RESOLVES' if res else 'inside null'}")
    print(f"\n     ⚠ D2 in force: the variance ratio is printed above; the MEAN is reported only to "
          f"show why the RANK statistic is the estimand")
    for k, r in rows.items():
        print(f"     {k:<12} MDE mean {r['mde_mean']:>8.3f} (raw units)   MDE rank "
              f"{r['mde_rank']:.4f} (statistic units)")
    surv = sum(1 for _, r in cells if r)
    print(f"     MULTIPLICITY: primary cells {len(cells)} (3 axes x 1 rank estimator); surviving "
          f"{surv}; the mean and median columns are descriptive and not tested")
    print(f"     D1 comparison: this design n=110 vs 968 -> "
          f"{ZEFF * math.sqrt(1/110 + 1/968):.4f} SD; R783's proposed n=18 -> "
          f"{ZEFF * math.sqrt(1/18 + 1/968):.4f} SD")
    out["e2"] = rows
    out["e3"] = {"mde_sd_110": ZEFF * math.sqrt(1 / 110 + 1 / 968),
                 "mde_sd_18": ZEFF * math.sqrt(1 / 18 + 1 / 968),
                 "cells": len(cells), "surviving": surv}

    # ================= E4 · the bound ==============================================================
    print("\n  E4 - THE BIAS THIS IMPOSES ON THE ARC'S CLAIMS")
    print(f"     ⛔ STRUCTURALLY UNIDENTIFIED: the 110 have no rubric, so no rubric-derived arm has "
          f"criteria there and nothing can be scored.")
    print(f"     What IS statable: the arc's population is {len(scored)} of {len(ranked)} ranked "
          f"prompts = {len(scored)/len(ranked):.2%}, and the excluded decile "
          f"{'differs' if surv else 'does not resolvedly differ'} on {surv} of {len(cells)} axes.")
    out["e4"] = {"coverage": len(scored) / len(ranked), "axes_resolving": surv,
                 "identified": False, "would_require": "rubrics for the 110 prompts"}

    # ================= WORLD =======================================================================
    mde_sd = ZEFF * math.sqrt(1 / len(missing) + 1 / len(scored))
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif surv > 0:
        which = [k for k, r in cells if r]
        world = (f"A - THE EXCLUSION IS STRUCTURED: {surv} of {len(cells)} axes resolve against the "
                 f"group-label permutation null ({', '.join(which)}); every claim in this arc carries "
                 f"an unstated restriction to {len(scored)} of {len(ranked)} ranked prompts")
    elif mde_sd < 0.28:
        world = (f"B - THE EXCLUSION IS INCIDENTAL: no axis resolves and the design's MDE is "
                 f"{mde_sd:.4f} SD")
    else:
        world = (f"C - UNDERPOWERED: no axis resolves and the MDE is {mde_sd:.4f} SD, too coarse to "
                 f"exclude a difference that matters")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "population.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> population.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
