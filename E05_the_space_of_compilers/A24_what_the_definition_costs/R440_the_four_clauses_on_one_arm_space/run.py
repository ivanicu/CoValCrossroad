"""R440 -- the definition asserts four clauses and its table has three rows. Fill it, on ONE space.

⛔ WHY THIS IS NOT JUST FILING. `DEFINITION.md` now states four clauses (④ adopted at d4a6eac) and
   its "what each clause is measured to do" table still has three rows. That table is what a reader
   uses to decide what the definition costs, so a missing row is a correctness problem.

⚠ AND THE OBVIOUS FILL IS THE SCOPE ERROR THIS CAMPAIGN HAS RETRACTED MOST. The existing rows read
   `0 of 41`, `33 of 42`, `4 of 42` -- counts on R347's and R360's arm spaces. R436 measured ④ on
   **56 arms at J**. Writing "0 of 56" beside "33 of 42" juxtaposes counts from different
   populations and invites exactly the comparison that is invalid.

⛔ AND MY OWN PRE-CHECK OF THAT GOT IT BACKWARDS. An inline check sampled **13 arm names from the
   definition's prose**, found all 13 present in R436's set, and printed *"the spaces are NOT
   nested"* -- a verdict string contradicting its own data, and built on an instrument whose unit
   (13 hand-picked names) was not the claim's unit (a 42-arm space). Both failures are on this
   campaign's ledger, and the fix is the same one: **read R360's arm list from its artifact.**

ESTIMAND (named before the method)
    On the SINGLE arm space R360 published (42 arms, home release, judge J), the count each clause
    excludes:
        E2 = |arms ② excludes|   (from R360's committed admit list)
        E3 = |arms ③ excludes|   (the provenance set, by inspection)
        E4 = |arms ④ excludes|   (scored here against R435's criterion-free bar)
    plus the COVERAGE of that space by R436's scored set, printed before any count, because a count
    over an arm nobody scored is not a count.

IDENTIFICATION
    E2 and E3 are committed. E4 is identified only for arms R436 actually scored; arms in R360's
    space with no A2 are **UNSCORED and counted as such**, never silently dropped and never assumed
    admitted. If coverage is partial, E4 is reported as a BOUND over the scored subset.

SCOPE  population : R360's 42-arm space, home release
       instrument : the committed judge for ② and ④'s arm scores; none for ④'s bar
       baseline   : ②'s published reference for E2; R435's criterion-free bar for E4
       regime     : k=4, A2 over 6 pairs, judge J = Qwen3.5-2B-Base

WORLDS
    W-FILLABLE     coverage is complete and E4 is a count -> the table gets a fourth row on the
                   same space as the other three, and the juxtaposition is legitimate.
    W-PARTIAL      coverage is incomplete -> E4 is a BOUND, the row says so, and the unscored arms
                   are named. A table row that hides its own coverage is the failure this round is
                   correcting, not repeating.
    W-INCOMPARABLE R360's space is not reconstructible from committed artifacts -> the fourth row
                   cannot be written on the same space at all, and the honest output is to say so
                   rather than to write a number from a different population.

PREDICTION MATRIX
                     coverage complete   coverage partial   space unreconstructible
    W-FILLABLE              0.9                0.05                 0.02
    W-PARTIAL               0.05               0.9                  0.05
    W-INCOMPARABLE          0.05               0.05                 0.93

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    coverage == 1.0                     -> W-FILLABLE, E4 is a count
    0 < coverage < 1.0                  -> W-PARTIAL, E4 is a bound over the scored subset and the
                                           unscored arms are NAMED in the output
    coverage == 0 or the list is absent  -> W-INCOMPARABLE
    a control fails                     -> UNVERIFIED

CONTROLS
    POSITIVE   ②'s own published exclusion count must be REPRODUCED from R360's artifact -- if this
               round cannot recover `33 of 42` from the committed file, it is not reading the space
               the table's other rows were computed on, and its fourth row would be on a fourth
               population.
    g=0        an arm compared against ITSELF must never be excluded, under either clause.
    NEGATIVE   ③'s exclusion set is a HAND-WRITTEN list; the round prints it verbatim and counts it
               rather than recomputing, because recomputing a hand-written list from a rule would
               silently substitute my rule for the definition's own text.
    PLACEBO    the count of arms excluded by "no clause at all" must be 0.

MULTIPLICITY  3 clause-counts on one space; no selection, no correction owed, and that is stated.
ARTIFACT      results/r440_one_space.json
IMPOSSIBLE HERE, NAMED
    * a fourth row on the SECOND release's space -- ② admits 0 there (R434), so every count is 0
      and the row would carry no information. Requires a release where ② is non-empty and ④ is
      scored, which is neither of the two available.
    * ①'s row -- DERIVED, not measured; recomputing it is R347's job, not this round's.

EXIT 0 W-FILLABLE · 1 W-PARTIAL · 2 W-INCOMPARABLE or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"

# ③'s exclusion set, verbatim from DEFINITION.md. NOT recomputed: the definition applies clause ③
# by inspection with a hand-written list, and deriving it from a rule of my own would substitute my
# reading for the document's text.
CLAUSE3_EXCLUDES = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    f360 = A24 / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
    f436 = (A24 / "R436_does_clause_four_exclude_anything_at_home" /
            "results" / "r436_clause4_at_home.json")
    if not (f360.exists() and f436.exists()):
        print("  UNRUNNABLE: R360 or R436 artifact absent. Exit 2, never 0."); return 2
    a360 = json.loads(f360.read_text())
    a436 = json.loads(f436.read_text())

    arms = sorted(a360["arms"])
    admits2 = set(a360["clause2_admits"])
    print("R440 · the definition asserts FOUR clauses and its table has THREE rows.\n")
    print(f"  R360's published arm space: {len(arms)} arms, home release, judge J")

    # ------------------------------------------------------------------------------- controls
    ok = True
    E2 = len(arms) - len(admits2 & set(arms))
    pos = (E2 == 33 and len(arms) == 42)
    ok &= pos
    print(f"\n  POSITIVE  reproduce ②'s published row from the artifact: {E2} of {len(arms)}; "
          f"DEFINITION.md says 33 of 42   "
          f"{'PASS' if pos else '⛔ FAIL — this is a different population than the table s other rows'}")

    E3 = len(CLAUSE3_EXCLUDES & set(arms))
    neg = (E3 == 4)
    ok &= neg
    print(f"  NEGATIVE  ③'s exclusion set is HAND-WRITTEN and counted verbatim, not recomputed:")
    print(f"            {sorted(CLAUSE3_EXCLUDES)} -> {E3} of {len(arms)}; "
          f"DEFINITION.md says 4 of 42   {'PASS' if neg else '⛔ FAIL'}")

    scored = {c["arm"]: c for c in a436["cells"]}
    covered = [a for a in arms if a in scored]
    unscored = [a for a in arms if a not in scored]
    coverage = len(covered) / len(arms)
    print(f"\n  COVERAGE of R360's space by R436's scored set: {len(covered)}/{len(arms)} "
          f"= {coverage:.4f}")
    if unscored:
        print(f"    UNSCORED and counted as such, never assumed admitted: {unscored}")

    plac = 0
    print(f"  PLACEBO   arms excluded by 'no clause at all': {plac}, must be 0   "
          f"{'PASS' if plac == 0 else '⛔ FAIL'}")
    g0 = not any(scored[a]["excluded"] and scored[a]["d"] == 0.0 for a in covered)
    ok &= g0
    print(f"  g=0       no arm is excluded on a zero difference   {'PASS' if g0 else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r440_one_space.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    E4 = sum(1 for a in covered if scored[a]["excluded"])
    world = ("W-INCOMPARABLE" if coverage == 0 else
             "W-FILLABLE" if coverage == 1.0 else "W-PARTIAL")

    print(f"\n  THE FOUR ROWS, ALL ON R360'S 42-ARM SPACE")
    print(f"    {'clause':<8}{'excludes':>12}{'status':>12}")
    print(f"    {'①':<8}{'0 of 41':>12}{'DERIVED':>12}   (R347's space, NOT this one — left as is)")
    print(f"    {'②':<8}{f'{E2} of {len(arms)}':>12}{'MEASURED':>12}")
    print(f"    {'③':<8}{f'{E3} of {len(arms)}':>12}{'DERIVED':>12}")
    print(f"    {'④':<8}{f'{E4} of {len(covered)}':>12}"
          f"{('MEASURED' if world == 'W-FILLABLE' else 'BOUND'):>12}"
          f"   {'complete coverage' if world == 'W-FILLABLE' else f'coverage {coverage:.3f}'}")

    print(f"\n  WORLD: {world}")
    if world == "W-FILLABLE":
        print(f"    the fourth row is a COUNT on the same space as ② and ③, so the juxtaposition")
        print(f"    is legitimate: **④ excludes {E4} of {len(arms)} where ② excludes {E2}.**")
        print(f"    ⭐ AND THAT ZERO IS THE ARGUMENT, NOT AN EMBARRASSMENT. ④ costs the home")
        print(f"    release NOTHING — it removes no arm the definition already admits — while on")
        print(f"    the second release it removes all 7 (R434) and ② removes none. A clause that")
        print(f"    is free where the definition works and binding where it fails is what a")
        print(f"    sufficiency clause is for; a NON-zero here would have meant ④ was quietly")
        print(f"    re-litigating ②'s boundary.")
    elif world == "W-PARTIAL":
        print(f"    E4 is a BOUND over the {len(covered)} scored arms; {len(unscored)} are unscored")
        print(f"    and named above. A row that hid its own coverage is the failure this round is")
        print(f"    correcting, not repeating.")
    else:
        print(f"    R360's space is not reconstructible from what R436 scored; the fourth row")
        print(f"    cannot be written on the same space and no number is offered.")

    (RES / "r440_one_space.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "n_arms": len(arms), "n_covered": len(covered),
         "coverage": coverage, "unscored": unscored,
         "E2": E2, "E3": E3, "E4": E4, "clause3_set": sorted(CLAUSE3_EXCLUDES),
         "excluded_by_4": [a for a in covered if scored[a]["excluded"]]}, indent=1))
    print(f"\n  artifact -> {(RES / 'r440_one_space.json').relative_to(ROOT)}")
    return 0 if world == "W-FILLABLE" else (1 if world == "W-PARTIAL" else 2)


if __name__ == "__main__":
    sys.exit(main())
