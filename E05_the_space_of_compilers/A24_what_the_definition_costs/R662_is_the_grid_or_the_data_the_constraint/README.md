# R662 · Max power 0.14 at every resolution — the whole inferential arm is dead, and the censuses survive

**Decision this makes safe:** whether any statistical claim about the naming rate can be made from
this data. **No. At 8 resolutions × 200 permutations, the design never reaches 50% power. R661's
"null with power" is RETRACTED, and so is my own NEXT's assertion about the cause.**

## The specification curve, whole

| k | bins | p50 | **p95** | plant (best of 7) | plant median | **power** | sham | unif | obs |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 3 | 1.000 | **1.000** | 1.000 | 1.000 | **0.00** | 0.500 | 0.500 | 1.000 |
| 4 | 4 | 0.800 | **1.000** | 1.000 | 1.000 | **0.00** | 0.400 | 0.800 | 1.000 |
| 6 | 6 | 0.829 | **1.000** | 0.943 | 0.829 | **0.00** | 0.086 | 0.543 | 0.943 |
| 8 | 8 | 0.810 | **0.976** | 0.952 | 0.810 | **0.00** | 0.167 | 0.643 | 0.881 |
| 12 | 12 | 0.692 | **0.888** | 0.930 | 0.204 | **0.14** | 0.175 | 0.664 | 0.888 |
| 16 | 16 | 0.440 | **0.694** | 0.591 | 0.165 | **0.00** | 0.331 | 0.466 | 0.692 |
| 24 | 22 | 0.613 | **0.783** | 0.513 | 0.204 | **0.00** | 0.252 | 0.525 | 0.802 |
| 32 | 28 | 0.376 | **0.642** | 0.421 | 0.139 | **0.00** | 0.103 | 0.410 | 0.737 |

**Power = the fraction of 7 planted 5× draws clearing p95. Max = 0.14. No resolution reaches 0.5.**

## ⛔⛔⛔ R661 is RETRACTED, and the mechanism is exact

| | |
|---|---|
| R661 at k=8, null from **5 draws, min/max** | `[0.238, 0.857]` |
| here at k=8, null from **200 draws, p95** | **0.976** |
| R661's planted 0.929 vs its own 0.857 | **CLEARED** — its conclusion |
| R661's planted 0.929 vs the proper **0.976** | **DOES NOT CLEAR** |

**R661's positive control passed only because a 5-draw min/max understates the null.** ⭐ And the
planted arm's spread across 7 draws is **0.190–0.952** — **R661's 0.929 was one draw near the top.**
*A positive control run once is a point estimate of power: the same error as a 5-draw null, one
level up.*

## ⭐ Why nothing fires — the statistic's own granularity

`p95 = 1.000` at k = 3, 4, 6 is **forced**: a Spearman over k points takes few discrete values and
`P(|rho| = 1)` by chance is `2/k!` — **33.3% at k=3, 8.3% at k=4.** §4's `floor == ceiling` case:
**the statistic is degenerate and no threshold is admissible.** Above k=12 the null falls but so
does the planted signal, because 86 mentions cannot fill a finer grid.

## ⛔ Two defects in this round's own verdict, both caught before shipping

**① `pos_fires` read power off the BEST of 7 planted draws** — §4's sub-kind ③, *selecting with
`max()` over arms*, **in the round that quotes that row.** With power as a *fraction*, the design
goes from "fires at k=12" to **0 of 8**.
**② The verdict said *"R661's null survives the whole specification curve"* while the block above it
retracted R661.** A contradiction inside one output — **the fourth verdict-string defect in four
rounds.**

## ⛔ Check #263 — three clauses verify, one was asserted

✓ the null was 5 draws · ✓ §4 names that failure · ✓ the control cleared by 0.0714.
⛔ *"the MDE is set by having 8 bins, **not by the data**"* — **asserted, never computed.** Now
computed, and **the answer is inadmissible either way**: with max power 0.14 the question of which
constraint binds cannot be settled by this design at all.

## Controls

| control | returned |
|---|---|
| **positive** — power ≥ 0.5 at any resolution | **0 of 8 (max 0.14)** — ⛔ **FAIL**, and the verdict obeys it |
| **sham** — pure exposure ≤ p95 | **PASS** at every resolution |
| **placebo** — uniform-at-random inside the null | **PASS** at every k |
| **noise floor** — p50/p95 over 200 draws, never min/max | the specific failure R661 committed |

**MULTIPLICITY:** 8 resolutions × (observed + planted×7 + sham + uniform) × 200 permutations =
**1600 null draws**; the whole curve printed including all 8 resolutions where the control fails.

**IMPOSSIBLE, named:** the exposure proxy needs ledger timestamps the file does not carry —
inherited from R661, unchanged, and its direction stated (it biases *toward* manufacturing an age
gradient, so a null is conservative).

## What survives, and what does not

| **STANDS** — censuses, not inferences | |
|---|---|
| tight / loose wall-entries | **39 / 132** |
| rounds declaring an `IMPOSSIBLE` register | **288–290 of 334** |
| declaring rounds named by any wall-entry | **53** |

| **WITHDRAWN** — every inferential claim built on them | |
|---|---|
| R661 "a null with power" | its control passed on an understated null |
| R661 per-round `|rho| = 0.167` | unit with no power |
| R660 "86.1% traceability" | below a random baseline |
| my NEXT "the grid binds, not the data" | undecidable at 0.14 power |

## The sentence I can no longer write

> *"no age gradient is detectable, at a unit where a planted one is."*

**There is no such unit.** The design cannot detect a planted 5× gradient at any of eight
resolutions, so its null was never evidence of absence.

## NEXT

**Both pre-registered estimates landed INSIDE their intervals on a design with 0.14 power** — argmax
k=12 in {4,6,8,12}, observed-clears 2 in [0,2]. **A forecast that hits on a powerless design is not a
calibrated forecast; it is a coincidence I would otherwise have counted as evidence of judgement.**
**Recompute the forecast record with every prediction made against a powerless or withdrawn statistic
marked INADMISSIBLE**, because the record currently reads "six of seven directional predictions
held" and at least three of those were about numbers that no longer exist.
