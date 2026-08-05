# R532 · The ③ fork, priced: it forbids an operation worth +0.0748 in A2

**Decision this makes safe:** what choosing ③-any over ③-rank actually costs, in the benchmark's
own units.

## ⛔ First — my last closing line pointed at a retired clause

`d99f45a` closed proposing an audit of `random_k4_s0` *"because clause ① compares every arm against
it."* **Clause ① was retired eight rounds ago (R516/R519).** The comparator still matters — but for
this reason instead: **`coval_core`'s +0.0738 over it is the number that prices the fork**, and R531
found that comparator uses the **same criterion indices for every prompt**. One draw reused, not a
per-prompt draw.

## Result — WORLD A

| comparator | baseline A2 | advantage |
|---|---|---|
| **fixed-index** `random_k4_s0` (published) | — | **+0.0738** |
| true per-prompt draw, seed 0 | 0.4902 | +0.0763 [+0.0665, +0.0859] |
| seed 1 | 0.4891 | +0.0774 [+0.0679, +0.0864] |
| seed 2 | 0.4958 | +0.0707 [+0.0615, +0.0805] |
| **mean of 3 seeds** | | **+0.0748** (spread 0.0030) |

**Ratio to the published figure: 1.01×**, against a pre-registered kill at 0.50×.
⭐ **The fixed-index comparator did not inflate anything.**

## Controls
- **Positive** — the fixed-index contrast must reproduce R294's stored `c1` for `coval_core`:
  **+0.073790 vs +0.073790.** PASS, so both comparators are on one scale.
- **Negative** — the per-prompt draw must actually vary across prompts: **True**, where
  `random_k4_s0` is **False** (R531). PASS.
- **Noise floor** — 3 seeds, spread **0.0030** against a per-cell MDE of ~0.0136.

## What it means for the formulation

⭐⭐⭐ **③-any forbids an operation worth +0.0748 in A2** — selecting rubric items by their
annotator-assigned weights rather than at random.

**Set against R530's measurement that the ③-any world is 1.29 MDE (≈0.0153) from non-empty, the
forbidden operation is worth roughly 5× the gap.** So ③-any is not marginally restrictive: **it
removes the largest single source of advantage a ③-rank core has.**

⚠ **Which reading is right remains register row 7 — a decision about purpose.** This round prices
the choice; it does not make it.

⭐ **And a flag of mine that turned out not to bite:** R531's fixed-index finding is a real property
of the comparator and **did not bias this number**. Worth stating plainly, having raised it.
