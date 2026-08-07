# R495 · Discriminativeness is not testable this way either

**The decision this made safe.** R494 excluded repetition as `gen`'s deficit. The next candidate is
written into `select_core.py:145`: a criterion whose satisfaction is identical across the four
responses is **arithmetically inert**. ⭐ **That is a DERIVATION** — the algebra forces it. What would
be a measurement is how much of each arm's budget goes to near-inert criteria.

## The exact test is degenerate, and that was measured

Counting criteria **exactly** identical across responses: **0.0–0.1% for every arm**, including
`topvar_k4`, which selects on spread. **§4: `floor == ceiling` means the statistic is degenerate and
no threshold is admissible.** Float scores essentially never tie. ⚠ **Reported because it would
otherwise have looked like a clean null.**

## The graded version, with a control that could fail

| arm | mean SD | % SD<0.15 | A2 |
|---|---|---|---|
| **`topvar_k4`** | **0.2215** | 15.7% | **0.4854** ← lowest A2 |
| `coval_core` | 0.1555 | 51.0% | 0.5640 |
| `generic` | 0.1445 | 56.0% | 0.5505 |
| `random_k4_s0` | 0.1408 | 59.5% | 0.4920 |
| `topw_k4` | 0.1403 | 59.6% | 0.5618 |
| `full` | 0.1403 | 60.0% | 0.5077 |
| **`gen`** | **0.1356** | **62.5%** | 0.5337 |

**POSITIVE control PASSES:** `topvar_k4` has the highest mean SD, as its definition requires. **If the
measurement had disagreed, the measurement would be wrong.**

## Why the mechanism is not established — the sign is owned by one arm

`corr(mean SD, A2)` over 7 arms = **−0.4758**. Leave-one-out:

| dropped | corr |
|---|---|
| `random_k4_s0` | −0.6601 |
| `full` · `coval_core` · `gen` · `generic` · `topw_k4` | −0.56 … −0.44 |
| **`topvar_k4`** | **+0.4819 ⛔ SIGN FLIPS** |

**One arm decides the direction — and it is the arm constructed to maximise the predictor.** With
n=7 non-independent arms, **the across-arm design cannot test this**, and the flip demonstrates it
rather than suggesting it.

## What survives

**`gen` has the lowest mean SD of the real arms** (0.1356 vs `coval_core`'s 0.1555; 62.5% vs 51.0%
below SD 0.15). **That is a measurement.** Whether it **causes** the deficit is not answerable by
correlating seven arms — and the honest form of that sentence is the finding.

⭐ **Two candidates now excluded, both by controls that could have confirmed them:** repetition
(R494, killed by the `generic` confound control) and discriminativeness (here, killed by its own
leave-one-out). **`gen`'s deficit remains undiagnosed, and the ways of finding out have narrowed.**

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R495_discriminativeness_is_not_the_mechanism_either/run.py
