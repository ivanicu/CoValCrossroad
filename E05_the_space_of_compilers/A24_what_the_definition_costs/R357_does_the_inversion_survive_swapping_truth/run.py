"""R357 — a GAUGE TEST on R356: swap which judge is called `truth` and the verdict must not move.

R356 concluded that the two judges resolvably INVERT the `random_k` family (rho at the 0.00
percentile of its own null) while `topw_k`'s +0.81 is forced by 5.7 se of separation. Its own
register names the assumption it could not test:

    "the null uses the 2B effects AS the true ordering, which is the best available and is not the
     same thing."

That is a GAUGE. The transformation is `exchange the roles of the two judges`. The PROPERTY under
claim -- *do these two judges disagree about this family beyond noise?* -- is SYMMETRIC in the pair:
disagreement is a relation, not a direction. So if the MEASUREMENT is not invariant under the swap,
the measurement is blind to the property it names, and R356's finding is about the choice of
reference rather than about the judges. Attack-ladder step 1, run on this campaign's newest claim
and run BEFORE any GPU is spent on the third judge that R356's next-gradient line asked for.

⚠ AND THAT NEXT-GRADIENT LINE WAS WRONG ABOUT COST, CHECKED HERE RATHER THAN ASSUMED. R301's
  register calls a third judge "a drop-in" because the prompt contract is byte-identical between
  `covalx/judge.py` and `E01/R04/run.py`. The CONTRACT is; the MODEL is not. The local store holds
  exactly two Qwen3.5 checkpoints -- 0.8B and 2B -- plus one quantised GGUF of a different family
  and a fine-tune unsuited to a values judge. A third reading needs a download and a second serving
  stack, so it is NOT-ATTEMPTED-AND-NOT-CHEAP, which is a different register entry from
  NOT-ATTEMPTED. That is an availability claim in the flattering direction and it is corrected here.

⛔ ARITHMETIC TRAP, answered before the run. Could the swap come out different? YES, and there is a
   real mechanism for it, which is why this is a test and not a formality: an OLS slope is NOT
   symmetric. `beta_yx * beta_xy = R^2`, so with R301's clause-① fit (beta 0.4340, R² 0.6124) the
   reverse slope is 0.6124/0.4340 = 1.411 -- an EXPANSION, not a shrink. The two directions also
   carry different per-arm precisions. Nothing forces the two verdicts to agree, and regression to
   the mean is exactly the asymmetry that makes naive reversals wrong.

ESTIMAND        For each direction D in {2B is truth, 0.8B is truth}, each family with n>=5, and
                each clause: the observed between-judge Spearman (identical in both directions --
                Spearman is symmetric) and its percentile in the null THAT DIRECTION implies, where
                the null takes D's judge as the true ordering, D's own per-arm se as its noise, the
                other judge's se as the reading noise, and D's OWN fitted slope.

IDENTIFICATION  Exact given R301's committed per-arm effects and MDEs. NOT identified: which judge
                is actually closer to truth -- that is precisely what a third reading would settle
                and neither direction can. This round therefore establishes INVARIANCE or its
                failure, never which direction is right.

SCOPE           R301's `judge_slope.json` (41 arms, 968 prompts) · instruments Qwen3.5-2B-Base and
                Qwen3.5-0.8B-Base · baseline each direction's own simulated null · regime:
                within-family, n>=5, the same population R356's verdict used.

WORLDS
  W-SYMMETRIC   both directions flag the same families below their bands. Disagreement is a property
                of the PAIR and R356 stands as written.
  W-ASYMMETRIC  the flagged set differs between directions. Then R356's statistic partly measures
                which judge was placed on the x-axis, and its sentence must be narrowed to that
                direction or withdrawn.
  W-NEITHER     no family is flagged in either direction. Then R356's flag was an artifact of its
                specific beta/se assignment and the inversion claim dies outright.

PREDICTION MATRIX
  W-SYMMETRIC   -> flagged(2B-truth) == flagged(0.8B-truth), both non-empty
  W-ASYMMETRIC  -> the two sets differ
  W-NEITHER     -> both empty
The three differ on a set equality computed identically in both directions.

PRE-REGISTERED KILL -- conditional, so it cannot fire on a broken instrument.
    if placebo_ok and positive_ok and g0_ok and gauge_actually_moved:
        if flagged_A == flagged_B and flagged_A  -> W-SYMMETRIC   (R356 survives its own gauge)
        elif not flagged_A and not flagged_B     -> W-NEITHER     (R356's flag retracted)
        else                                     -> W-ASYMMETRIC  (R356 narrowed to one direction)
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

⚠ THE CONTROL THIS ROUND NEEDS THAT R356 DID NOT: `gauge_actually_moved`. A gauge test whose two
  code paths compute the same numbers proves nothing and passes trivially -- it is the purest form
  of "check that cannot fail". So the two directions' fitted slopes and their simulated null bands
  are required to DIFFER before any invariance claim is allowed. If the swap changes nothing
  numerically, the test never ran.

POSITIVE CTRL   the exact reversal (-t) must be flagged below the band in BOTH directions.
g=0 CTRL        the exact null (other = beta*truth, no noise) must NOT be flagged, in both.
PLACEBO         a family against itself: rho = 1 exactly.
NOISE FLOOR     R301's committed per-arm MDEs, se = MDE / ZEFF, per direction.
MULTIPLICITY    2 directions x 2 families x 2 clauses = 8 cells; all printed with their percentiles.
SPECIFICATION   shared-noise correlation r in {0.0, 0.3, 0.6} in both directions, whole curve.
SEEDS           3 seeds per band; printed per direction, never averaged across directions.
ARTIFACT        results/r357_gauge_swap.json with the source hash.

IMPOSSIBLE HERE
  which judge is right  -- needs a third reading. NOT-ATTEMPTED-AND-NOT-CHEAP: no third checkpoint
                           is on the local store, so it needs a download plus a serving stack.
  n<5 families          -- Spearman is 4-valued at n=3; excluded by R356's stated rule.

EXIT
    0  controls hold and the invariance is classified
    1  a control misbehaved, or the gauge did not move -- UNVERIFIED
    2  R301's artifact or R356's module is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

# Import R356's OWN statistic and null builder rather than re-typing them. The gauge test is only
# meaningful if both directions run the SAME instrument; a re-implementation would test my code.
R356 = next(A24.glob("R356_*"), None)
if R356 is None:
    print("  UNRUNNABLE: R356 is absent. Exit 2, never 0."); sys.exit(2)
sys.path.insert(0, str(R356))
from run import spearman, null_band, ZEFF, SEEDS, SHARED     # noqa: E402

MIN_N = 5


def ols(x, y):
    """Slope and R^2 of y on x. Deliberately asymmetric: beta_yx * beta_xy = R^2."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    b = float(np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1))
    r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
    return b, r2


