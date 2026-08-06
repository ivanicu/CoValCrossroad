# R801 · two robustness statistics, two different winners — so the round claims no world

`run.py` · `PREREGISTRATION.txt` · `results/frontier.json` · 1,820 blind 4-subsets × 968 prompts ×
all annotators · **NO WORLD CLAIMED** — the pre-registered *first* branch ·
two hash seeds byte-identical, md5 `3f1d883356ecf49ef165cbc65114bd82`

## THE DECISION THIS MAKES SAFE

**"Robust across prompts" is not one objective.** Over the full space of blind 4-criterion cores:

| objective | argmax subset | value |
|---|---|---:|
| pooled mean | **(0, 3, 9, 14)** | 0.5575 |
| −cross-prompt sd | **(1, 2, 3, 14)** | sd 0.1479 |
| worst-decile | **(0, 1, 9, 14)** | 0.2783 |

**The two robustness statistics pick different subsets from each other**, not merely from the mean.
The preregistration made that outcome the branch checked *first*, and it fired — so no world is
named. Choosing one would be choosing the statistic that gives the answer.

## ⭐ AND THE MEAN FORGONE IS UNRESOLVED EITHER WAY

| choosing the… | mean forgone against the pooled-mean winner |
|---|---|
| −sd argmax (1, 2, 3, 14) | **+0.00358 [−0.00136, +0.00818]** — unresolved |
| worst-decile argmax (0, 1, 9, 14) | **+0.00085 [−0.00280, +0.00429]** — unresolved |

Paired bootstrap over prompts (D4: all 1,820 share the same 968, so an unpaired comparison would be
meaningless). **Robustness is not expensive here — it is simply not identified as a distinct choice.**

## ⛔ AND THE ARITHMETIC TRAP WAS REAL: ~80% OF "ROBUSTNESS" IS THE MEAN

| robustness statistic | R² on the pooled mean | residual sd |
|---|---:|---:|
| −cross-prompt sd | **0.7844** | 0.00119 |
| worst-decile | **0.8366** | 0.00417 |
| −noise-corrected sd | 0.7843 | 0.00129 |

D2 registered this before the run: an affine robustness statistic **cannot** disagree with the mean,
so the estimand is the residual, never the rank agreement. Four fifths of each robustness statistic
is the mean restated; what is left is small and its argmax is a different subset again
((9,11,12,13) for sd, (3,6,11,13) for the decile).

**Only 4 of 1,820 subsets are Pareto-optimal in (mean, −sd), and the pooled-mean winner is one of
them.**

## ⭐ THE RELEASED BLIND ARM IS NEAR-OPTIMAL ON BOTH AT ONCE

`generic` = `POOL[0:4]` = subset (0, 1, 2, 3):

> pooled mean **0.5504 — percentile 93.7**
> cross-prompt sd **0.1504 — percentile 3.1** (among the 3% most consistent)
> worst-decile 0.2721

**It is simultaneously in the top decile on the mean and the bottom decile on spread**, which is why
no choice between the objectives was ever forced for it.

## ⛔⛔ AND HALF THE POPULATION CANNOT ASK THIS QUESTION AT ALL

`select_core.py:121` loops **per prompt** and selects from that prompt's own rubric, so every
rubric-derived arm is chosen independently on each prompt and **has no cross-prompt objective to
vary**. R800's NEXT was well-posed only for blind arms. Saying so is part of the finding.

## ⛔ MY OWN OBJECT ANCHOR WAS REFUTED BY R788 BEFORE I WROTE IT

D1 required the subset (0,1,2,3) to equal `generic`'s committed A2 **to 1e-9**. The run exited 2 at
**0.5504358540** against **0.5513543392**. R788 had already established that `generic` **is**
`POOL[0:4]` as a criterion set but was **scored in a different judge pass** — satisfactions differing
by mean |Δ| **0.005638**, up to 0.121 on 73 of 968 prompts. **An exact match was never available and
my own prior round said so.** Repaired: the anchor is agreement within that measured discrepancy —
observed **|Δ| 0.000918**, well inside **0.005638**. ⭐ The first anchor stands unchanged and exact:
the all-16 subset **is** `genericpool16`, |Δ| **0.0e+00**.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT anchor 1 | all-16 subset **0.5422329001** vs committed, \|Δ\| **0.0e+00** | PASS, exact |
| OBJECT anchor 2 | \|Δ\| **0.000918** against R788's **0.005638** | PASS **after repair**; exit 2 fired first |
| PLACEBO | a subset against itself: **0.0e+00** | PASS |
| POSITIVE | mean-preserving perturbation, sd 0.02 → cross-prompt sd 0.1490→**0.1500**, decile 0.2765→**0.2726**; sd 0.08 → **0.1731** / **0.2436**; mean moves **+0.00e+00** at both | PASS — band at two magnitudes, both statistics monotone, mean unmoved |
| NEGATIVE | humans shuffled across prompts (46 subsets sampled): mean **0.5386 → 0.4247** | PASS |
| CONFOUND | annotator noise subtracted: sd range **[0.1479, 0.1614] → [0.1354, 0.1501]**; the residual R² moves 0.7844 → 0.7843 | the correction changes nothing |
| NOISE FLOOR | per-prompt annotator split-half variance **0.003527** (sd 0.0594) | measured |

## MULTIPLICITY

1,820 subsets × 3 statistics = 5,460 computed quantities, but **one comparison is tested**: the mean
forgone, on a paired bootstrap. ⚠ **The winner's mean 0.5575 is an extremum of 1,820 correlated
draws** and is quoted as such — it is not an estimate of that subset's population value.

## WHAT DIED

- **R800's NEXT as posed** — half the population cannot express the choice.
- **"robust across prompts" as a single objective** — its two natural statistics disagree with each
  other.
- **my own D1 anchor**, refuted by R788 before the round was written.

## WHAT SURVIVES

The two anchors, one exact. And an object fact worth keeping: the released blind arm sits at the
**93.7th percentile on the mean and the 3.1st on spread**, so the release's own generic core is
already near the joint optimum of a space of 1,820.

## SCOPE

1,820 blind 4-subsets of `genericpool16` × 968 prompts × all annotators (median 16) · instrument A2
against the human annotators · paired bootstrap over prompts, NBOOT 1,200 · first release, home
judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| the same question for rubric-derived arms | a selector with a cross-prompt objective; `select_core.py:121` chooses per prompt |
| a blind pool larger than 16 | the release ships one, of 16 |
| whether robustness is DESIRABLE | a stated purpose for the benchmark |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The objective question is answered in the negative: over 1,820 blind cores the mean and two
robustness statistics agree to R² 0.78–0.84 and their argmaxes disagree with each other, with the
mean forgone unresolved in both directions. Computed by this round's `run.py`, only 4 of 1,820 are
Pareto-optimal and `generic` already sits at percentile 93.7 / 3.1. So clause ② does not have to
choose an objective — the space is too flat for the choice to matter. The step is back to the
definition's own text: **write clause ② as the per-prompt predictive-standing claim R800 located,
state the objective as the pooled mean because nothing distinguishes it, and then name the admissible
object it excludes** — which is the one test §4 says every clause must survive and which this arc has
run on only two of its five clauses.
