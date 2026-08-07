# R501 · Can clause ③'s provenance be replaced by a behavioural test? — UNVERIFIED, and the round says why

**Decision this was meant to make safe:** whether the definition can become object-level. **It is not
made safe.** The chosen instrument failed its own positive control, so the null is silence.

## The derivation that needed no measurement

R465 measured a label-reading and a label-free selector emitting **identical criteria on 9 of 967
prompts, with identical A2 to machine precision**. It follows — a **derivation**, labelled as one —
that ***core* as written is not a predicate on criterion sets, but on *(criterion set, construction
history)* pairs.** A third party handed only the artifact can never decide clause ③. That is settled
by arithmetic; this round asked whether it is *forced*.

## What ran, and what stopped it

| control | result |
|---|---|
| **POSITIVE** — `oracle_k4`, the **maximal** label-reader, must rank at an extreme | ⛔ **rank 11 of 23 — dead mid-pack. FAIL.** |
| **NEGATIVE** — family labels shuffled, 200 draws | residual sep **0.334**, 95th pct **0.863** |
| **PLACEBO** — `random_k4` seeds, identical construction | relative sd spread **0.016** (a floor, as it should be) |
| grid | **6 cells** (2 statistics × 3 offsets), **0** clearing the shuffled bar |

**Verdict: `UNVERIFIED`.** Not World A. A zero from an instrument that cannot localise the most
extreme case on the site is **silence, not an acquittal.**

## ⛔ What the round did wrong, and it is the same row twice in two rounds

The first verdict printed **`A PROVENANCE IS IRREDUCIBLE`** while the positive control was failing
two lines above it — **§4's "the verdict string is not a computation", sub-kind ①, committed in the
round immediately after logging that exact failure in R500.** The branch now references the control,
and a failed control yields `UNVERIFIED`, never `A`.

## ⭐ The arithmetic trap, and why the big number was never evidence

Raw separation between the families is **d ≈ 1.11** — large, and worthless. **Label-readers score
higher by construction**, and per-prompt sd tracks mean A2, so the raw statistic is `1+1=2` wearing a
result's clothes. Conditioning on mean A2 halves it to **0.49**, below the shuffled-label bar. **The
design was built around this trap from the start — the estimand was a residual, never a raw
statistic — which is why the failure landed on the control rather than in the conclusion.**

## ⛔ And a scope error caught only by a crash

The first arm list included `transport_generic`, `transport_randblind_*`, `transport_vacuous` as
③-admissible. Their meta keys carry **four** fields (`c365|int10006|ut3170|0`) against this
population's three (`<uuid>|0|A`): **they are scored on the second release.** Coercing the key would
have compared label-readers on one corpus against label-free arms on two, silently. **A schema guard
now refuses any arm whose key shape differs and prints the exclusion**, so it can never be invisible.
**It was a crash, not diligence, that caught this.**

## What is established, narrowly

**Per-prompt A2 dispersion, residualised on mean A2, is not an instrument for provenance on this
population.** A candidate instrument must first be shown to rank `oracle_k4` at an extreme. The
question itself is untouched.
