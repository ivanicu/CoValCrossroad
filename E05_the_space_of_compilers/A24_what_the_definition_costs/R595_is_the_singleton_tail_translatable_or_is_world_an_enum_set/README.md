# R595 · `world` is a genuinely open vocabulary — not an enum, and not an enum_set either

**Decision this makes safe:** **no mechanical repair of `world` is available.** The tail cannot be
folded into the core, and the compound evidence that would have justified an `enum_set` type change
is **letter co-occurrence, not verdict co-occurrence.**

**WORLD B OPEN**, unanimous across three matchers after the disagreement was resolved by a unit test.

| matcher | t (tail) | f (`why`) | f (README prose) | **excess** | compounds | plant | placebo |
|---|---|---|---|---|---|---|---|
| `prefix` | 0.1806 | 0.0000 | 0.0217 | **+0.1589** | **0.0000** | 1.0000 | 0.0000 |
| `word` | 0.2222 | 0.0444 | 0.1126 | **+0.1096** | 0.0046 | 1.0000 | 0.0000 |
| `substring` | 0.6528 | 0.1111 | **0.3577** | +0.2951 | 0.1944 | 1.0000 | 0.0000 |

**Core is `B` · `A` · `UNVERIFIED`, 80 of 317 occurrences = 25.2%.** 216 tail values. Under the two
matchers with clean false-positive rates, **only 18–22% of the tail carries a core token at all** —
far below the 60% bar, so there is nothing to fold.

## ⛔ The instrument my own NEXT line proposed would have found "translatable" by collision
R594 closed with *"test whether each sentence value contains exactly one core token as a prefix."*
The core tokens are **`A`, `B`, `UNVERIFIED`**. **Measured: the substring matcher fires on 35.77% of
random README prose.** §4's *a search is an instrument and has no positive control*, and the repair
it licensed would have rewritten real verdicts into letters chosen by an accident of spelling.

## ⭐⭐⭐ The specification curve disagreed, and a unit test resolved it — not a preference
`prefix` and `word` said **B OPEN**; `substring` said **C ENUM_SET** at a 29.8% compound rate.
§2.5 forbids adjudicating by picking the design you like, so the assumption they differ on was tested
directly.

**First test — is the compound rate collision with prose?** No: `substring` compounds run **0.1944 on
the tail against 0.0489 on control text**, a real 4× excess. *The obvious dismissal failed.*

**Second test, mechanical and decisive** — if `substring` finds ≥2 tokens where `word` finds ≤1 in the
**same string**, the extra tokens sit *inside words*:

> **41 of 42 = 97.6%**

```
'A STABLE'                          <- 'A' … and 'B' inside "STA-B-LE"
'A CORE IS A RANKER (score.py …'
'B (DIFFICULTY — the gradient is …'
```

⭐ **The compound signal is letter co-occurrence, not verdict co-occurrence.** `enum_set` is refuted,
and it was refuted by a **unit** test rather than by preferring a matcher.

## ⛔ Three defects in my own design, all caught by the numbers
1. **My "core" contained a 2,188-character JSON blob.** A value occurring ≥5 times is a *frequent
   value*, not a *categorical label* — v1 conflated them. Fixed with a **type** test (does it parse as
   a dict/list?), not an invented length threshold.
2. **The `prefix` matcher failed a plant it could not possibly pass.** I planted `"the verdict is B
   because…"` for all three matchers, where `B` never sits at the start — so `prefix` scored 0.0000
   and was condemned by a malformed control. §4's *control that cannot PASS*, built by me. **Plants
   are now per matcher**, in the shape each exists to recognise, and `prefix` came back **1.0000 and
   live**.
3. **My verdict averaged the three matchers** — `(0.1806 + 0.2222 + 0.6528)/3 = 0.352` — across
   designs whose false-positive rates differ by **16×**. §2.5 forbids that explicitly. The curve is
   now read **per cell, on each matcher's excess over its own control.**

## Controls
- **plant, per matcher** — 1.0000 / 1.0000 / 1.0000
- **negative** — control text with no verdict role: 180 `why` values + 4,476 README sentences
- **placebo** — a token in no vocabulary (`ZZQ`): **exactly 0.0000** on every corpus
- **blindness gate** — pre-registered `t − f ≤ 0.10 ⇒ the matcher reports nothing`; all three cleared

**IMPOSSIBLE, named:** whether a round *intended* the verdict a matcher recovers is not decidable from
the string — it needs the round's author or an external reader. **Every `t` is an upper bound on
translatability.**

## The sentence I can no longer write
> *"the `world` tail is a formatting failure with a mechanical repair."*

**It is not a formatting failure.** The field has been used as prose for 216 distinct values, and the
`B`/`A`/`UNVERIFIED` core is a genuine but minority convention covering **a quarter** of occurrences.

## NEXT
The core covers 25.2% of `world` occurrences and the corpus has **no** enforced verdict type — yet
`assurance/statement_provenance.py` gates the deliverable on `world != "UNVERIFIED"`, a **string
comparison against a field with 220 distinct values.** Check what that gate actually accepts: run it
against a synthetic artifact whose `world` is a sentence containing the word *unverified*, and one
whose `world` is absent, and see whether the two are distinguishable to it — **a gate reading an
unenforced field may already be passing rounds it was built to stop.**
