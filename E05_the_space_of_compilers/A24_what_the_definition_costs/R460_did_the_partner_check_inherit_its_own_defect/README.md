# R460 · R459 inherited the defect it was built to test — and both quoted numbers are outliers

**The decision this round makes safe:** whether R459's partner-free result rested on its own n=1
draw. **It did.** `W-STRENGTH`.

## The announced step survived and indicts its proposer

R459 attacked R457 for an estimand whose sham partner was **drawn once and frozen**, then answered it
with `core − generic` — where `generic` is **one** fixed prompt-blind set, drawn from a population
R450/R453 measured at **0.0033–0.6247** in strength. *Twenty-eighth announced step checked.*

**And it is cheaper than announced, which changed the design:** every fixed size-4 prompt-blind set is
a **row** of the C(16,4) matrix already built, so this is a **census of all 1,820**, not a sample of
"several". No selection, nothing to correct.

## Result — the whole comparator population

| min | p5 | p25 | median | p75 | p95 | max | **IQR** |
|---|---|---|---|---|---|---|---|
| 0.8226 | 0.8342 | 0.8419 | **0.8486** | 0.8544 | 0.8601 | 0.8675 | **0.0125** |

| quoted number | ρ | where it sits |
|---|---|---|
| R459's `core − generic` | **0.8114** | **percentile 0.000** — below *every* one of the 1,820 |
| R457's `core − sham` | **0.8726** | **above the census max** (0.8675) |
| corr(ρ, strength) | **−0.7995** | reliability rises as the comparator **weakens** |

> ⛔ **R457's 0.8812 and R459's 0.8363 are two extremes, and the entire comparator population lies
> between them.** Their agreement within ±0.15 was arithmetic, not evidence: two outliers on
> opposite sides will always bracket the middle.

**The mechanism is understood, not just observed:** a weaker comparator contributes less signal
variance, so the difference is dominated by the core's own reliable variation and ρ rises. **A high
"reliability of the advantage" is therefore partly a statement about the comparator being weak.**

## ⚠ What this does and does not overturn

- **Does not overturn:** that the per-prompt advantage is reliable. **The census minimum is 0.8226** —
  *every* comparator gives high reliability. The per-prompt structure is real.
- **Does narrow:** the *number* and its reading. The honest quantity is the census IQR
  **0.8419–0.8544**, and any single-comparator figure must name its comparator.
- **Does narrow R459's conclusion:** "the result does not depend on the partner" was inferred from two
  numbers agreeing. The census shows *why* they agreed and that neither is representative.

## Controls

| control | returned |
|---|---|
| ANCHOR-1 — `core − generic` vs R459's committed 0.8363 | **0.8114** ✅ *(single split here vs R459's 5-split mean)* |
| ANCHOR-2 — `core − sham` vs R457's committed 0.8812 | **0.8726** ✅ *(the sham is **not** in this population; printed as a reference line, never a percentile)* |
| NEGATIVE — prompt labels of half B shuffled | **+0.0129** ✅ |
| g=0 — F = the core itself | `d = 0` identically → ρ **UNDEFINED**, constructed explicitly and reported as undefined |
| across-seed spread of the quartiles | p25 0.0100 · med 0.0099 · p75 0.0094 |

## ⛔ And I mixed two objects in one sentence — caught in-round

The first version printed *"R459's `generic` sits at ρ 0.8114 → percentile 0.041"*. **0.8114 is the
generic ARM** (from `sat_generic.npz`); **0.041 was pool ROW 0's** percentile, on the assumption that
`generic`'s criterion indices `(0,1,2,3)` name the same texts as pool16's indices 0–3.

**Index identity is not text identity** — my own R451 caveat, applied to the wrong file. They are
genuinely different objects: pool row 0 sits at **ρ 0.8337, percentile 0.041**, while the generic arm
sits at **0.8114, percentile 0.000**. Both are now reported separately and labelled, and the
percentile that matters is computed **by value**.

## Impossible here, named

- **comparators outside this pool** — exactly one prompt-blind family with breadth exists (R454).
- **decomposing partner variance for the sham** — unchanged from R459: the partner is fixed per prompt.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
