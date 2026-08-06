# R791 · the finest decomposition the release supports is a reparameterisation — the scalar was not throwing anything away

`run.py` · `PREREGISTRATION.txt` · `results/components.json` · 20 objects × 968 prompts × 6
components · 1,140 cells · **WORLD C** · two hash seeds byte-identical, md5 `68b10b813c7847b7b9e0771624eaceeb`

## THE DECISION THIS MAKES SAFE

**A2 is exactly the mean of six pairwise-comparison agreements (D1, verified to 1.1e-16), and those
six carry one direction.** The centred (20 arms × 6 components) matrix has eigenvalue shares

> **0.9936** · 0.0031 · 0.0015 · 0.0009 · 0.0007 · 0.0002

**99.36% in the first component.** So the decomposition is a **reparameterisation**, and R790's
question — *should clause ② be a scalar comparison at all?* — has an answer for this release: **on
the finest decomposition it supports, there is nothing the scalar was hiding.**

## ⭐ AND THE DECISIVE PAIR IS INDISTINGUISHABLE ON ALL SIX

`coval_core` − `topw_k4`, which the scalar cannot resolve at `t` 0.75:

| component | eff | MDE | `t` | p | |
|---|---:|---:|---:|---:|---|
| AB | +0.010331 | 0.016766 | 1.73 | 0.0800 | — |
| AC | +0.005510 | 0.017702 | 0.87 | 0.3683 | — |
| AD | **−0.002140** | 0.017495 | 0.34 | 0.7600 | — |
| BC | **−0.004866** | 0.019459 | 0.70 | 0.4700 | — |
| BD | +0.001375 | 0.017368 | 0.22 | 0.8500 | — |
| CD | +0.003569 | 0.017240 | 0.58 | 0.5683 | — |

**Not one survives BH+MDE**, and the signs are mixed while every magnitude sits inside its own
resolution. The two arms are the same object at every resolution this release offers.

## ⛔ AND THE DECOMPOSITION RESOLVES *FEWER* PAIRS, NOT MORE

| family | cells | surviving BH + MDE | pairs resolved |
|---|---:|---:|---:|
| scalar A2 | 190 | 155 | **155** |
| componentwise | 1,140 | 855 | **152** |

**D2 was registered in advance for exactly this**: more cells is arithmetic, so only the post-BH
comparison is a finding — and after each family's own BH the decomposition **loses three pairs**.
Identical at all three seeds (155 / 152). The componentwise test's own MDE is roughly **2×** the
scalar's per component (0.0175 against 0.0085 on the decisive pair), and the POSITIVE control shows
the cost directly: a one-component plant needs **δ = 0.05** to fire and returns nothing at 0.02.

## ⭐ E3 · THE ADMITTED SETS DIFFER — AND THE DIFFERENCE IS A LOSS

| clause ② built on | admits |
|---|---|
| the scalar | **14 named arms** |
| componentwise | **11 named arms** |
| the symmetric difference | **`topw_k4`, `topw_k4_detA`, `topw_k4_detB`** |

The decomposition changes the definition's output — but only by **dropping the three arms nearest
the released core**, never by admitting anything new. *A formulation that differs from the incumbent
solely by losing power is not a better formulation.*

## ⚠ WHAT THE COMPONENTS *DO* SHOW, HONESTLY SCOPED

`coval_core` − `generic` resolves on the scalar (`t` 3.96) and componentwise on **2 of 6**:

| | AB | AC | AD | BC | BD | CD |
|---|---|---|---|---|---|---|
| `t` | 1.80 | **3.47** | 1.23 | 0.70 | 1.54 | **3.20** |
| | — | **SURVIVES** | — | — | — | **SURVIVES** |

