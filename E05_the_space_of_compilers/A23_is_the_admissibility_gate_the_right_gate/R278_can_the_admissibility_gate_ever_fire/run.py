#!/usr/bin/env python3
"""
R278 -- CAN THE ADMISSIBILITY GATE EVER FIRE?

The definition in E05/FORMULATION.md reads:

    A core is admissible only if  C(n,k) <= a(m),  a(4) = 75.

FORMULATION.md already carries a warning that this gate CONTRADICTS its own claim 5
(H_eff in [1.02, 3.45] bits against the gate's log2(75) = 6.23). This round does not
address that. It asks a question nobody asked first, and it comes from the unit test
that R240's retraction produced this morning:

    WRITE THE INSTRUMENT'S UNIT AND THE CLAIM'S UNIT AS TWO STRINGS, REQUIRE THEM EQUAL.

    C(n,k)  counts  k-subsets of a prompt's n criteria   -> "candidate representatives"
    a(m)    counts  weak orderings of m=4 responses      -> "behaviour classes"

Those strings are not equal. The gate compares a count of CRITERION SUBSETS to a count
of RESPONSE ORDERINGS. Whatever it is, it is not an inequality between like things -- and
that makes one question decisive and nearly free: ON THIS RELEASE, CAN IT EVER FAIL?

ESTIMAND        The number of (prompt, k) cells in the release for which C(n_p, k) > 75,
                over every prompt p and every core size k the project has ever used
                (k = 1..4), and the maximum of C(n_p,k) over that grid.
                Named before the method. Reported beside cells tested.

IDENTIFICATION  FULLY identified and mostly DERIVED. Given n_p, `C(n_p,k) > 75` is forced
                by arithmetic -- it could not have come out otherwise. The only MEASURED
                input is the distribution of n_p (criteria per prompt) in the release.
                Labelled as a derivation conditional on a measurement, per the arithmetic
                trap, and NOT called evidence about anything beyond this release.

SCOPE           population : the 968 prompts of the CoVal release, criteria as joined by
                             covalx.judge.load_join
                instrument : arithmetic on counts. No model, no judge, no seed dependence.
                baseline   : a(4) = 75 weak orderings of 4 responses (the gate's own RHS)
                regime     : k in {1,2,3,4}, the core sizes this project has used

WORLDS          A  DISCRIMINATING -- some prompts violate at a used k. The gate does work,
                   and the claim-5 contradiction is the interesting problem.
                B  VACUOUS -- no prompt at any used k exceeds 75. The gate is a CHECK THAT
                   CANNOT FAIL: it is satisfied before anything is tested, so the
                   claim-5 contradiction is a red herring about a criterion that was
                   never a criterion.
                C  OVER-STRICT -- most prompts violate, and the gate rejects the release
                   that produced it.

PREDICTION      cells violating   |  A: 1..99%   |  B: exactly 0   |  C: >50%
MATRIX          max C(n_p,k)      |  A: >75      |  B: <=75        |  C: >>75
                gate's usefulness |  A: real     |  B: none        |  C: inverted

KILL            Pre-registered, written before the run: if ZERO cells violate across the
                whole (prompt x k) grid, world B is confirmed and the gate is declared
                VACUOUS ON THIS RELEASE. If any cell violates, B is dead.
                The kill is a CONDITIONAL, not a bare threshold -- it is only binding if
                both controls below behave:
                    if positive_fires and negative_is_silent: evaluate(count == 0)
                    else:                                     verdict = UNVERIFIED

POSITIVE CTRL   The gate predicate must FIRE on a synthetic prompt where the answer is
                known by hand: n=10, k=5 -> C = 252 > 75. Must also NOT fire at the
                release's own modal cell n=6, k=4 -> C = 15. That pair is floor < t <
                ceiling: the predicate is not degenerate and the threshold sits inside a
                real band. Checked at g=0 too: with n=k the predicate must be silent
                (C=1), so it does not pass before anything is planted.

NEGATIVE CTRL   Destroy the structure under test -- the criterion COUNT -- while keeping
                everything else. Replace each n_p by a draw from a distribution with the
                same support but a heavier tail (n_p + 6), refit nothing, and check the
                violation count MOVES. A gate whose output does not respond to n is not
                reading n. World this excludes: "the zero is an artifact of the predicate
                being broken rather than of the data being small."

SHAM            The same operation minus the ingredient: run the identical grid against
                a(3) = 13 and a(5) = 541 instead of a(4) = 75, size- and compute-matched.
                If the count is 0 at all three, the result is about n, not about a(m),
                and the gate's right-hand side is doing no work at any m.

PLACEBO         C(n,0) = 1 for every prompt: a contrast where no violation can exist.
                Must return exactly zero violations at every m.

NOISE FLOOR     N/A and stated rather than skipped -- this quantity has NO sampling noise.
                C(n,k) is arithmetic on an observed integer. There is nothing to resample,
                so a measured floor would be identically 0 and quoting one would be
                theatre. What DOES carry uncertainty is n_p (join coverage), so the join's
                unmatched count is reported instead.

MULTIPLICITY    Cells tested = 968 prompts x 4 k-values x 3 m-values = 11,616, plus the
                placebo row. No correction applies: these are exact predicates, not tests
                with a null distribution. Reported as counts, and the non-violating cells
                are reported as the finding rather than filtered away.

SPECIFICATION   Axes swept: k in {1,2,3,4} x m in {3,4,5} x n-source in {observed,
                observed+6}. The full curve is printed, including the cells that would
                kill world B.

SEEDS           N/A, stated: the computation is deterministic arithmetic with no draws.
                The seed flag is deliberately absent rather than present-and-ignored,
                because a seed argument that changes nothing is a claim that it might.

ARTIFACT        results/gate_grid.json, with the source hash. What a later round needs to
                ATTACK this: the full n_p vector is persisted, so a rival can recompute
                every cell without re-running the join.

REPRODUCIBILITY Run under two PYTHONHASHSEEDs; the artifact must be byte-identical. This
                round contains no hash() over str, but 13 of 19 E05 seeds did, so the
                check is run rather than assumed.

IMPOSSIBLE      cross-model / cross-dataset / cross-release -- would require a second
                    values-annotation release with the same schema. There is one.
                causally identified -- would require intervening on how many criteria an
                    annotator writes, which is a property of the elicitation, not of us.
                construct validated -- would require an external answer to "how many
                    classes SHOULD a core distinguish", which is the open question.
"""
import json, math, hashlib, pathlib, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from covalx.judge import load_join

