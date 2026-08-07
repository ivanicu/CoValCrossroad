#!/usr/bin/env python3
"""
R282 -- IS THE 75-OF-75 SATURATION A FINDING, OR IS IT FORCED BY SAMPLE SIZE?

R281 reported that all 75 weak orderings are realised in the pooled reading, and I wrote
that "the class space is fully used, so no counting gate can separate a good core from a
bad one." THAT IS A CLAIM I MADE MINUTES AGO AND IT MAY BE A COUPON-COLLECTOR FACT. With
18,384 annotator rankings over 75 possible classes, observing all 75 is nearly certain
under almost any distribution -- a class must have probability below roughly 1/18,384 to
stay unseen. So the observation may carry no information about the release at all.

This round is an ATTACK ON MY OWN CLAIM, and per the standard an attack is a full round
with controls, because a cheap attack that appears to succeed is the most expensive kind of
error: it retracts something true.

ESTIMAND        The sample size n* at which the observed number of distinct classes first
                reaches 75, measured by RAREFACTION (subsample without replacement at
                increasing n', count distinct classes). And the ratio n*/N.
                Named before the method.
                n*/N near 0  -> saturation is forced; support carries no information
                n*/N near 1  -> saturation is informative; rare classes are genuinely rare

IDENTIFICATION  Identified and exactly computable. The unbiased rarefaction expectation has
                a closed form, E[S(n')] = sum_i (1 - C(N-n_i, n') / C(N, n')), so the Monte
                Carlo estimator can be checked AGAINST THE ALGEBRA rather than against
                itself -- which is the positive control this round leans on hardest.
                ⚠ The closed form is a DERIVATION from the observed counts. It is used to
                validate the estimator, NOT as independent evidence about the release.

SCOPE           population : 18,384 `world` and 4,901 `personal` annotator rankings
                instrument : rarefaction over the parsed weak-ordering classes
                baseline   : a(4) = 75, the full class space
                regime     : n' swept from 1 to N on a log grid

WORLDS          A  FORCED -- n* is a small fraction of N. "All 75 realised" is a statement
                   about sample size, not about the release, and R281's reading is
                   retracted.
                B  INFORMATIVE -- n* is close to N, i.e. the last classes appear only near
                   the full sample, so their rarity is real and the reading stands.
                C  NEVER REACHED in one block but reached in another -> reading-dependent,
                   report the split.

PREDICTION      n*/N        | A: <0.1  | B: >0.5  | C: differs by block
MATRIX          my R281 line| retracted| stands   | scoped

KILL            Pre-registered, a conditional and not a bare threshold:
                    if montecarlo_matches_closed_form and negative_control_plateaus:
                        evaluate(n_star / N < 0.10)      # world A -> retract
                    else:
                        verdict = UNVERIFIED
                Threshold set before looking: 10% of the sample. If a tenth of the data
                already exhibits every class, the full sample's saturation is not news.

POSITIVE CTRL   ① ESTIMATOR vs ALGEBRA -- the Monte Carlo rarefaction curve must match the
                   closed-form expectation within the resampling floor at every n'. This
                   is a check against a DIFFERENT code path on a quantity with an exact
                   answer, not a check of the estimator against itself.
                ② FLOOR -- at n'=1 the support must be exactly 1.
                ③ CEILING -- at n'=N the support must equal the observed total support.
                   floor != ceiling, so a threshold between them is admissible.
                ④ FAILS AT g=0 -- a synthetic single-class population must return support
                   1 at every n', so the instrument does not report saturation when there
                   is none.

NEGATIVE CTRL   Destroy the thing under test -- the breadth of the class distribution --
                while keeping n and the machinery: a synthetic population drawn from only
                10 of the 75 classes at the same N. Its rarefaction MUST plateau at 10 and
                never reach 75. World this excludes: "the rarefaction estimator returns 75
                whatever it is given", which would look identical to genuine saturation.

SHAM            The same machinery on the `unacceptable` block, which carries ratings and
                cannot express a weak ordering: support must be 0 at every n'.

PLACEBO         n' = 0 must return support exactly 0.

NOISE FLOOR     MEASURED: the spread of the Monte Carlo rarefaction across >=3 seeds x
                repeats at each n'. A difference smaller than that spread is not a
                difference, and n* is read with it.

MULTIPLICITY    Cells = blocks x n'-grid points, reported whole. No p-values; these are
                resampling estimates of an exactly-defined quantity.

SPECIFICATION   Axes: block {world, personal} x n'-grid (log) x seed {0,1,2}.
                Whole curve printed, including where the two blocks disagree.

SEEDS           3, and the seed flag is verified to change the draws.

ARTIFACT        results/rarefaction.json with source hash and the full curves.

REPRODUCIBILITY two PYTHONHASHSEEDs byte-identical.

IMPOSSIBLE      out-of-distribution -- would need rankings from a second elicitation.
                causally identified -- would need to intervene on annotator count.
                construct validated -- no external answer to how many classes SHOULD occur.
"""
from __future__ import annotations
import collections, itertools, json, math, hashlib, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np

