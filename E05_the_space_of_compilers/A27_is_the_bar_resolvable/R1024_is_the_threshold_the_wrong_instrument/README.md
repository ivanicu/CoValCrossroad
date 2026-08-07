# R1024 — is a coverage **threshold** the right instrument at all, or was the **estimator** the defect?

**The decision this round makes safe:** whether the coverage guard should be tuned or deleted. It
should be **deleted** — the defect was the estimator, and the constant has no job left to do.

## Two things withdrawn before any compute

- **R1023's own NEXT is not realizable.** It proposed *"resample the censoring as well as the
  prompts"*. That requires the arm's **full vector**, which is exactly what a partially-covered arm
  does not have. ⚠ Second time in this arc that a closing line named an action the data cannot
  support — it is the one sentence with no control attached.
- **The estimand had to change, because R1023's null is degenerate under the fix.** On an arm against
  itself the observed-only difference vector is identically zero, so `lo = 0` and the false-admission
  rate is **forced** to 0 at every k. Reporting *"the fix attains 0.000"* would be 1+1=2.

**The realizable fix needs no new machinery: do not impute.** Bootstrap the `k` observed prompts and
nothing else — what R1021 did by hand when it restricted the core/twin comparison to 200 prompts.

## Estimand

`P(lo ≤ Δ_true)` — one-sided coverage of the operator's lower bound, `Δ_true` being the
arm-minus-comparator mean over **all 968** prompts. Nominal **0.975**. R1023's false-admission rate is
the special case `Δ_true = 0`.

## Result — **World A.** The observed-only estimator holds coverage at every k.

| pair (A2) | k=4 | 10 | 25 | 50 | 100 | 200 | 400 | 968 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **impute (committed)** `coval_core` vs `generic` | 0.563 | 0.557 | 0.653 | 0.687 | 0.783 | 0.857 | 0.933 | 1.000 |
| **observed-only (fix)** `coval_core` vs `generic` | 0.920 | 0.960 | 0.967 | 0.977 | 0.977 | 0.987 | 0.993 | 1.000 |
| **impute** `topw_k6` vs `genericpool16` | 0.533 | 0.580 | 0.637 | 0.650 | 0.780 | 0.863 | 0.920 | 1.000 |
| **observed-only** `topw_k6` vs `genericpool16` | 0.940 | 0.960 | 0.973 | 0.980 | 0.977 | 0.987 | 0.997 | 1.000 |

**Worst observed-only coverage across every real pair at k ≥ 10: 0.953.** Even at k=4 it is **0.920**.
The committed estimator, by contrast, is at **0.53–0.69** exactly where the guard admits arms.

⭐ **The defect was the ESTIMATOR, not the sample size.** A minimum-k threshold is answering a
question that only exists because of the imputation.

⚠ **The fix is conservative, not exact** — coverage sits at 0.95–1.00 against a nominal 0.975, i.e.
slightly **over**-covering at large k. That costs power; it never costs correctness. The committed
estimator errs in the other, unforgivable direction.

## Diagnostic — how far the bound misses (same draws)

| estimator | `P(lo ≤ Δ−0.5)` | `P(lo ≤ Δ+0.5)` |
|---|---:|---:|
| impute (committed) | 0.000 | **0.973** |
| observed-only (fix) | 0.290 | **1.000** |

Read together: **the impute bound is biased high and too narrow** — it never lands far below the
truth, and 2.7% of the time it sits *above* truth+0.5. **The observed-only bound is honest but wide
at k=4**, which is the correct behaviour for four data points.

## Controls

- **POSITIVE** — the impute estimator must reproduce R1023's committed false-admission curve on the
  exact null. Worst Δ **0.020** against 4×SE = 0.092: **PASS** (4 cells).
- **ADEQUACY** — at k=968 neither estimator imputes, so their bounds must agree: worst |Δ| **0.0005**:
  **PASS**.
- **PLACEBO** — ⚠ **written wrong twice, the same way both times, and both printed FAIL with nothing
  wrong with the round.** v1 shifted the truth **up** 0.5 and demanded coverage ~1.000 everywhere
  (got 0.973). v2 shifted **down** and demanded ~0.000 (got 0.290). **Both expectations presuppose a
  calibrated estimator — and half the grid is the estimator whose miscalibration is the finding.**
  *A control whose expectation only holds when the thing under test is healthy cannot run while
  testing it.* Replaced with two estimator-independent checks over all **180** cells:
  - **(i) NESTING** — `lo ≤ Δ+δ` is nested in δ, so coverage is non-decreasing in δ. Pure arithmetic;
    fails only on an implementation bug (re-drawn seed, bad index). **0 violations.**
  - **(ii) RANGE** — scores ∈ [0,1] so |lo| ≤ 1; coverage must be **exactly** 0.000 at δ=−2 and
    **exactly** 1.000 at δ=+2. **0 violations.**
- **NEGATIVE** — the exact-null pair is carried through both estimators and printed to **show** its
  degeneracy under the fix, never used as evidence.
- **NOISE FLOOR** — binomial SE at 300 draws: **±0.0090**. No coverage read finer.
- **SEEDS** — 3 censoring seeds × 100 draws.

⚠ **k=4 is reported and never used in the verdict.** A bootstrap over 4 units is known-broken for
reasons that have nothing to do with this benchmark; letting it decide would be an instrument failure
read as a finding.

## What this settles, and what it does not touch

- ⭐ **The guard is deletable.** Replace `if isfinite(v).sum() < 200: return None` +
  `nan_to_num(..., nan=nanmean(...))` with a paired comparison on the observed prompts. Then no
  threshold is needed and the constant in 22 scripts should not exist.
- ✅ **No committed extension figure moves.** R1022's derivation already showed only 4 arms are
  partial (the two twins + the `promptecho` pair), `promptecho` is in no extension, and R1011 already
  withdrew the twins. The practical blast radius was closed before this round measured why.
- ❌ **Construct validity** — whether `A2` or `A1·consensus` is the right target still needs an
  external gold standard the release does not carry. **N/A, not planned.** This round is about the
  estimator only.

`run.py` · `results/estimator_vs_threshold.json`
