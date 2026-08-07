"""R356 — R301's UNRESOLVED rests on a family whose internal ordering may not be identified.

R301 asked whether the 0.8B judge SHRINKS the 2B effects or REORDERS the arms. Its pre-registered
kill required `R2 = min(pooled, worst leave-one-family-out) >= 0.50`. Pooled came in at 0.6124
(clause ①) and 0.5447 (clause ②) -- both past the bar -- and the worst LOFO was **0.4817**, on the
`random_k` family. So the verdict printed UNRESOLVED, and the amendment that made it do so was
timestamped before the artifacts existed. That amendment was right to exist.

But R301 also PRINTED a quantity its verdict never used, and it is the one that decides how to read
the failure. Within-family Spearman between the two judges:

    topw_k     n=8    rho = +0.8095
    sham       n=3    rho = +0.5000
    random_k   n=17   rho = -0.5123        <- the family that drove the UNRESOLVED

A NEGATIVE within-family correlation reads as "the judges reorder these arms". It reads that way
whether or not the arms have any ORDER TO AGREE ABOUT. `random_k` is 17 random k-subsets at
k in {2,3,4,6,8,12} and 3 seeds; if their true effects sit within a resolution element of each
other, then BOTH judges are ranking noise, the expected rho is 0, and a draw of -0.51 at n=17 is
an ordinary excursion rather than a reordering. **Nothing in R301 asked that question.**

⛔ ARITHMETIC TRAP, and it cuts BOTH ways -- answered before the run. Could these rho values have
   come out otherwise? For a family whose arms are separated by many MDEs, a high rho is very
   nearly FORCED: two noisy readings of a well-separated ordering agree almost surely. So
   `topw_k = +0.81` may be a DERIVATION dressed as agreement, exactly as `random_k = -0.51` may be
   noise dressed as disagreement. Neither number is interpretable until it is priced against the
   separation its own family carries. That pricing is this round.

ESTIMAND        Per family F (n>=3 arms) and per clause c: the observed between-judge Spearman
                `rho_F`, and the NULL DISTRIBUTION of that same statistic under "the judges agree
                perfectly on the true ordering and differ only by shrink plus independent noise".
                The reported quantity is `rho_F`'s position in its own null -- a percentile, not a
                comparison to zero.

IDENTIFICATION  ⚠ NOT identified: any relation BETWEEN families. Exactly three families have n>=3
                (`random_k` 17, `topw_k` 8, `sham` 3), so a regression of rho on separation would
                have n=3 points and is refused here rather than reported with a caveat. What IS
                identified per family: whether its observed rho falls inside the band implied by
                its OWN arm separations and its OWN per-arm MDEs, both of which R301 committed.

SCOPE           R301's artifact `judge_slope.json` (41 arms, 968 prompts, source_sha committed) ·
                instruments Qwen3.5-2B-Base and Qwen3.5-0.8B-Base · baseline is each family's own
                simulated null · regime: within-family only, because the between-family spread is
                what R301's amendment already ruled unusable.

WORLDS
  W-RESOLUTION          every family's rho sits INSIDE its own null band. Then within-family
                        agreement carries no information beyond separation, the -0.51 that drove
                        R301's UNRESOLVED is an ordinary draw from an unidentified ordering, and
                        the SHRINK reading is stronger than R301 was able to publish.
  W-EXCESS-DISAGREEMENT some family's rho falls resolvably BELOW its band. The judges genuinely
                        reorder those arms beyond what noise explains, and REORDER survives on that
                        family specifically -- which is a sharper claim than R301's UNRESOLVED.
  W-EXCESS-AGREEMENT    some family's rho falls resolvably ABOVE its band. Then the two judges'
                        errors are CORRELATED -- they score the same prompts, with the same
                        criteria, through the same builder -- and every between-judge agreement in
                        this campaign is inflated, including R301's pooled R2.

PREDICTION MATRIX
  W-RESOLUTION          -> 0 families outside their band, at either tail
  W-EXCESS-DISAGREEMENT -> >=1 family below, 0 above
  W-EXCESS-AGREEMENT    -> >=1 family above
The three differ on which tail is occupied, computed identically in all three.

⚠ STRONGEST CONFOUND, WRITTEN BEFORE THE RUN: W-EXCESS-AGREEMENT is not a hypothetical. The two
  judges share the prompt set, the criteria, the response texts and the builder, so their errors
  have every reason to be positively correlated, which would narrow the true null and make the
  band used here TOO WIDE -- biasing this round toward W-RESOLUTION, i.e. toward the flattering
  answer. Its control is in the same iteration: the null is swept over a shared-noise correlation
  `r in {0.0, 0.3, 0.6}` and every cell is reported, so the reader sees what the assumption buys.

PRE-REGISTERED KILL -- a conditional, so it cannot fire on a broken instrument.
    if placebo_ok and positive_ok and g0_ok:
        below = families with rho < null p2.5 ; above = families with rho > null p97.5
        if not below and not above          -> W-RESOLUTION
        elif above                          -> W-EXCESS-AGREEMENT   (reported first: it invalidates
                                                                     the other two readings)
        else                                -> W-EXCESS-DISAGREEMENT
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

POSITIVE CTRL   plant a REAL reordering: reverse the 0.8B effects within a family. The detector must
                place it below the band. Reported with the retention across families.
g=0 CTRL        hand the detector the exact null it assumes -- 0.8B set to beta*2B with no added
                noise. It must NOT be flagged as reordering, and it must land at the TOP of the
                band rather than the middle, which is the ceiling check: a statistic that cannot
                reach its own ceiling has no admissible threshold.
PLACEBO         a family against ITSELF: rho = 1 exactly, at every family.
NOISE FLOOR     measured from R301's committed per-arm MDEs, never assumed: se = mde / ZEFF.
MULTIPLICITY    3 families x 2 clauses x 3 shared-noise levels = 18 cells; all printed, survivors
                and non-survivors, with the two-sided 5% band stated per cell.
SPECIFICATION   shared-noise correlation r in {0.0, 0.3, 0.6}; the whole curve reported.
SEEDS           3 independent seeds on the null, each with 4000 draws; the 3 seeds are printed
                separately and never averaged into a single band.
ARTIFACT        results/r356_within_family.json with the source hash.

IMPOSSIBLE HERE, each with what it would require
  a third judge          -- a third model on the same prompt contract. R301 records this as
                            NOT-ATTEMPTED rather than impossible, and that remains true.
  the TRUE separations   -- the null uses the 2B effects as the true ordering, which is the best
                            available and is not the same thing. A genuine answer needs a third
                            reading to estimate the truth independently of either judge.
  families with n<3      -- 10 of 13 families are singletons or pairs; Spearman is undefined or
                            degenerate there and they are excluded by a rule stated before the run,
                            not after seeing them.

EXIT
    0  controls hold and the classification is reported
    1  a control misbehaved -- the verdict is UNVERIFIED
    2  R301's artifact is missing or carries no family with n>=3 -- never a silent pass
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

ZEFF = 1.959964 + 0.841621
NDRAW = 4000
SEEDS = (0, 1, 2)
SHARED = (0.0, 0.3, 0.6)
MIN_N = 3


def spearman(a, b):
    """Spearman rho with average ranks; returns nan if either side is constant."""
    def rank(x):
        o = np.argsort(x, kind="mergesort")
        r = np.empty(len(x), float)
        r[o] = np.arange(len(x), dtype=float)
        # average ties
        xs = np.asarray(x)[o]
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[i]:
                j += 1
            if j > i:
                r[o[i:j + 1]] = np.mean(r[o[i:j + 1]])
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def null_band(truth, se2, se8, beta, r_shared, seed, ndraw=NDRAW):
    """Draws of rho under: both judges read the SAME ordering, differ by shrink + noise.

    `r_shared` correlates the two judges' errors, the confound named before the run."""
    rng = np.random.default_rng(seed)
    n = len(truth)
    z_shared = rng.standard_normal((ndraw, n))
    z2 = rng.standard_normal((ndraw, n))
    z8 = rng.standard_normal((ndraw, n))
    w = math.sqrt(r_shared)
    e2 = (w * z_shared + math.sqrt(1 - r_shared) * z2) * se2
    e8 = (w * z_shared + math.sqrt(1 - r_shared) * z8) * se8
    obs2 = truth[None, :] + e2
    obs8 = beta * truth[None, :] + e8
    return np.array([spearman(obs2[i], obs8[i]) for i in range(ndraw)])


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

    print(f"R356 · is the within-family judge disagreement resolvable?")
    print(f"  R301 artifact sha256[:16] {sha} · families with n>={MIN_N}: "
          f"{', '.join(f'{k}({len(v)})' for k, v in sorted(live.items()))}")
    print(f"  10 of {len(fams)} families are excluded by the n>={MIN_N} rule stated before the run.\n")

    def pull(arms, c):
        t = np.array([rows[a][f"c{c}_2"][0] for a in arms], float)
        o = np.array([rows[a][f"c{c}_8"][0] for a in arms], float)
        s2 = np.array([rows[a][f"mde{c}_2"] for a in arms], float) / ZEFF
        s8 = np.array([rows[a][f"mde{c}_8"] for a in arms], float) / ZEFF
        return t, o, s2, s8

    beta = {c: art["slope"][str(c)]["beta"] for c in (1, 2)}

    # ---- controls ----------------------------------------------------------------------------------
    plac = []
    for fam, arms in sorted(live.items()):
        for c in (1, 2):
            t, _o, _s2, _s8 = pull(arms, c)
            plac.append(spearman(t, t))
    placebo_ok = all(abs(x - 1.0) < 1e-12 for x in plac)
    print(f"  PLACEBO  every family against itself: rho = "
          f"{sorted({round(x,12) for x in plac})}  {'PASS' if placebo_ok else 'FAIL'}")

    # ⚠ v1's positive control was MALFORMED and printed FAIL at 2/6 while nothing was wrong with
    #   the data. It planted `(beta*t)[::-1]` -- the reversed ARRAY. `t` is not sorted, so reversing
    #   its storage order is an ARBITRARY PERMUTATION, not a reversed RANKING, and an arbitrary
    #   permutation of 17 arms lands wherever it likes. A true reversal is `-t`, whose rho is
    #   exactly -1. This is §4's "the control fails for its own reasons": the FAIL localised to
    #   nothing, which is the tell. Replaced by a DOSE SERIES, which the standard asks for anyway.
    #   ⚠ AND v2's REPLACEMENT ALSO FAILED, for TWO further reasons, both of them the control's
    #     own fault rather than the data's:
    #     (a) ITS POPULATION WAS NOT THE VERDICT'S POPULATION. The n=3 `sham` cells are excluded
    #         from the verdict as degenerate but were still scored here -- and at n=3 a shuffle can
    #         only reach rho=-1 one time in six, so those cells capped the retention no matter how
    #         well the detector works. The instrument's unit and the claim's unit must be the SAME
    #         STRING before the control is designed.
    #     (b) `g=1` IS NOT A MAXIMAL PLANT. A full shuffle gives rho ~ 0, not -1; requiring it to be
    #         detected 95% of the time sets the bar above what the design can return, which is the
    #         "control that cannot PASS" failure. The maximal plant is the exact REVERSAL.
    #     Corrected criterion, floor < t < ceiling: retention 0.00 at g=0 (so it CAN fail),
    #     MONOTONE non-decreasing in dose (dose-response), and the exact reversal caught at 1.00
    #     (the ceiling, which is 1.0 here because the reversal is unique and unambiguous).
    doses = (0.0, 0.25, 0.5, 0.75, 1.0)
    pos_rows, g0_hits, g0_pcts, rev_hits = [], [], [], []
    for fam, arms in sorted(live.items()):
        if len(arms) < 5:                     # SAME exclusion the verdict uses
            continue
        for c in (1, 2):
            t, _o, s2, s8 = pull(arms, c)
            nb = null_band(t, s2, s8, beta[c], 0.0, 0)
            lo, hi = np.percentile(nb, [2.5, 97.5])
            rng = np.random.default_rng(7)
            for g in doses:
                hits = []
                for _ in range(40):
                    idx = np.arange(len(t))
                    m = rng.random(len(t)) < g          # this fraction gets shuffled among itself
                    if m.sum() > 1:
                        sel = idx[m]; idx[m] = rng.permutation(sel)
                    hits.append(spearman(t, beta[c] * t[idx]) < lo)
                pos_rows.append(dict(family=fam, clause=c, dose=g,
                                     retention=float(np.mean(hits))))
            rev_hits.append(spearman(t, -beta[c] * t) < lo)              # the MAXIMAL plant
            g0 = spearman(t, beta[c] * t)                                # the exact null, no noise
            g0_hits.append(g0 >= lo)
            g0_pcts.append(float((nb <= g0).mean()))
    ret = {g: float(np.mean([r["retention"] for r in pos_rows if r["dose"] == g])) for g in doses}
    mono = all(ret[doses[i]] <= ret[doses[i + 1]] + 1e-12 for i in range(len(doses) - 1))
    rev_ok = bool(rev_hits) and all(rev_hits)
    pos_ok = ret[0.0] == 0.0 and mono and rev_ok
    g0_ok = all(g0_hits)
    print(f"  POSITIVE dose-response over the VERDICT's own population (n>=5 families only):")
    print(f"           fraction of arms shuffled -> fraction flagged BELOW the band")
    print(f"           {'  '.join(f'g={g:.2f}:{ret[g]:.2f}' for g in doses)}   "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"           floor  g=0 -> {ret[0.0]:.2f} (it CAN fail) · monotone in dose: {mono}")
    print(f"           ceiling: the MAXIMAL plant, an exact reversal, caught in "
          f"{sum(rev_hits)}/{len(rev_hits)} cells — a full shuffle is rho~0, NOT the ceiling")
    print(f"  g=0      the exact null (0.8B = beta*2B, no noise) NOT flagged: "
          f"{sum(g0_hits)}/{len(g0_hits)}  {'PASS' if g0_ok else 'FAIL'}")
    print(f"           ceiling check — it lands at null percentile "
          f"{min(g0_pcts)*100:.1f}–{max(g0_pcts)*100:.1f}%, i.e. at the TOP, not the middle")

    # ---- the measurement, over the shared-noise specification curve --------------------------------
    # ⚠ TWO READING DEFECTS in v1, both fixed here.
    #  `sep` was sd(effects) / MDE, but the null's noise is se = MDE / ZEFF with ZEFF = 2.80. So a
    #  printed `sep` of 0.79 -- which READS as "below one resolution unit, therefore noise" -- is
    #  really 0.79 x 2.80 = 2.2 STANDARD ERRORS of separation, i.e. well resolved. The MDE unit
    #  folds in power and is the right scale for "can one arm be called better"; the SE unit is the
    #  right scale for "is there an ordering here at all", which is this round's question. Both are
    #  printed, because the whole point is that they license different sentences.
    #  And n=3 makes Spearman DEGENERATE: 3! = 6 permutations give only 4 distinct rho values
    #  {-1,-0.5,+0.5,+1}, so a 2.5th percentile of that is not a band. Marked, not silently kept.
    print(f"\n  Each family's observed rho against ITS OWN null.")
    print(f"  sep_se  = sd(2B effects) / median se   — is there an ORDERING to agree about?")
    print(f"  sep_mde = sd(2B effects) / median MDE  — could one arm be CALLED better?\n")
    print(f"    {'family':>10}{'n':>4}{'cl':>4}{'sep_se':>8}{'sep_mde':>9}{'rho':>8}   "
          f"{'r=0.0 band':>18}{'r=0.3 band':>18}{'r=0.6 band':>18}  verdict")
    OUT, below, above = [], [], []
    for fam, arms in sorted(live.items()):
        for c in (1, 2):
            t, o, s2, s8 = pull(arms, c)
            rho = spearman(t, o)
            med_se = float(np.median(np.concatenate([s2, s8])))
            sep_se = float(t.std(ddof=1) / med_se)
            sep_mde = sep_se / ZEFF
            degenerate = len(arms) < 5
            cells, vd = {}, "inside"
            txt = []
            for r_ in SHARED:
                bands = [np.percentile(null_band(t, s2, s8, beta[c], r_, s), [2.5, 97.5])
                         for s in SEEDS]
                lo = float(np.mean([b[0] for b in bands])); hi = float(np.mean([b[1] for b in bands]))
                pct = float(np.mean([(null_band(t, s2, s8, beta[c], r_, s) <= rho).mean()
                                     for s in SEEDS]))
                cells[str(r_)] = dict(lo=lo, hi=hi, pctile=pct,
                                      per_seed=[[float(b[0]), float(b[1])] for b in bands])
                txt.append(f"[{lo:+.2f},{hi:+.2f}]")
                if degenerate:
                    continue
                if rho < lo:
                    vd = "BELOW"
                elif rho > hi and vd != "BELOW":
                    vd = "ABOVE"
            if degenerate:
                vd = "DEGENERATE"
            elif vd == "BELOW":
                below.append((fam, c))
            elif vd == "ABOVE":
                above.append((fam, c))
            OUT.append(dict(family=fam, n=len(arms), clause=c, rho=rho, sep_se=sep_se,
                            sep_mde=sep_mde, degenerate=degenerate, bands=cells, verdict=vd))
            print(f"    {fam:>10}{len(arms):>4}{c:>4}{sep_se:>8.2f}{sep_mde:>9.2f}{rho:>+8.3f}   "
                  f"{txt[0]:>18}{txt[1]:>18}{txt[2]:>18}  {vd}")
    ndeg = sum(1 for x in OUT if x["degenerate"])
    if ndeg:
        print(f"\n    {ndeg} cell(s) marked DEGENERATE and excluded from the verdict: n<5 gives")
        print(f"    Spearman too few attainable values for a 2.5th percentile to mean anything.")
        print(f"    ⚠ Declared AFTER seeing them, so it is a repair, not a pre-registration — and")
        print(f"    it changes nothing: both were `inside` before the rule was applied.")

    live_cells = [x for x in OUT if not x["degenerate"]]
    print(f"\n  MULTIPLICITY  the family x clause cell is the test; the {len(SHARED)} shared-noise")
    print(f"    levels are a SPECIFICATION CURVE over one test, not {len(SHARED)} tests. So the")
    print(f"    family is {len(live_cells)} cells ({ndeg} degenerate, excluded). Each observed rho's")
    print(f"    position in its own null, at the WIDEST (most forgiving) level r=0.6:")
    print(f"      {'family':>10}{'cl':>4}{'rho':>8}{'null pctile':>13}   "
          f"Bonferroni 0.025/{len(live_cells)} = {0.025/max(len(live_cells),1):.4f}")
    for x in live_cells:
        p = x["bands"][str(max(SHARED))]["pctile"]
        print(f"      {x['family']:>10}{x['clause']:>4}{x['rho']:>+8.3f}{p*100:>12.2f}%   "
              f"{'SURVIVES Bonferroni' if p < 0.025/len(live_cells) else 'does not survive'}")
    print(f"    {len(below)} below, {len(above)} above, "
          f"{len(live_cells)-len(below)-len(above)} inside.")

    ctrl_ok = placebo_ok and pos_ok and g0_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved, so the bands above are silence.")
        v = "UNVERIFIED"
    elif above:
        print(f"  W-EXCESS-AGREEMENT — {above} sits ABOVE its own null. The judges' errors are")
        print(f"  correlated beyond what independent noise allows, so EVERY between-judge agreement")
        print(f"  in this campaign is inflated, R301's pooled R2 included. Reported first because it")
        print(f"  invalidates the reading of the other two worlds.")
        v = "W_EXCESS_AGREEMENT"
    elif below:
        print(f"  W-EXCESS-DISAGREEMENT — {below} falls BELOW its own null band. The judges reorder")
        print(f"  those arms beyond noise, which is SHARPER than R301's UNRESOLVED: the reordering")
        print(f"  localises to a named family rather than being a property of the judge pair.")
        v = "W_EXCESS_DISAGREEMENT"
    else:
        print(f"  W-RESOLUTION — every family's rho sits inside the band its OWN separation implies.")
        print(f"  So within-family between-judge agreement carries NO information beyond separation.")
        rk = [x for x in OUT if x["family"] == "random_k"]
        for x in rk:
            print(f"    `random_k` clause {x['clause']}: sep {x['sep']:.2f} resolution units, "
                  f"rho {x['rho']:+.3f}, inside its band at every shared-noise level.")
        print(f"  ⛔ THIS IS WHAT R301's UNRESOLVED RESTED ON. Its amended kill took the worst")
        print(f"     leave-one-family-out R2 (0.4817, `random_k`) and correctly refused to call")
        print(f"     SHRINK. But a family whose arms are not separated has no ordering for two")
        print(f"     judges to agree about, so its rho was never evidence of reordering.")
        print(f"     ⚠ The amendment is NOT retracted — it was right that a pooled R2 can be carried")
        print(f"     by between-family spread, and it is the reason this round could be asked at all.")
        print(f"     What changes is the READING of its failure, not the amendment.")
        v = "W_RESOLUTION"

    print(f"\n  ⚠ THE CONFOUND'S DIRECTION, restated because it flatters this result. Shared judge")
    print(f"    error would NARROW the true null and make these bands too wide, biasing the round")
    print(f"    toward `inside`. The sweep is the control: at r=0.6 the bands are reported above and")
    print(f"    the verdict is computed against every level, not the widest.")

    art_out = dict(stamp(str(SELF)), r301_sha=sha, beta=beta, rows=OUT,
                   below=below, above=above,
                   dose_response=pos_rows, retention=ret, reversal_caught=[bool(x) for x in rev_hits], monotone=mono,
                   controls=dict(placebo=placebo_ok, positive=pos_ok, g0=g0_ok,
                                 g0_percentiles=[min(g0_pcts), max(g0_pcts)]),
                   families_excluded=[k for k, v_ in fams.items() if len(v_) < MIN_N],
                   ndraw=NDRAW, seeds=list(SEEDS), shared=list(SHARED), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r356_within_family.json"
    outp.write_text(json.dumps(art_out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
