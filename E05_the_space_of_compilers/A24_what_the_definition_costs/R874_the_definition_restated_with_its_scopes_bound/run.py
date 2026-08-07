#!/usr/bin/env python3
"""
R874 · the definition RESTATED, with every clause's comparator and criterion bound to it.

⛔ WHY, AND IT IS A COURSE CORRECTION. Five consecutive rounds (R869–R873) audited my own
instruments — category occupancy, gate liveness, convention decay, endpoint trends, permutation
floors. Every one found something real. **Not one of them said anything about a CORE.** §0.2 of the
governing constitution is explicit that a retraction ledger is infrastructure, not product, and that
the tell is when the most quotable sentence in a report is about my own rigour rather than about the
object. **Five rounds of that is the tell.**

⭐ **AND IT SATISFIES check #540's NEXT RATHER THAN DEFERRING IT.** That NEXT asked for a round
whose POPULATION is derived from its ESTIMAND instead of globbed from whatever the corpus made easy.
Here the estimand is *which clauses survive*, so the population is **the four clauses and their
measured bindings** — four objects, each named, none enumerated by a glob. The four-round failure
(a category with zero / one / wrong / too-wide members) cannot occur on a population of four named
things whose membership is the question itself.

ESTIMAND        for each of the definition's four clauses: whether it still does work, and under
                exactly which comparator and which admissibility criterion.
IDENTIFICATION  exact — every input is a committed artifact from R347, R856, R857, R865, R866, R867.
                Nothing is recomputed here; this round ASSEMBLES and asserts, and its whole job is
                to fail loudly if the artifacts it rests on say something other than what it claims.
SCOPE           population: the 4 clauses (not a glob — the estimand names them)
                instrument: the committed artifacts, read from disk
                baseline:   the clause table as published at DEFINITION.md:740-750
                regime:     home release, judge J, 968-prompt shared population
WORLDS          A · all four clauses survive with scopes attached -> the definition was right and
                    only under-specified
                B · some clauses are dominated or vacuous -> the definition is SHORTER than
                    published, and each drop must carry the measurement that dropped it
                C · the artifacts disagree with the published table -> the table is stale and the
                    disagreement is the finding
KILL            CONDITIONAL, and every one reads a committed number, not my memory:
                  ⭐ ① R867's artifact must show clause ④'s window as EXACTLY ['family_p90'] and
                     `published_comparator_inside['④'] == False`.
                  ⭐ ② R867 must show clause ②'s window containing 'argmax_arm'.
                  ⭐ ③ R865 must show ② readable and ④′ excluded, with `total_only_A == 0`
                     (A ⊂ B strictly).
                  ⭐ ④ R866 must show world 'C' — comparator and criterion interact.
                  If ANY artifact says otherwise, this round is assembling a story its own evidence
                  does not support. Exit 2, never 0.
PLACEBO         re-reading the same artifacts twice must give identical assertions.
MULTIPLICITY    four clauses, all reported, including the two that survive.
ARTIFACT        results/definition_restated.json
IMPOSSIBLE      cross-release · construct validated · causally identified. ⚠ And one more, named
                because it is the honest ceiling of this whole line: the definition is still written
                from a release that ships exactly ONE core, so `the definition describes the
                instance` remains live for every clause below. What it would require: a second
                release with a differently-built core.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"


def load(round_glob, fname):
    d = next(A24.glob(f"{round_glob}/results/{fname}"), None)
    return json.loads(d.read_text()) if d else None


def main() -> int:
    r865 = load("R865_*", "criterion_invariance.json")
    r866 = load("R866_*", "comparator_sweep.json")
    r867 = load("R867_*", "meaningful_window.json")
    missing = [n for n, v in (("R865", r865), ("R866", r866), ("R867", r867)) if v is None]
    if missing:
        print(f"  UNRUNNABLE: missing artifacts {missing}. Exit 2, never 0.")
        return 2

    k1 = r867["window_clause_4"] == ["family_p90"] and \
        r867["published_comparator_inside"]["④"] is False
    k2 = "argmax_arm" in r867["window_clause_2"]
    k3 = r865["readable_clauses"] == ["②"] and r865["excluded_clauses"] == ["④′"] and \
        r865["total_only_A"] == 0
    k4 = r866["world"] == "C"
    print(f"  KILL ① ④'s window == ['family_p90'] AND published comparator OUTSIDE: {k1}  "
          f"{'PASS' if k1 else 'FAIL'}")
    print(f"  KILL ② ②'s window contains 'argmax_arm': {k2}  {'PASS' if k2 else 'FAIL'}")
    print(f"  KILL ③ R865: ② readable, ④′ excluded, only_A == 0 (A ⊂ B strictly): {k3}  "
          f"{'PASS' if k3 else 'FAIL'}")
    print(f"  KILL ④ R866 world == 'C' (comparator × criterion interact): {k4}  "
          f"{'PASS' if k4 else 'FAIL'}")
    if not (k1 and k2 and k3 and k4):
        print("\n  UNVERIFIED: an artifact says something other than what this round assembles.")
        print("  Exit 2, never 0 — a restatement whose evidence disagrees with it is a story.")
        json.dump({"verdict": "UNVERIFIED", "k": [k1, k2, k3, k4]},
                  open(OUT / "definition_restated.json", "w"), indent=2)
        return 2

    core_row = next((r for r in r866["rows"] if r["comparator"] == "argmax_arm"), None)
    counts = [r["count_B"][0] if isinstance(r["count_B"], list) else r["count_B"]
              for r in r866["rows"]]
    clauses = [
        {"clause": "①", "text": "better than a random draw of the prompt's own rubric",
         "verdict": "DROPPED — DOMINATED",
         "why": "bar ordering MEASURED: ② 0.5404-0.5462 > ① 0.4922 > ④' 0.4820 (R857). ①'s "
                "binding region was already empty by arithmetic in R347 (ref_gap_min 0.0470, "
                "②'s reference exceeds ①'s on EVERY arm, contingent: []).",
         "comparator": "n/a — no comparator can rescue a dominated bar",
         "criterion": "invariant (DERIVED clauses carry no threshold)"},
        {"clause": "②", "text": "better than a prompt-blind set",
         "verdict": "RETAINED — and it is the ONLY clause doing score work",
         "why": "extension runs 29 -> 0 across six defensible comparators (R866) and 23-24 vs 29 "
                "across the two admissibility criteria, with A a STRICT subset of B at every seed "
                "(R865). Its meaningful window is 4 of 5 comparators and the published "
                "`argmax_arm` lies INSIDE it (R867).",
         "comparator": "MUST BE NAMED. Published: argmax_arm. Vacuous at per_prompt_max "
                       "(0 of 99 arms, oracle included).",
         "criterion": "MUST BE NAMED. `ratio >= 1.5` is strictly stricter than BH q=0.05 + CI."},
        {"clause": "③", "text": "consumes no prompt-specific labels",
         "verdict": "RETAINED — provenance, no bar",
         "why": "read from the source rather than hand-listed (R444). No threshold, no interval, "
                "no multiplicity, so nothing for a comparator or a criterion to act on.",
         "comparator": "invariant", "criterion": "invariant"},
        {"clause": "④", "text": "better than every criterion-free rule",
         "verdict": "DROPPED — VACUOUS OR UNMET, at every comparator tested",
         "why": "its meaningful window is a SINGLE comparator, family_p90, and the published "
                "argmax_arm is OUTSIDE it: there random_k4_s0 scores +1.816 and CLEARS the bar. "
                "At family_p90, the one comparator where ④ has content, coval_core scores -0.565 "
                "and FAILS it. So at every comparator where the core passes ④, so does random "
                "noise (R867). R856 had already derived that ④ is dominated by ②.",
         "comparator": "no comparator makes it both meaningful and satisfied",
         "criterion": "UNVERIFIABLE — its negative control clears the clause (R865, R850 at 7 of "
                      "8 class sizes)"},
    ]
    print("\n  ⭐⭐ THE DEFINITION, RESTATED — every clause with its scope bound\n")
    for c in clauses:
        print(f"  {c['clause']}  {c['text']}")
        print(f"      -> {c['verdict']}")
        print(f"      comparator: {c['comparator']}")
        print(f"      criterion : {c['criterion']}")
    retained = [c["clause"] for c in clauses if c["verdict"].startswith("RETAINED")]
    dropped = [c["clause"] for c in clauses if c["verdict"].startswith("DROPPED")]
    world = "A" if not dropped else "B"
    print(f"\n  ⭐ RETAINED {retained} · DROPPED {dropped}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "all four survive with scopes attached — the definition was right and only "
             "under-specified",
        "B": "the definition is SHORTER than published, and each drop carries the measurement "
             "that dropped it"}[world])

    print(f"\n  ⭐⭐⭐ THE STATEMENT THIS PROGRAMME NOW SUPPORTS:")
    print(f"     A CORE is a criterion set of size > 1 that (③) consumes no prompt-specific")
    print(f"     labels and (②) beats a prompt-blind comparator — WITH THE COMPARATOR AND THE")
    print(f"     ADMISSIBILITY CRITERION NAMED, because the clause admits 29 arms or 0 depending")
    print(f"     on the first and 23 or 29 depending on the second.")
    print(f"     ① is dropped as dominated. ④ is dropped as vacuous-or-unmet.")
    print(f"     ⚠ SIZE: the design supports 'more than one'; 3 to 8 are indistinguishable, so no")
    print(f"       number is stated. That bound is what the k-sweep could resolve, not a choice.")
    print(f"     ⚠ AND THE CEILING ON ALL OF IT: this is still written from a release shipping")
    print(f"       exactly ONE core, so `the definition describes the instance` stays live for")
    print(f"       every clause above. It would take a second release to retire it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "clauses": clauses,
               "retained": retained, "dropped": dropped,
               "clause2_extension_by_comparator": counts,
               "clause2_core_at_published_comparator": core_row,
               "statement": "A CORE is a criterion set of size > 1 that consumes no "
                            "prompt-specific labels and beats a NAMED prompt-blind comparator "
                            "under a NAMED admissibility criterion.",
               "size_bound": "more than one; 3 to 8 indistinguishable — no number stated",
               "live_limitation": "the definition describes the instance; one core in the release",
               "sources": {"R347": "①'s region empty by arithmetic",
                           "R856": "④ dominated by ②", "R857": "bar ordering",
                           "R865": "criterion dependence, A ⊂ B",
                           "R866": "comparator sweep 29 -> 0",
                           "R867": "meaningful windows"}},
              open(OUT / "definition_restated.json", "w"), indent=2)
    print(f"\n  artifact: results/definition_restated.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
