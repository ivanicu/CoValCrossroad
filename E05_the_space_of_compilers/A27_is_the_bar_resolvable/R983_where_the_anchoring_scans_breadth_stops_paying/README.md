# R983 · the anchoring scan is over-broad by ~4×, and reporting an unbacked number backs it

**THE DECISION THIS MAKES SAFE.** How wide the anchoring scan should be. **Not as wide as possible.**
J peaks in the low hundreds of artifacts and is ~3–4× better there than at the full 785.

---

## ⭐ The floor is a count, not a sample

R625 and R982 both estimated the collision floor by drawing thousands of random decimals. A 4-place
decimal on [0,1) lives on a 10,000-point grid, so

```
floor(scan) = |values(scan) ∩ grid| / 10000
```

**exactly**. On the full corpus: **9202 / 10000 = 0.9202**, registered before the sweep, against
R982's sampled 0.919 / 0.922 / 0.912 and this round's own 12,000-draw check of **0.9247**
(|diff| = 0.0045, 4·se = 0.0096 — **PASS**). Every point on the curve below is noiseless in the
floor dimension because of it.

## The breadth curve — J = recall − floor

| b | recall | floor | **J** (seed 1) |
|---|---|---|---|
| 0 | 0.000 | 0.000 | +0.000 |
| 25 | 0.303 | 0.101 | +0.202 |
| **100** | 0.545 | 0.238 | **+0.307** |
| 200 | 0.844 | 0.632 | +0.212 |
| 400 | 0.928 | 0.689 | +0.239 |
| 600 | 0.982 | 0.902 | +0.080 |
| **785** | 1.000 | 0.920 | **+0.080** |

**argmax J per seed: 100 · 200 · 200 · 400 · 100.** ⚠ **The spread is the report** — b\* is "the low
hundreds", not a number. What is solid: **every seed peaks strictly inside**, and J at the optimum
(+0.30 to +0.34) is **3–4× J at the full scan (+0.080)**.

**Mechanism:** recall saturates faster than the floor. By b = 400 recall is already ~0.95 while the
floor is still climbing toward 0.92 — the last 385 artifacts buy 5 points of recall and pay 23 points
of floor.

## Controls

| control | result |
|---|---|
| **POSITIVE** | the *derived* floor reproduces a *sampled* one within 4·se — this tests the closed form, which is the new part of the instrument, rather than restating `recall(full) = 1` |
| **NEGATIVE** | at b = 0: floor, recall and J all **exactly** 0 |
| **PLACEBO** | a runtime-assembled decimal is absent from the full scan, so the floor is below 1 and the test is not vacuously saturated |

⚠ **`recall(full) = 1` is a DERIVATION** — the ground truth *is* the full scan. It is why the
positive control targets the floor instead.

## ⛔ And the finding I did not go looking for: publishing an unbacked number backs it

R982 reported **7 unbacked decimals** and listed them in its artifact:
`0.2796 · 0.3528 · 0.7803 · 0.7999 · 0.8482 · 2.1458 · 5.3997`.

This round scans R982's artifact — and finds **7 of 7 of them present**. They are now "anchored"
**by the record of their own exposure**, which is why R983 sees 0 unbacked where R982 saw 7.

⭐ **This is exactly the failure R622's v1 had** — a fabricated `0.9187` landing in the anchorable
tier because the round exposing it recorded the string — reappearing at a new site with a different
mechanism. R622 fixed it by walking *parsed value positions* instead of raw text. **That repair does
not help here**, because R982 wrote its unbacked list as genuine JSON values.

**So the anchoring test decays as the project audits itself.** Every audit that names a suspicious
number adds it to the corpus the next audit searches. The mitigation is the one this round already
applies — exclude the reporting round's own directory — but it does not generalise past one round,
and it is a structural property rather than a bug to patch.

## What this does not say

- **J optimises a detection trade-off, not correctness.** A decimal found by the optimal scan is
  still only "some artifact holds these digits" — R949 measured quantity-level agreement at 0.200.
- **The grid argument is 4-place-specific.** At 3 places R625 already measured ~92% and at 2 places
  100%, so there is no headroom to optimise there at all.
- **One corpus.** The saturation curve is a property of this project's artifact volume.

## Alternatives considered

**Recommend the full scan anyway, for completeness.** Refused: it is measurably the worst cell on the
curve outside b = 0, and "scan everything" is the choice that feels rigorous while costing 3–4× the
discriminating power.

**Pick b\* = 200 as the recommendation.** Refused as a point estimate. Two seeds say 100, two say
200, one says 400. Reporting 200 would be choosing a seed.
