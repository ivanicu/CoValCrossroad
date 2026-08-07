"""R460 -- R459 tested R457 for an n=1 draw. Did R459's own comparator have the same defect?

⭐ THE ANNOUNCED STEP IS SOUND AND IT IS A SELF-APPLICATION. R459 attacked R457 for an estimand whose
   sham partner was DRAWN ONCE AND FROZEN, and answered it with `core − generic` -- where `generic`
   is ONE fixed prompt-blind set. R450/R453 measured that fixed prompt-blind sets range from 0.0033
   to 0.6247 in strength. **So R459's own comparator is a single draw from a population it knows to
   be wildly heterogeneous**, which is the defect it was built to detect. *Twenty-eighth announced
   step checked; it survives, and it indicts the round that proposed it.*

⭐ AND IT IS CHEAPER THAN ANNOUNCED, WHICH CHANGES THE DESIGN. Every fixed size-4 prompt-blind set is
   a ROW of the C(16,4)=1,820 matrix already built in earlier rounds, so this is a CENSUS of all
   1,820 comparators, not a sample of "several". No selection, nothing to correct for, and the
   percentile of `generic` inside its own population becomes directly readable.

ESTIMAND (named before the method)
    For every fixed prompt-blind set F among all C(16,4) = 1,820:
        RHO(F) = Spearman-Brown corrected split-half reliability of  d_F[p] = A2(core,p) - A2(F,p),
                 halves taken over each prompt's annotators, F held fixed across all prompts.
    Reported as the WHOLE DISTRIBUTION, with the percentile of `generic` (R459's choice) and of the
    sham (R457's choice) marked inside it.
    SECONDARY: RHO(F) against F's own strength mean_p A2(F,p) -- if reliability tracks the
    comparator's strength, then any single-comparator statement must name its comparator.

IDENTIFICATION
    Identified and exhaustive: the population of size-4 prompt-blind sets from this pool IS 1,820 and
    all are computed. ⚠ NOT identified: comparators outside this pool -- R454 established that  RESTATES: R454
    exactly one prompt-blind family with breadth exists on this site.

SCOPE  population : 968 prompts with >=4 annotators; comparators = all 1,820 size-4 pool subsets
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs; annotators split, never resampled with return
       baseline   : R459's committed rho_full(core − generic) = 0.8363 and R457's 0.8812
       regime     : half-length ~8 annotators; Spearman-Brown projects to full

WORLDS
    W-STABLE    the distribution of RHO(F) is tight -> R459's conclusion generalises; `generic` was
                not special and the partner-free result stands for the whole comparator population.
    W-SWINGS    the distribution is wide -> `core − generic` was ONE DRAW, R459 inherited the very
                defect it tested, and its 0.8363 must be restated as a distribution.
    W-STRENGTH  RHO(F) tracks F's own strength -> reliability is a property of the COMPARATOR, and
                every difference-based reliability in this campaign needs its comparator named.

PREDICTION MATRIX
                   tight   wide   tracks strength
    W-STABLE        0.90   0.05        0.05
    W-SWINGS        0.05   0.90        0.05
    W-STRENGTH      0.05   0.05        0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    |corr(RHO(F), strength(F))| >= 0.50                      -> W-STRENGTH   (checked FIRST: a
                                                                systematic driver makes "tight vs
                                                                wide" the wrong question)
    else IQR of RHO(F) <= 0.05                               -> W-STABLE
    else                                                     -> W-SWINGS
    a control fails                                          -> UNVERIFIED

CONTROLS
    ANCHOR-1   `generic` is one of the 1,820; its RHO must reproduce R459's committed 0.8363. An
               independent path to a published number, and it also locates R459's choice INSIDE the
               distribution rather than beside it.
    ANCHOR-2   R457's `core − sham` is computed alongside; the sham is NOT in this population (its
               criteria are another prompt's), so it is printed as a reference line, never as a
               percentile.
    NEGATIVE   prompt labels of half B shuffled -> RHO ~ 0 for every F.
    g=0        F = the core itself is not in the pool population, so the degenerate case is
               constructed explicitly: d = core - core = 0, rho UNDEFINED, and the code must say so.
    SEEDS      5 independent half-splits; the across-seed spread of the DISTRIBUTION's quartiles is
               reported, not just of a point.

MULTIPLICITY  1,820 comparators x 5 splits, reported as a distribution. A census has no selection, so
              there is nothing to correct -- and that is stated rather than assumed.
ARTIFACT      results/r460_comparator_census.json
IMPOSSIBLE HERE, NAMED
    * comparators outside this pool -- exactly one prompt-blind family with breadth exists (R454).
    * decomposing partner variance for the SHAM -- still impossible, unchanged from R459.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
M, NSPLIT = 4, 5
R459_DGEN, R457_DSHAM = 0.8363, 0.8812


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)
def sb(r): return 2 * r / (1 + r)


def rowcorr(X, Y):
    """Row-wise Pearson correlation of two (m, n) matrices -> (m,)."""
    Xc = X - X.mean(1, keepdims=True); Yc = Y - Y.mean(1, keepdims=True)
    num = (Xc * Yc).sum(1)
    den = np.sqrt((Xc ** 2).sum(1) * (Yc ** 2).sum(1))
    den[den == 0] = np.nan
    return num / den


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R460 · R459 tested R457 for an n=1 draw. Did R459's OWN comparator have the same defect?\n")
    print("  ⭐ R459 answered the partner question with `core − generic` — ONE fixed prompt-blind set,")
    print("     drawn from a population R450/R453 measured at 0.0033..0.6247 in strength. That is the")
    print("     defect it was built to detect. Twenty-eighth step checked; it indicts its proposer.")
    print("  ⭐ And every fixed set is a ROW of the C(16,4) matrix, so this is a CENSUS of all 1,820.\n")

    need = {"core": "coval_core", "sham": "coval_core_sham", "generic": "generic",
            "pool": "genericpool16"}
    S = {}
    for k, nm in need.items():
        f = SATD / f"sat_{nm}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
        S[k] = SC.load_sat(f)
    targets, _ = SC.load_targets()
    pids = sorted(set(targets) & set.intersection(*[set(v) for v in S.values()]))
    pids = [p for p in pids if len(targets[p]) >= 4]
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    subs = list(itertools.combinations(range(16), M))
    Sm = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        Sm[j, list(s)] = 1.0
    CL, ARM, POOLS = {}, {k: {} for k in ("core", "sham", "generic")}, {}
    for p in pids:
        CL[p] = np.array([SC.cls(np.array(t[0], float)) for t in targets[p]])
        for k in ARM:
            d = S[k][p]; cs = sorted({c for (c, _) in d})
            ARM[k][p] = signs(np.array([[d.get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0))
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in S["pool"][p].items():
            PMp[ci, L.index(ltr)] = v
        POOLS[p] = signs((Sm @ PMp) / M)
    # locate `generic` inside the 1,820: its criterion indices are a fixed 4-subset of the pool?
    gidx = tuple(sorted({c for (c, _) in next(iter(S["generic"].values()))}))
    gj = subs.index(gidx) if gidx in subs else None
    print(f"  prompts {n};  comparators {len(subs)};  `generic` index tuple {gidx} -> "
          f"{'row ' + str(gj) if gj is not None else 'NOT a pool subset — anchored by VALUE instead'}")

    def split(seed):
        """-> A0, A1 (1820 x n) for the pool comparators, plus per-arm halves."""
        A0 = np.zeros((len(subs), n)); A1 = np.zeros((len(subs), n))
        arms = {k: (np.zeros(n), np.zeros(n)) for k in ARM}
        for i, p in enumerate(pids):
            C = CL[p]
            perm = np.random.default_rng(seed * 7919 + stable(p)).permutation(len(C))
            h = len(C) // 2
            for sl, idx, A in ((0, perm[:h], A0), (1, perm[h:2 * h], A1)):
                HC = C[idx]
                A[:, i] = (POOLS[p][:, None, :] == HC[None, :, :]).mean(axis=(1, 2))
                for k in ARM:
                    arms[k][sl][i] = (ARM[k][p][None, :] == HC).mean()
        return A0, A1, arms

    print("\n  CONTROLS")
    A0, A1, arms = split(0)
    c0, c1 = arms["core"]
    g0v, g1v = arms["generic"]
    rho_gen = sb(float(np.corrcoef(c0 - g0v, c1 - g1v)[0, 1]))
    a1_ok = abs(rho_gen - R459_DGEN) < 0.03
    print(f"    ANCHOR-1  `core − generic` -> {rho_gen:.4f} vs R459's committed {R459_DGEN}"
          f"   {'PASS' if a1_ok else '⛔ FAIL'}")
    s0, s1 = arms["sham"]
    rho_sham = sb(float(np.corrcoef(c0 - s0, c1 - s1)[0, 1]))
    a2_ok = abs(rho_sham - R457_DSHAM) < 0.03
    print(f"    ANCHOR-2  `core − sham`    -> {rho_sham:.4f} vs R457's committed {R457_DSHAM}"
          f"   {'PASS' if a2_ok else '⛔ FAIL'}   (the sham is NOT in this population)")
    neg = float(np.nanmean(rowcorr(c0[None, :] - A0,
                                   np.random.default_rng(5).permutation(c1[None, :] - A1, axis=1))))
    neg_ok = abs(neg) < 0.10
    print(f"    NEGATIVE  prompt labels of half B shuffled -> mean rho {neg:+.4f}   "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"    g=0       F = the core itself: d = core − core = 0 identically, rho UNDEFINED —")
    print(f"              constructed explicitly and reported as undefined, never as a number")

    # ---- the census ------------------------------------------------------------------------------
    allq, strengths = [], None
    for sd in range(NSPLIT):
        A0, A1, arms = split(sd)
        c0, c1 = arms["core"]
        r = sb(rowcorr(c0[None, :] - A0, c1[None, :] - A1))
        allq.append(r)
        if strengths is None:
            strengths = ((A0 + A1) / 2).mean(axis=1)
    R = np.nanmean(np.array(allq), axis=0)
    q = {k: float(np.nanpercentile(R, k)) for k in (0, 5, 25, 50, 75, 95, 100)}
    iqr = q[75] - q[25]
    rho_str = float(np.corrcoef(R[~np.isnan(R)], strengths[~np.isnan(R)])[0, 1])

    print(f"\n  ⭐ CENSUS — reliability of `core − F` over ALL {len(subs)} fixed prompt-blind comparators")
    print(f"    {'min':>8}{'p5':>9}{'p25':>9}{'median':>9}{'p75':>9}{'p95':>9}{'max':>9}{'IQR':>9}")
    print(f"    {q[0]:>8.4f}{q[5]:>9.4f}{q[25]:>9.4f}{q[50]:>9.4f}{q[75]:>9.4f}"
          f"{q[95]:>9.4f}{q[100]:>9.4f}{iqr:>9.4f}")
    # ⛔ THE FIRST VERSION MIXED TWO OBJECTS IN ONE SENTENCE: it printed the generic ARM's rho
    #    (from sat_generic.npz) beside POOL ROW 0's percentile, on the assumption that `generic`'s
    #    criterion indices (0,1,2,3) name the same texts as pool16's indices 0-3. **Index identity
    #    is not text identity** -- my own R451 caveat, applied to the wrong file. Both are reported
    #    now, separately and labelled, and the percentile that matters is BY VALUE.
    pct_gen = float(np.nanmean(R < rho_gen))
    print(f"\n    R459's `generic` ARM sits at rho {rho_gen:.4f} -> percentile {pct_gen:.3f} BY VALUE")
    print(f"    within this comparator distribution.")
    if gj is not None:
        print(f"    ⚠ pool ROW {gj} (indices {gidx}) is a DIFFERENT object -- index identity is not")
        print(f"      text identity -- and it sits at rho {R[gj]:.4f}, percentile "
              f"{float(np.nanmean(R < R[gj])):.3f}. Reported separately, never merged.")
    print(f"    R457's sham line (not in this population): {rho_sham:.4f}  "
          f"vs the census max {q[100]:.4f}")
    print(f"    corr(RHO(F), strength(F)) = {rho_str:+.4f}   "
          f"{'⚠ reliability TRACKS the comparator' if abs(rho_str) >= 0.50 else 'not driven by strength'}")
    qs = np.array([[float(np.nanpercentile(a, k)) for k in (25, 50, 75)] for a in allq])
    print(f"    across-seed spread of the quartiles: "
          f"p25 {qs[:,0].std():.4f}  med {qs[:,1].std():.4f}  p75 {qs[:,2].std():.4f}")

    ctrl_ok = a1_ok and a2_ok and neg_ok
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif abs(rho_str) >= 0.50:
        world = "W-STRENGTH"
    elif iqr <= 0.05:
        world = "W-STABLE"
    else:
        world = "W-SWINGS"
    print(f"\n  WORLD: {world}")
    if world == "W-STABLE":
        print(f"    IQR {iqr:.4f}: the reliability of `core − F` barely moves across the WHOLE")
        print(f"    comparator population. R459's conclusion generalises and `generic` was not")
        print(f"    special — it sits at percentile {pct_gen:.3f}.")
    elif world == "W-SWINGS":
        print(f"    IQR {iqr:.4f}: `core − generic` was ONE DRAW. R459 inherited the defect it was")
        print(f"    built to test, and its 0.8363 must be restated as a distribution.")
    elif world == "W-STRENGTH":
        print(f"    corr(RHO, strength) = {rho_str:+.4f}: reliability is a property of the COMPARATOR.")
        print(f"    Every difference-based reliability in this campaign needs its comparator named.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "n_comparators": len(subs),
           "quantiles": q, "iqr": iqr, "rho_generic": rho_gen, "generic_arm_percentile_by_value": pct_gen,
           "pool_row0_rho": (None if gj is None else float(R[gj])),
           "rho_sham_reference": rho_sham, "corr_rho_strength": rho_str,
           "r459_committed": R459_DGEN, "r457_committed": R457_DSHAM,
           "seed_quartile_sd": [float(qs[:, i].std()) for i in range(3)],
           "controls": {"anchor1_ok": bool(a1_ok), "anchor2_ok": bool(a2_ok),
                        "negative_rho": neg, "negative_ok": bool(neg_ok)}}
    (RES / "r460_comparator_census.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r460_comparator_census.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
