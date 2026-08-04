# R323 — the last unexplained number was `NCAL`, and it reproduces to six decimals

**Decision this makes safe:** whether anything in the four-detector spread is still unaccounted
for. **Nothing is.**

## The residual R322 left

R268 reports `tau = 0.416`, R274 reports `0.424` — same tensor, same 250 prompts, and R322 proved
it is **not** a replicate effect (`tau` is identical at 40, 100 and 400 REPS).

Reading both scripts:

```
R268   REPS, NCAL, NHOLD = 100,  200,  200
R274   REPS, NCAL, NHOLD = 400, 3000, 3000
```

Identical construction on both sides — `cal = [arm_value(0.0, default_rng(10_000 + i)) …]`, then
`tau = quantile(cal, 0.95)`. Same seed formula. And at `g = 0` the two `arm_value` bodies consume
the same rng draws in the same order: R268's `carry[i] and rng.random() < g` short-circuits exactly
as R274's `mode == "real" and rng.random() < g`, because `carry` is all-True when `sham=False`.

## W-NCAL

| round | NCAL | `quantile(0.95)` of R274's prefix | committed tau | \|diff\| |
|---|---:|---:|---:|---:|
| R268 | 200 | **0.416000** | 0.416000 | 0.00e+00 |
| R274 | 3000 | **0.424000** | 0.424000 | 0.00e+00 |

**Both committed taus reproduced from one array of draws, to six decimals.** R268's calibration set
**is** the prefix of R274's. The entire gap is the calibration size — a 95th percentile from 200
draws against one from 3000 — and **there is nothing left over.**

## ⚠ And it could have come out otherwise

Different seed offsets, a different `arm_value`, a different `P` or `delta` would each have broken
the match. `the arithmetic trap` asks whether the algebra forced the result: **it did not.** This is
a measurement of code identity, reported as exact.

## Controls

| control | result |
|---|---|
| **positive** — the 3000 cell must reproduce R274's own tau from its own dumped array | 0.424000, exact |
| **estimator moves** — prefix sweep must take more than one value | 4 distinct of 7 |
| **negative** — an *unused* prefix must match neither committed tau | 400 and 500 give 0.4280 |
| placebo | n/a and stated: this is an identity check, and inventing a contrast that must return zero would be decoration |

**Prefix sweep:** `100:0.4242 · 200:0.4160 · 400:0.4280 · 500:0.4280 · 1000:0.4240 · 2000:0.4240 ·
3000:0.4240`. Note 200 is the *lowest* value in the sweep — R268 drew the short straw, not a
systematically lower threshold.

## Noise floor

`cal` lives on a lattice (a proportion over ~250 prompts), so nearby prefix lengths tie — 1000, 2000
and 3000 all give 0.4240. That is the resolution, and it is why the sweep is reported whole rather
than as a trend.

## Scope

R274's committed calibration draws at `g = 0` · `arm_value` on the canonical tensor · `ALPHA = 0.05`.
`cal_dump.npy` is committed beside the artifact so a later round can attack this without re-running
R274.

## What this does not touch

R267's dose grid and rule differences — a different estimand (R321), and not addressed here.
