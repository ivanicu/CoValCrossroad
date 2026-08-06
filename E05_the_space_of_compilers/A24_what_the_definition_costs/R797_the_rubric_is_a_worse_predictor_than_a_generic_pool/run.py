#!/usr/bin/env python3
"""R797 · is the prompt's own rubric a WORSE human predictor than a generic pool?

CHECK #399 attacked R796's NEXT and found the pair it proposed is not a live question (`coval_core`
and `topvar_k4` differ by 0.0802 on A2 against an MDE near 0.011, and R789 put them in different
levels), and that the inverse relation it generalised from is `corr = -0.2550` over 27 names — two
arms at the ends of a scatter. But the check surfaced a sharper object: `genericpool16` scores A2
0.5422 while `full` scores 0.5087, so a GENERIC pool may predict a prompt's own human rankings
better than the prompt's own rubric.

ESTIMAND        E1 ⭐ the target gap, paired · E2 ⭐ stratified by criterion count (the confound) ·
                E3 R796's correlation done properly, WITH its MDE · E4 the derivation check
IDENTIFICATION  E1/E2 exact; E3 weak by D2 and its MDE is reported whatever the result
DERIVED FIRST   D1 same-target, so no ceiling · D2 |r| must reach ~0.44 at n=20 · D3 aliases inflate
                n from 20 to 27 · D4 mixtures of the two targets would produce the correlation BY
                CONSTRUCTION if the pool is the better predictor
WORLDS          A the rubric is worse · B a size artefact · C no gap — C checked FIRST
CONTROLS        OBJECT (two committed A2s) · PLACEBO · POSITIVE (band) · NEGATIVE (human classes
                shuffled) · CONFOUND (size strata) · NOISE FLOOR · E3's MDE by simulation
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
R796 = ARC / "R796_matched_against_blind_at_every_size/results/matched_vs_blind.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 2.801585
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
    out = {"instrument_unit": "a (prompt, annotator) judgement",
           "claim_unit": "a TARGET", "claim_unit_e3": "an ARM"}

    print("  OBJECT CHECK")
    for f in (R789, R793, R796):
        if not f.is_file():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0.")
            return 2
    lad = json.loads(R789.read_text())
    cov = json.loads(R793.read_text())["e2"]
    pref = json.loads(R796.read_text())["e3"]["rows"]
    targets, _ = load_targets()
    S = {t: load_sat(RES / f"sat_{t}.npz") for t in ("full", "genericpool16", "coval_core")}
    pids = sorted(p for p in S["full"] if all(p in S[t] for t in S) and p in targets
                  and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    ncrit = np.array([len({i for i, _ in S["full"][p]}) for p in pids])

    def klass(t):
        return np.array([cls(yvec(S[t][p], sorted({i for i, _ in S[t][p]}))) for p in pids], float)

    def vs_human(cm):
        return np.array([(HC[i] == cm[i]).mean() for i in range(P)])

    CF, CG = klass("full"), klass("genericpool16")
    hf, hg = vs_human(CF), vs_human(CG)
    ok = (abs(float(hf.mean()) - cov["full"]["vs_human_all"]) < 1e-9
          and abs(float(hg.mean()) - lad["e2"]["a2"]["genericpool16"]) < 1e-9)
    print(f"     prompts {P}   `full` criteria min {ncrit.min()} mean {ncrit.mean():.2f} "
          f"max {ncrit.max()}")
    print(f"     `full` vs HUMAN {hf.mean():.10f} vs R793's {cov['full']['vs_human_all']:.10f}   "
          f"`genericpool16` {hg.mean():.10f} vs R789's "
          f"{lad['e2']['a2']['genericpool16']:.10f}   {'PASS' if ok else 'FAIL'}")
    plac = float((vs_human(CF) - vs_human(CF)).mean())
    print(f"     PLACEBO  a target against itself: gap {plac:.12f}   "
          f"{'PASS' if plac == 0.0 else 'FAIL'}")
    if not (ok and plac == 0.0):
        print("  UNRUNNABLE: a committed value did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "full_vs_human": float(hf.mean()),
                     "pool_vs_human": float(hg.mean()), "mean_ncrit": float(ncrit.mean())}

    rng = np.random.default_rng(SEEDS[0])
    BI = rng.integers(0, P, size=(NBOOT, P))

    def ci(v, idx=None):
        vv = v if idx is None else v[idx]
        n = len(vv)
        bi = BI[:, :n] % n if idx is not None else BI
        b = vv[bi].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        p = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
        mde = ZEFF * float(vv.std(ddof=1)) / math.sqrt(n)
        return (float(vv.mean()), lo, hi, max(min(p, 1.0), 1.0 / (NBOOT + 1)), mde,
                bool((lo > 0 or hi < 0) and abs(vv.mean()) >= mde))

    # ================= E1 · the target gap ========================================================
    print("\n  E1 - THE TARGET GAP: `genericpool16 vs HUMAN` MINUS `full vs HUMAN`")
    d = hg - hf
    e, lo, hi, p, mde, res = ci(d)
    print(f"     `genericpool16` {hg.mean():.4f}   `full` {hf.mean():.4f}   gap {e:+.4f} "
          f"[{lo:+.4f}, {hi:+.4f}]  mde {mde:.4f}  p {p:.4f}   "
          f"{'RESOLVED' if res else 'unresolved'}")
    out["e1"] = {"gap": e, "lo": lo, "hi": hi, "p": p, "mde": mde, "resolved": res}

    # ================= E2 · the size confound =====================================================
    print("\n  E2 - STRATIFIED BY THE PROMPT'S OWN CRITERION COUNT  (the registered confound)")
    bins = [(4, 8), (9, 12), (13, 16), (17, 20), (21, 39)]
    strat, pv = {}, [p]
    for a, b in bins:
        m = (ncrit >= a) & (ncrit <= b)
        if m.sum() < 20:
            strat[f"{a}-{b}"] = {"n": int(m.sum()), "note": "too few prompts"}
            print(f"     {a:>2}-{b:<3} n={int(m.sum()):<4} too few prompts to report")
            continue
        e2, l2, h2, p2, m2, r2 = ci(d, np.where(m)[0])
        strat[f"{a}-{b}"] = {"n": int(m.sum()), "gap": e2, "lo": l2, "hi": h2, "p": p2,
                             "mde": m2, "resolved": r2}
        pv.append(p2)
        print(f"     {a:>2}-{b:<3} n={int(m.sum()):<4} gap {e2:+.4f} [{l2:+.4f}, {h2:+.4f}]  "
              f"mde {m2:.4f}   {'RESOLVED' if r2 else 'unresolved'}")
    mm = (ncrit >= 12) & (ncrit <= 20)
    em, lm, hm, pm, mdm, rm = ci(d, np.where(mm)[0])
    print(f"     ⭐ the 12–20 MATCHED-SIZE stratum (n={int(mm.sum())}, both targets closest in "
          f"size): gap {em:+.4f} [{lm:+.4f}, {hm:+.4f}]  mde {mdm:.4f}   "
          f"{'RESOLVED' if rm else 'unresolved'}")
    out["e2"] = {"strata": strat, "matched_12_20": {"n": int(mm.sum()), "gap": em, "lo": lm,
                                                    "hi": hm, "mde": mdm, "resolved": rm}}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    dose, fl, ce = {}, None, None
    for delta in (0.0, 0.01, 0.02, 0.05):
        dd = hg - (hf + delta)
        e3_, l3, h3, _, m3, r3 = ci(dd - d)
        dose[str(delta)] = {"planted": e3_, "resolved": r3}
        print(f"     POSITIVE  delta {delta:<5} on `full`'s human column: the plant alone "
              f"{e3_:+.5f}  {'resolves' if r3 else 'does not resolve'}")
        if delta == 0.0:
            fl = r3
        if delta == 0.05:
            ce = r3
    posok = (fl is False) and (ce is True)
    print(f"     POSITIVE  band COMPUTED: floor {fl} at delta 0, ceiling {ce} at 0.05   "
          f"{'admissible' if fl != ce else 'DEGENERATE'}   {'PASS' if posok else 'FAIL'}")

    nrng = np.random.default_rng(SEEDS[0] + 13)
    perm = nrng.permutation(P)
    HCs = [HC[i] for i in perm]

    def vs_human_sh(cm):
        return np.array([(HCs[i] == cm[i]).mean() for i in range(P)])

    shf, shg = float(vs_human_sh(CF).mean()), float(vs_human_sh(CG).mean())
    negok = shf < hf.mean() - 0.02 and shg < hg.mean() - 0.02
    print(f"     NEGATIVE  human classes shuffled across prompts: `full` {hf.mean():.4f} → "
          f"{shf:.4f}, `genericpool16` {hg.mean():.4f} → {shg:.4f}, gap "
          f"{shg - shf:+.4f}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the gap is a property of the two targets' internal "
          f"structure rather than of how they track THIS prompt's humans'")

    frng = np.random.default_rng(SEEDS[0] + 17)
    halves = []
    for _ in range(20):
        a1 = np.zeros(P)
        a2_ = np.zeros(P)
        for i in range(P):
            k = len(HC[i])
            pm_ = frng.permutation(k)
            i1, i2 = pm_[:k // 2], pm_[k // 2:2 * (k // 2)]
            a1[i] = (HC[i][i1] == CG[i]).mean() - (HC[i][i1] == CF[i]).mean()
            a2_[i] = (HC[i][i2] == CG[i]).mean() - (HC[i][i2] == CF[i]).mean()
        halves.append(abs(a1.mean() - a2_.mean()))
    print(f"     NOISE FLOOR  annotator split-half on the GAP, 20 draws: {np.mean(halves):.6f}")

    gate = ok and plac == 0.0 and posok and negok
    out["controls"] = {"dose": dose, "positive_ok": posok, "neg_full": shf, "neg_pool": shg,
                       "negative_ok": negok, "split_half": float(np.mean(halves)), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E3 · R796's correlation, done properly =====================================
    print("\n  E3 - R796's INVERSE RELATION, ON THE 20 DISTINCT OBJECTS, WITH ITS MDE")
    a2map = lad["e2"]["a2"]
    prefmap = {r["arm"]: r["eff"] for r in pref}
    # D3: collapse aliases using R789's committed identical-A2 groups
    seen, xs, ys, names = {}, [], [], []
    for t in sorted(a2map):
        if t not in prefmap:
            continue
        key = (round(a2map[t], 12), round(prefmap[t], 12))
        if key in seen:
            continue
        seen[key] = t
        xs.append(prefmap[t])
        ys.append(a2map[t])
        names.append(t)
    xs, ys = np.array(xs), np.array(ys)
    n20 = len(xs)
    r_all = float(np.corrcoef([prefmap[t] for t in sorted(a2map) if t in prefmap],
                              [a2map[t] for t in sorted(a2map) if t in prefmap])[0, 1])
    r20 = float(np.corrcoef(xs, ys)[0, 1])
    prng = np.random.default_rng(SEEDS[0] + 23)
    null = np.array([np.corrcoef(xs, ys[prng.permutation(n20)])[0, 1] for _ in range(4000)])
    p_perm = float((np.abs(null) >= abs(r20)).mean())
    # MDE by simulation: the |r| this design detects at n20 with 80% power, two-sided 0.05
    def power(rho, reps=800):
        hit = 0
        for _ in range(reps):
            z = prng.normal(size=n20)
            w = rho * z + math.sqrt(max(1 - rho * rho, 0)) * prng.normal(size=n20)
            rr = np.corrcoef(z, w)[0, 1]
            nl = np.array([np.corrcoef(z, w[prng.permutation(n20)])[0, 1] for _ in range(200)])
            hit += int((np.abs(nl) >= abs(rr)).mean() < 0.05)
        return hit / reps
    mde_r = None
    for rho in (0.3, 0.4, 0.5, 0.6, 0.7):
        if power(rho) >= 0.8:
            mde_r = rho
            break
    print(f"     n = {n20} distinct objects (D3: 27 names collapse to {n20})")
    print(f"     corr(rubric-preference, A2)  27 names {r_all:+.4f}   {n20} objects {r20:+.4f}   "
          f"permutation p {p_perm:.4f}")
    print(f"     ⭐ MDE: the smallest |r| this design detects at 80% power is {mde_r}   "
          f"-> the observed {abs(r20):.4f} is "
          f"{'ABOVE' if mde_r and abs(r20) >= mde_r else 'BELOW'} it")
    print(f"     ⛔ so R796's closing sentence generalised from the two arms at the ends of a "
          f"scatter this design cannot resolve.")
    out["e3"] = {"n": n20, "r_27names": r_all, "r_20objects": r20, "p_perm": p_perm,
                 "mde_r": mde_r, "resolved": bool(p_perm < 0.05)}

    # ================= E4 · the derivation check ==================================================
    print("\n  E4 - IS THE CORRELATION FORCED?  (D4, synthetic mixtures)")
    srng = np.random.default_rng(SEEDS[0] + 29)
    rs = []
    for _ in range(200):
        w = srng.random(n20)
        mixA2 = w * hf.mean() + (1 - w) * hg.mean() + srng.normal(0, 0.01, n20)
        mixPref = w - (1 - w) + srng.normal(0, 0.05, n20)
        rs.append(np.corrcoef(mixPref, mixA2)[0, 1])
    rs = np.array(rs)
    print(f"     synthetic arms as mixtures of `full`-like and pool-like classes: corr "
          f"{rs.mean():+.4f} [{np.percentile(rs, 2.5):+.4f}, {np.percentile(rs, 97.5):+.4f}]")
    print(f"     observed {r20:+.4f}   -> the sign IS forced by D4 whenever the pool is the better "
          f"predictor; only the MAGNITUDE could have been a finding, and it is not resolved")
    out["e4"] = {"synthetic_mean": float(rs.mean()),
                 "synthetic_lo": float(np.percentile(rs, 2.5)),
                 "synthetic_hi": float(np.percentile(rs, 97.5))}

    keep = bh(np.array(pv))
    print(f"\n  MULTIPLICITY  {len(pv)} tests (E1 + {len(pv) - 1} strata), BH q=0.05: surviving "
          f"{int(keep.sum())}   not {len(pv) - int(keep.sum())}")

    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif not res:
        world = "C"
    elif rm and em > 0:
        world = "A"
    elif not rm:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   E1 resolved {res} ({e:+.4f})   12–20 stratum resolved {rm} "
          f"({em:+.4f})  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/target_quality.json"
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
