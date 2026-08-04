# R454 · R453's bound **saturates** in pool breadth — so it is not a pool-size artifact

**The decision this round makes safe:** whether the 59.6% within-family figure is a fact about clause
② or about the 16-criterion pool it was measured against. **Saturated by W≈12, so not pool-size
limited** — but *not* breadth-independent either. `W-CLAUSE`, with the shape stated.

## ⛔ The announced step was unrunnable — and it failed at IDENTIFICATION, before power

R453 closed proposing to rebuild the reference class from **a different prompt-blind family**, citing
`promptecho` and `generic`. Asking the objects rather than my memory:

| family | prompts | k min/mean/max | |
|---|---|---|---|
| `genericpool16` | 968 | 16/16.0/16 | prompt-**blind** |
| `full` | 968 | 4/15.5/39 | the **rubric** — prompt-specific |
| `provenance_probe` | **4** | 16/16/16 | population too small |

`promptecho` has **zero** hits in `corebench/*.py`, so its provenance cannot be established from the
source and I will not assert it is prompt-blind. **Exactly one prompt-blind family has breadth ≥ 16,
and no resampling makes a second.** *Twenty-second announced step checked, twelfth killed.*

**But the worry is runnable inside the pool**: if "within-family" is a fact about how *broad* the
family is, narrowing it must move the bound.

## Result — the breadth dose-response, every cell printed

| W | \|class\| | 1/C | floor | g0 | worst | **best** | core | **POS** |
|---|---|---|---|---|---|---|---|---|
| 6 | 15 | 0.0667 | 0.0987 | 0.1353 | 0.0013 | 0.3580 | 0.7620 | *0.3910* ⚠ granularity-limited |
| 8 | 70 | 0.0143 | 0.0845 | 0.0969 | 0.0009 | 0.3919 | 0.7647 | **0.4518** |
| 10 | 210 | 0.0048 | 0.1330 | 0.1444 | 0.0000 | 0.5391 | 0.8311 | **0.5817** |
| 12 | 495 | 0.0020 | 0.1178 | 0.1142 | 0.0001 | 0.5918 | 0.8318 | **0.6639** |
| 14 | 1001 | 0.0010 | 0.1114 | 0.1240 | 0.0000 | 0.5737 | 0.8457 | **0.6296** |
| 16 | 1820 | 0.0005 | 0.1284 | 0.1877 | 0.0000 | **0.5773** | 0.8368 | **0.6337** |

> **POS rises +0.1298 from W=8 to W=10, then plateaus — sd over W=12…16 is 0.0153.**

**R453's W=16 measurement sits in the saturated regime, so it is not limited by the pool's size —
more breadth would not move it.** What that does *not* license: that the fraction is
breadth-independent. **Below W≈12 it clearly is not.**

## Controls

| control | returned |
|---|---|
| **ANCHOR** — W=16 must reproduce R453 | **0.5773** vs committed **0.5773** ✅ *exact, independent path* |
| g=0 — objective destroyed, at every W≥8 | sits at each W's own **computed** floor ✅ |
| NEGATIVE — worst-on-train | below each floor at every W ✅ |
| FLOOR | computed per W, never reused from W=16 and never guessed |

## ⛔ My own granularity test was invalid — collinearity

`W-GRANULAR` existed so the resolution artifact could *win*, and it fired: `corr(1/C(W,4), POS) =
−0.9685`. **That correlation is meaningless.** Over 5 points, `1/C(W,4)` and POS are **both monotone
in W**, so they are collinear by construction and `ρ ≈ −1` *whatever the cause*. It cannot separate
"granularity did it" from "breadth did it".

**The valid discriminator is arithmetic:** one quantisation step of POS is `(1/|class|)/(core−floor)`
= **0.0210** at W=8, and the observed shift is **0.1818 = 8.7 steps**. Quantisation cannot produce it.

⭐ **The lesson is not "use a better statistic" — it is that a correlation between two monotone
functions of the same driver is never a discriminator**, and this design put both on the x-axis
without noticing.

## ⛔ And the verdict string said "FLAT" when the grid shows rise-then-plateau

The `W-CLAUSE` branch printed *"the within-family fraction is FLAT in breadth"*. **It is not flat** —
it rises 0.1298 then saturates. §4's *verdict string is not a computation*, again: the shape is now
computed (`rise`, `plateau sd`) and printed, not asserted. ⚠ The pre-registered
`|POS(16) − POS(8)| = 0.1818` sits just under its 0.20 threshold **precisely because it pairs one
point in the rising regime with one in the plateau** — a threshold I wrote before knowing the curve
had two regimes.

## Impossible here, named

- **a second prompt-blind family with breadth** — exactly one exists; would require generating and
  scoring ≥16 new prompt-blind criteria, a generation job with its own assumptions.
- **whether `promptecho` is prompt-blind** — its provenance is not in the source that was searched.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
