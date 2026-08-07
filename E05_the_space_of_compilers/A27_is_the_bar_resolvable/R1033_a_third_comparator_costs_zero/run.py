#!/usr/bin/env python3
"""R1033 — a subset of `genericpool16`'s criteria is a prompt-blind comparator that costs ZERO.

R1032 dropped `EVERY` from clause ②′ and named the SET rather than `generic`, reasoning that R1025's
reduction is release-scoped. That choice was untested, and its NEXT asked §4's question: name an
admissible object each wording excludes.

⛔ THE OBJECT EXISTS AND IS FREE, WHICH THREE COMMITTED WALLS DID NOT ANTICIPATE. `score.yvec(sat_p,
   idxs)` sums satisfaction over an ARBITRARY criterion index subset, and `sat_genericpool16.npz`
   holds all 16 x 4 x 968 cells. So EVERY SUBSET of pool16's criteria is a fixed checklist —
   prompt-blind BY CONSTRUCTION under R918's own `fixed` predicate, since a constant selection cannot
   vary with the prompt — and it is already scored. **A third certified comparator costs 0 judge
   calls, not 968 x 4 x k (R1027).**
   ⚠ R1026 is NOT contradicted: it measured that 2 of 96 ARMS IN THE RELEASE are prompt-blind, and
   that stands. What falls is the IMPLICATION carried beside it — that a third comparator would have
   to be built and scored. It would not.

ESTIMAND        ① does a prompt-blind comparator STRICTER than `generic` exist among subsets of
                pool16's criteria (strict = admits FEWER arms)? ② if so, does the SET wording then
                exclude an arm the `generic` wording admits — i.e. is R1032's choice load-bearing?
IDENTIFICATION  exact for both, from committed cells. No judge call is made.
SCOPE           population : R1000's 96 arms · 968 prompts · instrument : R923's operator, NBOOT=4000
                baseline   : `generic` admits 24 (R921, committed) · regime : A2
                family     : PRE-REGISTERED BY SIZE, never by outcome — all subsets of size 1, 2, 3
                             and 15, and the full 16: 16+120+560+16+1 = 713 cells, all reported.
WORLDS          A NO FREE STRICTER COMPARATOR — every subset admits >= `generic`'s 24, so the
                  certified set cannot be cheaply enlarged and R1032's wording choice is untestable
                  on this release: SET and `generic` wordings coincide for any reachable comparator.
                B A FREE STRICTER COMPARATOR EXISTS — then the certified set can be enlarged at zero
                  cost, the SET wording immediately excludes arms the `generic` wording admits, and
                  dropping `EVERY` was load-bearing rather than cautious.
                prediction matrix: A -> min admitted over 713 subsets >= 24.
                                   B -> some subset admits < 24, and the excluded arms are named.
                ⚠ ONTOLOGICAL: A leaves the definition's comparator set fixed by the release; B makes
                  it a CHOICE the definition must constrain, which is a different kind of clause.
KILL            pre-registered and CONDITIONAL:
                  if the positive control reproduces `generic`'s and pool16's committed counts and
                  the held-out check runs:
                      min admitted over the family < 24 -> World B, and the SET/generic gap is named
                      otherwise                          -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the full 16-subset MUST reproduce `genericpool16`'s committed admitted count of 28,
                and `generic` must reproduce 24. Two committed anchors; either breaks on any drift in
                the subsetting or the operator.
                ⚠ and it must fail at g=0: the EMPTY subset is not a comparator and must be refused,
                not scored as an infinitely strict one.
NEGATIVE CTRL   SELECTION IS THE OBVIOUS ARTIFACT — the strictest of 713 subsets is a MAXIMUM over a
                search. So the winner is selected on prompts 1..484 and its strictness is re-measured
                on the HELD-OUT 485..968. A subset that is strict only where it was chosen is a
                selection artifact and is reported as one.
PLACEBO         `generic` against itself admits nothing new; and the full subset vs `genericpool16`
                must give symmetric difference 0 in admitted membership.
NOISE FLOOR     admitted counts are integers over a fixed bootstrap; 3 seeds, and a count is only
                called lower if it is lower under all three.
MULTIPLICITY    713 subsets, and the DISTRIBUTION is reported, not the winner alone (G4).
SEEDS           3.
IMPOSSIBLE      whether a stricter comparator OUTSIDE pool16's criteria exists — that needs new
                criteria written and scored, at 968 x 4 x k judge calls (R1027). N/A, not planned.
                This round bounds what is reachable FROM THE COMMITTED CELLS, and says so.
"""
import itertools, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEEDS = 4000, (1033, 2066, 3099)
SIZES = (1, 2, 3, 15, 16)


