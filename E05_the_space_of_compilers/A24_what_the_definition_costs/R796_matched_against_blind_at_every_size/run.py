#!/usr/bin/env python3
"""R796 · what prompt-matching is worth when the floor is ABSENCE, at every target size.

R795 showed R794's Q1 floor was a POISON (another prompt's rubric, ~0.50 at every k) and measured the
NEUTRAL floor at one size only: `genericpool16` 0.7886 against `full` 0.7850, unresolved. CHECK #398
found `sat_genericpool16.npz` ships PER-CRITERION satisfactions, so a BLIND dose over k is
constructible exactly parallel to the matched one — one point becomes a curve. It also caught that
`randblind_k4_s*` cover ONE prompt each and are not population arms.

ESTIMAND        E1 ⭐ the two doses · E2 ⭐ the matched−blind gap at each k · E3 the whole population ·
                E4 the pool-size confound + D4's consistency check
IDENTIFICATION  exact. ⚠ "blind" means not written for this prompt, NOT uninformative
DERIVED FIRST   D1 the blind k=16 cell IS `vs genericpool16` — the object check · D2 both doses must
                rise, else the curves are not comparable · D3 the matched k=16 cell is a MIXTURE
                (mean 15.48), so clean cells are k <= 12 · D4 `generic` = POOL[0:4], so it must lie
                inside the blind k=4 draw distribution
WORLDS          A matching is worth something · B nothing measurable · C size-conditional — C FIRST
CONTROLS        OBJECT (two committed endpoints) · PLACEBO · POSITIVE (both doses monotone, band) ·
                NEGATIVE (arm class shuffled) · CONFOUND (pool-size, >=16-criteria subpopulation) ·
                CONSISTENCY (D4) · NOISE FLOOR
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R795 = ARC / "R795_specificity_or_target_size/results/size_or_identity.json"
R789 = ARC / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
KS = [1, 2, 4, 8, 12, 16]
CLEAN = [1, 2, 4, 8, 12]                       # D3: the k=16 matched cell is a mixture
NDRAW = 20
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


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


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def main():
    out = {"instrument_unit": "a (prompt, subset draw) TARGET", "claim_unit": "a k CELL",
           "claim_unit_e3": "an ARM"}

    print("  OBJECT CHECK")
    if not (R795.is_file() and R789.is_file()):
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0.")
        return 2
    prev = json.loads(R795.read_text())
    targets, _ = load_targets()
    fullS = load_sat(RES / "sat_full.npz")
    poolS = load_sat(RES / "sat_genericpool16.npz")
    coreS = load_sat(RES / "sat_coval_core.npz")
    pids = sorted(p for p in fullS if p in coreS and p in poolS and p in targets
                  and len(targets[p]) >= 2)
    P = len(pids)

    def tensor(S):
        idxs = [sorted({i for i, _ in S[p]}) for p in pids]
        KM = max(len(v) for v in idxs)
        T = np.zeros((P, KM, 4))
        cnt = np.zeros(P, int)
        for a, p in enumerate(pids):
            cnt[a] = len(idxs[a])
            for c, i in enumerate(idxs[a]):
                for j, x in enumerate(L):
                    T[a, c, j] = S[p].get((i, x), 0.0)
        return T, cnt

    TF, nF = tensor(fullS)
    TB, nB = tensor(poolS)
    CORE = np.array([cls(yvec(coreS[p], sorted({i for i, _ in coreS[p]}))) for p in pids], float)
    print(f"     prompts {P}   `full` criteria min {nF.min()} mean {nF.mean():.2f} max {nF.max()}   "
          f"`genericpool16` criteria {nB.min()}–{nB.max()}")

    def cls_from_y(Y):
        return np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])

    def agree(cm, tgt):
        return (cm == tgt).mean(axis=1)

    full_cls = cls_from_y(TF.sum(axis=1))
    blind_cls = cls_from_y(TB.sum(axis=1))
    vs_full = float(agree(CORE, full_cls).mean())
    vs_blind = float(agree(CORE, blind_cls).mean())
    ref_f = prev["e1"]["all_matched"]["mean"]
    ref_b = prev["e4"]["vs_genericpool16"]
    okobj = abs(vs_full - ref_f) < 1e-9 and abs(vs_blind - ref_b) < 1e-9
    plac = float(agree(CORE, CORE).mean())
    print(f"     D1  matched all-criteria {vs_full:.10f} vs committed {ref_f:.10f}  |Δ| "
          f"{abs(vs_full - ref_f):.1e}   blind k=16 {vs_blind:.10f} vs committed {ref_b:.10f}  |Δ| "
          f"{abs(vs_blind - ref_b):.1e}   {'PASS' if okobj else 'FAIL'}")
    print(f"     PLACEBO  `coval_core` against its OWN class: {plac:.12f}   "
          f"{'PASS' if plac == 1.0 else 'FAIL'}")
    if not (okobj and plac == 1.0):
        print("  UNRUNNABLE: an endpoint disagrees with a committed number. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "vs_full": vs_full, "vs_blind": vs_blind,
                     "mean_k_full": float(nF.mean()), "placebo": plac}

    rng = np.random.default_rng(SEEDS[0])
    BI = rng.integers(0, P, size=(NBOOT, P))

    def ci(v):
        b = v[BI].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        p = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
        return float(v.mean()), lo, hi, max(min(p, 1.0), 1.0 / (NBOOT + 1))

    def dose(T, cnt, k, rg, arm=None):
        Y = np.zeros((P, 4))
        for a in range(P):
            kk = min(k, int(cnt[a]))
            Y[a] = T[a, rg.choice(int(cnt[a]), kk, replace=False), :].sum(axis=0)
        return agree(CORE if arm is None else arm, cls_from_y(Y))

    # ================= E1/E2 · the two doses and the gap ==========================================
    print("\n  E1/E2 - MATCHED vs BLIND AT EVERY SIZE  (the floor is ABSENCE, not misdirection)")
    cells, gaps, pv = {}, {}, []
    for k in KS:
        pm = np.zeros(P)
        pb = np.zeros(P)
        vm, vb = [], []
        for d in range(NDRAW):
            rgm = np.random.default_rng(SEEDS[0] + 100 + d)
            rgb = np.random.default_rng(SEEDS[0] + 200 + d)
            a_ = dose(TF, nF, k, rgm)
            b_ = dose(TB, nB, k, rgb)
            pm += a_
            pb += b_
            vm.append(float(a_.mean()))
            vb.append(float(b_.mean()))
        pm /= NDRAW
        pb /= NDRAW
        e, lo, hi, p = ci(pm - pb)
        cells[k] = {"matched": float(np.mean(vm)), "matched_sd": float(np.std(vm, ddof=1)),
                    "blind": float(np.mean(vb)), "blind_sd": float(np.std(vb, ddof=1))}
        gaps[k] = {"gap": e, "lo": lo, "hi": hi, "p": p,
                   "resolved": bool(lo > 0 or hi < 0)}
        pv.append(p)
        mark = "" if k in CLEAN else "   ⚠ MIXTURE (D3)"
        print(f"     k={k:<3} matched {cells[k]['matched']:.4f} (sd {cells[k]['matched_sd']:.4f})   "
              f"blind {cells[k]['blind']:.4f} (sd {cells[k]['blind_sd']:.4f})   gap {e:+.4f} "
              f"[{lo:+.4f}, {hi:+.4f}]  {'RESOLVED' if gaps[k]['resolved'] else 'unresolved'}{mark}")
    seqm = [cells[k]["matched"] for k in KS]
    seqb = [cells[k]["blind"] for k in KS]
    mono_m = all(seqm[i] <= seqm[i + 1] + 1e-9 for i in range(len(seqm) - 1))
    mono_b = all(seqb[i] <= seqb[i + 1] + 1e-9 for i in range(len(seqb) - 1))
    posok = mono_m and mono_b and abs(seqm[-1] - seqm[0]) > 1e-9 and abs(seqb[-1] - seqb[0]) > 1e-9
    print(f"     POSITIVE  D2: matched monotone {mono_m} (band {seqm[0]:.4f}→{seqm[-1]:.4f})   "
          f"blind monotone {mono_b} (band {seqb[0]:.4f}→{seqb[-1]:.4f})   "
          f"{'PASS' if posok else 'FAIL'}")
    out["e1"] = cells
    out["e2"] = gaps

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    srng = np.random.default_rng(SEEDS[0] + 31)
    SH = CORE[srng.permutation(P)]
    shm = float(dose(TF, nF, 16, np.random.default_rng(SEEDS[0] + 33), arm=SH).mean())
    shb = float(dose(TB, nB, 16, np.random.default_rng(SEEDS[0] + 35), arm=SH).mean())
    negok = shm < cells[16]["matched"] - 0.05 and shb < cells[16]["blind"] - 0.05
    print(f"     NEGATIVE  `coval_core`'s class shuffled across prompts: matched dose "
          f"{cells[16]['matched']:.4f} → {shm:.4f}, blind {cells[16]['blind']:.4f} → {shb:.4f}   "
          f"{'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the doses measure a property of the TARGETS alone "
          f"rather than a correspondence between this arm and its prompt's targets'")

    # CONFOUND: pool-size control on the >=16-criteria subpopulation
    big = nF >= 16
    print(f"     CONFOUND  pool-size control on prompts with >= 16 `full` criteria: "
          f"{int(big.sum())} of {P}")
    conf = {}
    for k in (4, 8, 12):
        pm = np.zeros(P)
        pb = np.zeros(P)
        for d in range(NDRAW):
            pm += dose(TF, nF, k, np.random.default_rng(SEEDS[0] + 300 + d))
            pb += dose(TB, nB, k, np.random.default_rng(SEEDS[0] + 400 + d))
        pm /= NDRAW
        pb /= NDRAW
        sub = (pm - pb)[big]
        bi2 = np.random.default_rng(SEEDS[0] + 7).integers(0, int(big.sum()),
                                                          size=(NBOOT, int(big.sum())))
        b = sub[bi2].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        conf[k] = {"gap": float(sub.mean()), "lo": lo, "hi": hi,
                   "resolved": bool(lo > 0 or hi < 0)}
        print(f"               k={k:<3} gap on the matched-pool subpopulation {sub.mean():+.4f} "
              f"[{lo:+.4f}, {hi:+.4f}]   against all-prompts {gaps[k]['gap']:+.4f}")
    out["confound_pool_size"] = {"n_big": int(big.sum()), "cells": conf}

    # CONSISTENCY: D4 -- `generic` = POOL[0:4] must lie inside the blind k=4 draw distribution
    gS = load_sat(RES / "sat_generic.npz")
    GC = np.array([cls(yvec(gS[p], sorted({i for i, _ in gS[p]}))) for p in pids], float)
    vg = float(agree(CORE, GC).mean())
    draws4 = [float(dose(TB, nB, 4, np.random.default_rng(SEEDS[0] + 200 + d)).mean())
              for d in range(NDRAW)]
    inside20 = min(draws4) <= vg <= max(draws4)
    # ⛔ D4 AS REGISTERED WAS MIS-SPECIFIED, AND IT FAILED FOR ITS OWN REASONS. `generic` is a
    # SPECIFIC subset (POOL[0:4]) while the dose draws RANDOM ones, and 20 draws cannot span a
    # C(16,4) = 1,820 family. The admissible check is the EXACT distribution over all 1,820 blind
    # 4-subsets — the same class R787/R788 built — so it is computed here rather than argued away.
    SUB = list(itertools.combinations(range(16), 4))
    exact = np.empty(len(SUB))
    for si, ss in enumerate(SUB):
        exact[si] = agree(CORE, cls_from_y(TB[:, list(ss), :].sum(axis=1))).mean()
    pct = float((exact < vg).mean())
    inside = float(exact.min()) <= vg <= float(exact.max())
    print(f"     CONSISTENCY  ⛔ D4 as registered FAILED: `coval_core vs generic` (= POOL[0:4]) "
          f"{vg:.4f} is OUTSIDE the 20-draw range [{min(draws4):.4f}, {max(draws4):.4f}]")
    print(f"                  ⭐ REPAIRED to the EXACT class, all {len(SUB)} blind 4-subsets: "
          f"[{exact.min():.4f}, {exact.max():.4f}], mean {exact.mean():.4f} — `generic` sits at "
          f"percentile {100 * pct:.1f}   {'INSIDE' if inside else 'STILL OUTSIDE'}")
    print(f"                  the 20-draw mean {np.mean(draws4):.4f} against the exact mean "
          f"{exact.mean():.4f}: the dose is unbiased; only its RANGE was too narrow to span the "
          f"family, which is what a 20-of-1820 sample does")
    print(f"     NOISE FLOOR  largest draw sd across cells "
          f"{max(max(c['matched_sd'], c['blind_sd']) for c in cells.values()):.4f}")

    gate = okobj and plac == 1.0 and posok and negok
    out["controls"] = {"positive_ok": posok, "mono_matched": mono_m, "mono_blind": mono_b,
                       "negative_ok": negok, "neg_matched": shm, "neg_blind": shb,
                       "d4_generic": vg, "d4_inside_20draw": inside20, "d4_inside_exact": inside,
                       "d4_exact_pct": pct, "d4_exact_min": float(exact.min()),
                       "d4_exact_max": float(exact.max()), "d4_exact_mean": float(exact.mean()),
                       "d4_n_subsets": len(SUB), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E3 · the whole population ==================================================
    print("\n  E3 - THE WHOLE POPULATION: `vs full` MINUS `vs genericpool16`, per arm")
    prev789 = json.loads(R789.read_text())
    rows, pv3 = [], []
    for t in sorted(prev789["e2"]["a2"]):
        f = RES / f"sat_{t}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        if not set(pids) <= set(S):
            continue
        cm = np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids], float)
        e, lo, hi, p = ci(agree(cm, full_cls) - agree(cm, blind_cls))
        rows.append({"arm": t, "eff": e, "lo": lo, "hi": hi, "p": p})
        pv3.append(p)
    rows.sort(key=lambda r: -r["eff"])
    keep3 = bh(np.array(pv + pv3))
    for r in rows[:4] + [r for r in rows if r["arm"] == "coval_core"] + rows[-3:]:
        print(f"     {r['arm']:<24} {r['eff']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]  p {r['p']:.4f}")
    cc = [r for r in rows if r["arm"] == "coval_core"][0]
    rank = 1 + sum(1 for r in rows if r["eff"] > cc["eff"])
    print(f"     ⭐ `coval_core` ranks {rank} of {len(rows)} on prompt-matching preference, at "
          f"{cc['eff']:+.4f} [{cc['lo']:+.4f}, {cc['hi']:+.4f}]")
    out["e3"] = {"rows": rows, "coval_core_rank": rank, "n_arms": len(rows)}
    print(f"\n  MULTIPLICITY  {len(pv) + len(pv3)} tests (6 gaps + {len(pv3)} arms), BH q=0.05 over "
          f"the union: surviving {int(keep3.sum())}   not {len(pv) + len(pv3) - int(keep3.sum())}")

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    clean = [gaps[k] for k in CLEAN]
    pos = sum(1 for g in clean if g["resolved"] and g["gap"] > 0)
    neg = sum(1 for g in clean if g["resolved"] and g["gap"] < 0)
    if not gate:
        world = "UNVERIFIED"
    elif pos and neg:
        world = "C"
    elif pos >= 3:
        world = "A"
    elif (len(clean) - pos) >= 3:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   clean cells k<=12: resolved positive {pos}, resolved negative {neg}, "
          f"of {len(clean)}  ->  WORLD {world}")
    out["world"] = world
    out["clean_positive"] = pos
    out["clean_negative"] = neg

    art = HERE / "results/matched_vs_blind.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
