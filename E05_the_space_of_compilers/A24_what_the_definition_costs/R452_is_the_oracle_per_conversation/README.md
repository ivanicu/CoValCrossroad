# R452 · the oracle is a **fixed better subset**, not per-conversation selection

**The decision this round makes safe:** what R451's oracle ceiling of 1.0000 actually demonstrates.
**Largely a fixed prompt-blind subset plus max-of-N inflation.** `W-FIXED`.

## ⛔ Rung 2 killed the announced statistic before any compute

R451 closed proposing to compare the oracle against **the best fixed subset**. The oracle is `argmax`
over **C(16,4) = 1,820** candidates per prompt, and a max of 1,820 draws exceeds the best fixed draw
**even with no per-prompt information at all** — the winner's curse. *Twentieth announced step
checked, its statistic killed.*

Reported so it cannot be mistaken for a result:

| | |
|---|---|
| oracle mean A2 | 0.6610 |
| best **fixed** subset | 0.5618 |
| difference | **+0.0992** ← **DERIVATION, not evidence** |

## ⛔ And rung 1 then killed *my* replacement estimand

Both permutation nulls came back **above** the real oracle (N1 = 1.0000, N2 = 0.9309). Diagnosing
that rather than discarding it:

1. **`oracle_mean = mean_p max_j A[j,p]` is invariant under permutation of prompt labels** —
   permuting columns does not change the multiset of column maxima. **So no permutation null exists
   for it**, and `EXCESS vs a permutation null` was mis-specified from the start.
2. Both nulls **destroy the inter-subset correlation**, and that correlation is exactly what holds
   the max away from the ceiling. Made independent, **N1 saturates at 1.0000** — *a control that
   cannot PASS*, built again.

## ⭐ The un-forced fact needs no null to state

| | |
|---|---|
| effective distinct winners | **57.8** of 1,820 (**3.2%**) |
| top-1 subset's win share | **0.3357** vs uniform 0.00055 (**611×**) |

**One single prompt-blind subset wins a third of all 968 prompts.**

## The correct null: a synthetic pool with no per-prompt structure

Criteria get a **fixed** quality with no prompt dependence, assembled through the **identical**
C(16,4) combinatorics so the overlap correlation is reproduced exactly.

| | eff-winners | top-1 | sd(A) |
|---|---|---|---|
| **real** | **57.8** | **0.3357** | 0.1978 |
| synthetic, no structure | 185.7 | 0.1273 | 0.1932 |
| ratio | **0.311** | **2.64×** | *calibration 0.98* ✅ |

> **The real oracle is 3.2× MORE concentrated than no-structure combinatorics produces.** Per-prompt
> structure would push concentration the *other* way.

## Controls, and the honest weakness of one of them

| control | returned |
|---|---|
| CALIBRATION — synthetic on the real scale | sd ratio **0.98** ∈ [0.5, 2.0] ✅ |
| POSITIVE — plant a different favoured criterion per prompt | 190.3 vs 185.7 ✅ **direction only** |
| g=0 — the no-structure synthetic itself | 185.7 |

⚠ **The positive control is weak in magnitude: a large plant (δ = 3.0) moved eff-winners by only
+2.5%.** So this statistic is *poorly sensitive to per-prompt structure in the spreading direction*.
**The conclusion does not rest on that direction.** It rests on `real (57.8) ≪ no-structure (185.7)`,
and concentration *below* the no-structure baseline can only mean some subsets are genuinely better
**across** prompts. Stating which half of the instrument the inference uses is the point.

## What this changes

- **R451's oracle control STANDS** — a disjoint object *can* be admitted, at 1.0000.
- **Its interpretation NARROWS.** What that control demonstrates is largely **a fixed better subset
  of generic criteria**, not a per-conversation core. `per-conversation` overstates the oracle.
- **And that sharpens a circularity already flagged.** If a *fixed prompt-blind* set sits near the top
  of the prompt-blind class, clause ② is a **within-family ranking** where it was meant to be a
  prompt-specificity test — the same objection R451 raised about `generic` at 0.7154, now with a
  mechanism behind it.

## Impossible here, named

- **separating conversation content from the annotator draw** — needs multiple independent draws per
  conversation scored separately; the 3-draw design does not support it.
- **whether a per-conversation oracle is achievable without hindsight** — R451 measured that our one
  generator is not. This round says only what the ceiling is worth.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
