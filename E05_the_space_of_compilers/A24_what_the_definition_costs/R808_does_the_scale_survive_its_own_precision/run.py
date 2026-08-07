#!/usr/bin/env python3
"""R808 · does R807's scale survive its own precision sweep, and does the leak's IDENTITY matter?

CHECK #410 read R807's own definition of lambda: it is the slope of the leak's margin on parity-0
half B against half A — the reliability of the EVALUATION draw, not of the proxy. R807's NEXT
proposed sweeping PARITY-1 annotators "as lambda improves", which conflates two axes. They are
separated here, and the A-axis is realstat §4's remedy aimed at my own headline: if an estimate
moves as the instrument sharpens, the correction was never correcting anything.

ESTIMAND        A-AXIS ⭐ disattenuated slope vs the number of parity-0 annotators on the x-side
                (evaluation precision; must be FLAT) · B-AXIS ⭐ vs the number of parity-1
                annotators building the leak (proxy identity; fitted should RISE, honest should not)
IDENTIFICATION  A identified; B identified only as a BETWEEN-arm contrast, since m1_j is a different
                object at each j
DERIVED FIRST   D1 lambda_k rises with k · D2 the RAW slope rises too, so only the DISATTENUATED
                slope drifting is evidence against the scale · D3 leak on itself is exactly 1.000
                (placebo) · D4 the honest arms are the floor for sensitivity to j
WORLDS          A-STABLE / A-DRIFT · B-SPECIFIC / B-GENERIC — A-DRIFT checked FIRST
CONTROLS        OBJECT (R807's committed lambda + 5 values) · PLACEBO at every k · POSITIVE (planted
                arm calibrated at EVERY k) · g=0 (pure copy must land at 1.000 at every k) ·
                NEGATIVE (permutation null at min and max k) · NOISE FLOOR (20 splits per cell)
"""
import hashlib
import itertools
import json
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
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
FITTED = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
HONEST = ["coval_core", "topw_k4"]
ARMS = FITTED + HONEST
KS = [1, 2, 3, 4]
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


