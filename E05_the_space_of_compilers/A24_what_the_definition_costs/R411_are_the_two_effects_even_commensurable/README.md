# R411 — the naive comparison said 0.96×; standardised it is 2.50× or 4.57×, and the clustering unit decides which

**The decision this makes safe:** *should the second-corpus replication be run as R410 stated it?*
**Not as stated — and the number that would have decided it was in the wrong units.**

## Result — `W_MARGINAL`. Gauge test passes **after its own repair**. **No GPU.**

| comparison | value | reads |
|---|---:|---|
| **NAIVE** — effect `+0.009002` (A2 units) ÷ R401's MDE `+0.009360` (accuracy units) | **0.96×** | "marginal" |
| | | ⚠ **meaningless** — numerator and denominator are not the same quantity |
| **STANDARDISED** `d = e/sd = 0.07814` ÷ `MDE_d = ZEFF/√n` | | |
| … at n = **26,789** interactions | **4.57×** | powered |
| … at n = **8,011** conversations | **2.50×** | marginal |

**The verdict takes the worse of the two: `W-MARGINAL`.**

## ⛔ R410's NEXT compared a length to a mass because both printed as four decimals

`+0.009` is in CoVal's **A2-agreement** units — the share of criterion-level verdicts matching a
human. R401's `0.0094` is in **"pick the chosen response" accuracy** units on the second corpus,
against a chance floor of **0.4328**. **Setting them side by side and reading "marginal" is a unit
error, and it was mine.**

**The fix is not to abandon the comparison but to standardise it.** `d = e/sd` is dimensionless; the
design's resolution in the same units is `ZEFF/√n`, a function of n alone.

## ⭐ And the real finding is that the clustering unit decides the answer

**4.57× vs 2.50×** is the same effect against the same design — the only difference is whether the
independent unit is the **interaction** or the **conversation**. R398 measured 8,011 conversations
holding 27,172 interactions, ≈3.4 per conversation. **If interactions within a conversation are
correlated, the effective n is nearer 8,011 and the replication is marginal; if not, it is powered.**

> This is the campaign's own *"name the estimand before the bound"* row: the same zero errors read
> 2.34% or 24.71% depending on the sampling unit. **Nobody has measured the within-conversation
> correlation on the second corpus, and until someone does, the power statement is a range.**

## ⛔ The gauge control failed for its own reasons, and the control was fixed — not the criterion

**First version**: added **uncentred** noise. Its own sample mean (`se ≈ 0.0039` at n=968) moved the
**signal** of 0.01 as well as the dispersion — **two changes, one question** — and `d` rose on one
seed.

**The criterion was right; the manipulation was not.** Repaired by **centring** the added noise so the
sample mean is preserved exactly and only dispersion moves. **The uncentred version is kept beside
it, averaged over 200 replicates**, where it does shrink — so the fix is visibly a repair to the
manipulation rather than a retreat to an easier criterion.

| | returned |
|---|---|
| **GAUGE (+)** | ×3 on every measurement is a change of **units** → `d` identical, `max\|Δd\| = 1.4e-17` — `PASS` |
| **GAUGE (−)** | **centred** noise is a change of the **object** → `d` shrinks — `PASS` |
| **NAIVE** | the wrong-units comparison is **computed and printed**, because *a described error is not a demonstrated one* |
| **SOURCE** | `e`, `se`, `n` read from R408's committed artifact, never retyped |

## ⚠ Conditional on an assumption that is not validated here and may be false

A standardised effect is comparable across metrics **only if the two measure the same construct with
different scaling.** CoVal's A2 agreement and `if_chosen` accuracy plausibly do not. **Validating it
needs both metrics on a shared population, which no object on this box provides** — so this is a power
statement *conditional on transport*, not a promise that the replication will resolve.

**And both `d` and `MDE_d` are DERIVATIONS** — a definition and algebra. Only the `sd` behind them was
measured. **The ratio is what this round adds.**

## The sentence I can no longer write

> *"the effect is +0.009 and the target design's MDE is 0.0094, so the replication is marginal"* —
> **those are different quantities.** Standardised, the same two designs give 2.50× and 4.57×, and
> which one applies is a clustering question nobody has asked.

Artifact: `results/r411_commensurability.json`, source-stamped.
