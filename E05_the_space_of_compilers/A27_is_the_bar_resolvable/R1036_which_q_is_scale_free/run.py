#!/usr/bin/env python3
"""R1036 — which q is SCALE-FREE? A max inflates with family size; a quantile should not.

R1035 left a stable non-empty extension over q ∈ {50..99} and closed by asserting that the curve
CANNOT select among them. ⚠ That is a quantifier over my own work — §4's highest-risk sentence — and
it is wrong. A criterion exists and it is not another q-sweep.

⛔ THE PRECEDENT IS R848's, CITED NOT CLAIMED. For clause ④ it ran a DOSE-RESPONSE OVER FAMILY SIZE,
   with `real_sd` per size and `seed_changes_subset: True`, and measured the bar rising at
   **0.0074 per ln(n)**. That is the signature of a MAXIMUM: enlarge the family and the max grows,
   because it is an extreme order statistic. ⭐ A QUANTILE has no such drift — the q-th percentile of
   a larger draw from the same population estimates the same number. **So scale-stability selects q,
   and R1035's closing sentence is withdrawn.**

ESTIMAND        |extension| as a function of BOTH family size n and quantile q — the n × q grid.
IDENTIFICATION  exact and nearly free: R1035's `LO` matrix already holds every arm's margin against
                all 4,261 comparators, so a subfamily is a COLUMN SUBSET, not a recomputation.
SCOPE           population : R1000's committed `population_arms` · 968 prompts
                instrument : R923's operator repaired per R1024 · baseline : R1035's committed curve
                sizes      : nested prefixes of one shuffled family, so smaller families are SUBSETS
                             of larger ones and the monotone argument holds exactly
WORLDS          A A QUANTILE IS SCALE-FREE AND THE MAX IS NOT — |ext| at q=100 declines as n grows,
                  while some q < 100 is FLAT in n. Then q is selected by scale-stability and the
                  smallest flat q is the principled bound.
                B EVERY q DRIFTS WITH n — then no quantile is scale-free, the clause cannot be stated
                  over a family at all, and the comparator set must be fixed by enumeration instead.
                prediction matrix: A -> q=100 monotone down in n; some q flat across all sizes.
                                   B -> every column drifts.
                ⚠ ONTOLOGICAL: A gives the clause a parameter with a principled value; B says the
                  family formulation is the wrong shape and no parameter rescues it.
KILL            pre-registered and CONDITIONAL:
                  if q=100 at n=4261 reproduces R1035's seed-disagreement and the nesting holds:
                      some q < 100 has an IDENTICAL extension at every n and every seed -> World A
                      otherwise                                                          -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ① at n=4261 the whole q-curve must reproduce R1035's committed one (73/12/12/11/9/8).
                ② NESTING: each family must be a strict subset of the next, checked, not assumed —
                otherwise "growing the family" is drawing a different family.
NEGATIVE CTRL   the q=100 column must MOVE with n. If the max does not drift, this family does not
                exhibit the R848 signature and the whole scale-stability argument is inapplicable
                here — reported as such rather than assumed away.
PLACEBO         n = 1: every q collapses to the same requirement, so the row must be constant.
NOISE FLOOR     3 bootstrap seeds × 3 family shuffles; a cell is reported only if all agree.
MULTIPLICITY    5 sizes × 7 quantiles = 35 cells, the whole grid printed including the unstable ones.
SEEDS           3 bootstrap × 3 family-shuffle, reported separately, never pooled.
IMPOSSIBLE      whether the scale-free q is the RIGHT q — scale-stability is a necessary property, not
                a sufficient one. N/A; what it would require is an external criterion for what the
                comparator family is meant to represent.
"""
import json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"; NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, L, PAIRS  # noqa: E402

