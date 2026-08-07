# A26 — can the definition be applied without provenance?

**The decision this arc must make safe:** *can `DEFINITION.md` be applied to a core someone else
produced, or does it require the producer's source code?*

Clause ③ says a core *consumes no prompt-specific labels*. Every application of it in this project
has been made by reading `corebench/select_core.py:102` — the line where `oracle_k`, `indep_k` and
`greedy_k` open `data/comparisons.jsonl`. **That is a fact about the producer, not a property of
the produced object.** If the clause cannot be checked on the artifact, the definition is not a
definition of cores; it is a certification scheme for pipelines, and it must say so.

**Per P16 this file is a table of contents only** — every finding, its interval and its scope live
in `E05/DEFINITION.md`.

| round | what it asked |
|---|---|
| `R920` is clause ③ detectable from the artifact | does an arm's rank among all size-k subsets separate label-consumers from label-blind rules, without reading the generator? |
| `R921` is the admitted set a property of the arms or of the comparator | does changing the comparator change WHICH arms pass, or only how many? |
| `R922` is clause ② a comparison or a threshold | does the comparator do work the mean-A2 ordering cannot do? |

## Rounds indexed 2026-08-07 — GENERATED FROM ARTIFACTS, not authored

⚠ Each row's text is READ from that round's own results JSON (its `world`/`verdict` and its own
scope note). Nothing here is written from memory, and nothing is a summary I composed: a table of
contents that paraphrases is a second account of the results, which P16 forbids. For the finding,
its interval and its caveat, open the round.

`every_round_reaches_the_readme` had been failing for 93 rounds across five arcs, and
had been failing unasked for a whole session. A round that ran and is never mentioned is a result
nobody has.

| round | as its artifact states it |
|---|---|
| `R920_is_clause_three_detectable_from_the_artifact` | world **C_implies_B** · pi is a mean percentile in [0,1]; A2 is agreement in [0,1] |
| `R921_is_the_admitted_set_a_property_of_the_arms_or_of_the_comparator` | world **A** · counts are ARMS; lo is a bootstrap 2.5th percentile of a paired per-prompt A2 difference |
| `R922_is_clause_two_a_comparison_or_a_threshold` | world **A** · counts are ARM PAIRS for inversions, ARMS for admitted; the cut is in mean A2 units |
