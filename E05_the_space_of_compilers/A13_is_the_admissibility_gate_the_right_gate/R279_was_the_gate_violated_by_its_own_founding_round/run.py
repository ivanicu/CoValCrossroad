#!/usr/bin/env python3
"""
R279 -- WAS THE GATE VIOLATED BY THE ROUND THAT PROPOSED IT?

R278 showed the gate `C(n,k) <= a(m)` is UNDEFINED: its left-hand side admits two
readings of `n` that give 0% and 91.7% violation at the operating point. R278's closing
note said the tie is broken by a FACT ABOUT CODE ALREADY RUN, not by a preference --
which pool did the recovery experiments actually draw from?

Answered by reading the source, not by memory:
    R248, R252, R253 all draw from `coval_full`, bounded NMIN,NMAX = 6,14, NPROMPT=250,
    at KS = [1,2,3] (R253: [1,2]). Extracted with an AST walk, not a grep, because
    `NMIN, NMAX, NPROMPT = 6, 14, 250` is a TUPLE assignment and the obvious pattern
    `NPROMPT *= *[0-9]+` returns 6 -- the fourth loose pattern of the day, caught only
    because 6 prompts is an absurd population.

So the pool is `coval_full`. That makes a sharper question available, and it needs no
re-run at all: R248's own persisted artifact records `C` for every (prompt, k) cell it
studied. THE ROUND THAT PROPOSED THE GATE RECORDED WHETHER ITS OWN GATE HELD.

ESTIMAND        The number of cells in R248's own study population -- its 250 selected
                prompts x its own k in {1,2,3} -- for which C(n,k) > a(4) = 75, i.e. the
                gate R248 introduced is violated by R248's own data. Reported as a count
                and a share, beside cells tested. Named before the method.

IDENTIFICATION  FULLY identified, and this is the strongest form available here: the
                quantity is read from the founding round's persisted artifact, so it is
                not a reconstruction of its population but the population itself. No
                join, no model, no draw.
                DERIVATION, conditional on the artifact: given the recorded n, the
                predicate is arithmetic. Labelled per the arithmetic trap.

SCOPE           population : the 250 prompts R248 selected (coval_full, n in [6,14],
                             filtered to items with scores and full saturation coverage)
                instrument : R248's own results/gate_test.json, cross-checked against
                             math.comb
                baseline   : a(4) = 75, R248's own capacity constant (it records 75 and
                             6.22881869049588 bits, so the baseline is its own, not mine)
                regime     : k in {1,2,3}. R248 never ran k=4, so nothing here speaks to
                             k=4 and that is stated rather than extrapolated.

WORLDS          A  THE GATE HELD IN ITS OWN ROUND -- 0 cells violate. The gate was
                   proposed by data consistent with it, and R278's 91.7% comes entirely
                   from prompts and k-values R248 excluded.
                B  THE GATE WAS VIOLATED BY ITS OWN FOUNDING DATA -- some cells violate.
                   Then the gate was never satisfied by the evidence offered for it, and
                   the artifact recording that has been on disk unread since R248.
                C  UNREADABLE -- the artifact's C is not C(n,k), so the field means
                   something else and this round says nothing.

PREDICTION      cells violating |  A: 0       | B: >0        | C: n/a
MATRIX          C == comb(n,k)  |  A: yes     | B: yes       | C: no
                what it implies |  A: gate is scope-limited  | B: gate never held | C: --

KILL            Pre-registered, a conditional and not a bare threshold:
                    if C_matches_comb and negative_control_moves:
                        evaluate(violations == 0)      # world A
                    else:
                        verdict = UNVERIFIED           # world C, never an acquittal

POSITIVE CTRL   ① The artifact's own `C` must equal math.comb(n,k) in EVERY cell. This is
                   a cross-check between two independent code paths -- R248's and
                   Python's -- on a quantity whose right answer is fixed. If it fails,
                   the field is not what its name says and world C fires.
                ② The predicate must fire on a hand-known case (n=10,k=5 -> 252 > 75) and
                   be silent at n=6,k=4 -> 15, so the threshold sits inside a real band.
                ③ Fails at g=0: silent at n=k (C=1), so it is not satisfied before
                   anything is planted.

NEGATIVE CTRL   Destroy the criterion count while keeping the artifact's structure:
                n -> n+6 for every cell. The violation count must MOVE. World it excludes:
                "the count is an artifact of a predicate that never reads n."
                Built by transforming the real artifact, not by inventing cases -- a
                control validated only against cases I invented is validated against my
                imagination.

SHAM            The same operation with the ingredient a(m) replaced: a(3)=13, a(5)=541,
                same cells, same compute. If the count is unchanged across all three, the
                right-hand side is doing no work.

PLACEBO         k=0 is not in the artifact, so the placebo is the k=1 column under a(5):
                C(n,1) = n <= 14 < 541, which MUST be exactly zero violations. A contrast
                where no effect can exist.

NOISE FLOOR     N/A and stated, not skipped: the quantity is a comparison of two integers
                already on disk. There is nothing to resample; a measured floor would be
                identically zero and quoting one would be theatre. The uncertainty that
                DOES exist is R248's population selection, which is not re-run here and
                therefore not re-estimated -- its 250 prompts are taken as given, which is
                the point.

MULTIPLICITY    Cells tested = 250 prompts x 3 k-values x 3 m-values = 2,250, plus the
                placebo column. No correction: exact predicates, no null distribution.
                Non-violating cells reported beside violating ones.

SPECIFICATION   Axes swept: k in {1,2,3} (R248's own) x m in {3,4,5} x n-source in
                {artifact, artifact+6}. Whole curve printed including cells that kill each
                world.

SEEDS           N/A, deliberately absent rather than present-and-ignored. No draws.

ARTIFACT        results/founding_round_gate.json with source hash and the full (k, n, C)
                table, so a rival can recompute every cell without reading R248.

REPRODUCIBILITY Two PYTHONHASHSEEDs, byte-identical.

IMPOSSIBLE      k=4 -- R248 never ran it, and this round cannot invent the cells.
                    Would require re-running R248's selection at k=4.
                cross-release -- one release exists.
                causally identified -- would require intervening on the criterion count.
"""
import json, math, hashlib, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R248 = (ROOT / "E05_the_space_of_compilers"
             / "A13_is_the_admissibility_gate_the_right_gate"
             / "R248_capacity_versus_realised_alphabet" / "results" / "gate_test.json")
