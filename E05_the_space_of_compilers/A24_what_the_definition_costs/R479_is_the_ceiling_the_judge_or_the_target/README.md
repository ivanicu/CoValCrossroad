# R479 · Is the 0.54 ceiling the criteria, the judge, or the target?

**The decision this made safe.** R478 found four unrelated routes converging at 0.54–0.55. That band
is **not** where the target stops being predictable. **There is +0.0467 of headroom (3.8× the floor),
and the binding constraint is the JUDGE.**

## The ceiling, and why it is the mode

The maximum A2 any scorer without sight of the target can reach is the **modal human ranking** — the
Bayes-optimal point predictor under per-pair 0/1 loss — scored against a **held-out** annotator.

| | |
|---|---|
| **BAYES** (leave-one-out mode) | **0.6132** |
| single annotator vs another | **0.5458** |
| chance (R477, measured) | 0.4280 |
| ⚠ leaky version — held-out annotator *inside* the mode | 0.6520 → **leakage +0.0388** |

⭐ **The leave-one-out discipline is the whole design.** Including the held-out annotator in the mode
that scores against it inflates the ceiling by **+0.0388** — and that error runs in exactly the
direction that manufactures headroom and licenses *"the criteria are the problem"*.

⭐ **A free positive control.** Single-annotator-vs-annotator returns **0.5458** against the campaign's
independently committed human ceiling of **0.5451** — **Δ +0.0007**. A loader written this round
reproduces a number computed by other code in another round.

## Convergence — measured, not asserted

| m (annotators forming the mode) | 2 | 4 | 8 | 16 | all |
|---|---|---|---|---|---|
| BAYES | 0.5457 | 0.5643 | 0.5944 | 0.6184 | 0.6132 |

Estimator noise at 4 seeds: 0.6132 · 0.6169 · 0.6185 · 0.6175 → **resolution 0.0093**. The m=16 → all
step is **0.0052**, inside it. **Converged.**

## Attainment — `(arm − chance) / (BAYES − chance)`, all cells

| arm | 2B A2 | att | 0.8B A2 | att |
|---|---|---|---|---|
| `oracle_k4` | 0.6294 | **1.088** | 0.4475 | 0.105 |
| `coval_core` | **0.5665** | 0.748 | — | — |
| `topw_k4` | 0.5647 | **0.738** | 0.4638 | **0.193** |
| `generic` | 0.5513 | 0.666 | — | — |
| `genericpool16` | 0.5415 | 0.613 | — | — |
| `random_k4_s0` | 0.4928 | 0.350 | 0.4083 | **−0.106** |

**The same criteria attain 0.738 of the ceiling under one judge and 0.193 under the other.** That is
world **B**: the instrument, not the criteria, is what the band is made of.

⭐ `oracle_k4` exceeding 1.0 is not a defect — it was **fitted on the prompt's own rankings**, so it
is not a member of the class BAYES bounds. **Its +0.088 excess is the fitting advantage, measured.**

## Controls

| control | returned | |
|---|---|---|
| POSITIVE — the mode beats a single annotator | **+0.0673** > floor | ✓ |
| g=0 — mode over *shuffled* rankings | **0.4007** ≈ chance 0.428 | ✓ |
| CONVERGED — against measured resolution | 0.0052 ≤ 0.0093 | ✓ |
| LEAKAGE — reported beside the honest number | +0.0388 | ✓ |

## ⚠ Scope: this population is not R478's

R479 uses the **1,078** prompts with ≥3 rankings; R477/R478 used the **968** with `genericpool16`
coverage. So `topw_k4` reads 0.5647 here and 0.5475 there — **both correct for their populations**,
and the *ordering* of arms is what this round rules on. Quoting one number against the other's
baseline would be the scope error this campaign retracts most often.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R479_is_the_ceiling_the_judge_or_the_target/run.py

Compute-free · 20 mode resamples × 5 held-out draws · artifact `results/r479_ceiling.json`.
