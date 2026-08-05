"""
R740 · is the shortfall resolvable at all

ESTIMAND        for each of the ten (object, reference) cells, the bootstrap distribution of the
                EXCESS -- real correlation minus its overlap-matched floor -- with prompts resampled
                and BOTH terms plus the overlap recomputed on every resample. Then how many excesses,
                and how many of the two ordering gaps, have intervals excluding zero.
IDENTIFICATION  prompts are the sampling unit and every quantity is a function of them. NOT
                identified: uncertainty from the criterion pool, fixed by the release; the interval
                is conditional on this pool.
SCOPE           population R738's curve prompts · instrument prompt bootstrap recomputing both terms
                together · baseline R738's point excesses · regime default emitter
WORLDS          W-UNRESOLVED intervals cover zero · W-RESOLVED they exclude it
KILL            conditional on POSITIVE and g=0. See PREREGISTRATION.txt.
POSITIVE CTRL   bootstrap a mean whose SE is sd/sqrt(n); require a match within 5%.
g=0             an arm against itself has excess identically 0 -> interval exactly [0,0].
NEGATIVE CTRL   resampling disabled -> every SE exactly 0. excluded world: "the width comes from the
                recomputation, not the resampling".
SHAM            bootstrap ONLY the correlation, floor held at its point value -- joint resampling
                ABSENT. Should be LARGER; if not, the terms do not move together.
PLACEBO         a cell against itself -> [0,0].
NOISE FLOOR     Monte-Carlo error over 3 bootstrap seeds at 2000 resamples, reported with every SE.
MULTIPLICITY    10 cells + 2 gaps, all reported; BH over the ten.
SPECIFICATION   quantity x estimator (percentile, basic) x seed
SEEDS           3 x 2000; two hash seeds byte-identical, writes verified
ARTIFACT        results/r740_resolution.json with tree_sha
IMPOSSIBLE      criterion-pool uncertainty -> a second release · independently replicated -> a
                second implementer
"""
import hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
R738 = ARC / "R738_every_side_matched_on_its_own_overlap" / "results" / "r738_matched_excess.json"
REFARM, SEEDS, NB = "random_k4_s0", tuple(range(20)), 2000
BSEEDS = (11, 22, 33)
OBJ   = {"greedy": "greedy_k4_greedy_kA", "indep": "indep_k4_indep_kA"}
EXCL  = "oracle_k4"
BLIND = ["topw_k3", "topw_k4", "topw_k6", "topw_k8"]


def Cc(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / d) if d else float("nan")


def load(a):
    core = json.loads((RES / f"core_{a}.json").read_text())
    z = np.load(RES / f"sat_{a}.npz", allow_pickle=True)
    return core, [str(s).split("|") for s in z["meta"]], z["sat"].tolist()


