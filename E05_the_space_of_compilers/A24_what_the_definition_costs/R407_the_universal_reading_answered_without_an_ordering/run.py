"""R407 -- the universal reading, answered from ONE cell, and the fourth thing the sentence does not say.

R405 computed R360's top sweep cell and refused to interpret it, because calling it "the strictest
reading" presupposes an ordering the sweep does not provide. R406 then showed R327's "universal"
reading was instantiated at a p99 bar, 0.0028733259 below the true maximum.

⛔ BUT A SINGLE-CELL CLAIM DOES NOT NEED AN ORDERING, AND THAT IS THE OPENING R405 LEFT. "No
   label-free arm beats the maximum blind set of its own size" is a statement about ONE cell. It
   needs only that the cell's reference IS that maximum -- not that the cells are ordered by
   strictness. R405 blocked the ORDERING claim correctly and, in doing so, blocked a weaker claim
   that never depended on it.

⭐ AND THE REFERENCE IS VERIFIABLE FROM SOURCE WITHOUT A RUN. R360's `ref_at(k, p)` sorts the blind
   sets of size k by mean and indexes `round(p/100 * (len-1))`, so p=100 returns `order[-1]` -- the
   single highest-scoring prompt-blind set of that arm's own size. That is the literal referent of
   "every prompt-blind set of that size", read off the code rather than assumed from the name.

⛔ AND HERE IS THE FOURTH UNDER-SPECIFICATION, WHICH IS THE REASON THIS ROUND IS NOT A VICTORY LAP.
   R360's `admits(a, ref)` returns `e > 0 and abs(e) >= ZEFF * se`. The definition's sentence says
   "scores BETTER THAN". The code says "scores SIGNIFICANTLY better than". Those are different tests,
   the coded one is STRICTER, and the difference runs in the direction that makes the definition look
   more demanding than it reads. So the emptiness at the top cell is an answer to the STRICT test,
   and the LITERAL test has never been run. Same shape as R406's finding, one level down.

⛔ ARITHMETIC TRAP. Reading a percentile index off source is not a measurement -- `p=100 -> order[-1]`
   is what the expression evaluates to and could not be otherwise. It is a DERIVATION and is labelled
   one. What is NOT forced is the CELL CONTENTS, which R360 measured, and the per-arm brackets below,
   which are read from where each arm disappears along the committed grid.

ESTIMAND        (A) whether R360's p=100 reference is the per-k MAXIMUM, established from source;
                (B) the admitted set at that cell, split into label-free and label-reading;
                (C) for each arm clause ② admits, the highest committed grid point at which it is
                    still admitted -- a per-arm BRACKET on where it sits against the blind
                    distribution, which no round has reported at arm resolution.

IDENTIFICATION  (A) exact, by reading the expression. (B) exact, from R360's committed cell.
                (C) BRACKETED to the 45-point grid, never a point: an arm last admitted at 98.5
                    sits somewhere between the 98.5th and 100th percentile and the artifact cannot
                    say where. NOT identified: the LITERAL `e > 0` test, which needs the arrays.

SCOPE           population: R360's 42 arms · instrument: R360's committed sweep + its source ·
                baseline: the per-k maximum blind set · regime: the STRICT test, `e > 0 and
                |e| >= ZEFF*se`, which is not the sentence's test.

WORLDS
  W-UNIVERSAL-EMPTY   no label-free arm is admitted at the maximum reference. Then, under the strict
                      test, nothing satisfies "better than every prompt-blind set of its size" except
                      arms that read the answer.
  W-UNIVERSAL-NONEMPTY  some label-free arm clears the maximum. Then the definition's plain-English
                      reading is satisfiable without label access and the campaign has a survivor.

PREDICTION MATRIX
  W-UNIVERSAL-EMPTY    -> admitted at p=100 minus label-readers is empty
  W-UNIVERSAL-NONEMPTY -> that difference is non-empty, arms named

PRE-REGISTERED KILL -- conditional on the source check, never on the cell alone.
    if ref_at_100_is_the_max_by_source and the_top_cell_exists:
        if (admitted@100 - labels) == set() -> W-UNIVERSAL-EMPTY
        else -> W-UNIVERSAL-NONEMPTY, arms named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
    ⚠ EITHER VERDICT IS SCOPED TO THE STRICT TEST and must say so in its own sentence.

CONTROLS
  SOURCE (+)     the p=100 index expression must evaluate to the last element under a reproduced
                 sort. Checked by re-implementing the index arithmetic on a synthetic array of known
                 order, so the claim `p=100 means max` is executed rather than asserted.
  SOURCE (-)     the same expression at p=0 must return the FIRST element. Without it, an expression
                 that always returns the last would pass the positive check.
  ORDERING-FREE  the round must NOT use monotonicity anywhere. Asserted by construction: only the
                 p=100 cell decides the verdict, and the brackets in (C) are labelled as grid
                 positions rather than as an ordering of strictness.
  CELL EXISTS    a p=100 cell must be present in the committed sweep, else exit 2.

MULTIPLICITY    1 deciding cell; 9 per-arm brackets, all printed.
SEEDS           none.
ARTIFACT        results/r407_universal_reading.json with the source hash.

IMPOSSIBLE HERE
  the LITERAL `e > 0` test        -- needs R360's arrays; named as the next step and NOT approximated.
  a numeric cross-check of ref_at(4,100) against R331's committed max -- would need R360's `build(k)`,
                                     which loads and scores; the source-level check stands in, and the
                                     numeric one is recorded as OWED.
  a point estimate of any arm's percentile -- the grid is 45 points. Bracketed.
  a second release                -- two corpora.

EXIT
    0  the source check holds and the cell is reported
    1  the source check fails -- UNVERIFIED
    2  the cell or artifact is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R360D = HERE.parent / "R360_which_clause_is_load_bearing"
R360 = R360D / "results" / "r360_clause_ledger.json"
R331 = HERE.parent / "R331_what_makes_a_clause2_reference_safe" / "results" / "reference_safety.json"


def idx_at(p, n):
    """R360's own index arithmetic, re-implemented so `p=100 means max` is EXECUTED, not asserted."""
    return min(int(round(p / 100 * (n - 1))), n - 1)


