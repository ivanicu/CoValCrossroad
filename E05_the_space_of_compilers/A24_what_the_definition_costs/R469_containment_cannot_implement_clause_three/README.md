# R469 · containment is **constant on ③'s partition** — it cannot implement ③, and that is a derivation

**The decision this round makes safe:** whether the 19-arm UNKNOWN region is decidable.
**Not by this instrument, and provably so.** `W-DEGENERATE`.

## ⛔ Rung 1 killed the announced confusion matrix twice, at zero compute

R468 closed proposing *"the selector verdict as reference, containment as candidate, report the
confusion matrix."*

1. **Unit mismatch.** The selector verdict is per **arm** (101 values); containment is per **prompt**
   (968). The matrix is ill-typed — §4's unit-equality, this time in my own announced plan.
2. **And at arm level it is FORCED.** Every selector in `select_core.py` draws from the prompt's own
   rubric — the ③-**excluded** ones (`oracle_k`, `indep_k`, `greedy_k`, `topw_k`, `topabs_k`,
   `topwvar_k`) **and** the ③-**admitted** ones (`random_k`, `full`, `topvar_k`). **So containment is
   ~1.0 for both classes by construction.**

*Thirty-seventh announced step checked; killed on both counts before any compute.*

## The derivation, confirmed rather than asserted

| ③'s verdict class | n | mean containment | sd | range |
|---|---|---|---|---|
| **EXCLUDED** | 39 | **0.9744** | 0.1581 | [0.0000, 1.0000] |
| **ADMITTED** | 43 | **0.9767** | 0.1507 | [0.0000, 1.0000] |
| UNKNOWN | 7 | 0.0002 | 0.0004 | [0.0000, 0.0013] |

> **Separation = −0.0023.** Containment is essentially **constant on ③'s own partition**.

**So containment does not merely fail to validate against ③ — it is *provably unable to implement
it*.** ⭐ That converts R466's `UNVERIFIED` from *"not yet decided"* into **"not decidable by this
instrument"**, and makes the definition's **third verdict permanent** for the UNKNOWN region rather
than provisional.

⭐ **And the UNKNOWN class at 0.0002 is the mechanism made visible**: those arms are the ones *not*
built by a rubric selector, so they share almost nothing with the rubric — which is exactly why the
selector-based instrument cannot classify them and the text-based one puts them all in one bucket.
**Two instruments, and the arms neither can separate are the same arms.**

## Controls

| control | returned |
|---|---|
| **ANCHOR** — `coval_core` reproduces its committed containment | **0.0778** vs **0.0779** ✅ |
| FLOOR — cross-prompt sham | **0.0000** ✅ |
| **POSITIVE** — `full`, every rubric criterion | **0.9999** ✅ *without it, a low number is silence* |
| g=0 — an arm against its own texts | 1.0 **by construction** — a DERIVATION |
| SPREAD | printed within each class: a class mean of 1.0 with **zero** spread would be a derivation; sd 0.15 makes it a measurement |

## ⛔ The anchor as designed was unavailable, and the round exited 2 rather than proceed

It was to read the core's texts from the **ranking** space and the rubric from the **rubric** space,
so reproducing 0.0779 would have validated R468's join a **third** time on a third channel. **There is
no `core_coval_core.json`** — the released core's texts exist **only** in
`conversation_rubrics.jsonl`, in rubric space.

**So the anchor runs *within* one space: it validates the instrument and *not* the join.** Weaker than
designed, stated as such rather than quietly re-labelled — and the first version **exited 2** rather
than run a measurement whose anchor could not fire.

## What this closes

- **R466's UNVERIFIED is now characterised**, not resolved: the containment instrument is
  *structurally* incapable of deciding ③, so no amount of care with it will help.
- **The definition's third verdict is permanent** for the 19 UNKNOWN arms unless a *different*
  instrument is built.
- ⚠ **It rules out one instrument.** Another would need its own round — and this round says so rather
  than generalising, which is the exact error R466 and R467 made and R468 caught.

## Impossible here, named

- **ruling out every possible ③-instrument** — this rules out one, by showing it constant on ③'s
  partition.
- **classifying the UNKNOWN arms** — precisely what this round shows containment cannot do.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
