# R497 · The deficit is real — the predictors were wrong

**The decision this made safe.** Three predictors failed to explain `gen`'s deficit, and a fourth
(criterion length: **9.34 vs 13.25 words**, corr **+0.0319**, CI [−0.0231, +0.0896]) failed too.
**Three large between-arm differences, three null within-prompt correlations** — a pattern with a
comfortable explanation: *the deficit is a constant offset and there is nothing per-prompt to
explain.* **It is false, and testing it before believing it is the round.**

| | |
|---|---|
| mean deficit `coval_core − gen` | **+0.0311** |
| observed sd of the per-prompt deficit | **0.1388** |
| **noise floor**, measured from two independent annotator draws | **0.0353** |
| **implied true sd** | **0.1342** — **3.8×** the noise |
| **test-retest reliability** | **+0.9355** |

⭐ **The floor is measured, not modelled.** A2 samples a held-out annotator per prompt, so re-running
at an independent seed is a second draw of the *same* quantity and `sd(d₀−d₁)/√2` is its per-draw
noise directly. **This is the one design in the thread where the instrument supplies its own floor.**

## What it means

**`gen` does not lose uniformly.** The deficit's spread is **4.3× its own mean** — it loses
enormously on some prompts and **wins** on others, and that pattern **reproduces at r = 0.94** across
independent annotator draws.

⛔ **So the three nulls are not one dead design.** There is a large, stable, per-prompt target;
**repetition, discriminativeness and length are simply the wrong predictors of it.**

| round | candidate | outcome |
|---|---|---|
| R494 | repetition | excluded — `generic` confound control showed the same gradient |
| R495 | discriminativeness (7 arms) | untestable — one arm owned the sign |
| R496 | discriminativeness (paired, n=968) | **excluded with power**, firing control |
| R497 | *"nothing to explain"* | **excluded** — r = 0.94, true sd 3.8× noise |

⭐ **The search is validated rather than excused**, which is the opposite of what a fourth null
usually buys.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R497_the_deficit_is_real_and_the_predictors_were_wrong/run.py
