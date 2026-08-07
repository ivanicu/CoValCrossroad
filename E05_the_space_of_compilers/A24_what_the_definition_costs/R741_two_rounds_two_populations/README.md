# R741 · two rounds, two populations

**R738 and R740 ran on different populations against different pools. The disagreement I read as a
sign flip was the POOL. R738's ten excesses are withdrawn; R740's stand; the ordering is still
unresolved.**

## What the arithmetic step found — not what I went looking for
R740's NEXT proposed extrapolating the prompt count needed to resolve a two-hundredth shortfall,
asserting `SE ∝ 1/√n`. Checked: the construction-seed component is **0.0034 of an SE of 0.0162**, so
the SE **is** prompt-dominated — the assertion was right and **unmeasured when I made it**.

⛔ **The check surfaced a larger defect.** R738 ran on **968** prompts, R740 on **734**, both printing
a 12-criterion requirement. **R738's pool was the union of observed selections — which R739 proved is
biased by the rules under study. R740 used the full candidate set.** Fewer prompts clear the threshold
against the true pool.

## The ten cells on both pools
| object | ref | TRUE pool | UNION pool | SE | 95% CI | covers 0 |
|---|---|---|---|---|---|---|
| greedy | oracle | **+0.0211** | −0.0176 | 0.0162 | [−0.0116, +0.0524] | yes |
| greedy | topw_k3/k4/k6/k8 | −0.0088 / −0.0122 / −0.0120 / −0.0411 | −0.1212 / −0.1201 / −0.1027 / −0.1164 | 0.025–0.031 | span 0 | yes |
| indep | oracle | **+0.0176** | −0.0638 | 0.0232 | [−0.0294, +0.0621] | yes |
| indep | topw_k3/k4/k6 | −0.0214 / −0.0231 / −0.0339 | −0.1237 / −0.1181 / −0.1155 | 0.025–0.030 | span 0 | yes |
| **indep** | **topw_k8** | **−0.0556** | −0.1273 | 0.0234 | **[−0.1008, −0.0116]** | **no** |

**Mean absolute pool effect: 0.0857** — several times the bootstrap SEs.

⭐ **R740's point estimates reproduce here within their own SE in all ten cells** (0 of 10 outside).
**So R740's numbers stand and only its COMPARISON to R738 was wrong.**

⛔ **RETRACTED, from my own report one round ago:** *"the signs are not stable — greedy↔oracle is
+0.0211 here against −0.0176 as R738's point estimate… the interval covering zero arriving as a sign
flip."* **That difference is a population change, not sampling noise.**

⛔ **R738's ten excesses are withdrawn** — computed on the wrong pool.

## The conclusions on one population
**Ordering gaps:** greedy **+0.0396 [−0.0109, +0.0915]** · indep **+0.0511 [−0.0004, +0.1023]**.
**1 of 10 excesses and 0 of 2 gaps exclude zero. The ordering remains unresolved.**

⚠ **A limit this round creates rather than inherits.** Correcting the pool **drops 234 prompts**, and
that is **a selection on pool size, not a random subsample** — surviving prompts have a median pool
of 15 against the dropped prompts' smaller sets. **The surviving population is not the release**, and
both distributions are printed rather than exchangeability assumed.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: the bootstrap reproduces analytic `sd/√n` within 5% **on this population** — *an
interval estimator unvalidated on the population it is used on prices nothing* · **g=0**: a cell
against itself → exactly 0 · **NEGATIVE**: resampling disabled → SE **exactly 0** · **SHAM**: the
union pool computed **in full**, both columns side by side, so the pool effect is **visible rather
than asserted** · **PLACEBO**: 0.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A prompts on the true pool | 734 [0, 968] | **734** | yes |
| B greedy↔excl on true pool | 0.021 [−1, 1] | **0.0211** | yes |
| C excesses excluding 0 | 1 [0, 10] | **1** | yes |
| D gaps excluding 0 | 0 [0, 2] | **0** | yes |
| DIRECTIONAL R740 reproduces | — | **holds, 0 of 10 outside** | — |

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, both writes verified.
**Artifact:** `results/r741_one_population.json` · every cell on both pools.
