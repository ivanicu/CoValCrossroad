# R593 · The artifact was never the carrier — and the codeless rounds carry less even so

**Decision this makes safe:** stop treating `codeless` as the variable that governs whether a claim
can be attacked. **The corpus never used artifacts as claim carriers**, and fixing the 8 cited
codeless rounds would repair 8 of a problem that has 569.

**Both answers are true, on two orthogonal axes, in both specification cells.**

| depth | \|convention\| | codeless | code-bearing | Δ | p (time-stratified) |
|---|---|---|---|---|---|
| **top-level** | 4 | 0.2500 | 0.3501 | **−0.1001** | **0.0012** |
| **all-depth** | 5 | 0.2083 | 0.3449 | **−0.1366** | **0.0002** |

**SPEC SURVIVAL: both cells agree** on both axes.

## ⭐⭐⭐ The convention barely exists — that is the finding
Derived from the **545 code-bearing rounds only** *(the group under test contributed nothing, so it
cannot be circular)*, keys at ≥20% prevalence:

| key | prevalence |
|---|---|
| `verdict` | **0.49** |
| `world` | 0.44 |
| `controls` | 0.26 |
| `n_prompts` | 0.22 |

⛔ **The most common key in the entire corpus's artifacts appears in fewer than half the rounds.**
Mean coverage is **0.35 among code-bearing rounds and 0.21–0.25 among codeless ones** — *nobody* was
writing scope into artifacts. **`codeless` was the wrong variable**, and R592's NEXT line — which
proposed auditing 8 rounds — was aimed at a subset of a corpus-wide property.

⚠ **And world B is ALSO true and ALSO resolved:** codeless rounds carry significantly less even
against that low bar, **p = 0.0012 / 0.0002 time-stratified over 12,000 draws**, in both cells.

## The 8 cited codeless rounds, named
`R444 · R544 · R545 · R546 · R578 · R580 · R581 · R585` — **every one carries exactly `world` and
nothing else. Zero variance across all eight.** They record the **answer** and none of the
**conditions**. ⚠ Reported as a **bound, not a point**: n = 8 is far below anything this design
resolves.

## ⛔ Three defects in my own design this round, all one family
1. **The world set was not a partition.** `C` is about the **absolute level**; `A`/`B` are about the
   **difference** — orthogonal axes chained with `elif`, so **C silently shadowed a second answer
   that was also true and also resolved**. Both axes are now computed and both reported.
2. **The MDE comparison was malformed.** `under_powered = |Δ_obs| < |Δ_MDE|` compares the **spread**
   observed contrast against a **concentrated** plant (scores forced to 0.0 in a random subset) —
   two variance structures treated as one object, §4's *the control fails for its own reasons*,
   form ①. The observed effect has its own test — the stratified permutation — and that is the only
   admissible one for it.
3. **The spec-agreement test compared formatted strings with the p-value interpolated into them**, so
   two identical conclusions could never compare equal. It printed `THE CELLS DISAGREE` on two cells
   that agree. **Third unit-mismatch of the session in this round alone**; fixed by comparing a
   number-free tag.

⚠ **All three were invisible until a number contradicted the branch.** None would have been caught by
re-reading the code.

## Controls
| control | returned |
|---|---|
| **positive** — convention stripped from 24 random code-bearing rounds | Δ = **−0.3477 / −0.3370**, p = **0.0001 / 0.0007** — PASS |
| **positive @ g=0** — nothing stripped | reproduces the observed Δ exactly — PASS, it can fail |
| **dose-response** | 10% → p 1.0000 · 25% → 0.0440 · **50% → 0.0007** · 75% · 100% |
| **negative** — permutation **within 5 time bands** (12,000 draws, floor 0.00008) | p = 0.0012 / 0.0002 |
| **unstratified, for contrast** | p = 0.0295 — **weaker than the stratified test**, so the time trend was *masking* this effect, not creating it |
| **placebo** — random flag at the same marginal, 3 seeds | +0.037 / +0.016 / −0.061 — PASS |

⭐ **The time-stratification was built in the same iteration because R592 had just measured the
confound** — and it *strengthened* the result rather than dissolving it. **That is the opposite of
what happened one round ago, and the reason to run the control either way.**

**IMPOSSIBLE, named:** key **presence** is not key **content** — a round can write `"world": "B"` and
mean nothing by it. Establishing content would need an external reader scoring each artifact against
its own README, a gold standard this site does not have. **Every number bounds attackability from
above.** Δ is a **DERIVATION** over a complete enumeration; only the permutation p is tested.

## The sentence I can no longer write
> *"the 8 cited codeless rounds are where the deliverable's claims lack a carrier."*

**569 rounds lack one.** The 8 are the visible corner of a corpus-wide convention that was never
adopted.

## NEXT
`verdict` and `world` are the only keys with meaningful prevalence, and **R593's own artifact records
`world` as a sentence rather than a letter** — so the corpus's most-used key has no enforced type.
**Measure how many distinct `world` values exist across the 239 rounds that write one**, because a
key whose vocabulary is unbounded is a free-text field wearing an enum's name — HB8's schema bug —
and that is checkable without any judgement about content.
