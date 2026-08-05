# R739 · the floor was drawn from a different population

**The variance hypothesis is REFUTED. Rule-produced arms do not select higher-variance criteria, and
R738's negative excesses survive — one candidate explanation is eliminated rather than confirmed.**

## ⛔ My proposed statistic was wrong, and `select_core.py` says so in its own comment
R738's NEXT proposed comparing the **satisfaction level** of a rule's criteria against the pool. The
selection source carries a derivation that makes level the wrong quantity:

> *"a criterion whose satisfaction is IDENTICAL across the four responses adds the same constant to
> every `y_x`, so it changes no pairwise sign and is arithmetically INERT no matter how important it
> is."*

**So the quantity is across-response VARIANCE.** A rule fitting the human target cannot afford inert
criteria. That was the hypothesis. **It is false.**

## The measurement — mean variance percentile rank, null exactly 0.5
| arm | rank |
|---|---|
| **`topvar_k4`** *(selects BY variance — the known answer)* | **0.8528** |
| `topwvar_k4` | 0.7903 |
| `oracle_k4` *(excluded, target-reading)* | **0.5028** |
| `greedy` / `indep` *(admitted, target-reading)* | **0.4677 / 0.5318** |
| `topw_k3/k4/k6/k8` *(label-blind)* | 0.4925 / 0.4966 / 0.4973 / 0.4982 |
| `random_k12_s0/s1/s2` | 0.5006 / 0.4990 / 0.5002 |

**The registered DIRECTIONAL fails: the target-reading arms sit at the null.**

## The consequence — D = 0 of 10
| | R738 excess | var-matched excess |
|---|---|---|
| greedy ↔ oracle | −0.0176 | **−0.0360** |
| greedy ↔ topw k3/k4/k6/k8 | −0.1212 / −0.1201 / −0.1027 / −0.1164 | −0.0855 / −0.0368 / −0.0747 / −0.0482 |
| indep ↔ oracle | −0.0638 | **−0.0190** |
| indep ↔ topw k3/k4/k6/k8 | −0.1237 / −0.1181 / −0.1155 / −0.1273 | −0.0619 / −0.0167 / −0.0673 / −0.1271 |

**Magnitudes shrink; every sign holds.** ⚠ **222 prompts** cannot supply a variance-matched subset at
the widest target and are **excluded, not back-filled**.

## ⛔ Three of my own defects, each caught by a control
1. **A mean of per-prompt ratios.** Inflated wherever the denominator is small — uniform random arms
   returned **1.28** where the null is 1. **g=0 caught it.** Replaced by the **mean percentile rank**,
   whose null is **exactly 0.5** by construction and which no small denominator can inflate.
2. **The pool was the union of observed selections** — a sample of the candidate set **biased by the
   very rules under study**. g=0 still returned 0.5664 **and the SHAM on criterion text length
   returned 0.65**. *The sham is what proved the bias was not variance-specific.*
3. **I was about to declare the true population unmeasurable.** `select_core.py:127` requires every
   candidate to be judged in both npzs, the `full` arm selects the whole candidate set, and its
   satisfaction coverage is **exactly 1.0**. **The wall was false — the second time in three rounds.**

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: ⭐ a **known-answer case from the source** — `topvar_k` selects by this variance and
ranks **first at 0.8528** · **g=0**: uniform arms **0.5005 ± 0.0029**, |Δ| 0.0005 < 3sd 0.0088 ·
**NEGATIVE**: criterion→variance permuted → **0.4916 / 0.4940 / 0.5010** · **SHAM**: criterion text
length → **0.5343** mean · **PLACEBO**: pool against itself → 1.0 by construction.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A oracle variance rank | 0.60 [0, 1] | **0.5028** | yes |
| B topw_k4 variance rank | 0.55 [0, 1] | **0.4966** | yes |
| C greedy var-matched floor | 0.85 [0, 1] | **0.8392** | yes |
| D excesses now ≥ 0 | 5 [0, 10] | **0** | yes |
| **DIRECTIONAL** ranks above 0.5 | — | **FAILS** | — |

⚠ **A and B were registered above the null and both came in at it.** The intervals absorbed both,
which is what wide intervals do; **the directional is the point that carries the refutation.**

⚠ **Eliminating one confound does not name the cause.** R738's shortfall is now **unexplained**
rather than explained away, and variance is not the only property these rules could select on.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, both writes verified.
**Artifact:** `results/r739_variance_matched.json`.
