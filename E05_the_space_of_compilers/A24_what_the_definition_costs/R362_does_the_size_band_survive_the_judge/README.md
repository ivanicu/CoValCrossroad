# R362 — the size band's premise fails at the second judge, not merely its boundaries

**The decision this makes safe:** *may `DEFINITION.md` state the size band unindexed?* **No.** At
0.8B the rubric's top-k does not beat a size-matched blind reference at **any** k — so there is no
band there to have boundaries.

## Result — `W_PARTIAL_OVERLAP`. All controls PASS. Two runs byte-identical.

The size claim was the last quantitative statement in the definition whose supporting round predates
the judge axis entirely.

| step | @ 2B | @ 0.8B |
|---|---|---|
| 1→2 | **RESOLVED** +0.0241 | unresolved +0.0062 |
| 2→3 | **RESOLVED** +0.0108 | unresolved +0.0091 |
| 3→4 | unresolved −0.0042 | **RESOLVED** −0.0143 |
| 4→6 | unresolved | unresolved |
| 6→8 | unresolved | unresolved |
| 8→12 | **RESOLVED** −0.0192 | **RESOLVED** −0.0212 |

**Only the EXIT (8→12) survives both judges.** Both entry boundaries collapse, and 0.8B resolves an
interior step (3→4) that 2B does not. **Neither *collapse* nor *moves* describes this**, which is
why the round carried a fourth branch — added because this session repeatedly had a default branch
assert past its data. It fired.

## ⛔ And the absolute value in my own "is it forced?" line hid the finding

| | |
|---|---:|
| median margin ratio 0.8B / 2B | **−0.343** |
| R301's fitted clause-② shrink β | **+0.401** |
| median MDE ratio | +1.186 |

A pure shrink gives a ratio near β and **positive**. The observed median is **negative**: at **4 of 7
sizes the margin changes sign between judges** (k = 2, 4, 6, 8).

> **This is not attenuation.** At 0.8B the margins are negative at **6 of 7** sizes and resolvably so
> at k=12. The rubric's top-k does not merely beat the blind reference *by less* — it mostly **stops
> beating it**.

My printed test compared `|margin ratio|` to the MDE ratio and concluded *"the shrink alone predicts
collapse."* True as arithmetic, **and it described the wrong phenomenon** — an absolute value that
erased a sign inversion. The sign is the result.

## What was NOT asked, because it is settled

Two parts of the size question would have been demonstrations, and the round declines them by name:

- **The upper bound is a derivation with no judge in it.** R224/R228 give
  `k_max(n,m) = max{k : C(n,k) ≤ a(m)}` — pure combinatorics on criteria-per-prompt and
  responses-per-prompt. Recomputing it at a second judge is **forced** to return the same answer.
- **The curve's shape is already measured.** R356 computed the between-judge rank correlation
  *within* the `topw_k` family — which **is** this k-curve — at **ρ = +0.667**, inside its own
  forced band. Re-deriving it would be R356 under a new name.

## Controls

| | @ 2B | @ 0.8B |
|---|---|---|
| **POSITIVE** — centred cell + dose, fraction resolved | 0.00 · 0.14 · **1.00** · 1.00 | 0.00 · 0.29 · **1.00** · 1.00 |
| — floor / ceiling / monotone | 0.00 / 1.00 / **True** | 0.00 / 1.00 / **True** |
| **g=0** — an arm against itself: margin 0, not resolved | PASS | PASS |
| **PLACEBO** — that self-contrast has zero spread | PASS | PASS |
| noise floor | each cell's **own** paired sd, never pooled (R331) | |
| multiplicity | 2 judges × 7 k margins + 6 steps = **26** cells, all printed | |
| reproducibility | two runs **byte-identical** (`210e68559065`) | |

### ⛔ The positive control could not pass in v1 — the fourth of that shape this session

v1 added `+2·MDE` to each cell's **raw** difference vector. But `k=1` sits at **−1.26 MDE**, so
+2 MDE lands it at +0.74 — **unresolvable no matter how good the instrument is.** The threshold was
above what the design can return for that cell, so its FAIL said nothing about the detector.

Fixed the standard way: **centre the difference vector first** so every cell starts at a true effect
of exactly 0, then dose. That gives a real floor (g=0 → 0.00) and a real ceiling (g=4 → 1.00), with
monotonicity between.

## Register

| criterion | status |
|---|---|
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) — no third checkpoint locally |
| **the upper bound at another judge** | **NOT A QUESTION** — it is combinatorial |
| **the curve's shape** | **already measured** (R356), not re-run |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"Its size is greater than one; sizes 3 to 8 are not distinguishable by this release."*

**At 2B the band is 3–8 with a resolved entry and exit. At 0.8B there is no band: top-k loses to a
size-matched blind set at 6 of 7 sizes.**

Artifact: `results/r362_size_band.json`, source-stamped.