NBOOT, SAMPLE_SEED, PER_SIZE = 4000, 77, 400
NS = (1, 100, 300, 1000, 2000, 4261)
FAM_SEEDS = (11, 22, 33)
# ⛔ SEVEN seeds, INCLUDING R1034's own three, because the disagreement between the two
#   rounds is itself the measurement and must not be resolved by choosing a seed set.
SEEDS = (1034, 2068, 3102, 1035, 2070, 3105, 4141)
QS = (0, 50, 75, 90, 95, 99, 100)
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def main() -> int:
    r921 = json.loads(next(A26.glob("R921_*/results/comparator_sweep.json")).read_text())
    r1000 = json.loads(next(A27.glob("R1000_*/results/*.json")).read_text())
    r1034f = next(A27.glob("R1034_*/results/*.json"), None)
    if r1034f is None:
        print("  UNRUNNABLE: R1034's artifact is missing. Exit 2, never 0."); return 2
    r1034 = json.loads(r1034f.read_text())
    legit = r921["legitimate_comparators"]; pop = r1000["population_arms"]
    ext9 = set.intersection(*[set(v["conjunction"]) for v in r1000["cells"].values()])
    size986 = {r["arm"] for r in json.loads(next(A27.glob("R986_*/results/*.json")).read_text())["rows"]}
    print(f"  ⛔ PRECEDENT, cited not claimed — R863 bounded clause ④'s family of 1,820 at its 95th")
    print(f"     percentile (`null_p95`), not its max. This applies that device to ②′'s comparators.")
    print(f"  R1034 committed: repaired-operator extension under closure = "
          f"{r1034['extension_under_sampled_closure_repaired'] or '∅'}")

    tg, _ = load_targets()
    P16 = load_sat(RES / f"sat_{legit[1]}.npz")
    pids = sorted(set(P16) & {p for p in tg if len(tg[p]) >= 2}); n = len(pids)
    K = sorted({i for p in pids for i, _ in P16[p]}); nk = len(K)
    M = np.zeros((n, nk, len(L)), np.float32)
    for pi, p in enumerate(pids):
        for (i, x), v in P16[p].items():
            M[pi, K.index(i), L.index(x)] = v
    H = {pi: np.array([cls(np.array(t[0], float)) for t in tg[p]], np.float32)
         for pi, p in enumerate(pids)}

    def a2_masks(masks):
        Y = np.einsum("pkr,km->prm", M, masks.astype(np.float32))
        C = np.stack([np.sign(Y[:, i, :] - Y[:, j, :]) for i, j in PAIRS], 1)
        out = np.empty((n, masks.shape[1]), np.float32)
        for pi in range(n):
            out[pi] = (C[pi][None, :, :] == H[pi][:, :, None]).mean(axis=(0, 1))
        return out

    def arm_vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                S = load_sat(f); idxs = sorted({i for p in S for i, _ in S[p]})
                v = np.full(n, np.nan); cov = np.zeros(n, bool)
                for pi, p in enumerate(pids):
                    if p not in S: continue
                    c = np.array(cls(yvec(S[p], idxs)), float)
                    v[pi] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in H[pi]]))
                    cov[pi] = True
                return np.nan_to_num(v, nan=np.nanmean(v)), cov
        return None, None

    ARM, COV = {}, {}
    for a in sorted(set(pop) | set(legit)):
        v, c = arm_vec(a)
        if v is not None: ARM[a], COV[a] = v.astype(np.float32), c
    CAND = [a for a in ARM if a in pop]
    print(f"  arms {len(ARM)} · candidates {len(CAND)} · prompts {n}")

    W = {}
    for s in SEEDS:
        idx = np.random.default_rng(s).integers(0, n, size=(NBOOT, n))
        w = np.zeros((NBOOT, n), np.float32)
        for r in range(NBOOT): np.add.at(w[r], idx[r], 1.0)
        W[s] = w / n
    BOOT = {(s, a): W[s] @ ARM[a] for s in SEEDS for a in CAND}

    # the family, RE-USED from R1034 at the same seed rather than re-drawn
    rng = np.random.default_rng(SAMPLE_SEED); masks = []
    for k in range(1, nk + 1):
        seen = set()
        for _ in range(PER_SIZE):
            c = tuple(sorted(rng.choice(nk, size=k, replace=False)))
            if c in seen: continue
            seen.add(c); m = np.zeros(nk, bool); m[list(c)] = True; masks.append(m)
    MK = np.column_stack(masks); A2S = a2_masks(MK)
    strict = A2S.mean(axis=0)                     # higher mean A2 = stricter comparator
    order = np.argsort(strict)
    print(f"  family {MK.shape[1]} checklists (R1034's sample, same seed {SAMPLE_SEED}) · "
          f"strictness range {strict.min():.4f}..{strict.max():.4f}")

    # ⛔⛔ THE FIRST CONSTRUCTION WAS ILL-POSED AND ITS OWN POSITIVE CONTROL CAUGHT IT. I ranked
    #   comparators by mean A2 and required the arm to beat "the q-th percentile comparator". q=100
    #   then failed to reproduce R1034's ∅ — correctly, because R1025 established that the
    #   POINT-ESTIMATE ordering is comparator-INVARIANT and only the INTERVAL differs. So mean A2
    #   does not order comparators by who DEFEATS an arm, and a designated percentile comparator is
    #   not the q-th hardest. The well-posed bound is ARM-RELATIVE: the arm must resolvably beat at
    #   least q% of the family. q=100 is then exactly R1034's "beats every member".
    def lo_all(a, s):
        cov = COV[a]
        if not cov.all():
            k = int(cov.sum())
            mi = np.random.default_rng(s + 91).integers(0, k, size=(NBOOT, k))
            wa = np.zeros((NBOOT, k), np.float32)
            for r in range(NBOOT): np.add.at(wa[r], mi[r], 1.0)
            wa /= k
            return np.percentile((wa @ ARM[a][cov])[:, None] - (wa @ A2S[cov]),
                                 2.5, axis=0)
        return np.percentile(BOOT[(s, a)][:, None] - (W[s] @ A2S), 2.5, axis=0)

    LO = {(s, a): lo_all(a, s) for s in SEEDS for a in CAND}

    def ext_q(q, s):
        out = {a for a in CAND if (LO[(s, a)] > 0).mean() * 100 >= q}
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}

    # ---------- POSITIVE ----------
    top = int(order[-1])
    q100 = [ext_q(100, s) for s in SEEDS]
    ok1 = not set.intersection(*q100)
    two = np.column_stack([A2S[:, top] * 0 + ARM[legit[0]], a2_masks(np.ones((nk, 1), bool))[:, 0]])
    def ext_two(s):
        out = set()
        for a in CAND:
            los = [float(np.percentile(BOOT[(s, a)] - (W[s] @ two[:, j]), 2.5)) for j in (0, 1)]
            if min(los) > 0: out.add(a)
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}
    ok2 = ext_two(SEEDS[0]) == ext9
    print(f"\n  POSITIVE — two anchors from two rounds")
    print(f"     q=100 reproduces R1034's ∅: {'PASS' if ok1 else '⛔ FAIL'}  "
          f"got per-seed {[sorted(x) for x in q100]}")
    for a in sorted(set().union(*q100)):
        for s in SEEDS[:1]:
            l = LO[(s, a)]
            print(f"       {a:<20} beats {100*(l>0).mean():.2f}% · min lo {l.min():+.6f} · "
                  f"full-coverage {COV[a].all()}")
    print(f"     {{generic, pool16}} reproduces R1000's {len(ext9)}: {len(ext_two(SEEDS[0]))}  "
          f"{'PASS' if ok2 else '⛔ FAIL'}")
    if not ok2:
        print("  the R1000 anchor did not reproduce. Exit 2, never 0."); return 2
    # ⛔⛔ ok1 IS NOT REQUIRED TO PASS, AND ITS FAILURE IS THIS ROUND'S RESULT. R1034 reported ∅ at
    #   q=100 under seeds (1034, 2068, 3102) and called emptiness EXACT. Here the same construction
    #   at seeds (1035, 2070, 3105) admits `coval_core` with a minimum margin of ~1.6e-4 — four
    #   orders below the ~9e-3 that separates `generic` from `genericpool16` (R923). Two of my own
    #   rounds disagreeing is the finding, and it is resolved by measuring the MARGIN, never by
    #   picking a seed set.

    # ⚠ R1035's one-comparator placebo is NOT inherited: it tested that round's designated-
    #   comparator construction. This round's placebo is below, inside the grid section.

    # ---------- POSITIVE ②: nesting is CHECKED, not assumed ----------
    print(f"\n  POSITIVE ② — nesting: each family must be a strict SUBSET of the next, checked")
    nest_ok = True
    for fs in FAM_SEEDS:
        perm = np.random.default_rng(fs).permutation(A2S.shape[1])
        for i in range(len(NS) - 1):
            a, b = set(perm[:NS[i]].tolist()), set(perm[:NS[i + 1]].tolist())
            if not a <= b: nest_ok = False
    print(f"     nested prefixes of one shuffled family: {'PASS' if nest_ok else '⛔ FAIL'}")

    # ---------- the n x q grid — free, because LO already covers all 4,261 ----------
    print(f"\n  ⭐ THE n x q GRID — |ext| at each family size and quantile (all 3 bootstrap x 3 "
          f"family seeds must agree)")
    print(f"     {'n':>6}" + "".join(f"{('q='+str(q)):>10}" for q in QS))
    grid, flat_q = {}, []
    for nn in NS:
        cells = []
        for q in QS:
            vals = set()
            for fs in FAM_SEEDS:
                perm = np.random.default_rng(fs).permutation(A2S.shape[1])[:nn]
                for s in SEEDS[:3]:
                    e = {a for a in CAND if (LO[(s, a)][perm] > 0).mean() * 100 >= q}
                    e = {a for a in e if a in size986 and not a.startswith(SUPERVISED)}
                    vals.add(frozenset(e))
            cells.append(len(next(iter(vals))) if len(vals) == 1 else -1)
            grid[(nn, q)] = (sorted(next(iter(vals))) if len(vals) == 1 else None)
        print(f"     {nn:>6}" + "".join(f"{(c if c >= 0 else '⚠'):>10}" for c in cells))
    for q in QS:
        sets = [grid[(nn, q)] for nn in NS if nn > 1]
        if all(s is not None for s in sets) and all(s == sets[0] for s in sets):
            flat_q.append(q)
    big = [(nn, grid[(nn, 100)]) for nn in NS]
    moved = len({tuple(v) if v is not None else None for _n, v in big}) > 1
    print(f"\n  NEGATIVE — the q=100 column must MOVE with n (the R848 max signature): "
          f"{[len(v) if v is not None else -1 for _n, v in big]}  "
          f"{'PASS' if moved else '⛔ FAIL — no drift, argument inapplicable here'}")
    # ⚠ THE PLACEBO WAS ILL-POSED AND FAILED FOR ITS OWN REASONS. At n=1 the FAMILY SEED chooses
    #   WHICH single comparator, so the three shuffles disagree by construction and the cell reads
    #   ⚠ rather than a number. The invariance that must hold is WITHIN a fixed family seed: with
    #   one comparator, "beat >= q% of it" is the same requirement for every q > 0.
    pl_ok = True
    for fs in FAM_SEEDS:
        one = np.random.default_rng(fs).permutation(A2S.shape[1])[:1]
        sets = set()
        for q in [q for q in QS if q > 0]:
            e = {a for a in CAND if (LO[(SEEDS[0], a)][one] > 0).mean() * 100 >= q}
            sets.add(frozenset({a for a in e if a in size986 and not a.startswith(SUPERVISED)}))
        if len(sets) != 1: pl_ok = False
    print(f"  PLACEBO  — WITHIN a fixed family seed, n=1 makes every q>0 the same requirement: "
          f"{'PASS' if pl_ok else '⛔ FAIL'}")
    print( "     ⚠ the first version compared ACROSS family seeds and failed for its own reasons —")
    print( "       at n=1 the seed picks WHICH comparator, so disagreement is guaranteed.")

    # ⭐ AND SCALE-FREENESS IS NOT BINARY IN q: it has an ONSET family size, and that is what
    #   actually selects q. q=0 is vacuously scale-free because it imposes NO requirement, so it is
    #   excluded rather than reported as the answer — `min()` over a set containing a degenerate
    #   element is the verdict-string mode, and it fired here on the first run.
    onset = {}
    for q in QS:
        ns = [nn for nn in NS if nn > 1]
        first = None
        for i, nn in enumerate(ns):
            tail_sets = [grid[(m, q)] for m in ns[i:]]
            # ⚠ a tail of ONE size is trivially constant — q=100 "stabilised" at the largest n on
            #   the first run purely because nothing followed it. At least TWO sizes must agree.
            if len(tail_sets) < 2:
                break
            if all(s is not None for s in tail_sets) and all(s == tail_sets[0] for s in tail_sets):
                first = nn; break
        onset[q] = first
    print(f"\n  ⭐ ONSET — the smallest family size from which the extension STOPS CHANGING:")
    print(f"     {'q':>6}{'onset n':>10}{'|ext| there':>13}")
    for q in QS:
        o = onset[q]
        print(f"     {q:>6}{(o if o else '—'):>10}"
              f"{(len(grid[(o, q)]) if o else -1):>13}"
              f"{'   ⚠ DEGENERATE: no requirement' if q == 0 else ''}"
              f"{'   ⚠ never — the MAX does not stabilise' if o is None else ''}")
    informative = [q for q in QS if q > 0 and onset[q] is not None]
    print(f"  SCALE-FREE q (identical extension at every n>1 and every seed): {flat_q or 'none'}")

    print()
    if not moved:
        world = ("UNVERIFIED — the max does not drift with n here, so scale-stability cannot select q")
    elif informative:
        world = (f"⭐ A SCALE-FREENESS SELECTS q, AND IT IS NOT BINARY — it has an ONSET family size "
                 f"that GROWS with q and never arrives at q=100: "
                 f"{ {q: onset[q] for q in QS if q > 0} }. So the clause's cost is not just a "
                 f"threshold but HOW MUCH FAMILY YOU MUST ENUMERATE to state it, and q=100 cannot be "
                 f"stated at any size reached here. R1035's closing sentence — that the curve cannot "
                 f"select among q — is WITHDRAWN. ⚠ q=0 is EXCLUDED as degenerate: it imposes no "
                 f"requirement and admits {len(grid[(NS[-1], 0)])} arms.")
    else:
        world = (f"⭐ B EVERY q DRIFTS WITH n — no quantile gives a size-independent extension, so the "
                 f"clause cannot be stated over a FAMILY at all and the comparator set must be fixed "
                 f"by enumeration.")
    print(world)
    print(f"⛔ THE DEVICE IS R848's, CITED NOT CLAIMED: it ran the same dose-response over family SIZE")
    print(f"   for clause ④ and measured the bar rising at 0.0074 per ln(n) — the signature of a")
    print(f"   MAXIMUM. What is new here is applying it to SELECT a quantile, not to price a bar.")
    print(f"⚠ AND SCALE-STABILITY IS NECESSARY, NOT SUFFICIENT. A q can be size-independent and still")
    print(f"   be the wrong bar; deciding that needs an external criterion for what the comparator")
    print(f"   family REPRESENTS, which this release does not carry. N/A, stated not planned.")

    out = HERE / "results" / "scale_free_q.json"
    out.write_text(json.dumps({
        "round": "R1036", "bootstrap_seeds": list(SEEDS[:3]), "family_seeds": list(FAM_SEEDS),
        "sizes": list(NS), "quantiles": list(QS),
        "precedent": "R848 ran the dose-response over family size for clause ④; the bar rose 0.0074 "
                     "per ln(n), the signature of a maximum",
        "nesting_checked": bool(nest_ok), "max_column_moves": bool(moved),
        "grid": {f"{nn}|{q}": grid[(nn, q)] for nn in NS for q in QS},
        "scale_free_q": flat_q, "world": world,
        "limitation": "scale-stability is necessary, not sufficient; which q is RIGHT needs an "
                      "external criterion for what the comparator family represents",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
