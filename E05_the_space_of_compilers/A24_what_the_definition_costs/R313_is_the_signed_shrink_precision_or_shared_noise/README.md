# R313 — is the signed shrink-vs-precision relation a property of the ARM, or of this judge's measurement of it?

**Decision this makes safe:** whether R312's recorded `R² = 0.3954` may be carried forward as
evidence that precisely-measured arms survive the smaller judge. **It may not.**

## The question

R312 left a number with no null: `corr(1/SE_0.8B, signed residual) = −0.6288`, four times what
rule membership explains. R312 refused to claim it and named the reason — no floor. This round
builds the floor, and one control the absolute-value statistic did not need.

## The trap this statistic carries and the previous one did not

The residual is built from the 0.8B effect. The covariate is `1/SE_0.8B`, estimated from **the
same cluster bootstrap over the same prompts**. If a realisation whose sampling error pushed
`eff_08B` off the line also moved its own `SE_08B`, covariate and outcome share an estimation
error and the correlation is manufactured.

Simulating at the observed SEs does **not** address this — that null holds SE fixed and true,
so it cannot contain the channel under suspicion. `realstat §4 · a control validated by its own
instrument's noise`.

## The separator, and it is free

The 2B judge supplies a second precision, `1/SE_2B`, estimated from a different judge's
outputs. It **cannot** share estimation noise with a residual built from 0.8B effects. The two
correlate at **+0.804**, so they largely measure a common latent property of the arm.

| instrument | corr(precision, signed residual) | R² | vs its own floor |
|---|---:|---:|---|
| `1/SE_0.8B` — shares a bootstrap with the outcome | −0.6288 | 0.3954 | **OUTSIDE** [−0.299, +0.313] |
| `1/SE_2B` — cannot | −0.2548 | 0.0649 | inside [−0.293, +0.290] |

## The estimand is a mixture fraction, not a pair of pure worlds

Two pure worlds would not span the outcome space — R301's defect, diagnosed in R310. So the
estimand is **f**, the share of the relation carried by the component both judges measure.
Each `(f, g)` is simulated, and the observed **pair** is scored jointly by Mahalanobis against
that world's own 2-D cloud — not by calibrating one coordinate and testing the other, which
conditions on the match.

**Admissible: f ∈ {0.0, 0.1, 0.2, 0.3}. Everything from f = 0.4 up is excluded at every dose.**
Peak p = 0.790 at f = 0.2, g = 0.45. Identical admissible set at 3 disjoint seed blocks.

## Controls

| control | result |
|---|---|
| PLACEBO `corr(e2, residual)` | +1.16e−16 — **a DERIVATION**, OLS forces it; tests the code, not the world |
| NEGATIVE floor, 400 sims × 2 blocks | 8B [−0.299, +0.313] · 2B [−0.293, +0.290] |
| POSITIVE f=1 plant at the observed size | 2B recovers −0.707, **clears its floor** — the 2B null is not blindness |
| g = 0 | 2B +0.051, lands **on** the floor |
| CEILING maximal plant, no noise | 2B −0.983, outside the floor — **a threshold is admissible** (R312 died here) |
| seed | admissible set identical at blocks 4000 / 12000 / 20000 |

## Robustness — reported beside the verdict, not gating it

- **leverage** drop-one over all 39 arms: 8B ∈ [−0.662, −0.594], 2B ∈ [−0.300, −0.202]. The 8B
  relation stays below its floor after **every** single-arm drop; worst drop is `generic`.
- **estimator** Spearman −0.712 vs −0.288 — the ordering survives ranks and widens.
- **reliability** if both measured one latent precision, disattenuating by `√0.804` would make
  them equal: −0.701 vs −0.284. The residual gap **0.417** is what the f-surface measures.
  *[DERIVATION under that assumption.]*

## Verdict — W-SPECIFIC

The signed relation lives in the component of `1/SE_0.8B` that `1/SE_2B` cannot see. It is a
property of **this judge's measurement of the arm**, not of the arm. Its natural reading —
precisely-measured arms survive the smaller judge — requires f ≥ 0.5, which the data excludes.

**⚠ Not named `artifact`.** The 0.8B-specific component contains *both* shared bootstrap noise
*and* any genuine 0.8B-specific precision. This design separates *generalises across judges*
from *does not*; it does **not** isolate a mechanism. Naming one would be the verdict string
asserting what nobody computed.

## Specifications — both run, both reported

1. **MARGINAL** (run first): dose each f so its 8B coordinate matches the observed, then test
   the 2B coordinate alone → admissible **f ≤ 0.25** on a 5-point grid.
2. **JOINT** (reported above): Mahalanobis over an 11 × 12 surface, no conditioning →
   admissible **f ≤ 0.3**.

The second was written because the first conditions on one coordinate — a design defect — not
because of what the first returned. They agree.

## Multiplicity

134 cells: 2 instrument-vs-floor + 132 `(f, g)`. **No correction applied, and the reason is
computed rather than assumed:** more cells gives a high-f world *more* chances to admit by
chance, so multiplicity makes the exclusion of f ≥ 0.4 **harder** to obtain, not easier. Zero
degenerate cells.

## Scope

39 arms of R301's fit · Qwen3.5-2B and 0.8B · baseline `random_k4_s0` · clause ① effects,
A2·annotator · one release.

## What this site structurally cannot do

- **separate shared bootstrap noise from genuine 0.8B-specific precision** — needs independent
  re-judgings per arm. The release has 2, enough for R309's noise estimate, not for a slope.
- **a third judge**, which is what would break a tie had the surface been flat. It was not.
