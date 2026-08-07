# R1036 — which q is **scale-free**? A max inflates with family size; a quantile does not

**The decision this round makes safe:** which quantile the clause can carry. R1035 closed by asserting
the curve **cannot** select among q ∈ {50…99}. **That was wrong, and it is withdrawn** — a criterion
exists, and it is not another q-sweep.

## ⛔ The precedent is R848's, cited not claimed

For clause ④, R848 ran a **dose-response over family SIZE**, with `real_sd` per size and
`seed_changes_subset: True`, and measured the bar rising at **0.0074 per ln(n)** — the signature of a
**maximum**, which grows as you enlarge the family. ⭐ **A quantile has no such drift.** So
**scale-stability selects q**, and the new part is applying the device to *select a quantile* rather
than to *price a bar*.

## The n × q grid — 3 bootstrap × 3 family seeds must agree

| n | q=0 | q=50 | q=75 | q=90 | q=95 | q=99 | q=100 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 73 | 12 | 12 | 11 | ⚠ | ⚠ | ⚠ |
| 300 | 73 | 12 | 12 | 11 | 9 | ⚠ | ⚠ |
| 1000 | 73 | 12 | 12 | 11 | 9 | ⚠ | ⚠ |
| 2000 | 73 | 12 | 12 | 11 | 9 | 8 | ⚠ |
| 4261 | 73 | 12 | 12 | 11 | 9 | 8 | 0 |

## ⭐ Scale-freeness is **not binary** — it has an **onset size that grows with q**

| q | onset n | \|ext\| there |
|---:|---:|---:|
| 0 | 100 | 73 — ⚠ **degenerate: no requirement** |
| 50 | **100** | 12 |
| 75 | **100** | 12 |
| 90 | **100** | 11 |
| 95 | **300** | 9 |
| 99 | **2000** | 8 |
| 100 | **—** | ⚠ **never stabilises** |

**So the clause's cost is not a threshold but how much family you must enumerate to state it** — and
**q=100 cannot be stated at any size reached here.** That is the max-over-search, seen as a *rate*
rather than a cliff.

## Controls

- **POSITIVE ②** — **nesting checked, not assumed**: each family is a strict subset of the next
  (prefixes of one shuffled family), so "growing the family" is not "drawing a different one":
  **PASS**.
- **NEGATIVE** — the q=100 column must **move** with n (the R848 signature): **PASS**.
- **PLACEBO** — within a fixed family seed, n=1 makes every q>0 the same requirement: **PASS**.
  ⚠ **My first version compared *across* family seeds and failed for its own reasons** — at n=1 the
  seed picks *which* comparator, so disagreement is guaranteed. Ill-posed, replaced.
- **SEEDS** — 3 bootstrap × 3 family shuffles; a cell is reported only if all nine agree.

## ⚠ Two defects of my own, both caught by reading the grid

1. **`min(flat_q)` returned 0** — and q=0 imposes **no requirement**, admitting 73 arms. *The
   verdict-string mode: `min()` over a set containing a disqualified element.* q=0 is now excluded
   explicitly.
2. **q=100 first "stabilised" at n=4261** — on a tail of **length 1**, which is trivially constant.
   The onset rule now requires **at least two sizes** to agree.

## What this cannot say

**Scale-stability is necessary, not sufficient.** A q can be size-independent and still be the wrong
bar. Deciding that needs an external criterion for what the comparator family **represents**, which
this release does not carry. **N/A, stated not planned.**

`run.py` · `results/scale_free_q.json`