def modal(hs):
    best, bc = None, -1
    for c in {tuple(h) for h in hs}:
        n = sum(1 for h in hs if tuple(h) == c)
        if n > bc:
            best, bc = c, n
    return np.array(best)


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "an ARM x an axis position"}
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
    n0 = np.array([len(H0[p]) for p in pids])
    n1 = np.array([len(H1[p]) for p in pids])
    print(f"  POPULATION  {N} prompts   parity-0 per prompt: median {int(np.median(n0))} "
          f"min {n0.min()} max {n0.max()}   parity-1: median {int(np.median(n1))} min {n1.min()}")
    print(f"     prompts with >= 2*max(KS) = {2 * max(KS)} parity-0 annotators: "
          f"{int((n0 >= 2 * max(KS)).sum())}   the A-axis uses each prompt's OWN cap, and the cap "
          f"is printed per k below")
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    BL = {p: np.array(cls(yvec(POOL[p], [0, 1, 2, 3]))) for p in pids}
    M1FULL = {p: modal(H1[p]) for p in pids}

    def marg(getc, hsel):
        v = np.zeros(N)
        for i, p in enumerate(pids):
            h = hsel(p)
            hh = np.array(h)
            v[i] = float((hh == getc(p)).mean()) - float((hh == BL[p]).mean())
        return v

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R807 on R807's own fixed split")
    r807 = json.loads(R807J.read_text())
    rf = np.random.default_rng(20240)
    HA, HB = {}, {}
    for p_ in pids:
        h = H0[p_]
        pm = rf.permutation(len(h))
        k = max(1, len(h) // 2)
        HA[p_] = [h[i] for i in pm[:k]]
        HB[p_] = [h[i] for i in pm[k:]] or [h[i] for i in pm[:k]]
    lkF = marg(lambda p: M1FULL[p], lambda p: HA[p])
    lcF = marg(lambda p: M1FULL[p], lambda p: HB[p])
    LAMF = float(np.polyfit(lkF, lcF, 1)[0])
    disF = {a: float(np.polyfit(lkF, marg(lambda p, a=a: CL[a][p], lambda p: HB[p]), 1)[0] / LAMF)
            for a in ARMS}
    ok = abs(LAMF - r807["e3"]["lambda_fixed"]) < 1e-6 and all(
        abs(disF[a] - r807["e3"]["disattenuated_fixed_split"][a]) < 1e-6 for a in ARMS)
    print(f"     lambda {LAMF:.6f} vs R807's committed {r807['e3']['lambda_fixed']:.6f}")
    for a in ARMS:
        print(f"       {a:<18} {disF[a]:.6f} vs committed "
              f"{r807['e3']['disattenuated_fixed_split'][a]:.6f}")
    print(f"     {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R807's scale did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"lambda": LAMF, "disattenuated": disF}

    # ================= the sweep machinery =======================================================
    def cell(xk, j, rng):
        """x-side = xk parity-0 annotators; leak built from j parity-1 annotators.
        y-side = a FIXED half of parity-0, disjoint from the x-side."""
        res = {}
        lk, lc, arm, plant = np.zeros(N), np.zeros(N), {a: np.zeros(N) for a in ARMS}, np.zeros(N)
        half = set(pids[::2])
        for i, p in enumerate(pids):
            h = H0[p]
            pm = rng.permutation(len(h))
            ysz = max(1, len(h) // 2)
            Y = [h[t] for t in pm[:ysz]]
            rest = [h[t] for t in pm[ysz:]] or Y
            X = rest[:min(xk, len(rest))]
            hs1 = H1[p]
            jj = min(j, len(hs1))
            m = modal([hs1[t] for t in rng.permutation(len(hs1))[:jj]])
            Ya, Xa = np.array(Y), np.array(X)
            bY, bX = (Ya == BL[p]).mean(), (Xa == BL[p]).mean()
            lk[i] = (Xa == m).mean() - bX                 # x-side: the leak, xk annotators
            lc[i] = (Ya == m).mean() - bY                 # y-side: the same leak -> lambda, and g=0
            for a in ARMS:
                arm[a][i] = (Ya == CL[a][p]).mean() - bY
            plant[i] = (Ya == (m if p in half else CL["coval_core"][p])).mean() - bY
        lam = float(np.polyfit(lk, lc, 1)[0])
        res["lambda"] = lam
        res["g0"] = float(np.polyfit(lk, lc, 1)[0] / lam)          # exactly 1 by construction
        res["placebo"] = float(np.polyfit(lk, lk, 1)[0])           # exactly 1 by construction
        res["raw"] = {a: float(np.polyfit(lk, arm[a], 1)[0]) for a in ARMS}
        res["dis"] = {a: res["raw"][a] / lam for a in ARMS}
        res["planted"] = float(np.polyfit(lk, plant, 1)[0] / lam)
        res["_vec"] = (lk, arm)
        return res

    # ================= A-AXIS ====================================================================
    print("\n  A-AXIS - EVALUATION PRECISION.  y-side FIXED; x-side = k parity-0 annotators.")
    print("     ⭐ noise in y does not bias a slope; only noise in x attenuates it. So the")
    print("     DISATTENUATED slope must be FLAT in k if the correction works. D2: the RAW slope")
    print("     rising is expected and is NOT evidence against the scale.")
    A = {}
    for k in KS:
        reps = [cell(k, 99, np.random.default_rng(1000 + k * 97 + s)) for s in range(SPLITS)]
        A[k] = {"lambda": float(np.mean([r["lambda"] for r in reps])),
                "lambda_sd": float(np.std([r["lambda"] for r in reps])),
                "raw": {a: float(np.mean([r["raw"][a] for r in reps])) for a in ARMS},
                "dis": {a: float(np.mean([r["dis"][a] for r in reps])) for a in ARMS},
                "dis_sd": {a: float(np.std([r["dis"][a] for r in reps])) for a in ARMS},
                "planted": float(np.mean([r["planted"] for r in reps])),
                "g0": float(np.mean([r["g0"] for r in reps])),
                "placebo": float(np.mean([r["placebo"] for r in reps]))}
    print(f"     {'k':>3}{'lambda':>10}{'RAW oracle':>13}{'DIS oracle':>13}{'DIS greedy':>13}"
          f"{'DIS indep':>12}{'DIS coval':>12}{'DIS topw':>11}{'planted':>10}")
    for k in KS:
        r = A[k]
        print(f"     {k:>3}{r['lambda']:>10.4f}{r['raw']['oracle_k4_fit1']:>13.4f}"
              f"{r['dis']['oracle_k4_fit1']:>13.3f}{r['dis']['greedy_k4_fit1']:>13.3f}"
              f"{r['dis']['indep_k4_fit1']:>12.3f}{r['dis']['coval_core']:>12.3f}"
              f"{r['dis']['topw_k4']:>11.3f}{r['planted']:>10.3f}")
    d1 = all(A[KS[i]]["lambda"] <= A[KS[i + 1]]["lambda"] + 1e-9 for i in range(len(KS) - 1))
    d2 = all(A[KS[i]]["raw"]["oracle_k4_fit1"] <= A[KS[i + 1]]["raw"]["oracle_k4_fit1"] + 1e-9
             for i in range(len(KS) - 1))
    print(f"     D1 lambda rises with k: {d1}   D2 the RAW slope rises with k: {d2}")
    fit_dis = {k: float(np.mean([A[k]["dis"][a] for a in FITTED])) for k in KS}
    sds = float(np.mean([A[k]["dis_sd"][a] for k in KS for a in FITTED]))
    spread = max(fit_dis.values()) - min(fit_dis.values())
    a_drift = spread > 3 * sds
    print(f"     ⭐ fitted disattenuated slope across k: " +
          "  ".join(f"k={k} {fit_dis[k]:.3f}" for k in KS))
    print(f"     spread {spread:.4f}   3x across-split sd {3 * sds:.4f}   "
          f"{'A-DRIFT' if a_drift else 'A-STABLE'}")
    out["a_axis"] = {str(k): {x: A[k][x] for x in ("lambda", "lambda_sd", "raw", "dis", "dis_sd",
                                                   "planted", "g0", "placebo")} for k in KS}
    out["a_axis_summary"] = {"fitted": fit_dis, "spread": spread, "sd": sds, "drift": a_drift}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac_ok = all(abs(A[k]["placebo"] - 1.0) < 1e-9 for k in KS)
    g0_ok = all(abs(A[k]["g0"] - 1.0) < 1e-9 for k in KS)
    print(f"     PLACEBO   the leak on ITSELF at every k: " +
          "  ".join(f"{A[k]['placebo']:.9f}" for k in KS) +
          f"   {'PASS - exact' if plac_ok else 'FAIL'}")
    print(f"     g=0       the PURE leak copy, disattenuated, at every k: " +
          "  ".join(f"{A[k]['g0']:.9f}" for k in KS) +
          f"   {'PASS - lands at 1.000' if g0_ok else 'FAIL'}")
    hon = {k: float(np.mean([A[k]["dis"][a] for a in HONEST])) for k in KS}
    pred = {k: 0.5 * (hon[k] + 1.0) for k in KS}
    pos_dev = {k: abs(A[k]["planted"] - pred[k]) for k in KS}
    pos_ok = all(v < 0.06 for v in pos_dev.values())
    print(f"     POSITIVE  planted arm vs its predicted midpoint AT EVERY k:")
    for k in KS:
        print(f"        k={k}  planted {A[k]['planted']:.3f}  predicted "
              f"0.5*({hon[k]:.3f}+1.000) = {pred[k]:.3f}   |diff| {pos_dev[k]:.3f}")
    print(f"        {'PASS - calibrated across the whole sweep' if pos_ok else 'FAIL'}")
    rngn = np.random.default_rng(808)
    negs = {}
    for k in (min(KS), max(KS)):
        c = cell(k, 99, np.random.default_rng(5000 + k))
        lk, arm = c["_vec"]
        nulls = np.array([np.polyfit(lk[rngn.permutation(N)], arm["oracle_k4_fit1"], 1)[0]
                          for _ in range(200)])
        negs[k] = {"null_mean": float(nulls.mean()), "null_max": float(nulls.max()),
                   "real": c["raw"]["oracle_k4_fit1"],
                   "ok": bool(c["raw"]["oracle_k4_fit1"] > nulls.max())}
        print(f"     NEGATIVE  k={k}: permutation null (200) mean {nulls.mean():+.4f} max "
              f"{nulls.max():+.4f}   real {c['raw']['oracle_k4_fit1']:+.4f}   "
              f"{'PASS' if negs[k]['ok'] else 'FAIL'}")
    neg_ok = all(v["ok"] for v in negs.values())
    print(f"     NOISE FLOOR  across-split sd of the disattenuated slope, mean over cells: {sds:.4f}")
    gate = ok and plac_ok and g0_ok and pos_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "g0_ok": g0_ok, "positive_dev": pos_dev,
                       "positive_ok": pos_ok, "negative": negs, "negative_ok": neg_ok,
                       "noise_floor": sds, "gate": gate}

    # ================= B-AXIS ====================================================================
    print("\n  B-AXIS - PROXY IDENTITY.  the leak's modal class built from j parity-1 annotators.")
    print("     ⭐ DIFFERENTIAL PREDICTION: the FITTED arms were fitted on the FULL parity-1 set,")
    print("     so their slope should RISE with j. The HONEST arms never saw parity-1: FLAT.")
    B = {}
    for j in JS:
        reps = [cell(max(KS), j, np.random.default_rng(7000 + j * 31 + s)) for s in range(SPLITS)]
        B[j] = {"dis": {a: float(np.mean([r["dis"][a] for r in reps])) for a in ARMS},
                "sd": {a: float(np.std([r["dis"][a] for r in reps])) for a in ARMS},
                "lambda": float(np.mean([r["lambda"] for r in reps]))}
    print(f"     {'j':>3}{'lambda':>9}" + "".join(f"{a.split('_')[0]:>12}" for a in ARMS))
    for j in JS:
        print(f"     {j:>3}{B[j]['lambda']:>9.4f}" +
              "".join(f"{B[j]['dis'][a]:>12.3f}" for a in ARMS))
    df = {a: B[JS[-1]]["dis"][a] - B[JS[0]]["dis"][a] for a in ARMS}
    fit_rise = float(np.mean([df[a] for a in FITTED]))
    hon_rise = float(np.mean([df[a] for a in HONEST]))
    pooled_sd = float(np.mean([B[j]["sd"][a] for j in (JS[0], JS[-1]) for a in ARMS]))
    contrast = fit_rise - hon_rise
    b_specific = contrast > 2 * pooled_sd * np.sqrt(2)
    print(f"     rise from j={JS[0]} to j={JS[-1]}: " +
          "  ".join(f"{a.split('_')[0]} {df[a]:+.3f}" for a in ARMS))
    print(f"     ⭐ fitted mean rise {fit_rise:+.3f}   honest mean rise {hon_rise:+.3f}   "
          f"contrast {contrast:+.3f}   vs 2*sqrt(2)*sd {2 * pooled_sd * np.sqrt(2):.3f}   "
          f"{'B-SPECIFIC' if b_specific else 'B-GENERIC'}")
    out["b_axis"] = {str(j): B[j] for j in JS}
    out["b_axis_summary"] = {"rise": df, "fitted_rise": fit_rise, "honest_rise": hon_rise,
                             "contrast": contrast, "specific": b_specific}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        wa = wb = "UNVERIFIED"
    else:
        wa = "A-DRIFT" if a_drift else "A-STABLE"
        wb = "B-SPECIFIC" if b_specific else "B-GENERIC"
    print(f"     gate {gate}   A: spread {spread:.4f} vs 3*sd {3 * sds:.4f} -> {wa}")
    print(f"                   B: contrast {contrast:+.3f} -> {wb}")
    out["world"] = {"a": wa, "b": wb}

    art = HERE / "results/precision_sweep.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
