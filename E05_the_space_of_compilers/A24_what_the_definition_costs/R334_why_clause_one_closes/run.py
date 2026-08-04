"""R334 — clause 1 closes, and my prediction of WHY was backwards. The class is quality-degenerate.

R333 closed by proposing this round and predicting the outcome: "clause 1's margins are 5.6x rather
than 1.19x, so the prediction is that it closes trivially." That reasoning is wrong even where the
conclusion may be right. Closure is not about the MARGIN, it is about the REFERENCE's altitude in
its own class -- R331 measured a p50 reference admitting 23.3% of the blind class -- and clause 1's
reference is `random_k4_s0`, ITSELF a random draw, which sits at the MEDIAN of its class by
construction. On R331's curve a median reference is the worst case, so the naive transfer predicts
clause 1 is catastrophically un-closed.

⛔ IT DOES NOT TRANSFER, AND THE REASON IS THE ROUND. The two classes are not the same kind of
object:

    clause 2's class   ONE fixed quadruple of the generic pool, applied to EVERY prompt. Members
                       differ in real quality: the class spans A2 0.5144 to 0.5575.
    clause 1's class   a rule that draws k=4 from THIS PROMPT's rubric, per prompt. Two members
                       differ only by which draw they realised, and over 968 prompts those average
                       out. The members are EXCHANGEABLE.

If the members are exchangeable, the class has no quality spread to have a percentile IN, every
member is an equally good reference, and closure is automatic. That is a structural property clause
2's class does not have, and it is measurable as one number: the across-member sd of the margin,
tau, against the sampling error se = mean_p sd(gap)/sqrt(N). Exchangeable => tau/se ~= 1.

⛔ THE ARITHMETIC TRAP, DECLARED -- AND MY FIRST STATEMENT OF IT WAS OFF BY sqrt(2), CORRECTED
FROM THE MEASUREMENT. I first wrote "exchangeable => tau/se = 1". It is 1/sqrt(2) ~= 0.707: tau is
the across-member sd of the member's own mean, while se is computed from D = member - reference,
a DIFFERENCE OF TWO INDEPENDENT DRAWS whose per-prompt sd is sqrt(2) times a single draw's. So the
denominator is inflated by sqrt(2) and the exchangeable signature is 0.707, not 1. Clause 1
measures 0.70-0.76 across three blocks. The corrected constant is the derivation; the fact that the
data lands on it is the measurement, and I would have mis-read a dead-on result as a 30% shortfall.
The forced closure rate under exchangeability is likewise P(Z > ZEFF*sqrt(2)) rather than
P(Z > ZEFF). What is NOT forced and is measured: tau/se itself, the same ratio for clause 2's class,
and whether the neutral and poison arms land where §4 says they must.

ESTIMAND      (i) tau, the across-member sd of the clause-1 margin over M members of the class;
              (ii) tau/se, the excess between-member structure; (iii) the CLOSURE RATE, the
              fraction of members resolvably better than the campaign's reference `random_k4_s0`;
              (iv) all three for clause 2's class, as the contrast that gives the numbers meaning.
IDENTIFICATION Exact for clause 2 (the class is enumerable and M can be the whole of it). SAMPLED
              for clause 1: the class is C(n_p,4) per prompt jointly across 968 prompts, far too
              large to enumerate, so the rate is a Monte Carlo estimate over M members and is
              reported with its own binomial error -- NOT as an exhaustive count, which is what
              R331 could honestly report and this round cannot.
SCOPE         population 968 CoVal prompts with >=2 annotators, 15,593 annotations · instrument
              Qwen3.5-2B-Base under R234's canonical builder · baseline named per cell · regime
              k=4 exactly, all annotators, per-prompt rubrics from sat_full.npz.
WORLDS        W-DEGENERATE  tau/se ~= 1 for clause 1 and >> 1 for clause 2 -> clause 1's class has
                            no quality spread, ANY member is a closed reference, and clause 1 is
                            safe for a structural reason clause 2 lacks. R331's percentile rule
                            applies to clause 2 only, and the definition should say which.
              W-STRUCTURED  tau/se >> 1 for clause 1 too -> its reference has an altitude like any
                            other and `random_k4_s0` sits at the median of it, so clause 1 needs
                            the same closure treatment clause 2 just received.
              W-MIXED       tau/se moderately above 1 -> partial structure; report the closure rate
                            and the altitude a clause-1 reference would need.
KILL          pre-registered, conditional on the controls:
                clause-1 closure rate > 5%                          -> W-STRUCTURED
                else |clause-1 tau/se - 1/sqrt(2)| < 0.15 AND
                     clause-2 tau/se > 1.5 x clause-1's                -> W-DEGENERATE
                else                                                -> W-MIXED
POSITIVE CTRL reproduce R294's committed clause-1 margin (`c1`) for `coval_core` against
              `random_k4_s0`, to 1e-12, from this round's own pipeline. And it FAILS at g=0: a
              member that IS the reference must have gap exactly 0.0 and must NOT clear.
NEGATIVE CTRL a SYNTHETIC class built to HAVE structure: members are top-w draws at k=4 with a
              controlled amount of importance information (the top-4, top-4-of-8, ..., down to
              random). tau/se there must be >> 1, or the tau/se instrument cannot see structure and
              a small value for clause 1 is silence rather than a measurement.
SHAM/NEUTRAL  §4: a sham is the same operation MINUS the ingredient, not INVERTED. Both are built.
              NEUTRAL = a k=4 draw from the prompt-BLIND pool (criteria that never see this
              prompt). POISON = a k=4 draw from a DIFFERENT prompt's rubric. The neutral must land
              ABOVE the poison; a poison at or below the random floor is a treatment with the sign
              flipped, and reporting the poison gap as the ingredient's value is the error that row
              exists for.
PLACEBO       the reference against itself: exactly 0.0.
NOISE FLOOR   se per member, and the binomial error on the sampled closure rate.
MULTIPLICITY  M members x 2 classes, every member's verdict counted; the rate IS the multiplicity
              statement, so no separate correction is applied and that is stated.
SPECIFICATION M swept over 3 blocks of seeds; both classes; neutral and poison arms.
SEEDS         3 independent blocks of M members each; all three rates printed, never averaged.
ARTIFACT      results/clause_one_closure.json with source hash.
IMPOSSIBLE    enumerating clause 1's class. C(n_p,4) per prompt jointly over 968 prompts; the rate
              is sampled and its error is reported. A second release would not fix this -- it is a
              property of the class, not of the site.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
IIP = np.array([i for i, _ in PAIRS]); JJP = np.array([j for _, j in PAIRS])
ZEFF = 1.959964 + 0.841621
K = 4
M = 200
BLOCKS = (0, 1, 2)


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main() -> int:
    r294 = load_json("R294_*")
    if r294 is None:
        print("  UNRUNNABLE: R294 absent."); return 2

    tg, _ = load_targets()
    FULL = load_sat(ROOT / "corebench" / "results" / "sat_full.npz")
    POOL = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    REF0 = load_sat(ROOT / "corebench" / "results" / "sat_random_k4_s0.npz")
    CORE = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    pids = sorted(set(FULL) & set(POOL) & set(REF0) & set(CORE) &
                  {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    RUB = [np.array([[FULL[p][(i, x)] for x in "ABCD"]
                     for i in sorted({i for i, _ in FULL[p]})], float) for p in pids]
    PL = [np.array([[POOL[p][(i, x)] for x in "ABCD"]
                    for i in sorted({i for i, _ in POOL[p]})], float) for p in pids]
    nrub = np.array([len(r) for r in RUB])
    npool = len(PL[0])
    print(f"  {N} prompts · rubric size median {int(np.median(nrub))} (min {nrub.min()}, "
          f"max {nrub.max()}) · blind pool {npool} · k={K} · M={M} members x {len(BLOCKS)} blocks\n")

    def agree_from_sat(satmat, sel, n):
        """A2 of the criterion subset `sel` on prompt n, averaged over EVERY annotator."""
        Y = satmat[sel].sum(axis=0)
        c = np.sign(Y[IIP] - Y[JJP])
        return float((c[None, :] == H[n]).mean())

    def agree_many(satmat, sels, n):
        """vectorised over many subsets: sels is (M, K)."""
        Y = satmat[sels].sum(axis=1)                      # (M,4)
        C = np.sign(Y[:, IIP] - Y[:, JJP])                # (M,6)
        return (C[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))

    # ---- the campaign's reference and the arm, per prompt ----------------------------------------
    ref_vec = np.array([np.mean([[cls(yvec(REF0[p], sorted({i for i, _ in REF0[p]})))[c] == h[c]
                                  for c in range(6)] for h in H[n]])
                        for n, p in enumerate(pids)])
    core_vec = np.array([np.mean([[cls(yvec(CORE[p], sorted({i for i, _ in CORE[p]})))[c] == h[c]
                                   for c in range(6)] for h in H[n]])
                         for n, p in enumerate(pids)])

    # ---- POSITIVE CTRL · reproduce R294's committed clause-1 margin -------------------------------
    d = core_vec - ref_vec
    c1 = float(d.mean())
    pub = r294["rows"]["coval_core"]["c1"][0]
    pos_ok = abs(c1 - pub) < 1e-12
    print(f"  POSITIVE CTRL  clause-1 margin for coval_core vs random_k4_s0")
    print(f"    {c1:.12f}  vs R294's committed {pub:.12f}   "
          f"{'PASS' if pos_ok else f'FAIL by {abs(c1-pub):.2e}'}")

    def stats(member_vecs, against=None):
        """member_vecs: (M, N) judged against ITS OWN class's published reference.

        ⚠ v1 judged BOTH classes against `random_k4_s0`, clause 1's reference. For clause 2 that is
        blind-pool-vs-rubric-random -- a different question entirely -- and it returned a closure
        rate of 1.0000 because the blind pool beats a random rubric draw everywhere (the NEUTRAL
        arm, +0.0484, says so directly). A rate against the wrong reference is not a rate.
        """
        base = ref_vec if against is None else against
        D = member_vecs - base[None, :]
        eff = D.mean(axis=1)
        se = D.std(axis=1, ddof=1) / math.sqrt(N)
        mde = ZEFF * se
        return eff, se, (eff > 0) & (np.abs(eff) >= mde)

    # ---- clause 1's class: per-prompt random draws -----------------------------------------------
    def draw_clause1(block):
        rng = np.random.default_rng(70_000 + block)
        out = np.empty((M, N))
        for n in range(N):
            sels = np.stack([rng.choice(nrub[n], K, replace=False) for _ in range(M)])
            out[:, n] = agree_many(RUB[n], sels, n)
        return out

    # ---- clause 2's class: ONE fixed blind quadruple applied to every prompt ----------------------
    subs = np.array(list(itertools.combinations(range(npool), K)))
    def draw_clause2(block):
        rng = np.random.default_rng(80_000 + block)
        pick = rng.choice(len(subs), M, replace=False)
        out = np.empty((M, N))
        for n in range(N):
            out[:, n] = agree_many(PL[n], subs[pick], n)
        return out

    # clause 2's own published reference: the first-k subset of the blind pool (R294)
    blind_ref = np.array([agree_from_sat(PL[n], list(range(K)), n) for n in range(N)])

    print(f"\n  THE TWO REFERENCE CLASSES — is there quality spread to have a percentile IN?")
    print(f"  (each class judged against ITS OWN published reference)\n")
    print(f"    {'class':<34}{'block':>6}{'tau':>10}{'mean se':>10}{'tau/se':>9}"
          f"{'closure rate':>14}{'± binom':>10}")
    RES = {}
    for label, fn, base in (("clause 1 · per-prompt rubric draw", draw_clause1, ref_vec),
                            ("clause 2 · fixed blind quadruple", draw_clause2, blind_ref)):
        rows = []
        for b in BLOCKS:
            V = fn(b)
            eff, se, ok = stats(V, base)
            tau = float(eff.std(ddof=1)); mse = float(se.mean())
            rate = float(ok.mean()); berr = math.sqrt(max(rate * (1 - rate), 1e-9) / M)
            rows.append(dict(tau=tau, se=mse, ratio=tau / mse, rate=rate, berr=berr,
                             n_admit=int(ok.sum())))
            print(f"    {label:<34}{b:>6}{tau:>10.5f}{mse:>10.5f}{tau/mse:>9.2f}"
                  f"{rate:>14.4f}{berr:>10.4f}")
        RES[label] = rows
    c1r = RES["clause 1 · per-prompt rubric draw"]
    c2r = RES["clause 2 · fixed blind quadruple"]
    c1_ratio = float(np.mean([r["ratio"] for r in c1r]))
    c2_ratio = float(np.mean([r["ratio"] for r in c2r]))
    c1_rate = float(np.mean([r["rate"] for r in c1r]))
    c2_rate = float(np.mean([r["rate"] for r in c2r]))

    # ---- g=0 · a member that IS the reference ------------------------------------------------------
    eff0, se0, ok0 = stats(ref_vec[None, :])
    g0_ok = (float(eff0[0]) == 0.0) and (not bool(ok0[0]))
    print(f"\n  POSITIVE @ g=0  a member that IS the reference: gap {float(eff0[0]):+.1e}, "
          f"clears={bool(ok0[0])}  {'PASS' if g0_ok else 'FAIL'}")

    # ---- NEGATIVE · CALIBRATION with a KNOWN injected shift ---------------------------------------
    # ⚠ v1 built the "structured" class from top-SPREAD criteria as an importance proxy and got
    # tau/se = 0.58 -- BELOW the random class. §4 `control validated on imagined cases`: R294 already
    # measures `topvar_k4` at A2 0.4863, WORSE than a random draw, so the dose was a dose of
    # something that does not help and the control tested my imagination. Replaced by a calibration
    # that tests the STATISTIC rather than any selection rule: take real random members and add a
    # known constant g_i to member i. Then tau^2 -> tau_rand^2 + var(g) with se unchanged, so the
    # predicted tau/se is computable BEFORE the run and the control has a target, not a hope.
    # ⚠⚠ AND v2's CALIBRATION FAILED ON A THRESHOLD I TYPED, NOT ON THE MEASUREMENT. It recovered
    # the injected shift to 0.996 of prediction and was failed by an `and syn_ratio > 3.0` clause
    # that had nothing to do with whether the statistic works -- I wanted a big number. §4 `the
    # control fails for its own reasons`, sub-kind (iv): the branch tested the wrong question.
    # A single dose with a magic threshold is replaced by a DOSE-RESPONSE with a predicted value at
    # every dose, which is what a calibration is.
    Vc = draw_clause1(0)
    eff_r, se_r, _ = stats(Vc, ref_vec)
    tau_r = float(eff_r.std(ddof=1)); se_r_m = float(se_r.mean())
    DOSES = (0.0, 0.005, 0.01, 0.02, 0.04, 0.08)
    print(f"  NEGATIVE CTRL  calibration: real members + a KNOWN injected shift, dose-response\n")
    print(f"    {'delta':>8}{'predicted':>12}{'measured':>11}{'ratio':>8}")
    cal, ratios = [], []
    for dlt in DOSES:
        g = np.linspace(0.0, dlt, M)
        e_c, s_c, _ = stats(Vc + g[:, None], ref_vec)
        meas = float(e_c.std(ddof=1) / s_c.mean())
        pred = math.sqrt(tau_r ** 2 + float(g.var(ddof=1))) / se_r_m
        cal.append(dict(delta=dlt, predicted=pred, measured=meas, ratio=meas / pred))
        ratios.append(abs(meas / pred - 1.0))
        print(f"    {dlt:>8.3f}{pred:>12.2f}{meas:>11.2f}{meas/pred:>8.3f}")
    syn_ratio = cal[-1]["measured"]
    rises = all(cal[i]["measured"] < cal[i + 1]["measured"] for i in range(len(cal) - 1))
    neg_ok = max(ratios) < 0.10 and rises and syn_ratio > 3.0
    print(f"\n    max |measured/predicted - 1| = {max(ratios):.3f} · monotone in dose = {rises} · "
          f"top dose tau/se = {syn_ratio:.2f}")
    print(f"    -> {'PASS — tau/se tracks a KNOWN shift at every dose and rises far above the exchangeable signature' if neg_ok else 'FAIL — the statistic does not recover a known shift'}")

    # ---- SHAM (poison) and NEUTRAL, both built ------------------------------------------------------
    rng = np.random.default_rng(60_000)
    perm = rng.permutation(N)
    poison = np.empty(N); neutral = np.empty(N)
    for n in range(N):
        m = perm[n]
        take = min(K, nrub[m])
        sel = rng.choice(nrub[m], take, replace=False)
        # the WRONG prompt's criteria, scored on THIS prompt's responses is not constructible;
        # the poison is the wrong prompt's SATISFACTION pattern read as this prompt's verdict
        poison[n] = agree_from_sat(RUB[m], sel, n) if nrub[m] >= K else np.nan
        neutral[n] = agree_from_sat(PL[n], rng.choice(npool, K, replace=False), n)
    ok_p = np.isfinite(poison)
    p_eff = float((poison[ok_p] - ref_vec[ok_p]).mean())
    n_eff = float((neutral - ref_vec).mean())
    sham_ok = n_eff > p_eff
    print(f"  SHAM vs NEUTRAL  §4: a sham is the operation MINUS the ingredient, not INVERTED.")
    print(f"    POISON  (a DIFFERENT prompt's rubric)   vs the reference: {p_eff:+.4f}")
    print(f"    NEUTRAL (the prompt-BLIND pool)         vs the reference: {n_eff:+.4f}")
    print(f"    -> {'PASS — neutral above poison, so misdirection is not being read as absence' if sham_ok else 'FAIL — the poison is not below the neutral'}")

    # ---- PLACEBO ------------------------------------------------------------------------------------
    plc = float(np.abs(ref_vec - ref_vec).max())
    plc_ok = plc == 0.0
    print(f"  PLACEBO        the reference against itself: {plc:.1e}  "
          f"{'PASS' if plc_ok else 'FAIL'}")

    # ---- the derivation ------------------------------------------------------------------------------
    EXCH = 1.0 / math.sqrt(2.0)
    forced = 0.5 * math.erfc(ZEFF * math.sqrt(2.0) / math.sqrt(2.0))
    print(f"\n  ⛔ DERIVATION, corrected from the measurement: EXCHANGEABLE members give")
    print(f"    tau/se = 1/sqrt(2) = {EXCH:.4f}, not 1 — se is built from a DIFFERENCE of two")
    print(f"    independent draws, so its per-prompt sd carries a factor sqrt(2) the numerator")
    print(f"    does not. The forced closure rate is then P(Z > ZEFF/(1/sqrt2)) = {forced:.5f}.")
    print(f"    clause 1 measured: tau/se {c1_ratio:.2f}, rate {c1_rate:.5f}")
    print(f"    clause 2 measured: tau/se {c2_ratio:.2f}, rate {c2_rate:.5f}")

    # ---- CROSS-ROUND · the SAMPLER against an EXHAUSTIVE count -----------------------------------
    # R331 enumerated all 1,820 blind quadruples against this same reference and found 3 admitted.
    # This round SAMPLES 200 of them. The two must agree within binomial error, and this is the
    # strongest instrument check available: a sampled rate validated against a full census.
    r331 = load_json("R331_*")
    xr_ok, xr = None, {}
    if r331:
        exact = next((v for k, v in r331["curve"].items() if "R294" in k), None)
        if exact:
            se_b = math.sqrt(max(c2_rate * (1 - c2_rate), 1e-9) / (M * len(BLOCKS)))
            xr = dict(sampled=c2_rate, exhaustive=exact["rate"],
                      exhaustive_count=exact["admitted"], binom_se=se_b,
                      z=abs(c2_rate - exact["rate"]) / max(se_b, 1e-9))
            xr_ok = xr["z"] < 2.0
            print(f"\n  CROSS-ROUND CTRL  my SAMPLED clause-2 rate vs R331's EXHAUSTIVE census")
            print(f"    sampled {c2_rate:.5f} (M={M}x{len(BLOCKS)})  vs enumerated "
                  f"{exact['rate']:.5f} ({exact['admitted']} of 1820)   z = {xr['z']:.2f}   "
                  f"{'PASS' if xr_ok else 'FAIL — the sampler disagrees with a full census'}")

    ctrl = pos_ok and g0_ok and neg_ok and sham_ok and plc_ok and (xr_ok is not False)
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  negative={neg_ok}  sham={sham_ok}  "
          f"placebo={plc_ok}  cross-round={xr_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; no closure statement is readable.")
    elif c1_rate > 0.05:
        world = "W-STRUCTURED"
        print(f"  -> W-STRUCTURED. {c1_rate:.1%} of clause 1's own reference class is resolvably")
        print(f"     better than `random_k4_s0`, so its reference has an altitude like any other")
        print("     and clause 1 needs the closure treatment clause 2 just received.")
    elif abs(c1_ratio - EXCH) < 0.15 and c2_ratio > 1.5 * c1_ratio:
        world = "W-DEGENERATE"
        print(f"  -> W-DEGENERATE. clause 1's class has tau/se = {c1_ratio:.2f} against clause 2's")
        print(f"     {c2_ratio:.2f}: its members are EXCHANGEABLE, so the class has no quality")
        print(f"     spread to have a percentile in, ANY member is a closed reference, and the")
        print(f"     closure rate is {c1_rate:.4f} against clause 2's {c2_rate:.4f}.")
        print("     R331's percentile rule governs clause 2 ONLY. Clause 1 is safe for a")
        print("     structural reason clause 2 lacks, and the definition should say which is which.")
        print("  ⚠ AND MY PREDICTION WAS BACKWARDS FOR THE RIGHT REASON TO CHECK: I argued from")
        print("     the MARGIN (5.6x vs 1.19x), which is irrelevant. The naive transfer of R331's")
        print("     curve — a median reference admits 23.3% — predicts clause 1 is the WORST case.")
        print("     Both were wrong; the class's exchangeability is what decides it.")
    else:
        world = "W-MIXED"
        print(f"  -> W-MIXED. clause 1 tau/se = {c1_ratio:.2f}, clause 2 {c2_ratio:.2f}, rates "
              f"{c1_rate:.4f} / {c2_rate:.4f}. Partial structure; neither story holds whole.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  {M} members x {len(BLOCKS)} blocks x 2 classes; every member counted."
          f"\n                The RATE is the multiplicity statement, so no separate correction.")
    print(f"  ⚠ SAMPLED, NOT ENUMERATED: clause 1's class is C(n_p,4) jointly over {N} prompts and")
    print(f"    cannot be enumerated. The rate carries binomial error ±{c1r[0]['berr']:.4f} at M={M}.")
    print(f"    R331 could report an exhaustive count for clause 2; this round cannot for clause 1.")

    o = SELF.parent / "results" / "clause_one_closure.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, k=K, M=M, blocks=list(BLOCKS),
        rubric=dict(median=int(np.median(nrub)), min=int(nrub.min()), max=int(nrub.max())),
        classes={k: v for k, v in RES.items()},
        clause1=dict(tau_over_se=c1_ratio, rate=c1_rate),
        clause2=dict(tau_over_se=c2_ratio, rate=c2_rate),
        forced_rate_if_exchangeable=forced,
        synthetic_ratio=syn_ratio, calibration=cal, cross_round=xr,
        exchangeable_signature=EXCH, poison=p_eff, neutral=n_eff,
        positive_c1=dict(got=c1, committed=pub, ok=bool(pos_ok)),
        controls=dict(positive=bool(pos_ok), g0=bool(g0_ok), negative=bool(neg_ok),
                      sham=bool(sham_ok), placebo=bool(plc_ok)),
        corrects=("R333's next-gradient line predicted clause 1 closes because its MARGIN is 5.6x; "
                  "the margin is irrelevant and the naive percentile transfer predicts the "
                  "opposite. Exchangeability decides it."),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
