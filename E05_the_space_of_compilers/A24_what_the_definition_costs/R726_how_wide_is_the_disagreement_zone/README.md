# R726 · how wide is the disagreement zone

**R725's zero-of-410 is structural, not luck — but 246 of those 410 checks could never have failed.**

## The zone
`r = SE_ci/SE_mde` over 82 cells: min–max **[0.9478, 1.0691]**, 5th–95th **[0.9689, 1.0569]**.
The gap between the two spreads, **0.0334**, is this design's noise floor — min–max is an extreme
order statistic of 82 draws and is reported *beside* the percentile range, never instead of it.

| rule | boundary in `t` | zone | width |
|---|---|---|---|
| point | `0` | — | **0** |
| ci_only | `1.959964·r` | [1.8576, 2.0954] | **0.237796** |
| mde_only / strict | `2.801585` | — | **0** |
| conservative | `2.801585 + 1.959964·r` | [4.6592, 4.8970] | **0.237796** |

⛔ **Only two rules have an SE-dependent boundary, and their widths are equal — by algebra, not by
measurement.** `point` and `mde_only` never touch `SE_ci`; `strict` binds on `mde_only` when
`eff > 0`. The equality of the two widths is `1.959964·(r_max − r_min)` in both cases.

## ⭐ What this does to R725's own number
R725 reported **0 mismatches over 410 checks** (82 cells × 5 rules). **Only 164 of those checks had
a boundary that could move at all.** The remaining **246 are arithmetic** — three rules that could
not have disagreed however the data fell. **The failable population was 164, not 410**, and the
severity of that check was overstated by a factor of 2.5.

## Occupancy — 0, and not marginally
**No cell of 82 falls inside either zone**, and none would flip under the adverse end of the
observed `r` range. Under the 5–95 range the widths are **0.172352** and occupancy is still 0.

## DOSE–RESPONSE — the control that makes this a measurement
| r-spread × | zone width | inside | would flip |
|---|---|---|---|
| **0.0** | **0.000000** | 0 | 0 |
| 0.5 | 0.118898 | 0 | 0 |
| 1.0 *(observed)* | 0.237796 | 0 | 0 |
| **2.0** | 0.475591 | **2** | **2** |
| 4.0 | 0.951183 | 5 | 5 |

**Monotone, and exactly 0 at multiplier 0.** A width that did not scale with the spread would be
arithmetic dressed as a finding. **The SE spread would have to double before one cell entered a
zone** — that is the design's resolution, stated as a factor rather than asserted as safety.

## Controls — 5 PASS, 0 FAIL
**POSITIVE + g=0**: a cell planted at the zone centre (`t = 1.9765`) is inside and flips; a far cell
at `t = 10` is inside nothing and flips nothing · **DOSE**: monotone, zero at zero · **NEGATIVE**:
every `r` set to exactly 1 → all five widths 0, occupancy 0, excluding *"the zones come from the
threshold arithmetic rather than the SE spread"* · **SHAM**: the three rules whose predicates never
touch `SE_ci` → width exactly 0, the ingredient **absent** rather than inverted · **PLACEBO**: each
cell against itself → 0 flips.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A ci_only zone width | 0.24 [0, 5] | **0.2378** | yes |
| B cells inside any zone | 3 [0, 82] | **0** | yes |
| C cells that would flip | 0 [0, 82] | **0** | yes |
| D dose at first occupancy | 2.0 [0, 64] | **2.0** | yes |
| DIRECTIONAL ⛔ derivation | — | **holds** | — |

⚠ **B's point prediction was wrong** — I registered 3 and measured 0. The interval was wide enough
to absorb it, which is what a wide interval is for and also what makes it weak evidence about my
calibration. Recording the miss rather than the interval-pass.

## Residue
The `r` of an arm this release does not contain is unmeasurable here — it would need a new arm
judged by the same pipeline.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r726_zone_width.json` · 2050 classifications.
