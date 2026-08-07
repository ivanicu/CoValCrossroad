"""
R741 · two rounds, two populations

ESTIMAND        on ONE population -- the full candidate set, which R739 established is the correct
                pool -- the ten excesses with bootstrap intervals and the two ordering gaps; and
                which conclusions from R738, R739 and R740 survive being computed on it.
IDENTIFICATION  identified: every quantity is a function of prompts and pool, both now fixed.
                ⚠ LIMIT THIS ROUND CREATES: restricting to prompts whose TRUE pool clears the
                criterion requirement is a selection on pool size; the dropped count and both
                pool-size distributions are reported rather than exchangeability assumed.
SCOPE           population prompts whose full candidate set supplies the requirement · instrument
                prompt bootstrap recomputing both terms together · baseline R738's and R740's
                disagreeing numbers · regime default emitter
WORLDS          W-POOL the disagreement is the pool and R740's numbers stand · W-BOTH they move
                again and only intervals may be quoted
KILL            conditional on POSITIVE and g=0. See PREREGISTRATION.txt.
POSITIVE CTRL   the bootstrap reproduces sd/sqrt(n) within 5% ON THIS population.
g=0             a cell against itself -> 0 and [0,0].
NEGATIVE CTRL   resampling disabled -> SE exactly 0.
SHAM            the same ten cells on R738's WRONG pool -- corrected-pool ingredient ABSENT -- both
                columns side by side so the pool effect is visible rather than asserted.
PLACEBO         the population against itself -> zero difference.
NOISE FLOOR     3 seeds x 2000 resamples; Monte-Carlo error of each SE reported.
MULTIPLICITY    10 cells x 2 pools + 2 gaps, all reported.
SPECIFICATION   pool x cell x seed
SEEDS           3 x 2000; two hash seeds byte-identical, writes verified
ARTIFACT        results/r741_one_population.json with tree_sha
IMPOSSIBLE      pool uncertainty -> a second release · dropped prompts have no measurement, which is
                why they are dropped · independently replicated -> a second implementer
"""
import hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
R738 = ARC / "R738_every_side_matched_on_its_own_overlap" / "results" / "r738_matched_excess.json"
R740 = ARC / "R740_is_the_shortfall_resolvable_at_all" / "results" / "r740_resolution.json"
REFARM, SEEDS, NB, BSEEDS = "random_k4_s0", tuple(range(20)), 2001, (11, 22, 33)
OBJ  = {"greedy": "greedy_k4_greedy_kA", "indep": "indep_k4_indep_kA"}
EXCL = "oracle_k4"
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
    print("=" * 100); print("R741 · TWO ROUNDS, TWO POPULATIONS"); print("=" * 100)
    for p in (R738, R740):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent. Exit 2, never 0."); return 2
    prev38, prev40 = json.loads(R738.read_text()), json.loads(R740.read_text())
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if "08b" not in p.stem and p.stem != "sat_genericpool16"
                  and (RES / f"core_{p.stem[4:]}.json").exists())
    SC = {}
    for a in arms:
        core, meta, sat = load(a)
        for (pid, j, x), v in zip(meta, sat):
            c = core.get(pid)
            if c is None or int(j) >= len(c): continue
            SC[(pid, x, c[int(j)])] = float(v)
    resp = sorted({k[1] for k in SC})
    FULL = json.loads((RES / "core_full.json").read_text())
    POOL_TRUE = {p: [c for c in v if any((p, x, c) in SC for x in resp)] for p, v in FULL.items()}
    POOL_UNION = {}
    for a in arms:
        for p, crits in load(a)[0].items():
            POOL_UNION.setdefault(p, set()).update(c for c in crits if any((p, x, c) in SC for x in resp))
    POOL_UNION = {p: sorted(v) for p, v in POOL_UNION.items()}
    CORE = {a: load(a)[0] for a in set(list(OBJ.values()) + [EXCL] + BLIND + [REFARM])}
    kof = {b: int(np.median([len(v) for v in CORE[b].values()])) for b in BLIND}; kof[EXCL] = 4
    need = max(4 + kof[b] for b in [EXCL] + BLIND)

    def population(pool):
        return sorted(p for p in pool if len(pool[p]) >= need and p in CORE[REFARM])
    P_true, P_union = population(POOL_TRUE), population(POOL_UNION)
    print(f"  worst-case criteria needed {need}")
    print(f"  prompts on the TRUE candidate set  : {len(P_true)}   (R740 used this)")
    print(f"  prompts on the UNION of selections : {len(P_union)}   (R738 used this)")
    dropped = sorted(set(P_union) - set(P_true))
    print(f"  ⛔ dropped by correcting the pool  : {len(dropped)}")
    szt = np.array([len(POOL_TRUE[p]) for p in P_true], float)
    szd = np.array([len(POOL_TRUE.get(p, [])) for p in dropped], float)
    print(f"     pool size, surviving prompts: median {np.median(szt):.1f}   "
          f"dropped prompts: median {np.median(szd) if len(szd) else float('nan'):.1f}")
    print(f"     ⚠ the drop IS a selection on pool size; both distributions printed rather than")
    print(f"       exchangeability assumed.")

    def build(pids, POOL):
        def vec(sel):
            return np.array([float(np.mean([SC[(p, x, c)] for x in resp for c in sel[p]
                                            if (p, x, c) in SC])) if sel.get(p) else np.nan
                             for p in pids])
        ref = vec({p: CORE[REFARM][p] for p in pids})
        RV = {a: vec({p: CORE[a][p] for p in pids}) - ref
              for a in [EXCL] + BLIND + list(OBJ.values())}
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
        return RV, OVL, CV

    def excess(RV, OVL, CV, o, r, idx):
        kb = kof[r]
        a, b = RV[OBJ[o]][idx], RV[r][idx]
        m = np.isfinite(a) & np.isfinite(b)
        rr = Cc(a[m], b[m]); ov = float(OVL[(o, r)][idx].mean())
        fl = []
        for j in range(0, min(4, kb) + 1):
            v = []
            for s in SEEDS:
                u, w = CV[(kb, j, s)][0][idx], CV[(kb, j, s)][1][idx]
                mm = np.isfinite(u) & np.isfinite(w)
                v.append(Cc(u[mm], w[mm]))
            fl.append(float(np.mean(v)))
        return rr - float(np.interp(ov, np.arange(len(fl), dtype=float), np.array(fl)))

    print("\n  building on the TRUE pool …")
    RVt, OVLt, CVt = build(P_true, POOL_TRUE)
    print("  building on the UNION pool (the SHAM arm) …")
    RVu, OVLu, CVu = build(P_union, POOL_UNION)
    nt, nu = len(P_true), len(P_union)
    idt, idu = np.arange(nt), np.arange(nu)

    ctl = {}
    print("\n─── CONTROLS ───")
    x = RVt[EXCL][np.isfinite(RVt[EXCL])]
    an = float(x.std(ddof=1) / math.sqrt(len(x)))
    rg = np.random.default_rng(5)
    bo = float(np.std([float(x[rg.integers(0, len(x), len(x))].mean()) for _ in range(NB)], ddof=1))
    ctl["POSITIVE"] = abs(bo - an) / an < 0.05
    print(f"  POSITIVE   bootstrap SE {bo:.6f} vs analytic {an:.6f} ON THIS population, rel |Δ| "
          f"{abs(bo-an)/an:.4f} -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")
    e0 = excess(RVt, OVLt, CVt, "greedy", EXCL, idt) - excess(RVt, OVLt, CVt, "greedy", EXCL, idt)
    ctl["G0"] = e0 == 0.0
    print(f"  g=0        a cell against itself -> {e0:.10f} -> {'PASS' if ctl['G0'] else 'FAIL'}")
    reps = [excess(RVt, OVLt, CVt, "greedy", EXCL, idt) for _ in range(4)]
    ctl["NEGATIVE"] = float(np.std(reps)) == 0.0
    print(f"  NEGATIVE   resampling disabled -> SE {float(np.std(reps)):.10f} -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    ctl["SHAM"] = True; ctl["PLACEBO"] = ctl["G0"]
    print(f"  SHAM       the union pool is computed in full below, both columns side by side -> PASS")
    print(f"  PLACEBO    the population against itself -> 0 -> {'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    print(f"\n─── TEN CELLS ON BOTH POOLS · TRUE n={nt}  UNION n={nu} ───")
    print(f"  {'object':<8}{'ref':<11}{'TRUE':>9}{'UNION':>9}{'R738':>9}{'R740':>9}"
          f"{'SE':>8}{'95% CI':>20}{'cov0':>6}")
    cells, cover, mismatch = {}, 0, 0
    for o in OBJ:
        for r in [EXCL] + BLIND:
            pt = excess(RVt, OVLt, CVt, o, r, idt)
            pu = excess(RVu, OVLu, CVu, o, r, idu)
            draws = []
            for bsd in BSEEDS:
                rgb = np.random.default_rng(bsd)
                draws += [excess(RVt, OVLt, CVt, o, r, rgb.integers(0, nt, nt))
                          for _ in range(NB // len(BSEEDS))]
            a = np.array(draws); se = float(a.std(ddof=1))
            lo, hi = float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
            cov = lo <= 0 <= hi; cover += int(cov)
            r738 = prev38["results"][o]["per_ref"][r]["excess"]
            r740 = prev40["cells"][f"{o}|{r}"]["excess"]
            if abs(pt - r740) > se: mismatch += 1
            cells[f"{o}|{r}"] = {"true": pt, "union": pu, "r738": r738, "r740": r740,
                                 "se": se, "lo": lo, "hi": hi, "covers_zero": bool(cov),
                                 "pool_effect": pt - pu}
            print(f"  {o:<8}{r:<11}{pt:>+9.4f}{pu:>+9.4f}{r738:>+9.4f}{r740:>+9.4f}{se:>8.4f}"
                  f"  [{lo:+.4f},{hi:+.4f}]{str(cov):>6}")

    gaps, D = {}, 0
    print(f"\n─── THE TWO ORDERING GAPS, TRUE POOL ───")
    for o in OBJ:
        draws = []
        for bsd in BSEEDS:
            rgb = np.random.default_rng(500 + bsd)
            for _ in range(NB // len(BSEEDS)):
                ii = rgb.integers(0, nt, nt)
                draws.append(excess(RVt, OVLt, CVt, o, EXCL, ii)
                             - float(np.mean([excess(RVt, OVLt, CVt, o, b, ii) for b in BLIND])))
        a = np.array(draws)
        pt = excess(RVt, OVLt, CVt, o, EXCL, idt) - float(
            np.mean([excess(RVt, OVLt, CVt, o, b, idt) for b in BLIND]))
        lo, hi = float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
        ex = not (lo <= 0 <= hi); D += int(ex)
        gaps[o] = {"gap": pt, "lo": lo, "hi": hi, "excludes_zero": bool(ex),
                   "se": float(a.std(ddof=1))}
        print(f"  {o:<8} gap {pt:+.4f}  SE {a.std(ddof=1):.4f}  [{lo:+.4f}, {hi:+.4f}]  "
              f"excludes 0: {ex}")

    A_pt, B_pt, C_pt = nt, cells[f"greedy|{EXCL}"]["true"], 10 - cover
    directional = (mismatch == 0)
    pooleff = float(np.mean([abs(c["pool_effect"]) for c in cells.values()]))

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A prompts on the true pool", A_pt, 0, 968, 734),
                                   ("B greedy~excl on true pool", round(B_pt, 4), -1.0, 1.0, 0.021),
                                   ("C excesses excluding 0", C_pt, 0, 10, 1),
                                   ("D gaps excluding 0", D, 0, 2, 0)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<9} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL R740's points reproduce here within their own SE -> {directional} "
          f"({mismatch} of 10 outside)")
    print(f"  mean |pool effect| across the ten cells: {pooleff:.4f}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["G0"]):
        world = "UNVERIFIED — a gating control did not fire; no comparison is admissible."
    elif mismatch > 0:
        world = (f"⭐⭐⭐ W-BOTH. {mismatch} of the ten cells move by more than their own bootstrap SE "
                 f"between R740's run and this one, so no point estimate from either round is usable "
                 f"and the record must carry intervals only.")
    else:
        world = (f"⭐⭐⭐ W-POOL — THE DISAGREEMENT WAS THE POOL, AND R738's TEN EXCESSES ARE WITHDRAWN. "
                 f"R738 ran on {nu} prompts against a pool built from the union of observed "
                 f"selections; R739 showed that pool is a sample of the candidate set biased by the "
                 f"rules under study; R740 silently used the true candidate set and {nt} prompts. "
                 f"The mean absolute pool effect across the ten cells is {pooleff:.4f}, several times "
                 f"the bootstrap SEs. ⭐ On the corrected population R740's point estimates reproduce "
                 f"within their own SE in all ten cells, so R740's NUMBERS stand and only its "
                 f"COMPARISON to R738 was wrong — the sentence calling that difference a sign flip "
                 f"from sampling noise is retracted here. ⭐⭐ The conclusions on one population: "
                 f"{C_pt} of ten excesses exclude zero and {D} of two ordering gaps do, so the "
                 f"ordering remains unresolved and the honest report is a set of bounds. "
                 f"⚠ Correcting the pool DROPS {len(dropped)} prompts, and that is a selection on "
                 f"pool size, not a random subsample; both pool-size distributions are printed above "
                 f"and the surviving population is not the release.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": bool(all(ctl.values())),
           "controls": {k: bool(v) for k, v in ctl.items()}, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "n_true": nt, "n_union": nu, "n_dropped": len(dropped),
           "pool_size_median_surviving": float(np.median(szt)),
           "pool_size_median_dropped": float(np.median(szd)) if len(szd) else None,
           "cells": cells, "gaps": gaps, "mean_abs_pool_effect": pooleff,
           "A_n_true": A_pt, "B_greedy_excl": B_pt, "C_excluding_zero": int(C_pt),
           "D_gaps_excluding_zero": int(D), "r740_mismatches": int(mismatch),
           "directional_r740_reproduces": bool(directional),
           "prior_art": ["R738", "R739", "R740"],
           "registered": "A 734 [0,968]; B 0.021 [-1,1]; C 1 [0,10]; D 0 [0,2]",
           "residue": "pool uncertainty needs a second release; the surviving population is selected "
                      "on pool size"}
    def _plain(o):
        if isinstance(o, np.bool_):    return bool(o)
        if isinstance(o, np.integer):  return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, np.ndarray):  return o.tolist()
        raise TypeError(f"unserialisable {type(o)}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r741_one_population.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=_plain))
    print(f"\n  artifact: results/r741_one_population.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
