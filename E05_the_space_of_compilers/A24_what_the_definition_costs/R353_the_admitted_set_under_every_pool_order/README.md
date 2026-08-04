# R353 — the published five recurs in 7.7% of pool orderings

**The decision this makes safe:** may the page print *the* admitted set? **No.** The set of five is a
consequence of one unregistered choice — the row order of a `.npz` — and a typical ordering admits
**seven**.

## Result — `W2_ORDER_IS_THE_ANSWER`

400 permutations × 2 seeds, 170 s. **All three controls PASS.**

| seed | P(published set) | distinct sets | mean \|admitted\| | min | max |
|---:|---:|---:|---:|---:|---:|
| 3531 | **0.077** | 24 | 6.90 | 2 | 9 |
| 3532 | **0.070** | 25 | 6.78 | 1 | 9 |

**The published five recurs in 7–8% of orderings, and it is smaller than typical: the mean admitted
set is ~6.8.** The census's reference sits at the **93.7th percentile** of size-4 subsets — an
unusually *strict* baseline — so the published set is not a central draw, it is a tail one.

## Per-arm inclusion over pool orderings

| arm | P(seed 3531) | P(seed 3532) | in published five? |
|---|---:|---:|---|
| `coval_core` | 1.000 | 0.998 | ✓ |
| `topw_k6` | 0.998 | 0.998 | ✓ |
| `topw_k4` | 0.985 | 0.988 | ✓ |
| `topw_k8` | 0.963 | 0.938 | ✓ |
| `topw_k3` | 0.955 | 0.960 | ✓ |
| **`generic`** | **0.800** | **0.757** | ✗ |
| **`topw_k2`** | **0.723** | **0.685** | ✗ |
| **`topw_k1`** | **0.430** | **0.415** | ✗ |
| `gen` | 0.045 | 0.045 | ✗ |

**Three arms the published set excludes are admitted under most orderings.** The five that are
published are the five that survive *everywhere* — which is a real property, and not the one the page
claims.

## ⭐ Two uncertainty sources, opposite pictures of the same arms

R339 bootstrapped over **prompts** and reported `topw_k2` admitted in **13%** of resamples,
`generic` in **5%**. This round varies the **reference subset** and finds `topw_k2` at **68–72%**,
`generic` at **76–80%**.

**Both are correct and they answer different questions.** Sampling noise in the *data* says those
arms are marginal; the *choice of baseline* says they are admitted unless the baseline is unusually
strict — which the published one is. **Neither number alone characterises the arm.**

## Controls

| | returned |
|---|---|
| **REPRODUCTION** | the identity permutation gives **exactly** R294's committed five: `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` |
| **DETERMINISM, g=0** | identity evaluated twice → same set |
| **MOVEMENT, negative** | at least one ordering gives a different set — otherwise *"order is noise"* would be unfalsifiable |
| **SEEDS** | two, reported separately, **never averaged** |

The reproduction control is the load-bearing one: **a reimplementation that cannot reproduce the
census cannot be trusted to vary it.** It reproduces it exactly, and the arm-level agreement is
tight (`coval_core` effect +0.0160 / MDE 0.01062 here vs 0.016042 / 0.010616 committed).

## Why permutations and not independent subsets

The census's rule is **`POOL[0:k]` — a prefix**, and prefixes at different k are **nested**. Drawing
an independent subset per k would measure a policy the census does not use. A permutation is exactly
*"the file could have been written in any order"*, which is the question.

## Register

| criterion | status |
|---|---|
| clause ③ | **declared**, not computed — carried from R294 unchanged. Invariant to pool order, so it cannot bias this comparison, but it is not re-derived here |
| sampling | **400 of 16!** permutations; binomial se ≈ **0.025** at p = 0.5 — enough to separate *almost always* from *almost never*, **not** enough to rank two arms three points apart |
| what this does not touch | whether the **pool itself** is the right reference class. A different 16 criteria would move everything, and that is R287's budget question, still unanswered |

## The sentence I can no longer write

> *"the definition admits five arms."*

**It admits five under one ordering of one file. Under a typical ordering it admits about seven.**

Artifact: `results/r353_pool_order.json`.
