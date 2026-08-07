# R557 · Row 1 measured identity where the requirement was recoverability

**Decision this makes safe:** whether ③′ on the released core needs the publisher at all.

**WORLD B.** Similarity matching, per prompt, over **968** prompts and **3,828** core items:

| control | result |
|---|---|
| **POSITIVE** — top-1 on the 298 items whose source is known verbatim | **1.0000** |
| **PLACEBO** — a different prompt's rubric matches at least as well | **0.0000** |

| | median top1−top2 margin | n |
|---|---|---|
| KNOWN | **0.8035** | 298 |
| UNKNOWN (the rewrites) | 0.3101 | 3,530 |
| **clearing the KNOWN set's 10th percentile** | **21.0%** | — |

⭐⭐⭐ **The row named an OBJECT — the field `source_rubric_item_ids` — where the requirement is a
PROPERTY: a recoverable mapping.** And its evidence, *"only 6.6% verbatim"*, is an **identity**
measurement on an object the dataset card documents as a **rewrite and merge**. An exact-match
instrument cannot see a rewrite; that is what a rewrite is.

⚠ **21.0% is a BOUND on identifiability, not an accuracy.** No ground-truth mapping exists — **that
absence is the row** — so accuracy is identified only on the verbatim subset. **Partial
identification licenses bounds, never a point.**

⚠ **My verbatim share is 7.8% (298/3,828); the row says 6.6%.** My normalisation is strictly more
permissive, so a larger share is consistent, not contradictory. Both reported.

**Net:** the row's price is right for a **complete** mapping and wrong for the **requirement**.
Partial recovery costs nothing here; the publisher's field remains the only route to completeness.
