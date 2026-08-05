# R620 · There is no category to carve — and I committed R619's defect one round after retracting it

**Decision this makes safe:** whether to widen the gate's artifact-noun list. **No.** The unflagged
and flagged classes have **the same head-concentration**, so the list moves a boundary through a
continuum rather than closing a gap.

| top-k nouns | **VOCAB** (unflagged, n=88) | **FLAGGED** (baseline, n=105) |
|---|---|---|
| 3 | 15.9% | 18.1% |
| **5** | **22.7%** | **27.6%** |
| 10 | 34.1% | 41.9% |

**67 distinct nouns · 56 singletons (83.6% of types).** Both classes are long tails.

## ⛔⛔ World C again — I wrote two worlds, coded two branches, and the data landed between them
**R619's retraction, one round earlier, was *"three worlds designed, two branches coded."*** v1 of
this round designed **two** and coded **two**, and the answer was neither: not *head-heavy so widen
it*, not *long tail so the rejection is correct*, but **both classes are long tails of the same
shape**. ⭐ *Fixing the diagnosis did not fix the habit — the branch structure is written last, with
the same released attention as the closing sentence, and it fails the same way.*

## ⛔ The negative control failed for its own reasons, and the ceiling is why
v1 required the forward-only extractor to land on an artifact noun in **≥30% of ALL flagged lines** —
a threshold set **without ever computing what the design can return**.

| where the gate's noun actually sits | share of flagged |
|---|---|
| **AFTER** the quantifier — reachable | 34.8% |
| **BEFORE** the quantifier — invisible to a forward-only rule | 34.8% |
| flagged by `BARE_COUNT`, no quantifier rule at all | 17.0% |
| the **first** quantifier is not the one that fired | 13.4% |

**Ceiling = 34.8%, and the threshold demanded 86% of it.** §4's remedy verbatim — compute floor and
ceiling, require `floor < t < ceiling`. Normalised to the reachable subset the control becomes a
**recall measurement**: **56.4% — noisy but not blind**, so the distribution is a noisy sample and
the shape claim is stated with that attenuation.

## ⛔ Check #219 — two overstatements in the previous closing line
- *"the open-vocabulary failure R594–R596 measured on the `world` field"* — **an analogy stated as an
  identity.** That was a **data field I control and could have typed**; this is **prose**, open-
  vocabulary by nature and not thereby defective. Same shape, different mechanism.
- *"cannot be made sound by adding words"* — **a universal I did not compute.** A keyword list has a
  precision/recall tradeoff, and which regime it sits in is measurable. It is measured above.

## Controls
| control | returned |
|---|---|
| **positive** — the one known miss (#217) must surface with noun `axis` | **1 line** — PASS |
| **g=0** — empty population | **0 nouns** — PASS, it can return nothing |
| **negative (repaired)** — recall on the reachable subset | **56.4%** vs a **37.1%** ceiling on all flagged — PASS |
| **placebo** — a noun occurring nowhere | **0** — PASS |

**MULTIPLICITY:** 88 + 105 lines × 1 extractor + 4 controls + 3 threshold cells. All reported.

**IMPOSSIBLE, named:** *"this noun denotes a project artifact"* is a judgement no extractor can make.
The 30 most frequent nouns are printed **verbatim with counts** so a reader overrules the reading;
**head-concentration is the only thing asserted.** ⚠ And **13 of 88 lines carry more than one
quantifier**, counted by their first — line-level and token-level counts differ, and that is the gap.

## The sentence I can no longer write
> *"87 lines sit outside the artifact-noun list, so the list needs widening."*

**They sit outside a list whose inside has the same shape as its outside.** Widening it changes which
lines are flagged without changing what kind of line gets flagged.

## NEXT
Three consecutive rounds have now been about the gate rather than the definition, and each found the
gate less broken than the last (`amnesty` 1 of 368 → the vocabulary gap is not a gap). **Return to the
object.** `FORMULATION.md` still flips zero gates — measured, in the long-standing debt list — so ask
what a gate over `FORMULATION.md` would have to check that `STATEMENT.md`'s six do not, and whether
that check is computable from artifacts already on disk.
