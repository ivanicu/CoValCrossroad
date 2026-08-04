# R465 · clause ③ is a **provenance** predicate — the definition mixes two types of clause

**The decision this round makes safe:** what a reader holding a criterion set can actually verify.
**Three clauses of four.** `W-PROVENANCE`.

## ⛔ Rung 1 killed the announced step's framing, zero compute

R464 closed proposing to *"construct the adversarial case and check the **predicate** rather than the
label"* for ③. But ③ — *no prompt labels* — is derived by R444 from `select_core.py`: it is
determined by **which selector built the arm**, and is therefore **invariant under every measurable
property of the object** (criteria, satisfaction scores, A2). **Two arms with identical criteria, one
built by reading the prompt's human labels and one by luck, are behaviourally indistinguishable and ③
must treat them differently.** *"Measure that ③'s predicate fires on an object"* is not a coherent
test. *Thirty-third announced step checked; framing killed, and the corrected question is sharper.*

## The corrected question — about the definition's **type structure**

①, ② and ④ are **behavioural**: hand someone an arm and they can check them. ③ is not. **If ③ can
separate two behaviourally identical objects, the definition mixes two kinds of clause** — and a
formulation that claims to be complete must say which clauses are checkable from the object alone.

## Result

| | n | collision |
|---|---|---|
| **CHOICE prompts** (≥2 candidate subsets) | 967 | **0.0097 — 9 prompts**, seed spread 0.0018 |
| FORCED prompts (exactly one subset) | 1 | 1.0000 — **DERIVATION**, excluded from the rate |
| label-free vs label-free baseline | 967 | 0.0062 |

> ⭐ **On 9 prompts a label-READING selector emits exactly the set a label-FREE one emits** —
> identical criteria, identical scores, **identical A2 to machine precision** — **and ③ excludes one
> while admitting the other.**

⚠ **0.0097 against a 0.0062 baseline is not a resolved difference, and does not need to be.** The
estimand is **existence**, not rate: one collision suffices to show ③ separates identical objects.
The baseline exists so that *"they sometimes agree"* cannot be over-read as a label effect.

## Controls

| control | returned |
|---|---|
| **DERIVATION** — prompts with exactly one possible subset | **1.0000**, exactly, by construction ✅ — *and it doubles as the positive control on set identity: if it were not 1.0, the comparison would be broken* |
| **IDENTITY** — collided arms must have identical A2 | true to machine precision ✅ *asserted, not assumed* |
| **NEGATIVE** — two independent label-free draws | 0.0062 — the baseline a label-reader is read against |
| SEEDS | 3 draws; spread 0.0018 |

## ⭐ What this costs the formulation

**①, ② and ④ can be checked on an object you are handed. ③ cannot.** A reader given a criterion set
can verify three of the four clauses and **has no way to verify the fourth** — they must be given the
construction history too.

That is not a defect to remove; provenance requirements are legitimate. **It is a fact the
formulation must state**, because a definition that reads as four uniform predicates silently
promises a check it cannot deliver.

⚠ **What it does not establish:** that a real generator would ever collide. The collision was
**constructed**, on purpose, to expose ③'s type — which is the point of the test and equally its
limit.

## Impossible here, named

- **a natural collision rate for a real generator** — needs a generator; this constructs instead.
- **checking ③ on an object without its construction history** — that is the finding, not a gap in it.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
