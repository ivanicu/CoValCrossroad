#!/usr/bin/env python3
"""
R904 · R903's headline was a DERIVATION — the arms draw criteria from different SOURCES.

⛔⛔ WHY, AND IT RETRACTS THE PREVIOUS ROUND'S HEADLINE. R903 reported, as a finding about the
definition: *"the definition admits two arms whose criterion sets are LITERALLY DISJOINT."* The
criterion sets are **text strings**, and the three admitted families draw them from structurally
different places:
  · `topw_k*`, `topabs_k4`, `topvar_k4`, `full` — **select from the PROMPT'S OWN RUBRIC**
  · `generic`, `genericpool16` — a **FIXED external checklist**, the same strings on every prompt
  · `coval_core` — **freshly generated per prompt**, which R494 measured at 99.6% unique
**Two arms drawing from disjoint vocabularies have overlap 0 by construction.** The disjointness is
forced by the algebra of where the strings come from, not observed about the definition. It is a
DERIVATION and R903 banked it as evidence.

⭐ **AND THE CORRECTED STATEMENT IS STRONGER, NOT WEAKER.** The definition does not merely admit
arms that disagree about criteria — **it admits three structurally different KINDS of criterion
source**, and *overlap is not a meaningful statistic across kinds at all*. Saying `Jaccard = 0`
between a rubric-selector and a fixed checklist is like saying two texts in different alphabets
share no words. **The right report is the TYPE PARTITION, plus overlap computed only WITHIN the one
type where it can vary.**

⚠ **THE TELL I WALKED PAST.** R901's own floor drew random subsets from `core_full.json` — *the
prompt's own pool* — and R903 reused that floor while comparing an arm that does not draw from that
pool at all. **The control and the comparison were over different universes, and the floor's
provenance said so in the code I copied.**

ESTIMAND        the criterion-source TYPE of each admitted arm, verified from the strings; and the
                overlap distribution WITHIN the rubric-selecting type only.
IDENTIFICATION  exact. Type is decided by two checks on the committed strings: does the arm emit
                the SAME set on every prompt (fixed checklist), and are its strings a SUBSET of the
                prompt's rubric (`core_full.json`)?
SCOPE           population: the admitted arms with a per-prompt selection on disk — named
                instrument: string-set membership against `core_full.json`; Jaccard within type
                baseline:   the random floor, admissible ONLY within the rubric-selecting type
                regime:     home release, judge 2B
WORLDS          A · the arms partition into >1 source type -> R903's cross-type zero is a
                    derivation, and the corrected finding is the type partition itself
                B · all arms select from the prompt's rubric -> R903's zero was a real measurement
                    and stands
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, a type test that can fail: `topw_k4` MUST be a subset of the
                     prompt's rubric on ~every prompt. If the arm the release builds by ranking
                     rubric criteria is not inside the rubric, the type test is broken.
                  ⭐ ② PLACEBO / the derivation made explicit: `generic`'s set must be IDENTICAL
                     across prompts. A fixed checklist that varies is not a fixed checklist.
                  ⭐ ③ within-type overlap must REPRODUCE R901's 0.5562 for topw_k4 vs topabs_k4 —
                     a cross-round wiring check that the strings are being compared the same way.
MULTIPLICITY    every arm typed and printed; within-type pairs reported whole.
ARTIFACT        results/criterion_source_types.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this says the cross-type comparison is ill-posed. It does not
                say the definition is wrong to admit several kinds — that may be the point.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R901_PAIR = 0.5562


def core(nm):
    f = RES / f"core_{nm}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def main() -> int:
    a889 = next(A24.glob("R889_*/results/two_admitted_sets.json"), None)
    if a889 is None:
        print("  UNRUNNABLE: R889 artifact missing. Exit 2, never 0.")
        return 2
    twelve = json.loads(a889.read_text())["r888_corrected"]["surviving"]
    full = core("full")
    if full is None:
        print("  UNRUNNABLE: core_full.json missing. Exit 2, never 0.")
        return 2

    sel = {a: core(a) for a in twelve + ["topabs_k4"]}
    have = [a for a in sel if sel[a]]
    pids = sorted(set.intersection(*[set(sel[a]) for a in have]) & set(full))
    print(f"  arms with selections: {len(have)} · shared prompts: {len(pids)}")
    if len(pids) < 100:
        print("  UNRUNNABLE: fewer than 100 shared prompts. Exit 2, never 0.")
        return 2

    rows = []
    for a in sorted(have):
        sets = [frozenset(sel[a][p]) for p in pids]
        fixed = len(set(sets)) == 1
        insub = float(np.mean([len(s - frozenset(full[p])) == 0
                               for s, p in zip(sets, pids)]))
        t = ("FIXED_CHECKLIST" if fixed else
             "RUBRIC_SELECTOR" if insub > 0.95 else "GENERATED_OR_OTHER")
        rows.append({"arm": a, "type": t, "identical_across_prompts": bool(fixed),
                     "share_inside_prompt_rubric": insub,
                     "mean_k": float(np.mean([len(s) for s in sets]))})
    print(f"\n  ⭐ CRITERION-SOURCE TYPE, decided from the committed STRINGS:")
    print(f"     {'arm':<20}{'type':<20}{'same set every prompt':>23}{'⊆ rubric':>10}")
    for r in rows:
        print(f"     {r['arm']:<20}{r['type']:<20}{str(r['identical_across_prompts']):>23}"
              f"{r['share_inside_prompt_rubric']:>10.3f}")

    tw = next((r for r in rows if r["arm"] == "topw_k4"), None)
    gn = next((r for r in rows if r["arm"] == "generic"), None)
    c1 = tw is not None and tw["share_inside_prompt_rubric"] > 0.95
    c2 = gn is not None and gn["identical_across_prompts"]
    print(f"\n  ① POSITIVE topw_k4 is inside the prompt's rubric on "
          f"{tw['share_inside_prompt_rubric'] if tw else float('nan'):.3f} of prompts > 0.95: "
          f"{c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"  ② PLACEBO/DERIVATION generic emits the SAME set on every prompt: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"     a fixed checklist that varied would not be a fixed checklist")

    types = {}
    for r in rows:
        types.setdefault(r["type"], []).append(r["arm"])
    rub = sorted(types.get("RUBRIC_SELECTOR", []))
    within = []
    for a, b in itertools.combinations(rub, 2):
        js = [len(set(sel[a][p]) & set(sel[b][p])) / len(set(sel[a][p]) | set(sel[b][p]))
              for p in pids]
        within.append({"a": a, "b": b, "jaccard": float(np.mean(js)),
                       "k_a": float(np.mean([len(sel[a][p]) for p in pids])),
                       "k_b": float(np.mean([len(sel[b][p]) for p in pids]))})
    ref = next((r for r in within if {r["a"], r["b"]} == {"topw_k4", "topabs_k4"}), None)
    c3 = ref is not None and abs(ref["jaccard"] - R901_PAIR) < 0.01
    print(f"  ③ WIRING within-type topw_k4 vs topabs_k4 = "
          f"{ref['jaccard'] if ref else float('nan'):.4f} vs R901's {R901_PAIR}: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows,
                   "controls": [bool(c1), bool(c2), bool(c3)]},
                  open(OUT / "criterion_source_types.json", "w"), indent=2)
        return 2

    world = "A" if len(types) > 1 else "B"
    print(f"\n  ⭐⭐ THE TYPE PARTITION — {len(types)} source kind(s) among the admitted arms:")
    for t, arms in sorted(types.items()):
        print(f"     {t:<20} {len(arms):>2}  {sorted(arms)}")
    print(f"\n  ⭐ OVERLAP WITHIN THE RUBRIC-SELECTING TYPE ONLY ({len(within)} pair(s)) — the one")
    print(f"     type where overlap CAN vary:")
    for r in sorted(within, key=lambda x: x["jaccard"]):
        print(f"     {r['a']:<18} {r['b']:<18} k={r['k_a']:.0f}/{r['k_b']:.0f}  "
              f"J={r['jaccard']:.4f}")

    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"the admitted arms partition into {len(types)} criterion-source KINDS. **R903's "
             "`literally disjoint` is a DERIVATION** — a fixed external checklist and a "
             "prompt-rubric selector draw from disjoint vocabularies by construction, so their "
             "overlap is 0 whatever the definition does. RETRACTED as evidence.",
        "B": "every admitted arm selects from the prompt's rubric, so R903's zero was a real "
             "measurement and stands"}[world])
    if world == "A":
        print(f"\n  ⭐ AND THE CORRECTED STATEMENT IS STRONGER: the definition admits arms whose")
        print(f"     criteria come from **different sources entirely** — a fixed checklist, the")
        print(f"     prompt's own rubric, and (for `coval_core`, 99.6% unique per R494) freshly")
        print(f"     generated text. **Overlap is not a meaningful statistic across those kinds.**")
        print(f"     `Admitted` spans criterion SOURCES, which is a sharper claim than `admitted")
        print(f"     arms disagree`, and it is the one the evidence supports.")
    print(f"\n  ⚠ THE TELL I WALKED PAST: R901's floor drew from `core_full.json` — the prompt's")
    print(f"    OWN pool — and R903 reused that floor while comparing an arm that never draws")
    print(f"    from it. **The control and the comparison were over different universes**, and")
    print(f"    the floor's provenance was written in the code I copied.")
    print(f"\n  ⚠ THIS DOES NOT SAY THE DEFINITION IS WRONG to admit several kinds. It says the")
    print(f"    cross-kind overlap comparison is ill-posed and must not be quoted.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": len(pids),
               "arms": rows, "type_partition": {t: sorted(a) for t, a in types.items()},
               "within_rubric_type_pairs": within,
               "retracts": "R903's headline that the definition admits arms with LITERALLY "
                           "DISJOINT criterion sets. The zero is forced: a fixed external "
                           "checklist and a prompt-rubric selector draw from disjoint "
                           "vocabularies by construction.",
               "corrected_statement": "the definition admits arms whose criteria come from "
                                      "DIFFERENT SOURCES — fixed checklist, prompt rubric, and "
                                      "freshly generated text — and overlap is not a meaningful "
                                      "statistic across those kinds",
               "the_tell": "R901's floor drew from core_full.json, the prompt's own pool; R903 "
                           "reused it while comparing an arm that never draws from that pool",
               "controls": {"positive_topw_in_rubric": bool(c1),
                            "placebo_generic_is_fixed": bool(c2),
                            "wiring_reproduces_R901_pair": bool(c3),
                            "reference_pair_jaccard": ref["jaccard"] if ref else None},
               "does_not_say": "that admitting several kinds is wrong — only that the cross-kind "
                               "overlap comparison is ill-posed",
               "unit_note": "J is a set overlap over TEXT STRINGS; k is CRITERIA per prompt",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "criterion_source_types.json", "w"), indent=2)
    print(f"\n  artifact: results/criterion_source_types.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
