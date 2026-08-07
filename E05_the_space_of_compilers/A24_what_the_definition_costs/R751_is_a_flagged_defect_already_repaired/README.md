# R751 · `UNVERIFIED` — the annotation detector inverted its own SHAM, and the instrument is dead

**I set out to measure how much of a defect-flag's count is already repaired on the page. The
detector cannot answer it: figures that ARE supported carry annotation keywords at **0.5133**, while
flagged ones carry them at **0.3030** — the SHAM inverted. The preregistration named this as the most
informative way the round could fail, and it is the verdict: `UNVERIFIED`, and a keyword detector must
not be used to net repaired defects off a residue count.**

## check #353 — P4 stopped the fourth rebuild in this arc

R750 closed by proposing a corpus-wide search for its zero-support figures. **R591 already did it** —
355 rounds scanned for R590's four orphans, with a collision floor and a hit null, returning four
*different* verdicts: one truncated citation, one grounded-as-a-derived-difference, one where the
estimand was false, and `0.0200` **CONFIRMED UNGROUNDED**.

⛔ **And it exposed a defect in R750's report.** Of its two zero-support sentences, **one is the row
STATEMENT.md already annotates** — in the page's own words, `⁇ BOTH DECIMALS ARE UNGROUNDED (R591)`,
with the reason it is annotated rather than substituted. **R750 reported as actionable residue a
defect the page had already repaired.** The actionable residue was **1**, not 2 *(ledger 1022)*.

## the grid — 3 matchers × 3 windows, with the SHAM arm beside every cell

| matcher | window | flagged | annot | share | **SHAM share (supported)** |
|---|---|---|---|---|---|
| prefix | tight | 71 | 23 | 0.3239 | **0.4643** |
| prefix | loose | 71 | 27 | 0.3803 | **0.5357** |
| **rounded** | **tight** | **33** | **6** | **0.1818** | **0.4600** |
| rounded | medium | 33 | 8 | 0.2424 | 0.4667 |
| **rounded** | **loose** | **33** | **10** | **0.3030** | **0.5133** |
| tolerance | tight / loose | 33 | 6 / 10 | 0.1818 / 0.3030 | 0.4600 / 0.5133 |

⛔ `annotated ≤ flagged` and `loose ≥ tight` are **both FORCED**. The order is algebra; only the gaps
measure.

## ⛔ the SHAM did not merely match — it INVERTED

Annotation keywords are **more** common near **supported** figures than near unsupported ones, at
every window and every matcher. **Annotation does not track groundedness**, so the precision question
this round asked is unanswerable with this detector.

## where the failure lives — the confound control, run on BOTH arms

I built the keyword breakdown to diagnose exactly this and had run it on one arm only. On both:

| keyword | flagged | supported | |
|---|---|---|---|
| **`ungrounded`** | **0.0606** | 0.0400 | flagged **1.5×** higher |
| **`corrected`** | **0.0606** | 0.0200 | flagged **3.0×** higher |
| `retracted` | 0.1515 | **0.2867** | supported higher |
| `unverified` | 0.1818 | **0.4400** | supported higher |

**The two keywords that mean *this figure has no source* point the right way. The two that dominate
the aggregate are scope-and-verdict language and point the other way**, and they are what inverted the
pooled SHAM. A keyword detector cannot separate *"this number is ungrounded"* from *"this claim's
scope is unverified"* — they are the same string to it.

⚠ **AND I AM NOT REPORTING THE RESTRICTED DETECTOR'S NUMBER.** Selecting `ungrounded|corrected`
*after seeing which subset points my way* is choosing the specification from the result. It is a
**hypothesis for a later round with its own preregistration**, not a finding here *(ledger 1024)*.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 flagged figures, rounded | 10, band [3, 40] | **33** | in band, point wrong |
| P2 share annotated, tight | 0.10, band **[0.00, 1.00]** | 0.1818 | ⛔ **the band cannot fail** *(ledger 1023)* |
| P3 share annotated, loose | 0.40, band **[0.00, 1.00]** | 0.3030 | ⛔ same |
| P4 the known case found loose, missed tight | yes *(hard)* | **yes** | ✓ |
| P5 flagged figures citing an R591-adjudicated round | 2, band [0, 10] | **10** | at the ceiling, point badly wrong |
| D annotation share rises with window | true | **true** (0.1818 → 0.2424 → 0.3030) | ✓ |

⛔ **P2 and P3 were registered with bands of `[0.00, 1.00]`, which no measurement can fall outside.**
That is §4's *check that cannot fail*, in my own preregistration, in a round whose subject is
instruments that cannot fail.

## controls — 4 PASS, 1 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `0.0200` on line 610: **missed** at the tight window, **found** at loose (`ungrounded`). Band computed: never-annotating floor 0, ceiling 1. **A detector that found it at every window would not be measuring the window** |
| **g=0** | **23** flagged figures carry no keyword at any window — the detector does not annotate everything |
| **NEGATIVE** | windows detached (each figure given another line's context): **0.2424 vs 0.3030** — the share drops |
| **PLACEBO** | scored twice → **0** differing, 0 of 33 |
| **SHAM** | ⛔ **FAIL, and inverted**: supported **0.5133** vs flagged **0.3030** |
| **UNIT** | **17 of 33** flagged figures share a line with another; annotation is resolved per **figure** and the sharing is printed |

## the sentence I can no longer write

*"the page annotates its ungrounded figures, so a residue count can be netted against annotations."*
The detector that would net them is more likely to fire on a **supported** figure.

## NEXT

The pooled detector is dead and the restricted one is a hypothesis, so the next round must
**preregister the restricted detector before looking at it again** — `ungrounded|corrected` only,
with the same SHAM, and a kill that fires if the restricted share still does not exceed its supported
arm. That is a different round from this one because the specification is now fixed in advance rather
than chosen from a breakdown. The quantity to register is the restricted share on flagged versus
supported figures at the loose window, and the honest prior is that it will separate weakly: the two
keywords together fire on **4 of 33** flagged figures, so the design is thin and its MDE should be
computed before the run rather than discovered after it.
