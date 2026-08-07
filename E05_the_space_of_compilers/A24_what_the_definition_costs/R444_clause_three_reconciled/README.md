# R444 · the contradiction is closed — and it was closed by a **decision**, not an experiment

**The decision this round makes safe:** which of the two readings of clause ③ the campaign
publishes. **The set was corrected to match the text.** No new measurement was needed, and this
round says so rather than dressing the decision as a twelfth experiment.

## Why the decision was forced, not a matter of taste

R442 left two readings — ③ as **implemented** (a hand-written 4-arm set, extension **5**) and ③ as
**written** (extension **1**). Two ways to close it:

| | viable? |
|---|---|
| **(a)** correct the **set** to match the text | ✅ |
| **(b)** weaken the **text** to match what a hand-list can enforce | **only while ③-as-written looked unenforceable** |

**R443 removed (b)'s premise.** `select_core.py:131` computes `w = mean annotator importance score`,
and the file *names* every selector that consumes it. **The text is mechanically enforceable**, so
the reason to weaken it disappeared. **(a).**

## What changed

`assurance/clause3_as_written.py` derives clause ③ from the source instead of listing arms:

| origin | selectors | source |
|---|---|---|
| **target-readers** | `oracle_k`, `indep_k`, `greedy_k` | R363, audited against `comparisons.jsonl` |
| **w-readers** | `topw_k`, `topabs_k`, `topwvar_k` | R443, `select_core.py:138–152` |
| **not excluded** | `topvar_k` | its own comment: *"a property of the responses, never of the human target"* |

| | before | after |
|---|---|---|
| ③ excludes, on R360's 42-arm space | **4** | **14** |
| the definition's extension (②∧③) | **5** | **1** — `coval_core` |

**The 10 newly excluded arms are all w-readers:** `topabs_k4`, `topw_k1/k2/k3/k4/k6/k8`,
`topw_k4_sham`, `topwvar_k4`.

## ⚠ What the corrected clause cannot do, and does not pretend to

Arms whose selector the source does not name — `coval_core`, `gen`, `generic`, `promptecho` and
their shams — are returned **UNKNOWN**, never silently admitted. Clause ③ is a **provenance**
requirement and their provenance lives outside `select_core.py`. `coval_core` survives on R443's
separate measurement (containment **0.0779** against a cross-prompt sham of **0.0000**), not on
anything this file can decide.

**And shams are excluded with their parents** — `topw_k4_sham` read the same importance scores. The
objection is about what the arm **consumed**, not how well it performed.

## Selftest

| check | returned |
|---|---|
| POSITIVE — the two reader sets are disjoint | ✅ |
| 8 named cases incl. `topw_k4_sham` → excluded, `topvar_k4` → not | **8 of 8** ✅ |
| NEGATIVE — `topvar_k4` is *not* excluded | ✅ |
| g=0 — unclassifiable arms → **UNKNOWN**, not admitted | ✅ |

## ⛔ This round has no p-value, and that is correct

The campaign's own standard says a decision always closes — *deferring it is also closing it.* The
measurement that would have settled this was already done (R443); what remained was a **choice
between two documents**, and running a twelfth experiment to avoid making it would have been
activity, not evidence.

⚠ **`[unchallenged]`.** This standard prescribes dispatching a clean-context adversary for a
judgement call rather than deciding alone. **Agent dispatch is unavailable in this session**, so the
decision is recorded as unchallenged — *not* as clean. The argument that forced it is stated above
in full so a later reader can attack the premise rather than the conclusion.

Findings and their scope live in `DEFINITION.md`. This file states the decision and its reasoning.
