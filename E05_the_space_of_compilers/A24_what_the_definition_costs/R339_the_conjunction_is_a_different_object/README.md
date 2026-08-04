# R339 — the published admitted set recurs in 53% of resamples, across 30 distinct sets

**Decision this makes safe:** whether the page may print **one** admitted set. **Marginally yes —
and only with per-arm inclusion probabilities beside it.** **W-STABLE**, at 53.4% against a
pre-registered boundary of 50%. *That is a thin verdict and the number is the report.*

## The distribution over admitted sets

| P | set |
|---:|---|
| **0.534** | `coval_core` · `topw_k3` · `topw_k4` · `topw_k6` · `topw_k8` **← what the page prints** |
| 0.122 | + `topw_k2` |
| 0.112 | − `topw_k4` |
| 0.037 | + `generic` |
| 0.035 | − `topw_k8` |

**30 distinct sets** (seed 2: 32). `P(published) = 0.534` (seed 2: **0.558**).

## Per-arm inclusion probability — the number the page should carry

| arm | P(①) | P(②) | **P(both)** | seed 2 |
|---|---:|---:|---:|---:|
| `topw_k6` | 1.000 | 0.995 | **0.995** | 0.999 |
| `topw_k3` | 1.000 | 0.943 | **0.943** | 0.952 |
| `coval_core` | 1.000 | 0.919 | **0.919** | 0.918 |
| `topw_k8` | 1.000 | 0.882 | **0.882** | 0.885 |
| **`topw_k4`** | 1.000 | 0.763 | **0.763** | 0.763 |
| `topw_k2` *(excluded)* | 1.000 | 0.130 | 0.130 | 0.130 |
| `generic` *(excluded)* | 1.000 | 0.051 | 0.051 | 0.043 |

**`topw_k4` carries a checkmark on the page and is admitted in 76% of resamples. `topw_k2` carries
no checkmark and is admitted in 13%.** Neither fact is currently on the page.

## ⛔ The independence contrast is UNIDENTIFIED — and that *is* the result

I pre-registered `P(both)` vs `P(①)·P(②)` as the price of reporting clauses separately. The measured
excess is **+0.000 everywhere** — **not because the clauses are independent, but because
`P(①) = 1.000` for every arm carrying any clause-② mass.** With clause ① saturated, `P(both) ≡ P(②)`
**by arithmetic** and no dependence can show.

> **Clause ② carries 100% of the joint sampling uncertainty.** The page's claim that clause ② is the
> binding constraint is now measured *at the set level*, not just per arm.

**And the +0.000 is not silence**, because the instrument was checked where dependence *can* appear:
a synthetic arm with clause ① shrunk to its own MDE gives `P(①) 0.507 · P(②) 0.774 · P(both) 0.429`
against a product of `0.393` — **excess +0.037**. The instrument sees dependence when it is there.

## Controls

| control | result |
|---|---|
| **placebo** — full sample reproduces R294's committed verdicts | **37 of 37** |
| **positive** — `coval_core` at 5.6× on clause ① must be resample-stable | P(①) = **1.000** |
| **positive @ g=0** — `gen_sham` (0.60× on ①, loses ②) | P(both) = **0.000** |
| **positive · dependence instrument** — synthetic arm, both clauses live | excess **+0.037** |
| **negative** — independent draws for the two clauses | max ΔP = **0.017**, *as forced* |
| specification — weaker rule (CI excludes 0, no MDE) | 27 sets, P(published) = **0.434** |

### ⚠ The negative control was invariant to its own permutation first

v1 permuted the *elements* of one clause's difference vector. **A permutation cannot change a
vector's mean or sd**, so `verdict` was invariant to it and the control destroyed nothing — it
"failed" by reproducing the real result exactly. The structure under test is the **shared resample**,
so the destruction is to draw the two clauses **independently**.

## The sentence I can no longer write

> *"the admitted set is {coval_core, topw_k3, topw_k4, topw_k6, topw_k8}"* — without `0.53`
> beside it, or the five inclusion probabilities.

## Scope

37 clause-③-passing arms · 968 prompts · cluster bootstrap over prompts, 2,000 draws × 2 seeds ·
baselines as R294 published them · **prompt uncertainty only** — the reference axis (R326) and the
judge axis (R290) are separate and are not folded in.

## What this cannot do

Fold reference, judge and prompt uncertainty into one interval. That needs a joint resampling scheme
the release does not support, and the three are measured separately by design.
