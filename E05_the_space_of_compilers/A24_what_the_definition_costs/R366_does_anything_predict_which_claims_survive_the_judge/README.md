# R366 — nothing in the record predicts which claims survive the judge, and R365's survival was cheap

**The decision this makes safe:** *should the definition be restated in differences?* **No — that
proposal rested on a hypothesis my own committed artifacts refute.**

## Result — `W_NEITHER_SORTS`. Controls PASS, **including power.** Two runs byte-identical.

R365's commit closed with a mechanism *and an action*:

> ~~*"it survived because it is a claim about a DIFFERENCE rather than about a level, and differences
> are what shrink transformations preserve. … the definition should be restated in differences
> wherever possible."*~~

**It was never checked.** Here is the whole population — every claim this campaign has run at both
judges, enumerated from artifacts:

| round | form | null | survived | claim |
|---|---|---|---|---|
| R301 | level | no | **no** | the definition admits a non-empty set (2B 5 arms → 0.8B 0) |
| R355/R358 | level | no | **YES** | the closed region is not upward-closed (18 → 4, k overlap 12,13) |
| R362 | **difference** | no | **no** | size-band step 1→2 resolves |
| R362 | **difference** | no | **no** | size-band step 2→3 resolves |
| R362 | **difference** | no | **YES** | size-band step 8→12 resolves |
| R361 | level | no | **no** | no reference purges a label-user (4 → 0) |
| R364/R365 | **difference** | **yes** | **YES** | the rubric channel carries nothing |

| classification | survived / died | vs other | Fisher exact p |
|---|---|---|---:|
| **DIFFERENCE** | 2 / 2 | 1 / 2 | **1.0000** |
| **NULL** | 1 / 0 | 2 / 4 | **0.4286** |

## This is a null, not silence — the positive control decides that

A **perfect** separation at n=7 (3/0 vs 0/4) reaches **p = 0.0286**. So the design *could* have
resolved a sorting rule and **did not**. Had it not cleared 0.05, both p-values above would have been
silence and no rule could be read from them in either direction.

g=0 (same marginals, no association) returns **1.0000**; the placebo (all claims classified alike) is
degenerate, never a pass.

## Two things that hold independently of any p-value

**① The observation that started the round.** R362's adjacent-k steps are **differences of
differences — the same algebraic form as R365's dose contrast** — and **1 of 3** survive. So
*"it is a difference"* fails as an explanation regardless of the test, **because differences do both
here.**

**② ⛔ The rival explanation is a DERIVATION, and it downgrades my own last headline.** Under **any**
scaling `x → βx`, a **true zero maps to zero exactly**, while a true nonzero maps to `β·nonzero` and
may fall below its MDE.

> **A null claim surviving a shrink is the cheapest possible survival.** R365 *is* a null.

So *"the first claim in this definition to survive a change of judge"* is true and **worth less than
it sounds** — it survived partly by being a zero, and zeros are preserved by construction.

## What is withdrawn

- **`restate the definition in differences wherever possible`** — an action I proposed one round ago,
  resting on a hypothesis with **p = 1.0000** on a powered test.
- **The weight of R365's headline** — corrected in `DEFINITION.md` and the top-level README rather
  than left standing.

## What is not withdrawn

R365's measurement itself. The dose is flat at both judges, the controls hold at both, and the 0.8B
design was wide enough by only 1.11×. **What changes is what that survival is evidence FOR.**

## Register

| criterion | status |
|---|---|
| **a larger population** | **N/A** — the 7 claims here are *all* the campaign has run at both judges; more requires more cross-judge rounds |
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) |
| **separating `form` from `nullness`** | on this population the labels nearly coincide; a bigger set would be needed to tell them apart |

## The sentence I can no longer write

> *"it survived because it is a difference, and differences are what shrink transformations
> preserve — so the definition should be restated in differences."*

**Differences do both here, and the one that survived is a zero.**

Artifact: `results/r366_what_survives.json`, source-stamped.
