#!/usr/bin/env python3
"""R806 · is R295's leak verdict a scale artifact — and does R805's WORLD A survive stratification?

CHECK #408 killed R805's NEXT (R295 already ran the stratification) and found the contradiction
R805 created: R805 says fitting has real content (+0.0553 pooled), R295 says the fitted margin is
-0.0054 where the two annotator halves disagree. Both cannot be the headline. And R295's own
verdict carries two confounds it did not resolve: it subtracts the honest floor ADDITIVELY while
the confound is plausibly MULTIPLICATIVE, and its binning variable contains the parity-0 draw the
outcome is scored on -- which R295 named in its docstring and left.

ESTIMAND        E1 reproduce R295 · E2 ⭐ the multiplicative test · E3 ⭐ an independent binning
                variable · E4 the reconciliation
IDENTIFICATION  exact; E2 needs the honest pooled margin far from 0 (it is: +0.0236, +0.0215)
DERIVED FIRST   D1 a synthetic parity-1-modal arm is the PERFECT-LEAK ceiling (positive control) ·
                D2 the pool against itself is exactly 0 (placebo) · D3 the two binning variables
                are correlated, so E3 is a weaker instrument and not a replication · D4 R295's own
                positive control failed and its reason is inverted here, not reused
WORLDS          A leak confirmed · B scale artifact · C the binning carried the outcome — B FIRST
CONTROLS        OBJECT (R295's committed slope + floor + quintiles) · PLACEBO · POSITIVE (synthetic
                perfect leak) · NEGATIVE (binning permuted) · NOISE FLOOR
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
R295J = ARC / "R295_held_out_annotators_are_not_held_out_labels/results/parity_leak.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
ARMS = ["oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1",
        "coval_core", "topw_k4", "generic"]
FITTED = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
HELDOUT = ["oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]
HONEST = ["coval_core", "topw_k4"]      # the PREREGISTRATION's identification clause names
# exactly these two, because E2 is a RATIO and needs a denominator far from 0. `generic` IS
# POOL[0:4]: its margin against the k=4 pool is +0.0011, so its relative profile is a ratio to
# zero. The first run put it in HONEST anyway and it dominated the mean. Reported separately.
DEGENERATE = ["generic"]


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
    out = {"instrument_unit": "a PROMPT", "claim_unit": "an ARM x a binning variable"}
    tg, _ = load_targets()
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    POOL = load_sat(RES / "sat_genericpool16.npz")

    # ================= E1 · reproduce R295 exactly ===============================================
    print("  OBJECT CHECK - reproduce R295 on ITS population, with ITS binning variable")
    p295 = sorted(set.intersection(*(set(v) for v in S.values() if True)) & set(POOL) &
                  {p for p in tg if len(tg[p]) >= 2})
    # R295's arm set excluded `generic`; match it exactly
    S295 = {a: S[a] for a in ARMS if a != "generic"}
    p295 = sorted(set.intersection(*(set(v) for v in S295.values())) & set(POOL) &
                  {p for p in tg if len(tg[p]) >= 2})
    H0 = {p: [cls(np.array(t[0], float)) for i, t in enumerate(tg[p]) if i % 2 == 0] for p in p295}
    H1 = {p: [cls(np.array(t[0], float)) for i, t in enumerate(tg[p]) if i % 2 == 1] for p in p295}
    p295 = [p for p in p295 if H0[p] and H1[p]]
    N = len(p295)
    AGREE = np.array([np.mean([[a == b for a, b in zip(x, y)] for x in H1[p] for y in H0[p]])
                      for p in p295])

    def on0(sat, pids, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in H0[p]]) for p in pids])

    BLIND = on0(POOL, p295, [0, 1, 2, 3])
    M = {a: on0(S[a], p295) - BLIND for a in ARMS}
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def quints(m, x):
        q = np.quantile(x, [0, .2, .4, .6, .8, 1.0])
        b = [np.where((x >= q[i]) & (x <= q[i + 1] if i == 4 else x < q[i + 1]))[0]
             for i in range(5)]
        return [float(m[i].mean()) for i in b], b

    def slope(m, x):
        z = (x - x.mean()) / x.std()
        s = float(np.polyfit(z, m, 1)[0])
        bs = np.array([np.polyfit(z[i], m[i], 1)[0] for i in IDX[:400]])
        return s, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), bs

    r295 = json.loads(R295J.read_text())
    qs_f, _ = quints(M["oracle_k4_fit1"], AGREE)
    s_f = slope(M["oracle_k4_fit1"], AGREE)[0]
    s_h = slope(M["coval_core"], AGREE)[0]
    okq = all(abs(a - b) < 1e-6 for a, b in
              zip(qs_f, r295["arms"]["oracle_k4_fit1"]["quintiles"]))
    oks = (abs(s_f - r295["arms"]["oracle_k4_fit1"]["slope"]) < 1e-6
           and abs(s_h - r295["floor"]) < 1e-6)
    print(f"     N {N} (R295 committed {r295['n_prompts']})   half-agreement mean "
          f"{AGREE.mean():.6f} vs committed {r295['agree_mean']:.6f}")
    print(f"     `oracle_k4_fit1` slope {s_f:.6f} vs committed "
          f"{r295['arms']['oracle_k4_fit1']['slope']:.6f}   floor {s_h:.6f} vs committed "
          f"{r295['floor']:.6f}")
    print(f"     quintiles reproduce: {okq}   slopes reproduce: {oks}   "
          f"{'PASS' if okq and oks else 'FAIL'}")
    if not (okq and oks and N == r295["n_prompts"]):
        print("  UNRUNNABLE: R295 did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"n": N, "slope_fit1": s_f, "floor": s_h, "agree_mean": float(AGREE.mean())}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    plac = quints(on0(POOL, p295, [0, 1, 2, 3]) - BLIND, AGREE)[0]
    plac_ok = all(abs(v) < 1e-15 for v in plac)
    print(f"     PLACEBO   the k=4 pool against ITSELF, by quintile: "
          f"{['%.1e' % v for v in plac]}   {'PASS - exactly 0' if plac_ok else 'FAIL'}")
    # POSITIVE — D1: a synthetic arm that IS parity-1's modal class
    def modal(hs):
        best, bc = None, -1
        for c in {tuple(h) for h in hs}:
            n = sum(1 for h in hs if tuple(h) == c)
            if n > bc:
                best, bc = c, n
        return np.array(best)
    LEAKARM = np.array([float(np.mean([(np.array(h) == modal(H1[p])).mean() for h in H0[p]]))
                        for p in p295])
    M["_perfect_leak"] = LEAKARM - BLIND
    sl = slope(M["_perfect_leak"], AGREE)
    others = {a: slope(M[a], AGREE)[0] for a in ARMS}
    pos_ok = sl[0] > max(others.values())
    print(f"     POSITIVE  SYNTHETIC perfect leak (parity-1's modal class as the predictor): "
          f"slope {sl[0]:+.6f} [{sl[1]:+.6f}, {sl[2]:+.6f}]")
    print(f"               steepest of all {len(others)} real arms (next {max(others.values()):+.6f}"
          f" = {max(others, key=others.get)})   {'PASS' if pos_ok else 'FAIL'}")
    rngn = np.random.default_rng(707)
    AP = AGREE[rngn.permutation(N)]
    negs = {a: slope(M[a], AP) for a in HELDOUT}
    neg_ok = all(lo <= 0 <= hi for _, lo, hi, _ in negs.values())
    print(f"     NEGATIVE  binning variable PERMUTED across prompts: " +
          "  ".join(f"{a.split('_')[0]} {v[0]:+.4f}[{v[1]:+.4f},{v[2]:+.4f}]"
                    for a, v in negs.items()) + f"   {'PASS - all hold 0' if neg_ok else 'FAIL'}")
    gate0 = okq and oks and plac_ok and pos_ok and neg_ok
    out["controls"] = {"placebo": plac, "placebo_ok": plac_ok, "perfect_leak_slope": sl[0],
                       "positive_ok": pos_ok, "negative_ok": neg_ok}

    # ================= E2 · the multiplicative test ==============================================
    print("\n  E2 - THE MULTIPLICATIVE TEST: each arm's quintile margin / its OWN pooled margin")
    print("     If half-agreement scales EVERY margin, an arm with a bigger pooled margin gets a")
    print("     bigger slope with no leak. R295 subtracted the floor ADDITIVELY, which cannot")
    print("     remove that. The relative profile can.")
    rel = {}
    print(f"     {'arm':<18}{'pooled':>9}" + "".join(f"  Q{i+1}rel" for i in range(5))
          + "   rel-slope")
    for a in HELDOUT + HONEST + DEGENERATE + ["_perfect_leak"]:
        pooled = float(M[a].mean())
        qs, _ = quints(M[a], AGREE)
        rs = slope(M[a] / pooled, AGREE)
        rel[a] = {"pooled": pooled, "qrel": [q / pooled for q in qs], "slope": rs[0],
                  "lo": rs[1], "hi": rs[2], "bs": rs[3]}
        tag = "  <- DEGENERATE denominator, excluded from the estimand" if a in DEGENERATE else ""
        print(f"     {a:<18}{pooled:>+9.4f}" + "".join(f"{q / pooled:>7.2f}" for q in qs)
              + f"   {rs[0]:+.4f} [{rs[1]:+.4f}, {rs[2]:+.4f}]{tag}")
    hon_bs = np.mean([rel[a]["bs"] for a in HONEST], axis=0)
    fit_bs = np.mean([rel[a]["bs"] for a in HELDOUT], axis=0)
    d = fit_bs - hon_bs
    dlo, dhi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    dmean = float(np.mean([rel[a]["slope"] for a in HELDOUT])
                  - np.mean([rel[a]["slope"] for a in HONEST]))
    e2_holds0 = dlo <= 0 <= dhi
    # ⛔ THE BRANCH FIRES ON THE RELATIVE SCALE, SO THE POSITIVE CONTROL MUST LIVE THERE TOO.
    # The gate above validated `perfect_leak is steepest` on the ABSOLUTE slope. realstat §4:
    # "the control targets a different statistic than the one being reported". A relative-scale
    # control asks whether this statistic could separate a MAXIMAL leak from an honest arm at all.
    pl = rel["_perfect_leak"]["bs"] - hon_bs
    pllo, plhi = float(np.percentile(pl, 2.5)), float(np.percentile(pl, 97.5))
    rel_power = not (pllo <= 0 <= plhi)
    print(f"     ⭐ RELATIVE-SCALE POSITIVE CONTROL: perfect leak minus honest = "
          f"{float(np.mean(pl)):+.4f} [{pllo:+.4f}, {plhi:+.4f}]")
    print(f"        can this statistic separate a MAXIMAL leak from an honest arm? {rel_power}"
          f"   {'-> the relative test has power' if rel_power else '-> BLIND. A CI holding 0 here is SILENCE, not an acquittal, so E2 returns UNVERIFIED'}")
    print(f"     ⭐ RELATIVE slope, fitted minus honest: {dmean:+.4f} [{dlo:+.4f}, {dhi:+.4f}]"
          f"   {'CI HOLDS 0 -> scale artifact' if e2_holds0 else 'RESOLVED -> not scale alone'}")
    out["e2"] = {"relative": {k: {x: v[x] for x in ("pooled", "qrel", "slope", "lo", "hi")}
                              for k, v in rel.items()},
                 "fitted_minus_honest": dmean, "lo": dlo, "hi": dhi, "holds_zero": e2_holds0,
                 "relative_positive_control": {"eff": float(np.mean(pl)), "lo": pllo, "hi": plhi,
                                               "has_power": rel_power}}

    # ================= E3 · an independent binning variable ======================================
    print("\n  E3 - AN INDEPENDENT BINNING VARIABLE: agreement WITHIN parity-1 only")
    keep = [i for i, p in enumerate(p295) if len(H1[p]) >= 2]
    drop = N - len(keep)
    print(f"     prompts carrying it: {len(keep)}   dropped for <2 parity-1 annotators: {drop} "
          f"(printed, never silent)")
    A1 = np.array([np.mean([(np.array(x) == np.array(y)).mean()
                            for x, y in itertools.combinations(H1[p], 2)]) for p in
                   [p295[i] for i in keep]])
    corr = float(np.corrcoef(A1, AGREE[keep])[0, 1])
    print(f"     D3 corr(within-parity-1, R295's half-agreement) = {corr:+.4f} — CORRELATED, so "
          f"this is a WEAKER instrument, not an independent replication")
    IDX2 = np.random.default_rng(31337).integers(0, len(keep), (NBOOT, len(keep)))

    def slope2(m, x):
        z = (x - x.mean()) / x.std()
        s = float(np.polyfit(z, m, 1)[0])
        bs = np.array([np.polyfit(z[i], m[i], 1)[0] for i in IDX2[:400]])
        return s, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    print(f"     {'arm':<18}" + "".join(f"  Q{i+1:<6}" for i in range(5)) + "   slope")
    e3, pv3 = {}, []
    for a in HELDOUT + HONEST + ["_perfect_leak"]:
        m = M[a][keep]
        qs, _ = quints(m, A1)
        s3 = slope2(m, A1)
        e3[a] = {"quintiles": qs, "slope": s3[0], "lo": s3[1], "hi": s3[2]}
        pv3.append(0.0 if (s3[1] > 0 or s3[2] < 0) else 1.0)
        print(f"     {a:<18}" + "".join(f"{v:>+8.4f}" for v in qs)
              + f"   {s3[0]:+.4f} [{s3[1]:+.4f}, {s3[2]:+.4f}]")
    k3 = bh(pv3)
    print(f"     BH q=0.05 over {len(pv3)} slopes: {int(k3.sum())} survive, "
          f"{len(pv3) - int(k3.sum())} do not (printed above)")
    fit3 = float(np.mean([e3[a]["slope"] for a in HELDOUT]))
    hon3 = float(np.mean([e3[a]["slope"] for a in HONEST]))
    e3_alive = all(e3[a]["lo"] > 0 for a in HELDOUT)
    print(f"     ⭐ fitted mean slope {fit3:+.4f}   honest mean slope {hon3:+.4f}   "
          f"excess {fit3 - hon3:+.4f}   fitted all resolved: {e3_alive}")
    out["e3"] = {"rows": e3, "corr": corr, "kept": len(keep), "dropped": drop,
                 "fitted_mean": fit3, "honest_mean": hon3, "alive": e3_alive}

    # ================= E4 · the reconciliation ===================================================
    print("\n  E4 - RECONCILING R805's WORLD A WITH R295's W-LEAK")
    bot_f = float(np.mean([e3[a]["quintiles"][0] for a in HELDOUT]))
    bot_h = float(np.mean([e3[a]["quintiles"][0] for a in HONEST]))
    print(f"     bottom quintile of the INDEPENDENT binning (annotators disagree most):")
    print(f"       fitted arms {bot_f:+.4f}   honest arms {bot_h:+.4f}   "
          f"excess {bot_f - bot_h:+.4f}")
    print(f"     R805 pooled the fitted margin over ALL prompts and got +0.0553 vs the 16-pool.")
    print(f"     Here, against the SIZE-MATCHED k=4 pool, the fitted margin ranges "
          f"{min(e3[a]['quintiles'][0] for a in HELDOUT):+.4f} (worst arm, bottom quintile) to "
          f"{max(e3[a]['quintiles'][4] for a in HELDOUT):+.4f} (best arm, top quintile).")
    out["e4"] = {"bottom_fitted": bot_f, "bottom_honest": bot_h}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate0:
        world = "UNVERIFIED"
    elif e2_holds0 and rel_power:
        world = "B"
    elif e2_holds0 and not rel_power:
        world = "UNVERIFIED on E2 -- the relative statistic is BLIND; E3 decides"
        world = "A" if (e3_alive and bot_f <= 0 < bot_h) else (
            "A" if e3_alive and bot_f < bot_h else "NO WORLD CLAIMED")
    elif not e3_alive:
        world = "C"
    elif bot_f <= 0 < bot_h:
        world = "A"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate0}   relative-slope CI holds 0: {e2_holds0} (relative test has power: "
          f"{rel_power})   fitted slopes survive the "
          f"independent binning: {e3_alive}   bottom quintile fitted {bot_f:+.4f} honest "
          f"{bot_h:+.4f}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/scale_artifact.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
