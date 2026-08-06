#!/usr/bin/env python3
"""R809 · the B contrast on a scale where lambda cancels.

R808 returned B-SPECIFIC on an ADDITIVE contrast (+0.094 vs a 0.079 threshold, ratio 1.19) and
flagged it as marginal. CHECK #411 found the arithmetic before the bootstrap: every disattenuated
value is raw/lambda_j and lambda_j FALLS with j (0.5834 -> 0.4954), so every j=8 value carries a
common multiplicative inflation and an arm STARTING HIGHER collects a bigger absolute rise for free.
That is the multiplicative trap for the third time in four rounds. lambda_j is common to all arms,
so it cancels exactly in a difference of LOGS — which is the identified estimand.

ESTIMAND        E1 the additive contrast (R808's NEXT as posed) · E2 ⭐ PRIMARY the log contrast,
                lambda-free by derivation · E3 a calibrated j-sensitivity scale · E4 level vs rise
IDENTIFICATION  E2 identified; E1 confounded by the common lambda_j and reported as E2's contrast
DERIVED FIRST   D1 the pure leak copy's log-rise is exactly 0 (placebo) · D2 `_target_full` is what
                the proxy converges to, so its log-rise is the ceiling (positive) · D3 if the two
                scales disagree, the disagreement IS the finding · D4 lambda_j must fall with j or
                this round's premise is wrong
WORLDS          A B-SPECIFIC survives · B B-SPECIFIC withdrawn · C unverified — B checked FIRST
CONTROLS        OBJECT (R808's whole B table) · PLACEBO · POSITIVE with a g=0 check · NEGATIVE
                (200-permutation null, not a bootstrap around one draw) · NOISE FLOOR
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
R808J = ARC / "R808_does_the_scale_survive_its_own_precision/results/precision_sweep.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
FITTED = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
HONEST = ["coval_core", "topw_k4"]
ARMS = FITTED + HONEST
JS = [1, 2, 4, 8]
SPLITS = 20


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


def modal(hs):
    best, bc = None, -1
    for c in {tuple(h) for h in hs}:
        n = sum(1 for h in hs if tuple(h) == c)
        if n > bc:
            best, bc = c, n
    return np.array(best)


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "an ARM's RISE across j"}
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
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    BL = {p: np.array(cls(yvec(POOL[p], [0, 1, 2, 3]))) for p in pids}
    TGT = {p: modal(H1[p]) for p in pids}                      # the fitted arms' actual fit target
    print(f"  POPULATION  {N} prompts")

    def build(j, rng):
        """x-side = 4 parity-0 annotators; y-side = a fixed half. Leak's class from j parity-1."""
        lk = np.zeros(N); lc = np.zeros(N); tf = np.zeros(N)
        arm = {a: np.zeros(N) for a in ARMS}
        for i, p in enumerate(pids):
            h = H0[p]
            pm = rng.permutation(len(h))
            ysz = max(1, len(h) // 2)
            Y = np.array([h[t] for t in pm[:ysz]])
            rest = [h[t] for t in pm[ysz:]] or [h[t] for t in pm[:ysz]]
            X = np.array(rest[:min(4, len(rest))])
            hs1 = H1[p]
            m = modal([hs1[t] for t in rng.permutation(len(hs1))[:min(j, len(hs1))]])
            bY, bX = (Y == BL[p]).mean(), (X == BL[p]).mean()
            lk[i] = (X == m).mean() - bX
            lc[i] = (Y == m).mean() - bY
            tf[i] = (Y == TGT[p]).mean() - bY
            for a in ARMS:
                arm[a][i] = (Y == CL[a][p]).mean() - bY
        return lk, lc, tf, arm

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R808's whole B-axis table")
    r808 = json.loads(R808J.read_text())["b_axis"]
    POINT = {}
    for j in JS:
        reps = [build(j, np.random.default_rng(7000 + j * 31 + s)) for s in range(SPLITS)]
        lam = float(np.mean([np.polyfit(lk, lc, 1)[0] for lk, lc, _, _ in reps]))
        dis = {a: float(np.mean([np.polyfit(lk, ar[a], 1)[0] / np.polyfit(lk, lc, 1)[0]
                                 for lk, lc, _, ar in reps])) for a in ARMS}
        tfd = float(np.mean([np.polyfit(lk, tf, 1)[0] / np.polyfit(lk, lc, 1)[0]
                             for lk, lc, tf, _ in reps]))
        POINT[j] = {"lambda": lam, "dis": dis, "target_full": tfd}
    ok = all(abs(POINT[j]["lambda"] - r808[str(j)]["lambda"]) < 1e-6 for j in JS) and all(
        abs(POINT[j]["dis"][a] - r808[str(j)]["dis"][a]) < 1e-6 for j in JS for a in ARMS)
    print(f"     {'j':>3}{'lambda':>10}" + "".join(f"{a.split('_')[0]:>11}" for a in ARMS)
          + f"{'target_full':>13}")
    for j in JS:
        print(f"     {j:>3}{POINT[j]['lambda']:>10.4f}" +
              "".join(f"{POINT[j]['dis'][a]:>11.3f}" for a in ARMS)
              + f"{POINT[j]['target_full']:>13.3f}")
    print(f"     all 4 lambdas and all 20 disattenuated cells match R808 to 1e-6: {ok}   "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R808's B table did not reproduce. Exit 2, never 0.")
        return 2
    d4 = all(POINT[JS[i]]["lambda"] >= POINT[JS[i + 1]]["lambda"] - 1e-12
             for i in range(len(JS) - 1))
    print(f"     D4 lambda_j FALLS with j: {d4}   "
          f"{'PASS - the round premise holds' if d4 else 'FAIL - the premise is wrong and this round says so'}")
    out["object"] = {"point": POINT, "matches_r808": ok, "d4_lambda_falls": d4}

    # ================= the paired bootstrap ======================================================
    print("\n  E1/E2 - THE CONTRAST ON BOTH SCALES, PAIRED BOOTSTRAP OVER PROMPTS")
    rng = np.random.default_rng(31337)
    V = {j: build(j, np.random.default_rng(90000 + j)) for j in (1, 8)}
    BI = rng.integers(0, N, (NBOOT, N))

    def cell(j, idx):
        lk, lc, tf, arm = V[j]
        lam = np.polyfit(lk[idx], lc[idx], 1)[0]
        d = {a: np.polyfit(lk[idx], arm[a][idx], 1)[0] / lam for a in ARMS}
        d["_target_full"] = np.polyfit(lk[idx], tf[idx], 1)[0] / lam
        d["_leakcopy"] = np.polyfit(lk[idx], lc[idx], 1)[0] / lam
        return d

    ALL = ARMS + ["_target_full", "_leakcopy"]
    base = {j: cell(j, np.arange(N)) for j in (1, 8)}
    nonpos = [(a, j) for a in ALL for j in (1, 8) if base[j][a] <= 0]
    print(f"     cells with a non-positive disattenuated value (log undefined): {len(nonpos)} "
          f"{nonpos if nonpos else '- none, the log estimand is defined everywhere'}")
    if len(nonpos) > 1:
        print("  UNVERIFIED: more than one arm has an undefined log cell. Exit 2.")
        return 2
    add_bs, log_bs = [], []
    per_add, per_log = {a: [] for a in ALL}, {a: [] for a in ALL}
    for i in BI:
        c1, c8 = cell(1, i), cell(8, i)
        for a in ALL:
            per_add[a].append(c8[a] - c1[a])
            per_log[a].append(math.log(max(c8[a], 1e-9)) - math.log(max(c1[a], 1e-9)))
        fa = np.mean([c8[a] - c1[a] for a in FITTED])
        ha = np.mean([c8[a] - c1[a] for a in HONEST])
        fl = np.mean([math.log(max(c8[a], 1e-9)) - math.log(max(c1[a], 1e-9)) for a in FITTED])
        hl = np.mean([math.log(max(c8[a], 1e-9)) - math.log(max(c1[a], 1e-9)) for a in HONEST])
        add_bs.append(fa - ha)
        log_bs.append(fl - hl)
    add_bs, log_bs = np.array(add_bs), np.array(log_bs)
    A_pt = float(np.mean([base[8][a] - base[1][a] for a in FITTED])
                 - np.mean([base[8][a] - base[1][a] for a in HONEST]))
    L_pt = float(np.mean([math.log(base[8][a] / base[1][a]) for a in FITTED])
                 - np.mean([math.log(base[8][a] / base[1][a]) for a in HONEST]))
    alo, ahi = float(np.percentile(add_bs, 2.5)), float(np.percentile(add_bs, 97.5))
    llo, lhi = float(np.percentile(log_bs, 2.5)), float(np.percentile(log_bs, 97.5))
    print(f"     {'arm':<16}{'j=1':>8}{'j=8':>8}{'additive':>11}{'log':>9}{'ratio':>8}")
    for a in ALL:
        r = base[8][a] / base[1][a]
        print(f"     {a:<16}{base[1][a]:>8.3f}{base[8][a]:>8.3f}"
              f"{base[8][a] - base[1][a]:>+11.3f}{math.log(r):>+9.3f}{r:>8.3f}")
    print(f"\n     E1 ADDITIVE contrast (R808's NEXT as posed): {A_pt:+.4f} [{alo:+.4f}, {ahi:+.4f}]"
          f"   {'EXCLUDES 0' if (alo > 0 or ahi < 0) else 'contains 0'}")
    print(f"     ⭐ E2 LOG contrast (lambda cancels by derivation): {L_pt:+.4f} "
          f"[{llo:+.4f}, {lhi:+.4f}]   {'EXCLUDES 0' if (llo > 0 or lhi < 0) else 'CONTAINS 0'}")
    out["e1"] = {"contrast": A_pt, "lo": alo, "hi": ahi}
    out["e2"] = {"contrast": L_pt, "lo": llo, "hi": lhi,
                 "per_arm": {a: {"j1": base[1][a], "j8": base[8][a],
                                 "additive": base[8][a] - base[1][a],
                                 "log": math.log(base[8][a] / base[1][a])} for a in ALL}}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = math.log(base[8]["_leakcopy"] / base[1]["_leakcopy"])
    plac_ok = abs(plac) < 1e-9
    print(f"     PLACEBO   the pure leak copy's log-rise: {plac:+.9f}   "
          f"{'PASS - exactly 0' if plac_ok else 'FAIL'}")
    tf_log = math.log(base[8]["_target_full"] / base[1]["_target_full"])
    arm_logs = {a: math.log(base[8][a] / base[1][a]) for a in ARMS}
    pos_ok = tf_log > max(arm_logs.values())
    print(f"     POSITIVE  `_target_full` (the fitted arms' ACTUAL fit target) log-rise "
          f"{tf_log:+.4f}   largest of any arm (next {max(arm_logs.values()):+.4f} = "
          f"{max(arm_logs, key=arm_logs.get)})   {'PASS' if pos_ok else 'FAIL'}")
    hon_log = float(np.mean([arm_logs[a] for a in HONEST]))
    print(f"     g=0 CHECK the placebo must NOT rise, and does not ({plac:+.9f}); band "
          f"floor {hon_log:+.4f} < fitted < ceiling {tf_log:+.4f}")
    # ⛔ THE FIRST NEGATIVE CONTROL DESTROYED NOTHING. It permuted lk8[pm] AND arm8[a][pm] with
    # the SAME permutation — and a regression slope is invariant to reordering (x,y) PAIRS. The
    # null came back as a point mass exactly equal to the observation, [-0.1317, -0.1317], which
    # is the signature of a permutation that did not permute. realstat §4, "the control fails for
    # its own reasons". The structure this estimand rests on is the ARM-LABEL split, so that is
    # what the null must destroy — and with 5 arms it is EXACTLY enumerable, not sampled.
    splits = [c for c in itertools.combinations(ARMS, 3)]
    lab_null = []
    for c in splits:
        f_ = [a_ for a_ in ARMS if a_ in c]
        h_ = [a_ for a_ in ARMS if a_ not in c]
        lab_null.append(float(np.mean([arm_logs[a_] for a_ in f_])
                              - np.mean([arm_logs[a_] for a_ in h_])))
    lab_null = np.array(lab_null)
    rank = int((lab_null <= L_pt).sum())
    nlo, nhi = float(lab_null.min()), float(lab_null.max())
    neg_ok = bool(nlo < nhi)          # the null must have SPREAD, or it destroyed nothing
    print(f"     NEGATIVE  ARM-LABEL permutation, EXACT over all {len(splits)} ways to split 5 arms "
          f"3/2: null [{nlo:+.4f}, {nhi:+.4f}]")
    print(f"               the real fitted/honest split ranks {rank} of {len(splits)} "
          f"(observed {L_pt:+.4f})   "
          f"{'PASS - the null has spread' if neg_ok else 'FAIL - destroyed nothing'}")
    sds = []
    for s in range(SPLITS):
        Vs = {j: build(j, np.random.default_rng(60000 + j * 7 + s)) for j in (1, 8)}
        def c2(j):
            lk, lc, tf, arm = Vs[j]
            lam = np.polyfit(lk, lc, 1)[0]
            return {a: np.polyfit(lk, arm[a], 1)[0] / lam for a in ARMS}
        b1, b8 = c2(1), c2(8)
        sds.append(np.mean([math.log(b8[a] / b1[a]) for a in FITTED])
                   - np.mean([math.log(b8[a] / b1[a]) for a in HONEST]))
    NF = float(np.std(sds))
    print(f"     NOISE FLOOR  across {SPLITS} independent splits, sd of the LOG contrast: {NF:.4f}"
          f"   (the contrast is {abs(L_pt) / NF:.2f}x it)")
    gate = ok and plac_ok and pos_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "placebo_ok": plac_ok, "target_full_log": tf_log,
                       "positive_ok": pos_ok, "null_lo": nlo, "null_hi": nhi,
                       "label_null": lab_null.tolist(), "rank": rank, "n_splits": len(splits),
                       "negative_ok": neg_ok, "noise_floor": NF, "gate": gate}

    # ================= E3/E4 ====================================================================
    print("\n  E3 - THE CALIBRATED j-SENSITIVITY SCALE")
    print(f"     floor (honest arms) {hon_log:+.4f}   ceiling (`_target_full`) {tf_log:+.4f}")
    pos = {a: (arm_logs[a] - hon_log) / (tf_log - hon_log) for a in ARMS}
    for a in FITTED:
        if arm_logs[a] < hon_log:
            print(f"        {a:<18} log-rise {arm_logs[a]:+.4f}  ->  BELOW THE HONEST FLOOR "
                  f"({hon_log:+.4f}); the 'percent of the way to the ceiling' framing does not "
                  f"apply and no percentage is quoted")
        else:
            print(f"        {a:<18} log-rise {arm_logs[a]:+.4f}  ->  {100 * pos[a]:5.1f}% of the "
                  f"way from the honest floor to its own fit target")
    pv = [float(2 * min((np.array(per_log[a]) <= 0).mean(), (np.array(per_log[a]) >= 0).mean()))
          for a in ARMS]
    keep = bh(pv)
    print(f"     BH q=0.05 over {len(pv)} per-arm log-rises: {int(keep.sum())} survive, "
          f"{len(pv) - int(keep.sum())} do not — " +
          ", ".join(f"{a}{'' if k else ' (NOT)'}" for a, k in zip(ARMS, keep)))
    print("\n  E4 - HOW MUCH OF R808's +0.094 WAS LEVEL RATHER THAN RISE")
    fit1 = float(np.mean([base[1][a] for a in FITTED]))
    hon1 = float(np.mean([base[1][a] for a in HONEST]))
    print(f"     fitted arms START at {fit1:.3f}, honest at {hon1:.3f} — a ratio of "
          f"{fit1 / hon1:.2f}x before anything is measured about RISING.")
    print(f"     on the additive scale the rises are {np.mean([base[8][a] - base[1][a] for a in FITTED]):+.3f} "
          f"vs {np.mean([base[8][a] - base[1][a] for a in HONEST]):+.3f} — a ratio of "
          f"{np.mean([base[8][a] - base[1][a] for a in FITTED]) / np.mean([base[8][a] - base[1][a] for a in HONEST]):.2f}x")
    print(f"     on the LOG scale they are {np.mean([arm_logs[a] for a in FITTED]):+.3f} vs "
          f"{hon_log:+.3f} — a ratio of "
          f"{np.mean([arm_logs[a] for a in FITTED]) / hon_log:.2f}x")
    out["e3"] = {"floor": hon_log, "ceiling": tf_log, "position": pos,
                 "bh": [bool(k) for k in keep]}
    out["e4"] = {"fitted_start": fit1, "honest_start": hon1}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif llo <= 0 <= lhi:
        world = "B"
    elif llo > 0:
        world = "A"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   LOG contrast {L_pt:+.4f} [{llo:+.4f}, {lhi:+.4f}]  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/lambda_free.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
