# R494 · The generator's deficit is not repetition

**The decision this made safe.** ②∧③ is UNDETERMINED because the best ③-admissible prompt-aware arm,
`gen`, sits at **percentile 32.6** of the prompt-blind class. Settling it needs a **better admissible
arm**, so the first question is why this one is weak — **and the answer decides what to build.**

## Two explanations excluded before any mechanism was proposed

| | |
|---|---|
| *"`gen` isn't really prompt-aware"* | **dead** — 3,868 criteria, **84.2% unique**, only **0.1%** coincide with the generic pool |
| *"prompt-specificity doesn't help"* | **dead** — `coval_core` is prompt-specific too (**99.6% unique**) and **beats** `generic` (0.5640 vs 0.5505), while `gen` loses to it (0.5337) |

**⇒ the deficit is in what `gen` writes.**

## The candidate, and the control that killed it

`gen` repeats phrasings up to **29×** against `coval_core`'s near-total uniqueness — mode-collapse
toward generic-sounding text is the obvious mechanism. Stratifying prompts by the max corpus-frequency
of their own generated criteria:

| stratum | `gen` | `generic` — **CONTROL** |
|---|---|---|
| unique-ish (≤2), n=644 | 0.5287 | 0.5407 |
| repeated (≥6), n=204 | 0.5643 | 0.5799 |
| **gradient** | **−0.0357** | **−0.0393** |

⭐ **`generic` uses the same four criteria on every prompt.** Its criteria *cannot* repeat
differentially, so any gradient it shows across these strata is **prompt difficulty by construction** —
and its gradient is the **same sign and within a factor of 2**. **World B: repetition explains
nothing.**

⚠ **And the sign is the opposite of the hypothesis.** Prompts whose criteria repeat score **higher**,
in both arms. I predicted repetition would hurt; it tracks **easier prompts**.

## What this leaves

**`gen`'s deficit is UNDIAGNOSED.** One candidate is excluded — with a control that could have
confirmed it and did not, which is the only kind of exclusion worth having. **The build target for a
better admissible arm is still unknown, and that is a more honest position than "add decoding
diversity", which is what I would have written without the control.**

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R494_the_generators_deficit_is_not_repetition/run.py
