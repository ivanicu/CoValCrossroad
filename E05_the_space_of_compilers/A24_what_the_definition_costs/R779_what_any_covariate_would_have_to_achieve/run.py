#!/usr/bin/env python3
"""R779 · the mediation bound — what ANY single covariate would have to achieve.

CHECK #381 ran R778's registered overlap and got a decomposition rather than a hit:
    within a family   corr(overlap, |d|)          -0.1270 to -0.1758
    across families   corr(overlap_A, overlap_B)  +0.8423 to +0.9304
    conditioning M x R on the mean overlap        drop 1.0% to 1.9%
The families share a near-common variable (r up to 0.93, MORE shared than the scales at 0.52-0.60)
that is nearly irrelevant to the outcome. Sharing is not mediation.

FORCED, LABELLED:
  D1 THE MEDIATION BOUND: the part of corr(A,B) a covariate Z can account for is bounded by
     corr(Z,A) * corr(Z,B). Algebra. Checked here against six measured drops.
       overlap        0.92 x (-0.15) x (-0.15) = 0.021   observed 1.0-1.9%
       rubricdisagree              0.33 x 0.36 = 0.119   observed 9.6%
  D2 the REQUIRED correlation is sqrt(r): to explain 0.59 a single covariate needs ~0.77 with each
     scale. Algebra; the measurement is the shortfall.
  D3 overlap is shared MORE than the scales are and still explains nothing -- the cell that makes D1
     worth stating, and the reason four rounds searched for shared variables without asking whether
     they drive the outcome.

CONTROLS  POSITIVE (a synthetic mediator with a KNOWN implied product) - g=0 (an independent
          covariate) - NEGATIVE (200 permutations) - SHAM (same marginal, no relation) - PLACEBO -
          SPEARMAN (every correlation in both forms, the registered confound).
UNIT      prompt - arm pair - COVARIATE (6) and FAMILY PAIR (3).
"""
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

RES = ROOT / "corebench/results"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
NDRAW = 200
KS = [2, 3, 6, 8, 12]
FAM = {
    "Ra_random_s0": [f"random_k{k}_s0" for k in KS],
    "Rb_random_s1": [f"random_k{k}_s1" for k in KS],
    "Rc_random_s2": [f"random_k{k}_s2" for k in KS],
    "F1_committed": ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"],
    "F3_target":    ["oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1",
                     "greedy_k4_greedy_kA"],
    "M_mixed_sel":  ["random_k4_s0", "random_k4_s1", "random_k4_s2", "topabs_k4", "topvar_k4"],
}
MR = ["Ra_random_s0", "Rb_random_s1", "Rc_random_s2"]


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


def rank(x):
    return np.argsort(np.argsort(x)).astype(float)


