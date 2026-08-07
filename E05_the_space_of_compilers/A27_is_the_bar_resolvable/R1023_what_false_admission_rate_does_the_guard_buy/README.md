# R1023 — censoring is an intervention, so the guard's value can be **priced** instead of asserted

**The decision this round makes safe:** what coverage threshold clause ②′ needs. It is no longer a
habit — the false-admission rate is now a table, and any threshold can be read off it.

## What provoked it

R1022's NEXT. Its dose–response had **three** points, and they were the only three the release ships;
three points cannot separate monotone from step, and they confound coverage with **which arm**.
Censoring removes both: take a full-coverage arm, hide all but `k` prompts, impute exactly as the
committed loader does. The arm's true signal is held fixed **by construction**.

⭐ This is the one place in the arc where `causally identified` and `interventionally validated` are
**not** N/A: the confound is removed by intervention, not adjusted for.

## The arithmetic first — most of the phenomenon is forced

Imputing `968−k` cells with the observed mean leaves that mean **exactly** unchanged, so the point
estimate is unbiased at every `k`. But those cells become a **constant**, and the bootstrap reads a
constant as having **zero variance** — while it is really an *estimate*. So `lo` is dragged toward a
point estimate that is still as noisy as `k` prompts allow.

**"Imputation manufactures admission" is really "imputation collapses the interval around a
small-sample mean" — and that much is DERIVED, not measured.** What the algebra does not give is the
**rate**, which is what a threshold should have been chosen against and had never been computed.

## Result — **World B, the guard's value is too low.** ⛔ Kill fired.

**The exact null** (an arm against **itself**, censored — true Δ = 0 by construction, so every
admission is a false positive with no model involved). Nominal level **0.025**:

| null arm | target | k=4 | 10 | 25 | 50 | 100 | **200** | 400 | 800 | 968 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `generic` | `A2` | 0.507 | 0.433 | 0.377 | 0.363 | 0.280 | **0.190** | 0.080 | 0.040 | 0.000 |
| `generic` | `A1·consensus` | 0.447 | 0.363 | 0.370 | 0.267 | 0.213 | **0.173** | 0.157 | 0.043 | 0.000 |
| `genericpool16` | `A2` | 0.503 | 0.437 | 0.330 | 0.350 | 0.267 | **0.207** | 0.073 | 0.050 | 0.000 |
| `genericpool16` | `A1·consensus` | 0.440 | 0.377 | 0.350 | 0.237 | 0.240 | **0.210** | 0.150 | 0.040 | 0.000 |

**At the guard's own value of 200, an arm whose true difference is exactly zero is certified as
resolvably better ~21% of the time — 8× nominal.** Even at k=800 it is ~0.04, still above nominal.
Only uncensored is it 0.

## The mechanism predicts the curve — so this is not a coincidence

The bootstrap SE understates the true sampling SD by a ratio computable in closed form (`sd(v)`
cancels, so it depends on `k` and `n` alone):

| k | SD_true / SE_boot | predicted level | measured |
|---:|---:|---:|---:|
| 4 | 15.56 | 0.450 | 0.474 |
| 25 | 6.22 | 0.376 | 0.357 |
| 100 | 3.11 | 0.264 | 0.250 |
| **200** | **2.20** | **0.186** | **0.195** |
| 400 | 1.56 | 0.104 | 0.115 |
| 800 | 1.10 | 0.037 | 0.043 |

Worst |predicted − measured| over the 8 censored levels: **0.024**.
⚠ **This is a consistency check, not an independent confirmation** — both sides use the same normal
approximation. It rules out a coding artifact; it cannot rule out a shared model error.

## Verdict flip rate on arms whose uncensored verdict is committed

| arm | target | truth | k=4 | 50 | **200** | 800 | 968 |
|---|---|---|---:|---:|---:|---:|---:|
| `coval_core` | `A2` | admitted | 0.547 | 0.630 | **0.763** | 1.000 | 1.000 |
| `coval_core` | `A1·consensus` | excluded | 0.470 | 0.500 | **0.513** | 0.200 | 0.000 |
| `topw_k6` | `A2` | admitted | 0.517 | 0.563 | **0.690** | 0.987 | 1.000 |
| `topw_k6` | `A1·consensus` | admitted | 0.463 | 0.610 | **0.643** | 0.763 | 1.000 |

Censoring is **not** conservative in one direction: at k=200 a truly-admitted arm fails 24–31% of the
time **and** a truly-excluded arm is admitted 51% of the time. It destroys the verdict, both ways.

## Controls

- **POSITIVE** — at k=968 every verdict equals R1022's committed one, 4 of 4 cells: **PASS**.
- **g=0** — `generic` against itself uncensored must give `lo` exactly 0.0, never positive: **PASS**.
- **PLACEBO** — at k=968 the null difference vector is identically zero; rate exactly 0.000 in all
  four cells: **PASS**.
- **NEGATIVE** — the exact null *is* the measurement: true Δ = 0 by construction, two different null
  arms so the rate is not one arm's peculiarity.
- **NOISE FLOOR** — binomial SE at 300 draws, p=0.025: **±0.0090**. No rate read finer.
- **SEEDS** — 3 censoring seeds; worst per-seed spread over all null cells **0.150** (at small k,
  where the rate is ~0.45 and the spread is expected).

## What this settles

- ⭐ **Clause ②′'s operator is only calibrated on full-coverage arms.** On any partial-coverage arm it
  has no imputation-uncertainty correction, so its nominal 2.5% is not its actual level. This is a
  **scope statement the definition must carry**, not a defect of one round.
- ⭐ **The guard now has a price list.** A threshold can be read off the null curve. At the operator's
  own nominal level nothing below full coverage qualifies; at a relaxed 5% the curve reaches it only
  between k=800 and k=968.
- It **explains** R1011's withdrawal of the twins quantitatively rather than retracting anything new.

## Impossible here

**Construct validity** — whether `A2` or `A1·consensus` is the right target needs an external gold
standard the release does not carry. **N/A, not planned.** This prices the **operator** under each
target as given; it says nothing about which target is right.

`run.py` · `results/false_admission_rate.json`
