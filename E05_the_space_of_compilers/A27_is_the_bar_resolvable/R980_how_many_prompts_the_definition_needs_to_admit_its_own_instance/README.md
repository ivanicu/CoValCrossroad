# R980 · the definition needs ~240 of its 968 prompts to admit its own instance at even a coin flip

**THE DECISION THIS MAKES SAFE.** Whether "`coval_core` is a core" can be stated without a sample
size. It cannot. At full N the admission is deterministic and holds — but the headroom is **about a
quarter of the corpus**, against an oracle that needs **nine prompts**.

---

## The fact R978 measured and I did not report

R978's artifact contains it, in a `left` list: at N=242 under `generic`, **`coval_core` itself leaves
the extension in 2 of 3 seeds**, and its `_2bA`/`_2bB` siblings leave in 3 of 3. The churn's most
consequential member was the released core, and I reported the count instead of the member.

## The arithmetic, registered before the sweep

Admission is `lo > 0` on the paired bootstrap margin, so an arm is resolvably admitted once
`z·sd/√N < margin`:

```
N* = (z · sd / margin)²
```

| arm vs comparator | margin | sd | **N\*** |
|---|---|---|---|
| `coval_core` vs **`generic`** | +0.015123 | 0.11876 | **236.9** |
| `coval_core` vs `genericpool16` | +0.024245 | 0.12000 | 94.1 |
| `oracle_k4` vs `generic` | +0.076949 | 0.11900 | **9.2** |
| `random_k4_s0` vs `generic` | −0.058667 | 0.15943 | ∞ (never) |

R978 sampled at **242**, just above 237 — which is exactly why that cell was a coin flip.

## The sweep — out of sample against that curve

Admission rate over 10 seeds, `coval_core`:

| N | `generic` | `genericpool16` |
|---|---|---|
| 60 | 2/10 | 4/10 |
| 120 | 2/10 | 8/10 |
| 180 | 3/10 | 9/10 |
| **240** | **6/10** | 9/10 |
| 300 | 7/10 | 9/10 |
| 400 | 8/10 | 10/10 |
| **500** | **10/10** | 10/10 |
| 968 | 10/10 | 10/10 |

**Registered 237 → measured 0.5 crossing at 240. Registered 94 → crossing between 60 and 120.**
The shape matches too: monotone, and `generic`'s curve strictly right of `genericpool16`'s, as the
stronger comparator's larger cut requires.

⚠ **The grid is coarse and 10 seeds is few.** Wilson intervals are wide — even 10/10 is only
[0.72, 1.00], and 6/10 is [0.31, 0.83]. **The crossing points are consistent with the registered N\*,
not measured to a prompt.** What is solid is the ordering, the shape, and the bracket.

## Controls

| control | result |
|---|---|
| **POSITIVE (high)** | `oracle_k4` (N\* = 9) admitted **10/10 at every N and both comparators** |
| **POSITIVE (low)** | `random_k4_s0` (N\* = ∞) admitted **0/10 everywhere** — so the rule does not admit anything |
| **NEGATIVE** | at N = 968 the subsample *is* the corpus: every seed gives the identical verdict, rate exactly 0 or 1 |
| **PLACEBO** | each comparator against itself: never admitted, both |

**54 cells recorded, all reported.**

## What this says about the definition

- **`coval_core` clears its own bar by a margin needing ~237 prompts; `oracle_k4` needs 9.** The
  released core sits **26× closer to the bar** than the arm the benchmark treats as the ceiling.
- **The reliable figure is ~500, not 237.** N\* is the 0.5 crossing; 10/10 arrives at 500 under
  `generic`. A definition quoted at "we used 968 prompts" is quoting roughly **2× the headroom** it
  actually needs, which is thinner than the number 968 suggests.
- **This is not fragility at full N.** At 968 the verdict is deterministic and `coval_core` is in.
  The claim is about how much of the corpus is *load-bearing*, and the answer is about a quarter.

## What it cannot say

- **Subsampling varies N, not the corpus** — "fewer prompts" and "different prompts" are not
  separated here, and a second release would be required.
- **It never asks whether the rule is right.** Construct validity for `core` needs an external gold
  standard this site does not have. This measures how much data the rule needs, nothing more.
- **The 0.95 crossing is a measurement, not a prediction.** `N*` predicts the 0.5 point only; the
  500 above is read off the grid and inherits its coarseness.

## Alternatives considered

**Fit a logistic curve to the rates and report a continuous N\*.** Refused: with 10 seeds per point
the fit would report a precision the design does not have, and the registered closed form already
gives the 0.5 point without fitting anything.

**Report only `genericpool16`, where the instance is admitted from N=120.** Refused — R923 measured
`generic` as the stronger and correct comparator, and reporting the weaker one because it flatters
the instance is the failure this project has already committed once.
