# R327 — clause ② names a class, not a reference, and the under-specification is load-bearing

**Decision this makes safe:** whether *"two arms admitted of nine"* can be stated without naming a
clause-② reference. **It cannot — the claim is true under one reading and false under another.**

## The asymmetry, in the definition's own words

> **①** better than the same number **drawn at random** from that conversation's own rubric
> **②** better than the same number that **never read the conversation at all**

Clause ① names a **procedure** — draw at random from a stated pool — so the comparison it licenses
is unambiguous. **Clause ② names a class, no member and no procedure.** English reads it most
naturally as a *universal*: better than any such set. The campaign has instead tested it against
five different members, and R326 measured that they disagree.

## W-DIVERGES

| reading | reference | `coval_core` | `topw_k4` | admits |
|---|---|---:|---:|---|
| **A · UNIVERSAL** — better than *every* prompt-blind set of that size | best held-out of 1,820 | 1.18× | **0.92×** | `coval_core` only |
| **B · NAMED** — better than a stated held-out reference | `generic` @ k=4 | 1.41× | 1.19× | **both** |
| **C · PROCEDURAL** — better than one *drawn at random*, symmetric with ① | budget 0 · random | 2.69× | *unmeasured* | `coval_core`; `topw_k4` **not run** |
| *✗ disqualified* — in-sample argmax | 0.5575 | *0.87×* | — | *none — negative control, not an option* |

> **`Two arms admitted of nine` is true under reading B, FALSE under reading A, and UNDETERMINED
> under C** — and the definition does not say which it means.

## ⚠ Same shape as R293, which this definition already suffered once

`held out from the core's own construction` was **an adjective nothing computed** until a round
asked *held out from what*, and applied to `oracle_k4` the definition **admitted** an arm its own
author called leaky. **`never read the conversation at all` is the same shape** — a phrase that
sounds like a criterion and never names what it is measured against.

## ⚠ And the tension is real, not a drafting slip

Reading **C** is the one **symmetric with clause ①'s own wording** — and R287 already established
that *a random draw is too weak a baseline to test anything against*. **So the symmetric reading is
the weakest test, and the strongest test breaks an admission.** That is a choice about what
*better* quantifies over; **no measurement settles it**, which is why this round prices the options
and does not pick.

## Controls

| control | result |
|---|---|
| **positive** — the strictest reading must admit no more than the loosest | 1 vs 1, holds |
| **negative** — the disqualified in-sample argmax carried, not offered as an option | present |
| placebo | n/a and stated: this round selects among measured cells; inventing a zero-contrast would be decoration |

## ⚠ Unmeasured is not not-admitted

The first version reported reading C's admitted set as `['coval_core']` — which reads as an
exclusion and is **an absence of data**: R287 never ran `topw_k4` at budget 0. **Sixth population
error this session**, same fix each time — make the three-valued split explicit, and read divergence
off the readings that measured **both** arms.

And the verdict sentence initially said *"true under B and C"*. **C is unmeasured**; a verdict string
must not fill in a cell the round did not compute.

## Scope

The two arms clause ② currently admits · 968 prompts · A2·annotator · references as published by
R286, R287, R307, R308. This round **selects among R326's committed cells** and adds no estimate.

## What this cannot do

**Decide which reading the definition should take.** That is a choice about quantification, and the
round's job is to price each option — not to pick.
