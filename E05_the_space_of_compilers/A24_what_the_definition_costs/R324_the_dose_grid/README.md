# R324 — the dose grid, and the decomposition closes

**Decision this makes safe:** whether anything structural is still unpriced between A23's four
detectors. **Nothing is.**

## The isolation the other rounds could not do

Both coarse grids are **exact subsets** of R274's — 0.01 and 0.02 are multiples of 0.005 — so the
grid varies with the **curve, rule, replicates and tau all held byte-identical.** No resampling
enters; these numbers are exact given R274's curve.

| grid | n | bracket | vs committed |
|---|---:|---|---|
| R274 (0.005, max 0.20) | 41 | **[0.105, 0.125]** | +0.000 / +0.000 |
| R268 (0.02, max 0.20) | 11 | [0.120, 0.140] | **+0.015 / +0.015** |
| R267 (0.01, **max 0.12**) | 13 | [0.110, **None**] | **upper end undefined** |
| *degenerate {0, 0.2}* | 2 | [0.200, 0.200] | *(control)* |

**Step sweep:** `0.005:[0.105,0.125] · 0.01:[0.11,0.13] · 0.02:[0.12,0.14] · 0.025:[0.125,0.125] ·
0.05:[0.15,0.15]`

**W-GRID-MATTERS.** A published grid moves an end by up to **0.015**, above the pre-registered
0.010 threshold — and **R267's grid produces no upper end at all**, because it stops before the CI
lower bound reaches 0.8. That is stronger than "coarse": one end is *undefined*.

## Controls

| control | result |
|---|---|
| **positive** — full grid reproduces R274's committed bracket exactly | `[0.105, 0.125]` |
| **knob alive** — a non-full grid must differ | it does |
| **negative** — a 2-dose grid must not return the fine answer | gives `[0.200, 0.200]` |
| placebo | full grid against itself: zero by construction, labelled a derivation not a check |
| noise floor | **none is resampled, and that is the point** — with the curve fixed this round has no sampling noise; R322's replicate spread is the floor that matters and is quoted, not re-run |

## ⚠ The verdict quoted from the wrong population, and I caught it

The first computation swept the **degenerate control** into the published-grid statistic, so the
verdict said *"a published grid moves an end by up to 0.095"* — 0.095 being the 2-dose control.
**Fourth time this session a verdict quoted a number from a population the claim did not name.** The
fix is the same each time: name the population **in the code**, not in the prose.

## ⚠ R267's grid stops at 0.12; the one effect it calls resolvable is 0.1680

It never measured detection there — **it divided**, and its own output labels that section
*"A DERIVATION, not evidence"*. Not a defect. But a grid whose maximum sits below the largest
published effect can never do anything else, and that is a property of the grid worth pricing here.

## The A23 spread, fully decomposed

| component | round | effect |
|---|---|---|
| two **estimands** (point crossing vs CI containment) | R321 | on identical data the rules agree |
| **replicates** | R322 | CI lower end falls, upper does not; tau invariant |
| **threshold** = calibration size | R323 | 200 vs 3000 draws, exact to six decimals |
| **dose grid** | R324 | up to 0.015, and one end undefined |

## What this cannot say

**Which grid is right.** A finer grid localises the crossing better and costs replicates per dose
at a fixed budget. That trade is a design choice this round prices and cannot adjudicate.
