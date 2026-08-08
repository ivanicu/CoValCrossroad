# R1086 — `q buys 2 arms` is a **distribution**, not a value. In **27.5%** of families it buys nothing.

**The decision this round makes safe:** whether R1057's KEEP of `q` rests on a representative
measurement. **The decision survives; the number does not.** `q` buys 2 at the mode of every family
size where it can act — and it buys 0 in 825 of the 3003 families at `k = 10`.

## What R1057 actually did, read from its code rather than its README

```python
Cc = C[:k]      # the lexicographically FIRST k of the 15 blind subsets
```

The three "seeds" reseed the **bootstrap**, never the family. So the composition axis had exactly one
cell — and `itertools.combinations` orders by subset **size**, so `C[:10]` is the 4 singletons plus 6
pairs: the smallest comparators in the space. **At `k = 10` there are C(15,10) = 3003 families and
they are fully enumerable, so no sampling was ever needed.**

## The whole family space — 4944 families, none summarised away

`delta(F) = |admitted by q=90| − |admitted by every-comparator|`

| k | families | min | **mode** | max | mode share | distinct values | R1057's `C[:k]` |
|---:|---:|---:|---:|---:|---:|---:|---|
| **10** | 3003 | **0** | **2** | **7** | 65.7% | **7** | 2 (≤ 98.0% of families) |
| 11 | 1365 | 0 | 2 | 4 | 72.8% | 5 | **0** (≤ 24.2%) |
| 12 | 455 | 0 | 2 | 3 | 79.8% | 4 | **0** (≤ 19.3%) |
| 13 | 105 | 0 | 2 | 2 | 86.7% | 2 | **0** (≤ 13.3%) |
| 14 | 15 | 0 | 2 | 2 | 93.3% | 2 | **0** (≤ 6.7%) |
| 15 | 1 | 2 | 2 | 2 | 100.0% | 1 | 2 |

**Full distribution at k = 10:** `{0: 825, 1: 144, 2: 1974, 3: 46, 4: 10, 5: 3, 7: 1}`

⭐ **World A (a value) is KILLED.** `delta` takes **7 distinct values spanning [0, 7]** at `k = 10`.
**`q buys N arms` cannot be stated without naming the family.**

⭐ **And R1057's cell is unrepresentative in a `k`-dependent direction.** It sits at the mode for
`k = 10` and `k = 15` — the two sizes R1057 reported — and gives **0 where the mode is 2** at every
size in between. Its own README noted "nothing at `k = 12`" and read that as a property of 12; it is
a property of *that family*, which only 19.3% of families at `k = 12` match or fall below.

## What survives, and it is the decision rather than the number

**KEEP still holds.** The mode is **2 at every size where `q` can act**, and at `k = 15` — the single
complete family, where there is nothing to choose — `delta = 2` exactly. `q` is a live parameter
awaiting a live family. **What is withdrawn is the point estimate:** the clause's justification must
read *"2 at the mode, 0 in 27.5% of families at k=10, spanning 0–7"*, not *"2"*.

## Controls — 8, all green, and one was rebuilt

| control | result |
|---|---|
| DERIVATION CHECK the fast bootstrap equals the direct one on sampled pairs | PASS |
| g=0 `delta = 0` for **every** family at `k ≤ 9` (the algebra, reproduced) | PASS |
| POSITIVE an arm beating every comparator is admitted by both rules | PASS |
| POSITIVE an arm beating exactly `ceil(0.9k)` is admitted by `q` **only** | PASS |
| NEGATIVE relabelling the comparators leaves the **whole distribution identical** | PASS |
| NEGATIVE breaking the arm-comparator pairing **moves** the distribution | PASS |
| SHAM `k` copies of one comparator gives `delta = 0` at every `k` | PASS |
| PLACEBO both rules at `q = 100` gives `delta = 0` everywhere | PASS |

⛔ **The first NEGATIVE control failed for its own reasons — the fifth time in this arc.** It shuffled
each arm's row and asserted `delta` over the fixed family `range(k)` was unchanged, on the reasoning
that *"both rules depend only on the count."* They depend on the count **within the family**, which a
per-arm shuffle changes by construction. **The control was wrong; the instrument was not.** It is
replaced by the invariance that does hold — enumerating *every* family of size `k` is invariant to
relabelling comparators — plus its complement, that breaking the pairing must move the distribution.

**Noise floor:** 7 of 1500 (arm, subset) decisions are not unanimous across 3 bootstrap seeds; a beat
requires **all three**, so a family-level spread cannot be manufactured by one unstable pair.

⭐ **A derivation that made the enumeration free, labelled as one.** Under the same resample indices,
`mean_b(V_i − C_j) = mean_b(V_i) − mean_b(C_j)` by linearity — so R1057's per-pair resampling inside
its family loop (99 × 15 × 2000 × 968 gathers per seed) collapses to 114 gathers and 1485
subtractions. **This changes the cost, not the number**, and a control checks it against the direct
computation on sampled pairs.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| whether any of these families could be **certified** from the release | **N/A** | R1056 measured the certified family is 2 at every defensible threshold; these are synthetic and the round claims nothing about the shipped family |
| `k > 15` | **N/A** | more than 4 universally-available criteria; `2⁴−1` is a hard cap |
| cross-release | **N/A** | a second release with its own blind space |

`run.py` · `results/q_value_or_draw.json`
