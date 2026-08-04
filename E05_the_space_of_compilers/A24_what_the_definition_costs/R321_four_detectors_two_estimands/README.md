# R321 — four detectors, two estimands, and a bias that explains a third of the gap

**Decision this makes safe:** how the deliverable may present the four MDE brackets. **Not as four
opinions about the site — but not as one quantity at four precisions either.**

## First: they are not the same estimand, and that is readable from the code

| rounds | rule | its width is |
|---|---|---|
| R267 / R268 / R269 | `hi = min(g : curve[g] ≥ 0.8)`, `lo = max(below < hi)` | the **dose step** |
| R274 | `lo = min(g : CI_upper ≥ 0.8)`, `hi = min(g : CI_lower ≥ 0.8)` | the **binomial CI** |

A grid bracket around the first observed crossing, versus a confidence interval for where the
crossing is. **Applying R267's rule to R274's own 400-replicate curve gives `[0.110, 0.115]`, which
R274's `[0.105, 0.125]` contains.** On identical data the two rules agree — the headline
"disagreement" was never between the detectors' answers.

## Second: the same rule at three replicate counts

`0.090` (40 reps) → `0.100` (100) → `0.115` (400). Monotone. `min(g : observed ≥ 0.8)` is a
**minimum over a noisy sequence**, and a minimum over noise is biased low.

Resampling R274's curve at each replicate count, 2000 draws, 2 seeds:

| reps | E[MDE_hat] | median | 95% range | arc produced | gap |
|---:|---:|---:|---|---:|---:|
| 40 | 0.1077 | 0.1100 | [0.090, 0.125] | 0.0900 | **+0.0177** |
| 100 | 0.1124 | 0.1150 | [0.105, 0.125] | 0.1000 | **+0.0124** |
| 400 | 0.1159 | 0.1150 | [0.105, 0.125] | 0.1150 | +0.0009 |

**W-PARTIAL.** The bias is real, monotone, and in the predicted direction — **and it is too small to
account for the arc's values.** It moves the estimate about `0.008` of a `0.025` gap. At 40 reps the
arc's 0.090 sits exactly at the bottom edge of the simulated range; at 100 reps its 0.100 sits
*below* the 2.5th percentile.

**The remainder is design difference, not precision** — and one is visible in the artifacts: R268
calibrates `τ = 0.416`, R274 `τ = 0.424`. Different thresholds on the same curve move the crossing.

## Controls

| control | result |
|---|---|
| **placebo** — reference scored against itself | 0.1150, exactly the arc's 400-rep value |
| **negative** — deterministic curve, no resampling | 0.115 at *every* rep count: the bias is not the machinery |
| **positive** — 400-rep simulation reproduces the reference | 0.1159 vs 0.1150 |
| **knob alive** — 40 vs 400 must differ | 0.0082 apart, so the replicate knob is not dead |
| **seeds** | second seed within 0.010 at every cell |

## ⚠ The scope limit that matters

R267's and R268's curves are **their own runs, not subsamples of R274's.** This shows the estimator
**can** produce their values at their replicate counts; it does not show it **did**. Matched re-runs
at equal replicate counts are GPU work through pueue, and are named here rather than described as
planned.

## What the deliverable may now say

Not *"four brackets, one split"* — that presented four comparable opinions. Not *"one quantity at
four precisions"* — the simulation refuses that too. **Two estimands; within the point-crossing
one, a demonstrated low-replicate downward bias explaining roughly a third of the spread; the
remainder unexplained and at least partly a different calibrated threshold.**

## Scope

R274's 41-dose curve at 400 replicates · first-crossing rule at 0.8 detection · binomial resampling
per dose · 3 replicate counts × 2000 draws × 2 seeds.