So the core's advantage over the prompt-blind baseline is carried by **AC and CD** and is unresolved
on the other four. That is a real refinement of a claim R789 stated as a single number — and it is
worth exactly as much as World C allows, which is a description of where one effect sits, not a new
axis.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | D1 identity \|mean of six components − A2\| worst **1.11e-16**; scalar `t` against R789's committed matrix worst **1.07e-14**; 20 objects, 968 prompts, 6 components | PASS, else exit 2 |
| PLACEBO | the 9 alias pairs: worst component effect **exactly 0.0** | PASS — expected value fixed by D4 before the run |
| POSITIVE | plant on component AB only: δ=0 → **0** components fire (the floor fails, as required) · 0.005/0.01/0.02 → 0 · **0.05 → AB alone** | PASS — band admissible **and component-SPECIFIC** |
| NEGATIVE | the gauge operation: permute the six component labels within each prompt → **A2 unchanged to 2.2e-16** (a derivation, checked) while the largest component effect moves **0.021265** | PASS |
| NEGATIVE (synthetic) | an arm with i.i.d. component noise and no structure: **0 of 6** resolve | PASS |
| SHAM | the machinery minus the decomposition — the scalar alone: 155 pairs against 152 | ⭐ **the ingredient's removal makes it stronger** |
| NOISE FLOOR | annotator split-half, 20 draws, 968 prompts: AB 0.006317 · AC 0.005018 · AD 0.006572 · BC 0.005035 · BD 0.005624 · CD 0.005867 | ⚠ MARGINAL — see below |

⚠ **The noise floor is per-ARM and marginal; every effect above is a PAIRED difference in which the
annotator draw is common to both arms.** R790's unit note applies unchanged: the two may not be
compared directly. It bounds the per-arm component estimate, not the pair. **It was nearly shipped as
dead code** — the first draft's loop multiplied by `0.0 * g` and returned nothing while printing a
line; it is now measured from the stored sign matrices.

## MULTIPLICITY

**1,140 componentwise cells** (6 × 190) and **190 scalar cells**, BH at q=0.05 over each family's own
whole grid. Surviving: 855 componentwise cells across 152 pairs; 155 scalar. Non-survivors: 285 cells
and 38 pairs componentwise, 35 pairs scalar. Pre-multiplicity counts published beside them
(ci_only 167 vs 161, strict 152 vs 155, conservative 138 vs 145) precisely because D2 makes the raw
comparison arithmetic.

## WHAT DIED

- **R790's NEXT as a direction** — "clause ② should not be a scalar comparison" is not supported: the
  finest decomposition available is 99.36% one direction and resolves fewer pairs.
- **the hope that `coval_core` and `topw_k4` differ somewhere** — they do not, on any of the six
  comparisons, at any sign.
- **a NOISE FLOOR that computed nothing** while printing a line, caught before the run shipped.
- **reading a verdict off the screen** — the ⭐ line printed directly beneath a *different* pair's
  component block, whose CD component does survive. The decisive pair was re-read from the artifact.

## WHAT SURVIVES

The scalar. After four rounds attacking its threshold and one attacking its dimensionality, A2 with
a stated comparison is what this release supports — and R789's `coval_core` − `generic` = +0.01512
now carries a componentwise location: **AC and CD, not the other four.**

## SCOPE

population 20 distinct objects (27 named arms, 9 alias pairs collapsed) × 968 prompts × 6 components
· instrument per-(prompt, component) agreement with the annotators' class, paired mean difference ·
baseline the scalar A2 test, the incumbent clause ② · NBOOT 1,200, 3 seeds · regime first release,
home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether a component difference MATTERS to a reader | an external criterion for what clause ② should admit — the construct-validity wall (R631) |
| a decomposition finer than the six comparisons | graded judgements rather than pairwise signs; the release ships signs |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

Five formulations have now been tried and the axis has been attacked at its threshold (R787–R790)
and at its dimensionality (R791), with the same result each time: `coval_core` is not separable from
`topw_k4`, whose criteria are chosen by importance weight alone. Computed by this round's `run.py`,
the first eigenvalue takes 0.9936 of the component variance, so no reweighting of these six
comparisons will separate them either. The remaining move is not another statistic on this
release — it is to ask what the released core is supposed to be *for*, given that a
top-weight-`k`=4 selection reproduces it within 0.0023 of A2 and within resolution on all six
components. That is the construct question R631 registered as impossible here, and this arc has now
spent five rounds establishing that everything upstream of it is settled.
