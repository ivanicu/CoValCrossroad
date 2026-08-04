# R407 — at the maximum blind set, the only survivors are the arms that read the answer

**The decision this makes safe:** *does anything satisfy clause ② read as a universal?* **Under the
strict test: nothing label-free. And the literal test has never been run.**

## Result — `W_UNIVERSAL_EMPTY`. Three controls pass. **No GPU, no run of the object.**

| p = 100 (the per-k **maximum** blind set) | |
|---|---|
| admitted | `greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4`, `oracle_k4_fit1` |
| of which **read the prompt's own rankings** | **all four** |
| **label-free admitted** | **∅ (n = 0)** |

## ⛔ R405 blocked the ordering claim correctly — and blocked a weaker one with it

*"No label-free arm beats the maximum blind set of its own size"* is a statement about **one cell**.
It needs the cell's reference to **be** that maximum — **not** the cells to be ordered by strictness.
**No monotonicity is used anywhere in this round.**

**And the reference is verifiable from source without a run.** `ref_at(k, p)` sorts the blind sets of
size *k* by mean and indexes `round(p/100·(len−1))`, so `p=100` returns `order[-1]` — the single
highest-scoring prompt-blind set **of that arm's own size**, which is the literal referent of *"every
prompt-blind set of that size"*.

## ⭐ Per-arm brackets — reported at arm resolution for the first time

| arm | last admitted at pct | |
|---|---:|---|
| `topw_k8` | 95.0 | |
| `topw_k3` | 95.5 | |
| `topw_k4` | 98.0 | |
| **`coval_core`** | **99.5** | **gone by 100.0** |
| `topw_k6` | 99.5 | gone by 100.0 |
| the four label-readers | **100.0** | still in at the maximum |

> **The released core clears the 99.5th-percentile blind set and does not clear the maximum.** That is
> a *grid position*, not a strictness ordering, and not a point — the grid has 45 rungs.

## ⛔ The fourth under-specification in clause ②

R360's `admits` is **`e > 0 AND |e| ≥ ZEFF·se`** — *significantly* better. **The definition says
"scores better than."** The coded test is **stricter**, and the gap runs in the direction that makes
the definition look **more demanding than it reads**.

> So this answers the **strict** universal reading. **The literal one — `e > 0` alone — has never been
> run**, and is deliberately not approximated here.

**Clause ② has now yielded four distinct under-specifications:** ① it names a class and no member
(R327) · ② held-out vs in-sample (R405) · ③ a p99 bar called *every* (R406) · ④ **"better" implemented
as "significantly better"** (this round).

## Controls

| | returned |
|---|---|
| **SOURCE (+)** | the index expression at `p=100` over n=1,820 returns element **1,819** (the last) — `PASS`. **Executed, not asserted** |
| **SOURCE (−)** | the same expression at `p=0` returns element **0** — `PASS`. Without it, an expression always returning the last would pass (+) |
| **EXPRESSION** | R360's line is present **verbatim** in its source — `PASS`, so I am not checking arithmetic R360 does not do |
| **ORDERING-FREE** | asserted by construction and recorded in the artifact: `monotonicity_used = false` |

## ⚠ And one cross-check is OWED, not done

Confirming `ref_at(4,100)` equals R331's committed max `0.5574753088` needs R360's `build(k)`, which
loads and scores. **The source-level check stands in for it and is weaker.** Recorded as owed rather
than quietly skipped.

## Register

| criterion | status |
|---|---|
| **the literal `e > 0` test** | **NOT RUN** — needs R360's arrays. Named as the next step, not approximated |
| **numeric cross-check of `ref_at(4,100)`** | **OWED** — source-level check substituted |
| **a point estimate of any arm's percentile** | **N/A** — 45-point grid; bracketed |

## The sentence I can no longer write

> *"the core is better than every prompt-blind set of its size"* — **under the strict test it is not,
> and the only arms that are read the answer.** What remains open is whether it clears the literal
> test, and that is one run away rather than unknowable.

Artifact: `results/r407_universal_reading.json`, source-stamped.
