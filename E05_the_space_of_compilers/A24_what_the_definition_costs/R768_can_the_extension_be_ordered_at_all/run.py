#!/usr/bin/env python3
"""R768 · can the extension be ORDERED at all, or is it a set the definition cannot rank?

⛔ CHECK #370 KILLED R767's NEXT FROM MY OWN COMMITTED ARTIFACT, IN ONE ARITHMETIC STEP:
      k = 4  eff 0.013745      k = 6  eff 0.013681      difference -0.000063
   **On the effect itself the curve peaks at k = 4.** `eff/MDE` orders by `eff/sd` because
   `MDE = z*sd/sqrt(n)`; implied sds are 0.1208 (k=4) and 0.1159 (k=6). "k=6 outscores k=4" is a
   statement about the DENOMINATOR, written while both effects were printed side by side in my own
   table. SIXTH NEXT line this arc killed by the first check of the round that acted on it.

WHAT IS OPEN IS BIGGER THAN THE PAIR: `eff/MDE` is right for ADMISSION and wrong for ORDERING, and
nothing in this campaign has asked whether the extension's members can be ordered — every comparison
so far in this round's lineage is an arm against the BASELINE.

⛔ FORCED, LABELLED:
  D1 eff/MDE ranks by eff/sd — it rewards LOW VARIANCE, not high effect. Algebra.
  D2 var(a-b) = var(a)+var(b)-2cov(a,b), and both arms are scored on the same prompts, so the paired
     sd is SMALL and the pairwise verdicts cannot be predicted from the marginal MDEs in EITHER
     direction. The round must measure them.
  D3 the matrix is antisymmetric — 31 pairs, not 62; reporting both halves would double-count in BH.

CONTROLS  POSITIVE (`coval_core` vs `gen_sham`, a ~0.07 gap, must be BEATS; band from both degenerate
          ends) · g=0 (an arm vs ITSELF, eff exactly 0) · NEGATIVE (pairing destroyed, 200 draws →
          the MDE inflation ratio) · SHAM (the per-arm sd REMOVED from the ranking — re-rank with the
          POOLED sd) · PLACEBO (`topw_k4` vs `_detA`, identical artifacts) · CONFOUND (criterion-set
          overlap beside every verdict, and its correlation with |eff|/MDE).
UNIT      instrument = a PROMPT-PAIRED DIFFERENCE over 968 · claim = an ORDERED PAIR of arms.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402
from report import verdict, POS                        # noqa: E402

RES = ROOT / "corebench/results"
NBOOT, ZEFF, L = 1200, 1.959964 + 0.841621, "ABCD"
PR = list(itertools.combinations(range(4), 2))
COMMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
KFAM = [f"topw_k{k}" for k in (1, 2, 3, 4, 6, 8, 12)]


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    Hm = max(len(h) for h in HC)
    HP = np.zeros((P, Hm, 6)); HK = np.zeros((P, Hm))
    for a, h in enumerate(HC):
        HP[a, :len(h)] = h; HK[a, :len(h)] = 1.0
    nH = HK.sum(1)
    T = np.zeros((P, len(idxs), 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)

    def a2(Y):
        s = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        return ((s[:, None, :] == HP).mean(2) * HK).sum(1) / nH

    def arm(t):
        f = RES / f"sat_{t}.npz"
        if not f.is_file(): return None
        S = load_sat(f); Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            if p not in S: return None
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        return a2(Y)

    ib = np.random.default_rng(31337).integers(0, P, (NBOOT, P))

    def pair(x, y):
        d = x - y
        bs = d[ib].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        sd = float(d.std(ddof=1)); mde = ZEFF * sd / math.sqrt(P)
        p2 = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        return {"eff": float(d.mean()), "lo": lo, "hi": hi, "sd": sd, "mde": mde,
                "p_boot": float(max(p2, 1.0 / (NBOOT + 1))),
                "verdict": verdict(float(d.mean()), lo, hi, mde)}

    arms = sorted(set(COMMITTED) | set(KFAM) | {"gen_sham", "topw_k4_detA"})
    A = {t: arm(t) for t in arms}
    A = {t: v for t, v in A.items() if v is not None}
    bv = a2(T[:, list(range(4)), :].sum(axis=1))
    print(f"  prompts {P}   arms loaded {len(A)}")

    # ---- CONTROLS ------------------------------------------------------------------------------
    pos = pair(A["coval_core"], A["gen_sham"])
    print(f"\n  POSITIVE    coval_core vs gen_sham: eff {pos['eff']:+.4f} "
          f"[{pos['lo']:+.4f}, {pos['hi']:+.4f}] MDE {pos['mde']:.4f} -> {pos['verdict']}  "
          f"{'PASS' if pos['verdict'] == POS else '⛔ FAIL'}")
    print(f"              band: a BEATS-everything instrument also fires on g=0 and PLACEBO below; "
          f"a BEATS-nothing one fails here. Unreachable from either end.")
    g0 = pair(A["coval_core"], A["coval_core"])
    print(f"  g=0         coval_core vs ITSELF: eff {g0['eff']:.6f} -> {g0['verdict']}  "
          f"{'PASS' if g0['eff'] == 0.0 and g0['verdict'] != POS else '⛔ FAIL'}")
    plc = pair(A["topw_k4"], A["topw_k4_detA"])
    print(f"  PLACEBO     topw_k4 vs _detA: eff {plc['eff']:.6f} -> {plc['verdict']}  "
          f"{'PASS' if plc['eff'] == 0.0 else '⛔ FAIL'}")
    rng = np.random.default_rng(768)
    real = pair(A["coval_core"], A["topw_k4"])
    infl = [pair(A["coval_core"], A["topw_k4"][rng.permutation(P)])["mde"] / real["mde"]
            for _ in range(200)]
    print(f"  NEGATIVE    pairing destroyed x200: MDE inflates x{np.mean(infl):.2f} "
          f"[{np.percentile(infl,2.5):.2f}, {np.percentile(infl,97.5):.2f}]  -> D2's mechanism holds"
          if np.mean(infl) > 1 else "  NEGATIVE    pairing did not inflate the MDE")

    # ---- criterion-set overlap, the registered confound -----------------------------------------
    cores = {}
    for t in A:
        f = RES / f"core_{t}.json"
        if f.is_file():
            try: cores[t] = json.loads(f.read_text())
            except Exception: pass

    def overlap(x, y):
        if x not in cores or y not in cores: return None
        ps = sorted(set(cores[x]) & set(cores[y]) & set(pids))
        if not ps: return None
        return float(np.mean([len(set(cores[x][p]) & set(cores[y][p])) /
                              max(1, len(set(cores[x][p]) | set(cores[y][p]))) for p in ps]))

    # ---- E1/E2 · the pairwise matrices -----------------------------------------------------------
    rows = []
    for fam, members in (("committed", COMMITTED), ("k-family", KFAM)):
        for x, y in itertools.combinations([m for m in members if m in A], 2):
            r = pair(A[x], A[y]); r.update({"family": fam, "a": x, "b": y,
                                            "overlap": overlap(x, y)})
            rows.append(r)
    # D3: antisymmetric, so each unordered pair appears once
    print(f"\n  ⭐ E1/E2 · THE PAIRWISE MATRIX — {len(rows)} unordered pairs (D3: not 2x that)")
    print(f"  {'family':<11}{'a':<12}{'b':<12}{'eff':>10}{'lo':>10}{'hi':>10}{'MDE':>9}"
          f"{'ovl':>7}   verdict")
    for r in sorted(rows, key=lambda z: -abs(z["eff"])):
        o = f"{r['overlap']:.2f}" if r["overlap"] is not None else "  —"
        print(f"  {r['family']:<11}{r['a']:<12}{r['b']:<12}{r['eff']:>10.4f}{r['lo']:>10.4f}"
              f"{r['hi']:>10.4f}{r['mde']:>9.4f}{o:>7}   {r['verdict']}")

    # ---- E3 · multiplicity over the WHOLE grid ---------------------------------------------------
    ps = sorted(rows, key=lambda z: z["p_boot"])
    C, q = len(ps), 0.05
    surv = []
    for i, r in enumerate(ps, 1):
        r["bh_thresh"] = q * i / C
        if r["p_boot"] <= r["bh_thresh"]: surv = ps[:i]
    print(f"\n  ⭐ E3 · MULTIPLICITY — BH q=0.05 over the whole grid of {C} pairs")
    print(f"  (BH's threshold at rank k is q*k/C, largest = q; q/C is Bonferroni and is not used)")
    print(f"  cells tested {C}   surviving {len(surv)}")
    for r in ps[:8]:
        mark = "SURVIVES" if r in surv else "no"
        print(f"    {r['a']:<12}{r['b']:<12} p {r['p_boot']:.4f}  BH {r['bh_thresh']:.4f}  "
              f"{r['verdict']:<18} {mark}")
    print(f"    ... {max(0, C-8)} more non-survivors in the artifact")
    comm_res = [r for r in rows if r["family"] == "committed" and r["verdict"] == POS]
    comm_surv = [r for r in surv if r["family"] == "committed"]
    print(f"  committed pairs resolvable by verdict: {len(comm_res)} of 10   "
          f"surviving BH: {len(comm_surv)}")

    # ---- CONFOUND · does resolution track overlap? -----------------------------------------------
    ov = [(r["overlap"], abs(r["eff"]) / r["mde"]) for r in rows if r["overlap"] is not None]
    if len(ov) >= 3:
        a_, b_ = np.array([o for o, _ in ov]), np.array([t for _, t in ov])
        cc = float(np.corrcoef(a_, b_)[0, 1])
        print(f"\n  ⚠ CONFOUND  corr(criterion overlap, |eff|/MDE) over {len(ov)} pairs = {cc:+.4f}")
    else:
        cc = float("nan")
        print(f"\n  ⚠ CONFOUND  too few pairs with core JSONs to correlate: {len(ov)}")

    # ---- E4 + SHAM · the ordering decomposition ---------------------------------------------------
    kA = [t for t in KFAM if t in A]
    eff_vs_base = {t: pair(A[t], bv) for t in kA}
    pooled = float(np.mean([eff_vs_base[t]["sd"] for t in kA]))
    o_eff = sorted(kA, key=lambda t: -eff_vs_base[t]["eff"])
    o_emd = sorted(kA, key=lambda t: -(eff_vs_base[t]["eff"] / eff_vs_base[t]["mde"]))
    o_pool = sorted(kA, key=lambda t: -(eff_vs_base[t]["eff"] / (ZEFF * pooled / math.sqrt(P))))

    def transpositions(x, y):
        iy = {t: i for i, t in enumerate(y)}
        return sum(1 for i in range(len(x)) for j in range(i + 1, len(x))
                   if iy[x[i]] > iy[x[j]])
    print(f"\n  ⭐ E4 + SHAM · the ranking, with and without the per-arm sd")
    print(f"  by eff        : {[t.replace('topw_','') for t in o_eff]}")
    print(f"  by eff/MDE    : {[t.replace('topw_','') for t in o_emd]}")
    print(f"  by eff/POOLED : {[t.replace('topw_','') for t in o_pool]}   (SHAM: sd removed)")
    t_em = transpositions(o_eff, o_emd); t_sh = transpositions(o_eff, o_pool)
    print(f"  transpositions vs the eff order:  eff/MDE {t_em}   pooled {t_sh}   -> the per-arm sd "
          f"moves {t_em - t_sh} inversion(s)")

    # ⛔ THE FIRST BRANCH FIRED OFF BH SURVIVAL ALONE AND PRINTED "ordered in part" WHILE THE VERDICT
    # COLUMN READ 0 OF 10. BH tests "is the difference non-zero"; the verdict tests "is it RESOLVABLE",
    # i.e. it additionally requires |eff| >= MDE. R767 established that this floor is exactly what
    # separates a 4-member extension from a 5-member one, so a branch that ignores it here would
    # contradict this round's own lineage. §4: the branch must reference every control the round
    # declared. Both counts are printed; the verdict decides.
    print(f"\n  ⚠ TWO COUNTS, TWO QUESTIONS, stated before the verdict:")
    print(f"     resolvable BY VERDICT (|eff| >= MDE and CI excludes 0): {len(comm_res)} of 10")
    print(f"     surviving BH on the bootstrap p (no MDE floor)        : {len(comm_surv)} of 10")
    print(f"     the gap is the MDE floor — the same floor R767 showed decides 4 vs 5 members")
    ctrl = pos["verdict"] == POS and g0["eff"] == 0.0 and g0["verdict"] != POS and plc["eff"] == 0.0
    if not ctrl:
        world = "UNVERIFIED"
    elif cc == cc and cc > 0.7:
        world = "C · resolution tracks criterion overlap, not quality"
    elif not comm_res:
        world = ("A · the extension is an UNORDERED SET — 0 of 10 committed pairs are resolvably "
                 f"ordered; {len(comm_surv)} would be if the MDE floor were dropped")
    else:
        world = f"B · ordered in part — {len(comm_res)} committed pair(s) resolvable by verdict"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/pairwise_ordering.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "n_pairs": C, "n_surviving_bh": len(surv),
        "committed_resolvable_by_verdict": len(comm_res),
        "committed_surviving_bh": [f"{r['a']} vs {r['b']}" for r in comm_surv],
        "committed_resolvable_pairs": [f"{r['a']} vs {r['b']}" for r in comm_res],
        "pairs": rows,
        "controls": {"positive": pos, "g0": g0, "placebo": plc,
                     "negative_mde_inflation_mean": float(np.mean(infl))},
        "confound_corr_overlap_vs_resolution": cc,
        "order_by_eff": o_eff, "order_by_eff_mde": o_emd, "order_by_pooled": o_pool,
        "transpositions_eff_vs_effmde": t_em, "transpositions_eff_vs_pooled": t_sh,
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