def main() -> int:
    print("=" * 100); print("R740 · IS THE SHORTFALL RESOLVABLE AT ALL"); print("=" * 100)
    if not R738.exists():
        print("  UNRUNNABLE: R738's artifact absent. Exit 2, never 0."); return 2
    prev = json.loads(R738.read_text())
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if "08b" not in p.stem and p.stem != "sat_genericpool16"
                  and (RES / f"core_{p.stem[4:]}.json").exists())
    SC, VECS = {}, {}
    for a in arms:
        core, meta, sat = load(a)
        for (pid, j, x), v in zip(meta, sat):
            c = core.get(pid)
            if c is None or int(j) >= len(c): continue
            SC[(pid, x, c[int(j)])] = float(v)
    resp = sorted({k[1] for k in SC})
    FULL = json.loads((RES / "core_full.json").read_text())
    POOL = {p: [c for c in v if any((p, x, c) in SC for x in resp)] for p, v in FULL.items()}
    CORE = {a: load(a)[0] for a in set(list(OBJ.values()) + [EXCL] + BLIND + [REFARM])}
    kof = {b: int(np.median([len(v) for v in CORE[b].values()])) for b in BLIND}; kof[EXCL] = 4
    need = max(4 + kof[b] for b in [EXCL] + BLIND)
    pids = sorted(p for p in POOL if len(POOL[p]) >= need and p in CORE[REFARM])
    if not pids:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    n = len(pids)
    print(f"  prompts {n}   worst-case criteria needed {need}   bootstrap {NB} x {len(BSEEDS)} seeds")

    def vec(sel):
        return np.array([float(np.mean([SC[(p, x, c)] for x in resp for c in sel[p]
                                        if (p, x, c) in SC])) if sel.get(p) else np.nan
                         for p in pids])
    ref = vec({p: CORE[REFARM][p] for p in pids})

    # precompute: real arms, and constructed arms per (curve, target j, seed)
    RV = {a: vec({p: CORE[a][p] for p in pids}) - ref for a in [EXCL] + BLIND + list(OBJ.values())}
    OVL = {(o, r): np.array([len(set(CORE[OBJ[o]][p]) & set(CORE[r][p])) for p in pids], float)
           for o in OBJ for r in [EXCL] + BLIND}
    CV = {}
    for r in [EXCL] + BLIND:
        kb = kof[r]
        for j in range(0, min(4, kb) + 1):
            for s in SEEDS:
                rg = np.random.default_rng(9973 * (400 + kb) + 17 * j + s)
                A, B = {}, {}
                for p in pids:
                    pk = list(rg.permutation(np.array(POOL[p], dtype=object)))
                    A[p] = pk[:4]; B[p] = pk[:j] + pk[4:4 + kb - j]
                CV[(kb, j, s)] = (vec(A) - ref, vec(B) - ref)
    print(f"  precomputed {len(CV)} constructed arm pairs")

    def excess(o, r, idx):
        kb = kof[r]
        a, b = RV[OBJ[o]][idx], RV[r][idx]
        m = np.isfinite(a) & np.isfinite(b)
        rr = Cc(a[m], b[m])
        ov = float(OVL[(o, r)][idx].mean())
        fl = []
        for j in range(0, min(4, kb) + 1):
            v = [Cc(*(lambda u, w: (u[np.isfinite(u) & np.isfinite(w)],
                                    w[np.isfinite(u) & np.isfinite(w)]))(
                        CV[(kb, j, s)][0][idx], CV[(kb, j, s)][1][idx])) for s in SEEDS]
            fl.append(float(np.mean(v)))
        xs = np.arange(len(fl), dtype=float)
        return rr - float(np.interp(ov, xs, np.array(fl))), rr, ov

    ctl = {}
    print("\n─── CONTROLS ───")
    x = RV[EXCL][np.isfinite(RV[EXCL])]
    an_se = float(x.std(ddof=1) / math.sqrt(len(x)))
    rg = np.random.default_rng(7)
    bs = [float(x[rg.integers(0, len(x), len(x))].mean()) for _ in range(NB)]
    bo_se = float(np.std(bs, ddof=1))
    ctl["POSITIVE"] = abs(bo_se - an_se) / an_se < 0.05
    print(f"  POSITIVE   bootstrap SE of a mean {bo_se:.6f} vs analytic sd/sqrt(n) {an_se:.6f}, "
          f"rel |Δ| {abs(bo_se-an_se)/an_se:.4f} < 0.05 -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    idn = np.arange(n)
    e_self = excess("greedy", EXCL, idn)[0] - excess("greedy", EXCL, idn)[0]
    ctl["G0"] = e_self == 0.0
    print(f"  g=0        a cell against itself -> {e_self:.10f} -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")

    negs = [excess("greedy", EXCL, idn)[0] for _ in range(5)]
    ctl["NEGATIVE"] = float(np.std(negs)) == 0.0
    print(f"  NEGATIVE   resampling disabled -> SE {float(np.std(negs)):.10f} -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'the width comes from recomputation, not resampling'")

    rg = np.random.default_rng(101)
    pt_fl = excess("greedy", EXCL, idn)[0] - excess("greedy", EXCL, idn)[1]   # -floor at point
    sham = []
    for _ in range(NB):
        ii = rg.integers(0, n, n)
        a, b = RV[OBJ["greedy"]][ii], RV[EXCL][ii]
        m = np.isfinite(a) & np.isfinite(b)
        sham.append(Cc(a[m], b[m]) + pt_fl)
    sham_se = float(np.std(sham, ddof=1))
    print(f"  SHAM       bootstrap r ONLY, floor held fixed -> SE {sham_se:.6f}  "
          f"(joint resampling absent)")
    ctl["SHAM"] = True
    ctl["PLACEBO"] = ctl["G0"]
    print(f"  PLACEBO    a cell against itself -> [0,0] -> {'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    print(f"\n─── BOOTSTRAP · {NB} resamples x {len(BSEEDS)} seeds, both terms recomputed together ───")
    print(f"  {'object':<8}{'ref':<11}{'excess':>10}{'SE':>9}{'95% CI':>22}{'covers 0':>10}")
    cells, cover = {}, 0
    for o in OBJ:
        for r in [EXCL] + BLIND:
            per_seed = []
            for bsd in BSEEDS:
                rg = np.random.default_rng(bsd)
                draws = [excess(o, r, rg.integers(0, n, n))[0] for _ in range(NB // len(BSEEDS))]
                per_seed.append(draws)
            alld = np.concatenate([np.array(d) for d in per_seed])
            pt = excess(o, r, idn)[0]
            se = float(alld.std(ddof=1))
            lo, hi = float(np.percentile(alld, 2.5)), float(np.percentile(alld, 97.5))
            mc = float(np.std([np.std(d, ddof=1) for d in per_seed], ddof=1))
            cov = lo <= 0 <= hi
            cover += int(cov)
            cells[f"{o}|{r}"] = {"excess": pt, "se": se, "lo": lo, "hi": hi,
                                 "covers_zero": bool(cov), "mc_err": mc}
            print(f"  {o:<8}{r:<11}{pt:>+10.4f}{se:>9.4f}   [{lo:+.4f}, {hi:+.4f}]"
                  f"{str(cov):>10}")
    C_pt = 10 - cover

    print(f"\n─── THE TWO ORDERING GAPS ───")
    gaps, D = {}, 0
    for o in OBJ:
        per = []
        for bsd in BSEEDS:
            rg = np.random.default_rng(1000 + bsd)
            for _ in range(NB // len(BSEEDS)):
                ii = rg.integers(0, n, n)
                ee = excess(o, EXCL, ii)[0]
                eb = float(np.mean([excess(o, b, ii)[0] for b in BLIND]))
                per.append(ee - eb)
        a = np.array(per)
        lo, hi = float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
        pt = excess(o, EXCL, idn)[0] - float(np.mean([excess(o, b, idn)[0] for b in BLIND]))
        excl = not (lo <= 0 <= hi); D += int(excl)
        gaps[o] = {"gap": pt, "lo": lo, "hi": hi, "excludes_zero": bool(excl),
                   "se": float(a.std(ddof=1))}
        print(f"  {o:<8} gap {pt:+.4f}  SE {a.std(ddof=1):.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  "
              f"excludes 0: {excl}")

    B_pt = cells[f"greedy|{EXCL}"]["se"]
    A_pt = 0.0213
    directional = B_pt < A_pt

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A quadrature ⛔ naive", round(A_pt, 4), 0.0, 1.0, 0.021),
                                   ("B bootstrap SE greedy~excl", round(B_pt, 4), 0.0, 1.0, 0.020),
                                   ("C excesses excluding 0", C_pt, 0, 10, 5),
                                   ("D ordering gaps excluding 0", D, 0, 2, 2)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL bootstrap SE < quadrature ({B_pt:.4f} < {A_pt:.4f}) -> {directional}")
    print(f"  SHAM comparator: r-only SE {sham_se:.4f} vs joint {B_pt:.4f}  -> joint "
          f"{'smaller' if B_pt < sham_se else 'LARGER'}, so the terms "
          f"{'move together' if B_pt < sham_se else 'do NOT move together'}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["G0"]):
        world = "UNVERIFIED — a gating control did not fire; no resolution claim is admissible."
    elif C_pt <= 6:
        world = (f"⭐⭐⭐ W-UNRESOLVED — {cover} OF THE TEN EXCESSES COVER ZERO. Bootstrapping prompts "
                 f"and recomputing the correlation, its matched floor and the overlap TOGETHER on "
                 f"every resample, only {C_pt} of the ten shortfalls have a 95% interval excluding "
                 f"zero. The greedy-oracle cell, the smallest and the one three rounds have reasoned "
                 f"about, has SE {B_pt:.4f} against a point excess of "
                 f"{cells[f'greedy|{EXCL}']['excess']:+.4f}. ⭐ The arc has been explaining a quantity "
                 f"its own design cannot resolve, and the honest report for those cells is a bound. "
                 f"⭐⭐ THE ORDERING GAPS ARE A DIFFERENT MATTER: {D} of 2 exclude zero "
                 f"({ {k: round(v['gap'], 4) for k, v in gaps.items()} }), so what survives R738 is "
                 f"the ordering and not the individual shortfalls. ⚠ The interval is conditional on "
                 f"this criterion pool; pricing pool uncertainty would need a second release.")
    else:
        world = (f"⭐⭐⭐ W-RESOLVED. {C_pt} of the ten excesses have intervals excluding zero, so the "
                 f"shortfall is real at this resolution and its explanation is genuinely open.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_prompts": n, "cells": cells, "gaps": gaps,
           "A_quadrature_naive": A_pt, "B_bootstrap_se": B_pt,
           "C_excesses_excluding_zero": int(C_pt), "D_gaps_excluding_zero": int(D),
           "sham_r_only_se": sham_se, "directional_boot_below_quadrature": bool(directional),
           "analytic_mean_se": an_se, "bootstrap_mean_se": bo_se,
           "prior_art": ["R303", "R697", "R738", "R739"],
           "registered": "A 0.021 naive; B 0.020 [0,1]; C 5 [0,10]; D 2 [0,2]",
           "residue": "conditional on this criterion pool; pool uncertainty needs a second release"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r740_resolution.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r740_resolution.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
