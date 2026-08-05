# R480 · The judge moves every level. Does it move the order?

**The decision this made safe.** Clause ② reads *"better than the best generalising prompt-blind
set"* — a **comparative**. R479 showed the judge owns most of the level. **Order survives across
families (0.9130) and REVERSES within them (0.3692), and the entire reversal is one family.**

## The gradient I announced was void by algebra, not by measurement

R479 closed by proposing to select criteria maximising **attainment** rather than A2.
`attainment = (A2 − chance)/(BAYES − chance)`; both constants are properties of the human target, so
the map is affine with slope **5.3997 > 0** and `argmax` is invariant. **Maximising attainment IS
maximising A2.** Killed at rung 1 of the attack ladder, zero compute. **A DERIVATION, not a finding.**

## The estimand

`SIGN_SURVIVAL` = P(the 0.8B judge agrees with the 2B judge on which of two arms is better), over
pairs **resolved under 2B** (|Δ| > 0.0122). Restricting to resolved pairs *is* the identification
argument: an unresolved pair flips for free and would drag the statistic to 0.5 for reasons that have
nothing to do with the judge.

| | survival | pairs |
|---|---|---|
| **pooled** | **0.8019** [0.7610, 0.8396] | 318 of 465 |
| across-family | **0.9130** | 253 |
| **within-family** | **0.3692** | 65 |

**0.3692 is below chance. That is a systematic reversal, not disagreement.**

## The reversal is one family, and it has a direction

| family | corr(k, A2) 2B | corr(k, A2) 0.8B | sign survival | |
|---|---|---|---|---|
| `topw` — selective | −0.0211 | −0.4234 | **10/10** | same direction |
| `random` — unselected | **+0.8570** | **−0.5026** | **14/55** | ⛔ **OPPOSITE** |

**Adding criteria to a *random* set helps the 2B judge (+0.86) and hurts the 0.8B judge (−0.50).**
The judges agree on the ordering of **selective rules** and disagree on the effect of **size** for
unselected sets. ⭐ **This lands on the definition's size clause** — *"more than one; 3–8
indistinguishable"* was established on 2B, and under 0.8B the k-gradient for unselected sets has the
opposite sign. **A size claim is judge-relative in a way a family claim is not.**

## Controls

| control | returned | |
|---|---|---|
| **PLACEBO ⭐ split-half of the SAME judge** | **0.9848 ± 0.0121** | order survives near-perfectly when the judge does not change |
| POSITIVE — 20 largest-\|Δ\| pairs | **1.0000** | |
| g=0 — pairs *unresolved* under 2B | **0.4218** (147 pairs) | ≈ chance, so the statistic is not high everywhere |
| NEGATIVE — 0.8B labels shuffled | **0.5135** | null |

⭐ **The split-half placebo is why this round is readable at all.** Without it, 0.80 is uninterpretable
— it could be judge disagreement or estimation noise. At 0.9848 the design demonstrably resolves
order, so the **−0.1829 gap is the judge**, measured against what a non-changing judge achieves.

## Specification curve — resolution threshold, all cells

| threshold | pairs | survival | placebo |
|---|---|---|---|
| 0.0122 (1× floor) | 318 | **0.8019** | 0.9801 |
| 0.0244 (2×) | 247 | 0.9109 | 0.9992 |
| 0.0366 (3×) | 209 | 0.9522 | 1.0000 |

**The disagreement is concentrated in small differences** — which is exactly where a definition's fine
distinctions live. At 3× floor the judges essentially agree; at the resolution the definition
actually operates at, they do not.

## Reproducibility

Two independent processes, **byte-identical output**. This required a fix: the per-prompt annotator
draw was seeded from `hash(p)`, and Python salts string hashing per process — see retraction 303.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R480_does_the_judge_change_the_order_or_only_the_level/run.py

31 arms × 2 judges × 968 prompts · compute-free · artifact `results/r480_order.json`.
