#!/usr/bin/env python3
"""R807 · is the fitted arm a rank-constrained copy of the leak?

R806 left the fitted arms at roughly half the maximal-leak profile — neither content nor pure label
access — and proposed regressing each fitted arm's per-prompt margin on the synthetic
`_perfect_leak`'s. CHECK #409 found the defect in that as posed: both margins are scored on the SAME
parity-0 annotators, so their sampling errors are correlated and the slope is inflated by
construction — the same shared-term defect R806 had just corrected in R295. This round runs it both
ways and reports the inflation as a number.

ESTIMAND        E1 the regression as posed · E2 ⭐ the shared-draw fix (leak on half A, arm on half
                B) · E3 the honest floor · E4 content = fitted intercept − honest intercept
IDENTIFICATION  E1 confounded by construction, reported only as E2's contrast; E2/E3/E4 identified
DERIVED FIRST   D1 leak on itself is slope 1 intercept 0 (placebo) · D2 a planted half-and-half arm
                is slope ~0.5 with a resolved intercept, and must NOT fire at g=0 · D3 the honest
                arms never saw parity-1 · D4 E1 slope >= E2 slope or the shared-draw story is wrong
⛔ THE ESTIMAND IS THE INTERCEPT, NOT THE RESIDUAL. R804 committed the lesson: an OLS residual mean
   is 0 by construction. The informative quantity is the arm's margin AT ZERO LEAK MARGIN.
WORLDS          A content · B copy · C uninformative — C checked FIRST
CONTROLS        OBJECT (R806's committed slopes) · PLACEBO · POSITIVE (planted, with a g=0 check) ·
                NEGATIVE (leak permuted) · NOISE FLOOR (20 half-splits)
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
R806J = ARC / "R806_is_the_leak_verdict_a_scale_artifact/results/scale_artifact.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
FITTED = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
HONEST = ["coval_core", "topw_k4"]
ARMS = FITTED + HONEST


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
    out = {"instrument_unit": "a PROMPT", "claim_unit": "an ARM"}
    tg, _ = load_targets()
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    POOL = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set.intersection(*(set(v) for v in S.values())) & set(POOL) &
                  {p for p in tg if len(tg[p]) >= 2})
    H0 = {p: [cls(np.array(t[0], float)) for i, t in enumerate(tg[p]) if i % 2 == 0] for p in pids}
    H1 = {p: [cls(np.array(t[0], float)) for i, t in enumerate(tg[p]) if i % 2 == 1] for p in pids}
    pids = [p for p in pids if H0[p] and H1[p]]
    N = len(pids)
    short = sum(1 for p in pids if len(H0[p]) < 2)
    print(f"  POPULATION  {N} prompts; carrying a parity-0 HALF-SPLIT: {N - short}; "
          f"too few parity-0 annotators to split: {short} (printed, never silent)")
    M1 = {p: modal(H1[p]) for p in pids}
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    BL = {p: np.array(cls(yvec(POOL[p], [0, 1, 2, 3]))) for p in pids}

    def margin(getcls, hsel):
        """mean agreement with the chosen parity-0 annotators, minus the k=4 pool's."""
        v = np.zeros(N)
        for i, p in enumerate(pids):
            h = hsel(p)
            if len(h) == 0:
                v[i] = np.nan
                continue
            hh = np.array(h)
            v[i] = float((hh == getcls(p)).mean()) - float((hh == BL[p]).mean())
        return v

    ALL0 = lambda p: H0[p]                                             # noqa: E731

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R806's committed slopes under R806's own binning")
    r806 = json.loads(R806J.read_text())
    AGREE = np.array([np.mean([[a == b for a, b in zip(x, y)] for x in H1[p] for y in H0[p]])
                      for p in pids])
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def slope_only(m, x):
        z = (x - x.mean()) / x.std()
        return float(np.polyfit(z, m, 1)[0])

    leak_all = margin(lambda p: M1[p], ALL0)
    marg_all = {a: margin(lambda p, a=a: CL[a][p], ALL0) for a in ARMS}
    s_leak = slope_only(leak_all, AGREE)
    s_o = slope_only(marg_all["oracle_k4_fit1"], AGREE)
    ok = (abs(s_leak - r806["e3"]["rows"]["_perfect_leak"]["slope"]) < 1e-6
          and abs(s_o - r806["e3"]["rows"]["oracle_k4_fit1"]["slope"]) < 1e-6)
    print(f"     ⚠ R806's E3 binned on WITHIN-parity-1 agreement; this check uses R806's E1/E2 "
          f"binning (half-agreement), so it anchors the MARGIN VECTORS, not the slope value.")
    print(f"     `_perfect_leak` slope here {s_leak:+.6f}   `oracle_k4_fit1` {s_o:+.6f}")
    print(f"     committed under R806's E3 binning: {r806['e3']['rows']['_perfect_leak']['slope']:+.6f}"
          f" / {r806['e3']['rows']['oracle_k4_fit1']['slope']:+.6f}   exact match: {ok}")
    # the anchor that MUST hold: the pooled margins, which are binning-free
    pm_ok = (abs(float(leak_all.mean()) - r806["e2"]["relative"]["_perfect_leak"]["pooled"]) < 1e-9
             and abs(float(marg_all["oracle_k4_fit1"].mean())
                     - r806["e2"]["relative"]["oracle_k4_fit1"]["pooled"]) < 1e-9)
    print(f"     ⭐ BINNING-FREE ANCHOR: pooled margins {leak_all.mean():+.9f} / "
          f"{marg_all['oracle_k4_fit1'].mean():+.9f} vs R806's committed "
          f"{r806['e2']['relative']['_perfect_leak']['pooled']:+.9f} / "
          f"{r806['e2']['relative']['oracle_k4_fit1']['pooled']:+.9f}   "
          f"{'PASS' if pm_ok else 'FAIL'}")
    if not pm_ok:
        print("  UNRUNNABLE: R806's margin vectors did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"pooled_leak": float(leak_all.mean()),
                     "pooled_oracle": float(marg_all["oracle_k4_fit1"].mean()), "n": N}

    # ================= the regression machinery ==================================================
    def fit(y, x, idx):
        b, a = np.polyfit(x, y, 1)
        r2 = 1 - np.var(y - (a + b * x)) / max(np.var(y), 1e-18)
        bs = np.array([np.polyfit(x[i], y[i], 1) for i in idx[:400]])
        return {"slope": float(b), "intercept": float(a), "r2": float(r2),
                "s_lo": float(np.percentile(bs[:, 0], 2.5)),
                "s_hi": float(np.percentile(bs[:, 0], 97.5)),
                "i_lo": float(np.percentile(bs[:, 1], 2.5)),
                "i_hi": float(np.percentile(bs[:, 1], 97.5)),
                "_ib": bs[:, 1]}

    # ================= E1 · as posed =============================================================
    print("\n  E1 - THE REGRESSION AS R806's NEXT POSED IT  (leak and arm on the SAME parity-0 draw)")
    print(f"     {'arm':<18}{'slope':>22}{'intercept':>24}{'R2':>7}")
    e1 = {}
    for a in ARMS:
        f = fit(marg_all[a], leak_all, IDX)
        e1[a] = f
        print(f"     {a:<18}{f['slope']:>+8.4f} [{f['s_lo']:+.4f},{f['s_hi']:+.4f}]"
              f"{f['intercept']:>+9.4f} [{f['i_lo']:+.4f},{f['i_hi']:+.4f}]{f['r2']:>7.3f}")
    print("     ⚠ confounded by construction: both margins carry the SAME parity-0 annotator noise.")

    # ================= E2 · the shared-draw fix ==================================================
    print("\n  E2 - THE SHARED-DRAW FIX  (leak scored on parity-0 half A, arm on half B)")
    rng = np.random.default_rng(2024)
    DRAWS = 20
    acc = {a: {"slope": [], "intercept": []} for a in ARMS + ["_planted", "_leakcopy"]}
    e2_last = {}
    for d in range(DRAWS):
        HA, HB = {}, {}
        for p in pids:
            h = H0[p]
            pm = rng.permutation(len(h))
            k = max(1, len(h) // 2)
            HA[p] = [h[i] for i in pm[:k]]
            HB[p] = [h[i] for i in pm[k:]] or [h[i] for i in pm[:k]]
        lk = margin(lambda p: M1[p], lambda p: HA[p])
        # the PLANTED positive control: leak on half the prompts, honest class on the other half
        half = set(pids[::2])
        planted = margin(lambda p: M1[p] if p in half else CL["coval_core"][p],
                         lambda p: HB[p])
        leakcopy = margin(lambda p: M1[p], lambda p: HB[p])
        for a in ARMS:
            m = margin(lambda p, a=a: CL[a][p], lambda p: HB[p])
            f = fit(m, lk, IDX)
            acc[a]["slope"].append(f["slope"])
            acc[a]["intercept"].append(f["intercept"])
            if d == DRAWS - 1:
                e2_last[a] = f
        for nm, vec in (("_planted", planted), ("_leakcopy", leakcopy)):
            f = fit(vec, lk, IDX)
            acc[nm]["slope"].append(f["slope"])
            acc[nm]["intercept"].append(f["intercept"])
            if d == DRAWS - 1:
                e2_last[nm] = f
    print(f"     {'arm':<18}{'slope (mean of 20 splits)':>30}{'intercept':>26}")
    e2 = {}
    for a in ARMS:
        sm, im = float(np.mean(acc[a]["slope"])), float(np.mean(acc[a]["intercept"]))
        e2[a] = {"slope": sm, "intercept": im,
                 "slope_sd": float(np.std(acc[a]["slope"])),
                 "int_sd": float(np.std(acc[a]["intercept"])),
                 "s_lo": e2_last[a]["s_lo"], "s_hi": e2_last[a]["s_hi"],
                 "i_lo": e2_last[a]["i_lo"], "i_hi": e2_last[a]["i_hi"]}
        print(f"     {a:<18}{sm:>+10.4f} ±{np.std(acc[a]['slope']):.4f} "
              f"[{e2_last[a]['s_lo']:+.4f},{e2_last[a]['s_hi']:+.4f}]"
              f"{im:>+10.4f} ±{np.std(acc[a]['intercept']):.4f} "
              f"[{e2_last[a]['i_lo']:+.4f},{e2_last[a]['i_hi']:+.4f}]")
    infl = {a: e1[a]["slope"] - e2[a]["slope"] for a in ARMS}
    d4 = all(v > 0 for v in infl.values())
    print(f"     ⭐ SHARED-TERM INFLATION (E1 slope − E2 slope): " +
          "  ".join(f"{a.split('_')[0]} {v:+.4f}" for a, v in infl.items()))
    print(f"     D4 every arm's E1 slope exceeds its E2 slope: {d4}   "
          f"{'PASS' if d4 else '⚠ FAIL - the shared-draw story is wrong and this round says so'}")
    out["e1"] = {a: {k: v for k, v in e1[a].items() if not k.startswith("_")} for a in ARMS}
    out["e2"] = e2
    out["inflation"] = infl

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    ps = fit(leak_all, leak_all, IDX)
    plac_ok = abs(ps["slope"] - 1) < 1e-9 and abs(ps["intercept"]) < 1e-9
    print(f"     PLACEBO   `_perfect_leak` regressed on ITSELF: slope {ps['slope']:.9f}  "
          f"intercept {ps['intercept']:+.9f}   {'PASS - exact' if plac_ok else 'FAIL'}")
    pl_s = float(np.mean(acc["_planted"]["slope"]))
    pl_i = float(np.mean(acc["_planted"]["intercept"]))
    lc_s = float(np.mean(acc["_leakcopy"]["slope"]))
    lc_i = float(np.mean(acc["_leakcopy"]["intercept"]))
    pos_ok = (0.25 < pl_s < 0.75) and pl_i > 0 and e2_last["_planted"]["i_lo"] > 0
    g0_ok = abs(lc_i) < abs(pl_i)
    print(f"     POSITIVE  PLANTED half-leak/half-honest arm: slope {pl_s:+.4f} (D2 predicted ~0.5)"
          f"   intercept {pl_i:+.4f} [{e2_last['_planted']['i_lo']:+.4f},"
          f"{e2_last['_planted']['i_hi']:+.4f}]   {'PASS' if pos_ok else 'FAIL'}")
    print(f"     g=0 CHECK the PURE-leak copy (no honest content planted): slope {lc_s:+.4f}   "
          f"intercept {lc_i:+.4f}   {'PASS - control can fail' if g0_ok else 'FAIL - fires with nothing planted'}")
    # ⛔ THE FIRST VERSION BOOTSTRAPPED AROUND ONE PERMUTED DRAW. That measures the PRECISION of
    # that single permutation's slope, not the NULL distribution — so it reported +0.0843
    # [+0.0308, +0.1346] and "FAIL" for a pairing that had in fact been destroyed. A permutation
    # null is a distribution over permutations; 200 of them.
    rngn = np.random.default_rng(808)
    nulls = np.array([np.polyfit(leak_all[rngn.permutation(N)],
                                 marg_all["oracle_k4_fit1"], 1)[0] for _ in range(200)])
    obs_real = e1["oracle_k4_fit1"]["slope"]
    nlo, nhi = float(np.percentile(nulls, 2.5)), float(np.percentile(nulls, 97.5))
    neg_ok = nlo <= 0 <= nhi and obs_real > nulls.max()
    print(f"     NEGATIVE  PERMUTATION NULL over 200 permutations: slope null "
          f"{nulls.mean():+.4f} [{nlo:+.4f}, {nhi:+.4f}]  max {nulls.max():+.4f}")
    print(f"               the real slope {obs_real:+.4f} lies outside the whole null: "
          f"{obs_real > nulls.max()}   {'PASS' if neg_ok else 'FAIL'}")
    negf = {"slope": float(nulls.mean()), "s_lo": nlo, "s_hi": nhi}
    print(f"     NOISE FLOOR  over {DRAWS} half-splits: slope sd " +
          "  ".join(f"{a.split('_')[0]} {e2[a]['slope_sd']:.4f}" for a in ARMS))
    # ⚠ g0_ok is DELIBERATELY not in this conjunction any more: the g=0 failure was not a defect
    # in the instrument, it was the discovery that the INTERCEPT estimand is unidentified. It is
    # reported above, and E3 replaces the estimand rather than pretending the control passed.
    gate = pm_ok and plac_ok and pos_ok and neg_ok
    print(f"     GATE (pre-repair)  {'PASS' if gate else 'FAIL'}   "
          f"g=0 on the INTERCEPT: {g0_ok} -> that estimand is abandoned in E3, not rescued")
    out["controls"] = {"placebo": ps["slope"], "placebo_ok": plac_ok, "planted_slope": pl_s,
                       "planted_intercept": pl_i, "positive_ok": pos_ok,
                       "leakcopy_slope": lc_s, "leakcopy_intercept": lc_i, "g0_ok": g0_ok,
                       "negative_slope": negf["slope"], "negative_ok": neg_ok, "gate": gate}

    # ================= E3/E4 · the honest floor and the content ==================================
    print("\n  E3/E4 - THE ESTIMAND, REPAIRED BY THIS ROUND's OWN g=0 CONTROL")
    print("     ⛔ THE INTERCEPT IS NOT IDENTIFIED. The g=0 control -- the SAME predictor scored on")
    print("     two independent halves, with nothing planted -- returned a resolved positive")
    print("     intercept. That is errors-in-variables: noise in x attenuates the slope to lambda")
    print("     and forces intercept = (1-lambda)*mean(y). So a bigger mean margin buys a bigger")
    print("     intercept with no content at all.")
    LAM = lc_s                                  # the leak's own split-half reliability
    pred = (1 - LAM) * float(leak_all.mean())
    print(f"     DERIVATION CHECK: (1-lambda)*mean(leak) = (1-{LAM:.4f})*{leak_all.mean():.4f} = "
          f"{pred:+.6f}   observed g=0 intercept {lc_i:+.6f}   |diff| {abs(pred - lc_i):.6f}")
    print(f"\n     ⭐ THE IDENTIFIED ESTIMAND: the DISATTENUATED slope, observed / lambda.")
    print(f"     lambda = the leak's split-half reliability = {LAM:.4f}   "
          f"(a pure copy of the leak scores exactly 1.000 -- a DERIVATION, the ceiling)")
    print(f"     {'arm':<18}{'observed':>10}{'disattenuated':>15}{'sd over 20 splits':>20}")
    dis = {}
    for a in ARMS:
        d = e2[a]["slope"] / LAM
        dis[a] = d
        sd = e2[a]["slope_sd"] / LAM
        print(f"     {a:<18}{e2[a]['slope']:>+10.4f}{d:>15.3f}{sd:>20.3f}")
    fs = float(np.mean([e2[a]["slope"] for a in FITTED]))
    hs = float(np.mean([e2[a]["slope"] for a in HONEST]))
    fd = float(np.mean([dis[a] for a in FITTED]))
    hd = float(np.mean([dis[a] for a in HONEST]))
    pd_ = pl_s / LAM
    print(f"\n     honest floor {hd:.3f}   fitted {fd:.3f}   PLANTED half-and-half {pd_:.3f}   "
          f"pure copy 1.000")
    mid = 0.5 * (hd + 1.0)
    print(f"     ⭐ POSITIVE CONTROL ON THE REPAIRED ESTIMAND: a half-honest/half-leak arm should")
    print(f"        land at 0.5*(floor + ceiling) = 0.5*({hd:.3f} + 1.000) = {mid:.3f}; it lands at")
    print(f"        {pd_:.3f}, |diff| {abs(pd_ - mid):.3f}   "
          f"{'PASS - the scale is calibrated' if abs(pd_ - mid) < 0.05 else 'FAIL'}")
    pos2_ok = abs(pd_ - mid) < 0.05
    # ⛔ THE FIRST VERSION BOOTSTRAPPED THE GAP ON THE E1 (same-draw) SLOPES while the point
    # estimate came from the E2 (half-split) ones -- so the point estimate +0.248 fell OUTSIDE its
    # own reported CI [+0.386, +0.601]. A CI computed on a different estimator is not a CI. Fixed:
    # one FIXED half-split, bootstrapped over prompts, with lambda estimated on that same split, so
    # every quantity below comes from one estimator.
    rf = np.random.default_rng(20240)
    HA, HB = {}, {}
    for p_ in pids:
        h = H0[p_]
        pm = rf.permutation(len(h))
        k = max(1, len(h) // 2)
        HA[p_] = [h[i] for i in pm[:k]]
        HB[p_] = [h[i] for i in pm[k:]] or [h[i] for i in pm[:k]]
    lkF = margin(lambda p_: M1[p_], lambda p_: HA[p_])
    armF = {a: margin(lambda p_, a=a: CL[a][p_], lambda p_: HB[p_]) for a in ARMS}
    lcF = margin(lambda p_: M1[p_], lambda p_: HB[p_])
    rngg = np.random.default_rng(4242)
    BI = rngg.integers(0, N, (1200, N))
    def slp(y, x, i):
        return np.polyfit(x[i], y[i], 1)[0]
    lam_bs = np.array([slp(lcF, lkF, i) for i in BI])
    LAMF = float(np.polyfit(lkF, lcF, 1)[0])
    arm_bs = {a: np.array([slp(armF[a], lkF, i) for i in BI]) for a in ARMS}
    dis_ci = {a: (float(np.percentile(arm_bs[a] / lam_bs, 2.5)),
                  float(np.percentile(arm_bs[a] / lam_bs, 97.5))) for a in ARMS}
    fb = np.mean([arm_bs[a] for a in FITTED], axis=0) / lam_bs
    hb = np.mean([arm_bs[a] for a in HONEST], axis=0) / lam_bs
    gaps = fb - hb
    glo, ghi = float(np.percentile(gaps, 2.5)), float(np.percentile(gaps, 97.5))
    gap = float(np.mean([np.polyfit(lkF, armF[a], 1)[0] for a in FITTED]) / LAMF
                - np.mean([np.polyfit(lkF, armF[a], 1)[0] for a in HONEST]) / LAMF)
    print(f"\n     ON ONE FIXED SPLIT, every quantity from the SAME estimator (lambda {LAMF:.4f}):")
    for a in ARMS:
        print(f"        {a:<18} disattenuated {np.polyfit(lkF, armF[a], 1)[0] / LAMF:>6.3f} "
              f"[{dis_ci[a][0]:+.3f}, {dis_ci[a][1]:+.3f}]")
    print(f"     ⭐ fitted minus honest, disattenuated: {gap:+.3f} [{glo:+.3f}, {ghi:+.3f}]")
    ovl = not (max(dis_ci[a][1] for a in HONEST) < min(dis_ci[a][0] for a in FITTED))
    print(f"     PRE-REGISTERED BRANCH: honest CI overlaps fitted CI (same estimator): {ovl}")
    dis_fixed = {a: float(np.polyfit(lkF, armF[a], 1)[0] / LAMF) for a in ARMS}
    out["e3"] = {"lambda": LAM, "eiv_predicted_intercept": pred, "eiv_observed": lc_i,
                 "disattenuated": dis, "disattenuated_fixed_split": dis_fixed,
                 "disattenuated_ci": dis_ci, "lambda_fixed": LAMF,
                 "fitted": fd, "honest": hd, "planted": pd_,
                 "planted_expected": mid, "positive_ok_repaired": pos2_ok,
                 "gap": gap, "gap_lo": glo, "gap_hi": ghi, "slope_ci_overlap": ovl,
                 "fitted_slope": fs, "honest_slope": hs}
    gate = gate and pos2_ok and neg_ok
    print(f"     GATE (repaired, recomputed after the two control fixes): "
          f"{'PASS' if gate else 'FAIL - UNVERIFIED'}")

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif ovl:
        world = "C"
    elif glo > 0 and max(dis_ci[a][1] for a in FITTED) < 1.0:
        world = "A"
    elif min(dis_ci[a][0] for a in FITTED) >= 1.0 or glo <= 0 <= ghi:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   slope CIs overlap: {ovl}   disattenuated gap {gap:+.3f} "
          f"[{glo:+.3f}, {ghi:+.3f}]   max fitted CI upper "
          f"{max(dis_ci[a][1] for a in FITTED):.3f} vs the "
          f"pure-copy ceiling 1.000  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/copy_of_the_leak.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
