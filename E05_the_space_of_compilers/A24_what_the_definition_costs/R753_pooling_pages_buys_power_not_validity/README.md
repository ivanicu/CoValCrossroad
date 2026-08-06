# R753 · the three deliverables are NOT one population — and the ungated one is 4.5× worse

**Flagged rates: `STATEMENT.md` **0.1793** · `DEFINITION.md` **0.3814** · `FORMULATION.md` **0.8000**.
All three pairwise differences clear the MDE, and the largest (**0.6207**) is **6.7×** the
within-document floor the SHAM measured (**0.0933**). **Pooling them to reach R752's sample size would
manufacture power without validity — which is worse than being under-powered, because the number would
look answerable. ⛔ And it would not even work: 427 pooled figures is 0.50 of ONE arm.**

## check #355 — the question asked was division, so the round asked the one underneath it

R752 left a requirement of **846 figures per arm** and asked how many pages would reach it.

⛔ **That is division, and answering only it would be the arithmetic trap.** The count settles itself:

| document | figures | lines | flagged | **rate** | median cited era |
|---|---|---|---|---|---|
| `STATEMENT.md` | 184 | 68 | 33 | **0.1793** | R607 |
| `DEFINITION.md` | 118 | 67 | 45 | **0.3814** | R439 |
| **`FORMULATION.md`** | 125 | 57 | **100** | **0.8000** | R256 |
| **pooled** | **427** | | 178 | 0.4169 | |

**427 / 846 = 0.50 of one arm.** At this density, **12 documents** of average size would be needed.

**The question worth asking is whether pooling is legitimate at all** — §1's G1: *asking for power on
an unidentified quantity is how a well-powered-looking round gets built.*

## the pairwise comparison, with the MDE computed before it was interpreted

| pair | diff | MDE (figures) | MDE (lines, conservative) | verdict |
|---|---|---|---|---|
| STATEMENT vs DEFINITION | 0.2020 | 0.1629 | 0.2378 | **DIFFERENT** |
| **STATEMENT vs FORMULATION** | **0.6207** | 0.1601 | 0.2481 | **DIFFERENT** |
| DEFINITION vs FORMULATION | 0.4186 | 0.1773 | 0.2489 | **DIFFERENT** |

⛔ Three rates on ~120–180 items **will** differ by something under perfect exchangeability. **The
spread is not evidence unless it clears the MDE** — and here the largest clears even the conservative
line-based MDE by 2.5×.

## ⭐ the SHAM is what makes the comparison readable

**Ingredient absent** = *being a different document*. Splitting `STATEMENT.md` in half by line gives
two halves that are **exchangeable by construction**: rates **0.1429** vs **0.2361**, difference
**0.0933**. That is the floor any between-document difference must clear. The largest observed is
**0.6207** — **6.7×** it.

## ⚠ the confound is live, was written before the run, and is NOT resolved

Median cited era: **R607 / R439 / R256**. **The ungated document is also the oldest.** Governance and
era are **confounded in this design**, and it cannot separate them. The directional fires —
`FORMULATION.md`, which R598 measured as flipping **0 of 28** gates, has **4.5×** STATEMENT's flagged
rate — but **"being ungated caused it" is not established**, and the era column is printed beside the
rate rather than absorbed into it *(ledger 1029)*.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | the monotone ladder `0.0529 → 0.2955 → 0.8026 → 0.9999`. Band computed: floor **0.0529**, ceiling **0.9999**. Asserting the searched MDE rejects at 0.80 would be circular; the **order** is not |
| **g=0** | zero planted difference rejects at **0.0532 ≈ α** |
| **NEGATIVE** | document labels shuffled across figures: spread collapses **0.6207 → 0.0482**. The rates are a property of the documents, not of the partition |
| **SHAM** | two halves of one document, **0.0933** — the exchangeability floor |
| **PLACEBO** | each rate computed twice differs by exactly **0** |

⭐ **And the formula was honest this time** — analytic MDE **0.1601**, empirical **0.1620**, ratio
**1.01×**. In R752 the same approximation was **1.37×** too generous. **The difference is expected
count**: R752's smaller arm expected under 2 events, this one expects ~52. *The approximation fails
where the counts are thin and holds where they are not* — which is why R752's repair was needed there
and not here.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 flagged rate, STATEMENT | 0.18, band [0.05, 0.40] | **0.1793** | ✓ |
| **P2** flagged rate, FORMULATION | 0.30, band [0.00, 0.80] | **0.8000** | ⛔ **at the ceiling — badly wrong** |
| **P3** max pairwise difference | 0.12, band [0.00, 0.60] | **0.6207** | ⛔ **outside the band** |
| P4 analytic MDE | 0.125, band [0.05, 0.30] | **0.1601** | ✓ |
| P5 simulated rejection at that MDE | 0.75, band [0.60, 0.90] | **0.7955** | ✓ |
| D the ungated document is worse | true | **true** | ✓ |

**I under-predicted the disagreement by 5×.** I expected three pages of one project to be roughly one
population; two of the three registered points failed in that direction.

## the sentence I can no longer write

*"the repository's deliverables are one corpus, so pooling them raises n."* They differ in flagged rate
by up to 62 points, against an exchangeability floor of 9.

## NEXT

`FORMULATION.md` carries **100 flagged figures of 125** — the largest single block of unsupported
numbers in this repository, in the one document no gate reads. Whether that is a governance
consequence or an era artifact is confounded here, and the way to separate them is available: the
flagged rate can be computed **per cited era** within each document, so a document's old citations and
its new ones are compared against each other rather than across documents. If STATEMENT's oldest
citations flag at FORMULATION's rate, era explains it and governance does not; if they do not, the
governance reading survives its strongest confound. The unit becomes the (document, era) cell, and the
MDE must be recomputed because those cells are smaller than the documents.
