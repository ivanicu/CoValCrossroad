#!/usr/bin/env python3
"""
R888 · what does clause ③ EXCLUDE that clause ② admits — and is the headline's count ②'s alone?

⛔ WHY. §4's row `the definition describes the instance` gives one mechanical remedy, per clause:
**name an admissible object this clause EXCLUDES.** If nothing is excluded, the clause is untested
decoration. That question killed `drawn from a rubric` in one line. **It has never been run on the
two SURVIVING clauses.** Eight consecutive rounds audited instruments instead — the drift §0.2 names.

⭐ AND THERE IS A WALL SITTING ON IT. R856's artifact carries, verbatim:
      "clause3_on_99_arms": "IMPOSSIBLE — provenance measured only on 42"
**The same JSON prints a `c2` list containing five arms named `oracle_*`.** §4's `a wall never
checked` row, exactly: *the falsifying evidence was in the author's own sentence.* An unchecked wall
is UNVERIFIED, never SETTLED — and here the check is one read of the generator.

⚠ **A NAME IS NOT EVIDENCE ABOUT THE OBJECT**, so provenance is read from the GENERATOR, never from
the arm id. `corebench/select_core.py:102` is the whole identification:

      if a.rule in ("oracle_k", "indep_k", "greedy_k"):
          for line in open(ROOT / "data" / "comparisons.jsonl", ...):
              ys = [parse_ranking(e["ranking"]) ...]

**Those three rules, and only those three, open the human comparison file and parse rankings.**
That is what clause ③ forbids. ⚠ The comment directly above that branch reads *"human target, for
the ORACLE arm only"* — **one rule behind its own code**, which is why the name-level story and the
code-level story disagree, and why the wall was believable.

⭐⭐ AND THE STAKE IS THE DELIVERABLE'S HEADLINE NUMBER. `DEFINITION.md` says the definition
*"admits 28 arms"*. If ③ excludes a nonzero share of ②'s extension, **28 is clause ②'s count being
reported as the definition's** — a two-clause definition quoting a one-clause extension.

ESTIMAND        n_excluded = |{a in c2 : a's generating rule opens data/comparisons.jsonl}|,
                and the corrected extension |c2| - n_excluded.
IDENTIFICATION  EXACT, and it is a DERIVATION on top of two reads, which is labelled as such:
                the rule set is a literal at select_core.py:102, the arm tag is CONSTRUCTED from
                `a.rule` at select_core.py:203-206, so rule membership is recoverable from the tag
                by prefix. Nothing is inferred from what a name suggests.
SCOPE           population: the 29 arms in R856's committed `c2` — DERIVED (it IS clause ②'s
                            extension), not globbed
                instrument: the rule literal in select_core.py + R856's committed c2 list
                baseline:   ③ excludes nothing, i.e. the clause is decoration
                regime:     home release, judge J, 968 prompts, 99 scored arms
WORLDS          A · ③ excludes 0 of c2 -> it is decoration ON THIS RELEASE and the definition
                    reduces to ONE clause. The headline's 28 is then correct.
                B · ③ excludes >0 -> ③ is load-bearing and MEASURED, and the headline's arm count
                    is clause ②'s extension mis-reported as the definition's.
                C · the rule literal cannot be read -> the wall stands, UNVERIFIED not SETTLED.
KILL            CONDITIONAL — the classifier must prove it can see, in BOTH directions, against
                sources committed by a DIFFERENT file than the one it reads:
                  ⭐ ① POSITIVE: `oracle_k4_fit1` must classify LABEL-CONSUMING. It is independently
                     declared `LEAKY` at dimension_curve.py:38 and unit_robustness.py:34 — two files
                     that know nothing about this round.
                  ⭐ ② g=0: `random_k4_s0` must classify LABEL-FREE. It is declared `INCOMPETENT`
                     and NOT leaky at unit_robustness.py:34 — a bad arm that is bad for a different
                     reason, so a classifier keying on "is this arm bad" fails here.
                  ⭐ ③ the comparator `genericpool16` must classify LABEL-FREE, else clause ②'s own
                     reference violates clause ③ and the definition is incoherent.
                  ④ the rule literal must be READ from select_core.py, not hard-coded here.
MULTIPLICITY    one estimand; every arm's classification printed, both classes, no truncation.
ARTIFACT        results/clause3_exclusion.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this measures what the clause EXCLUDES on the released arm set.
                It cannot say the clause is well-formed for an arm generated some other way — the
                live limitation `the definition describes the instance` is NOT retired by it.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
GEN = ROOT / "corebench" / "select_core.py"
R856 = ROOT / ("E05_the_space_of_compilers/A24_what_the_definition_costs/"
               "R856_clause_four_is_dominated_by_clause_two/results/clause4_dominated.json")


def label_rules():
    """The rule set that opens the human comparison file — READ from the generator, not typed."""
    src = GEN.read_text()
    m = re.search(r'if a\.rule in \(([^)]*)\):\s*\n\s*for line in open\([^)]*comparisons\.jsonl',
                  src)
    if not m:
        return None
    return tuple(x.strip().strip('"\'') for x in m.group(1).split(",") if x.strip())


def consumes(arm, rules):
    """rule -> tag is `a.rule` with the trailing `_k` carrying the k. Prefix match on the base."""
    return any(arm.startswith(r[:-2] + "_k") or arm.startswith(r) for r in rules)


def main() -> int:
    if not R856.exists():
        print("  UNRUNNABLE: R856 artifact missing. Exit 2, never 0.")
        return 2
    rules = label_rules()
    if rules is None:
        print("  ⭐ WORLD C: the rule literal could not be read from the generator.")
        print("     The wall stands as UNVERIFIED — never SETTLED. Exit 2, never 0.")
        json.dump({"world": "C", "verdict": "UNVERIFIED"},
                  open(OUT / "clause3_exclusion.json", "w"), indent=2)
        return 2
    print(f"  ④ rule literal READ from {GEN.name}:102 -> {rules}")

    p1 = consumes("oracle_k4_fit1", rules)
    p2 = not consumes("random_k4_s0", rules)
    p3 = not consumes("genericpool16", rules)
    print(f"  ① POSITIVE  oracle_k4_fit1 is LABEL-CONSUMING: {p1}  {'PASS' if p1 else 'FAIL'}")
    print(f"     independently declared LEAKY at dimension_curve.py:38 + unit_robustness.py:34")
    print(f"  ② g=0       random_k4_s0 is LABEL-FREE: {p2}  {'PASS' if p2 else 'FAIL'}")
    print(f"     declared INCOMPETENT and NOT leaky — a bad arm bad for a DIFFERENT reason, so a")
    print(f"     classifier keying on 'is this arm bad' fails right here")
    print(f"  ③ the comparator genericpool16 is LABEL-FREE: {p3}  {'PASS' if p3 else 'FAIL'}")
    if not (p1 and p2 and p3):
        print("\n  UNVERIFIED: the classifier failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [p1, p2, p3]},
                  open(OUT / "clause3_exclusion.json", "w"), indent=2)
        return 2

    c2 = json.loads(R856.read_text())["c2"]
    excl = [a for a in c2 if consumes(a, rules)]
    kept = [a for a in c2 if not consumes(a, rules)]
    assert len(excl) + len(kept) == len(c2), "partition does not sum"   # R885's lesson

    print(f"\n  clause ② admits {len(c2)} arms. clause ③ then EXCLUDES {len(excl)}, "
          f"leaving {len(kept)}.")
    print(f"\n  EXCLUDED by ③ — the generator opens data/comparisons.jsonl for these ({len(excl)}):")
    for a in excl:
        print(f"    {a}")
    print(f"\n  SURVIVING both clauses ({len(kept)}):")
    for a in kept:
        print(f"    {a}")

    world = "B" if excl else "A"
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "clause ③ excludes nothing clause ② admits — on this release it is DECORATION, and "
             "the definition reduces to ONE clause",
        "B": "clause ③ is LOAD-BEARING and now MEASURED — it removes "
             f"{len(excl)} of {len(c2)} ({len(excl)/len(c2):.1%}) of clause ②'s extension"}[world])
    if world == "B":
        print(f"\n  ⛔⛔ AND THE DELIVERABLE'S HEADLINE COUNT IS CLAUSE ②'s, NOT THE DEFINITION'S.")
        print(f"     DEFINITION.md says the definition 'admits 28 arms'. Clause ② admits "
              f"{len(c2)} here;")
        print(f"     the TWO-clause definition admits {len(kept)}. A two-clause definition has been")
        print(f"     quoting a one-clause extension.")
    print(f"\n  ⛔ AND THE WALL IS FALSE. R856 recorded clause ③ on 99 arms as")
    print(f"     'IMPOSSIBLE — provenance measured only on 42', while its own c2 list printed")
    print(f"     the arms whose generator reads the human file. An unchecked wall is UNVERIFIED,")
    print(f"     never SETTLED, and this one cost {len(excl)} arms of a headline number.")
    print(f"\n  ⚠ NOT RETIRED: `the definition describes the instance`. This measures what ③")
    print(f"    excludes on the RELEASED arm set; it says nothing about an arm generated some")
    print(f"    other way, and one release still ships one core.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "rules_read_from_source": list(rules),
               "n_c2": len(c2), "n_excluded_by_clause3": len(excl), "n_surviving_both": len(kept),
               "excluded": excl, "surviving": kept,
               "share_excluded": len(excl) / len(c2),
               "wall_overturned": "R856 clause3_on_99_arms = 'IMPOSSIBLE — provenance measured "
                                  "only on 42' is FALSE; provenance is in the generator's rule "
                                  "branch, select_core.py:102",
               "controls": {"positive_oracle_k4_fit1": p1, "g0_random_k4_s0": p2,
                            "comparator_genericpool16": p3},
               "unit_note": {"n_c2": "ARMS admitted by clause 2",
                             "n_surviving_both": "ARMS surviving both clauses",
                             "warning": "every count here is ARMS — not prompts, not criteria"},
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "clause3_exclusion.json", "w"), indent=2)
    print(f"\n  artifact: results/clause3_exclusion.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
