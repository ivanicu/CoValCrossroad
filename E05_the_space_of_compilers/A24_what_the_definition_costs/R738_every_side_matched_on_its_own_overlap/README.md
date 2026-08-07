# R738 · every side matched on its own overlap

**With every side matched on its own measured overlap and its own `(k_a,k_b)` curve, all ten excesses
are NEGATIVE. The real rule-produced arms correlate BELOW the random-subset floor. The ordering
survives, but the claim it supported does not.**

## The result
| object | ref | k | overlap | r | matched floor | **excess** |
|---|---|---|---|---|---|---|
| `greedy` | **oracle** *(excluded)* | 4 | 2.8492 | 0.8123 | 0.8299 | **−0.0176** |
| `greedy` | topw_k3 / k4 / k6 / k8 | 3/4/6/8 | 0.9700 / 1.3140 / 1.9855 / 2.5775 | 0.4364 / 0.4927 / 0.5784 / 0.6004 | 0.5577 / 0.6128 / 0.6811 / 0.7168 | −0.1212 / −0.1201 / −0.1027 / −0.1164 |
| `indep` | **oracle** *(excluded)* | 4 | 2.1095 | 0.6608 | 0.7246 | **−0.0638** |
| `indep` | topw_k3 / k4 / k6 / k8 | 3/4/6/8 | 1.1653 / 1.5372 / 2.2624 / 2.8337 | 0.4684 / 0.5260 / 0.5958 / 0.6108 | 0.5922 / 0.6441 / 0.7113 / 0.7381 | −0.1237 / −0.1181 / −0.1155 / −0.1273 |

**greedy: −0.0176 vs −0.1151, gap +0.0975 · indep: −0.0638 vs −0.1212, gap +0.0574 · band 0.0151.**

⭐⭐ **What this changes.** R733 reported these objects tracking the excluded one *beyond* the floor by
+0.4632 and +0.3965. **Against a floor matched on measured overlap, they track it BELOW the floor.**
What survives is a comparison of two **deficits** — they fall short of the random-subset expectation
by *less* against the excluded object than against the blind arms. **That ordering holds. "They move
with it prompt by prompt" does not.**

## The curves — one per k-pair, not one for all
| curve | ρ | floors by j | max held-out \|Δ\| |
|---|---|---|---|
| 4×3 | 0.3026 | 0.3857 / 0.5630 / 0.7396 / 0.9153 | 0.0023 |
| 4×4 | 0.3361 | 0.4143 / 0.5687 / 0.7090 / 0.8514 / 1.0000 | 0.0051 |
| 4×6 | 0.3826 | 0.4631 / 0.5726 / 0.6827 / 0.7914 / 0.8975 | 0.0066 |
| 4×8 | 0.4007 | 0.4822 / 0.5789 / 0.6687 / 0.7520 / 0.8408 | 0.0100 |

⛔ **R737's NEXT proposed reading all four off "the same curve".** That curve is 4×4 and three of the
four comparisons are **cross-k** — reusing it would have been the same unit error this arc has made
three times. Caught before building.

⭐ **Model verified before the round**: for independent components the raw correlation of two means
over `k_a`, `k_b` sharing `j` is `j/√(k_a·k_b)` — checked synthetically at 18 cells to **0.0032**.
With the shared per-response component it is `ρ + (1−ρ)·j/√(k_a·k_b)`, fit at **j=0 alone** per curve
and predicting every held-out target to **0.0100**.

## ⛔ The SHAM failed twice, and both failures were mine
1. `same=True` **extended** the draw when `k_b > k_a`, so the two arms were not the same draw.
2. After fixing that it still failed — **the rng seed carried `j`**, so the "same draw" re-drew at
   every target and could not return a constant. Now `[0.0, 0.0, 0.0, 0.0]`.

*A sham that varies with the ingredient it is supposed to have removed is not a sham.*

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: pooled max held-out |Δ| **0.0100** · **g=0**: every curve responds to overlap, j=0
below j=1 by >3sd, all four · **NEGATIVE**: nominal j not realised → every curve flattens, all four ·
**PLACEBO**: 4×4 at j=4 → **1.000000** · **SHAM**: **0.0** on all four curves.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A pooled held-out \|Δ\| | 0.05 [0, 1] | **0.0100** | yes |
| B greedy floor vs excluded | 0.83 [0, 1] | **0.8299** | yes |
| C greedy mean blind floor | 0.70 [0, 1] | **0.6421** | yes |
| D orderings surviving | 2 [0, 2] | **2** | yes |
| DIRECTIONAL both survive | — | **holds** | — |

⚠ **The preregistration declined to predict this**, and said so: *"greedy's overlap with topw_k8
(2.5775) is close to its overlap with the excluded object (2.8492) … I am NOT able to predict the
outcome."* The outcome was not the one the interval-passing suggests — **all excesses went negative,
which no registered point asked about.**

⚠ **Every floor here is a RANDOM-SUBSET floor.** Whether a rule-produced arm behaves like a random
subset at equal overlap is **not identified** and needs a new selection run. **That is exactly the
gap the negative excesses now point at.**

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, both writes verified.
**Artifact:** `results/r738_matched_excess.json` · 968 prompts fixed across every target of every curve.