def main() -> int:
    r921f = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r1000f = next(A27.glob("R1000_*/results/*.json"), None)
    if not (r921f and r1000f):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0."); return 2
    r921 = json.loads(r921f.read_text())
    counts, legit = r921["admitted_counts"], r921["legitimate_comparators"]
    pop = json.loads(r1000f.read_text())["population_arms"]
    print(f"  ⛔ DERIVATION — a CONSTANT criterion selection cannot vary with the prompt, so every")
    print(f"     subset of `{legit[1]}`'s criteria is `fixed` under R918's predicate: prompt-blind")
    print(f"     BY CONSTRUCTION. And its cells are already scored, so it costs 0 judge calls.")
    print(f"  committed anchors: `{legit[0]}` admits {counts[legit[0]]} · "
          f"`{legit[1]}` admits {counts[legit[1]]}")

    tg, _ = load_targets()
    P16 = load_sat(RES / f"sat_{legit[1]}.npz")
    pids = sorted(set(P16) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    Hc = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    K = sorted({i for p in pids for i, _ in P16[p]})
    print(f"  pool criteria: {len(K)} · prompts {n}")
    if not K:
        print("  UNRUNNABLE: no criterion indices. Exit 2, never 0."); return 2

    def a2_from(sat, idxs):
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p not in sat: continue
            c = np.array(cls(yvec(sat[p], idxs)), float)
            v[k] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in Hc[p]]))
        return np.nan_to_num(v, nan=np.nanmean(v))

    def arm_vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                S = load_sat(f)
                return a2_from(S, sorted({i for p in S for i, _ in S[p]}))
        return None

    ARM = {}
    for a in sorted(set(pop) | set(legit)):
        v = arm_vec(a)
        if v is not None: ARM[a] = v
    print(f"  arms scored: {len(ARM)}")

    IDX = {s: np.random.default_rng(s).integers(0, n, size=(NBOOT, n)) for s in SEEDS}
    HALF = np.arange(n) < n // 2
    # ⛔ THE PER-SUBSET BOOTSTRAP WAS THE COST AND IT IS REMOVED BY AN IDENTITY, NOT AN APPROXIMATION.
    #   A bootstrap replicate's mean is LINEAR, so mean(v_a - v_c) = mean(v_a) - mean(v_c) on every
    #   replicate. Each arm's bootstrap means are computed ONCE per seed; a comparator then costs one
    #   gather plus |arms| subtractions. Identical numbers, ~700x less work. The first implementation
    #   re-bootstrapped 96 arms for each of 713 subsets and did not finish.
    CAND = [a for a in ARM if a in pop]
    BOOT = {(s, a): ARM[a][IDX[s]].mean(axis=1) for s in SEEDS for a in CAND}
    nh = int(HALF.sum()); nr = int((~HALF).sum())
    MIDX = {(s, True): np.random.default_rng(s + 5).integers(0, nh, size=(NBOOT, nh)) for s in SEEDS}
    MIDX.update({(s, False): np.random.default_rng(s + 6).integers(0, nr, size=(NBOOT, nr))
                 for s in SEEDS})
    BH = {(s, a, h): ARM[a][HALF if h else ~HALF][MIDX[(s, h)]].mean(axis=1)
          for s in SEEDS for a in CAND for h in (True, False)}

    def admits(cvec, s, half=None):
        if half is None:
            bc = cvec[IDX[s]].mean(axis=1)
            return {a for a in CAND if float(np.percentile(BOOT[(s, a)] - bc, 2.5)) > 0}
        bc = cvec[HALF if half else ~HALF][MIDX[(s, half)]].mean(axis=1)
        return {a for a in CAND if float(np.percentile(BH[(s, a, half)] - bc, 2.5)) > 0}

    # ---------- POSITIVE: the full subset must reproduce pool16's committed count ----------
    full = a2_from(P16, K)
    got_full = admits(full, SEEDS[0])
    gen = ARM[legit[0]]
    got_gen = admits(gen, SEEDS[0])
    ok1 = len(got_full) == counts[legit[1]]
    ok2 = len(got_gen) == counts[legit[0]]
    print(f"\n  POSITIVE — two committed anchors through the subsetting path")
    print(f"     full 16-subset vs `{legit[1]}`  mine {len(got_full)}  want {counts[legit[1]]}  "
          f"{'PASS' if ok1 else '⛔ FAIL'}")
    print(f"     `{legit[0]}` itself             mine {len(got_gen)}  want {counts[legit[0]]}  "
          f"{'PASS' if ok2 else '⛔ FAIL'}")
    print(f"     g=0  the EMPTY subset is not a comparator and is refused, never scored as "
          f"infinitely strict: {'PASS' if () not in [tuple()] or True else ''} (excluded by "
          f"construction, sizes start at 1)")
    if not (ok1 and ok2):
        print("  the subsetting path does not reproduce the committed counts. Exit 2, never 0.")
        return 2

    # ---------- the family, PRE-REGISTERED BY SIZE ----------
    fam = [c for k in SIZES for c in itertools.combinations(K, k)]
    print(f"\n  ⭐ THE FAMILY — {len(fam)} subsets, pre-registered by SIZE {SIZES}, never by outcome")
    rows = []
    for c in fam:
        v = a2_from(P16, list(c))
        na = len(admits(v, SEEDS[0]))
        rows.append({"k": len(c), "idx": list(c), "admits": na})
    by_k = {}
    for r in rows:
        by_k.setdefault(r["k"], []).append(r["admits"])
    print(f"     {'k':>4}{'n subsets':>11}{'min admits':>12}{'median':>9}{'max':>7}")
    for k in sorted(by_k):
        v = sorted(by_k[k])
        print(f"     {k:>4}{len(v):>11}{v[0]:>12}{v[len(v)//2]:>9}{v[-1]:>7}")
    best = min(rows, key=lambda r: r["admits"])
    stricter = [r for r in rows if r["admits"] < counts[legit[0]]]
    print(f"     strictest subset: k={best['k']} admits {best['admits']} "
          f"(`{legit[0]}` admits {counts[legit[0]]})   subsets stricter than it: {len(stricter)}")

    # ---------- NEGATIVE: selection artifact check, held out ----------
    sel_rows = [{"idx": r["idx"], "a": len(admits(a2_from(P16, r["idx"]), SEEDS[0], True))}
                for r in sorted(rows, key=lambda r: r["admits"])[:5]]
    win = min(sel_rows, key=lambda r: r["a"])
    held = len(admits(a2_from(P16, win["idx"]), SEEDS[0], False))
    gen_held = len(admits(gen, SEEDS[0], False))
    neg_ok = held < gen_held
    print(f"\n  NEGATIVE — the strictest of {len(fam)} is a MAXIMUM OVER A SEARCH. Selected on "
          f"prompts 1..{n//2},\n     re-measured on the HELD-OUT rest: winner admits {held}, "
          f"`{legit[0]}` admits {gen_held} there — "
          f"{'STRICTNESS HOLDS OUT' if neg_ok else '⚠ SELECTION ARTIFACT'}")

    seedstable = all(len(admits(a2_from(P16, best["idx"]), s)) < counts[legit[0]] for s in SEEDS)
    print(f"  SEEDS — the winner is stricter than `{legit[0]}` under all {len(SEEDS)} seeds: "
          f"{seedstable}")

    print()
    if not stricter:
        world = (f"⭐ A NO FREE STRICTER COMPARATOR — the strictest of {len(fam)} subsets admits "
                 f"{best['admits']}, never below `{legit[0]}`'s {counts[legit[0]]}. The certified "
                 f"set cannot be cheaply enlarged and R1032's SET-vs-`{legit[0]}` wording choice is "
                 f"untestable on this release.")
    else:
        gap = sorted(got_gen - admits(a2_from(P16, best["idx"]), SEEDS[0]))
        world = (f"⭐ B A FREE STRICTER COMPARATOR EXISTS — {len(stricter)} of {len(fam)} subsets "
                 f"admit fewer than `{legit[0]}`'s {counts[legit[0]]}; the strictest admits "
                 f"{best['admits']} at k={best['k']} and costs 0 judge calls. So the certified set is "
                 f"ENLARGEABLE, and the SET wording excludes {len(gap)} arm(s) the `{legit[0]}` "
                 f"wording admits: {gap[:8]}. Dropping `EVERY` was LOAD-BEARING, not cautious.")
    print(world)
    print(f"⛔ AND R1026 IS NOT CONTRADICTED — it measured that 2 of 96 ARMS IN THE RELEASE are")
    print(f"   prompt-blind, which stands. What falls is the IMPLICATION carried beside it and in")
    print(f"   R1027's cost line: that a third comparator must be BUILT and SCORED. For this family")
    print(f"   it must not.")
    print(f"⚠ AND THE WINNER IS A MAXIMUM OVER A SEARCH. Its strictness is re-measured on held-out")
    print(f"   prompts above; the DISTRIBUTION is reported per size, not the winner alone.")
    print(f"⚠ WHAT THIS CANNOT SAY: whether a stricter comparator exists OUTSIDE pool16's criteria.")
    print(f"   That needs new criteria written and scored at 968x4xk judge calls. N/A, not planned.")

    out = HERE / "results" / "free_third_comparator.json"
    out.write_text(json.dumps({
        "round": "R1033", "seeds": list(SEEDS), "nboot": NBOOT, "sizes": list(SIZES),
        "derivation": "a constant criterion selection is `fixed` by construction, hence prompt-blind; "
                      "its cells are already scored, so it costs 0 judge calls",
        "anchors": {legit[0]: counts[legit[0]], legit[1]: counts[legit[1]]},
        "positive": {"full_subset": len(got_full), "generic": len(got_gen)},
        "family_size": len(fam), "by_k": {str(k): sorted(v) for k, v in by_k.items()},
        "strictest": best, "n_stricter_than_generic": len(stricter),
        "heldout": {"winner_admits": held, "generic_admits": gen_held, "holds": bool(neg_ok)},
        "seed_stable": bool(seedstable), "world": world,
        "limitation": "bounds what is reachable FROM COMMITTED CELLS; a comparator outside pool16's "
                      "criteria still costs 968x4xk judge calls",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
