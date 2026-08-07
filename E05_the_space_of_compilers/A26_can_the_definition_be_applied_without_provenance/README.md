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
