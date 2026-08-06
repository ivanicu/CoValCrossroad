#!/usr/bin/env python3
"""R798 · are the rubric's criteria individually weaker, or does the loss appear only in AGGREGATE?

R797 measured `genericpool16` beating `coval_full` at predicting a prompt's own humans by
+0.0335 [+0.0251, +0.0420]. CHECK #400 found (a) singleton agreement mixes DISCRIMINATION with
ACCURACY — zero-sign shares 0.0444 vs 0.0508, small and running AGAINST the pool — and (b) each
`full` criterion appears on EXACTLY ONE prompt, so no per-criterion estimate exists. The identified
estimand is the distribution over criterion INSTANCES.

ESTIMAND        E1 ⭐ the two singleton distributions · E2 ⭐ D1's decomposition · E3 ⭐ individual
                versus aggregate · E4 the satisfaction-spread confound
IDENTIFICATION  instance and pool level only. ⛔ NOT identified: any individual `full` criterion (D2)
DERIVED FIRST   D1 composite = (1 − tie) × accuracy, exactly — the placebo · D2 a `full` criterion is
                observed on one prompt · D3 the aggregate is NOT the mean of the singletons, which is
                what makes A and B distinguishable · D4 the pool's instances cluster by CRITERION
                (16), not by instance — the most likely place to overstate precision
WORLDS          A individually weaker · B only in aggregate · C summing destroys — C checked FIRST
CONTROLS        OBJECT (both summed A2s against committed) · PLACEBO (D1's identity) · POSITIVE
                (sign-flip dose) · NEGATIVE (humans shuffled) · CLUSTERING (both, plus the naive one
                printed to show what it overstates) · CONFOUND (spread matching) · NOISE FLOOR
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
R789 = ARC / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json"
R793 = ARC / "R793_seven_artifacts_nobody_opened/results/coverage.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 2.801585
NBOOT = 1200
SEEDS = [31337, 31338, 31339]
AGG_GAP = 0.0335


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
    out = {"instrument_unit": "a (prompt, criterion, annotator) judgement", "claim_unit": "a POOL",
           "reporting_unit": "a criterion INSTANCE"}

    print("  OBJECT CHECK")
    lad = json.loads(R789.read_text())
    cov = json.loads(R793.read_text())["e2"]
    targets, _ = load_targets()
    SF = load_sat(RES / "sat_full.npz")
    SG = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(p for p in SF if p in SG and p in targets and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]

    def summed_a2(S):
        v = np.zeros(P)
        for a, p in enumerate(pids):
            c = cls(yvec(S[p], sorted({i for i, _ in S[p]})))
            v[a] = (HC[a] == c).mean()
        return v

    af, ag = summed_a2(SF), summed_a2(SG)
    ok = (abs(float(af.mean()) - cov["full"]["vs_human_all"]) < 1e-9
          and abs(float(ag.mean()) - lad["e2"]["a2"]["genericpool16"]) < 1e-9)
    print(f"     prompts {P}   summed `full` {af.mean():.10f} vs committed "
          f"{cov['full']['vs_human_all']:.10f}   summed pool {ag.mean():.10f} vs committed "
          f"{lad['e2']['a2']['genericpool16']:.10f}   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: a summed aggregate disagrees with its committed value. Exit 2.")
        return 2

    # ---- singleton instances -------------------------------------------------------------------
    def singles(S, tag):
        comp, tie, acc, acct, spread, pidx, cidx = [], [], [], [], [], [], []
        for a, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for ci, i in enumerate(ii):
                y = np.array([S[p].get((i, x), 0.0) for x in L])
                s = np.sign(y[[u for u, _ in PR]] - y[[v for _, v in PR]])
                m = (HC[a] == s)
                comp.append(float(m.mean()))
                nz = s != 0
                tie.append(float((~nz).mean()))
                acc.append(float(m[:, nz].mean()) if nz.any() else np.nan)
                acct.append(float(m[:, ~nz].mean()) if (~nz).any() else 0.0)
                spread.append(float(y.std()))
                pidx.append(a)
                cidx.append(i if tag == "pool" else -1)
        return (np.array(comp), np.array(tie), np.array(acc), np.array(spread),
                np.array(pidx), np.array(cidx), np.array(acct))

    F = singles(SF, "full")
    G = singles(SG, "pool")
    print(f"     criterion INSTANCES: `full` {len(F[0])} (each on ONE prompt, D2)   pool "
          f"{len(G[0])} = 16 criteria x {P} prompts")
    out["object"] = {"prompts": P, "full_instances": len(F[0]), "pool_instances": len(G[0]),
                     "full_agg": float(af.mean()), "pool_agg": float(ag.mean())}

    # PLACEBO: D1's identity
    # ⛔ D1 AS REGISTERED WAS FALSE, AND ITS OWN PLACEBO CAUGHT IT AT |Δ| 3.246e-01. I derived
    # `composite = (1 - tie) * accuracy` on the assumption that a tied sign can never agree with a
    # human. It can: `cls()` returns 0 whenever a HUMAN ranks two responses equally, so a tie-tie
    # match counts. The true identity carries both terms, and it is checked here instead.
    def ident(X):
        return float(np.nanmax(np.abs(
            X[0] - ((1 - X[1]) * np.nan_to_num(X[2], nan=0.0) + X[1] * X[6]))))
    plac = max(ident(F), ident(G))
    print(f"     PLACEBO  ⛔ D1 as registered was FALSE (a tie CAN agree, when the human also ties);")
    print(f"              corrected identity  composite == (1-tie)*acc_nontied + tie*acc_tied   "
          f"worst |Δ| {plac:.3e}   {'PASS' if plac < 1e-12 else 'FAIL'}")

    rng = np.random.default_rng(SEEDS[0])

    def cl_ci(v, groups):
        """cluster bootstrap over `groups`."""
        gs = np.unique(groups)
        idx = {g: np.where(groups == g)[0] for g in gs}
        b = np.empty(NBOOT)
        for t in range(NBOOT):
            pick = rng.choice(gs, len(gs), replace=True)
            b[t] = np.concatenate([idx[g] for g in pick]).size and \
                np.nanmean(np.concatenate([v[idx[g]] for g in pick]))
        return float(np.nanmean(v)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    # ================= E1 · the two distributions =================================================
    print("\n  E1 - SINGLETON AGREEMENT WITH THE HUMAN, PER CRITERION INSTANCE")
    for nm, X, gr in (("full", F, F[4]), ("pool", G, G[5])):
        m, lo, hi = cl_ci(X[0], gr)
        q = np.percentile(X[0], [5, 25, 50, 75, 95])
        print(f"     {nm:<5} n={len(X[0]):<6} mean {m:.4f} [{lo:.4f}, {hi:.4f}] (clustered by "
              f"{'PROMPT' if nm == 'full' else 'CRITERION, 16'})   quantiles "
              f"{'  '.join(f'{z:.3f}' for z in q)}")
    # the paired-by-prompt difference of prompt-level singleton means
    pm_f = np.array([np.nanmean(F[0][F[4] == a]) for a in range(P)])
    pm_g = np.array([np.nanmean(G[0][G[4] == a]) for a in range(P)])
    d = pm_g - pm_f
    BI = rng.integers(0, P, size=(NBOOT, P))
    b = d[BI].mean(axis=1)
    e, lo, hi = float(d.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
    mde = ZEFF * float(d.std(ddof=1)) / math.sqrt(P)
    p1 = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
    res1 = bool((lo > 0 or hi < 0) and abs(e) >= mde)
    naive = 1.96 * float(np.nanstd(G[0], ddof=1)) / math.sqrt(len(G[0]))
    print(f"     ⭐ paired-by-prompt singleton gap (pool − full) {e:+.4f} [{lo:+.4f}, {hi:+.4f}]  "
          f"mde {mde:.4f}   {'RESOLVED' if res1 else 'unresolved'}")
    print(f"     ⚠ D4: the NAIVE independent-instance half-width for the pool would be ±{naive:.4f}, "
          f"treating {len(G[0])} instances as independent when they are 16 criteria seen {P} times")
    out["e1"] = {"gap": e, "lo": lo, "hi": hi, "mde": mde, "p": max(p1, 1 / (NBOOT + 1)),
                 "resolved": res1, "naive_halfwidth": naive}

    # ================= E2 · the decomposition =====================================================
    print("\n  E2 - D1's DECOMPOSITION: DISCRIMINATION AND ACCURACY")
    pv = [max(p1, 1 / (NBOOT + 1))]
    comps = {}
    for lab, i in (("discrimination (1 - tie)", 1), ("accuracy on non-tied", 2)):
        vf = (1 - F[i]) if i == 1 else F[i]
        vg = (1 - G[i]) if i == 1 else G[i]
        pf = np.array([np.nanmean(vf[F[4] == a]) for a in range(P)])
        pg = np.array([np.nanmean(vg[G[4] == a]) for a in range(P)])
        dd = pg - pf
        bb = dd[BI].mean(axis=1)
        ee, l2, h2 = float(dd.mean()), float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5))
        m2 = ZEFF * float(dd.std(ddof=1)) / math.sqrt(P)
        p2 = max(2.0 * min(float((bb <= 0).mean()), float((bb >= 0).mean())), 1 / (NBOOT + 1))
        pv.append(p2)
        comps[lab] = {"full": float(np.nanmean(vf)), "pool": float(np.nanmean(vg)), "gap": ee,
                      "lo": l2, "hi": h2, "mde": m2,
                      "resolved": bool((l2 > 0 or h2 < 0) and abs(ee) >= m2)}
        print(f"     {lab:<26} full {np.nanmean(vf):.4f}   pool {np.nanmean(vg):.4f}   gap "
              f"{ee:+.4f} [{l2:+.4f}, {h2:+.4f}]  mde {m2:.4f}   "
              f"{'RESOLVED' if comps[lab]['resolved'] else 'unresolved'}")
    out["e2"] = comps

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    # ⛔ THE FIRST POSITIVE DEMANDED A 0.05 DROP FROM AN OPERATION THAT CANNOT PRODUCE ONE. Mirroring
    # the agreement value (v -> 1-v) at share 1.0 moves a mean of 0.5142 to 0.4858 — a maximum drop
    # of 0.0284 — so the threshold sat OUTSIDE the achievable band. §4's *control that cannot PASS*.
    # Repaired: invert the criterion's SIGN VECTOR (a real inversion of its direction), and compute
    # the ceiling from the share-1.0 cell rather than asserting one.
    frng = np.random.default_rng(SEEDS[0] + 7)
    dose = {}
    base = float(np.nanmean(G[0]))
    inv = np.empty(len(G[0]))
    j = 0
    for a, p in enumerate(pids):
        for i in sorted({i for i, _ in SG[p]}):
            y = np.array([SG[p].get((i, x), 0.0) for x in L])
            sgn = -np.sign(y[[u for u, _ in PR]] - y[[v for _, v in PR]])
            inv[j] = (HC[a] == sgn).mean()
            j += 1
    for s_ in (0.0, 0.1, 0.25, 0.5, 1.0):
        flip = frng.random(len(G[0])) < s_
        v = np.where(flip, inv, G[0])
        dose[str(s_)] = float(v.mean())
        print(f"     POSITIVE  criterion-direction inverted on share {s_:<5} pool singleton mean "
              f"{v.mean():.4f}")
    floor, ceiling = dose["0.0"], dose["1.0"]
    posok = abs(floor - base) < 1e-12 and ceiling < floor and dose["0.5"] < floor - (floor - ceiling) / 4
    print(f"     POSITIVE  band COMPUTED: floor {floor:.4f} (unmoved at share 0) → ceiling "
          f"{ceiling:.4f} (full inversion). The achievable drop is {floor - ceiling:.4f}; the "
          f"criterion is a quarter of it, not an asserted 0.05.   {'PASS' if posok else 'FAIL'}")

    nrng = np.random.default_rng(SEEDS[0] + 13)
    perm = nrng.permutation(P)
    HCs = [HC[i] for i in perm]

    def sh_mean(S):
        tot, n = 0.0, 0
        for a, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for i in ii:
                y = np.array([S[p].get((i, x), 0.0) for x in L])
                sgn = np.sign(y[[u for u, _ in PR]] - y[[v for _, v in PR]])
                tot += (HCs[a] == sgn).mean()
                n += 1
        return tot / n

    shf, shg = sh_mean(SF), sh_mean(SG)
    negok = shf < np.nanmean(F[0]) - 0.02 and shg < np.nanmean(G[0]) - 0.02
    print(f"     NEGATIVE  human classes shuffled: full singleton {np.nanmean(F[0]):.4f} → "
          f"{shf:.4f}, pool {np.nanmean(G[0]):.4f} → {shg:.4f}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'singleton agreement is a property of the CRITERIA "
          f"alone rather than of their fit to THIS prompt's humans'")

    # ================= E4 · the satisfaction-spread confound ======================================
    print("\n  E4 - THE SATISFACTION-SPREAD CONFOUND")
    print(f"     spread (sd of a criterion's satisfaction across the 4 responses): full "
          f"{F[3].mean():.4f}   pool {G[3].mean():.4f}")
    edges = np.percentile(np.concatenate([F[3], G[3]]), [20, 40, 60, 80])
    bf, bg = np.digitize(F[3], edges), np.digitize(G[3], edges)
    mf = np.array([np.nanmean(F[0][bf == q]) for q in range(5)])
    mg = np.array([np.nanmean(G[0][bg == q]) for q in range(5)])
    wts = np.array([(bf == q).sum() for q in range(5)], float)
    wts /= wts.sum()
    matched = float((wts * (mg - mf)).sum())
    print("     spread quintile:  " + "  ".join(f"Q{q + 1} {mg[q] - mf[q]:+.4f}" for q in range(5)))
    print(f"     ⭐ spread-MATCHED gap (reweighted to `full`'s spread distribution) {matched:+.4f}   "
          f"against the raw {e:+.4f}")
    out["e4"] = {"spread_full": float(F[3].mean()), "spread_pool": float(G[3].mean()),
                 "quintile_gaps": (mg - mf).tolist(), "matched_gap": matched}

    frng2 = np.random.default_rng(SEEDS[0] + 17)
    halves = []
    for _ in range(10):
        s1 = s2 = 0.0
        n = 0
        for a, p in enumerate(pids):
            k = len(HC[a])
            pm_ = frng2.permutation(k)
            i1, i2 = pm_[:k // 2], pm_[k // 2:2 * (k // 2)]
            ii = sorted({i for i, _ in SG[p]})
            for i in ii:
                y = np.array([SG[p].get((i, x), 0.0) for x in L])
                sgn = np.sign(y[[u for u, _ in PR]] - y[[v for _, v in PR]])
                s1 += (HC[a][i1] == sgn).mean()
                s2 += (HC[a][i2] == sgn).mean()
                n += 1
        halves.append(abs(s1 - s2) / n)
    print(f"     NOISE FLOOR  annotator split-half on the pool's singleton mean, 10 draws: "
          f"{np.mean(halves):.6f}")

    gate = ok and plac < 1e-12 and posok and negok
    out["controls"] = {"placebo_identity": plac, "dose": dose, "positive_ok": posok,
                       "neg_full": shf, "neg_pool": shg, "negative_ok": negok,
                       "split_half": float(np.mean(halves)), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    keep = bh(np.array(pv))
    print(f"\n  MULTIPLICITY  {len(pv)} tests, BH q=0.05: surviving {int(keep.sum())}   "
          f"not {len(pv) - int(keep.sum())}")

    # ================= E3 · individual versus aggregate ===========================================
    print("\n  E3 - INDIVIDUAL VERSUS AGGREGATE")
    print(f"     singleton gap {e:+.4f}   aggregate gap (R797) +{AGG_GAP:.4f}   ratio "
          f"{e / AGG_GAP:+.3f}")
    print(f"     ⚠ D3: these are DIFFERENT quantities — summing k criteria then taking signs is not "
          f"averaging k singleton classes — so either could be larger and the comparison is the "
          f"finding, not an inconsistency.")
    out["e3"] = {"singleton_gap": e, "aggregate_gap": AGG_GAP, "ratio": e / AGG_GAP}

    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif res1 and e < 0:
        world = "C"
    elif res1 and e >= AGG_GAP / 2:
        world = "A"
    elif (not res1) or e < AGG_GAP / 2:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   singleton gap {e:+.4f} resolved {res1}   half the aggregate "
          f"{AGG_GAP / 2:.5f}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/singletons.json"
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
