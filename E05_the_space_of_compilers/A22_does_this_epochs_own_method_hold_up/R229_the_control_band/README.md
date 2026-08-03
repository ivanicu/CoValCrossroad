# R229 — the control band

**Arc E05·A05.** The decision this makes safe: **how do I set a positive control's threshold?**

Three of the last five rounds failed *first* on a control whose target the design made unreachable.
`realstat` §4 names the mirror image — *"check that cannot fail", built 4×, caught 4×* — and has
nothing for this direction. P7: **the third instance is infrastructure, not a third patch.**

## The rule

```
floor    = the statistic with NO plant                    (what chance returns)
ceiling  = the statistic with a MAXIMAL plant, no noise   (what perfect detection returns)

a registered threshold t is admissible only if   floor < t < ceiling
  t ≥ ceiling  →  the control CANNOT PASS.  Its failure says nothing about the world.
  t ≤ floor    →  the control CANNOT FAIL.  Its success says nothing about the world.
```

> ⚠ **The ceiling is not 1.0 by default.** It is 1.0 only where the design admits a *unique* correct
> answer. Wherever ties, degeneracy or saturation exist — which is most places worth studying — the
> ceiling is strictly below 1 and must be **computed**, not assumed.

Implemented as `covalx/control_band.py`, importable by every future round.

## The replay

| control | floor | ceiling | threshold | observed | verdict |
|---|---:|---:|---:|---:|---|
| R221 `posthoc` | 0.2713 | 0.2713 | 0.2713 | 0.0537 | **CANNOT PASS** |
| R225a dispersion | 1.0000 | 1.0000 | 0.5000 | 0.9650 | **CANNOT FAIL** |
| R225b sparsity | 1.0000 | 1.0000 | 0.5000 | 0.9970 | **CANNOT FAIL** |
| R228 recovery | 0.0870 | 0.7269 | 0.9000 | 0.7269 | **CANNOT PASS** |
| R227 richness | 0.0182 | 0.9993 | 0.0527 | 0.0690 | admissible (5% of band) |
| R226 entropy | 0.0000 | 6.2288 | 3.0000 | 5.9561 | admissible (96% of band) |

**Controls on the checker itself** — a checker that has never caught anything is silence, not an
acquittal:

- **positive**: fires on **4/4** known-bad thresholds ✔
- **negative**: silent on **2/2** admissible ones ✔

## Two distinct kinds, and only one is about the number

**`floor == ceiling`** (R221, R225a, R225b) — the statistic returns the *same value* under a maximal
plant as under none. **No threshold on it is admissible, and the defect is the statistic, not the
number I picked.** Tie-count saturates at both ends; selection rate under a rank-fitter is blind to a
winner-predictor. Choosing a better number would not have helped.

**threshold outside a real band** (R228) — floor 0.0870, ceiling 0.7269, threshold 0.9000. The band
exists and the number was simply wrong.

**Diagnosing which kind you have requires computing the ceiling, which is the step all four skipped.**

## A free diagnostic the band gives

`headroom_used = (observed − floor) / (ceiling − floor)`. R227 used **5%** of its band — the effect
was tiny relative to what the design *could* have detected. R226 used **96%** — near-saturated. That
number distinguishes *"small effect"* from *"instrument nearly maxed"*, which a bare p-value or a
bare threshold comparison cannot.

## Register

Whether the 217 rounds **before** E05 have the same defect is **UNVERIFIED, not clean**. They do not
record their ceilings, so the check cannot be retro-applied without re-deriving each one — and
claiming a clean sweep over the subset that happens to be machine-readable is the
completeness-over-a-visible-subset failure this repository has hit before.

## The sentence that can no longer be written

*"The positive control failed, so the instrument is broken."* In four cases out of four the
instrument was fine and the threshold was impossible.
