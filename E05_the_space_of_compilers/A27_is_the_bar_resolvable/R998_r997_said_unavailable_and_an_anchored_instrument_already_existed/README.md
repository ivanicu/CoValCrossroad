# R998 · R997 said "unavailable"; an anchored instrument already existed and returns 14

**THE DECISION THIS MAKES SAFE.** Whether the retraction→round join exists. **It does** — at 14
edges, via an instrument this project built at R951 and I did not check for before declaring a wall.
**R997's claim is corrected**, and R996's bound is not.

---

## Three instruments, one population

| instrument | entries | note |
|---|---|---|
| R954 **structured header** | **0** | R997's measure — the format binds from entry 1388, ledger stops at 1387 |
| R951 **anchored relation** | **11** (**14 round edges**) | a relation phrase gating `R\d+`, **per sentence** |
| bare `R\d{2,4}` scan | **799** | uncalibrated — 73× the anchored count |

**R997 was right that the bare scan is uncalibrated. It was wrong to conclude the join is
unavailable** — "uncalibrated bare scan" and "no join exists" are different claims, and it asserted
the second. ⭐ **That is the fabricated-impossibility direction: a wall makes stopping feel earned, so
nobody audits it.** Caught one round later by R997's own NEXT.

## ⛔ And my first attempt claimed verbatim reuse that was a paraphrase

v1's comment read *"R951's instrument, reused **VERBATIM**"*. It was reconstructed from memory:

- R951's third alternative is `as R\d+ (?:caught|found)`; I wrote `(?:this|it) is the same`
- **R951 matches per SENTENCE** (`for s in sentences(body)`, `run.py:125`); I matched per entry

Result: **42 entries / 100 edges against a committed 14**, and the positive control refused it.
Copied from the source — with the sentence split — it reproduces **14 exactly**.

⭐ **A claim of verbatim reuse is checkable, and mine was false.** The control is the only reason
that did not reach a report.

## Controls

| control | result |
|---|---|
| **POSITIVE** | reproduces R951's committed **14** edges — **it already failed once and caught a paraphrased instrument** |
| **NEGATIVE** | the anchor **matters**: 799 bare vs 11 anchored, **73×** — without this, the gating could be doing nothing and R997's objection would stand |
| **PLACEBO** | a round id with **no** relation phrase (`"this withdraws what R123 established"`) is not counted |

## ⚠ The correction is to the claim, not to the number

**14 edges against 504 finding-typed unmentioned rounds.** Even if every edge retracted a distinct
one, 504 → 490. **R996's bound survives.** What does not survive is R997's wording, which is narrowed
to *unavailable via R954's header*.

**Inherited limit (R951's own):** the 14 are a **lower** bound — two entries can concern the same
round and say so nowhere.

## Alternatives considered

**Leave R997 standing, since the number barely moves.** Refused: the claim was wrong regardless of
whether the correction is consequential, and a wall left standing is one a later round routes around
instead of testing. §4's row exists because an unchecked wall is UNVERIFIED, never SETTLED.

**Re-derive R951's regex "better".** Refused: the point was to reuse its instrument, and improving it
mid-comparison would have meant measuring a third thing while claiming to reproduce the first.
