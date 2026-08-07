# R1063 — the join is blocked at the KEY, and the universes are disjoint anyway. ⭐ **The line closes: score-level comparison was valid throughout.**

**The decision this round makes safe:** whether R1062's prescribed recovery of a global criterion
identity is worth building. **It is not executable as described** — and the object answers the
question without it.

## ⛔⛔ First: the id finding is NOT NEW — R466 has it, and I rediscovered it

`DEFINITION.md` already records, from **R466**: *"rubric-text ids **986**, ranking ids **1078**,
**intersection 0** — the two instruments cannot be joined on disk without a mapping, and none was
used."*

⭐ **I built this round without running the prior-art gate**, and the disjointness half is a
rediscovery. Worse, **what surfaced it was an accident**: the currency gate went GREEN with nothing
written because my registered pattern coincidentally matched R466's own sentence. **A coincidence is
not a mechanism** — the gate that should have caught this is L20/P4, run before building, and I did
not run it.

⚠ My numbers differ from R466's on one side — **968** (`core_full`'s prompts) versus its **1078**
(ranking ids) — because we counted different populations. R466's statement stands; mine adds the arc
key by name.

## What IS new here

| | |
|---|---:|
| `core_generic` distinct criterion texts across **all 968 prompts** | **4** |
| distinct per-prompt selections for `generic` | **1** (prompt-blind, by construction) |
| `core_full` distinct criterion texts | **14,808** |
| **strings shared between them** | **0** |

**R466 is about ID spaces. This is about CRITERION spaces**, and it is not in the record.

## The join is blocked at the key

| | |
|---|---:|
| arc prompt ids (`corebench/results/*`) | **968** |
| rubric conversation ids (`data/conversation_rubrics.jsonl`) | **986** |
| **intersection** | **0** |

The rubric file is keyed by `conversation.id`; **every artifact in this arc is keyed by
`comparisons.jsonl:prompt_id`** (measured: 968 of 1,078 scanned rows carry one). The two sets share
nothing. R1062's prescription would need a bridge built from **message text** — a different and much
larger task than the join it described.

⭐ **The round's own empty-population guard caught this**: the first version joined on
`conversation.id`, got 0 prompts, and **exited 2 rather than reporting a zero overlap as a finding**.

## ⭐⭐ And the object answers the original question without the join

| | |
|---|---:|
| `core_generic` distinct criterion texts across **all 968 prompts** | **4** |
| distinct per-prompt selections for `generic` | **1** (prompt-blind, by construction) |
| `core_full` distinct criterion texts | **14,808** |
| **strings shared between them** | **0** |

`generic`'s four are fixed generic sentences — *"the reply is accurate and factually correct."*,
*"…clear and easy to understand."*, *"…helpful and addresses what was asked."*, *"…avoids harmful or
unsafe content."* — **not rubric items at all**.

⭐ **The two arms draw from DISJOINT criterion universes.** That fully explains R1062's 96% index
disagreement: **there is no correspondence to recover.** Criterion-level cross-arm claims are
**meaningless**, not merely unrecovered.

## ⭐⭐⭐ Which closes the line rather than extending it

**The admission operator consumes a RANKING of the same four responses — never criteria.** Two arms
drawing from disjoint criterion universes still rank the same objects, so **score-level comparison was
valid throughout**. Only **R1061's criterion-index reasoning** was ever void, and R1062 already
withdrew it.

## Controls

- **POSITIVE** — the arc's key must be **locatable in the release**, or *"disjoint"* is just *"not
  found"*: **True** (`comparisons.jsonl:prompt_id`).
- **NEGATIVE** — the two key spaces shown disjoint on the **full sets**, not on a sample: **True**. My
  first check compared against 3 rubric ids and would have been worthless.
- **PLACEBO** — a rubric against itself overlaps completely: **True**.
- **EMPTY POPULATION** — exit **2**, never 0; this is the control that fired first.

## IMPOSSIBLE here

- **whether two differently-worded criteria mean the same thing** — exact text match measures **string
  reuse**, the weaker question and the only one committed text can answer.
  **SETTLES: OUT-OF-RELEASE** for semantics.

`run.py` · `results/criterion_universes.json`
