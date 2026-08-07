# R1081 — **368 of 476 rounds** carry a number their own artifact holds only at higher precision.

**The decision this round makes safe:** whether the helper's zero adoption is a shrug — nobody had
an occasion — or a debt. **It is a debt, and it is the majority of the corpus.** The question was
answered by **running** the comparison both ways, without classifying a single line of code, which
is the thing three previous rounds could not do from syntax.

## The number and its scope

**Population** every round directory holding both a `README.md` and ≥1 `results/*.json` — **690** of
1079 round directories; **476** are eligible in the headline cell (they contain ≥1 decimal token at
2+ places). **Instrument** this script; the helper `assurance/valuematch.py`, **imported, not
re-implemented**. **Baseline** two measured floors, below. **Regime** this checkout.

| headline cell (`cap=100`, no integers, `min_dp≥2`) | |
|---|---:|
| eligible rounds | **476** |
| rounds whose prose holds a decimal exact matching **cannot** locate in their own artifact and precision-aware matching **can** | **368** (0.773) |
| shuffled-pairing floor | **0.170 ± 0.027** |
| within-round shifted-artifact floor | **0.385** |

⛔ **DERIVATION, not evidence.** `E(r) ⊆ P(r)` is forced by the algebra: float equality survives
rounding to any precision, so *"the precision-aware test finds at least as many"* could not have
come out otherwise. **Only the STRICT-superset rate against its own floors is a measurement.**

## The prediction matrix separated the worlds

World **A** (coincidence — `0.5` matches anything) predicts real ≈ floor, gap flat in precision.
World **B** (latent defect) predicts real ≫ floor, **gap widening** with displayed precision, because
a high-precision token is progressively harder to hit by accident.

| `min_dp` | occasion rate | placebo floor | gap |
|---:|---:|---:|---:|
| ≥0 | 0.6357 | 0.2994 | **+0.3363** |
| ≥1 | 0.6732 | 0.1863 | +0.4869 |
| ≥2 | 0.7516 | 0.1552 | +0.5964 |
| ≥3 | 0.7613 | 0.0885 | +0.6728 |
| ≥4 | 0.7500 | 0.0645 | **+0.6855** |

⭐ **World A is KILLED.** The gap doubles as precision rises, which is B's prediction and the
opposite of A's.

## Controls — and two of them changed the round

| control | required | result |
|---|---|---|
| POSITIVE | prose `0.507`, artifact `0.50713` → flagged (R1047's defect, planted) | **PASS** |
| POSITIVE | prose `12.46`, artifact `12.4638` → flagged | **PASS** |
| g=0 | prose `0.507`, artifact `0.507` → **not** flagged | **PASS** |
| g=0 | an integer present exactly → **not** flagged | **PASS** |
| NEGATIVE | prose `0.999`, artifact `0.12` → **not** flagged | **PASS** |
| SHAM | the plant vanishes when the rounding is removed | **PASS** |
| SHAM | identity dose reproduces the exact test · monotone · brackets the real result | **PASS** |
| REPRODUCIBILITY | the real half recomputed identically | **PASS** |

⛔ **The first SHAM could not have passed, and diagnosing it is what produced the dose-response.** I
asserted `force_dp = 17` removes the ingredient, because a double carries ~17 significant digits.
**`round(x, n)` is `n` places after the decimal point, not `n` significant digits** — below 1 the
leading zeros are free, so dp=17 still coarsens. It rescued 7 pairs (`0.002` in R789, `0.0250` in
R1038) against a control demanding exactly zero. **§4's `control that cannot PASS`, built here and
caught here.** The repair was not a looser threshold: a fixed precision is a **dose**, so it was
swept.

| fixed dp | 2 | 3 | 4 | 6 | 8 | 10 | 12 | 17 | 325 | **real** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rounds flagged | 387 | 356 | 321 | 132 | 49 | 45 | 28 | 2 | **0** | **381** |

⚠ **And the curve carries a limit on what the count means.** A blanket 2-decimal rounding flags
**387**, the token's own displayed precision **381**. **The count does not discriminate the two
rules** — it establishes that these prose numbers are *rounded renderings of stored values*, not
that displayed precision specifically is required. The displayed-precision rule is still the correct
one (a blanket rule is looser and can only over-match), but that correctness is not what this number
shows.

⚠ **The strongest confound, and the shuffled placebo is blind to it.** A round's own artifact holds
many numbers of the same family, so **within-round** collisions could beat cross-round ones. Control:
shift the artifact by one unit of the cell's own resolution — same count, same spacing, same
magnitudes, correspondence destroyed. **This control killed 4 cells.**

## Specification curve — 40 cells, **36 survive, 4 killed**, all reported

**Every killed cell is `min_dp = 0` with integers included**, where the *shifted* artifact scores
**0.959** against a real **0.611**: an integer matches anything, so the cell measures nothing. At
`min_dp ≥ 2` all **24 of 24** cells clear both floors. Sweeping the artifact cap (`0 / 10 / 100 /
None`) moves the rate 0.695 → 0.773 and never the sign.

## What the sentence is allowed to be

**Unit of the instrument** a (round, token) pair on which the two membership tests disagree.
**Unit of the claim** the same, deliberately. The round says: *any check over these 368 rounds using
exact matching would have been wrong.* It does **not** say those rounds ran such a check — author
intent is **N/A**, and would require the session transcript, which is not in the release.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| construct validity (did the author intend a comparison?) | **N/A** | the session transcript at the time of writing |
| cross-repository | **N/A** | a second site with its own round convention |
| multiplicity correction | **N/A** | each cell reports a rate against its **own measured floor**, not a test; a q-value on a floor comparison would be the arithmetic trap |
| multi-seed on the real measurement | **N/A** | it is deterministic; 5 seeds are used on the placebo and the real half is reproduced identically instead |

`run.py` · `results/occasion_by_execution.json`
