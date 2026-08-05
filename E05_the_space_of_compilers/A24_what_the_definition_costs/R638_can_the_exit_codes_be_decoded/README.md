# R638 · `EXIT 1` denotes 18 different worlds across 19 rounds — there is no fix, only a prohibition

**Decision this makes safe:** whether to build the exit-code decoder my closing line called "one
line". **No — it cannot be built at all.**

| | |
|---|---|
| rounds with a `run.py` (self excluded) | **313** |
| declaring an `EXIT` convention | **95 (30.4%)** — the 43-round subset's 34.9% **holds** |
| `EXIT 0` | 95 rounds, **85 distinct meanings** |
| **`EXIT 1`** | 19 rounds, **18 distinct meanings** |
| `EXIT 2` | 19 rounds, **15 distinct meanings** |

**Essentially one meaning per round.** `EXIT 1` is `W-REFERENCE` in two rounds and something unique
in every other — *"a control misbehaved"*, *"kill fired (downgrade owed)"*, `W-BOTH or W-THIRD`,
`W-CONFOUND or W-BOTH`…

> **No generic harness can decode it. The only sound rule is the weak one: NON-ZERO DOES NOT MEAN
> FAILURE.**

⭐ **So "the fix is one line" is false in a deeper way than cost — there is no fix, only a
prohibition.** ⚠ And I made uncomputed cost claims in **both** directions in three rounds:
*"re-runs are expensive"* to avoid work, *"the fix is one line"* to justify it. **Neither measured,
both felt obviously true.**

## ⛔ The negative control failed, and it caught my own grep rather than this instrument
v1 asserted R431 declares no convention — from `grep -E "EXIT [0-9]"`, **a single space.** R431:9
reads:
```
EXIT  0 W-COMPOSITION · 1 W-CONFOUND or W-BOTH · 2 UNVERIFIED
```
**Two spaces.** ⭐⭐ **So all five of R636's "failures" were verdicts and NONE was a failure** —
retraction 607's *"only R431 shows none"* was a whitespace artifact. Repaired to a round **verified**
to have no `EXIT` line (219 of 314 qualify), so the control tests the instrument instead of my prior.

## Controls
| control | returned |
|---|---|
| **positive** — the 4 rounds known to declare a convention | **4/4** — PASS |
| **negative** — a round verified to have no `EXIT` line (`R276`) | **not found** — PASS |
| **g=0** — rounds matching the pattern but yielding no mapping | **0** — PASS |
| **placebo** — an exit code no round declares (`7`) | **0** — PASS |

**MULTIPLICITY:** 313 rounds × 3 exit codes + 4 controls. Full distribution printed.

**IMPOSSIBLE, both directions named and neither favourable:** the 30.4% is a **LOWER** bound (a round
can encode a convention without the word `EXIT`); the 18 meanings are an **UPPER** bound (two wordings
may name one world). ⚠ And **a docstring is not the code** — this measures what the corpus
*declares*, and R636 showed declaration and behaviour can disagree in the other direction.

## The sentence I can no longer write
> *"classify a round's exit by its declared convention."*

**There are 18 conventions for one code.** The declaration is per-round private vocabulary, not a
protocol.

## NEXT
The prohibition is cheap to install and needs no decoding: **any harness that runs a round must treat
a non-zero exit as UNKNOWN, never as failure.** R636 is the only harness in the corpus that runs
rounds — **check whether its `failed` count is used anywhere downstream**, because if it feeds only a
printed line the repair is a wording change, and if it feeds world C's threshold then the
fires-on-nothing derivation is live in committed code and outranks the wording.
