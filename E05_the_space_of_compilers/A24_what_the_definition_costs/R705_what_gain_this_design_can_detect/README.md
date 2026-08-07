# R705 · what gain can this design detect at all? — R704's `+0.0476`, priced against its own floor

**R704's `+0.0476` is resolvable in `1` of `6` specifications — and not in the one that matters. At
F1's base rate under `(family,k)` the design has power `0.807` at that value; at F2's it has `0.564`.
So a comparison between the two clauses is between a value this design can see and one it cannot,
which is not a comparison, and R704's F1-vs-F2 ordering is withdrawn.**

Population **the 42 arms of R360's ledger carrying SYNTHETIC labels** — the real labels are what is
being judged and cannot also be the measuring stick · instrument **count-preserving swap
dose-response, power against a nuisance-matched permutation null** · baseline **α = 0.05, power target
0.80, 2000 null draws, 400 replicates per dose cell** · regime **this partition, this n, this base
rate, and nothing else**.

## check #307 on R704's NEXT line — the quantifier is false, and my gate could not see it

R704 closed: *"Clause one is the **only** clause whose exclusions the name touches **at all**."* ⛔
False from R704's own committed grid — **F2's best gain is `+0.0476` at `(family,k,sham)`, identical
in raw units to F1's**. §4 names `only` as the exact tell, and the sentence was written one round
after I committed a block about verdict strings needing to be computed.

⛔ And `assurance/next_line_quantifiers_are_computed.py` extracts `^NEXT:` while R704's commit body
wrote `NEXT.` — so the gate found **no NEXT paragraph at all** and passed on an empty population.
Measured across history: **58 of 1269 commits (4.6%)** are invisible the same way, `20d1d1f` among
them. Fixed in its own commit; the count is recorded here so the fix was not built blind.

## ⛔ the derivation, stated before the measurement

`gain ≤ 1 − base_rate`, because accuracy cannot exceed 1.

| clause | base rate | ceiling | observed | share of **its own** ceiling |
|---|---|---|---|---|
| F1 provenance | 0.9048 | **0.0952** | +0.0476 | **50.0%** |
| F2 behaviour | 0.7857 | **0.2143** | +0.0476 | **22.2%** |

⭐ **The two equal numbers were never the same quantity**, and check #307's own "identical" reading
was a raw-units artifact. This is a **derivation** and is not what the round measures.

## the grid — 3 base rates × 2 partitions × 11 doses, every cell reported

| partition | base rate | null95 | ceiling | MDE | power @ +0.0476 | |
|---|---|---|---|---|---|---|
| `(family,k)` | m=9 (F2's) | +0.0238 | 0.2143 | 0.0792 | 0.564 | below target |
| `(family,k)` | m=38 (F1's) | +0.0000 | 0.0952 | **0.0468** | **0.807** | ⭐ resolvable |
| `(family,k)` | m=21 (balanced) | +0.4048 | 0.5000 | 0.4957 | 0.037 | below target |
| `(family,k,sham)` | m=9 (F2's) | +0.0476 | 0.2143 | 0.0855 | 0.395 | below target |
| `(family,k,sham)` | m=38 (F1's) | +0.0000 | 0.0952 | **never reached** | 0.685 | below target |
| `(family,k,sham)` | m=21 (balanced) | +0.2619 | 0.5000 | 0.3430 | 0.030 | below target |

⚠ Even the one resolvable cell is **razor-edge**: MDE `0.0468` against an observed `0.0476` — eight
ten-thousandths, well inside one arm's worth of movement (`0.0238`).

⛔ **My first MDE statistic contradicted my own table.** It took the smallest *sampled* mean-gain
whose 11-point dose cell reached power 0.80 — a coarse figure that overstates by up to a grid step —
and the verdict branch keyed on it asserted *"below resolution in every cell"* while the power column
beside it showed **0.807**. Both are now computed (`mde` by interpolation, `mde_grid` coarse, both
reported), and the branch keys on the power figure the round actually reports.

## controls — 8 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **g=0 / CALIB** *(evaluated first — it can condemn the instrument)* | power **0.0625** at dose 0 vs 2α = 0.10 — not anti-conservative |
| POSITIVE | power **1.000** at dose 1.0 vs t = 0.95, floor 0.0625 — the band is real |
| NEGATIVE | plant on the **true** cells, measure with **shuffled** ones → power **0.0275** |
| SHAM | plant on the true cells, measure with **one** cell → mean gain **+0.000000**, power 0.000 |
| PLACEBO | two identical runs differ by exactly 0 |
| MONOTONICITY | Spearman(dose, power) = **+0.991** — a real dose-response |
| NOISE FLOOR | sd of gain at dose 0 = **0.0453**, measured over 400 replicates |
| SEEDS | 3 streams at mid-dose: −0.0074 / −0.0107 / −0.0040 |
| UNIT | instrument unit `A SYNTHETIC LABEL VECTOR` ≠ claim unit `AN OBSERVED CLAUSE GAIN` |

⛔ **Two of those controls failed on the first run and were mis-specified in the same way.** I planted
the label as a function of the *same* partition I then measured with — so the NEGATIVE control
destroyed nothing and returned power **0.9975**, and the SHAM was **infeasible** rather than null
(a single cell cannot produce 9 positives, so it crashed). Both are one defect: the ingredient must be
removed from the **measurement** while the **plant** stays on the true structure.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** MDE at F2's base rate | 0.12 [0.03, 0.35] | **0.0792**, error −0.041, inside |
| **B** power at +0.0476, F2's | 0.25 [0.02, 0.70] | **0.564**, error +0.314, inside |
| **C** power at +0.0476, F1's | 0.40 [0.02, 0.90] | **0.807**, error +0.407, inside |
| directional | MDE(m=38) < MDE(m=9) | **0.0468 < 0.0792, HOLDS** |

⚠ **A note against myself**: A is reported on the interpolated MDE, which I built *after* seeing the
coarse one contradict the power column. The coarse value was **0.1378**. Both fall inside the
registered interval, so the choice of statistic did not decide the verdict — but the interval was wide
enough that it could not have, and that is a weakness of my registration, not a strength of the
result.

## limits

- An MDE bounds **what the design can resolve**, never whether a particular observed value is true.
- It is a property of **this partition at this n at this base rate**. The three base rates behave
  completely differently — at balanced the null95 alone is **+0.4048** — so "the MDE of the gain
  statistic" is not a single number and must never be quoted as one.
- The plant defines "true gain" synthetically; no external standard for it exists here.

## impossible here

| criterion | what it would require |
|---|---|
| cross-release | the partition and n are this release's |
| construct validity of "true gain" | an external standard for what a partition ought to encode |
