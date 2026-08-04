# R372 — the resolving set is not a quantity, and R371 committed the error it convicted R370 of

**The decision this makes safe:** *should the S-curve be reported at all?* **No.** Neither R370's
single cell nor R371's swept curve survives resampling. The object they both read is not stable
enough to be read.

## Result — `W_REAL_BUT_DIFFERENT_SET_UNSTABLE_TOP_IS_DF_ARTIFACT`. Five controls PASS. Two runs byte-identical. **No GPU spent.**

R371 found R370's transport verdict moves with the number of difficulty strata S, and closed with an
`[UNTESTED]` prediction that the curve would stabilise. This is that test: re-run the whole sweep on
**480 random halves** of the 250 prompts and ask whether the resolving set recurs.

| what R371 claimed | measured over 480 halves |
|---|---:|
| the resolving set on `exact` is `{2, 5}` | occurs in **2.9%** of halves |
| — | modal outcome is **∅** at **41.5%**; **38** distinct sets appear |
| the S=5-resolves-while-3,4-do-not signature | **4.8%** |
| two halves of one split agree on the set | **4.4%** *(after removing both-empty agreements)* |

**Raw set-match is 18.3%, but 14.6 points of that is both halves resolving NOTHING.** Agreement on
the empty set is agreement about nothing, and the conditional column is the one that carries
information.

## ⛔ Three separate reasons the curve cannot be read, and I built the third one

**① The marginal `p(S)` separation is a DERIVATION, and it was my own pre-registered statistic.**
R371 measured that the MDE **rises** with S while the contrast does not. A rising threshold against
a flat effect makes `p(S)` fall with S **by algebra**. So `var_true = +0.01965 > 0` restates R371's
finding and is not evidence about which stratum count is right. **The pre-registered kill is reported
as written** — moving a pre-registration after seeing the data is the thing pre-registration exists
to prevent — but the sentence it licenses is weaker than its label.

**② S = 2 tops every ranking because its denominator collapses, not because it has power.** The
between-stratum sd at S strata has **S−1 degrees of freedom**, so at S=2 it has **one**, and its
distribution has heavy mass near zero.

| S | 2 | 3 | 4 | 5 | 6 | 8 |
|---|---:|---:|---:|---:|---:|---:|
| P(MDE < half the typical contrast) | **28.3%** | 7.3% | 2.9% | 0.4% | 0.4% | 0.2% |
| p(S) | 0.483 | 0.277 | 0.235 | 0.183 | 0.115 | 0.096 |

**3.9× the next-worst cell.** The tell was in the run itself: the full-sample `pair|2` cell returned
**MDE = 0.0007**, which no real design achieves. *What orders the cells is df, not difficulty.*

**③ The set does not survive repairing R371's own floor.** With the order-independent floor, at full
n, `exact` resolves at **S = 2, 3, 5** — not `{2, 5}`.

## ⛔ A defect in R371, found while porting its code

R371's `floor_mean(ps, arm, seed, metric)` creates **one rng per call** and walks the prompt list in
order, so **a prompt's floor depends on which other prompts are in the list and in what order.**
Invisible at fixed population — R371 only ever called it on fixed strata — but this round subsets the
population 480 times.

**Measured, not asserted:** 12 permutations of the prompt order move the `exact|S=4` contrast from
**+0.0540 to +0.1185**, sd **0.0178**, against a published **+0.0810**. R372 seeds each draw from
`(pid, arm, seed)` so a prompt's floor is invariant to its company.

## Controls

| | returned |
|---|---|
| **REPRODUCTION** ⭐ | the per-prompt floor reproduces all 12 published cells within max(3× that cell's own floor-seed sd, 0.02); max delta **0.0313**. Tolerance **argued** — it is the floor's own seed-to-seed spread, computed here, not a number picked |
| **ORDER** | R371's shared stream, quantified above |
| **PLACEBO** | orig against itself — contrast 0 by algebra — **0 / 120** halves "resolved" |
| **POSITIVE (a)** | detector: p(S=6) **0.233 → 1.000** at g=0.30, var_true **+0.008 → +0.095**; scope stated — validates the p-spread detector, **not** the contrast pipeline |
| **POSITIVE (b)** | data-level: hardest quintile bumped 0.35 → max \|Δp(S)\| = **0.200**; both arms' full p(S) printed |
| **RANGE** | p spans 0.002…0.485 — not pinned at 0 or 1, so the spread statistic is admissible |
| reproducibility | two runs **byte-identical** (`21cba6034062`), stdout identical |

⚠ `hash()` was **not** used to seed the per-prompt draw: Python randomises string hashing per
process, and a run.py using it is irreproducible across invocations. Caught before the first run.

## Grid

6 values of S × 2 metrics × 2 edge specifications = **24 cells**, all printed, survivors and not.
**4 of 4** specifications "separate" — and all four separate for the derived reason in ① above.

## ⭐ The ontology shift

> **`The resolving set` is not a well-defined object of this design.** It is empty in 41.5% of
> halves, takes 38 distinct values, agrees with itself across a split 4.4% of the time, its top cell
> is a df artifact, and its marginal shape is a derivation.

R371 asked *"is the set stable?"*. The answer is that **the set is not a quantity.** R371 was right
that R370's S=4 was a specification choice — and then read a SET off the same single draw, which is
**the error it convicted R370 of, committed one level up, in the same round.**

## Register

| criterion | status |
|---|---|
| **p(S) at n=968 or n=250** | **N/A** — the full sample gives ONE draw per S, which is exactly why R371 could not tell a feature from a coin flip. Every statement about other n is an **extrapolation** and labelled one |
| **whether any S-dependence is about DIFFICULTY** | **N/A** — nothing isolates difficulty from what co-varies with the stratifier. Unchanged from R371 |
| **human rankings** | **N/A** — the fresh responses carry none; every number is agreement with the **full rubric**. Unchanged since R233 |
| **a second judge** | **N/A** — pool labels are 2B only |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"the `exact` contrast resolves at S = 2 and S = 5, so the honest statement is the curve."*

**The curve is a derivation, its top cell is a 1-df artifact, and its set recurs in 2.9% of halves.
Neither the cell nor the curve is reportable — and the 718-prompt job cannot fix an object that does
not survive resampling at the n it already has.**

Artifact: `results/r372_stability.json`, source-stamped.
