# R976 · φ\* is the design's resolution, not a property of clause ④

**THE DECISION THIS MAKES SAFE.** Whether clause ④'s reach can be stated as a fact about the clause.
It cannot: the boundary has a closed form in **δ, N, the lattice step and z**, with **no corpus term
and no free parameter**. Any statement of ④'s exclusion power that omits N and δ is unscoped.

---

## The arithmetic, written before the compute

R975 closed by saying the cheapest separator was to resample the corpus. Rung 2 comes before rung 4.
④'s removal is `hi < 0`; the margin is pinned at −δ by construction; the interval is ≈ `z·sd(d)/√N`.
On the lattice, `d` takes ±STEP on the `φN` raised prompts and on the `δN/STEP + φN` lowered steps:

```
sd(d) ≈ STEP·√(2φ + δ/STEP)      removal fails when   z·sd(d)/√N ≥ δ

  ⇒   φ*(δ, N) = [ δ²N / (z·STEP)² − δ/STEP ] / 2
```

Evaluated on R975's grid this gives **0.4236 / 1.7542 / 11.1890** for δ = 0.01 / 0.02 / 0.05, and
R975 measured the boundary inside (0.30, 0.40] for the first and removal everywhere for the other
two. ⚠ **That is a post-hoc fit**, which is why it is not the finding.

## The out-of-sample test — φ\* linear in N, quadratic in δ

Registered before the run: **φ\*(968)/φ\*(484) = 2.152** under world B; **[0.8, 1.25]** under world A
(φ\* a property of the clause or the corpus).

**Measured per seed: 1.500 · 2.714 · 2.250.** All three above world A's band. **World A is dead.**

⚠ **Report the spread, not the mean** — the seeds do not agree tightly, and the φ grid is quantised
at 0.025, which at φ\*≈0.2 is already ±6%.

## The whole 16-cell table, against a prediction with no free parameters

| N | δ=0.008 | δ=0.010 | δ=0.012 | δ=0.016 |
|---|---|---|---|---|
| **242** | .050/.075/.075 · *0.049* | .100/.100/.125 · *0.083* | .100/.125/.150 · *0.127* | .250/.225/.275 · *0.242* |
| **484** | .150/.125/.125 · *0.121* | .250/.175/.200 · *0.197* | .375/.325/.325 · *0.291* | .500/—/.500 · *0.533* |
| **726** | .175/.250/.200 · *0.194* | .275/.300/.325 · *0.310* | .425/.450/.450 · *0.454* | —/—/— · *0.823* |
| **968** | .250/.275/.300 · *0.266* | .375/.475/.450 · *0.424* | .500/—/— · *0.617* | —/—/— · *1.113* |

*(three seeds · prediction in italics; “—” = still removed at φ = 0.5)*

- **13 of 14 measured cells within 1.5 grid steps** of the prediction. Mean |error| **0.0214**,
  against a grid quantisation of **±0.0125**.
- The one outlier, `968 | δ=0.012` (predicted 0.617, measured 0.500), is **right-censored**: the
  prediction lies outside the grid and 2 of 3 seeds never crossed at all.
- **Both cells with no boundary have predicted φ\* > 0.5** — 0.823 and 1.113. The form's misses are
  where it says there should be none.

## Controls, and what they returned

| control | result |
|---|---|
| **OBJECT** | 968 prompts, floor `0.455679` — reproduces R821 exactly |
| **POSITIVE** | N=968, δ=0.010 boundary in (0.30, 0.50] on **every** seed — reproduces R975 |
| **PLACEBO** | δ=0 removals across all cells: **0 of 36** |
| **NEGATIVE** | margin spread across φ within a (N, δ) cell: **1.04e-17** |
| **NOISE FLOOR** | 0.00482 → 0.00224 across N=242→968; ratio **2.154** vs √4 = 2.000 |

**1,008 cells tested, all recorded**, survivors and non-survivors alike.

## What this says about the definition

Clause ④ has **no free parameter**. Its exclusion power is `f(δ, N, STEP, z)` — the design's
resolution wearing a clause's clothes. Two consequences:

1. **`54bab0e3`'s headline is a statement about a 968-prompt design, not about the clause.** *"The
   0.01 detection is finer than the design's own half-split noise floor of 0.0067"* holds at N=968
   and φ≈0; at N=242 the same δ is defeated by φ ≈ 0.10.
2. **Any clause-④ claim must carry N and δ**, exactly as R975 showed it must carry overlap.

## The limit this round cannot cross

Subsampling varies **N**, not the corpus. The closed form contains **no corpus quantity** and
predicts 13 of 14 cells, so corpus-specific variance is **not required** to explain the table — but
that is not the same as measuring a second corpus, and this round does not claim it. Separating
*"this corpus's per-prompt variance"* from *"variance in general"* still needs a second release.

## Alternatives considered

**Fit z or STEP to improve agreement.** Refused: both are fixed by the design (a 95% bootstrap
interval; agreement over 6 pairs). A fitted constant would convert a zero-parameter prediction into
a one-parameter description and destroy the only thing that makes this severe.

**Extend the φ grid past 0.5 to capture the censored cells.** Rejected for the reason R975 gave: an
arm above the floor on most prompts with a negative mean is a pathological object, and the two
censored cells already agree with the form by being censored.