def main() -> int:
    for f in (R360, R331):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    d = json.loads(R360.read_text())
    a331 = json.loads(R331.read_text())
    sweep = {c["pct"]: c for c in d["sweep"]}
    if 100.0 not in sweep:
        print("  UNRUNNABLE: no p=100 cell in the committed sweep. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R407 · the universal reading, from ONE cell, no ordering required   HEAD {head}\n")
    print("  ⛔ R405 BLOCKED THE ORDERING CLAIM CORRECTLY, AND BLOCKED A WEAKER ONE WITH IT.")
    print("     `No label-free arm beats the maximum blind set of its own size` is a statement about")
    print("     ONE cell. It needs the cell's reference to BE that maximum — not the cells to be")
    print("     ordered by strictness.\n")

    # ---- SOURCE CONTROLS: execute the index arithmetic, don't assert it ---------------------------
    n = 1820
    hi_ok = idx_at(100.0, n) == n - 1
    lo_ok = idx_at(0.0, n) == 0
    src = (R360D / "run.py").read_text()
    expr_present = "order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)]" in src
    print("  CONTROLS on the claim `p=100 means the maximum`")
    print(f"    SOURCE (+)   the index expression at p=100 over n={n:,} returns element "
          f"{idx_at(100.0, n):,} (last is {n-1:,}): {hi_ok}   {'PASS' if hi_ok else 'FAIL'}")
    print(f"    SOURCE (-)   the same expression at p=0 returns element {idx_at(0.0, n)}: {lo_ok}   "
          f"{'PASS' if lo_ok else 'FAIL — an expression always returning the last would pass (+)'}")
    print(f"    EXPRESSION   R360's line is present verbatim in its source: {expr_present}   "
          f"{'PASS' if expr_present else 'FAIL — I am checking arithmetic R360 does not do'}")
    if not (hi_ok and lo_ok and expr_present):
        print("\n  UNVERIFIED — the source check failed. Exit 1."); return 1
    print(f"    -> `ref_at(k, 100)` sorts the blind sets of size k by mean and takes the LAST, i.e.")
    print(f"       the single highest-scoring prompt-blind set OF THAT ARM'S OWN SIZE. That is the")
    print(f"       literal referent of `every prompt-blind set of that size`.")

    # ---- (B) the deciding cell --------------------------------------------------------------------
    top = sweep[100.0]
    adm, lab = set(top["admitted"]), set(top["labels"])
    free = sorted(adm - lab)
    print(f"\n  (B) THE DECIDING CELL — p = 100, the per-k MAXIMUM")
    print(f"      admitted            : {sorted(adm)}")
    print(f"      of which read labels: {sorted(lab)}")
    print(f"      LABEL-FREE ADMITTED : {free}   (n={len(free)})")

    # ---- (C) per-arm brackets ---------------------------------------------------------------------
    c2 = sorted(set(d["clause2_admits"]))
    print(f"\n  (C) PER-ARM BRACKETS — the highest committed grid point at which each clause-② arm is")
    print(f"      still admitted. A GRID POSITION, not a strictness ordering, and not a point")
    brackets = {}
    grid = sorted(sweep)
    for a in c2:
        last = None
        for p in grid:
            if a in set(sweep[p]["admitted"]):
                last = p
        nxt = next((p for p in grid if last is not None and p > last), None)
        brackets[a] = [last, nxt]
        tag = "reads labels" if a in lab else ""
        print(f"      {a:<20} last admitted at pct {last:>6.1f}"
              + (f", gone by {nxt:>6.1f}" if nxt is not None else ", still in at the maximum")
              + (f"   [{tag}]" if tag else ""))

    # ---- VERDICT ----------------------------------------------------------------------------------
    print()
    if not free:
        v = "W_UNIVERSAL_EMPTY"
        print(f"  W-UNIVERSAL-EMPTY — at the maximum prompt-blind set of its own size, NO label-free")
        print(f"  arm is admitted. The only arms that satisfy `better than every prompt-blind set of")
        print(f"  that size` are the {len(lab)} that read the prompt's own rankings.")
    else:
        v = "W_UNIVERSAL_NONEMPTY"
        print(f"  W-UNIVERSAL-NONEMPTY — {free} clears the maximum without reading labels.")

    print(f"\n  ⛔ AND THE VERDICT IS SCOPED TO A TEST THE SENTENCE DOES NOT CONTAIN. R360's `admits`")
    print(f"     is `e > 0 AND |e| >= ZEFF*se` — SIGNIFICANTLY better. The definition says BETTER")
    print(f"     THAN. The coded test is STRICTER, and the gap runs in the direction that makes the")
    print(f"     definition look more demanding than it reads. So this answers the STRICT universal")
    print(f"     reading; the LITERAL one — `e > 0` alone — has never been run, and is not")
    print(f"     approximated here. That is the FOURTH under-specification found in clause ②, after")
    print(f"     the missing member, held-out vs in-sample, and the percentile that was called EVERY.")
    print(f"  ⚠ NO MONOTONICITY IS USED ANYWHERE IN THIS ROUND. One cell decides the verdict, and the")
    print(f"    brackets above are grid positions rather than an ordering of strictness — which is")
    print(f"    exactly the premise R405 could not have.")
    print(f"  ⚠ AND THE NUMERIC CROSS-CHECK IS OWED, NOT DONE: confirming ref_at(4,100) equals")
    print(f"    R331's committed max of {a331['blind_dist']['max']:.10f} needs R360's build(k), which")
    print(f"    loads and scores. The source-level check stands in for it and is weaker.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, top_cell=sorted(adm), labels=sorted(lab), label_free_admitted=free,
               brackets=brackets, r331_k4_max=a331["blind_dist"]["max"],
               strict_test="e > 0 and abs(e) >= ZEFF*se", literal_test_run=False,
               controls=dict(idx_hi=hi_ok, idx_lo=lo_ok, expression_present=expr_present,
                             monotonicity_used=False),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r407_universal_reading.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
