# R626 · Anchoring does carry information — and my pre-registered direction was backwards

**Decision this makes safe:** whether R625's 36% collision floor voids anchoring entirely. **No.**
Conditioned on matching, multiplicity separates measurements from coincidences — **in the direction
opposite to the one I registered.**

| arm | n | median m | mean | **m = 1** | **m ≥ 10** |
|---|---|---|---|---|---|
| document decimals | 619 | 3.0 | 4.94 | **30.7%** | 13.6% |
| random, matched — seed 0/1/2 | 1446 / 1505 / 1407 | 1.0 | ~2.5 | **52.9 / 54.4 / 55.6%** | ~4.3% |
| **gate-re-derived (T1)** | 188 | **14.5** | 48.47 | **6.9%** | **59.6%** |

> **m = 1 is the COINCIDENCE signature. High multiplicity is the MEASUREMENT signature.**

**A load-bearing number is re-persisted across many rounds** — cited, re-checked, carried into later
artifacts. **An invented number collides in exactly one place.**

## ⛔⛔ The pre-registration had the sign wrong, and the negative control is what caught it
I registered *"median(doc) ≥ median(random) → world B, anchoring is its own null"*, reasoning that a
real measurement is **rare** and a coincidence is **common**. **The arm I wrote expecting to be
rarest — the values the live gate re-derives — has the HIGHEST multiplicity of all three, 14.5 against
the corpus's 1.**

⭐ *A pre-registered threshold with the wrong sign fires confidently on data that refutes it.* The
kill as written returned **world B** while `30.7% vs ~54%` at `m = 1` refutes world B decisively.
**§4's remedy — a kill is a conditional, not a threshold — needs a companion clause: the conditional
must include the arm that establishes the direction.** Mine did, as a control, and I had labelled it
`NEGATIVE` while treating its result as advisory.

## Controls
| control | returned |
|---|---|
| **g=0** — random draws must reproduce R625's rate | **36.1% · 37.6% · 35.2%** — PASS |
| **seeds** — the flag must actually change the draws | 3 distinct prefixes — PASS |
| **positive** — R621's fabricated `0.9187` must behave like a draw | carried by **1** round, corpus median **1** — PASS |
| **negative** — gate-re-derived values | **median 14.5**, and this is what reversed the sign |

**MULTIPLICITY:** 619 document decimals + 4,358 matched random draws across 3 seeds + 188 T1 values,
full distributions reported (median, mean, `m=1`, `m≥10`).

**IMPOSSIBLE, named:** a **shared instrument bias cancels in Δ** and is invisible here. And **rarity
is not correctness** — a value carried by one round can still be wrong in that round, which needs the
round's re-execution. ⚠ **DERIVATION, not evidence:** that a match is informative only where it is
improbable follows from the definition of a likelihood ratio; **what was measured is which direction
improbability runs**, and that could have gone either way.

## What this restores, and what it does not
- **R625's 36% floor stands** and is why `m = 1` cannot be read as provenance.
- **R622's `T2 anchorable 79.0%` is still overstated**, but not empty: **the T1 arm's separation is
  large** (m≥10: 59.6% vs 4.3%) and is the first measured discrimination this arc has produced.
- **Nothing here says any number is correct.**

## The sentence I can no longer write
> *"a value carried by one round is evidence; a value carried by forty is a coincidence with a
> citation."*

**Exactly inverted.** Both halves were illustrative numbers in a closing line, and a later round would
have built a threshold on them.

## NEXT
Multiplicity separates the arms, so the usable question is now a threshold rather than a boolean:
**at what `m` does the document population stop looking like the random one?** Sweep `m ≥ 1..20`,
report precision and recall against the T1 arm as the positive class and matched random draws as the
negative, **and report the whole curve** — because the previous four rounds each picked one cell and
three of them were reporting laxity.
