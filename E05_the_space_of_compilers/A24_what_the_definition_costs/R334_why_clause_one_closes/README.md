# R334 — clause ① closes, and both of my predictions of *why* were wrong

**Decision this makes safe:** whether R331's percentile rule must be applied to clause ① too.
**No — and not because clause ① is stronger.** Its reference class is **quality-degenerate**: the
members are exchangeable, so there is no percentile to sit at. **W-DEGENERATE.**

## The two classes are not the same kind of object

| | clause ① | clause ② |
|---|---|---|
| a member is | *draw k=4 from **this prompt's** rubric*, per prompt | **one fixed** quadruple of the generic pool, applied to every prompt |
| members differ by | which draw they realised — averages out over 968 prompts | **real quality**, A2 spanning 0.5144–0.5575 |
| **τ / se** | **0.72** *(0.70, 0.71, 0.76)* | **3.61** *(3.54, 3.57, 3.72)* |
| **closure rate** | **0.0000** | 0.0033 |

`τ` = across-member sd of the margin · `se` = mean sampling error. **Both classes judged against
their own published reference.**

## ⛔ Two predictions, both wrong, and they were wrong in opposite directions

**① R333's**: *"clause ①'s margins are 5.6× rather than 1.19×, so it closes trivially."* **The
margin is irrelevant to closure** — closure is about the reference's altitude in its own class.

**② The naive transfer of R331's curve**: clause ①'s reference `random_k4_s0` **is itself a random
draw**, so it sits at the *median* of its class — and R331 measured a p50 reference admitting
**23.3%**. That predicts clause ① is the **worst** case.

**Neither. Exchangeability decides it**, and it is a property of the class rather than of the
reference or the margin.

## ⛔ And my declared derivation was off by √2 — corrected *from* the measurement

I wrote *"exchangeable ⇒ τ/se = 1"*. It is **1/√2 ≈ 0.707**: `τ` is the across-member sd of a
member's own mean, while `se` comes from `D = member − reference`, **a difference of two independent
draws**, whose per-prompt sd carries a √2 the numerator does not.

**Clause ① measures 0.70–0.76.** Dead on. **I would have read a perfect result as a 30% shortfall.**

## Controls

| control | result |
|---|---|
| **positive** — reproduce R294's committed clause-① margin | `0.073790483396` **exact to 1e-12** |
| **positive @ g=0** — a member that *is* the reference | gap `+0.0e+00`, does not clear |
| **negative · calibration** — real members + a *known* injected shift, dose-response | see below |
| **sham vs neutral** — §4, both built | poison **−0.0625**, neutral **+0.0484** |
| **cross-round** — my *sampled* rate vs R331's *exhaustive* census | 0.00333 vs 0.00165 (3/1820), **z = 0.72** |
| **placebo** | 0.0 |

### The calibration, with a predicted value at every dose

| δ | predicted τ/se | measured | ratio |
|---:|---:|---:|---:|
| 0.000 | 0.76 | 0.76 | 1.000 |
| 0.005 | 0.81 | 0.81 | 0.997 |
| 0.010 | 0.95 | 0.95 | 0.996 |
| 0.020 | 1.38 | 1.37 | 0.996 |
| 0.040 | 2.42 | 2.42 | 0.998 |
| 0.080 | 4.67 | 4.66 | 0.999 |

**Max |measured/predicted − 1| = 0.004, monotone in dose.** The statistic recovers a known shift.

### ⚠ Two earlier versions of this control failed for their own reasons

**v1** built "structure" from top-**spread** criteria as an importance proxy and got τ/se = **0.58**,
*below* the random class. **R294 already measures `topvar_k4` at A2 0.4863 — worse than random.** The
dose was a dose of something that doesn't help: §4 `control validated on imagined cases`.

**v2** recovered the injected shift to **0.996 of prediction** and was failed by an `and syn_ratio >
3.0` clause I typed because I wanted a big number. §4 `the control fails for its own reasons`,
sub-kind ④ — **the branch tested the wrong question.**

### ⚠ And v1 judged both classes against clause ①'s reference

That made clause ②'s "closure rate" **1.0000** — blind-pool-vs-rubric-random, a different question
entirely, and the neutral arm (+0.0484) says so directly. **A rate against the wrong reference is not
a rate.**

## What this settles for the definition

> **R331's percentile rule governs clause ② only.** Clause ② needs a *named, computed* reference
> because its class has real quality spread. **Clause ① does not, because any member of its class is
> as good a reference as any other** — and that is a structural fact, not a margin.

## Scope

968 CoVal prompts with ≥2 annotators, 15,593 annotations · Qwen3.5-2B-Base under R234's canonical
builder · per-prompt rubrics from `sat_full.npz` (median 15 criteria, min 4, max 39) · k=4 ·
200 members × 3 independent blocks × 2 classes.

## What this cannot do

**Enumerate clause ①'s class.** It is `C(n_p, 4)` *jointly* over 968 prompts, so the rate is a Monte
Carlo estimate and carries binomial error — **R331 could report an exhaustive census for clause ②;
this round cannot for clause ①.** A second release would not fix that: it is a property of the class,
not of the site. The cross-round control is what compensates, and it validates the sampler against
the one census that exists.
