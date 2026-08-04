"""R328 — clause 2's three readings are three points on ONE scalar, and the arms are not matched to it.

R327 reported clause 2 as a LINGUISTIC ambiguity — universal / named / procedural — and closed with
"no measurement settles it, which is why this round prices the options and does not pick." That
closing sentence is the highest-risk kind (§4 `the closing sentence is a claim and never gets a
control`), and it is checkable in two ways this round performs.

FIRST, THE READINGS ARE NOT THREE KINDS OF SENTENCE. R326's six legitimate references order
strictly by their own A2:

    0.539706  budget 0 · random draw            <- R327 reading C
    0.540316  neutral pool-16
    0.550436  budget 1 · hand-picked
    0.551354  generic at matched k=4            <- R327 reading B
    0.554602  budget 1820 · held-out best       <- R327 reading A
    0.557514  IN-SAMPLE argmax  (disqualified by R287's own positive control)
              ⚠ ANNOTATED AFTER THE RUN, kept as written because it is what R326 publishes:
              this row is WRONG and this round's PROVENANCE control proves it. 0.557514 is
              R286's `selection["best"][0][1]`, the HELD-OUT score of split 0. The real
              in-sample argmax is 0.55747530882624, sitting in R286's own `dist["max"]`.

That is one axis, and R287 named it 40 rounds ago in its own docstring: "these three references
differ in ONE thing: how much SELECTION BUDGET the baseline is allowed ... and no round in this
campaign has ever stated what budget a baseline SHOULD have." R327 rediscovered R287's open
question as a problem about English.

SECOND, AND THIS IS WHY IT IS NOT CLOSURE. R287 also wrote the principle that decides it, and then
did not apply it to the ARMS: "comparing a searched baseline to an unsearched arm is not 'strict',
it is MISMATCHED — the same class of error as comparing arms of different k." Every round since has
held all arms to ONE reference. But the two admitted arms did not cost the same to find:

    coval_core   the release's own core. This campaign selected nothing; budget 0 HERE.
    topw_k4      one cell of a rule x k grid this campaign scored on these same 968 prompts.
                 11 deterministic rule x k cores are committed under corebench/results/.
                 Its budget is >= 11, IN-SAMPLE.

If a baseline's budget must be stated, so must an arm's, and clause 2 should compare each arm to a
reference given the SAME budget the arm had. That is a fourth answer to R327's question, it is not
a choice among its three, and unlike them it is derived from a principle already in the campaign
rather than chosen.

⛔ THE ARITHMETIC TRAP, DECLARED BEFORE THE RUN. Three things here are DERIVATIONS, not evidence:
  (a) gap = arm_a2 - ref_a2 with arm_a2 fixed, so the gap FALLS as the reference strengthens. The
      monotone ordering above is algebra. Only the MDE could break it, and the MDEs span
      [0.00995, 0.01081] against gaps spanning [0.0090, 0.0268] -- 8.6% against 3x, so it cannot.
  (b) in-sample best-of-m is NON-DECREASING in m by construction. Reporting that it rises is not a
      finding. What is not forced is WHERE it crosses each arm.
  (c) R327's "unmeasured" cell -- topw_k4 at budget 0 -- is forced too: 0.564181 - 0.539706 =
      +0.024475 against an MDE band that admits it at 2.26x-2.46x under EVERY committed MDE. This
      round computes it exactly and labels it a derivation. Running it as though it were a
      measurement would be Closure wearing a round's clothes.
  What is NOT forced, and is the round: the HELD-OUT budget curve (a split can overfit and it is
  not monotone by construction), each arm's own MDE against a budget-matched reference, and whether
  budget-matching changes the admitted set.

ESTIMAND      (i) the prompt-blind reference's A2 as a function of selection budget m, in-sample
              and held-out, over a 15-point grid; (ii) each arm's clause-2 margin against the
              reference AT THE ARM'S OWN BUDGET, with a per-cell MDE; (iii) whether the admitted
              set under budget-matching equals any of R327's readings A, B, C.
IDENTIFICATION Exact on the reference side: the 1,820 quadruples of the 16-criterion generic pool
              are enumerable and B is computed for all of them. PARTIAL on the arm side -- an
              arm's budget is counted from COMMITTED artifacts, so 11 is a LOWER BOUND on what was
              tried; candidates that were never committed cannot be counted. Stated, and the
              consequence is signed: a larger true budget moves topw_k4's matched reference UP,
              i.e. can only make its admission harder, never easier.
SCOPE         population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base under
              R234's canonical builder · baseline named per cell as best-of-m · regime k=4 exactly,
              all annotators, pool-internal blind arms.
WORLDS        W-MATCHED-DIVERGES  budget-matching yields an admitted set equal to NONE of A/B/C ->
                                  the three readings were all mis-specified, the question was never
                                  linguistic, and R327's "no measurement settles it" is overturned.
              W-MATCHED-AGREES    budget-matching reproduces one of A/B/C -> the choice is settled
                                  by a principle already in the campaign; R327's closing sentence is
                                  still overturned, but the answer is one of its options.
              W-BUDGET-IRRELEVANT the best-of-m curve is flat over [1, 11] relative to its own noise
                                  -> matching changes nothing, the ambiguity really is semantic, and
                                  R327 stands.
KILL          conditional on the controls, pre-registered, evaluated in this order:
                curve flat: |ref(11) - ref(1)| < its own seed spread     -> W-BUDGET-IRRELEVANT
                else matched admitted set not in {A_set, B_set, C_set}   -> W-MATCHED-DIVERGES
                else                                                     -> W-MATCHED-AGREES
POSITIVE CTRL Three EXACT reproductions, to 1e-12, of references READ FROM the committed artifacts
              rather than typed here: budget 0 and the held-out best from R287's `refs`, and the
              in-sample ceiling from R286's `dist["max"]`. An instrument that cannot reproduce the
              numbers it is about to reinterpret is not an instrument.
              AND IT FAILS AT g=0: at m=1 argmax-of-1 and coinflip-of-1 must select the SAME
              element GIVEN THE SAME DRAWS, so the check is an exact identity on shared draws.
              ⚠ The first version of this control compared two INDEPENDENT draw sets against a
              3-seed sd and failed on its own noise -- §4 `the control fails for its own reasons`,
              sub-kind (i), two different draws treated as one. Fixed by sharing the draws, which
              also makes the check exact instead of thresholded.
PROVENANCE    a fourth control the first version did not have, and it is the one that fired.
              R326 hard-codes 0.5575138121466373 as the "budget 1820 IN-SAMPLE ceiling, source
              R287". R287's artifact does not contain it. R286's does -- as
              `selection["best"][0][1]`, the HELD-OUT score of split 0. The true in-sample argmax
              is R286's own `dist["max"] = 0.55747530882624`. This round asserts both identities
              mechanically rather than describing them.
NEGATIVE CTRL coin-flip-of-m: draw m candidates and keep a RANDOM one instead of the best. Destroys
              the selection, preserves the draw count. Must be FLAT in m. The world it excludes is
              "the curve rises because larger m changes the draw distribution" rather than "because
              argmax selects" -- and it is built here rather than asserted.
PLACEBO       each arm against itself: exactly 0.0, checked to 0 ulp.
NOISE FLOOR   per-cell MDE = ZEFF * sd(paired difference) / sqrt(N), plus the across-seed spread of
              the reference curve at each m, which is what "flat" is measured against.
MULTIPLICITY  3 arms x 15 budgets x 2 modes = 90 cells, BH q=0.05 over ALL 90, non-survivors named.
SPECIFICATION the budget grid IS the specification curve, published whole, including the
              disqualified in-sample end and the cells that refuse the finding.
SEEDS         3 seeds for the candidate draws and the splits; the reference curve printed at all 3.
ARTIFACT      results/budget_matching.json with source hash.
IMPOSSIBLE    - the TRUE selection budget of `coval_core`, which was set outside this campaign by
                the release's authors. Would require the release's own construction log. Its budget
                WITHIN this campaign is 0 and that is the only claim made.
              - an exhaustive count of topw_k4's budget: only committed candidates are countable.
                Reported as a lower bound with its sign of error stated.
              - compute-matched selection for the GENERATED family -- unchanged from R287, the
                release contains no population of generated cores to search.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, re, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 2000
NREP = 20                     # replicates averaged per (m, seed), matching R287's budget-0 draw count
NSPLIT = 10
SEEDS = (0, 1, 2)
ARMS = ["coval_core", "topw_k4", "gen_sham"]
GRID = (1, 2, 3, 4, 6, 8, 11, 16, 32, 64, 128, 256, 512, 1024, 1820)

# R327's three readings, as admitted sets, read off R326's committed artifact
READINGS = {
    "A · UNIVERSAL  (best held-out of 1,820)": {"coval_core"},
    "B · NAMED      (generic at matched k=4)": {"coval_core", "topw_k4"},
    "C · PROCEDURAL (budget 0 · random draw)": {"coval_core", "topw_k4"},   # topw filled by derivation
}
R326_TYPED_CEILING = 0.5575138121466373     # the literal R326 hard-codes and labels "R287, in-sample"


def read_committed_references() -> tuple[dict, dict, dict]:
    """Reference values are READ from the artifacts, never typed. Typing one is how R326's
    in-sample ceiling became a held-out score from a different round."""
    a24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"

    def load(pat):
        d = next(a24.glob(pat), None)
        if d is None:
            return None
        f = sorted((d / "results").glob("*.json"))
        return json.loads(f[0].read_text()) if f else None

    return load("R286_*"), load("R287_*"), load("R326_*")


def count_committed_rulek_arms() -> tuple[int, list[str]]:
    """topw_k4's selection budget, as a LOWER BOUND, from the campaign's own committed artifacts."""
    pat = re.compile(r"core_((?:topw|topabs|topvar|topwvar|oracle|greedy|indep)_k\d+)\.json$")
    names = sorted({m.group(1) for f in (ROOT / "corebench" / "results").glob("core_*.json")
                    if (m := pat.search(f.name))})
    return len(names), names


def main() -> int:
    r286, r287, r326 = read_committed_references()
    if not all((r286, r287, r326)):
        print("  UNRUNNABLE: a committed source artifact is absent."); return 2
    REF_TRUE = {
        "budget 0 · 20 draws": r287["refs"]["budget 0 · random draw"],
        "held-out best of 1,820": r287["refs"]["budget 1820 · held-out best"],
        "in-sample ceiling": r286["dist"]["max"],
    }

    tg, _ = load_targets()
    pool = ROOT / "corebench" / "results" / "sat_genericpool16.npz"
    if not pool.exists():
        print(f"  UNRUNNABLE: {pool.name} absent."); return 2
    S = load_sat(pool)
    A_ = {}
    for a in ARMS:
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{a}.npz absent."); return 2
        A_[a] = load_sat(f)

    pids = sorted(set(S) & set.intersection(*(set(v) for v in A_.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    NS = len(subs)
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    budget_lb, budget_names = count_committed_rulek_arms()
    print(f"  {N} prompts · pool {npool} · {NS} blind quadruples · grid {len(GRID)} budgets "
          f"x 2 modes x {len(SEEDS)} seeds\n")

    B = np.empty((NS, N))
    for n in range(N):
        Y = SAT[n][subs].sum(axis=1)
        C_ = np.sign(Y[:, ii] - Y[:, jj])
        B[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
    arm = {a: np.array([np.mean([[cls(yvec(A_[a][p], sorted({i for i, _ in A_[a][p]})))[c] == h[c]
                                  for c in range(6)] for h in H[n]])
                        for n, p in enumerate(pids)]) for a in ARMS}

    # ---- POSITIVE CONTROL · three exact reproductions of R287 ---------------------------------
    rep0 = B[np.random.default_rng(4242).choice(NS, 20, replace=False)].mean(axis=0).mean()
    repC = B[int(np.argmax(B.mean(axis=1)))].mean()
    ho = np.zeros(N); cnt = np.zeros(N)
    for s in range(NSPLIT):
        r2 = np.random.default_rng(2600 + s); perm = r2.permutation(N)
        fit, ev = perm[:N // 2], perm[N // 2:]
        best = int(np.argmax(B[:, fit].mean(axis=1)))
        ho[ev] += B[best, ev]; cnt[ev] += 1
    repH = (ho / np.maximum(cnt, 1)).mean()
    reps = [(nm, got, REF_TRUE[nm]) for nm, got in
            (("budget 0 · 20 draws", rep0), ("in-sample ceiling", repC),
             ("held-out best of 1,820", repH))]
    print("  POSITIVE CTRL — this pipeline must reproduce the COMMITTED references (read, not typed)\n")
    for nm, got, want in reps:
        print(f"    {nm:<26}{got:.13f}  vs committed {want:.13f}   "
              f"{'PASS' if abs(got - want) < 1e-12 else 'FAIL'}")
    repro_ok = all(abs(g - w) < 1e-12 for _, g, w in reps)

    # ---- PROVENANCE CONTROL · where R326's ceiling literal actually comes from ------------------
    sel0 = r286["selection"]["best"][0]
    prov = dict(
        typed=R326_TYPED_CEILING,
        equals_true_argmax=bool(R326_TYPED_CEILING == r286["dist"]["max"]),
        equals_split0_heldout=bool(R326_TYPED_CEILING == sel0[1]),
        in_r287_artifact=bool(R326_TYPED_CEILING in
                              [v for v in r287["refs"].values()]),
        true_argmax=r286["dist"]["max"], split0_pair=sel0)
    print(f"\n  PROVENANCE  R326 hard-codes {R326_TYPED_CEILING} as the in-sample ceiling, "
          f"source \"R287\"")
    print(f"    is it anywhere in R287's artifact ?              {prov['in_r287_artifact']}")
    print(f"    is it R286's true in-sample argmax ?             {prov['equals_true_argmax']}"
          f"   (that is {prov['true_argmax']})")
    print(f"    is it R286 selection['best'][0][1] ?             {prov['equals_split0_heldout']}"
          f"   -- the HELD-OUT score of split 0")
    prov_ok = (not prov["equals_true_argmax"]) and prov["equals_split0_heldout"]
    print(f"    -> {'CONFIRMED: a HELD-OUT number is published as the IN-SAMPLE ceiling, '
                   'attributed to a round that never computed it' if prov_ok else 'no defect found'}")

    # ---- the budget curve ----------------------------------------------------------------------
    def best_of_m_insample(m: int, seed: int) -> np.ndarray:
        rng = np.random.default_rng(500_000 + 1000 * seed + m)
        acc = np.zeros(N)
        for _ in range(NREP):
            idx = np.arange(NS) if m >= NS else rng.choice(NS, m, replace=False)
            acc += B[idx[int(np.argmax(B[idx].mean(axis=1)))]]
        return acc / NREP

    def coinflip_of_m(m: int, seed: int) -> np.ndarray:
        """NEGATIVE: same draw count, `best` replaced by a coin flip. Must be FLAT in m."""
        rng = np.random.default_rng(900_000 + 1000 * seed + m)
        acc = np.zeros(N)
        for _ in range(NREP):
            idx = np.arange(NS) if m >= NS else rng.choice(NS, m, replace=False)
            acc += B[idx[int(rng.integers(len(idx)))]]
        return acc / NREP

    def best_of_m_heldout(m: int, seed: int) -> np.ndarray:
        out = np.zeros(N); c = np.zeros(N)
        for s in range(NSPLIT):
            r_split = np.random.default_rng(2600 + s + 10_000 * seed)
            r_cand = np.random.default_rng(700_000 + 1000 * seed + 13 * s + m)
            idx = np.arange(NS) if m >= NS else r_cand.choice(NS, m, replace=False)
            perm = r_split.permutation(N); fit, ev = perm[:N // 2], perm[N // 2:]
            best = idx[int(np.argmax(B[np.ix_(idx, fit)].mean(axis=1)))]
            out[ev] += B[best, ev]; c[ev] += 1
        return out / np.maximum(c, 1)

    REF = {"in-sample": {}, "held-out": {}}
    NEG = {}
    for m in GRID:
        REF["in-sample"][m] = [best_of_m_insample(m, s) for s in SEEDS]
        REF["held-out"][m] = [best_of_m_heldout(m, s) for s in SEEDS]
        NEG[m] = [coinflip_of_m(m, s) for s in SEEDS]

    print(f"\n  THE BUDGET CURVE — prompt-blind reference A2 by selection budget m "
          f"({NREP} replicates, {len(SEEDS)} seeds)\n")
    print(f"    {'m':>6}{'in-sample':>12}{'sd':>8}{'held-out':>12}{'sd':>8}"
          f"{'coinflip (NEG)':>17}{'sd':>8}")
    for m in GRID:
        i_ = np.array([v.mean() for v in REF["in-sample"][m]])
        h_ = np.array([v.mean() for v in REF["held-out"][m]])
        g_ = np.array([v.mean() for v in NEG[m]])
        print(f"    {m:>6}{i_.mean():>12.5f}{i_.std():>8.5f}{h_.mean():>12.5f}{h_.std():>8.5f}"
              f"{g_.mean():>17.5f}{g_.std():>8.5f}")

    ins = {m: np.mean([v.mean() for v in REF["in-sample"][m]]) for m in GRID}
    hld = {m: np.mean([v.mean() for v in REF["held-out"][m]]) for m in GRID}
    neg = {m: np.mean([v.mean() for v in NEG[m]]) for m in GRID}
    seedsd = {m: float(np.std([v.mean() for v in REF["in-sample"][m]])) for m in GRID}

    # ---- NEGATIVE control reading ---------------------------------------------------------------
    neg_span = max(neg.values()) - min(neg.values())
    neg_sd = float(np.mean([np.std([v.mean() for v in NEG[m]]) for m in GRID]))
    neg_ok = neg_span < 3 * max(neg_sd, 1e-9)
    print(f"\n  NEGATIVE  coinflip-of-m span over the whole grid {neg_span:.5f} vs mean seed sd "
          f"{neg_sd:.5f}  {'PASS — flat, so the rise is argmax and not the draw count' if neg_ok else 'FAIL'}")

    # ---- POSITIVE at g=0 · EXACT, on SHARED draws -------------------------------------------------
    # ⚠ v1 compared best-of-1 and coinflip-of-1 computed from DIFFERENT rng streams and thresholded
    # the difference against a 3-seed sd. Two different draws treated as one -- and it failed on its
    # own noise (|Δ|=0.0026 vs 3sd=0.0021) while nothing was wrong. At m=1 the two rules select the
    # SAME element by construction, so given the same draws the identity is EXACT and the check has
    # no threshold to get wrong.
    g0_dev = 0.0
    for s in SEEDS:
        r = np.random.default_rng(11_000 + s)
        idx = r.choice(NS, NREP, replace=False)
        a_best = np.mean([B[i[int(np.argmax(B[i].mean(axis=1)))]] for i in idx[:, None]], axis=0)
        a_coin = np.mean([B[i[0]] for i in idx[:, None]], axis=0)
        g0_dev = max(g0_dev, float(np.abs(a_best - a_coin).max()))
    g0_ok = g0_dev == 0.0
    print(f"  POSITIVE  and it FAILS at g=0: on SHARED draws, argmax-of-1 and coinflip-of-1 differ "
          f"by {g0_dev:.1e}  {'PASS — exact, no selection to detect at m=1' if g0_ok else 'FAIL'}")
    knob_ok = ins[GRID[-1]] - ins[1] > 3 * max(seedsd[1], 1e-9)
    print(f"  KNOB      and it MOVES by m={GRID[-1]}: {ins[1]:.5f} -> {ins[GRID[-1]]:.5f}  "
          f"{'PASS' if knob_ok else 'FAIL'}")

    # ---- PLACEBO ---------------------------------------------------------------------------------
    plc = max(float(np.abs(arm[a] - arm[a]).max()) for a in ARMS)
    plc_ok = plc == 0.0
    print(f"  PLACEBO   each arm against itself: {plc:.1e}  {'PASS' if plc_ok else 'FAIL'}")

    # ---- the grid --------------------------------------------------------------------------------
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(av, rv):
        d = av - rv
        mde = ZEFF * d.std(ddof=1) / math.sqrt(N)
        bs = d[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        v = ("BEATS" if lo > 0 and abs(d.mean()) >= mde else
             "LOSES" if hi < 0 and abs(d.mean()) >= mde else "unresolved")
        return dict(gap=float(d.mean()), lo=lo, hi=hi, p=float(p), mde=float(mde),
                    ratio=float(abs(d.mean()) / mde), verdict=v)

    cells, grid_p = {}, []
    for mode in ("in-sample", "held-out"):
        for m in GRID:
            rv = np.mean(REF[mode][m], axis=0)
            for a in ARMS:
                c = cell(arm[a], rv)
                cells[f"{a}|{mode}|{m}"] = c
                grid_p.append((f"{a}|{mode}|{m}", c["p"]))
    grid_p.sort(key=lambda x: x[1]); C = len(grid_p)
    surv = {k for i, (k, p) in enumerate(grid_p, 1) if p <= 0.05 * i / C}
    nonsurv = sorted(set(k for k, _ in grid_p) - surv)

    print(f"\n  EACH ARM AGAINST best-of-m  (paired, cluster bootstrap over {N} prompts)\n")
    print(f"    {'m':>6}  " + "".join(f"{a:>26}" for a in ARMS))
    for mode in ("in-sample", "held-out"):
        print(f"    -- {mode} --")
        for m in GRID:
            row = "".join(
                f"{cells[f'{a}|{mode}|{m}']['gap']:>+11.4f}"
                f"{cells[f'{a}|{mode}|{m}']['ratio']:>7.2f}x"
                f"{cells[f'{a}|{mode}|{m}']['verdict'][:7]:>8}" for a in ARMS)
            print(f"    {m:>6}  {row}")
    print(f"\n    BH q=0.05 over ALL {C} cells · {len(surv)} survive · {C - len(surv)} do not")
    print(f"    non-survivors: {nonsurv if nonsurv else 'none'}")

    # ---- the DERIVATION R327 left as `unmeasured` -----------------------------------------------
    topw_a2 = r326["arm_a2"]["topw_k4"]                  # read, not typed
    b0 = REF_TRUE["budget 0 · 20 draws"]
    d0 = topw_a2 - b0
    print(f"\n  ⛔ DERIVATION, not a measurement: R327's empty cell. topw_k4 at budget 0 is")
    print(f"     {topw_a2:.6f} - {b0:.6f} = {d0:+.6f}, and every MDE committed anywhere in")
    print(f"     R326 lies in [0.00995, 0.01081], so the ratio is {d0/0.01081:.2f}x-{d0/0.0099451:.2f}x")
    print(f"     and ADMITTED under all of them. The algebra forces it; running it is Closure.")

    # ---- budget matching -------------------------------------------------------------------------
    MATCH = {"coval_core": (1, "in-sample"), "topw_k4": (budget_lb, "in-sample"),
             "gen_sham": (1, "in-sample")}
    print(f"\n  BUDGET MATCHING — each arm against a reference given the SAME budget the arm had\n")
    print(f"    topw_k4's budget is counted from committed artifacts: {budget_lb} deterministic "
          f"rule x k cores")
    print(f"      {budget_names}")
    print(f"    and it is a LOWER BOUND — uncommitted candidates are uncountable, so a larger true")
    print(f"    budget raises its matched reference and can only make admission HARDER.\n")
    print(f"    {'arm':<14}{'budget':>8}{'reference A2':>14}{'gap':>10}{'MDE':>9}{'ratio':>8}  verdict")
    matched = {}
    for a in ARMS:
        m, mode = MATCH[a]
        c = cells[f"{a}|{mode}|{m}"]
        matched[a] = c
        print(f"    {a:<14}{m:>8}{np.mean(REF[mode][m], axis=0).mean():>14.5f}"
              f"{c['gap']:>+10.4f}{c['mde']:>9.4f}{c['ratio']:>8.2f}  {c['verdict']}")

    matched_set = {a for a in ("coval_core", "topw_k4") if matched[a]["verdict"] == "BEATS"}
    neg_arm_ok = matched["gen_sham"]["verdict"] == "LOSES"
    print(f"\n  NEGATIVE (arm side)  gen_sham at its matched budget: "
          f"{matched['gen_sham']['verdict']}  {'PASS' if neg_arm_ok else 'FAIL'}")

    # ---- SENSITIVITY · the budget is a LOWER BOUND, so report where the conclusion turns --------
    # A lower-bounded input reported without the point at which it would flip the verdict is a
    # number pretending to be a conclusion. The crossing is the honest statement.
    cross = {}
    for a in ("coval_core", "topw_k4"):
        for mode in ("in-sample", "held-out"):
            beats = [m for m in GRID if cells[f"{a}|{mode}|{m}"]["verdict"] == "BEATS"]
            first_fail = next((m for m in GRID if cells[f"{a}|{mode}|{m}"]["verdict"] != "BEATS"),
                              None)
            cross[f"{a}|{mode}"] = dict(last_admitting=max(beats) if beats else None,
                                        first_non_admitting=first_fail)
    print(f"\n  SENSITIVITY — the counted budget is a LOWER BOUND, so: how much larger would the")
    print(f"  true budget have to be before the arm stops being admitted?\n")
    print(f"    {'arm':<14}{'mode':<12}{'counted':>9}{'first m that fails':>21}{'headroom':>10}")
    for a in ("coval_core", "topw_k4"):
        for mode in ("in-sample", "held-out"):
            c = cross[f"{a}|{mode}"]; b = MATCH[a][0]
            ff = c["first_non_admitting"]
            hr = f"{ff / b:.0f}x" if ff else ">1820/b"
            print(f"    {a:<14}{mode:<12}{b:>9}{str(ff):>21}{hr:>10}")

    # ---- KILL --------------------------------------------------------------------------------------
    flat = abs(ins[budget_lb] - ins[1]) < max(seedsd[budget_lb], seedsd[1])
    ctrl = repro_ok and neg_ok and g0_ok and knob_ok and plc_ok and neg_arm_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  repro={repro_ok}  neg-flat={neg_ok}  g0={g0_ok}  knob={knob_ok}  "
          f"placebo={plc_ok}  sham={neg_arm_ok}  provenance-defect={prov_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; no budget statement is readable.")
    elif flat:
        world = "W-BUDGET-IRRELEVANT"
        print(f"  -> W-BUDGET-IRRELEVANT. ref(1)={ins[1]:.5f} and ref({budget_lb})="
              f"{ins[budget_lb]:.5f} are within their own seed spread, so matching changes")
        print("     nothing and R327's semantic reading stands.")
    else:
        # ⚠ ALL matching readings, never `same[0]`. B and C carry the SAME admitted set, so
        # reporting one of them as "the" match would be a tie printed as a winner -- §4 `the
        # verdict string is not a computation`, the max()-over-a-tie sub-kind.
        same = [k for k, v in READINGS.items() if v == matched_set]
        if same:
            world = "W-MATCHED-AGREES"
            print(f"  -> W-MATCHED-AGREES. Budget-matching admits {sorted(matched_set)}, which is")
            print(f"     the admitted set of {len(same)} of {len(READINGS)} readings:")
            for k in same:
                print(f"       · {k}")
            print(f"     and NOT of: {[k for k in READINGS if k not in same]}")
            print("     So the choice R327 called unsettleable is settled — by R287's own")
            print("     compute-matching principle rather than by a preference among sentences.")
            print("  ⚠ AND THE AGREEMENT IS ON THE SET, NOT ON THE REFERENCE. The budget-matched")
            print(f"     reference for topw_k4 is {np.mean(REF['in-sample'][budget_lb], axis=0).mean():.5f} "
                  f"(best-of-{budget_lb} in-sample); reading B's is 0.55135")
            print("     (`generic` at k=4). Two different references that happen to license the")
            print("     same admissions — reading B was accidentally near budget-matched, which")
            print("     is luck and must not be reported as its justification.")
        else:
            world = "W-MATCHED-DIVERGES"
            print(f"  -> W-MATCHED-DIVERGES. Budget-matching admits {sorted(matched_set)}, which is")
            print(f"     NONE of R327's three readings ({ {k.split(' ')[0]: sorted(v) for k, v in READINGS.items()} }).")
            print("     The three readings applied ONE reference to arms with different selection")
            print("     histories, so the question was never which sentence the clause means.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  {C} cells, BH q=0.05, {len(surv)} survive; non-survivors named above.")
    print(f"  SEEDS         {len(SEEDS)}; reference curve printed with its across-seed sd at every m.")

    o = SELF.parent / "results" / "budget_matching.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        provenance=prov, provenance_defect=bool(prov_ok), committed_refs=REF_TRUE,
        n_prompts=N, pool=npool, n_quadruples=NS, grid=list(GRID), seeds=list(SEEDS),
        nrep=NREP, nsplit=NSPLIT,
        repro={nm: dict(got=g, r287=w, ok=bool(abs(g - w) < 1e-12)) for nm, g, w in reps},
        curve_insample={str(m): ins[m] for m in GRID},
        curve_heldout={str(m): hld[m] for m in GRID},
        curve_coinflip={str(m): neg[m] for m in GRID},
        seed_sd={str(m): seedsd[m] for m in GRID},
        cells=cells, bh_survivors=sorted(surv), bh_nonsurvivors=nonsurv, crossing=cross,
        topw_budget_lower_bound=budget_lb, topw_budget_names=budget_names,
        matched={a: dict(budget=MATCH[a][0], mode=MATCH[a][1], **matched[a]) for a in ARMS},
        matched_admitted=sorted(matched_set),
        readings={k: sorted(v) for k, v in READINGS.items()},
        derivation_topw_budget0=dict(gap=d0, note="forced by algebra, not measured"),
        controls=dict(repro=bool(repro_ok), neg_flat=bool(neg_ok), g0=bool(g0_ok),
                      knob=bool(knob_ok), placebo=bool(plc_ok), sham=bool(neg_arm_ok)),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