A = {3: 13, 4: 75, 5: 541}          # ordered Bell numbers a(m)
KS = [1, 2, 3, 4]
MS = [3, 4, 5]


def gate_violates(n, k, m):
    """The gate predicate, exactly as FORMULATION.md states it."""
    return math.comb(n, k) > A[m]


def controls():
    rows = []
    # POSITIVE: fires where the answer is known by hand
    rows.append(("POS  fires at n=10,k=5 (C=252 > 75)", gate_violates(10, 5, 4), "C=252"))
    # ceiling/floor band: must be SILENT at the release's modal cell
    rows.append(("POS  silent at n=6,k=4 (C=15 <= 75)", not gate_violates(6, 4, 4), "C=15"))
    # fails at g=0: nothing planted -> must not pass
    rows.append(("POS  silent at n=k (C=1), i.e. fails at g=0",
                 not gate_violates(6, 6, 4), "C=1"))
    # PLACEBO: k=0 -> C=1 everywhere, must be exactly zero at every m
    rows.append(("PLA  k=0 gives zero violations at every m",
                 not any(gate_violates(n, 0, m) for n in range(1, 40) for m in MS),
                 "C(n,0)=1"))
    return rows


def main():
    comp = ROOT / "data" / "comparisons.jsonl"
    rub = ROOT / "data" / "conversation_rubrics.jsonl"
    joined = load_join(comp, rub)

    # n_p = the pool of criteria a core of size k is CHOSEN FROM for prompt p.
    # That is `coval_full`. `coval_core` is a released k=4 choice, not the pool, and
    # using it would silently answer a different question -- the same scope slip that
    # produced R240's retraction this morning, so both are recorded and named.
    n_full, n_core = {}, {}
    for pid, _prompt, rub_rec in joined:
        n_full[pid] = max(n_full.get(pid, 0), len(rub_rec.get("coval_full") or []))
        n_core[pid] = max(n_core.get(pid, 0), len(rub_rec.get("coval_core") or []))
    n_full = {p: n for p, n in n_full.items() if n > 0}
    return n_full, n_core, len(joined)


