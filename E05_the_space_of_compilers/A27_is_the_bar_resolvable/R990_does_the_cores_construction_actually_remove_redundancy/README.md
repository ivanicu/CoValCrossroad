# R990 · the core's construction really does remove redundancy — and the confound ran against the finding

**THE DECISION THIS MAKES SAFE.** Whether `non-redundant`, the property R988 found the definition
has no clause for, is a real property of the released cores or only an artefact of rewording. **It is
real**, at the lexical level, resolved on every seed.

---

## The design, and why the confound is the whole point

Core items are **synthesized** — the card: *"rewrites all rubric items … merges semantically
redundant rubric items."* So they use different words from full items **by construction**, and a
lower within-core overlap could mean redundancy was removed **or** merely that rewriting changed the
wording. A raw core-vs-full comparison cannot separate those.

**Difference-in-differences against cross-prompt baselines**, which carry each set's own vocabulary
and no shared topic:

```
DiD = (core_within − core_cross) − (full_within − full_cross)
```

The **sham** is the same-prompt full-rubric subset: identical topic, identical annotator pool,
size-matched — differing only in that no selection step ran.

## The result

| seed | core_within | full_within | core_cross | full_cross | **DiD** | 95% CI |
|---|---|---|---|---|---|---|
| 11 | 0.0253 | 0.0326 | 0.0081 | 0.0058 | **−0.0095** | [−0.0119, −0.0070] |
| 22 | 0.0253 | 0.0307 | 0.0076 | 0.0059 | **−0.0071** | [−0.0094, −0.0049] |
| 33 | 0.0253 | 0.0315 | 0.0090 | 0.0064 | **−0.0087** | [−0.0111, −0.0064] |

**Resolved on 3 of 3 seeds**, cluster-bootstrapped over prompts (the independent unit), 2,000 draws.

⭐ **The confound ran AGAINST the finding, which is the part worth keeping.** Raw gap **−0.0063**;
after correction **−0.0084**. Synthesized core items are *more* alike across prompts (0.0081) than
full items are (0.0058) — a shared synthesis style — so removing that vocabulary effect **enlarged**
the gap. **Reporting the raw number would have understated the result**, and I would not have known
which way without building the baseline.

## Controls

| control | result |
|---|---|
| **INSTRUMENT (positive)** | a hand-written paraphrase pair scores **0.625** — the measure can see repetition |
| **INSTRUMENT (negative)** | an unrelated pair scores **0.000** |
| **INSTRUMENT (self)** | a criterion against itself scores **exactly 1.000** |
| **SHAM** | same prompt, same annotators, size-matched, no selection step |
| **NOISE FLOOR** | cluster bootstrap over prompts, 2,000 draws × 3 seeds |
| **POPULATION** | 986 of 986 prompts usable — **0 excluded** |

The instrument controls run **before** anything touches the corpus, and a failure exits 2.

## ⚠ Proxy ledger — the measure is sound in one direction only

| | |
|---|---|
| **property** | criteria do not repeat the same idea |
| **proxy** | Jaccard over content words |
| **implication** | high overlap ⇒ repetition. **Low overlap does NOT ⇒ distinctness** |
| **safe side** | a negative DiD is evidence of removal; **a null would NOT have been evidence of redundancy** |

Two criteria can repeat an idea in disjoint words and this measure cannot see it. ⭐ **The measure is
deliberately model-free** so the result cannot be an artefact of a judge — which is what R989's
sibling finding about instrument-dependence makes worth paying for. The lexical bound is the price.

## What this adds to the definition

R988 established the card names `non-redundant` as constitutive and the definition has **no clause**
for it. This shows the property is **real and measurable** in the published text — so the missing
clause is a genuine gap, not a criterion that would be unenforceable anyway.

## Alternatives considered

**Use an embedding model for semantic similarity.** Refused *for this round*: ten of eleven claims in
this project's history turned out to be a local model's opinion stated as fact about a dataset, and a
model-free result that resolves is worth more than a model-dependent one that resolves further. A
semantic instrument is the honest next step, and it must carry its own gauge bound.

**Report the raw −0.0063.** Refused: it is the uncorrected number, and the correction moves it in the
direction that matters. Reporting the smaller figure would have been conservative in appearance and
wrong in fact.
