# R477 · What does clause ③ actually cost?

**The decision this made safe.** R475 left a fork — weaken ③ to forbid only the prompt's *rankings*,
or keep it strong and accept that the definition excludes CoVal-core. **That fork as posed is a
stipulation, not an experiment.** This round measures the thing that should decide it: **what does a
core gain by reading the annotator ratings?** Answer: **not enough to resolve above the floor.**
**③ stays strong. `coval_core` stays EXCLUDED. The extension stays 0.**

## The estimand and why the first version of it was wrong

`VALUE_OF_RATINGS = A2(topw_k4) − A2(best ③-admissible selector at k=4)`.

My first comparator was `topvar_k4` — same machinery (rank all criteria by a scalar, take top-4),
ingredient removed (the scalar is response spread, which `select_core.py:145` calls *"a property of
the responses, never of the human target"*). It gave **+0.0695**.

⛔ **It is a poison, not a placebo.** `topvar_k4` scores **0.4780** — *below* the random baseline
(0.4856 / 0.4913 / 0.4790). §4's stated tell, verbatim: *"the sham scores at or BELOW the random
baseline."* Most of `+0.0695` is the cost of ranking by variance, not the value of ratings.

## The measurement, against the best of the admissible class

| judge | admissible arms | best | `topw_k4 −` best | floor | effect/floor |
|---|---|---|---|---|---|
| **2B** | 9 | `generic` **0.5376** | **+0.0099** [+0.0009, +0.0189] | 0.0122 | **0.81** |
| 0.8B | 4 | `topvar_k4` 0.4279 | +0.0342 | 0.0096 | ⚠ class unbounded |

**`effect/floor = 0.81 < 1.5` — no count is admissible, only a direction.** The bootstrap CI excludes
zero while the seed floor does not; **the floor wins**, and the honest statement is that reading the
ratings buys a *positive but unresolved* amount over the best rating-blind arm this site can build.

⚠ **The 0.8B judge cannot test this**: `generic`, `genericpool16`, `gen`, `full` and `promptecho` have
no `_08b` variants, so its "best admissible" is bounded by 4 arms and is not comparable. **UNVERIFIED
there — not agreement, and not disagreement.**

## Controls

| control | returned |
|---|---|
| **g=0 / FLOOR** — three `random_k4` arms differing only in the draw | 0.0122 (2B), 0.0096 (0.8B), **measured** |
| **POSITIVE** — `oracle_k4` reads the human target directly | +0.1184 / +0.0365, both beyond floor |
| **PLACEBO** — every arm vs *shuffled* rankings | 0.4250–0.4293, spread 0.0043 |
| **SHAM** — `topvar_k4` | **failed as a sham** (below random); reported, not relied on |

⭐ **Chance is 0.428, not 0.5.** `cls()` returns {−1, 0, +1} per pair, so agreement with a random
relabelling is not a coin flip. The placebo **measured** it rather than assuming it.

## Specification curve — `topw_k` − `random_k`, every k, both judges

| k | 2B | 0.8B | signs agree |
|---|---|---|---|
| 1 | UNAVAILABLE | UNAVAILABLE | — |
| 2 | +0.0668 [+0.054, +0.079] | +0.0468 [+0.035, +0.059] | yes |
| 3 | +0.0741 [+0.063, +0.086] | +0.0534 [+0.043, +0.064] | yes |
| 4 | +0.0619 [+0.052, +0.072] | +0.0536 [+0.044, +0.063] | yes |
| 6 | +0.0610 [+0.052, +0.071] | +0.0378 [+0.030, +0.046] | yes |
| 8 | +0.0524 [+0.044, +0.061] | +0.0357 [+0.029, +0.043] | yes |
| 12 | +0.0272 [+0.021, +0.033] | +0.0175 [+0.012, +0.023] | yes |

`k=1` has no `random_k1` arm — **UNAVAILABLE, stated rather than dropped**. Selection-plus-ratings is
worth a lot over *random*; it is the split against a *good* rating-blind arm that does not resolve.

## The side finding, and it is not small

**`generic` — a fixed, prompt-blind criterion set that reads no ratings and no rankings — scores
0.5376, within the floor of `topw_k4`.** Clause ② is exactly *"better than the best generalising
prompt-blind set"*. This is the ② test seen from the other side, and `topw_k4` does not clear it.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R477_what_does_clause_three_actually_cost/run.py

Compute-free (all arms committed) · seeds 0,1,2 · artifact `results/r477_value_of_ratings.json`.