A = {3: 13, 4: 75, 5: 541}


def main():
    d = json.loads(R248.read_text())
    cap = d["capacity"]
    cells = [(int(k), r["n"], r["C"]) for k, rows in d["per_prompt"].items() for r in rows]

    ctrl = []
    # POS 1 -- the artifact's C must BE C(n,k), checked in every cell
    bad = [(k, n, C) for k, n, C in cells if C != math.comb(n, k)]
    ctrl.append(("POS  artifact C == comb(n,k) in every cell", not bad,
                 f"{len(cells)-len(bad)}/{len(cells)} agree"))
    # POS 2 -- band
    ctrl.append(("POS  predicate fires at n=10,k=5 (C=252>75)", math.comb(10, 5) > 75, "252"))
    ctrl.append(("POS  silent at n=6,k=4 (C=15<=75)", not math.comb(6, 4) > 75, "15"))
    # POS 3 -- fails at g=0
    ctrl.append(("POS  silent at n=k (C=1): not passing at g=0", not math.comb(6, 6) > 75, "1"))
    # the baseline is R248's own, not mine
    ctrl.append(("POS  baseline is R248's own capacity constant", cap == A[4], f"a(4)={cap}"))

    grid, neg = {}, {}
    for m in A:
        for k in sorted({c[0] for c in cells}):
            sel = [(n, C) for kk, n, C in cells if kk == k]
            grid[f"m{m}_k{k}"] = sum(C > A[m] for _n, C in sel)
            neg[f"m{m}_k{k}"] = sum(math.comb(n + 6, k) > A[m] for n, _C in sel)

    # PLACEBO -- k=1 under a(5): C = n <= 14 < 541, must be exactly 0
    ctrl.append(("PLA  k=1 under a(5) is exactly zero", grid.get("m5_k1", -1) == 0,
                 f"{grid.get('m5_k1')}"))

    ok = all(p for _n, p, _d in ctrl)
    moved = sum(neg.values()) > sum(grid.values())
    return d, cells, grid, neg, ctrl, ok, moved


if __name__ == "__main__":
    print("\n  R279 -- was the gate violated by the round that proposed it?\n")
    d, cells, grid, neg, ctrl, ok, moved = main()
    for name, passed, detail in ctrl:
        print(f"    [{'PASS' if passed else 'FAIL'}] {name:<48} {detail}")
    ks = sorted({c[0] for c in cells})
    ns = [n for _k, n, _C in cells]
    print(f"\n    R248's own population : {d['n_prompts']} prompts, "
          f"n in [{min(ns)}, {max(ns)}], k in {ks}")
    print(f"    cells in the artifact : {len(cells)}\n")
    print("    SPECIFICATION CURVE -- violating cells of {} per k".format(len(cells)//len(ks)))
    print("      m \\ k       " + "".join(f"{k:>9}" for k in ks) + "      a(m)")
    for m in A:
        print(f"      m={m} artifact" + "".join(f"{grid[f'm{m}_k{k}']:>9}" for k in ks)
              + f"   {A[m]:>7}")
    print("      -- negative control: n -> n+6 --")
    for m in A:
        print(f"      m={m} n+6     " + "".join(f"{neg[f'm{m}_k{k}']:>9}" for k in ks))

    tested = len(cells) * len(A)
    viol = sum(grid.values())
    viol4 = sum(grid[f"m4_k{k}"] for k in ks)
    n4 = len(cells)
    print(f"\n    cells tested          : {tested}")
    print(f"    cells violating       : {viol}")
    print(f"    AT R248's OWN a(4)=75 : {viol4} of {n4} = {viol4/n4:.4f}")
    print(f"    NEG control moved     : {moved} ({sum(grid.values())} -> {sum(neg.values())})")

    if not ok:
        verdict = "UNVERIFIED -- a control failed; no count is admissible (world C)"
    elif not moved:
        verdict = "UNVERIFIED -- the negative control did not move; the count is silence"
    elif viol4 == 0:
        verdict = "WORLD A -- the gate held in its own founding round"
    else:
        verdict = (f"WORLD B -- the gate was VIOLATED BY ITS OWN FOUNDING DATA in "
                   f"{viol4} of {n4} cells ({viol4/n4:.1%}), recorded in R248's artifact "
                   f"and unread since")
    print(f"\n    VERDICT: {verdict}\n")

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    art = {"source_sha256_16": src, "cells": cells, "grid": grid,
           "negative_control_grid": neg, "a": A, "cells_tested": tested,
           "cells_violating_all_m": viol, "violating_at_a4": viol4, "n_cells": n4,
           "controls": [(n, bool(p), dd) for n, p, dd in ctrl], "verdict": verdict}
    out = HERE / "results" / "founding_round_gate.json"
    out.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"    artifact: {out.relative_to(ROOT)}  (source {src})\n")
