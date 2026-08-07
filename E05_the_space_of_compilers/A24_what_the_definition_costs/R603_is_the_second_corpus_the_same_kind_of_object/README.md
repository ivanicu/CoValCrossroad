# R603 · The second file is a second DATASET, not a second RELEASE — and KIND, not overlap, is why

**Decision this makes safe:** whether the impossibility register's row 5 is discharged. **It is not.
R556's argument is overturned; R556's conclusion stands.**

**WORLD B DIFFERENT KIND. 2 of 5 requirements unsatisfiable. 0 shared top-level key names.**

| requirement | serves | home | second |
|---|---|---|---|
| a prompt / user turn | ②③ score responses *to* something | `prompt` | `user_prompt` — **DIRECT** |
| multiple responses per unit | ② compares a core's **ranking** | `responses` | `model_response` — **DIRECT** |
| a human preference target | A2 = agreement with a held-out annotator | `responses` | `score` — **DIRECT** |
| **shipped criteria (a rubric)** | **② is *"better than the released pool"* — the pool IS the baseline** | `coval_full`, `coval_core` | ⛔ **ABSENT** |
| **a released core** | **the object the definition is written from** | `coval_core` | ⛔ **ABSENT** |

⭐⭐⭐ **Clause ②'s baseline is "better than the released pool", and there is no released pool in the
second file. ② as written is not evaluable there** — R433 had to substitute a generated baseline,
which is why its `W-LOSES` is a result about a *different comparison*.

## ⚠ My first reading was an over-swing, and it is recorded as one
R602 measured the corpora as disjoint, and I began to read that as an objection to row 5.
**It is not. Disjointness is what a replication WANTS** — new data is the point, and low overlap is
not a defect. **The question is KIND, not overlap**, and the schemas decide it without any corpus
statistic. *That distinction is the round.*

## What falls and what stands in R556
| | |
|---|---|
| ⛔ **overturned** | *"one is already on disk"* — the file cannot carry ②'s baseline |
| ✅ **stands, and is strengthened** | *"what is missing is a second **designer**"* — with the release route closed, it is the **only** live one |

## ⛔ The placebo presupposed a non-null effect, and the zero it tripped over is the finding
v1's placebo was *"a key present in BOTH releases must be found in both"* — **undefined when the
intersection is empty, and it is empty.** §4's *the control presupposes a non-null effect*, and the
failure was mine, not the data's.

⭐ **Zero shared top-level key names is a RESULT, not a broken control** — the schema-level form of
the same answer the requirement table gives. Replaced with a placebo that can pass either way:
`prompt` must be found home-only and `score` second-only. **PASS.**

## Controls
| control | returned |
|---|---|
| **positive** — every requirement found in HOME, where all are known present | **5/5** — PASS |
| **negative** — a key present in NEITHER release | **absent in both** — PASS, absence is detectable |
| **placebo** — `prompt` home-only, `score` second-only | **PASS** |
| **reconstruction** — can multiple responses per unit be rebuilt in second? | **yes**: median **2** per `interaction_id` (98.90% have ≥2), median **8** per `conversation_id` (99.99%) |

**MULTIPLICITY:** 5 requirements × 2 releases + 3 control checks. **2 unsatisfiable.**

**IMPOSSIBLE, named:** *"the same kind of object"* is a judgement about what the estimand needs, **not
a property of a file.** Every requirement is printed with the clause it serves, marked direct /
reconstructed / absent, so a reader can overrule any row.

**DERIVATION, labelled:** that HOME satisfies its own estimand is forced — the estimand was written
from it. It is the positive control's ceiling, not evidence.

## ⛔ Check #202
R602 closed asserting *"R433 scores per interaction while the home release scores per prompt"* **as
fact, from a docstring comment I had read once — never from the keying code.** Door ①: a convincing
description is the most dangerous evidence, and it was my own. **This round reads the schemas
instead**, and the reconstruction numbers above are what that assertion should have been.

## The sentence I can no longer write
> *"a second release is already on disk, so independent replication is available here."*

A second **dataset** is on disk. **It has no rubric and no core**, so the clause the definition rests
on cannot be stated against it.

## NEXT
Two of five requirements are absent and **both are reconstructible in principle** — a rubric could be
generated and a core selected from it, which is what R433 did. **Measure what that substitution
costs**: R433's generated baseline versus the home release's `coval_full` pool, scored on the *home*
release where both exist. **If the generated pool is materially weaker, then every second-corpus
number is measured against a baseline that is not ②'s** — and that is checkable on the home release
alone, with no second corpus involved.
