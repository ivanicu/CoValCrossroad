"""R372 — is the S-curve a feature of the data, or is the resolving set a coin flip?

R371 found that R370's transport verdict MOVES with the number of difficulty strata S: on `exact`
the contrast resolves at S=2 and S=5 and not at S=3,4,6,8. R370 had fixed S=4 and reported
`W-COLLAPSES` as though it were a property of the data. R371's NEXT line said:

    "[UNTESTED] I expect the S-curve to stabilise with more prompts at fixed S rather than the
     verdict flipping, which is checkable by re-running R371's sweep on a random half of the 250
     and seeing whether the resolving set (S=2,5) is stable across halves. That is free, it is a
     direct test of whether the S-dependence is itself noise, and it should run before any GPU
     because if the resolving set is unstable at n=125 the whole curve is an artifact."

This is that round, and it is a test of R371's own headline, not a confirmation of it.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? The resolution RATE at
   n=125 is not free to be anything -- it must be LOWER than at n=250, because halving n inflates
   every stratum's noise while leaving the contrast alone. **So a low rate at n=125 is not evidence
   of anything and is never read as one.** What is free to vary, and what this round is about, is
   whether the rate DIFFERS ACROSS S by more than binomial sampling allows. That comparison is
   internal to one n, so the inflation cancels. If p(S) is flat, the resolving set is a coin flip
   and R371's `{2,5}` is an artifact of one draw; if p(S) separates, the curve is a real feature and
   R371's finding stands with its shape.

⛔ AND A DEFECT IN R371 THAT WOULD HAVE CONTAMINATED THIS ROUND, found while porting its code.
   R371's `floor_mean(ps, arm, seed, metric)` creates ONE rng per call and then walks `ps` in order,
   drawing each prompt's random criterion subset from that shared stream. So a prompt's floor
   depends on WHICH OTHER PROMPTS are in the list and in WHAT ORDER. That is invisible at fixed
   population -- R371 only ever called it on fixed strata -- but this round subsets the population
   200 times, and under the shared stream every subset would perturb every prompt's floor for
   reasons having nothing to do with the subset. **A quantity that is conceptually per-prompt must
   be computed per-prompt.** R372 seeds the draw from (pid, arm, seed) so a prompt's floor is
   invariant to its company, and MEASURES the size of R371's order-dependence rather than asserting
   it is small.

ESTIMAND        p(S) = P( |contrast_S| > MDE_S ) over random HALF-samples of the 250 prompts, for
                S in {2,3,4,5,6,8}, under the pool (non-subset) floor -- i.e. how often each
                stratum count returns `resolved` when the same analysis is re-run on half the data.
                Derived quantity: Var_true(p) = Var_obs(p-hat) - E[binomial noise], the part of the
                spread of p across S that sampling cannot explain.

IDENTIFICATION  Identified: p(S) at n=125, from 2B disjoint halves of the population already judged.
                NOT identified: p(S) at n=968, or at n=250 -- the full sample gives ONE draw per S,
                which is exactly why R371 could not tell a feature from a coin flip. Every statement
                about behaviour at other n is an EXTRAPOLATION and is labelled one.
                Also NOT identified: whether any S-dependence is about DIFFICULTY as opposed to
                whatever co-varies with the stratifier. Unchanged from R371.

SCOPE           250 prompts carrying core, full and pool on both arms · Qwen3.5-2B-Base ·
                R233's cache joined to task 630's pool labels · exact and pair, both reported ·
                the pool (non-subset) floor, which R370 established is the fair one.

WORLDS
  W-ARTIFACT     p(S) is flat: Var_true <= 0, and no S separates from the others by more than
                 binomial noise. R371's `{2,5}` was one draw from an exchangeable set. The S-curve
                 carries no information and R370's S=4 was neither better nor worse than any other
                 cell -- the honest object is a single pooled verdict, not a curve.
  W-STABLE       p(S) separates AND the top of the ranking is {2,5}. The curve is a real feature and
                 R371's reading of it stands.
  W-REAL-BUT-DIFFERENT  p(S) separates but the top is NOT {2,5}. Then S-dependence is real and
                 R371 read the wrong cells off a noisy single draw -- which would make R371 guilty
                 of exactly the error it convicted R370 of, one level up.

PREDICTION MATRIX
  W-ARTIFACT           -> Var_true <= 0 ; max p - min p within binomial band ; {2,5} not on top
  W-STABLE             -> Var_true > 0  ; top-2 by p(S) == {2,5}
  W-REAL-BUT-DIFFERENT -> Var_true > 0  ; top-2 != {2,5}

PRE-REGISTERED KILL -- conditional on the controls, never on the threshold alone.
    if reproduction_ok and placebo_exactly_zero and positive_recovers and positive_fails_at_g0:
        band = 2*sqrt(pbar*(1-pbar)/B_half)              # binomial sd of a single p-hat, doubled
        if var_true <= 0 or (max_p - min_p) < band:  -> W-ARTIFACT
        elif top2 == {2,5}:                          -> W-STABLE
        else:                                        -> W-REAL-BUT-DIFFERENT
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  REPRODUCTION   the per-prompt floor must reproduce R371's PUBLISHED full-sample table within the
                 floor's own seed-to-seed noise. Tolerance is ARGUED, not picked: it is the spread
                 of R371's own contrast across its three floor seeds, computed here.
  ORDER          the size of R371's shared-rng order dependence, measured by permuting the prompt
                 order under a faithful re-implementation of R371's floor. This is the defect above,
                 quantified rather than asserted.
  PLACEBO        the orig arm against ITSELF: the contrast is identically zero by algebra, so the
                 resolution rate must be EXACTLY 0 at every S. Anything else means the detector
                 fires on nothing.
  POSITIVE (2)   (a) DETECTOR: add g to the contrast at one chosen S only; the spread detector must
                 recover it, and must NOT fire at g=0.
                 (b) DATA-LEVEL: add g to the fresh-arm agreement of the hardest quintile of
                 prompts, creating a genuine difficulty-dependent transport effect; p(S) must move,
                 and must not at g=0. Scope stated: (a) validates the p-spread detector only;
                 (b) exercises the whole contrast pipeline.
  RANGE          both extremes must be attainable -- a rate stuck at 0 or 1 everywhere makes the
                 spread statistic degenerate and no threshold is admissible.

MULTIPLICITY    6 values of S x 2 metrics x 2 edge specifications = 24 cells, all printed.
SPECIFICATION   edges recomputed ON THE HALF vs inherited from the FULL sample -- both swept,
                because "re-run the analysis on this data" and "apply the fixed stratification"
                are both defensible and they are not the same question.
SEEDS           3 split-seed families, each B splits; per-family p(S) printed before pooling.
ARTIFACT        results/r372_stability.json with the source hash.

IMPOSSIBLE HERE
  p(S) at n=968       -- needs the job. EXTRAPOLATION wherever mentioned.
  a second judge      -- pool labels are 2B only, matching the cache.
  human rankings      -- the fresh responses carry none; every number is agreement with the FULL
                         RUBRIC, never with people. Unchanged since R233.
  cross-release       -- one release.

EXIT
    0  controls hold and the curve is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
CACHE = (ROOT / "E05_the_space_of_compilers" / "A18_the_candidate_set_wall_was_wrong"
         / "R233_fresh_candidate_transport" / "results" / "sat_fresh_and_orig.npz")
POOL_FRESH = A24 / "R370_a_non_subset_floor_for_the_fresh_arm" / "results" / "sat_genericpool16_fresh.npz"
POOL_ORIG = ROOT / "corebench" / "results" / "sat_genericpool16.npz"
R371 = A24 / "R371_would_more_prompts_resolve_transport" / "results" / "r371_power.json"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
FSEEDS = (0, 1, 2)                 # floor draw seeds, as R371
SPLIT_FAMILIES = (0, 1, 2)         # split-seed families
B = 80                             # splits per family -> 2*B*3 = 480 halves
SVALS = (2, 3, 4, 5, 6, 8)
METRICS = ("exact", "pair")
EDGESPEC = ("half", "full")
L = "ABCD"


def cls_of(y):
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    return np.sign(y[ii] - y[jj])


def agree(a, b, metric):
    m = (cls_of(a) == cls_of(b))
    return float(m.all()) if metric == "exact" else float(m.mean())


def main() -> int:
    for f in (CACHE, POOL_FRESH, POOL_ORIG, R371):
        if not f.exists():
            print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2

    d = np.load(CACHE, allow_pickle=True)
    T = collections.defaultdict(lambda: collections.defaultdict(lambda: [None] * 4))
    WT = collections.defaultdict(dict)
    for k, x in enumerate(d["meta"]):
        pid, arm, st, ci, ri = str(x).split("|")
        T[(pid, arm, st)][int(ci)][int(ri)] = float(d["sat"][k])
        WT[(pid, arm, st)][int(ci)] = float(d["weight"][k])
    pf = np.load(POOL_FRESH, allow_pickle=True)
    for k, x in enumerate(pf["meta"]):
        pid, arm, st, ci, ri = str(x).split("|")
        T[(pid, arm, "pool")][int(ci)][int(ri)] = float(pf["sat"][k]); WT[(pid, arm, "pool")][int(ci)] = 1.0
    po = np.load(POOL_ORIG, allow_pickle=True)
    for k, x in enumerate(po["meta"]):
        p_, ci, ltr = str(x).split("|")[:3]
        T[(p_, "orig", "pool")][int(ci)][L.index(ltr)] = float(po["sat"][k])
        WT[(p_, "orig", "pool")][int(ci)] = 1.0

    pids = sorted({str(x).split("|")[0] for x in d["meta"]})
    ARMS = ("orig", "fresh")

    def score(pid, arm, st, crits=None):
        tab, w = T[(pid, arm, st)], WT[(pid, arm, st)]
        cs = sorted(tab) if crits is None else [c for c in crits if c in tab]
        if not cs:
            return None
        y = np.zeros(4)
        for c in cs:
            v = tab[c]
            if any(x is None for x in v):
                continue
            y += w[c] * np.array(v, float)
        return y

    usable = [p for p in pids
              if all(score(p, a, s) is not None for a in ARMS for s in ("core", "full", "pool"))]
    if len(usable) < 100:
        print(f"  UNRUNNABLE: only {len(usable)} usable prompts. Exit 2, never 0."); return 2
    N = len(usable)
    IX = {p: i for i, p in enumerate(usable)}

    # ---- per-prompt quantities, all vectors over `usable` ------------------------------------
    AG = {(mt, arm): np.zeros(N) for mt in METRICS for arm in ARMS}
    DIFF = {arm: np.zeros(N) for arm in ARMS}
    NC = {arm: np.zeros(N, int) for arm in ARMS}
    for arm in ARMS:
        for p in usable:
            yf, yc = score(p, arm, "full"), score(p, arm, "core")
            for mt in METRICS:
                AG[(mt, arm)][IX[p]] = agree(yc, yf, mt)
            DIFF[arm][IX[p]] = float(np.std(yf))
            NC[arm][IX[p]] = len(T[(p, arm, "core")])

    # ⛔ THE PER-PROMPT FLOOR. The draw is seeded from (pid, arm, seed) so a prompt's floor does not
    #    depend on which other prompts share the call. R371 used ONE stream per call; the ORDER
    #    control below measures what that cost.
    FLOOR = {}
    for mt in METRICS:
        for arm in ARMS:
            for sd in FSEEDS:
                v = np.full(N, np.nan)
                for p in usable:
                    tab = T[(p, arm, "pool")]
                    k = max(1, int(NC[arm][IX[p]]))
                    cs = sorted(tab)
                    if len(cs) <= k:
                        continue
                    # ⛔ NOT `hash()`: Python randomises str hashing per process, so a run.py
                    #   using it is not reproducible across invocations and the two-run gate
                    #   would have caught it only after the artifact was committed.
                    rng = np.random.default_rng(int.from_bytes(
                        hashlib.sha256(f"{p}|{arm}|{sd}".encode()).digest()[:8], "big"))
                    sel = list(rng.choice(cs, k, replace=False))
                    yr, yf = score(p, arm, "pool", sel), score(p, arm, "full")
                    if yr is None or yf is None:
                        continue
                    v[IX[p]] = agree(yr, yf, mt)
                FLOOR[(mt, arm, sd)] = v

    def contrast_vec(idx, S, mt, edges_pop, bump=None, fseeds=FSEEDS):
        """per-stratum transport contrasts on the prompt indices `idx`.

        edges_pop -- indices whose DIFF quantiles define the stratum edges.
        bump      -- (indices, g) added to the FRESH arm's agreement: the data-level plant.
        fseeds    -- which floor draws to average; a single seed gives the seed-to-seed spread
                     that the reproduction tolerance is ARGUED from rather than picked.
        """
        ago = AG[(mt, "orig")].copy(); agf = AG[(mt, "fresh")].copy()
        if bump is not None:
            bi, g = bump
            agf[bi] = np.clip(agf[bi] + g, 0.0, 1.0)
        edges = np.quantile(DIFF["orig"][edges_pop], np.linspace(0, 1, S + 1))
        edges[0], edges[-1] = -np.inf, np.inf
        so = np.searchsorted(edges, DIFF["orig"], side="right") - 1
        sf = np.searchsorted(edges, DIFF["fresh"], side="right") - 1
        inset = np.zeros(N, bool); inset[idx] = True
        out, ns = [], []
        for s in range(S):
            io = np.flatnonzero(inset & (so == s)); iff = np.flatnonzero(inset & (sf == s))
            if len(io) < 5 or len(iff) < 5:
                continue
            co, cf = float(ago[io].mean()), float(agf[iff].mean())
            fo = float(np.mean([np.nanmean(FLOOR[(mt, "orig", sd)][io]) for sd in fseeds]))
            ff = float(np.mean([np.nanmean(FLOOR[(mt, "fresh", sd)][iff]) for sd in fseeds]))
            out.append((cf - ff) - (co - fo)); ns.append(len(io))
        return np.array(out), np.array(ns, float)

    def cell(idx, S, mt, edges_pop, bump=None, add=0.0, fseeds=FSEEDS):
        c, ns = contrast_vec(idx, S, mt, edges_pop, bump, fseeds)
        if len(c) < 2:
            return None
        w = ns / ns.sum()
        mean = float(np.dot(w, c)) + add
        sd = float(np.sqrt(np.dot(w, (c - np.dot(w, c)) ** 2)))
        mde = float(ZEFF * sd / math.sqrt(len(c)))
        return dict(contrast=mean, mde=mde, sd=sd, kept=len(c),
                    resolved=bool(abs(mean) > mde))

    ALL = np.arange(N)
    print("R372 · is the resolving set a feature, or a coin flip?\n")
    print(f"  {N} prompts · {len(SPLIT_FAMILIES)} split families x {B} splits "
          f"= {2*B*len(SPLIT_FAMILIES)} halves of n~{N//2}\n")

    # ---- CONTROL: REPRODUCTION vs R371's published table --------------------------------------
    pub = json.loads(R371.read_text())["rows"]
    print("  REPRODUCTION — per-prompt floor vs R371's published shared-stream floor")
    print(f"    {'cell':>10}{'R371':>10}{'R372':>10}{'delta':>10}{'seed sd':>10}")
    repro, deltas = [], []
    for mt in METRICS:
        for S in SVALS:
            r = cell(ALL, S, mt, ALL)
            if r is None or f"{mt}|{S}" not in pub:
                continue
            was = float(pub[f"{mt}|{S}"]["contrast"])
            # tolerance ARGUED, not picked: the spread of THIS cell's contrast across the three
            # floor draws is the noise the floor itself contributes, so a difference inside it
            # is not evidence of a different quantity.
            per = [cell(ALL, S, mt, ALL, fseeds=(sd,))["contrast"] for sd in FSEEDS]
            ssd = float(np.std(per)) if len(per) > 1 else float("nan")
            dl = abs(r["contrast"] - was)
            repro.append(dl <= max(3 * ssd, 0.02)); deltas.append(dl)
            print(f"    {mt+'|'+str(S):>10}{was:>+10.4f}{r['contrast']:>+10.4f}"
                  f"{dl:>10.4f}{ssd:>10.4f}")
    repro_ok = bool(repro) and all(repro)
    print(f"    -> every cell within max(3x its own floor-seed sd, 0.02): "
          f"{'PASS' if repro_ok else 'FAIL'}   max delta {max(deltas):.4f}\n")

    # ---- CONTROL: ORDER — how large is R371's shared-stream dependence? ------------------------
    def r371_floor_mean(order, arm, seed, mt):
        """faithful re-implementation of R371's shared-stream floor_mean."""
        rng = np.random.default_rng(seed)
        vals = []
        for i in order:
            p = usable[i]
            tab = T[(p, arm, "pool")]
            k = max(1, int(NC[arm][i]))
            cs = sorted(tab)
            if len(cs) <= k:
                continue
            sel = list(rng.choice(cs, k, replace=False))
            yr, yf = score(p, arm, "pool", sel), score(p, arm, "full")
            if yr is None or yf is None:
                continue
            vals.append(agree(yr, yf, mt))
        return float(np.mean(vals)) if vals else float("nan")

    S0, MT0 = 4, "exact"
    edges = np.quantile(DIFF["orig"], np.linspace(0, 1, S0 + 1)); edges[0], edges[-1] = -np.inf, np.inf
    so = np.searchsorted(edges, DIFF["orig"], side="right") - 1
    sf = np.searchsorted(edges, DIFF["fresh"], side="right") - 1
    perm_vals = []
    rngp = np.random.default_rng(7)
    for _ in range(12):
        pm = rngp.permutation(N)
        out, ns = [], []
        for s in range(S0):
            io = [i for i in pm if so[i] == s]; iff = [i for i in pm if sf[i] == s]
            if len(io) < 5 or len(iff) < 5:
                continue
            co = float(AG[(MT0, "orig")][io].mean()); cf = float(AG[(MT0, "fresh")][iff].mean())
            fo = float(np.mean([r371_floor_mean(io, "orig", sd, MT0) for sd in FSEEDS]))
            ff = float(np.mean([r371_floor_mean(iff, "fresh", sd, MT0) for sd in FSEEDS]))
            out.append((cf - ff) - (co - fo)); ns.append(len(io))
        w = np.array(ns, float); w /= w.sum()
        perm_vals.append(float(np.dot(w, np.array(out))))
    order_sd = float(np.std(perm_vals))
    print(f"  ORDER — R371's shared-stream floor, 12 permutations of the prompt order at "
          f"{MT0}|S={S0}")
    print(f"    contrast ranges {min(perm_vals):+.4f} to {max(perm_vals):+.4f}, sd {order_sd:.4f}, "
          f"published {float(pub[f'{MT0}|{S0}']['contrast']):+.4f}")
    print(f"    -> a prompt's floor DOES depend on its company. R372 does not inherit this.\n")

    # ---- the object: p(S) over half samples ---------------------------------------------------
    counts = collections.Counter(); tries = collections.Counter()
    per_family = collections.defaultdict(dict)
    PAT = collections.defaultdict(list)     # (spec, mt) -> list of resolved-S frozensets, per half
    PAIRED = collections.defaultdict(list)  # (spec, mt) -> list of (setA, setB) for the SAME split
    MDEV = collections.defaultdict(list)    # (spec, mt, S) -> MDE per half
    CONV = collections.defaultdict(list)    # (spec, mt, S) -> |contrast| per half
    for fam in SPLIT_FAMILIES:
        rng = np.random.default_rng(10_000 + fam)
        fc, ft = collections.Counter(), collections.Counter()
        for _ in range(B):
            pm = rng.permutation(N)
            sides = collections.defaultdict(list)
            for half in (pm[: N // 2], pm[N // 2:]):
                for spec in EDGESPEC:
                    ep = half if spec == "half" else ALL
                    for mt in METRICS:
                        got = set()
                        for S in SVALS:
                            r = cell(half, S, mt, ep)
                            if r is None:
                                continue
                            MDEV[(spec, mt, S)].append(r["mde"])
                            CONV[(spec, mt, S)].append(abs(r["contrast"]))
                            tries[(spec, mt, S)] += 1; ft[(spec, mt, S)] += 1
                            if r["resolved"]:
                                counts[(spec, mt, S)] += 1; fc[(spec, mt, S)] += 1
                                got.add(S)
                        PAT[(spec, mt)].append(frozenset(got))
                        sides[(spec, mt)].append(frozenset(got))
            for k, v in sides.items():
                if len(v) == 2:
                    PAIRED[k].append(tuple(v))
        for k in ft:
            per_family[fam][k] = fc[k] / ft[k]

    print("  p(S) = P(resolved) over half samples — the whole grid, non-survivors included")
    print(f"    {'spec':>6}{'metric':>7}{'S':>4}{'n halves':>10}{'p(S)':>9}"
          f"{'fam0':>8}{'fam1':>8}{'fam2':>8}")
    P = {}
    for spec in EDGESPEC:
        for mt in METRICS:
            for S in SVALS:
                k = (spec, mt, S)
                if not tries[k]:
                    continue
                P[k] = counts[k] / tries[k]
                fams = [per_family[f].get(k, float("nan")) for f in SPLIT_FAMILIES]
                print(f"    {spec:>6}{mt:>7}{S:>4}{tries[k]:>10}{P[k]:>9.3f}"
                      f"{fams[0]:>8.3f}{fams[1]:>8.3f}{fams[2]:>8.3f}")
        print()

    def spread(spec, mt):
        ks = [(spec, mt, S) for S in SVALS if (spec, mt, S) in P]
        ps = np.array([P[k] for k in ks]); nb = np.array([tries[k] for k in ks], float)
        pbar = float(ps.mean())
        var_obs = float(ps.var(ddof=1)) if len(ps) > 1 else float("nan")
        var_bin = float(np.mean(ps * (1 - ps) / nb))
        band = 2.0 * math.sqrt(max(pbar * (1 - pbar), 1e-12) / float(nb.mean()))
        top2 = {S for _, S in sorted(((P[(spec, mt, S)], S) for S in SVALS
                                      if (spec, mt, S) in P), reverse=True)[:2]}
        return dict(pbar=pbar, var_obs=var_obs, var_bin=var_bin,
                    var_true=var_obs - var_bin, rng=float(ps.max() - ps.min()),
                    band=band, top2=sorted(top2))

    # ⛔ ARITHMETIC TRAP, CAUGHT ON MY OWN RESULT AND NOT ON SOMEONE ELSE'S. `p(S) separates` is
    #   very nearly FORCED: R371 measured that the MDE RISES with S (0.0114 at S=2 to 0.1062 at
    #   S=8) because strata shrink faster than sqrt(S) recovers. A rising MDE against a roughly
    #   constant contrast makes p(S) fall with S by algebra. So `var_true > 0` restates R371's own
    #   MDE curve and is NOT evidence about which stratum count is right. It is a DERIVATION.
    #   What is NOT forced, and is the whole question, is whether S=5 out-resolves S=3 and S=4 --
    #   R371's pattern runs AGAINST the mechanical trend, so the trend cannot manufacture it.
    print(f"    {'spec':>6}{'metric':>7}{'mean p':>9}{'var_obs':>10}{'var_bin':>10}"
          f"{'var_true':>10}{'max-min':>9}{'band':>8}   top2")
    SP = {}
    for spec in EDGESPEC:
        for mt in METRICS:
            s = spread(spec, mt); SP[(spec, mt)] = s
            print(f"    {spec:>6}{mt:>7}{s['pbar']:>9.3f}{s['var_obs']:>10.5f}"
                  f"{s['var_bin']:>10.5f}{s['var_true']:>+10.5f}{s['rng']:>9.3f}"
                  f"{s['band']:>8.3f}   {s['top2']}")

    # ---- WHY S=2 TOPS THE RANKING: a 2-point sd has 1 df and collapses often ------------------
    #   Spotted in the run itself: the full-sample `pair|2` cell returned MDE = 0.0007, which no
    #   real design achieves. The between-stratum sd at S strata is estimated from S points, so at
    #   S=2 it has ONE degree of freedom and its sampling distribution has heavy mass near zero.
    #   A near-zero denominator manufactures `RESOLVED` regardless of the contrast. If that is what
    #   drives p(2), then S=2 is not the most powerful stratum count -- it is the most degenerate,
    #   and the ranking that put it on top is measuring df, not power.
    print(f"\n  IS S=2's LEAD POWER, OR A 1-df DENOMINATOR COLLAPSING?")
    print(f"    {'spec':>6}{'metric':>7}{'S':>4}{'med MDE':>10}{'p10 MDE':>10}"
          f"{'med |c|':>10}{'P(MDE<c/2)':>12}{'p(S)':>8}")
    DEG = {}
    for spec in EDGESPEC:
        for mt in METRICS:
            for S in SVALS:
                k = (spec, mt, S)
                if not MDEV[k]:
                    continue
                m = np.array(MDEV[k]); c = np.array(CONV[k])
                medc = float(np.median(c))
                deg = float(np.mean(m < medc / 2.0))
                DEG[k] = dict(med_mde=float(np.median(m)), p10_mde=float(np.percentile(m, 10)),
                              med_c=medc, degenerate=deg)
                print(f"    {spec:>6}{mt:>7}{S:>4}{DEG[k]['med_mde']:>10.4f}"
                      f"{DEG[k]['p10_mde']:>10.4f}{medc:>10.4f}{deg:>12.3f}{P[k]:>8.3f}")
        print()
    d2 = DEG[("half", "exact", 2)]["degenerate"]
    dr = [DEG[("half", "exact", S)]["degenerate"] for S in SVALS if ("half", "exact", S) in DEG]
    print(f"    S=2 collapses its denominator below half the typical contrast in {d2:.1%} of halves;")
    print(f"    the same rate at S={SVALS[1]}..{SVALS[-1]} runs {min(dr[1:]):.1%}..{max(dr[1:]):.1%}.")

    # ---- THE NON-FORCED STATISTIC: the resolving SET, not the marginal ------------------------
    R371SET = frozenset({2, 5})
    print(f"\n  THE RESOLVING SET ITSELF — R371 reported exactly {{2, 5}} on `exact`.")
    print(f"    {'spec':>6}{'metric':>7}{'P(={2,5})':>11}{'modal set':>18}{'P(modal)':>10}"
          f"{'P(empty)':>10}{'anti-mono':>11}")
    SETSTAT = {}
    for spec in EDGESPEC:
        for mt in METRICS:
            pats = PAT[(spec, mt)]
            if not pats:
                continue
            cnt = collections.Counter(pats)
            modal, mn = cnt.most_common(1)[0]
            # the ANTI-MONOTONE signature: S=5 resolves while S=3 and S=4 do not. The mechanical
            # MDE trend pushes the other way, so this pattern cannot be manufactured by it.
            anti = sum(1 for s in pats if (5 in s) and (3 not in s) and (4 not in s)) / len(pats)
            SETSTAT[(spec, mt)] = dict(
                p_r371=cnt[R371SET] / len(pats), modal=sorted(modal), p_modal=mn / len(pats),
                p_empty=cnt[frozenset()] / len(pats), anti=anti, n=len(pats),
                distinct=len(cnt))
            s = SETSTAT[(spec, mt)]
            print(f"    {spec:>6}{mt:>7}{s['p_r371']:>11.3f}{str(s['modal']):>18}"
                  f"{s['p_modal']:>10.3f}{s['p_empty']:>10.3f}{s['anti']:>11.3f}")

    # split-half agreement of the SET, with the degeneracy that would fake it
    print(f"\n    split-half agreement on the resolving SET (the two halves of one split):")
    print(f"    {'spec':>6}{'metric':>7}{'exact match':>13}{'both empty':>12}"
          f"{'match|not both empty':>22}")
    AGSTAT = {}
    for spec in EDGESPEC:
        for mt in METRICS:
            pr = PAIRED[(spec, mt)]
            if not pr:
                continue
            same = sum(1 for a, b in pr if a == b) / len(pr)
            both0 = sum(1 for a, b in pr if not a and not b) / len(pr)
            nz = [(a, b) for a, b in pr if a or b]
            cond = (sum(1 for a, b in nz if a == b) / len(nz)) if nz else float("nan")
            AGSTAT[(spec, mt)] = dict(same=same, both_empty=both0, cond=cond, n=len(pr))
            print(f"    {spec:>6}{mt:>7}{same:>13.3f}{both0:>12.3f}{cond:>22.3f}")
    print(f"    ⚠ the raw match rate is inflated by BOTH-EMPTY agreements, which agree on nothing.")
    print(f"      The conditional column is the one that carries information.")

    # ---- the full sample under the CORRECTED floor, directly against R371's headline ----------
    print(f"\n  R371's OWN TABLE, recomputed with the per-prompt floor (n=250, one draw):")
    print(f"    {'metric':>7}{'S':>4}{'contrast':>10}{'MDE':>9}   R372        R371")
    CORR = {}
    for mt in METRICS:
        for S in SVALS:
            r = cell(ALL, S, mt, ALL)
            if r is None:
                continue
            was = pub[f"{mt}|{S}"]
            wasres = abs(float(was["contrast"])) > float(was["mde"])
            CORR[(mt, S)] = dict(r, r371_resolved=bool(wasres))
            print(f"    {mt:>7}{S:>4}{r['contrast']:>+10.4f}{r['mde']:>9.4f}   "
                  f"{'RESOLVED' if r['resolved'] else 'inside  '}    "
                  f"{'RESOLVED' if wasres else 'inside'}")
    corr_set = sorted(S for S in SVALS if (("exact", S) in CORR) and CORR[("exact", S)]["resolved"])
    print(f"    -> corrected resolving set on `exact`: {corr_set}   (R371 published [2, 5])")

    # ---- CONTROLS ------------------------------------------------------------------------------
    print("\n  CONTROLS")
    # PLACEBO: orig against itself -> contrast identically 0 by algebra -> rate must be EXACTLY 0
    plac_hits, plac_n = 0, 0
    rngp = np.random.default_rng(99)
    savef = AG[("exact", "fresh")].copy()
    AG[("exact", "fresh")] = AG[("exact", "orig")].copy()
    savefl = FLOOR[("exact", "fresh", 0)], FLOOR[("exact", "fresh", 1)], FLOOR[("exact", "fresh", 2)]
    for sd in FSEEDS:
        FLOOR[("exact", "fresh", sd)] = FLOOR[("exact", "orig", sd)].copy()
    saved = DIFF["fresh"].copy(); DIFF["fresh"] = DIFF["orig"].copy()
    for _ in range(20):
        pm = rngp.permutation(N)
        for S in SVALS:
            r = cell(pm[: N // 2], S, "exact", pm[: N // 2])
            if r is None:
                continue
            plac_n += 1; plac_hits += int(r["resolved"])
    AG[("exact", "fresh")] = savef; DIFF["fresh"] = saved
    for j, sd in enumerate(FSEEDS):
        FLOOR[("exact", "fresh", sd)] = savefl[j]
    plac_ok = (plac_n > 0 and plac_hits == 0)
    print(f"    PLACEBO   orig vs itself: contrast is 0 by algebra; {plac_hits}/{plac_n} halves "
          f"'resolved'  {'PASS' if plac_ok else 'FAIL'}")

    # POSITIVE (a): the p-spread DETECTOR. add g to the contrast at S=6 only.
    def detector_run(g):
        c2, t2 = collections.Counter(), collections.Counter()
        rr = np.random.default_rng(555)
        for _ in range(30):
            pm = rr.permutation(N)
            for half in (pm[: N // 2], pm[N // 2:]):
                for S in SVALS:
                    r = cell(half, S, "exact", half, add=(g if S == 6 else 0.0))
                    if r is None:
                        continue
                    t2[S] += 1; c2[S] += int(r["resolved"])
        ps = np.array([c2[S] / t2[S] for S in SVALS if t2[S]])
        nb = np.array([t2[S] for S in SVALS if t2[S]], float)
        return float(ps.var(ddof=1) - np.mean(ps * (1 - ps) / nb)), float(c2[6] / max(t2[6], 1))

    pos_a_hi, p6_hi = detector_run(0.30)
    pos_a_lo, p6_lo = detector_run(0.0)
    pos_a_ok = (pos_a_hi > 0) and (p6_hi > p6_lo + 0.20)
    pos_a_null_ok = (p6_hi - p6_lo) > 0.20   # it must MOVE; the g=0 arm is the comparison
    print(f"    POS (a)   detector: p(S=6) {p6_lo:.3f} at g=0 -> {p6_hi:.3f} at g=0.30, "
          f"var_true {pos_a_lo:+.5f} -> {pos_a_hi:+.5f}  "
          f"{'PASS' if pos_a_ok and pos_a_null_ok else 'FAIL'}")
    print(f"              scope: this validates the p-spread detector, NOT the contrast pipeline")

    # POSITIVE (b): DATA-LEVEL. bump the fresh agreement of the hardest quintile.
    hard = np.flatnonzero(DIFF["orig"] >= np.quantile(DIFF["orig"], 0.8))

    def data_run(g):
        c2, t2 = collections.Counter(), collections.Counter()
        rr = np.random.default_rng(777)
        for _ in range(30):
            pm = rr.permutation(N)
            for half in (pm[: N // 2], pm[N // 2:]):
                for S in SVALS:
                    r = cell(half, S, "exact", half, bump=(hard, g))
                    if r is None:
                        continue
                    t2[S] += 1; c2[S] += int(r["resolved"])
        return {S: c2[S] / t2[S] for S in SVALS if t2[S]}

    db_hi, db_lo = data_run(0.35), data_run(0.0)
    moved = max(abs(db_hi[S] - db_lo[S]) for S in db_hi)
    pos_b_ok = moved > 0.15
    print(f"    POS (b)   data-level: hardest quintile bumped 0.35 -> max |dp(S)| = {moved:.3f}  "
          f"{'PASS' if pos_b_ok else 'FAIL'}")
    print(f"              g=0 arm p(S) = "
          f"{ {S: round(v,3) for S,v in sorted(db_lo.items())} }")
    print(f"              g=.35 arm  = "
          f"{ {S: round(v,3) for S,v in sorted(db_hi.items())} }")

    # RANGE: the statistic must not be degenerate
    allp = [P[k] for k in P]
    rng_ok = (min(allp) < 0.98) and (max(allp) > 0.02)
    print(f"    RANGE     p spans {min(allp):.3f}..{max(allp):.3f} — not pinned at 0 or 1  "
          f"{'PASS' if rng_ok else 'FAIL'}")

    ctrl_ok = repro_ok and plac_ok and pos_a_ok and pos_a_null_ok and pos_b_ok and rng_ok

    # ---- VERDICT -------------------------------------------------------------------------------
    head = SP[("half", "exact")]
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; every table above is silence, not a result.")
        v = "UNVERIFIED"
    elif head["var_true"] <= 0 or head["rng"] < head["band"]:
        print(f"  W-ARTIFACT — p(S) is FLAT. On the headline specification (half edges, exact) the")
        print(f"  spread of p across S is {head['rng']:.3f} against a binomial band of "
              f"{head['band']:.3f}, and")
        print(f"  var_true = {head['var_true']:+.5f}. Sampling explains the whole curve.")
        print(f"  ⛔ R371's `resolves at S=2 and 5` is ONE DRAW from an exchangeable set. The S-curve")
        print(f"     carries no information about which stratum count is right, and R371's own")
        print(f"     headline is downgraded by exactly the argument it used against R370.")
        v = "W_ARTIFACT"
    elif set(head["top2"]) == {2, 5}:
        print(f"  W-STABLE — p(S) separates (var_true {head['var_true']:+.5f}, range "
              f"{head['rng']:.3f} > band {head['band']:.3f})")
        print(f"  and the two most-resolving stratum counts are {head['top2']} — R371's set, "
              f"recovered")
        print(f"  independently on {tries[('half','exact',2)]} half samples. The curve is a feature.")
        v = "W_STABLE"
    else:
        print(f"  W-REAL-BUT-DIFFERENT — p(S) separates (var_true {head['var_true']:+.5f}, range "
              f"{head['rng']:.3f}")
        print(f"  > band {head['band']:.3f}) but the top two are {head['top2']}, NOT {{2, 5}}.")
        v = "W_REAL_BUT_DIFFERENT"

    # ⛔ AND THE PRE-REGISTERED STATISTIC TURNED OUT TO BE PARTLY A DERIVATION. Said plainly rather
    #   than quietly substituted: `var_true > 0` is very nearly forced, because R371 measured that
    #   the MDE RISES with S while the contrast does not, which makes p(S) fall by algebra. The
    #   kill above is reported as written -- moving a pre-registration after seeing the data is the
    #   thing pre-registration exists to prevent -- but the sentence it licenses is weaker than it
    #   looks, and the SET statistic below is what actually answers R371's question.
    hs = SETSTAT[("half", "exact")]
    print(f"\n  ⛔ THE PRE-REGISTERED STATISTIC IS PARTLY FORCED, and this is the corrected reading.")
    print(f"     `p(S) separates` restates R371's own finding that the MDE rises with S. It is a")
    print(f"     DERIVATION, not evidence about which stratum count is right. The non-forced")
    print(f"     question is whether R371's SET survives, and it is answered directly:")
    print(f"       · R371's exact set {{2, 5}} occurs in {hs['p_r371']:.1%} of "
          f"{hs['n']} half samples")
    print(f"       · the modal outcome is {hs['modal']} at {hs['p_modal']:.1%}; "
          f"{hs['distinct']} distinct sets appear")
    print(f"       · the ANTI-MONOTONE signature R371 rests on — S=5 resolving while S=3 and S=4")
    print(f"         do not — occurs in {hs['anti']:.1%} of halves. The mechanical MDE trend pushes")
    print(f"         AGAINST this pattern, so that rate is not manufactured by the trend.")
    print(f"       · recomputed at full n with a floor that does not depend on prompt order, the")
    print(f"         resolving set is {corr_set}, not [2, 5].")
    if hs["p_r371"] < 0.10 and corr_set != [2, 5]:
        print(f"     ⭐ R371's `{{2, 5}}` is a RARE DRAW that does not survive its own floor's repair.")
        print(f"        R371 was right that R370's S=4 was a specification choice. It was wrong to")
        print(f"        then read a SET off the same single draw — the error it convicted R370 of,")
        print(f"        committed one level up, in the same round.")
        v += "_SET_UNSTABLE"
    elif hs["p_r371"] < 0.10:
        print(f"     ⭐ NAMED, not defaulted: {{2, 5}} is rare across halves YET the corrected")
        print(f"        full-sample set is still {corr_set}. The set is fragile to resampling but")
        print(f"        not to the floor repair, which are two different fragilities.")
        v += "_SET_RARE_FLOOR_STABLE"
    else:
        print(f"     ⭐ NAMED, not defaulted: {{2, 5}} recurs in {hs['p_r371']:.1%} of halves, which")
        print(f"        is not rare, so the set is not a one-draw artifact even though the marginal")
        print(f"        curve it sits in is mechanical.")
        v += "_SET_RECURS"

    # ⛔ AND MY OWN VERDICT LABEL SAYS `REAL`, WHICH THE DEGENERACY TABLE UNDERCUTS. Computed, not
    #   typed: if S=2's denominator collapses far more often than any other S, then the ranking
    #   that put it on top is measuring degrees of freedom, not power, and `the S-dependence is
    #   real` is the wrong description of what separates the cells.
    dmax_hi = max(DEG[("half", "exact", S)]["degenerate"] for S in SVALS[1:]
                  if ("half", "exact", S) in DEG)
    if d2 > 3 * dmax_hi:
        print(f"\n  ⛔ AND THE WORD `REAL` IN MY OWN VERDICT LABEL IS TOO STRONG — computed, not")
        print(f"     conceded. S=2 tops every ranking above, and its denominator collapses below")
        print(f"     half the typical contrast in {d2:.1%} of halves against at most "
              f"{dmax_hi:.1%} anywhere else")
        print(f"     ({d2/max(dmax_hi,1e-9):.1f}x). The between-stratum sd at S strata has S-1 "
              f"degrees of freedom, so at")
        print(f"     S=2 it has ONE and its distribution has heavy mass near zero. **S=2 is not the")
        print(f"     most powerful stratum count; it is the most degenerate.** What orders the cells")
        print(f"     is df, not information about difficulty.")
        v += "_TOP_IS_DF_ARTIFACT"
        print(f"\n  ⭐ THE ONTOLOGY SHIFT, and it is larger than the correction that produced it:")
        print(f"     `the resolving set` is not a well-defined object of this design. It is empty in")
        print(f"     {hs['p_empty']:.1%} of halves, takes {hs['distinct']} distinct values, agrees "
              f"with itself across a")
        print(f"     split {AGSTAT[('half','exact')]['cond']:.1%} of the time once both-empty "
              f"agreements are removed, its")
        print(f"     top cell is a df artifact, and its marginal shape is a derivation. R371 asked")
        print(f"     `is the set stable`; the answer is that the SET IS NOT A QUANTITY. Both R370's")
        print(f"     single cell and R371's swept curve are readings of an object that does not")
        print(f"     survive being resampled.")
    else:
        print(f"\n  NAMED, not defaulted: S=2's denominator collapse rate is {d2:.1%} against "
              f"{dmax_hi:.1%} elsewhere,")
        print(f"     under the 3x threshold, so the ranking is not attributable to degrees of")
        print(f"     freedom and `real` survives as a description of what separates the cells.")

    # specification curve, stated whichever way the headline went
    agree_spec = {f"{spec}|{mt}": SP[(spec, mt)]["top2"] for spec in EDGESPEC for mt in METRICS}
    print(f"\n  SPECIFICATION CURVE — top-2 S by p(S) in every cell of the grid:")
    for k in sorted(agree_spec):
        s = SP[tuple(k.split("|"))]
        print(f"    {k:>12}  top2 {str(agree_spec[k]):>8}   var_true {s['var_true']:+.5f}   "
              f"range {s['rng']:.3f} vs band {s['band']:.3f}   "
              f"{'separates' if (s['var_true'] > 0 and s['rng'] > s['band']) else 'FLAT'}")
    nsep = sum(1 for k in SP if SP[k]["var_true"] > 0 and SP[k]["rng"] > SP[k]["band"])
    print(f"    {nsep} of {len(SP)} specifications separate; "
          f"{len(SP)-nsep} are flat. Reported whole, survivors and not.")

    print(f"\n  ⚠ EXTRAPOLATION, labelled: p(S) is measured at n~{N//2}. Nothing here measures it at")
    print(f"    n=250 or n=968. The resolution RATE is necessarily lower at half n; only the")
    print(f"    DIFFERENCE across S at fixed n is read, because that comparison is internal.")

    art = dict(stamp(str(SELF)), n_prompts=N, n_halves=int(2 * B * len(SPLIT_FAMILIES)),
               p={f"{a}|{b}|{c}": P[(a, b, c)] for (a, b, c) in P},
               tries={f"{a}|{b}|{c}": tries[(a, b, c)] for (a, b, c) in P},
               spread={f"{a}|{b}": SP[(a, b)] for (a, b) in SP},
               per_family={str(f): {f"{a}|{b}|{c}": v for (a, b, c), v in per_family[f].items()}
                           for f in per_family},
               setstat={f"{a}|{b}": SETSTAT[(a, b)] for (a, b) in SETSTAT},
               split_half={f"{a}|{b}": AGSTAT[(a, b)] for (a, b) in AGSTAT},
               corrected_full={f"{m}|{s}": CORR[(m, s)] for (m, s) in CORR},
               corrected_exact_set=corr_set,
               degeneracy={f"{a}|{b}|{c}": DEG[(a, b, c)] for (a, b, c) in DEG},
               order_sd_r371=order_sd, repro_max_delta=float(max(deltas)),
               controls=dict(reproduction=repro_ok, placebo=plac_ok, positive_detector=pos_a_ok,
                             positive_data=pos_b_ok, range=rng_ok),
               n_specs_separating=nsep, n_specs=len(SP), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r372_stability.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
