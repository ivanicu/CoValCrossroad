# R423 · was R422's 0.1 % a second judge, or my own join key?

**The decision this round makes safe:** whether R422's `W-DIFFERENT-EMITTER` may be acted on. It may
not — and the round that says so is the one that measured it, not a later one that inherited it.

## The repair, which is the instrument and not a patch

`select_core.py` emits `sat[pid][(i, letter)]` keyed on the criterion's **original index**; R422 keyed
on its **text**. **82 of 968 prompts (8.5 %) repeat a criterion text**, so the key names a *set* of
values and R422's dict kept an arbitrary member. Two files agree at that key when their sets
**intersect**; they disagree only when the sets are **disjoint**.

| rule | shared | R422 "differing" | **disjoint after repair** |
|---|---|---|---|
| `oracle_k4` | 8,180 | 5 | **2** |
| `greedy_k4_fit1` | 7,868 | 9 | **0** |
| `indep_k4_fit1` | 7,516 | 11 | **1** |
| `topvar_k4` | 7,044 | 14 | **0** |
| `topwvar_k4` | 7,760 | 13 | **0** |

**The two families agree with each other at ≤ 0.03 %.** The duplicate-text hypothesis is measured,
not asserted.

## Controls — all four passed, and two of them earned their place

| control | returned |
|---|---|
| g = 0 · a value from the multiset is contained | PASS |
| CONTAIN (+) · a synthetic `value + 1.0` is not | PASS |
| **REAL (=)** · `topw_k4` vs `topw_k2` still **0 disjoint of 7,728** after the repair | PASS |
| **DEFAULT-NPZ** · every `topw_k4` value contained: **15,440 of 15,440** | PASS |

`REAL (=)` is a **regression test**: a repair that fixes the failing case by breaking the passing one
has moved the error, not removed it. `DEFAULT-NPZ` is what establishes that `core_full.json` +
`sat_full.npz` **is** the default emitter's table — containment against the wrong table would pass or
fail everything with equal confidence.

## ⛔ And the column added as an afterthought is the finding

**~29,700 values per rule are absent from the default table — for *both* families.** So the question
this round built three worlds around (*did the judge differ between them?*) answers **no**, while the
question it never asked (*is either of them the default judge at all?*) answers **also no**.

**The printed `W-MIXED` is a mis-read, and the branch is only half the reason.** The condition mixed
two estimands — *agreement between families* and *agreement with the default* — into one boolean. The
deeper fault: **my three worlds had no cell for "same as each other, foreign to the default."** The
decomposition was wrong, so the branch had nowhere correct to land. That is the meta-separator firing
on the **world set**, not on the code.

⛔ **And `29,742 uncontained` is a count without its denominator, which is not a rate.** The ledger
has an entry for exactly this and I shipped it anyway. R424 prints the denominator with every count.

→ the identification: [`R424`](../R424_name_the_foreign_emitter)

Findings, with their scope, live in the top-level README. This file states the design.
