# R676 · the number FIVE is stable; the MEMBERSHIP is not

**⭐⭐⭐ Four committed artifacts state a five-member extension. Their intersection is exactly one arm
— `coval_core`, the object the definition was written from. Mean pairwise Jaccard 0.273 against a
0.008 chance floor.**

## WHY THIS ROUND AND NOT THE ONE R675 ASKED FOR
A **gauge test** (attack ladder step 1, zero compute) showed R675's proposed method is sound — a
round commit touches exactly one `run.py` and one `README.md`, so its diff *does* place a bare
basename. **That makes it a five-line resolver fix, not a round.** And a drift audit settled the
priority: of the headlines of **R672, R673, R674, R675 — zero make a claim about the object.**
**R664 measured this exact drift eleven rounds ago (0 of 24) and I walked straight back into it.**
⭐ The object-level fact was again sitting in committed artifacts, which is also what R664 found.

## THE CENSUS (every set printed, none sampled)

| set | cited | members |
|---|---|---|
| ③-rank extension | **22×** | `coval_core, topw_k3, topw_k4, topw_k6, topw_k8` |
| criteria-differ (not an extension) | 6× | `greedy_k4_fit1, indep_k4_fit1, oracle_k4, topvar_k4, topwvar_k4` |
| `R442.published_five` | 1× | `coval_core, topabs_k4, topvar_k4, topw_k4, topwvar_k4` |
| `R470.P` | 1× | `coval_core, greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1` |
| `R509.five` | 1× | `coval_core, greedy_k4_fit1, indep_k4_fit1, oracle_k4, topw_k4` |
| `R404.rubric_rules` (rule **prefixes**, not arms) | 1× | `full, topabs_k, topvar_k, topw_k, topwvar_k` |

- **6** distinct five-member arm sets · **4** of them assert an *extension* · union **17 arms**
- ⭐ **intersection of the 4 extension readings: `{coval_core}`** — one arm
- mean pairwise Jaccard **0.273** (extension subset) · **0.183** (all six) · **chance floor 0.008**
- Registered **A: 6 [4,12] → 6, error 0** · **B: 0.35 [0.15,0.60] → 0.183, INSIDE, −0.167** ·
  **directional (above chance) HOLDS**

**Controls.** POSITIVE: known-identical sets → 1.00. **g=0**: the same comparator on a known-different
pair → 0.67 (**it can return <1**). NEGATIVE: disjoint → 0.00. PLACEBO: a set against itself → 1.00.

## ⚠ TWO UNIT FAILURES IN MY OWN INSTRUMENT, ONE REPAIRED AND ONE PARTITIONED
The docstring asserted *instrument unit == claim unit, EQUAL*. **It was false twice.**
1. The first matcher admitted **arm PAIRS** (`R304`: `'coval_core(A) − generic(e)'`) and **rule
   PREFIXES** (`R404`: `topw_k`, no k value). Requiring membership in a canonical arm vocabulary
   removed the pairs — **7 → 6** — and **did not remove the prefixes**, which appear in ≥2 artifacts
   as bare strings.
2. Deeper: **not every five-member arm set is an extension claim.** `R416/R422/R423`'s set answers
   *"which arms' criteria differ"*.

**Partitioned rather than patched a third time** — a third patch would be fitting the instrument to
the answer. Both counts are reported and the headline rests on the extension-claiming subset.

## WHAT THIS SAYS ABOUT THE DEFINITION
The deliverable quotes *"the extension is 5"* as a fact about the definition. **It is a fact about
four readings that agree on a count and share one member.** And that member is `coval_core` — so
this is §4's *"the definition describes the instance"* failure mode, now with a number: **every
reading of the extension contains the instance, and nothing else in common.**

⚠ **NOT ANSWERED, and it is a decision rather than a measurement:** which reading the definition
*should* take. This round establishes that the readings differ; it does not adjudicate them.

## NEXT
The four extension readings share `coval_core` and differ everywhere else
(`results/five_member_sets.json`, field `extension_intersection`). Each was produced by a different
③ variant — ③-rank, ③-as-written, ③-checkable, ③-published. Read those four variants out of their
rounds' code and tabulate, per reading, **which ③ text produced it** — then the disagreement becomes
a comparison between four stated clauses rather than four lists, and whichever clause a next site
must implement is nameable.
