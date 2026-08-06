# R750 · a citation group typically has ONE member that holds the number

**Median support depth is **1** across the 17 multi-cited numeric sentences: when the page cites
several rounds for a figure, usually exactly one of them has that figure in its artifact. **7 of 17**
groups do have ≥2 supporters and **2 have none**. So R749's row-8 failure is not one bad row — it is
the typical shape. ⭐ And the SHAM makes the number readable: single-citation sentences are supported
**78.4%** of the time, so the artifacts *do* store printed values and a low group depth is not an
artifact of the store.**

## check #352 — the severity check came first, and it changed the round

R749's NEXT asked about multi-citation **object-count** sentences. There is exactly **1** of those.
**A round with n = 1 is not a measurement**, so before writing any code I counted the population one
level up: **1,389 sentences · 65 citing ≥2 rounds · 17 of those carrying a number**, group sizes
2, 3, 4, 5, 8. That is measurable; the object-count-only version was not, and saying so is the point.

## ⚠ R590's repair reused, not rediscovered

R590 asked whether *a* cited round holds a number and found 15 of 19. Its **first** matcher required
the printed value to be a **prefix** of a stored float, so every value the document rounded **up**
failed — 13 orphans of which **9 were its own bug**. R590 has no `run.py` (a codeless round), so the
relation is re-implemented **with the repair carried forward**, and the prefix rule is kept only as
the loose end of the curve, to price it.

## the grid — 3 matchers × 2 populations

| matcher | population | n | median | share ≥2 | share = 0 |
|---|---|---|---|---|---|
| prefix *(R590's broken rule)* | multi-cited | 17 | 1.0 | 0.4118 | **0.2353** |
| prefix | single-cited *(SHAM)* | 37 | 1.0 | — | 0.4595 |
| **rounded** *(its repair)* | **multi-cited** | **17** | **1.0** | **0.4118** | **0.1176** |
| **rounded** | **single-cited (SHAM)** | **37** | **1.0** | — | **0.2162** |
| tolerance | multi-cited | 17 | 1.0 | 0.4706 | 0.1176 |
| tolerance | single-cited *(SHAM)* | 37 | 1.0 | — | 0.2162 |

⛔ `support ≤ group size` **ALWAYS** — only the distribution is a measurement.
⛔ **The SHAM's `share ≥2` is STRUCTURALLY 0** — a single-citation sentence cannot have support 2.
Its informative column is `share = 0`, and the table prints `—` rather than a misleading zero.

⭐ **The broken prefix rule manufactures 2 extra orphans on this page** (4 vs 2) — R590's own bug,
re-measured on a different population and still live.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 median support, rounded | 1, band [0, 3] | **1** | ✓ exact |
| P2 share with support ≥2 | 0.35 | **0.4118** | ✓ |
| P3 SHAM base rate | 0.79 ⚠ **prior-art informed** from R590's 15/19 = 0.789, declared | **0.7838** | ✓ — and **not scored as a blind hit** |
| P4 groups with support 0 | 2 | **2 of 17** | ✓ exact |
| P5 orphans the broken rule manufactures | ≥ 1 | **2** | ✓ |
| D support does not grow with group size | true | **true** on usable sizes | ✓ |

⚠ **The directional is computed on sizes with n ≥ 3 only.** Sizes 4 and 8 carry **one sentence each**
and show mean support 4.00 — **a mean over n = 1 is not a trend**, so they are excluded from the test
and kept in the table *(ledger 1020)*.

| group size | n | mean support |
|---|---|---|
| 2 | 12 | 1.17 |
| 3 | 3 | 1.33 |
| 4 | **1** | 4.00 ⚠ one sentence |
| 8 | **1** | 4.00 ⚠ one sentence |

## ⛔ my NEGATIVE control was mathematically incapable of firing

v1 rotated the citation group **within** a sentence and reported **0/17 changed**. Of course it did:
`support` **sums over every member**, so rotating permutes a set being summed and the count is
invariant **by construction**. The control could never exclude the world it named — §4's
*control-that-cannot-PASS* in its mirror form *(ledger 1019)*.

⭐ **And the same operation was a valid control one round earlier.** R749's resolver reads exactly
**one** citation, so order is load-bearing there and inert here. **A control must be re-derived per
design, not carried across.**

**Repaired:** each sentence is given **another sentence's** citation group — destroying the
sentence↔group pairing while preserving everything else. **10 of 17 supports change. PASS.**

## controls — 4 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `0.0316`, found by **direct search** in both R294's and R426's artifacts — not by the matcher — scored **2**. Band computed: never-matching floor **0**, group size **2** |
| **g=0** | `987654.321`, in no artifact → support **0**, **reported not skipped**. A skipped zero would have raised the median by deleting the worst cases |
| **NEGATIVE** | cross-sentence group reassignment → **10/17** change |
| **PLACEBO** | scored twice → **0** differing, stated as 0 of 17 |
| **SHAM** | ingredient **absent**: single-citation sentences, **78.4%** supported |
| **UNIT** | **7 of 17** sentences state more than one number; support is per **number**, the sentence value is the **maximum**, printed rather than averaged away |

## ⚠ the confound was written before the run and does not rescue the result

*"The number may live in the README rather than the artifact."* Measured against the READMEs:
**median 1.0, share ≥2 = 0.4118** — identical to the artifact figures. **Reported beside, never
merged.**

## the sentence I can no longer write

*"the row cites three rounds, so it is well grounded."* Typically one of them holds the number, and
in 2 of 17 groups none does.

## NEXT

The 2 zero-support groups are the actionable residue and they are a different defect from the
single-support ones: a figure no cited round holds is either mis-transcribed, computed by a round the
sentence does not cite, or never persisted. Those three causes need different repairs and this round
cannot distinguish them, because it only ever asked whether the CITED rounds hold the value. Search
the whole artifact corpus for each of the 2 values and report which rounds do hold them — if some
round does, the citation is wrong and fixable; if no round does, the figure is unsupported by anything
on disk and must be withdrawn or recomputed. The unit is the value rather than the sentence, the
population is the committed artifact corpus rather than the cited subset, and the outcome names a
repair per figure rather than a rate.
