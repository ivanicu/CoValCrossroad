# R409 — the ordering carries information; the extremes are separable and the middle is not

**The decision this makes safe:** *is R408's NEXT worth its compute?* **Yes — but the verdict cleared
its own threshold by 1.7 points, and "`coval_core` is best" is a coin flip.**

## Result — `W_ORDER_REAL`. Three controls pass. **No GPU.**

### Rank matrix, B = 2,000 resamples (uniform would be 0.20 everywhere)

| arm | e | r1 | r2 | r3 | r4 | r5 |
|---|---:|---:|---:|---:|---:|---:|
| **`coval_core`** | +0.009002 | **0.53** | 0.24 | 0.14 | 0.07 | 0.02 |
| `topw_k6` | +0.008183 | 0.32 | 0.38 | 0.21 | 0.08 | 0.01 |
| `topw_k4` | +0.006705 | 0.11 | 0.25 | 0.33 | 0.26 | 0.05 |
| `topw_k8` | +0.004810 | 0.02 | 0.09 | 0.20 | 0.30 | 0.39 |
| `topw_k3` | +0.004114 | 0.02 | 0.04 | 0.12 | 0.29 | **0.53** |

**`P(rank 1)` for `coval_core` across seeds 1/2/3: `0.532 · 0.517 · 0.527`** — spread **0.015**.

## ⚠ The verdict cleared its pre-registered threshold by 1.7 points

The kill said `≥ 0.50 → W-ORDER-REAL`. It came in at **0.517–0.532**. **Had the threshold been 0.55
this would have read PARTIAL.** That is stated here rather than left for a reader to notice, because
a 3%-margin pass reported as a clean verdict is how a threshold becomes a narrative.

## ⭐ And the rank matrix says more than the verdict does

- **There is genuine information**: 0.53 against a 0.20 coin, and `topw_k3` sits last in **53%** of
  resamples. The ordering is not noise.
- **But no pairwise ordering is settled.** `coval_core` and `topw_k6` trade rank 1 at roughly 0.53 vs
  0.32 — *"the released core is the best label-free arm"* is barely better than a coin flip against
  its nearest rival.
- **The extremes are separable; the middle is a smear.** `topw_k4` and `topw_k8` spread across ranks
  2–5 with no mode above 0.33.

> **The honest summary is a partial order, not a ranking**: `{coval_core, topw_k6}` above
> `{topw_k8, topw_k3}`, with `topw_k4` unplaced.

## ⛔ Why this round exists at all

**R408's NEXT was a claim with no control** — the one sentence in a round that never gets one. It
proposed testing the ordering across judge and metric. **That presupposes the ordering is
distinguishable from noise on the data that produced it**, and with five effects spanning
`+0.0041…+0.0090` at `se ≈ 0.0037`, **the pairwise gaps are one arm's uncertainty wide.** Spending a
judge sweep first would have priced a question whose premise was untested.

## Controls

| | returned |
|---|---|
| **REPRODUCE** | all six point effects match R408's committed values to 6 decimals — `PASS`. No bootstrap is believed before the points reproduce |
| **SEPARATION (+)** ⭐ | `oracle_k4` (~8× the largest label-free effect) ranks above all five in **100.0%** of resamples — `PASS`. **Without it, a uniform result could not be told from a blind bootstrap** |
| **DUPLICATE (−)** | two identical objects split their wins **0.480 / 0.520** — `PASS`. Two identical things *must* be indistinguishable, or the resampler is not paired |
| **PAIRED** | resampling is over **prompts**, applied identically to every arm, so all arms see the same resampled set in each draw |
| **SEEDS** | 3 seeds, verdicts agreeing, spread **0.015** printed rather than averaged away |

## Register

| criterion | status |
|---|---|
| **cross-judge stability** | **STRUCTURALLY UNAVAILABLE** — at 0.8B nothing is admitted at any safe reference (R358/R359), so a second judge cannot host this comparison at all. R408's NEXT stays open and is now known to be *partly* unanswerable |
| **cross-metric stability** | **N/A here** — needs a different committed `sat_*` set |
| **a second release** | **N/A** — and it is the limit that matters most for `+0.004` effects |

## The sentence I can no longer write

> *"the five arms are ordered 0.87 > 0.81 > 0.62 > 0.46 > 0.38"* — **as though that were five facts.**
> It is roughly two: a top pair and a bottom pair, with one arm floating between them.

Artifact: `results/r409_ordering.json`, source-stamped.
