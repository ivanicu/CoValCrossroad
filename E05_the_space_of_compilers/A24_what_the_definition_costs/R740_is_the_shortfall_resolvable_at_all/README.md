# R740 · is the shortfall resolvable at all

**9 of the 10 excesses cover zero. Both ordering gaps cover zero. Three rounds reasoned about — and
one tried to explain — a quantity this design cannot resolve.**

## The measurement
Prompts bootstrapped, with the correlation, its overlap-matched floor **and the overlap itself**
recomputed together on every resample — 2000 × 3 seeds.

| object | ref | excess | SE | 95% CI | covers 0 |
|---|---|---|---|---|---|
| greedy | **oracle** | **+0.0211** | 0.0162 | [−0.0117, +0.0524] | **yes** |
| greedy | topw_k3 / k4 / k6 / k8 | −0.0088 / −0.0122 / −0.0120 / −0.0411 | 0.0245–0.0307 | all span 0 | **yes** |
| indep | **oracle** | **+0.0176** | 0.0232 | [−0.0294, +0.0621] | **yes** |
| indep | topw_k3 / k4 / k6 | −0.0214 / −0.0231 / −0.0339 | 0.0250–0.0300 | all span 0 | **yes** |
| indep | topw_k8 | **−0.0556** | 0.0234 | [−0.1009, −0.0116] | **no** |

**Ordering gaps:** greedy **+0.0396** [−0.0102, +0.0904] · indep **+0.0511** [−0.0022, +0.0995] —
**both cover zero.**

⭐ **And the signs are not stable.** greedy↔oracle is **+0.0211** here against **−0.0176** as R738's
point estimate. *That is the same statement as the interval covering zero, arriving as a sign flip.*

## ⛔ What this retracts
- **R738's "the ordering survives"** — the gaps it reported (+0.0975, +0.0574) do not exclude zero
  under joint resampling.
- **R739's premise.** It spent a round explaining a negative sign that is not resolvable. Its own
  finding — that the rules do not select higher-variance criteria — **stands**, because that was a
  refutation with its own validated instrument, not an explanation of the shortfall.
- **What survives**: `indep`↔`topw_k8` alone, at **−0.0556 [−0.1009, −0.0116]**, 1 of 10.

## Quadrature was the wrong combination, as registered
| | |
|---|---|
| naive quadrature *(labelled comparator)* | **0.0213** |
| bootstrap SE, joint resampling | **0.0162** |
| SHAM — bootstrap `r` only, floor held fixed | **0.0181** |

**The joint SE is smaller than both**, so the correlation and its floor **move together** — exactly
the directional registered before the run, and the reason independence-assuming quadrature overstates
the width.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: bootstrap SE of a mean matches analytic `sd/√n` within 5% — *an interval estimator that
cannot reproduce a known SE prices nothing* · **g=0**: a cell against itself → exactly 0 ·
**NEGATIVE**: resampling disabled → SE **exactly 0**, excluding *"the width comes from the
recomputation, not the resampling"* · **SHAM**: `r`-only resampling reported beside the joint ·
**PLACEBO**: [0, 0].

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A quadrature ⛔ naive | 0.021 [0, 1] | **0.0213** | yes |
| B bootstrap SE greedy↔excl | 0.020 [0, 1] | **0.0162** | yes |
| **C excesses excluding 0** | **5 [0, 10]** | **1** | yes |
| **D ordering gaps excluding 0** | **2 [0, 2]** | **0** | yes |
| DIRECTIONAL bootstrap < quadrature | — | **holds** | — |

⚠ **C and D were registered at 5 and 2 and came in at 1 and 0.** The intervals absorbed both; **the
registered points are what make the miss legible.**

⚠ The interval is **conditional on this criterion pool** — pricing pool uncertainty needs a second
release.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, both writes verified.
**Artifact:** `results/r740_resolution.json`.
