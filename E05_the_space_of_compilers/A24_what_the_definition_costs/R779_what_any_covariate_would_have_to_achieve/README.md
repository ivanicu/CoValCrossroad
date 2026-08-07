# R779 · the mediation bound — what ANY single covariate would have to achieve

`run.py` · `PREREGISTRATION.txt` · `results/mediation_bound.json` · tree_sha `1d64e4cdccc6` · 968 prompts

## THE DECISION THIS MAKES SAFE

**Stop looking for a prompt-level covariate that explains the arm families' co-movement.** Four
rounds (R776–R779) each proposed one and each returned a null, and until now every null was a
separate small disappointment that licensed one more attempt. This round replaces the sequence with
an arithmetic requirement: to account for a co-movement of `r = 0.5943`, a single covariate needs
`|corr(Z, each scale)| >= sqrt(r) = 0.7709`. **The best correlation any covariate in this thread
achieves with either scale is 0.3649** — short by a factor of **2.11** — and the in-sample multiple
correlation of all six together reaches at most **0.4290**, in **0 of 6** families.

## WHAT WAS MEASURED

E1 · the bound `corr(Z,A)·corr(Z,B)` against the measured drop when conditioning on Z. 6 covariates
× 3 M×R family pairs = 18 cells, whole table in the artifact. The eight largest bounds:

| covariate × pair | r(Z,A) | r(Z,B) | bound | measured | gap | spearman bound |
|---|---|---|---|---|---|---|
| rubricdisagree × Rc | +0.3588 | +0.3649 | +0.1309 | +0.0618 | −0.0691 | +0.1388 |
| rubricdisagree × Rb | +0.3393 | +0.3649 | +0.1238 | +0.0575 | −0.0663 | +0.1293 |
| rubricdisagree × Ra | +0.3206 | +0.3649 | +0.1170 | +0.0521 | −0.0649 | +0.1236 |
| overlap × Rb | −0.1708 | −0.1543 | +0.0264 | +0.0110 | −0.0154 | +0.0210 |
| overlap × Ra | −0.1414 | −0.1543 | +0.0218 | +0.0088 | −0.0130 | +0.0175 |
| n_rubric × Rb | +0.1549 | +0.1289 | +0.0200 | +0.0081 | −0.0119 | +0.0225 |
| overlap × Rc | −0.1192 | −0.1543 | +0.0184 | +0.0073 | −0.0111 | +0.0144 |
| n_rubric × Rc | +0.1119 | +0.1289 | +0.0144 | +0.0059 | −0.0085 | +0.0176 |

E2 · co-movement **0.5943**, required **0.7709**, best achieved **0.3649** → **2.11× short**.

E3 · in-sample multiple correlation, reported ONLY as a ceiling because it is fitted and evaluated on
the same 968 prompts: Ra 0.3938 · Rb 0.4110 · Rc 0.4133 · F1 0.3102 · F3 0.2034 · M 0.4290. **0 of 6
reach 0.7709**, and the true out-of-sample values are lower than these.

D3 · realised criterion **overlap is shared across families at 0.8871** while the **scales share only
0.5943**. The most-shared variable in the thread explains the least.

## CONTROLS, AND WHAT THEY RETURNED

| control | returned | |
|---|---|---|
| PLACEBO | a family against itself, 1.000000 | PASS |
| g=0 | an independent covariate removes +0.0000 | PASS, inside the negative band |
| NEGATIVE | 200 permutations, drop +0.0001 [−0.0010, +0.0023] | conditioning on *any* vector removes nothing |
| SHAM | same marginal, no relation, +0.0000 | |
| POSITIVE | a synthetic mediator, share recovered 1.0526 at w=0.5 and 1.0000 at w=1.0 | PASS |
| SPEARMAN | every bound in both forms; the rank version is *larger*, so the Pearson figure is not flattering the null | the registered confound |

### ⚠ THE POSITIVE CONTROL FAILED FIRST, AND THE FAILURE CORRECTED MY OWN D1

The registered POSITIVE built `Z = a·scale_A + b·scale_B + noise` and required the measured drop to
**match `corr(Z,A)·corr(Z,B)` within 0.05**. It failed: gaps of **−0.0031 (w=0), −0.0848 (w=0.25),
−0.1359 (w=0.50), +0.0080 (w=1.0)**, and the round gated to UNVERIFIED as the preregistration
required.

The diagnosis is not an instrument defect. It is that **I registered an inequality as an equality.**
Exactly,

```
r_AB.Z = (r_AB − r_ZA·r_ZB) / sqrt((1 − r_ZA²)(1 − r_ZB²))
```

so the *drop* is `r_AB − r_AB.Z`, and the denominator **inflates the partial**, pushing the drop
**below** the product everywhere except where `r_ZA, r_ZB` are small. The product is a first-order
approximation valid in the weak regime — which is exactly where every real covariate here sits
(`|r| <= 0.3649`), and precisely why it looked tight in the two cells the preregistration checked it
against. The sweep walked out of that regime and exposed it.

**The repair is not a looser tolerance.** Checking the exact formula would be a tautology — both
sides are built from the same three correlations, and §4's *check that cannot fail* covers it. So
the control was rebuilt against a **generative** truth: construct `A` and `B` from a common `Z` where
the mediated share is **1.0 by construction**, and require the measured drop to recover the whole
correlation. That can fail. It returns 1.0526 at w=0.5 and 1.0000 at w=1.0.

Consequences carried into the page: **every one of the 18 gaps is negative** (worst −0.0691), which
is now read as the inequality holding rather than as agreement, and world B's trigger is restated as
*a drop EXCEEDING its bound*, which no cell does. The w=0.25 rung recovers 1.4885 because its raw
correlation is 0.0431 and the share's denominator is near zero — reported, not gated on.

## WHAT DIED

- **the covariate programme**, with a number rather than with fatigue: `sqrt(0.5943) = 0.7709` versus
  a best of `0.3649`.
- **"sharing is mediation"** — overlap is shared at 0.8871, more than the scales are, and moves |d|
  by −0.15. A shared driver transmits co-movement only in proportion to how much it *drives*.
- **my own D1 as stated**: `corr(Z,A)·corr(Z,B)` is an upper bound on the drop, not its value.

## WHAT SURVIVES

The residual co-movement is a property of **which arms were chosen**, not of the prompts. Every
prompt-level variable this thread can construct is bounded from explaining it, and the bound is
computable before the next covariate is built.

## SCOPE

population 968 prompts · instrument A2 per prompt over all annotators · baseline the drops from
R776–R778 recomputed here · regime first release, home judge, tree_sha `1d64e4cdccc6`.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| a non-monotone mediator | a functional-form search, which on 968 prompts × 6 covariates is fitting noise; the Spearman column bounds the monotone case only |
| an out-of-sample multiple correlation | a held-out prompt set, halving an n already short by 2× (R769) |
| cross-release | a second release |
| independently replicated | a second team; the session prompt forbids agents |

## NEXT

The covariate route is closed by arithmetic, so the next gradient is not another covariate. The
residual belongs to the arm SET, so the next quantity is how much of a family's scale is fixed by its
**k profile and its selection rule jointly** — a 2-factor decomposition over the 6 families, which is
a different object from R775's rule gradient because it conditions on both at once rather than
ranking one. Searched before registering it: of **482** round directories in this arc,
`grep -rlE "two[- ]factor|2-factor|k *[x×] *rule|jointly.*(k|rule)"` over every `run.py` and
`PREREGISTRATION.txt` returns **1** — `R732_the_third_cell_varied_two_things`, which reports that a
cell varied two things at once rather than decomposing the variance between them.
