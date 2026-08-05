# R487 · The admissible population is 23 scorable arms, not three

**The decision this made safe.** R485 and R486 both rest on *the best ③-admissible prompt-aware arm*,
and both computed it over a **hand-picked list of 14 arms**. R486's report asserted *"gen, topvar_k4
and full are the whole population."* **`corebench/results/` holds 101 `sat_*.npz`.** Scoring every
eligible one: **`gen` really is the maximum, and the conclusion is now supported by 23 arms instead
of assumed from 3.**

## The population, counted rather than assumed

| | |
|---|---|
| `sat_*.npz` on disk | **101** |
| base arms (2B, non-sham) | 58 |
| ③-admissible **and prompt-aware** | **30** |
| — excluded by **schema** (`transport_*`) | 6 |
| — excluded by **coverage** (`provenance_probe`, 4 prompts) | 1 |
| **scored** | **23** |

⛔ **The `transport_*` family is not on this benchmark.** Its cells are keyed
`c365|int10006|ut3170|0` — conversation / intent / utterance ids from a different study — against this
benchmark's `prompt|criterion|response`. **Counting them was the same population error one scale
down: files matching a naming pattern are not members of a population.** They are excluded by schema
and named, never silently dropped.

## Result

| arm | A2 | percentile |
|---|---|---|
| **`gen`** | **0.5337** | **32.6** |
| `random_k12_s0` | 0.5080 | 0.0 |
| `full` | 0.5077 | 0.0 |
| `random_k8_s2` | 0.5025 | 0.0 |
| … 18 more … | 0.4764–0.5053 | **all 0.0** |
| `topvar_k4` | 0.4854 | 0.0 |

**22 of 23 sit at p0.0 — below every one of the 1,820 prompt-blind subsets.** Only `gen` rises above
the class floor at all, and it reaches p32.6.

⭐ **`random_k12` does beat `random_k4`** (0.5080 vs 0.4920), as R477's spec curve implied — **and it is
still below the entire class.** More random criteria help, and not nearly enough.

## What this does to R485 and R486

**World B: both hold, and both are now properly supported.**

- **R485 stands**: nothing ③-admissible clears the ceiling — now checked against 23 arms, not 3.
- **R486 stands, and is strengthened**: its downgrade rested on `gen` alone being weak. It is not just
  `gen` — **the entire admissible prompt-aware population on this site is at or below p32.6.**
- **The honest state is unchanged: UNDETERMINED.** Whether ③ forbids the winning mechanism, or nobody
  has built a good rating-blind prompt-aware arm, still cannot be separated here — but the second
  disjunct is now a **measured fact about 23 arms** rather than an inference from one.

## Controls

| control | returned |
|---|---|
| POSITIVE — `topw_k4` clears the ceiling and sits high | **p100.0** |
| g=0 — `random_k4_s0` must sit low | **p0.0** |
| COVERAGE — arms under 90% named and excluded from the max | `provenance_probe` (4 prompts, 0.4%) |
| SCHEMA — non-benchmark arms named and excluded | 6 `transport_*` |
| PLACEBO — `gen` vs shuffled rankings | **0.4472** ≈ chance 0.428 |

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R487_the_admissible_population_is_32_not_three/run.py

Compute-free · deterministic (crc32) · artifact `results/r487_full_admissible.json`.