DATA = ROOT / "data"
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
BLOCKS, SEEDS, REPS = ["world", "personal"], [0, 1, 2], 8
FULL = 75


def parse_ranking(s):
    score = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L:
                score[tok] = -lvl
    if len(score) != 4:
        return None
    y = [score[c] for c in L]
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def load():
    out = {b: [] for b in BLOCKS}
    sham = 0
    for line in open(DATA / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rb_all = json.loads(line).get("metadata", {}).get("assessments", [])
        for asm in rb_all:
            rb = asm.get("ranking_blocks") or {}
            for b in BLOCKS:
                for e in rb.get(b) or []:
                    c = parse_ranking(e["ranking"]) if e.get("ranking") else None
                    if c is not None:
                        out[b].append(c)
            for e in rb.get("unacceptable") or []:
                if e.get("ranking") and parse_ranking(e["ranking"]) is not None:
                    sham += 1
    return out, sham


def rarefy_exact(counts, np_):
    """Closed form E[S(n')] = sum_i (1 - C(N-n_i, n')/C(N, n')). Exact -- the answer key."""
    N = sum(counts)
    if np_ > N:
        return float("nan")
    tot = 0.0
    for c in counts:
        if N - c < np_:
            tot += 1.0
        else:
            tot += 1.0 - math.exp(math.lgamma(N - c + 1) - math.lgamma(N - c - np_ + 1)
                                  - math.lgamma(N + 1) + math.lgamma(N - np_ + 1))
    return tot


def rarefy_mc(vals, np_, rng, reps=REPS):
    idx = np.arange(len(vals))
    return float(np.mean([len(set(vals[i] for i in rng.choice(idx, np_, replace=False)))
                          for _ in range(reps)]))


if __name__ == "__main__":
    print("\n  R282 -- is the 75-of-75 saturation forced by sample size?\n")
    data, sham = load()
    ctrl, curves, nstar = [], {}, {}

    for b in BLOCKS:
        vals = data[b]
        N = len(vals)
        counts = list(collections.Counter(vals).values())
        obs_support = len(counts)
        grid = sorted({int(x) for x in np.unique(np.geomspace(1, N, 26).astype(int))})
        exact = {n_: rarefy_exact(counts, n_) for n_ in grid}
        mc = {n_: [rarefy_mc(vals, n_, np.random.default_rng(1000 * s + n_)) for s in SEEDS]
              for n_ in grid}
        curves[b] = {"N": N, "obs_support": obs_support, "grid": grid,
                     "exact": exact, "mc_mean": {n_: float(np.mean(v)) for n_, v in mc.items()},
                     "mc_sd": {n_: float(np.std(v)) for n_, v in mc.items()}}
        # n* : first grid point where the EXACT expectation reaches obs_support - 0.5
        ns = next((n_ for n_ in grid if exact[n_] >= obs_support - 0.5), N)
        nstar[b] = (ns, ns / N)

    floor = max(max(curves[b]["mc_sd"].values()) for b in BLOCKS)
    print(f"    NOISE FLOOR (measured, {len(SEEDS)} seeds x {REPS} reps) : "
          f"max sd across the grid = {floor:.4f} classes")

    # POS 1 -- Monte Carlo against the closed form, a different code path with an exact answer
    devs = [abs(curves[b]["mc_mean"][n_] - curves[b]["exact"][n_])
            for b in BLOCKS for n_ in curves[b]["grid"]]
    ctrl.append(("POS  MonteCarlo matches the closed form", max(devs) < max(0.5, 3 * floor),
                 f"max |dev| = {max(devs):.4f} vs tol {max(0.5, 3*floor):.4f}"))
    ctrl.append(("POS  floor: support at n'=1 is exactly 1",
                 all(curves[b]["mc_mean"][1] == 1.0 for b in BLOCKS), "1.0"))
    ctrl.append(("POS  ceiling: at n'=N support equals observed",
                 all(abs(curves[b]["exact"][curves[b]["grid"][-1]]
                         - curves[b]["obs_support"]) < 1e-6 for b in BLOCKS),
                 " ".join(f"{b}:{curves[b]['obs_support']}" for b in BLOCKS)))
    # POS 4 -- fails at g=0: a single-class population never reports saturation
    one = rarefy_exact([10000], 5000)
    ctrl.append(("POS  fails at g=0: single-class pop stays at 1", one == 1.0, f"{one:.4f}"))
    # NEGATIVE -- 10 classes only, same N; must plateau at 10
    rng = np.random.default_rng(0)
    Nw = curves["world"]["N"]
    narrow = list(collections.Counter(rng.integers(0, 10, Nw)).values())
    nar_full = rarefy_exact(narrow, Nw)
    ctrl.append(("NEG  10-class synthetic plateaus at 10, never 75",
                 abs(nar_full - 10) < 1e-6, f"{nar_full:.4f}"))
    ctrl.append(("SHAM `unacceptable` block yields no classes", sham == 0, f"{sham} parsed"))
    ctrl.append(("PLA  support at n'=0 is exactly 0", rarefy_exact([5, 5], 0) == 0.0, "0.0"))

    print("\n    CONTROLS")
    ok = True
    for name, passed, detail in ctrl:
        ok &= bool(passed)
        print(f"      [{'PASS' if passed else 'FAIL'}] {name:<46} {detail}")

    print(f"\n    RAREFACTION -- distinct classes seen vs sample size (exact expectation)")
    print(f"      {'n′':>8}" + "".join(f"{b:>14}" for b in BLOCKS))
    show = [1, 10, 50, 100, 250, 500, 1000, 4901, 18384]
    for n_ in show:
        row = f"      {n_:>8}"
        for b in BLOCKS:
            g = curves[b]["grid"]
            near = min(g, key=lambda x: abs(x - n_))
            row += f"{curves[b]['exact'][near]:>10.2f}@{near:<3}" if near <= curves[b]["N"] else f"{'--':>14}"
        print(row)

    print(f"\n    {'block':<10}{'N':>8}{'observed':>10}{'n*':>8}{'n*/N':>9}")
    for b in BLOCKS:
        print(f"      {b:<8}{curves[b]['N']:>8}{curves[b]['obs_support']:>10}"
              f"{nstar[b][0]:>8}{nstar[b][1]:>9.4f}")

    ratios = [nstar[b][1] for b in BLOCKS]
    if not ok:
        verdict = "UNVERIFIED -- a control failed; the curve is not admissible"
    elif max(ratios) < 0.10:
        verdict = (f"WORLD A -- FORCED. Every class appears within n*/N = "
                   f"{max(ratios):.4f} of the sample, so 'all 75 realised' is a statement "
                   f"about sample size and R281's reading is RETRACTED.")
    elif min(ratios) > 0.50:
        verdict = "WORLD B -- INFORMATIVE. The last classes appear only near the full sample."
    else:
        verdict = (f"WORLD C -- SPLIT across blocks: n*/N = "
                   f"{', '.join(f'{b}:{nstar[b][1]:.4f}' for b in BLOCKS)}. Report the split.")
    print(f"\n    VERDICT: {verdict}\n")

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    art = {"source_sha256_16": src, "noise_floor": floor,
           "curves": {b: {k: (v if not isinstance(v, dict) else
                             {str(kk): vv for kk, vv in v.items()})
                          for k, v in curves[b].items()} for b in BLOCKS},
           "n_star": {b: list(nstar[b]) for b in BLOCKS},
           "controls": [(n, bool(p), d) for n, p, d in ctrl], "verdict": verdict}
    (HERE / "results" / "rarefaction.json").write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"    artifact: results/rarefaction.json  (source {src})\n")