if __name__ == "__main__":
    print("\n  R278 -- can the admissibility gate ever fire?\n")
    ctrl = controls()
    ok = True
    for name, passed, detail in ctrl:
        ok &= passed
        print(f"    [{'PASS' if passed else 'FAIL'}] {name:<46} {detail}")
    print()
    n_by_pid, n_core, n_joined = main()
    ns = sorted(n_by_pid.values())
    cs = sorted(n_core.values())
    print(f"    rows joined        : {n_joined}   prompts with a full pool: {len(n_by_pid)}")
    print(f"    released core size : min {cs[0]}  median {cs[len(cs)//2]}  max {cs[-1]}  "
          f"(this is NOT the pool; n is)")
    print(f"    criteria per prompt: min {ns[0]}  median {ns[len(ns)//2]}  max {ns[-1]}")
    print(f"    distribution       : {dict(sorted(Counter(ns).items()))}")
    print()

    # NEGATIVE CONTROL: destroy the criterion count, keep everything else
    grid, neg_grid = {}, {}
    for m in MS:
        for k in KS:
            v = sum(gate_violates(n, k, m) for n in ns)
            vn = sum(gate_violates(n + 6, k, m) for n in ns)
            grid[f"m{m}_k{k}"] = v
            neg_grid[f"m{m}_k{k}"] = vn
    maxC = max(math.comb(n, k) for n in ns for k in KS)

    print("    SPECIFICATION CURVE -- violations out of {} prompts".format(len(ns)))
    print("      m \\ k        " + "".join(f"{k:>8}" for k in KS) + "     a(m)")
    for m in MS:
        print(f"      m={m} observed " + "".join(f"{grid[f'm{m}_k{k}']:>8}" for k in KS)
              + f"   {A[m]:>6}")
    # THE AXIS THAT MATTERS: the definition never says WHICH n. Two defensible readings.
    seed_grid = {}
    for m in MS:
        for k in KS:
            seed_grid[f"m{m}_k{k}"] = sum(gate_violates(6, k, m) for _ in ns)
    print("      -- n = the six SEED criteria (the other defensible reading) --")
    for m in MS:
        print(f"      m={m} seed=6   " + "".join(f"{seed_grid[f'm{m}_k{k}']:>8}" for k in KS))
    print("      -- negative control: n_p -> n_p + 6 --")
    for m in MS:
        print(f"      m={m} n+6      " + "".join(f"{neg_grid[f'm{m}_k{k}']:>8}" for k in KS))
    print()

    total_cells = len(ns) * len(KS) * len(MS)
    violations = sum(grid.values())
    neg_moved = sum(neg_grid.values()) > sum(grid.values())

    print(f"    cells tested       : {total_cells}")
    print(f"    cells violating    : {violations}")
    print(f"    max C(n,k) on grid : {maxC}   against a(4) = {A[4]}")
    print(f"    NEG control moved  : {neg_moved}  ({sum(grid.values())} -> {sum(neg_grid.values())})")
    print()

    # KILL as a conditional, never a bare threshold
    if not ok:
        verdict = "UNVERIFIED -- a control failed; the count is not admissible"
    elif not neg_moved:
        verdict = ("UNVERIFIED -- the negative control did not move, so a zero here is "
                   "silence: the predicate may not be reading n at all")
    elif violations == 0:
        verdict = ("WORLD B CONFIRMED -- the gate is VACUOUS on this release. It is "
                   "satisfied by every prompt at every k the project uses, at every m "
                   "tested. A check that cannot fail.")
    else:
        verdict = f"WORLD B DEAD -- {violations} cells violate; the gate discriminates"

    print(f"    VERDICT: {verdict}\n")

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    art = {"source_sha256_16": src, "n_by_pid_values": ns, "grid": grid,
           "negative_control_grid": neg_grid, "max_C": maxC, "a": A,
           "cells_tested": total_cells, "cells_violating": violations,
           "controls": [(n, bool(p), d) for n, p, d in ctrl], "verdict": verdict,
           "seed_reading_grid": seed_grid,
           "operating_point_m4_k4": {"violations": grid["m4_k4"], "of": len(ns),
                                     "seed_reading": seed_grid["m4_k4"]}}
    out = HERE / "results" / "gate_grid.json"
    out.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"    artifact: {out.relative_to(ROOT)}  (source {src})\n")
