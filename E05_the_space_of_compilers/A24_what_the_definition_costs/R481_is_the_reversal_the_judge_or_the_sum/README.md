# R481 · Is R480's size reversal the judge, or the SUM nobody chose deliberately?

**The decision this made safe.** Every A2 in this campaign routes through `score.py:63` — a plain
**sum** over selected criteria, chosen once and never swept (`/yvec/` and `/sum/` both return 0 in
DEFINITION.md). A sum's variance grows with k, so a k-gradient is exactly where an aggregation
artifact would hide. **The reversal survives 2 of the 3 aggregators that can see k at all.**

## Half the sweep was void by algebra

`mean = sum/k` with k fixed within a prompt, and `cls()` reads **signs of differences** — invariant
under positive scaling. **`cls(mean) ≡ cls(sum)`**, confirmed 2000/2000 on random matrices. So MEAN is
not a specification; it is used here as a **positive control on the implementation** — an identity the
code must reproduce and a buggy pipeline breaks. It returned **0.00e+00** across 26 arm×judge cells.

⭐ **And that control immediately earned its keep**: the synthetic null's first version printed
`sum = +0.4176` and `mean = −0.4790`. Two algebraically identical numbers disagreeing meant the
control itself was broken — a shared generator consumed in aggregator order, so each aggregator saw
different random data. **A control validating the harness fired on a defect in another control.**

## corr(k, A2) — all 24 sign cells

| agg | topw 2B | topw 0.8B | rev | rand 2B | rand 0.8B | rev |
|---|---|---|---|---|---|---|
| sum | +0.0558 | −0.4458 | ⛔ | **+0.8695** | **−0.4979** | ⛔ |
| mean | +0.0558 | −0.4458 | ⛔ | +0.8695 | −0.4979 | ⛔ |
| max | −0.7614 | −0.8650 | ok | +0.6393 | +0.5609 | ok |
| median | +0.0625 | −0.5899 | ⛔ | +0.8542 | −0.2602 | ⛔ |
| min | −0.8077 | −0.9879 | ok | −0.8687 | −0.8635 | ok |
| midrange | −0.4498 | −0.4960 | ok | −0.4785 | −0.5302 | ok |
| constant | 0.0000 | 0.0000 | ok | 0.0000 | 0.0000 | ok |

## The null that was nearly counted as evidence

*"Reversal absent under max, min, midrange"* reads as three disconfirmations. **Two of them cannot
resolve k at all.** A2 range across the k-ladder, real data:

| | sum | median | min | **max** | **midrange** |
|---|---|---|---|---|---|
| 2B | 0.0250 | 0.0332 | 0.0204 | **0.0084** | **0.0086** |
| 0.8B | 0.0046 | 0.0184 | 0.0182 | **0.0059** | **0.0077** |

`max` reports only the single best-satisfied criterion, so it **cannot see accumulation**; both it and
`midrange` move less than the 0.0122 floor. **A null from a blind instrument is silence, not an
acquittal.** Correct denominator: **2 of 3 seeing aggregators**, not 2 of 5.

## Two specification axes, both reported whole

**① Aggregator** — reversal under `sum` and `median`; absent under `min` (which sees k fine and
genuinely disagrees). **② Arm set** — R480 used 18 random arms (6 budgets × 3 seeds):

| arm set | n | 2B | 0.8B | reversal |
|---|---|---|---|---|
| `s0_only` | 6 | +0.9381 | **+0.0111** | no |
| `all_seeds` | 18 | +0.8695 | **−0.4979** | ⛔ yes |

**The sign flips with one seed per budget**, and the population is identical either way (968 prompts,
own-pop ≡ common-pop, verified). **R480 reported one cell of a two-cell sweep.**

## Why the synthetic null does *not* rescue the reversal

Spurious corr(k, A2) on structureless iid data: `sum`/`mean` **+0.4176**, `min` +0.3100, `median`
+0.2181, `max` +0.0125, `midrange` +0.0036, `constant` 0.0000. **`sum` — the committed choice — has
the largest mechanical gradient.** ⭐ **But it is a property of the aggregator, identical for both
judges, so it shifts both correlations equally and cannot create a sign difference between them.**
It explains levels, not the reversal.

## Controls

| control | returned |
|---|---|
| **POSITIVE ⭐ `A2(sum) ≡ A2(mean)`** — an algebraic identity | **0.00e+00** over 26 cells |
| NEGATIVE — criterion→response assignment shuffled | 0.4254 (chance 0.428) |
| PLACEBO — human rankings shuffled | 0.4297 |
| g=0 — constant aggregator manufactures no gradient | **0.0000** exactly |
| SYNTHETIC — structureless world, per-aggregator spurious gradient | reported above |

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R481_is_the_reversal_the_judge_or_the_sum/run.py

Compute-free · deterministic (crc32) · two-process byte-identical · `results/r481_aggregation.json`.
