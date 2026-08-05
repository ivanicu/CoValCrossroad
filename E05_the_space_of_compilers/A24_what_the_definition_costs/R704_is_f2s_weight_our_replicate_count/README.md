# R704 · is F2's weight our replicate count? — R703's premise, refuted

**The generator name is worth `+0.000` to F2 under the canonical `(family,k)` partition, and `+0.048`
at best across five partitions — two arms of 42, and no partition clears its own permutation null.
So F2's 20 unique exclusions are NOT "our parameterisation showing through": they are a COUNT, not a
signal. F2 excludes 33 of 42 arms, and a demanding clause produces many unique exclusions whatever it
encodes.**

Population **all 42 arms of R360's ledger** · instrument **leave-one-out cell-majority predictor over
a partition of the arm names** · baseline **the leave-one-out base rate + a 2000-draw label
permutation null** · regime **this repository at HEAD**.

## check #306 on R703's NEXT line

Counts CONFIRMED — 4 / 20 / 2 in `R703/results/load_bearing.json` field `rows`; R694's 95.2% at its
`README:26`. ⛔ But R703's own verdict string prints `str(r['unique'][:3])` (`run.py:120`) — three
members per clause, **no ellipsis, no count** — beside `n_unique: 20` in the same file. Third
occurrence of a display contradicting the artifact next to it (R690, R698, R703). Annotated onto
R703's README; the gate is deferred with its count rather than built blind.

## the admissible grid — gain over the base rate, all 42 arms

| clause | `(family,k)` | `family` | `k` | `(family,k,sham)` | single cell `[SHAM]` |
|---|---|---|---|---|---|
| F1 provenance | **+0.048** | +0.048 | +0.000 | +0.048 | +0.000 |
| **F2 behaviour** | **+0.000** | −0.071 | +0.000 | +0.048 | +0.000 |
| F3 size (repaired) | +0.262 | −0.262 | **+0.286** | +0.214 | +0.000 |

⚠ **F3's column is a DERIVATION, not a measurement.** F3 *is* the predicate `1 < k ≤ 4`, so a
`k`-partition must recover it exactly. Stated to name the mechanism, not offered as evidence.

30 cells tested (2 populations × 5 partitions × 3 clauses); **all reported**. BH q=0.10 over the whole
grid: 9 survive on the registered statistic, 10 on the repaired one — the per-cell lists, including
every non-survivor, are in `results/recoverability.json`.

## ⛔ both of my own statistics failed first, and a registered control caught each

**① The sham refuted my registered headline.** Cell-determined share reads **0.650** for the
treatment against **1.000** for the single-cell sham. §4: a sham above the treatment means the
statistic does not isolate the ingredient — under one cell *every* prediction counts as
cell-determined, so the category collapses exactly where it should read zero.

**② The registered population was outcome-conditioned.** I evaluated on each clause's *own* unique
exclusions. A clause excluding a majority then has base rate **1.000 by algebra**, and one excluding
a minority **0.000** — so `gain`'s sign is fixed before any data touches it. The `all 42 arms` rows
were added after the first run and are the admissible ones; the conditioned rows are kept and marked,
never deleted.

The repaired statistic got **its own** positive control and g=0, because a replacement proxy returns
numbers immediately and inherits nothing: planting `family=='random'` gives gain **+0.429** against
its null95 **+0.119** (fires), and an i.i.d. coin flip gives **+0.000** against **+0.143** (can fail).

## controls — 9 PASS, 0 FAIL

| control | returned |
|---|---|
| POSITIVE (share) | 0.714, with `floor 0.405 < t 0.560 < ceiling 0.714` — the band is real, so the threshold is both reachable and refusable |
| g=0 (share) | 0.286 < t — it can fail |
| POSITIVE (gain) | +0.429 vs null95 +0.119 |
| g=0 (gain) | +0.000 vs null95 +0.143 |
| NEGATIVE | cells shuffled at fixed sizes and majorities **refit** → 0.450 vs its own null95 0.600 |
| SHAM | single-cell partition — and it is what refuted ① above |
| PLACEBO | two identical runs differ by exactly 0 |
| UNIT | instrument unit `AN ARM` ≠ claim unit `A CLAUSE`, carried into the verdict |
| SEEDS | 3 nulls, means 0.4069 / 0.4137 / 0.4143 — the seed flag changes the draws |
| ARITHMETIC | `cell + fallback + wrong == n` in all 30 cells |

Two runs byte-identical.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** *(labelled DERIVED before the run)* | F2 cell-det 13 [6,18]; F1 2; F3 0 | **13 / 2 / 0**, error 0 |
| **B** | excess over null95 **+0.35** [+0.05,+0.65] | **+0.050** — inside only at the boundary, the point wrong by 7× |
| **C** | specs where F2 > F1 = 4 of 5 [1,5] | **4**, error 0 |
| directional | F2 > F3 in a majority of 5 | **4 of 5, HOLDS** |

**A was declared a derivation in `PREREGISTRATION.txt` before the code was written** — R360's ledger
prints the cells, so the split was recoverable by hand. It is a check on my arithmetic and licenses
nothing. **B is the honest miss**: I registered a large excess and got one arm's worth.

## limits

- `(family,k)` is **our** parameterisation of arms **we** built (carried from R694).
- Instrument unit is an arm, claim unit is a clause. At n=42 the resolution is **0.024 per arm**, so a
  gain under 0.048 is two arms: the cross-clause **ordering** is reported, the cross-clause
  **difference** is not.
- 13 of 13 arms the partition "determines" for F2 sit in cells made only of same-generator replicates
  or shams we shipped, and deduplicated to one arm per cell the cell contribution is 0 — **true, and
  moot**, since the base rate predicts them anyway. Recorded because it was this round's hypothesis
  and it did not survive contact with the right population.

## impossible here

| criterion | what it would require |
|---|---|
| cross-release | a second release with its own generator names |
| construct validity of "recoverable" | an external standard for what a generator name should encode |
