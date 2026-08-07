#!/usr/bin/env python3
"""R810 · is the fitted arms' level advantage SIZE or FITTING?

R809 closed the B-axis and left LEVEL as the only thing separating fitted from honest arms. But the
fitted arms measured in this arc are k=4 while `genericpool16` carries 16, so size and fitting have
been confounded throughout. CHECK #412 also killed R809's NEXT as named: `--rule oracle_k` caps at
20,000 combinations and SAMPLES above it — 367 of 968 prompts at k=8, 254 at k=12 — so the oracle's
identity changes with k. `greedy_k` and `indep_k` are linear and are used instead.

ESTIMAND        E1 the fitted−honest level gap at MATCHED k · E2 ⭐ its trend in k · E3 the
                EFFECTIVE k emitted · E4 the gap against the size-matched prompt-blind pool
IDENTIFICATION  only on prompts attaining nominal k; also reported on the common intersection
DERIVED FIRST   D1 `topw_k` → `full` as k → n · D2 ⚠ the gap MUST close at k = n by construction, so
                the question is whether it closes at reachable k · D3 POOL[0:k] is the clean size
                control · D4 fitted on parity-1, scored on parity-0
WORLDS          A size · B fitting · C unidentified — A checked FIRST
CONTROLS        OBJECT (R805's committed 0.5984 / 0.5866) · PLACEBO · POSITIVE with a g=0 check ·
                NEGATIVE (criteria permuted across prompts, 200-permutation null) · NOISE FLOOR
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
R805J = ARC / "R805_the_held_out_arms_scored_held_out/results/heldout.json"
KS = [2, 4, 8, 12]
FITRULES = ["greedy", "indep"]
NBOOT = 1200


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
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "a k"}
    tg, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    FULL = load_sat(RES / "sat_full.npz")
    names = {}
    for k in KS:
        for r in FITRULES:
            names[f"{r}_k{k}_fit1"] = RES / f"sat_{r}_k{k}_fit1.npz"
        names[f"topw_k{k}"] = RES / f"sat_topw_k{k}.npz"
        names[f"random_k{k}_s0"] = RES / f"sat_random_k{k}_s0.npz"
    missing = [n for n, p in names.items() if not p.is_file()]
    if missing:
        print(f"  UNRUNNABLE: missing arms {missing}. Exit 2.")
        return 2
    S = {n: load_sat(p) for n, p in names.items()}
    pids = sorted(set.intersection(*(set(v) for v in S.values())) & set(POOL) & set(FULL) &
                  {p for p in tg if len(tg[p]) >= 2})
    H0 = {p: np.array([cls(np.array(t[0], float))
                       for i, t in enumerate(tg[p]) if i % 2 == 0]) for p in pids}
    pids = [p for p in pids if len(H0[p]) >= 1]
    N0 = len(pids)
    npool = len({i for i, _ in POOL[pids[0]]})
    print(f"  POPULATION  {N0} prompts   blind pool of {npool} criteria")

    # ================= E3 · effective k ==========================================================
    print("\n  E3 - THE EFFECTIVE k ACTUALLY EMITTED, per arm per nominal k")
    eff = {}
    for n, sat in S.items():
        eff[n] = {p: len({i for i, _ in sat[p]}) for p in pids}
    nfull = {p: len({i for i, _ in FULL[p]}) for p in pids}
    print(f"     {'nominal k':>10}" + "".join(f"{r:>16}" for r in FITRULES) +
          f"{'topw':>10}{'attain all':>12}")
    ATT = {}
    for k in KS:
        arms_k = [f"{r}_k{k}_fit1" for r in FITRULES] + [f"topw_k{k}", f"random_k{k}_s0"]
        att = [p for p in pids if all(eff[a][p] >= k for a in arms_k) and npool >= k]
        ATT[k] = att
        print(f"     {k:>10}" + "".join(f"{np.mean([eff[f'{r}_k{k}_fit1'][p] for p in pids]):>16.2f}"
                                        for r in FITRULES) +
              f"{np.mean([eff[f'topw_k{k}'][p] for p in pids]):>10.2f}"
              f"{len(att):>8} / {N0}")
    COMMON = sorted(set.intersection(*(set(ATT[k]) for k in KS)))
    print(f"     ⭐ prompts attaining NOMINAL k at every k (the common intersection): {len(COMMON)}")
    under = [k for k in KS if len(ATT[k]) < 300]
    print(f"     UNDERPOWERED k (fewer than 300 attaining): {under if under else 'none'}")
    out["e3"] = {"attain": {str(k): len(ATT[k]) for k in KS}, "common": len(COMMON),
                 "underpowered": under,
                 "mean_eff": {f"{r}_k{k}_fit1": float(np.mean([eff[f"{r}_k{k}_fit1"][p]
                                                               for p in pids]))
                              for k in KS for r in FITRULES}}

    def a2(sat, ps, idx=None):
        v = np.zeros(len(ps))
        for i, p in enumerate(ps):
            c = np.array(cls(yvec(sat[p], idx if idx is not None
                                  else sorted({j for j, _ in sat[p]}))))
            v[i] = float((H0[p] == c).mean())
        return v

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK")
    r805 = {r["arm"]: r for r in json.loads(R805J.read_text())["e2"]["rows"]}
    g4 = float(a2(S["greedy_k4_fit1"], pids).mean())
    i4 = float(a2(S["indep_k4_fit1"], pids).mean())
    ok = (abs(g4 - r805["greedy_k4_fit1"]["p0"]) < 1e-4
          and abs(i4 - r805["indep_k4_fit1"]["p0"]) < 1e-4)
    print(f"     `greedy_k4_fit1` on parity-0 {g4:.6f} vs R805's committed "
          f"{r805['greedy_k4_fit1']['p0']:.6f}")
    print(f"     `indep_k4_fit1`  on parity-0 {i4:.6f} vs R805's committed "
          f"{r805['indep_k4_fit1']['p0']:.6f}")
    print(f"     {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R805's committed arms did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"greedy_k4": g4, "indep_k4": i4}

    # ================= E1/E2/E4 ==================================================================
    print("\n  E1/E2/E4 - THE LEVEL GAP AT MATCHED k")
    rows, curves = [], {}
    for popname, POPS in (("attaining nominal k", ATT), ("common intersection", {k: COMMON
                                                                                 for k in KS})):
        print(f"\n     population: {popname}")
        print(f"     {'k':>3}{'n':>6}{'fitted':>10}{'topw':>9}{'random':>9}{'pool[0:k]':>11}"
              f"{'full':>8}   gap vs topw            gap vs pool")
        curves[popname] = {}
        for k in KS:
            ps = POPS[k]
            if len(ps) < 300:
                print(f"     {k:>3}{len(ps):>6}   UNDERPOWERED (<300 attaining) — excluded")
                continue
            rng = np.random.default_rng(1234)
            idx = rng.integers(0, len(ps), (NBOOT, len(ps)))
            fit = np.mean([a2(S[f"{r}_k{k}_fit1"], ps) for r in FITRULES], axis=0)
            tw = a2(S[f"topw_k{k}"], ps)
            rd = a2(S[f"random_k{k}_s0"], ps)
            pl = a2(POOL, ps, list(range(min(k, npool))))
            fu = a2(FULL, ps)
            g1, g2 = fit - tw, fit - pl
            b1, b2 = g1[idx].mean(axis=1), g2[idx].mean(axis=1)
            lo1, hi1 = np.percentile(b1, [2.5, 97.5])
            lo2, hi2 = np.percentile(b2, [2.5, 97.5])
            curves[popname][k] = {"n": len(ps), "fitted": float(fit.mean()),
                                  "topw": float(tw.mean()), "random": float(rd.mean()),
                                  "pool": float(pl.mean()), "full": float(fu.mean()),
                                  "gap_topw": float(g1.mean()), "lo1": float(lo1),
                                  "hi1": float(hi1), "gap_pool": float(g2.mean()),
                                  "lo2": float(lo2), "hi2": float(hi2),
                                  "p1": float(2 * min((b1 <= 0).mean(), (b1 >= 0).mean()))}
            c = curves[popname][k]
            print(f"     {k:>3}{len(ps):>6}{c['fitted']:>10.4f}{c['topw']:>9.4f}"
                  f"{c['random']:>9.4f}{c['pool']:>11.4f}{c['full']:>8.4f}   "
                  f"{c['gap_topw']:+.4f} [{lo1:+.4f},{hi1:+.4f}]  "
                  f"{c['gap_pool']:+.4f} [{lo2:+.4f},{hi2:+.4f}]")
            if popname == "common intersection":
                rows.append((k, c))
    out["curves"] = curves

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = [float((a2(POOL, COMMON, list(range(min(k, npool))))
                   - a2(POOL, COMMON, list(range(min(k, npool))))).mean()) for k in KS]
    plac_ok = all(abs(v) < 1e-15 for v in plac)
    print(f"     PLACEBO   the blind pool at k against ITSELF: {['%.1e' % v for v in plac]}   "
          f"{'PASS - exactly 0' if plac_ok else 'FAIL'}")
    twk = {k: float(a2(S[f"topw_k{k}"], COMMON).mean()) for k in KS}
    fuv = float(a2(FULL, COMMON).mean())
    conv = abs(twk[KS[-1]] - fuv) < abs(twk[KS[0]] - fuv)
    print(f"     POSITIVE  D1 `topw_k` -> `full` as k grows: " +
          "  ".join(f"k={k} {twk[k]:.4f}" for k in KS) + f"   full {fuv:.4f}")
    print(f"               |topw_k{KS[-1]} - full| {abs(twk[KS[-1]] - fuv):.4f} < "
          f"|topw_k{KS[0]} - full| {abs(twk[KS[0]] - fuv):.4f}: {conv}   "
          f"{'PASS' if conv else 'FAIL'}")
    g0 = curves["common intersection"].get(KS[0])
    g0_ok = bool(g0 and (g0["lo1"] > 0 or g0["hi1"] < 0))
    print(f"     g=0 CHECK at k={KS[0]} the fitted and honest arms must NOT coincide: gap "
          f"{g0['gap_topw']:+.4f} [{g0['lo1']:+.4f},{g0['hi1']:+.4f}]   "
          f"{'PASS - the control can fail' if g0_ok else 'FAIL'}")
    # ⛔ THE FIRST NEGATIVE CONTROL DESTROYED NOTHING, and for a structural reason worth recording:
    # `select_core.py` RE-INDEXES the selected criteria as 0..k-1 when it emits the npz
    # (`meta.append(f"{pid}|{j}|{x}")`, j the position in `sel`). So "another prompt's selected
    # indices" is always the same list [0..k-1] and permuting prompts changes nothing — the null
    # came back as a point mass +0.0156 [+0.0156, +0.0156], the same degenerate signature R809 hit.
    # The selections are NOT recoverable from the emitted npz. The structure the gap actually rests
    # on is the prompt<->core pairing, so that is what this control destroys instead: score each
    # prompt's fitted core against ANOTHER prompt's parity-0 humans.
    rngn = np.random.default_rng(707)
    kmax = max(k for k in KS if k in curves["common intersection"])
    base_fit = np.mean([a2(S[f"{r}_k{kmax}_fit1"], COMMON) for r in FITRULES], axis=0)
    tw_max = a2(S[f"topw_k{kmax}"], COMMON)
    CLS = {r: {p: np.array(cls(yvec(S[f"{r}_k{kmax}_fit1"][p],
                                    sorted({j for j, _ in S[f"{r}_k{kmax}_fit1"][p]}))))
               for p in COMMON} for r in FITRULES}
    nulls = []
    for _ in range(200):
        pm = rngn.permutation(len(COMMON))
        v = np.zeros(len(COMMON))
        for i, p in enumerate(COMMON):
            q = COMMON[pm[i]]
            v[i] = float(np.mean([(H0[p] == CLS[r][q]).mean() for r in FITRULES]))
        nulls.append(float((v - tw_max).mean()))
    nulls = np.array(nulls)
    real = float((base_fit - tw_max).mean())
    nlo, nhi = float(np.percentile(nulls, 2.5)), float(np.percentile(nulls, 97.5))
    neg_ok = bool(nlo < nhi and real > nulls.max())
    print(f"     NEGATIVE  each prompt's fitted core scored against ANOTHER prompt's parity-0 "
          f"humans, 200 permutations:")
    print(f"               null {nulls.mean():+.4f} [{nlo:+.4f}, {nhi:+.4f}] max {nulls.max():+.4f}"
          f"   real gap at k={kmax} {real:+.4f}   "
          f"{'PASS - outside the whole null' if neg_ok else 'FAIL'}")
    rngf = np.random.default_rng(55)
    sds = []
    for _ in range(20):
        sub = rngf.choice(len(COMMON), max(2, len(COMMON) // 2), replace=False)
        ps = [COMMON[i] for i in sub]
        f_ = np.mean([a2(S[f"{r}_k{kmax}_fit1"], ps) for r in FITRULES], axis=0)
        sds.append(float((f_ - a2(S[f"topw_k{kmax}"], ps)).mean()))
    NF = float(np.std(sds))
    print(f"     NOISE FLOOR  20 half-population resamples at k={kmax}: sd {NF:.4f}")
    gate = ok and plac_ok and conv and g0_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "topw_curve": twk, "full": fuv,
                       "positive_ok": conv, "g0_ok": g0_ok, "null_mean": float(nulls.mean()),
                       "null_max": float(nulls.max()), "real": real, "negative_ok": neg_ok,
                       "noise_floor": NF, "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    ci = curves["common intersection"]
    ks = sorted(ci)
    gaps = [ci[k]["gap_topw"] for k in ks]
    mono = all(gaps[i] >= gaps[i + 1] - 1e-12 for i in range(len(gaps) - 1))
    last = ci[ks[-1]]
    pv = [ci[k]["p1"] for k in ks]
    keep = bh(pv)
    print(f"     gaps vs topw across k: " + "  ".join(f"k={k} {ci[k]['gap_topw']:+.4f}"
                                                      for k in ks))
    print(f"     monotone decreasing: {mono}   gap at largest feasible k={ks[-1]}: "
          f"{last['gap_topw']:+.4f} [{last['lo1']:+.4f}, {last['hi1']:+.4f}]")
    print(f"     BH q=0.05 over {len(pv)} per-k gaps: {int(keep.sum())} survive, "
          f"{len(pv) - int(keep.sum())} do not — " +
          ", ".join(f"k={k}{'' if kp else ' (NOT)'}" for k, kp in zip(ks, keep)))
    if not gate:
        world = "UNVERIFIED"
    elif last["lo1"] <= 0 <= last["hi1"] and mono:
        world = "A"
    elif last["lo1"] > 0:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     -> WORLD {world}")
    out["world"] = world
    out["kill"] = {"gaps": gaps, "monotone": mono, "bh": [bool(x) for x in keep]}

    art = HERE / "results/size_or_fitting.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
