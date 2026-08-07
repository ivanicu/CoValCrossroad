# R496 · The deficit is not discriminativeness — refuted at n=968, with power

**The decision this made safe.** R495 could not test whether `gen` loses because its criteria
discriminate less: across 7 non-independent arms the sign was owned by `topvar_k4`, the arm built to
be extreme on the predictor. **The paired per-prompt design has real n, and it refutes the mechanism.**

## The design I announced was the Oldham trap, killed before it ran

R495 closed proposing to find *"the prompts where `gen` loses most"* and ask what distinguishes them.
**That is selection on the outcome** — §4, Oldham 1962: binning a change score on one of its own arms
gives opposite gradients from the same data, and **regression to the mean guarantees a finding.**
Corrected: regress the paired difference on a predictor measured **independently** of the outcome,
over **all** prompts, none selected, dropped or binned.

## Result

| | |
|---|---|
| paired population | **968 prompts**, no selection on the outcome |
| mean deficit `coval_core − gen` | **+0.0311** |
| **corr(gen's criterion SD, the deficit)** | **+0.0013**, 95% CI **[−0.0640, +0.0608]** |
| **POSITIVE control** — corr(gen's SD, `generic`'s score) | **+0.2577** |
| corr(gen's SD, gen's own score) | +0.2067 |

⭐ **`generic` uses the same four criteria on every prompt.** That its score is predicted by *`gen`'s*
criterion spread at **+0.2577** proves two things at once: **the predictor is measurable** (so the null
is evidence, not silence) and **it is a prompt-difficulty proxy**. And gen's own score is predicted at
+0.2067 — **the same size**, i.e. entirely difficulty.

**World B.** The paired difference cancels difficulty by construction, and once it does, **the
correlation is +0.0013 with a CI tight around zero.** ⭐ **The CI is the MDE: any true |corr| above
~0.06 would have been seen.**

## Where this leaves the thread

**Three candidates for `gen`'s deficit, three exclusions, each by a control that could have confirmed:**

| round | candidate | killed by |
|---|---|---|
| R494 | repetition / mode-collapse | the `generic` confound control showed the same gradient |
| R495 | discriminativeness (across arms) | leave-one-out: `topvar_k4` alone flipped the sign |
| **R496** | **discriminativeness (paired, n=968)** | **null at +0.0013 with a firing control** |

**`gen`'s deficit is undiagnosed — and now undiagnosed with power on the leading candidate**, which is
a different epistemic position from undiagnosed for lack of trying.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R496_the_deficit_is_not_discriminativeness_at_n968/run.py
