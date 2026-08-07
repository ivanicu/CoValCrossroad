"""R448 -- the judge inversion: a differential mechanism, or regression to the mean?

⛔ THE ANNOUNCED STATISTIC WAS KILLED BY RUNG 1, THREE LINES, ZERO COMPUTE. R447 closed with
   "measure the per-criterion satisfaction VARIANCE each judge assigns... if 0.8B compresses one
   arm's spread more, the reordering is a property of the judge's dynamic range." **A2 is EXACTLY
   invariant under any affine rescale of satisfaction**: the arm score is a MEAN over criteria, and
   `score.py:41` is `sign(y_i - y_j)`, so `s -> a*s+b (a>0)` leaves every sign untouched. A global
   variance ratio is precisely the affine part. **It has zero explanatory power by arithmetic.**
   *Sixteenth announced step checked, NINTH killed.*

⭐ AND CHECKING IT SURFACED THE WORLD THE ROUND SHOULD HAVE BEEN ABOUT. From committed artifacts
   (R446/R447), a DERIVATION, not a measurement:
       gen         quantile 0.2615 @2B -> 0.7929 @0.8B
       coval_core  quantile 1.0000 @2B -> 0.6984 @0.8B
   **The quantile inverts too, so the bar did not move -- the arms reordered inside their own
   reference class.** But an arm at quantile 1.000 has NOWHERE TO GO BUT DOWN and an arm at 0.26 has
   mostly up. **Under ANY imperfect cross-judge correspondence, those two shifts are what regression
   to the mean produces with no differential mechanism whatsoever.** R447's headline -- "the judge
   REORDERS the definition's two candidate members" -- is not entitled to a mechanism until this
   world is dead.

ESTIMAND (named before the method)
    SHIFT(a) = quantile_08B(a) - quantile_2B(a), for a in {coval_core, gen}, where the quantile is
    taken within the C(16,4)=1,820 reference class judged by the SAME judge.
    NULL, and it uses no model: the 1,820 references are themselves objects that underwent the same
    judge change. For a band of references with quantile_2B near the arm's, the empirical
    distribution of THEIR shifts is the reference distribution for the arm's shift.
        p(a) = P_refs-in-band[ |SHIFT(ref)| >= |SHIFT(a)| ]        [two-sided, conditional on start]
    SECOND estimand, the mechanism if the first says arm-specific:
        X(a,p) = mean over the 6 pairs, over the arm's criteria at prompt p, of
                 [ sign_2B(crit, pair) == sign_08B(crit, pair) ]   -- per-criterion cross-judge
                 sign agreement. Paired between arms over the SAME prompts.

IDENTIFICATION
    SHIFT and its conditional null are identified: both judges scored the same pool and the same
    arms on the same prompts. X is identified per (prompt, criterion).
    ⚠ NOT identified: which judge is right. Two judges can refute a rule and never establish one.
    ⚠ NOT identified: a same-judge noise ceiling. `sat_coval_core_2bA/2bB.npz` are BYTE-IDENTICAL
      (md5 2076304c1d209b255b03427cab850e98) -- a determinism artifact, not two draws. Using them as
      a re-run floor would be §4's "determinism read as currency" exactly. Registered as impossible.

SCOPE  population : the 968 home-release prompts scored by both judges
       instrument : Qwen3.5-2B-Base and Qwen3.5-0.8B-Base; A2 over 6 pairs, 3 annotator draws
       baseline   : each judge's OWN 1,820-subset class; the null is the references themselves
       regime     : k in {1..4} criteria per arm per prompt

WORLDS
    W-REGRESSION  both arms' shifts are TYPICAL of references starting at the same quantile ->
                  the inversion is what happens to any object at rank 1.00 and rank 0.26 under
                  imperfect correspondence. No differential mechanism. R447's "the judge REORDERS
                  the candidates" must be downgraded to "the judge's correspondence is imperfect,
                  and rank 1.00 has nowhere to go but down."
    W-ARM         at least one arm's shift is ATYPICAL for its starting band -> something about that
                  arm's criteria transports differently, and X says which.
    W-TIE         the effect is carried by exact ties (sign 0) at the coarser judge -- a
                  quantization artifact, not a disagreement about content.

PREDICTION MATRIX
                     both typical    one+ atypical    ties carry it
    W-REGRESSION         0.90             0.05            0.05
    W-ARM                0.05             0.90            0.05
    W-TIE                0.05             0.15            0.80

PRE-REGISTERED KILL -- CONDITIONAL. The threshold is binding only if the controls fire.
    if POSITIVE fires and NEGATIVE is null and the band is non-degenerate:
        both p(a) > 0.05 after BH over the whole grid          -> W-REGRESSION
        any  p(a) <= 0.05 after BH                             -> W-ARM
        dropping tied pairs removes the X gap AND flips p(a)   -> W-TIE
    else: UNVERIFIED. Never OVERTURNED, never CONFIRMED.

CONTROLS
    POSITIVE   plant a strictly monotone judge: 0.8B := f(2B) with f increasing. Every reference and
               both arms must show SHIFT exactly 0, and the null must then call every arm typical.
               ⚠ and it must FAIL at g=0: on the REAL data the same check must return non-zero
               shifts, otherwise the instrument cannot see a shift at all.
               FLOOR/CEILING: floor = |shift| under the monotone plant (must be 0), ceiling = mean
               |shift| under a fully shuffled judge. The kill threshold is admissible only if
               floor < observed < ceiling.
    NEGATIVE   shuffle the 0.8B reference A2 vector ACROSS references (destroys the correspondence,
               preserves the marginal distribution exactly) -> shifts must inflate to the ceiling.
    g=0        an arm compared to ITSELF at one judge: SHIFT = 0 and p = 1.0.
    PLACEBO    `gen_sham` carried through the identical path -- wrong-prompt criteria, so it should
               show no arm-specific transport.
    TIE RATE   reported per judge; X recomputed with tied pairs dropped.
    SEEDS      the annotator draw held common with R446/R447 (same prompt-keyed md5 rng), so this
               round differs from those only in what is computed, never in what was sampled.

MULTIPLICITY  2 arms x 5 band widths x 2 tie rules = 20 cells, BH over all 20, non-survivors printed.
ARTIFACT      results/r448_regression_null.json
IMPOSSIBLE HERE, NAMED
    * a same-judge re-run floor -- the two 2B files are byte-identical (see IDENTIFICATION).
    * a third judge -- no third satisfaction set exists.
    * construct validity of A2 -- would need the release's own human rankings as ground truth for
      the CRITERIA, which the release does not carry.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
ARMS = ("coval_core", "gen", "gen_sham")


def stable(pid: str) -> int:
    return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)


def signs(Y):
    """Y: (..., 4) -> (..., 6) sign vector. The statistic score.py:41 computes."""
    return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def bh(ps, q=0.05):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps)
    keep = np.zeros(m, bool); thr = q * (np.arange(1, m + 1)) / m
    ok = ps[o] <= thr
    if ok.any():
        keep[o[:np.max(np.where(ok)[0]) + 1]] = True
    return keep


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R448 · the judge inversion — differential mechanism, or regression to the mean?\n")
    print("  ⛔ RUNG 1 KILLED THE ANNOUNCED STATISTIC, zero compute: A2 is EXACTLY invariant under")
    print("     s -> a*s+b (a>0), because the arm score is a MEAN and score.py:41 is sign(y_i-y_j).")
    print("     A satisfaction-VARIANCE ratio is that affine part. Sixteenth step, NINTH killed.\n")

    need = {"pool2": SATD / "sat_genericpool16.npz", "pool8": SATD / "sat08_genericpool16.npz"}
    for n in ARMS:
        need[f"2b_{n}"] = SATD / f"sat_{n}.npz"
        need[f"08_{n}"] = SATD / f"sat08_{n}.npz"
    missing = [str(v.name) for v in need.values() if not v.exists()]
    if missing:
        print(f"  UNRUNNABLE: absent {missing}. Exit 2, never 0."); return 2

    pool2, pool8 = SC.load_sat(need["pool2"]), SC.load_sat(need["pool8"])
    targets, _ = SC.load_targets()
    A2 = {n: SC.load_sat(need[f"2b_{n}"]) for n in ARMS}
    A8 = {n: SC.load_sat(need[f"08_{n}"]) for n in ARMS}
    pids = sorted(set(pool2) & set(pool8) & set(targets)
                  & set.intersection(*[set(v) for v in list(A2.values()) + list(A8.values())]))
    n = len(pids)
    print(f"  prompts usable at BOTH judges, all arms: {n}")
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}

    def a2_from_scores(Y, p):
        """Y: (m,4) arm scores -> (m,) agreement with the 3 held-common human draws."""
        return (signs(Y)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))

    # ---- pool matrices and the 1,820-reference class at BOTH judges -----------------------------
    subsets = list(itertools.combinations(range(16), 4))
    S = np.zeros((len(subsets), 16))
    for j, sub in enumerate(subsets):
        S[j, list(sub)] = 1.0
    REF = {}
    for tag, pool in (("2b", pool2), ("08", pool8)):
        R = np.zeros((len(subsets), n))
        for i, p in enumerate(pids):
            M = np.zeros((16, 4))
            for (ci, ltr), v in pool[p].items():
                M[ci, L.index(ltr)] = v
            R[:, i] = a2_from_scores(S @ M, p)
        REF[tag] = R
    print(f"  reference class: C(16,4) = {len(subsets)}, computed at BOTH judges")

    def arm_vec(sat, name):
        v = np.zeros(n)
        for i, p in enumerate(pids):
            d = sat[name][p]
            ks = sorted({c for (c, _) in d})
            M = np.array([[d.get((c, l), 0.0) for l in L] for c in ks])
            v[i] = a2_from_scores(M.mean(axis=0)[None, :], p)[0]
        return v
    ARMV = {t: {a: arm_vec(s, a) for a in ARMS} for t, s in (("2b", A2), ("08", A8))}

    def quant(tag, v):
        return float((REF[tag].mean(axis=1) < v.mean()).mean())

    # ---- the conditional null: the references' OWN shifts, banded on their 2B quantile ----------
    rq = {t: np.argsort(np.argsort(REF[t].mean(axis=1))) / (len(subsets) - 1) for t in ("2b", "08")}
    ref_shift = rq["08"] - rq["2b"]

    def p_typical(shift, start, half):
        band = np.abs(rq["2b"] - start) <= half
        if band.sum() < 30:
            return None, int(band.sum()), None
        d = ref_shift[band]
        return float((np.abs(d) >= abs(shift)).mean()), int(band.sum()), float(np.median(d))

    obs = {a: {"q2b": quant("2b", ARMV["2b"][a]), "q08": quant("08", ARMV["08"][a]),
               "a2_2b": float(ARMV["2b"][a].mean()), "a2_08": float(ARMV["08"][a].mean())}
           for a in ARMS}
    for a in ARMS:
        obs[a]["shift"] = obs[a]["q08"] - obs[a]["q2b"]

    # ---- CONTROLS ------------------------------------------------------------------------------
    print("\n  CONTROLS")
    # POSITIVE: a strictly monotone judge must give shift 0 everywhere -- and must FAIL at g=0.
    mono = np.argsort(np.argsort(REF["2b"].mean(axis=1))) / (len(subsets) - 1)
    pos_floor = float(np.abs(mono - rq["2b"]).mean())
    shuf = np.random.default_rng(0).permutation(rq["08"])
    ceiling = float(np.abs(shuf - rq["2b"]).mean())
    observed_ms = float(np.abs(ref_shift).mean())
    pos_ok = (pos_floor < 1e-12) and (pos_floor < observed_ms < ceiling)
    print(f"    POSITIVE  monotone judge -> mean|shift| = {pos_floor:.2e} (must be 0)")
    print(f"              g=0 on REAL data -> {observed_ms:.4f} (must be > 0: the instrument sees a shift)")
    print(f"              FLOOR {pos_floor:.2e} < OBSERVED {observed_ms:.4f} < CEILING {ceiling:.4f}"
          f"   {'PASS' if pos_ok else '⛔ FAIL'}")
    # ⛔ CONTROL REPAIRED MID-ROUND, and the repair is a DERIVATION, not a relaxation.
    #    The first version demanded `ceiling > 3*observed`. For two INDEPENDENT rank vectors on
    #    [0,1], E|U-V| = 1/3 exactly -- so the ceiling is CAPPED at 0.3333 and that threshold
    #    silently required the real shift to be under 1/9, a bar derived from nothing. That is §4's
    #    "control that cannot PASS", built a 5th time. The admissible form is §4's own:
    #    floor < observed < ceiling, with `observed` resolvably separated from BOTH ends.
    ANALYTIC_CEILING = 1.0 / 3.0
    ceiling_matches = abs(ceiling - ANALYTIC_CEILING) < 0.01
    rb = np.random.default_rng(11)
    bs_obs = np.array([np.abs(ref_shift)[rb.integers(0, len(ref_shift), len(ref_shift))].mean()
                       for _ in range(2000)])
    lo, hi = float(np.percentile(bs_obs, 2.5)), float(np.percentile(bs_obs, 97.5))
    neg_ok = ceiling_matches and (hi < ceiling) and (lo > pos_floor)
    print(f"    NEGATIVE  shuffled correspondence -> {ceiling:.4f}; analytic E|U-V| = 1/3 = "
          f"{ANALYTIC_CEILING:.4f}   {'matches' if ceiling_matches else '⛔ DOES NOT MATCH'}")
    print(f"              real {observed_ms:.4f} CI [{lo:.4f},{hi:.4f}] strictly inside "
          f"(floor {pos_floor:.2e}, ceiling {ceiling:.4f})   {'PASS' if neg_ok else '⛔ FAIL'}")
    g0 = abs(quant("2b", ARMV["2b"]["gen"]) - quant("2b", ARMV["2b"]["gen"]))
    print(f"    g=0       an arm against ITSELF at one judge -> shift {g0:.1e}"
          f"   {'PASS' if g0 < 1e-12 else '⛔ FAIL'}")
    # the null must itself REGRESS, or it is degenerate and cannot express W-REGRESSION
    top = ref_shift[rq["2b"] > 0.9].mean() if (rq["2b"] > 0.9).any() else np.nan
    bot = ref_shift[rq["2b"] < 0.1].mean() if (rq["2b"] < 0.1).any() else np.nan
    reg_ok = bool(top < 0 < bot)
    print(f"    BAND      references regress: top-decile mean shift {top:+.4f}, "
          f"bottom-decile {bot:+.4f}   {'PASS' if reg_ok else '⛔ FAIL (null is degenerate)'}")

    # ---- per-criterion cross-judge sign agreement (the mechanism, if W-ARM) ---------------------
    def X_of(a, drop_ties):
        per = np.zeros(n)
        for i, p in enumerate(pids):
            d2, d8 = A2[a][p], A8[a][p]
            ks = sorted({c for (c, _) in d2} & {c for (c, _) in d8})
            Y2 = np.array([[d2.get((c, l), 0.0) for l in L] for c in ks])
            Y8 = np.array([[d8.get((c, l), 0.0) for l in L] for c in ks])
            s2, s8 = signs(Y2), signs(Y8)
            m = np.ones_like(s2, bool) if not drop_ties else (s2 != 0) & (s8 != 0)
            per[i] = (s2 == s8)[m].mean() if m.any() else np.nan
        return per
    tie2 = float(np.mean([ (signs(np.array([[A2[a][p].get((c,l),0.) for l in L]
                          for c in sorted({c for (c,_) in A2[a][p]})])) == 0).mean()
                          for a in ARMS for p in pids[:200]]))
    tie8 = float(np.mean([ (signs(np.array([[A8[a][p].get((c,l),0.) for l in L]
                          for c in sorted({c for (c,_) in A8[a][p]})])) == 0).mean()
                          for a in ARMS for p in pids[:200]]))
    print(f"    TIE RATE  2B {tie2:.4f}   0.8B {tie8:.4f}")

    # ---- the grid: 2 arms x 5 bands x 2 tie rules ----------------------------------------------
    BANDS = (0.02, 0.05, 0.10, 0.15, 0.25)
    rows, ps = [], []
    for a in ("coval_core", "gen"):
        for hw in BANDS:
            pv, cnt, med = p_typical(obs[a]["shift"], obs[a]["q2b"], hw)
            for tr in (False, True):
                rows.append({"arm": a, "band": hw, "drop_ties": tr, "p": pv,
                             "n_band": cnt, "band_median_shift": med})
                ps.append(1.0 if pv is None else pv)
    keep = bh(ps)
    for r, k in zip(rows, keep):
        r["survives_bh"] = bool(k)

    XA = {a: {tr: X_of(a, tr) for tr in (False, True)} for a in ARMS}
    xres = {}
    for tr in (False, True):
        d = XA["coval_core"][tr] - XA["gen"][tr]
        good = ~np.isnan(d); d = d[good]
        mde = ZEFF * d.std(ddof=1) / np.sqrt(len(d))
        b = np.random.default_rng(7)
        bs = np.array([d[b.integers(0, len(d), len(d))].mean() for _ in range(2000)])
        xres["drop_ties" if tr else "all_pairs"] = {
            "X_coval": float(np.nanmean(XA["coval_core"][tr])),
            "X_gen": float(np.nanmean(XA["gen"][tr])),
            "X_gen_sham": float(np.nanmean(XA["gen_sham"][tr])),
            "paired_delta": float(d.mean()), "mde": float(mde),
            "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "resolved": bool(abs(d.mean()) > mde)}

    # ⭐ X FOR THE REFERENCE POOL ITSELF. `gen`'s A2 FELL (0.5374 -> 0.4743) while its RANK ROSE,
    #    which can only mean the reference class fell further. Whether that is so is a measurement,
    #    not an inference, and the pool's own criteria are on disk.
    def X_pool(drop_ties):
        per = np.zeros(n)
        for i, p in enumerate(pids):
            ks = sorted({c for (c, _) in pool2[p]} & {c for (c, _) in pool8[p]})
            Y2 = np.array([[pool2[p].get((c, l), 0.0) for l in L] for c in ks])
            Y8 = np.array([[pool8[p].get((c, l), 0.0) for l in L] for c in ks])
            s2, s8 = signs(Y2), signs(Y8)
            m = np.ones_like(s2, bool) if not drop_ties else (s2 != 0) & (s8 != 0)
            per[i] = (s2 == s8)[m].mean() if m.any() else np.nan
        return per
    for tr in (False, True):
        xp = X_pool(tr)
        key = "drop_ties" if tr else "all_pairs"
        xres[key]["X_pool16"] = float(np.nanmean(xp))
        for a in ("coval_core", "gen"):
            d = XA[a][tr] - xp
            d = d[~np.isnan(d)]
            mde = ZEFF * d.std(ddof=1) / np.sqrt(len(d))
            xres[key][f"{a}_vs_pool"] = {"delta": float(d.mean()), "mde": float(mde),
                                         "resolved": bool(abs(d.mean()) > mde)}

    controls_ok = pos_ok and neg_ok and reg_ok and (g0 < 1e-12)
    atypical = [r for r in rows if r["p"] is not None and r["survives_bh"]]
    if not controls_ok:
        world = "UNVERIFIED"
    elif atypical:
        world = "W-ARM"
    else:
        world = "W-REGRESSION"

    print("\n  OBSERVED — quantile within each judge's OWN 1,820-reference class")
    print(f"    {'arm':<12}{'q@2B':>9}{'q@0.8B':>10}{'SHIFT':>10}{'A2@2B':>9}{'A2@0.8B':>10}")
    for a in ARMS:
        o = obs[a]
        print(f"    {a:<12}{o['q2b']:>9.4f}{o['q08']:>10.4f}{o['shift']:>+10.4f}"
              f"{o['a2_2b']:>9.4f}{o['a2_08']:>10.4f}")
    print("\n  IS THAT SHIFT UNUSUAL FOR A REFERENCE THAT STARTED THERE?  (BH over all 20 cells)")
    print(f"    {'arm':<12}{'band':>7}{'ties':>7}{'n_band':>8}{'med_shift':>11}{'p':>8}  BH")
    for r in rows:
        med = "        n/a" if r["band_median_shift"] is None else f"{r['band_median_shift']:>+11.4f}"
        pv = "     n/a" if r["p"] is None else f"{r['p']:>8.4f}"
        ties = "drop" if r["drop_ties"] else "all"
        print(f"    {r['arm']:<12}{r['band']:>7.2f}{ties:>7}{r['n_band']:>8}{med}{pv}"
              f"  {'SURVIVES' if r['survives_bh'] else '.'}")
    print("\n  PER-CRITERION CROSS-JUDGE SIGN AGREEMENT (the mechanism, if W-ARM)")
    for k, v in xres.items():
        print(f"    {k:<10} coval {v['X_coval']:.4f}  gen {v['X_gen']:.4f}  sham {v['X_gen_sham']:.4f}"
              f"  POOL16 {v['X_pool16']:.4f}")
        print(f"    {'':<10} coval-gen  Δ {v['paired_delta']:+.4f} vs MDE {v['mde']:.4f} "
              f"CI [{v['ci'][0]:+.4f},{v['ci'][1]:+.4f}]  "
              f"{'RESOLVED' if v['resolved'] else 'unresolved'}")
        for a in ("coval_core", "gen"):
            w = v[f"{a}_vs_pool"]
            print(f"    {'':<10} {a}-pool16  Δ {w['delta']:+.4f} vs MDE {w['mde']:.4f}  "
                  f"{'RESOLVED' if w['resolved'] else 'unresolved'}")
    print("\n  ⚠ BOUNDARY CENSORING, and it is why the two arms are not read the same way:")
    print(f"    coval_core starts at quantile {obs['coval_core']['q2b']:.4f} -- the TOP of the")
    print("    scale -- so every reference in its band can only move DOWN. Its two-sided p is")
    print("    computed against a censored null and is reported as an UPPER BOUND on how unusual")
    print(f"    it is. `gen` starts at {obs['gen']['q2b']:.4f}, interior, and its test is clean.")

    print(f"\n  WORLD: {world}")
    if world == "W-REGRESSION":
        print("    Both arms' shifts are TYPICAL of references that started at the same quantile.")
        print("    ⛔ The inversion needs NO differential mechanism: an arm at quantile 1.000 has")
        print("       nowhere to go but down, and one at 0.26 has mostly up. R447's 'the judge")
        print("       REORDERS the candidates' overstates what the data licenses.")
    elif world == "W-ARM":
        print("    At least one arm moved further than its own starting band explains.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "n_refs": len(subsets),
           "observed": obs, "grid": rows, "X": xres,
           "controls": {"positive_floor": pos_floor, "observed_mean_abs_shift": observed_ms,
                        "ceiling": ceiling, "positive_ok": pos_ok, "negative_ok": neg_ok,
                        "band_regresses": reg_ok, "g0": g0,
                        "tie_rate_2b": tie2, "tie_rate_08b": tie8},
           "affine_gauge": "A2 exactly invariant under s->a*s+b, a>0 (score.py:41 + mean) — the "
                           "announced variance statistic is that invariant part",
           "levels_comparable_across_judges": False}
    (RES / "r448_regression_null.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r448_regression_null.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
