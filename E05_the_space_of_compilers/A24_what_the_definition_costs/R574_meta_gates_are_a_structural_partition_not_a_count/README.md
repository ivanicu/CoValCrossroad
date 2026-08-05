# R574 · The suite is 7 meta-gates and 39 ordinary ones — a partition, not a count

**Decision this makes safe:** what the debt list is a list of.

**WORLD B.** My NEXT line said to *"re-count the suite's sixteen non-passes"*. ⛔ **R570 retracted
that count two rounds earlier** — it is a draw (9, 10, 13 across three runs). **So this round
partitions structurally instead: a static source read is not a draw.**

| | n |
|---|---|
| **META** — runs sibling gates or every round's `run.py` | **7** |
| ORDINARY | 39 |
| of the META, hit the 90s cap | **3 — all 3 cap-hitters are META** |
| of the META, finish comfortably | **4** |

**META:** `attack_every_check` · `attack_no_withdrawn_framings` · `attack_outcome_variable_declared`
· `attack_scope_reaches_the_reader` · `attack_the_suite`⏱ · `backfilled_findings_are_rederivable`⏱ ·
`what_did_each_check_actually_read`⏱

⭐⭐⭐ **Being META is necessary but not sufficient for capping: 3 of 7 cap, 4 do not.** So cost is
part of the story and not all of it — which is a sharper statement than either "they hang" (R571,
retracted) or "they are three distinct defects" (R572's implication).

## ⛔ My pattern was the defect, for the seventh time this session
The first run returned **1 META against 3 cap-hitters**. The pattern required the literal
`executable` in the argument list; **`attack_the_suite` writes `subprocess.run([PY,
f"assurance/{check}.py"])`** — a module-level alias. **False negative.** Corrected to match **the
object being run**, not the name of the interpreter variable, it returns 7.

⭐ **And that unifies what R572 could not.** R572 asked whether the three cap-hitters share a
mechanism and answered **no**, correctly, on the feature it tested — `subprocess` presence is
neither necessary nor sufficient. **The right feature is one level up: *runs a fleet of sibling
processes*. All three do.** R572's finding stands; **its implication — "at least two distinct
defects" — does not.**

## Controls
- **Positive** — `what_did_each_check_actually_read` classifies META *(R573 read its loop directly)*.
- **Negative** — `statement_provenance` classifies ORDINARY: it opens two documents and exits.
