# R486 · Is ②'s bar an outlier, or the class? — and what it does to R485

**The decision this made safe.** R485 concluded ② and ③ **conflict**. That reading holds only if the
bar is fair *and* the admissible side is fairly represented. **It is not: the best ③-admissible
prompt-aware arm sits at percentile 32.6 of the prompt-blind class.** R485's observation stands; its
interpretation is downgraded to **UNDERDETERMINED**.

⚠ **And half my question was already answered.** `R454_is_the_bound_a_property_of_the_pool` swept pool
breadth W ∈ {6…16} and found the bound **saturates by W≈12** (sd over W=12–16 = 0.0153). The bar is
not pool-**size** limited. My next-gradient line said this "has never been asked" — it had, on the
axis that mattered most; what remained was **strength**, not size.

## The class, published as quantiles

| p0 | p10 | p25 | p50 | p75 | p90 | p100 |
|---|---|---|---|---|---|---|
| 0.5120 | 0.5259 | 0.5315 | **0.5378** | 0.5430 | 0.5474 | 0.5555 |

| arm | A2 | percentile |
|---|---|---|
| `coval_core` | 0.5640 | **100.0** |
| `topw_k4` | 0.5618 | **100.0** |
| `generic` | 0.5505 | 96.7 |
| **`gen`** — best ③-admissible **prompt-aware** | **0.5337** | **32.6** |
| `full` | 0.5077 | 0.0 |
| `random_k4_s0` | 0.4920 | 0.0 |

## What this does to R485

**Not world A** — the bar is not a thin unbeatable tail; `gen` loses to 67% of the class, not to a
handful of outliers. **Not world B** — `gen` is not mid-pack. **World C: the admissible arm is weak.**

⛔ **So the measured conflict is confounded with `gen`'s quality.** R485 could not distinguish
*"③ forbids the winning mechanism"* from *"nobody has built a good rating-blind prompt-aware arm
here"*, because **the admissible side is represented by exactly one arm and that arm is poor.**

⭐ **What still stands from R485, unchanged:** five of five arms clearing the cross-fitted ceiling are
③-excluded, and `coval_core` and `topw_k4` beat **every one of the 1,820 subsets**. That is an
observation about which mechanisms reach the top, and it does not depend on `gen`.

## Controls

| control | returned | |
|---|---|---|
| POSITIVE — `topw_k4`, which clears the ceiling, must sit high | **p100.0** | the percentile scale measures what the ceiling comparison measured |
| g=0 — `random_k4_s0` must sit low | **p0.0** | a scale where a random arm scores high is not a scale |
| PLACEBO — class re-scored against pair-shuffled targets | sd **0.0018** vs real **0.0082** | the spread is signal, not arithmetic |
| CROSS-CHK — `generic`, the released prompt-blind set | p96.7 — **near the top of its own class**, so R477 used a strong comparator, not a typical one |

## Register — what would settle it

**A second ③-admissible prompt-aware arm that is not weak.** R454 established this site has exactly
one prompt-blind family of breadth ≥ 16 and no resampling makes a second; the same scarcity applies
here — `gen`, `topvar_k4` and `full` are the whole admissible prompt-aware population, at p32.6, p0
and p0. **Building a strong one requires generating criteria and judging them: a GPU round, named
rather than pretended.**

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R486_is_clause_two_bar_an_outlier_or_the_class/run.py

1,820 subsets · 968 prompts · compute-free · deterministic (crc32).