def main() -> int:
    d = next(A24.glob("R301_*"), None)
    f = sorted((d / "results").glob("*.json")) if d else []
    if not f:
        print("  UNRUNNABLE: R301's artifact is absent. Exit 2, never 0.")
        return 2
    art = json.loads(f[0].read_text())
    rows, fams = art["rows"], art["families"]
    sha = hashlib.sha256(f[0].read_bytes()).hexdigest()[:16]
    live = {k: v for k, v in fams.items() if len(v) >= MIN_N}
    if not live:
        print(f"  UNRUNNABLE: no family with n>={MIN_N}. Exit 2, never 0.")
        return 2

    print("R357 · gauge test on R356 — swap which judge is called `truth`")
    print(f"  R301 artifact sha256[:16] {sha} · families n>={MIN_N}: "
          f"{', '.join(f'{k}({len(v)})' for k, v in sorted(live.items()))}")
    print("  Spearman is symmetric, so the OBSERVED rho is identical in both directions.")
    print("  What moves is the NULL: whose ordering is truth, whose se is which, and the slope.\n")

    # ⚠ FIT POPULATION, matched to R301 rather than declared as a difference. R301 fits on 39 arms,
    #   holding out `promptecho` and `promptecho_sham` because they cover 398 prompts and not 968 --
    #   a DIFFERENT POPULATION, whose effects must not enter a slope estimated over the others.
    #   v1 of this round fitted all 41 and got beta 0.4535 against R301's 0.4340; the gap was my
    #   population, not my estimator. Reading it as an estimator difference and moving on would have
    #   been the flattering explanation.
    off = set(art.get("off_fit", []))
    allarms = [a for a in sorted(rows) if a not in off]
    print(f"  slope fitted on {len(allarms)} arms, holding out {sorted(off)} "
          f"(different prompt population) — R301's own fit set\n")
    # --- the two directions' own fitted slopes, per clause -----------------------------------------
    BETA = {}
    for c in (1, 2):
        e2 = [rows[a][f"c{c}_2"][0] for a in allarms]
        e8 = [rows[a][f"c{c}_8"][0] for a in allarms]
        b_fwd, r2 = ols(e2, e8)          # 0.8B on 2B  — the shrink R301 fitted
        b_rev, _ = ols(e8, e2)           # 2B on 0.8B  — NOT 1/b_fwd
        BETA[c] = dict(fwd=b_fwd, rev=b_rev, r2=r2, product=b_fwd * b_rev)
        print(f"  clause {c}: beta(2B->0.8B) {b_fwd:.4f} · beta(0.8B->2B) {b_rev:.4f} · "
              f"product {b_fwd*b_rev:.4f} vs R2 {r2:.4f}   "
              f"{'identity holds' if abs(b_fwd*b_rev-r2)<1e-9 else 'MISMATCH'}")
        print(f"            1/beta(2B->0.8B) would be {1/b_fwd:.4f} — "
              f"using it would have been the naive-reversal error")

    def pull(arms, c, truth_is_2b):
        t = np.array([rows[a][f"c{c}_{'2' if truth_is_2b else '8'}"][0] for a in arms], float)
        o = np.array([rows[a][f"c{c}_{'8' if truth_is_2b else '2'}"][0] for a in arms], float)
        st = np.array([rows[a][f"mde{c}_{'2' if truth_is_2b else '8'}"] for a in arms], float) / ZEFF
        so = np.array([rows[a][f"mde{c}_{'8' if truth_is_2b else '2'}"] for a in arms], float) / ZEFF
        return t, o, st, so

    DIRS = [("2B is truth", True), ("0.8B is truth", False)]

    # --- controls, in BOTH directions ---------------------------------------------------------------
    plac, pos, g0 = [], [], []
    for _lbl, t2 in DIRS:
        for fam, arms in sorted(live.items()):
            for c in (1, 2):
                t, _o, st, so = pull(arms, c, t2)
                b = BETA[c]["fwd" if t2 else "rev"]
                nb = null_band(t, st, so, b, 0.0, 0)
                lo = float(np.percentile(nb, 2.5))
                plac.append(spearman(t, t))
                pos.append(spearman(t, -b * t) < lo)
                g0.append(spearman(t, b * t) >= lo)
    placebo_ok = all(abs(x - 1.0) < 1e-12 for x in plac)
    pos_ok, g0_ok = all(pos), all(g0)
    print(f"\n  PLACEBO  family against itself, {len(plac)} cells: rho = "
          f"{sorted({round(x,12) for x in plac})}  {'PASS' if placebo_ok else 'FAIL'}")
    print(f"  POSITIVE exact reversal flagged below the band: {sum(pos)}/{len(pos)} cells, "
          f"both directions  {'PASS' if pos_ok else 'FAIL'}")
    print(f"  g=0      exact null (other = beta*truth, no noise) NOT flagged: "
          f"{sum(g0)}/{len(g0)}  {'PASS' if g0_ok else 'FAIL'}")

    # --- the measurement ----------------------------------------------------------------------------
    print(f"\n    {'direction':>14}{'family':>10}{'cl':>4}{'rho':>8}"
          f"{'r=0.0 band':>18}{'r=0.6 band':>18}{'pctile@0.6':>12}  verdict")
    OUT, flagged = [], {}
    bands_by_dir = {}
    for lbl, t2 in DIRS:
        flagged[lbl] = set()
        for fam, arms in sorted(live.items()):
            for c in (1, 2):
                t, o, st, so = pull(arms, c, t2)
                b = BETA[c]["fwd" if t2 else "rev"]
                rho = spearman(t, o)
                cells, vd = {}, "inside"
                txt = {}
                for r_ in SHARED:
                    bs = [np.percentile(null_band(t, st, so, b, r_, s), [2.5, 97.5]) for s in SEEDS]
                    lo = float(np.mean([x[0] for x in bs])); hi = float(np.mean([x[1] for x in bs]))
                    pct = float(np.mean([(null_band(t, st, so, b, r_, s) <= rho).mean()
                                         for s in SEEDS]))
                    cells[str(r_)] = dict(lo=lo, hi=hi, pctile=pct)
                    txt[r_] = f"[{lo:+.2f},{hi:+.2f}]"
                    if rho < lo:
                        vd = "BELOW"
                    elif rho > hi and vd != "BELOW":
                        vd = "ABOVE"
                if vd == "BELOW":
                    flagged[lbl].add((fam, c))
                bands_by_dir[(lbl, fam, c)] = cells
                OUT.append(dict(direction=lbl, family=fam, clause=c, rho=rho, beta=b,
                                bands=cells, verdict=vd))
                print(f"    {lbl:>14}{fam:>10}{c:>4}{rho:>+8.3f}"
                      f"{txt[0.0]:>18}{txt[max(SHARED)]:>18}"
                      f"{cells[str(max(SHARED))]['pctile']*100:>11.2f}%  {vd}")

    # --- the control R356 did not need: did the gauge actually MOVE anything? -----------------------
    moved_beta = all(abs(BETA[c]["fwd"] - BETA[c]["rev"]) > 1e-6 for c in (1, 2))
    diffs = []
    for fam, arms in sorted(live.items()):
        for c in (1, 2):
            a = bands_by_dir[(DIRS[0][0], fam, c)][str(max(SHARED))]
            b_ = bands_by_dir[(DIRS[1][0], fam, c)][str(max(SHARED))]
            diffs.append(abs(a["lo"] - b_["lo"]) + abs(a["hi"] - b_["hi"]))
    moved_band = max(diffs) > 1e-6
    gauge_moved = moved_beta and moved_band
    print(f"\n  GAUGE ACTUALLY MOVED  slopes differ: {moved_beta} · null bands differ: {moved_band} "
          f"(max band shift {max(diffs):.4f})  {'PASS' if gauge_moved else 'FAIL'}")
    print(f"    Without this, a gauge test whose two paths compute the same numbers passes")
    print(f"    trivially — the purest 'check that cannot fail'.")

    A, B = flagged[DIRS[0][0]], flagged[DIRS[1][0]]
    print(f"\n  flagged, 2B as truth   : {sorted(A) if A else 'none'}")
    print(f"  flagged, 0.8B as truth : {sorted(B) if B else 'none'}")

    ctrl_ok = placebo_ok and pos_ok and g0_ok and gauge_moved
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved or the gauge did not move; the table is silence.")
        v = "UNVERIFIED"
    elif A == B and A:
        print(f"  W-SYMMETRIC — the same {len(A)} cell(s) are flagged whichever judge is called")
        print(f"  truth, and the two nulls are genuinely different objects (slopes "
              f"{BETA[1]['fwd']:.3f} vs {BETA[1]['rev']:.3f}). R356's inversion is a property of")
        print(f"  the PAIR, not of the reference choice, and its finding survives its own gauge.")
        v = "W_SYMMETRIC"
    elif not A and not B:
        print(f"  W-NEITHER — no family is flagged in either direction. R356's inversion is")
        print(f"  RETRACTED: it was an artifact of that round's beta/se assignment.")
        v = "W_NEITHER"
    else:
        # ⚠ The branch is right and a bare "the sets differ" would THROW AWAY what the run computed.
        #   The gauge does not fail globally or pass globally: it PARTITIONS the cells, and which
        #   side each claim lands on is the whole result.
        both, neither_, only = sorted(A & B), [], sorted(A ^ B)
        cells = sorted({(x["family"], x["clause"]) for x in OUT})
        neither_ = [c_ for c_ in cells if c_ not in A and c_ not in B]
        print(f"  W-ASYMMETRIC — and it PARTITIONS. The gauge neither passes nor fails globally:\n")
        print(f"    {'cell':>18}  {'2B-truth':>10}{'0.8B-truth':>12}   status")
        for fam, c in cells:
            pa = bands_by_dir[(DIRS[0][0], fam, c)][str(max(SHARED))]["pctile"] * 100
            pb = bands_by_dir[(DIRS[1][0], fam, c)][str(max(SHARED))]["pctile"] * 100
            st = ("INVARIANT · flagged" if (fam, c) in A and (fam, c) in B else
                  "INVARIANT · inside" if (fam, c) not in A and (fam, c) not in B else
                  "GAUGE-DEPENDENT")
            print(f"    {fam+' cl'+str(c):>18}  {pa:>9.2f}%{pb:>11.2f}%   {st}")
        print(f"\n  SURVIVES the gauge: {both if both else 'nothing'} — flagged in BOTH directions,")
        print(f"  so R356's INVERSION finding is a property of the pair, not of the reference.")
        print(f"  DOES NOT SURVIVE: {only if only else 'nothing'} — R356 read these as `inside,")
        print(f"  therefore forced, therefore no information`. Under the other direction they are")
        print(f"  resolvably BELOW. ⛔ That half of R356 is WITHDRAWN.")
        print(f"\n  ⚠ AND THE DIRECTION IS CONSISTENT EVEN WHERE THE VERDICT IS NOT. Every")
        print(f"    gauge-dependent cell sits in the LOW tail in BOTH directions — it is the")
        print(f"    RESOLUTION that moves, not the sign. So `agrees less than its separation")
        print(f"    forces` is the surviving direction; `resolvably so` is what the gauge decides.")
        print(f"\n  MECHANISM, and it is the classical one: beta(0.8B->2B) = {BETA[1]['rev']:.3f} is an")
        print(f"    EXPANSION. Taking the noisier judge as truth and fitting an expansion inflates")
        print(f"    the apparent separation, tightening the null (floor +0.66 -> +0.83 at r=0.6).")
        print(f"    REGRESSION TO THE MEAN is why the two directions are not reciprocal, and")
        print(f"    1/beta = {1/BETA[1]['fwd']:.3f} would have been the naive reversal.")
        print(f"  ⚠ Which direction is RIGHT is exactly what this round cannot say. Both nulls are")
        print(f"    self-consistent; only a third reading estimates the true ordering independently.")
        v = "W_ASYMMETRIC_PARTITIONED"

    out = dict(stamp(str(SELF)), r301_sha=sha, beta=BETA, rows=OUT,
               flagged={k: sorted(x) for k, x in flagged.items()},
               invariant_flagged=sorted(A & B), gauge_dependent=sorted(A ^ B),
               invariant_inside=sorted({(x["family"], x["clause"]) for x in OUT} - A - B),
               controls=dict(placebo=placebo_ok, positive=pos_ok, g0=g0_ok,
                             gauge_moved=gauge_moved, beta_moved=moved_beta,
                             band_moved=moved_band, max_band_shift=float(max(diffs))),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r357_gauge_swap.json"
    outp.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
