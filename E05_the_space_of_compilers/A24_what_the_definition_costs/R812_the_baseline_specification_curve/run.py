#!/usr/bin/env python3
"""R812 · the baseline specification curve — all 1,820 admissible baselines, not one.

R811 measured that `POOL[0:4]` sits at the 96.0th percentile of the exactly-enumerated C(16,4)=1,820
subset family. CHECK #414 established which rounds carry it: R806, R807, R808 and R809 each subtract
`yvec(POOL[p], [0,1,2,3])`. Four consecutive rounds rest on one near-best draw, and the baseline is a
defensible-choice axis never swept — realstat G4. R811's NEXT proposed swapping it for the subset
MEAN, which is one cell for another; the estimand is the whole curve.

⚠ And the obvious inference is unavailable: "extreme for the POOL's A2" does not imply "extreme for
the DERIVED slope", because a slope depends on the baseline's per-prompt COVARIANCE, not its level.

ESTIMAND        E1 R807's scale under every baseline · E2 ⭐ R809's log contrast under every baseline
                · E3 the ordering · E4 ⭐ the committed baseline's percentile in each DERIVED
                statistic's own distribution
IDENTIFICATION  exhaustive over the family; prompt bootstrap reported BESIDE the baseline spread,
                never pooled with it
DERIVED FIRST   D1 self-baseline gives margin 0 (placebo) · D2 the leak on itself is exactly 1.000
                under every baseline (positive) · D3 the baseline enters BOTH sides of a slope and
                partially cancels, so a small spread is PREDICTED and is not a null result ·
                D4 R805's +0.0553 uses all sixteen and is OUT OF SCOPE
WORLDS          A robust · B fragile · C biased point — B checked FIRST
CONTROLS        OBJECT (R807's lambda + 5 values, R809's contrast) · PLACEBO · POSITIVE with a g=0
                check · NEGATIVE (baseline permuted across prompts) · NOISE FLOOR
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
R807J = ARC / "R807_is_the_fitted_arm_a_copy_of_the_leak/results/copy_of_the_leak.json"
R809J = ARC / "R809_the_b_contrast_where_lambda_cancels/results/lambda_free.json"
PR = list(itertools.combinations(range(4), 2))
FITTED = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
HONEST = ["coval_core", "topw_k4"]
ARMS = FITTED + HONEST
NBOOT = 1200
L = "ABCD"


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


def modal(hs):
    best, bc = None, -1
    for c in {tuple(h) for h in hs}:
        n = sum(1 for h in hs if tuple(h) == c)
        if n > bc:
            best, bc = c, n
    return np.array(best)


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "a BASELINE SUBSET"}
    tg, _ = load_targets()
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    POOL = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set.intersection(*(set(v) for v in S.values())) & set(POOL) &
                  {p for p in tg if len(tg[p]) >= 2})
    H0 = {p: [np.array(cls(np.array(t[0], float)))
              for i, t in enumerate(tg[p]) if i % 2 == 0] for p in pids}
    H1 = {p: [np.array(cls(np.array(t[0], float)))
              for i, t in enumerate(tg[p]) if i % 2 == 1] for p in pids}
    pids = [p for p in pids if len(H0[p]) >= 2 and len(H1[p]) >= 1]
    N = len(pids)
    npool = len({i for i, _ in POOL[pids[0]]})
    COMBS = list(itertools.combinations(range(npool), 4))
    NC = len(COMBS)
    CIDX = COMBS.index((0, 1, 2, 3))
    print(f"  POPULATION  {N} prompts · pool of {npool} · baseline family C({npool},4) = {NC} "
          f"ENUMERATED IN FULL · the committed first-4 is index {CIDX}")

    # per-prompt pool satisfaction matrix (16 x 4) -> all 1820 subset class vectors
    print("  building the 1,820 x 4-response class vectors per prompt ...")
    CIA = np.array(COMBS)
    POOLCLS = {}
    for p in pids:
        M = np.array([[POOL[p].get((i, x), 0.0) for x in L] for i in range(npool)], float)
        Y = M[CIA].sum(axis=1)                                   # (1820, 4)
        POOLCLS[p] = np.sign(Y[:, [u for u, _ in PR]] - Y[:, [w for _, w in PR]]).astype(int)
    TGT = {p: modal(H1[p]) for p in pids}
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}

    # fixed parity-0 half-split, matching R807's seed
    rf = np.random.default_rng(20240)
    HA, HB = {}, {}
    for p in pids:
        h = H0[p]
        pm = rf.permutation(len(h))
        k = max(1, len(h) // 2)
        HA[p] = np.array([h[i] for i in pm[:k]])
        HB[p] = np.array([h[i] for i in pm[k:]]) if len(pm) > k else np.array([h[i] for i in pm[:k]])

    def a2_arm(clsmap, half):
        return np.array([float((half[p] == clsmap[p]).mean()) for p in pids])

    def a2_pool(half):
        """(N, 1820) pool A2 on the given half."""
        outm = np.zeros((N, NC))
        for i, p in enumerate(pids):
            hh = half[p]                                          # (n_ann, 6)
            outm[i] = (POOLCLS[p][None, :, :] == hh[:, None, :]).mean(axis=(0, 2))
        return outm

    print("  scoring the pool family on both halves ...")
    PA, PB = a2_pool(HA), a2_pool(HB)
    leak_A_raw = a2_arm(TGT, HA)
    leak_B_raw = a2_arm(TGT, HB)
    arm_B_raw = {a: a2_arm(CL[a], HB) for a in ARMS}

    # ================= the sweep =================================================================
    def slopes(ci):
        lk = leak_A_raw - PA[:, ci]
        lc = leak_B_raw - PB[:, ci]
        lam = np.polyfit(lk, lc, 1)[0]
        d = {a: np.polyfit(lk, arm_B_raw[a] - PB[:, ci], 1)[0] / lam for a in ARMS}
        d["_leakcopy"] = 1.0 if lam == 0 else np.polyfit(lk, lc, 1)[0] / lam
        return lam, d

    print(f"  sweeping all {NC} baselines ...")
    LAM = np.zeros(NC)
    DIS = {a: np.zeros(NC) for a in ARMS}
    LC = np.zeros(NC)
    degen = []
    for ci in range(NC):
        lam, d = slopes(ci)
        LAM[ci] = lam
        LC[ci] = d["_leakcopy"]
        for a in ARMS:
            DIS[a][ci] = d[a]
        if lam <= 0:
            degen.append(ci)
    print(f"     baselines with a degenerate lambda (<=0): {len(degen)} "
          f"({100 * len(degen) / NC:.2f}%)   "
          f"{'PASS' if len(degen) / NC <= 0.01 else 'FAIL - more than 1%, the family is mutilated'}")
    if len(degen) / NC > 0.01:
        print("  UNVERIFIED: too many degenerate baselines. Exit 2.")
        return 2
    good = np.array([i for i in range(NC) if i not in set(degen)])

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R807 at the committed first-4 baseline")
    r807 = json.loads(R807J.read_text())["e3"]
    ok = abs(LAM[CIDX] - r807["lambda_fixed"]) < 1e-6 and all(
        abs(DIS[a][CIDX] - r807["disattenuated_fixed_split"][a]) < 1e-6 for a in ARMS)
    print(f"     lambda {LAM[CIDX]:.6f} vs committed {r807['lambda_fixed']:.6f}")
    for a in ARMS:
        print(f"       {a:<18} {DIS[a][CIDX]:.6f} vs committed "
              f"{r807['disattenuated_fixed_split'][a]:.6f}")
    print(f"     {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R807 did not reproduce at its own baseline. Exit 2, never 0.")
        return 2
    out["object"] = {"lambda_committed": float(LAM[CIDX]),
                     "dis_committed": {a: float(DIS[a][CIDX]) for a in ARMS}}

    # ================= E1/E4 · the scale across the family =======================================
    print("\n  E1/E4 - R807's SCALE UNDER EVERY BASELINE   (⚠ D3 predicted a SMALL spread: the")
    print("           baseline enters BOTH sides of the slope and partially cancels)")
    print(f"     {'arm':<18}{'committed':>11}{'family mean':>13}{'sd':>8}"
          f"{'range':>20}{'percentile':>12}")
    e1 = {}
    for a in ARMS:
        v = DIS[a][good]
        pct = float((v <= DIS[a][CIDX]).mean() * 100)
        e1[a] = {"committed": float(DIS[a][CIDX]), "mean": float(v.mean()),
                 "sd": float(v.std()), "lo": float(v.min()), "hi": float(v.max()),
                 "percentile": pct}
        print(f"     {a:<18}{DIS[a][CIDX]:>11.4f}{v.mean():>13.4f}{v.std():>8.4f}"
              f"  [{v.min():.4f}, {v.max():.4f}]{pct:>11.1f}%")
    tails = [a for a in ARMS if e1[a]["percentile"] > 90 or e1[a]["percentile"] < 10]
    print(f"     ⭐ arms whose COMMITTED value sits in a tail of its own baseline distribution "
          f"(>90th or <10th): {tails if tails else 'none'}")
    out["e1"] = e1

    # ================= E3 · the ordering =========================================================
    print("\n  E3 - DOES THE ORDERING HOLD AT EVERY BASELINE?")
    fitmin = np.min([DIS[a][good] for a in FITTED], axis=0)
    honmax = np.max([DIS[a][good] for a in HONEST], axis=0)
    sep = fitmin > honmax
    print(f"     baselines where EVERY fitted arm exceeds EVERY honest arm: "
          f"{int(sep.sum())} / {len(good)}  ({100 * sep.mean():.1f}%)")
    below1 = np.max([DIS[a][good] for a in ARMS], axis=0) < 1.0
    print(f"     baselines where NO arm reaches the pure-copy ceiling of 1.000: "
          f"{int(below1.sum())} / {len(good)}  ({100 * below1.mean():.1f}%)")
    out["e3"] = {"ordering_holds": int(sep.sum()), "n": int(len(good)),
                 "below_ceiling": int(below1.sum())}

    # ================= E2 · R809's contrast across the family ====================================
    print("\n  E2 - R809's LOG CONTRAST UNDER EVERY BASELINE")
    r809 = json.loads(R809J.read_text())
    # ⛔ THE FIRST VERSION OF E2 DID NOT REPRODUCE R809 (+0.0815 against its committed -0.1317),
    # because R809 draws a FRESH parity-0 half-split inside each build(j) call (seed 90000+j) while
    # this round had reused R807's fixed split (seed 20240). A sweep of a DIFFERENT estimator
    # cannot speak to R809's verdict. Fixed: R809's own split, per j, and an OBJECT CHECK on it.
    def build_j(j):
        rng = np.random.default_rng(90000 + j)
        lkA, lcB = np.zeros(N), np.zeros(N)
        aB = {a: np.zeros(N) for a in ARMS}
        PAj, PBj = np.zeros((N, NC)), np.zeros((N, NC))
        for i, p in enumerate(pids):
            h = H0[p]
            pm = rng.permutation(len(h))
            ysz = max(1, len(h) // 2)
            Y = np.array([h[t] for t in pm[:ysz]])
            rest = [h[t] for t in pm[ysz:]] or [h[t] for t in pm[:ysz]]
            X = np.array(rest[:min(4, len(rest))])
            hs1 = H1[p]
            m = modal([hs1[t] for t in rng.permutation(len(hs1))[:min(j, len(hs1))]])
            lkA[i] = float((X == m).mean())
            lcB[i] = float((Y == m).mean())
            for a in ARMS:
                aB[a][i] = float((Y == CL[a][p]).mean())
            PAj[i] = (POOLCLS[p][None, :, :] == X[:, None, :]).mean(axis=(0, 2))
            PBj[i] = (POOLCLS[p][None, :, :] == Y[:, None, :]).mean(axis=(0, 2))
        return lkA, lcB, aB, PAj, PBj
    J = {j: build_j(j) for j in (1, 8)}

    def contrast_at(ci):
        vals = {}
        for j in (1, 8):
            lkA, lcB, aB, PAj, PBj = J[j]
            lk = lkA - PAj[:, ci]
            lam = np.polyfit(lk, lcB - PBj[:, ci], 1)[0]
            vals[j] = {a: np.polyfit(lk, aB[a] - PBj[:, ci], 1)[0] / lam for a in ARMS}
        f = np.mean([math.log(max(vals[8][a], 1e-9)) - math.log(max(vals[1][a], 1e-9))
                     for a in FITTED])
        h = np.mean([math.log(max(vals[8][a], 1e-9)) - math.log(max(vals[1][a], 1e-9))
                     for a in HONEST])
        return f - h
    anchor = contrast_at(CIDX)
    e2ok = abs(anchor - r809["e2"]["contrast"]) < 1e-6
    print(f"     OBJECT CHECK on E2: contrast at the committed baseline {anchor:+.6f} vs R809's "
          f"committed {r809['e2']['contrast']:+.6f}   {'PASS' if e2ok else 'FAIL'}")
    if not e2ok:
        print("     ⚠ E2 is UNVERIFIED: this sweep is not R809's estimator and cannot speak to its")
        print("       verdict. The curve below is reported as a property of THIS estimator only.")
    lg = np.array([contrast_at(ci) for ci in good])
    com = float(lg[list(good).index(CIDX)])
    neg_share = float((lg < 0).mean())
    print(f"     committed value {com:+.4f} (R809 committed {r809['e2']['contrast']:+.4f})")
    print(f"     family: mean {lg.mean():+.4f}  sd {lg.std():.4f}  range [{lg.min():+.4f}, "
          f"{lg.max():+.4f}]   percentile of committed {100 * (lg <= com).mean():.1f}%")
    print(f"     ⭐ baselines where the contrast is NEGATIVE (R809's direction): "
          f"{100 * neg_share:.1f}%   POSITIVE: {100 * (1 - neg_share):.1f}%")
    flip = 0.02 < neg_share < 0.98
    print(f"     sign flips somewhere in the family: {flip}")
    out["e2"] = {"committed": com, "mean": float(lg.mean()), "sd": float(lg.std()),
                 "lo": float(lg.min()), "hi": float(lg.max()), "negative_share": neg_share,
                 "sign_flips": flip}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    selfm = max(abs(float(((arm_B_raw["coval_core"] - arm_B_raw["coval_core"])).max())), 0.0)
    plac_ok = selfm == 0.0
    print(f"     PLACEBO   D1 an arm minus ITSELF as baseline, max |margin|: {selfm:.1e}   "
          f"{'PASS - identically 0' if plac_ok else 'FAIL'}")
    dev = float(np.max(np.abs(LC[good] - 1.0)))
    pos_ok = dev < 1e-9
    print(f"     POSITIVE  D2 `_perfect_leak` on itself under all {len(good)} baselines, max "
          f"deviation from 1.000: {dev:.1e}   {'PASS' if pos_ok else 'FAIL'}")
    hon_at_1 = float(np.max([np.abs(DIS[a][good] - 1.0).min() for a in HONEST]))
    g0_ok = hon_at_1 > 0.1
    print(f"     g=0 CHECK the honest arms must NOT sit at 1.000: closest approach "
          f"{1.0 - max(DIS[a][good].max() for a in HONEST):.3f} away   "
          f"{'PASS - the control can fail' if g0_ok else 'FAIL'}")
    rngn = np.random.default_rng(505)
    nulls = []
    for _ in range(200):
        pm = rngn.permutation(N)
        lk = leak_A_raw - PA[pm, CIDX]
        lc = leak_B_raw - PB[pm, CIDX]
        lam = np.polyfit(lk, lc, 1)[0]
        if lam == 0:
            continue
        nulls.append(float(np.polyfit(lk, arm_B_raw["oracle_k4_fit1"] - PB[pm, CIDX], 1)[0] / lam))
    nulls = np.array(nulls)
    real_sd = float(DIS["oracle_k4_fit1"][good].std())
    rlo, rhi = float(DIS["oracle_k4_fit1"][good].min()), float(DIS["oracle_k4_fit1"][good].max())
    # ⛔ THE FIRST CRITERION COMPARED SDs and asserted permuting must move the scale "far more".
    # That was never derived: the family's sd is variation across 1,820 DIFFERENT SUBSETS while the
    # permuted sd is variation across draws of ONE subset's misassigned values — two different
    # sources with no ordering between them. It printed FAIL (0.0223 vs 0.0229) while the control
    # had in fact separated perfectly. realstat §4, "the control targets a different statistic than
    # the one being reported". The statistic that matches the claim is DISJOINTNESS: a permuted
    # baseline must put the scale somewhere no REAL baseline can reach.
    neg_ok = bool(nulls.min() > rhi or nulls.max() < rlo)
    print(f"     NEGATIVE  the baseline's per-prompt values PERMUTED across prompts, 200 draws: "
          f"range [{nulls.min():.3f}, {nulls.max():.3f}]  sd {nulls.std():.4f}")
    print(f"               the REAL baseline family spans [{rlo:.3f}, {rhi:.3f}]  sd {real_sd:.4f}")
    print(f"               DISJOINT: {neg_ok}   "
          f"{'PASS - no real baseline can reach where permuting puts it' if neg_ok else 'FAIL'}")
    rngb = np.random.default_rng(1234)
    BI = rngb.integers(0, N, (400, N))
    lk0 = leak_A_raw - PA[:, CIDX]
    lc0 = leak_B_raw - PB[:, CIDX]
    bs = np.array([np.polyfit(lk0[i], arm_B_raw["oracle_k4_fit1"][i] - PB[i, CIDX], 1)[0]
                   / np.polyfit(lk0[i], lc0[i], 1)[0] for i in BI])
    print(f"     NOISE FLOOR  prompt bootstrap at the committed baseline: sd {bs.std():.4f}   "
          f"vs the BASELINE-family sd {real_sd:.4f}  -- reported side by side, never pooled")
    gate = ok and plac_ok and pos_ok and g0_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "positive_dev": dev, "positive_ok": pos_ok,
                       "g0_ok": g0_ok, "null_sd": float(nulls.std()), "family_sd": real_sd,
                       "negative_ok": neg_ok, "bootstrap_sd": float(bs.std()), "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    ordering_flips = int(sep.sum()) < len(good)
    ceiling_flips = int(below1.sum()) < len(good)
    any_flip = flip or ordering_flips or ceiling_flips
    if not gate:
        world = "UNVERIFIED"
    elif any_flip:
        world = "B"
    elif tails:
        world = "C"
    else:
        world = "A"
    print(f"     verdict flips — R809 contrast sign: {flip} · fitted>honest ordering: "
          f"{ordering_flips} · no arm at the ceiling: {ceiling_flips}")
    print(f"     committed value in a tail of its own distribution: {tails if tails else 'none'}")
    print(f"     -> WORLD {world}")
    out["world"] = world

    art = HERE / "results/baseline_curve.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