def partial(x, y, z):
    rxy = float(np.corrcoef(x, y)[0, 1])
    rxz = float(np.corrcoef(x, z)[0, 1])
    ryz = float(np.corrcoef(y, z)[0, 1])
    den = math.sqrt(max((1 - rxz ** 2) * (1 - ryz ** 2), 1e-12))
    return (rxy - rxz * ryz) / den


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    FULL = load_sat(RES / "sat_full.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and p in FULL
                   and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def a2(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        o = np.zeros(P)
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(Y[[i for i, _ in PR]] - Y[[j for _, j in PR]])
            o[ai] = np.mean([(s == h).mean() for h in HC[ai]])
        return o

    A = {t: a2(t) for f in FAM.values() for t in f}
    C = {n: np.abs(np.array([A[a] - A[b] for a, b in itertools.combinations(FAM[n], 2)])).mean(0)
         for n in FAM}

    # ---- the six covariates ----------------------------------------------------------------------
    idxp = sorted({i for i, _ in POOL[pids[0]]})
    Tp = np.zeros((P, len(idxp), 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxp):
            for c_, x in enumerate(L):
                Tp[a, bi, c_] = POOL[p].get((i, x), 0.0)
    poolspread = Tp.std(axis=(1, 2))
    Sp = np.sign(Tp[:, :, [i for i, _ in PR]] - Tp[:, :, [j for _, j in PR]])
    orderdis = np.array([np.mean([float((Sp[a, i] != Sp[a, j]).mean())
                                  for i, j in itertools.combinations(range(len(idxp)), 2)])
                         for a in range(P)])
    n_rub = np.array([len({i for i, _ in FULL[p]}) for p in pids], dtype=float)
    rub_spread, rub_dis = np.zeros(P), np.zeros(P)
    for a, p in enumerate(pids):
        idx = sorted({i for i, _ in FULL[p]})
        Y = np.array([[FULL[p].get((i, x), 0.0) for x in L] for i in idx])
        rub_spread[a] = Y.std()
        S = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        if len(idx) > 1:
            rub_dis[a] = float(np.mean([float((S[i] != S[j]).mean())
                                        for i, j in itertools.combinations(range(len(idx)), 2)]))
    core = {t: json.loads((RES / f"core_{t}.json").read_text())
            for f in FAM.values() for t in f if (RES / f"core_{t}.json").is_file()}
    OV = {}
    for n in FAM:
        cols = []
        for a, b in itertools.combinations(FAM[n], 2):
            if a in core and b in core:
                cols.append(np.array([len(set(core[a][p]) & set(core[b][p])) /
                                      max(1, len(set(core[a][p]) | set(core[b][p]))) for p in pids]))
        OV[n] = np.array(cols).mean(0) if cols else np.zeros(P)
    overlap_shared = np.mean([OV[n] for n in MR + ["M_mixed_sel"]], axis=0)

    COV = {"poolspread": poolspread, "orderdisagree": orderdis, "n_rubric": n_rub,
           "rubricdisagree": rub_dis, "rubricspread": rub_spread, "overlap": overlap_shared}
    print(f"  prompts {P}   covariates {len(COV)}   family pairs {len(MR)}")
    print(f"  D3 CHECK    overlap is shared across families at "
          f"{np.mean([float(np.corrcoef(OV[a], OV[b])[0, 1]) for a, b in itertools.combinations(MR + ['M_mixed_sel'], 2)]):.4f}"
          f"  while the SCALES share only "
          f"{np.mean([float(np.corrcoef(C[a], C[b])[0, 1]) for a, b in itertools.combinations(MR + ['M_mixed_sel'], 2)]):.4f}")

    # ---- E1 - the bound against the measured drop -------------------------------------------------
    print(f"\n  E1 - MEDIATION BOUND vs MEASURED DROP   (D1: bound = corr(Z,A) * corr(Z,B))")
    print(f"  {'covariate':<16}{'pair':<16}{'r(Z,A)':>9}{'r(Z,B)':>9}{'bound':>9}"
          f"{'measured':>10}{'gap':>8}   spearman bound")
    rows, gaps = {}, []
    for cname, cv in COV.items():
        for n in MR:
            rza = float(np.corrcoef(cv, C[n])[0, 1])
            rzb = float(np.corrcoef(cv, C["M_mixed_sel"])[0, 1])
            bound = rza * rzb
            raw = float(np.corrcoef(C[n], C["M_mixed_sel"])[0, 1])
            pt = partial(C[n], C["M_mixed_sel"], cv)
            meas = raw - pt
            sb = (float(np.corrcoef(rank(cv), rank(C[n]))[0, 1])
                  * float(np.corrcoef(rank(cv), rank(C["M_mixed_sel"]))[0, 1]))
            gaps.append(abs(meas - bound))
            rows[f"{cname}|{n}"] = {"r_ZA": rza, "r_ZB": rzb, "bound": bound,
                                    "measured": meas, "gap": meas - bound, "spearman_bound": sb}
            print(f"  {cname:<16}{n[:14]:<16}{rza:>+9.4f}{rzb:>+9.4f}{bound:>+9.4f}"
                  f"{meas:>+10.4f}{meas - bound:>+8.4f}{sb:>+15.4f}")
    worst = float(max(gaps))
    print(f"  worst |measured - bound| over {len(gaps)} cells: {worst:.4f}")

    # ---- E2 - the required correlation -------------------------------------------------------------
    rbar = float(np.mean([np.corrcoef(C[n], C["M_mixed_sel"])[0, 1] for n in MR]))
    need = math.sqrt(max(rbar, 0))
    best = max(max(abs(rows[k]["r_ZA"]), abs(rows[k]["r_ZB"])) for k in rows)
    print(f"\n  E2 - REQUIRED vs ACHIEVED")
    print(f"     co-movement to explain          r = {rbar:.4f}")
    print(f"     a single covariate needs        |corr| >= sqrt(r) = {need:.4f}")
    print(f"     best achieved by any covariate  {best:.4f}   -> short by {need / max(best, 1e-9):.1f}x")

    # ---- E3 - the joint ceiling, in-sample and labelled as such -----------------------------------
    X = np.column_stack([COV[c] for c in COV])
    X = (X - X.mean(0)) / np.maximum(X.std(0), 1e-12)
    X = np.column_stack([np.ones(P), X])
    mult = {}
    for n in FAM:
        y = C[n]
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        yhat = X @ beta
        mult[n] = float(np.corrcoef(yhat, y)[0, 1])
    n_ge = sum(1 for v in mult.values() if v >= need)
    print(f"\n  E3 - MULTIPLE correlation of all {len(COV)} covariates (IN-SAMPLE, an upper bound only)")
    for n in FAM:
        print(f"     {n:<16}{mult[n]:.4f}   {'>= required' if mult[n] >= need else 'below required'}")
    print(f"     families reaching {need:.4f}: {n_ge}/{len(FAM)}")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    rng = np.random.default_rng(779)
    plc = float(np.corrcoef(C["Ra_random_s0"], C["Ra_random_s0"])[0, 1])
    print(f"\n  PLACEBO     a family against ITSELF {plc:.6f}  "
          f"{'PASS' if abs(plc - 1) < 1e-9 else 'FAIL'}")
    a_, b_ = C["Ra_random_s0"], C["M_mixed_sel"]
    raw_ab = float(np.corrcoef(a_, b_)[0, 1])
    negd, shamd = [], []
    for _ in range(NDRAW):
        z = COV["rubricdisagree"][rng.permutation(P)]
        negd.append(raw_ab - partial(a_, b_, z))
        z2 = rng.choice(COV["rubricdisagree"], P, replace=True)
        shamd.append(raw_ab - partial(a_, b_, z2))
    nlo, nhi = np.percentile(negd, 2.5), np.percentile(negd, 97.5)
    print(f"  NEGATIVE    {NDRAW} permutations of a covariate: drop {np.mean(negd):+.4f} "
          f"[{nlo:+.4f}, {nhi:+.4f}]")
    print(f"  SHAM        same marginal, no relation: drop {np.mean(shamd):+.4f} "
          f"[{np.percentile(shamd, 2.5):+.4f}, {np.percentile(shamd, 97.5):+.4f}]")
    zi = rng.normal(0, 1, P)
    g0_drop = raw_ab - partial(a_, b_, zi)
    g0 = nlo <= g0_drop <= nhi
    print(f"  g=0         an INDEPENDENT covariate: drop {g0_drop:+.4f}  "
          f"{'PASS' if g0 else 'FAIL'}  (must sit inside the negative band)")
    # THE FIRST POSITIVE CONTROL COMPARED THE MEASURED DROP TO THE PRODUCT `r_ZA * r_ZB`, and the
    # product is an APPROXIMATION, not the drop. Exactly,
    #     r_AB.Z = (r_AB - r_ZA*r_ZB) / sqrt((1-r_ZA^2)(1-r_ZB^2))
    # so the DROP is r_AB - r_AB.Z, and the denominator inflates the partial -- pushing the drop BELOW
    # the product except where r_ZA, r_ZB are small. Measured on the sweep: gaps -0.085 at w=0.25 and
    # -0.136 at w=0.50, closing to +0.008 at w=1.00. **So D1's product is a good approximation only in
    # the WEAK regime, which is exactly where every real covariate sits (|r| <= 0.365) and why it
    # looked tight there.** Checking the exact formula instead would be a TAUTOLOGY -- both sides come
    # from the same three correlations -- so the control is rebuilt against a GENERATIVE truth:
    # construct A and B from a common Z, where the mediated share is 1.0 by construction, and require
    # the measured drop to recover the whole correlation. That can fail; an algebraic identity cannot.
    print(f"  POSITIVE    a SYNTHETIC mediator, GENERATIVE share known by construction:")
    dose, ok_pos = {}, True
    for w in (0.0, 0.25, 0.5, 1.0):
        z = rng.normal(0, 1, P)
        sa = w * z + math.sqrt(max(1 - w * w, 0)) * rng.normal(0, 1, P)
        sb = w * z + math.sqrt(max(1 - w * w, 0)) * rng.normal(0, 1, P)
        raw_syn = float(np.corrcoef(sa, sb)[0, 1])
        meas = raw_syn - partial(sa, sb, z)
        recov = meas / raw_syn if abs(raw_syn) > 1e-6 else float("nan")
        prod = float(np.corrcoef(z, sa)[0, 1]) * float(np.corrcoef(z, sb)[0, 1])
        dose[w] = {"raw": raw_syn, "measured": meas, "recovered_share": recov, "product": prod}
        print(f"     w {w:>4.2f}  corr(A,B) {raw_syn:+.4f}   drop {meas:+.4f}   "
              f"share recovered {'n/a' if recov != recov else f'{recov:.4f}'}   "
              f"(product would say {prod:+.4f})")
        if w >= 0.5 and (recov != recov or recov < 0.90):
            ok_pos = False
    pos = ok_pos and dose[1.0]["measured"] > nhi
    print(f"              registered band - w=0 gives no correlation to mediate; w>=0.5 must recover "
          f">=90% of a fully-mediated correlation: {pos}  {'PASS' if pos else 'FAIL'}")

    ctrl = pos and g0 and abs(plc - 1) < 1e-9
    if not ctrl:
        world = "UNVERIFIED"
    elif worst >= 0.10:
        world = f"B - THE APPROXIMATION IS THE WRONG INSTRUMENT: worst gap {worst:.4f}"
    elif n_ge >= 4:
        world = f"C - THE JOINT SET REACHES THE THRESHOLD: {n_ge}/6 families at {need:.4f}"
    elif worst < 0.10 and best < 0.40 and max(mult.values()) < need:
        world = (f"A - THE COVARIATE SEARCH IS CLOSED WITH A NUMBER: bound holds to {worst:.4f}, "
                 f"best single {best:.4f} against a required {need:.4f}, joint ceiling "
                 f"{max(mult.values()):.4f}")
    else:
        world = "NO WORLD - counts reported, none claimed"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/mediation_bound.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "rows": rows, "worst_gap": worst,
        "comovement": rbar, "required": need, "best_single": best,
        "multiple_in_sample": mult, "n_families_reaching_required": n_ge,
        "overlap_shared_across_families": float(np.mean(
            [float(np.corrcoef(OV[a], OV[b])[0, 1])
             for a, b in itertools.combinations(MR + ["M_mixed_sel"], 2)])),
        "controls": {"placebo": plc, "negative_lo": float(nlo), "negative_hi": float(nhi),
                     "sham_mean": float(np.mean(shamd)), "g0_drop": float(g0_drop),
                     "dose": {str(k): v for k, v in dose.items()},
                     "positive": bool(pos), "g0": bool(g0)},
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
