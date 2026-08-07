#!/usr/bin/env python3
"""
R857 · how many of the definition's clauses actually do work? — the bar ordering says ONE.

⛔ WHY. R856 showed clause ④ is dominated by ② (②'s comparator 0.5404 sits +0.0584 above ④′'s bar
0.4820, so ②⇒④′ is forced). Its NEXT asked whether other pairs stand in the same relation.
**Reading R347's committed artifact answers it, and shows the pattern was ALREADY ESTABLISHED for
① and never generalised**: its verdict string is literally `W1_DERIVATION`, with
`ref_gap_min = 0.0470` — ②'s reference exceeds ①'s on EVERY arm — and `contingent: []`.

ESTIMAND        the ordering of the three SCORE-COMPARISON clauses' reference bars on a common
                object, and which pairs therefore stand in a strictly-harder (dominating) relation.
IDENTIFICATION  yes, from committed artifacts. ⚠ Clause ③ has NO bar — it is a PROVENANCE test, a
                different kind of predicate — so it is outside this comparison by construction and
                is reported as such rather than forced onto the scale.
SCOPE           ① and ② bars: R347's `ref1_mean`/`ref2_mean`, 41 arms
                ④′ bar and the `genericpool16` comparator: R849/R856, 99 arms, EVEN half
                ⚠ TWO different numbers exist for ②'s comparator (0.5462 and 0.5404) because they
                are different comparator constructions on different halves. BOTH are reported with
                provenance; neither is silently substituted for the other.
WORLDS          A · ② is the highest bar -> ① and ④ are BOTH dominated, and the definition has ONE
                    working score clause
                B · the bars interleave -> each clause binds somewhere and all three do work
KILL            the ordering must hold under BOTH available values of ②'s comparator, or the claim
                is contingent on which construction is used and must be reported as contingent.
⚠ WHAT IS MEASURED AND WHAT IS DERIVED — the distinction this round turns on:
    MEASURED  the ORDERING of the bars. Nothing forces a random-rubric draw to sit below a
              prompt-blind set; it is an empirical fact about this release and could have come
              out otherwise.
    DERIVED   that a higher bar DOMINATES a lower one. That is algebra, exactly as in R856, and
              it is labelled rather than banked.
ARTIFACT        results/clause_bar_ordering.json
IMPOSSIBLE      clause ③ — no bar exists; comparing a provenance predicate to a score threshold
                would be a category error, named rather than approximated.
"""
import json, glob, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

r347 = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R347_*/results/r347_clause_one_binding.json"))[0]))
r849 = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R849_*/results/proposed_clause_extension.json"))[0]))
r856 = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R856_*/results/clause4_dominated.json"))[0]))

bar1, bar2a = r347["ref1_mean"], r347["ref2_mean"]
bar2b, bar4 = r856["comparator_A2"], r849["bar_even_half_A2"]
print(f"  ① random draw of the prompt's OWN rubric : {bar1:.4f}   (R347 ref1_mean, 41 arms)")
print(f"  ② prompt-blind set                       : {bar2a:.4f}   (R347 ref2_mean, 41 arms)")
print(f"  ②  same clause, `genericpool16` even half: {bar2b:.4f}   (R856, 99 arms)")
print(f"  ④′ response-only rule max                : {bar4:.4f}   (R849, 99 arms)")
print(f"\n  ⚠ TWO values for ②'s comparator — different constructions, different halves.")
print(f"    Both reported; neither substituted for the other.")

holds_a = bar2a > bar1 and bar2a > bar4
holds_b = bar2b > bar1 and bar2b > bar4
print(f"\n  KILL CHECK  ② is the highest bar under BOTH values: {holds_a and holds_b}  "
      f"{'PASS' if (holds_a and holds_b) else 'FAIL — the claim is contingent on the construction'}")
print(f"    R347 also commits `ref_gap_min = {r347['ref_gap_min']:.4f}` — ②'s reference exceeds ①'s")
print(f"    on EVERY arm — and `contingent: {r347['contingent']}`, with verdict {r347['verdict']}.")

if not (holds_a and holds_b):
    print("\n  UNVERIFIED: the ordering does not survive both constructions. Exit 2, never 0.")
    raise SystemExit(2)

print(f"\n  ⭐ WORLD A — the bar ordering is  ② ({min(bar2a,bar2b):.4f}) > ① ({bar1:.4f}) "
      f"> ④′ ({bar4:.4f})")
print("  ⭐⭐ MEASURED: the ordering. Nothing forces a random-rubric draw to sit below a")
print("     prompt-blind set — it is an empirical fact about this release.")
print("  ⚠ DERIVED: that a higher bar dominates a lower one. Algebra, as in R856. Labelled.")
print("\n  ⭐⭐⭐ SO OF THE THREE SCORE CLAUSES, ONLY ② DOES WORK. ① and ④ are BOTH dominated:")
print("     anything they would exclude, ② has already excluded. R347 said this for ① in its own")
print("     verdict string (`W1_DERIVATION`) and NOBODY GENERALISED IT; R856 found it for ④.")
print("\n  The definition therefore reduces to: ② (the one working score clause)")
print("                                     + ③ (PROVENANCE — a different kind of test, no bar)")
print("                                     + the size floor.")
print("  ⚠ ③ is outside this comparison BY CONSTRUCTION. Forcing a provenance predicate onto a")
print("    score scale would be a category error; it is named, not approximated.")

head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                      capture_output=True, text=True).stdout.strip()
json.dump({"commit": head, "world": "A",
           "bars": {"c1_random_own_rubric": bar1, "c2_prompt_blind_r347": bar2a,
                    "c2_genericpool16_even": bar2b, "c4prime_response_only": bar4},
           "ordering": "c2 > c1 > c4prime", "holds_under_both_c2_values": True,
           "r347_ref_gap_min": r347["ref_gap_min"], "r347_verdict": r347["verdict"],
           "measured": "the ORDERING of the bars",
           "derived": "that a higher bar dominates a lower one",
           "c3_excluded_by_construction": "provenance predicate, no bar exists"},
          open(OUT / "clause_bar_ordering.json", "w"), indent=2)
print(f"\n  artifact: results/clause_bar_ordering.json @ {head[:8]}")
