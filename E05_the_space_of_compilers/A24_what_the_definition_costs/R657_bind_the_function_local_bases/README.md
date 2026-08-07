# R657 · The estimate was written before the code, in an interval, and still missed low — for the third time

**Decision this makes safe:** whether function-scope binding closes the residual. **No — 6 of 14.
And the interval I widened *because* the last two forecasts missed, missed too.**

## The pre-registration, verbatim, written before any code existed

> **point 11 · interval [8, 14]** · *reasoning:* 13 of 14 bind exactly one local name; 7 bind
> `root`, usually `Path(__file__).resolve().parents[N]`; 3 bind `d`, usually a for-loop variable,
> and those are the doubtful ones. · **kill:** a measurement outside [8, 14] means the
> **forecasting procedure** failed, not merely the number.

| | |
|---|---|
| **measured** | **6** |
| verdict | **OUTSIDE the interval — world B *and* world C** |

## The 14, with scope binding

| | n |
|---|---:|
| CORPUS-DEPENDENT · OUTSIDE-BOTH | **5 · 1** |
| OWN-SCOPE · MIXED · PARTIAL-UNDECIDED · AMBIGUOUS | 0 · 0 · 0 · 0 |
| **STILL-LOCAL** (traces to a parameter — a *named* residual) | see grid |
| STILL-UNRESOLVED | remainder |

Population: R656's 14 FUNCTION-LOCAL rounds · instrument: `ast` + symbolic `pathlib` + function-scope
binding · baseline: R656's decided rounds · regime: tree `71a11b71`.

## ⭐⭐⭐ A control that demanded reproduction was demanding I reproduce a defect

`POSITIVE-1` v1 said *"every round R656 decided must stay decided"* and failed 3/4. The cause is not
a regression here: **R656 repaired its residual-folding for `OWN-SCOPE` and left it in place for
`CORPUS-DEPENDENT`.** Its order tests `if "CORPUS" in seen` *before* the residual check, so
`R319_six_rounds_read_the_typo` — **one CORPUS site and three unresolved** — was called decided.

> **A reproduction control makes the baseline's defects mandatory.** Repaired: a disagreement is
> admissible **iff** it is a fold the baseline committed, and each one is **named** — 1 found,
> 0 unexplained.

## ⛔ And the negative control caught a real conflation

`r = base` with `base` a parameter left `r` absent from the binding table, so it read as
**"unresolved"** — collapsing a *named* residual (traces to a caller) into an anonymous one.
**The entire point of `STILL-LOCAL` is that it says why.** Fixed by propagating `PARAM` through
assignment.

## My own forecast record, priced against its null

| forecast | predicted | measured | error |
|---|---:|---:|---:|
| R654 NEXT → R655 | 25 | 0 | **−25** |
| R655 NEXT → R656 | 11 | 4 | **−7** |
| R657 prereg → here | 11 | 6 | **−5** |

**All three over-estimates.** Under a symmetric null, 3/3 same-signed errors has **p = 0.125**.
⭐ **That is a DIRECTION, not an established bias** — n=3 clears no correction. The honest statement:
**the magnitude is shrinking (−25, −7, −5) while the sign has not flipped.**

## ⛔ Check #258 — three claims in R656's NEXT, two wrong

| claim | truth |
|---|---|
| *"14 of the 21 remaining are FUNCTION-LOCAL"* | ✓ |
| *"**12** of those bind a single name"* | **13** — and **I read it off my own grid printing `notes[:1]`**. `R554` looked like `RECV unresolved` but names `d`; `R337` names two. **The arc's fourth truncation** (`[:12]`, `head -3`, `tail -25`, `notes[:1]`) — this one printed three lines above the sentence that misread it. |
| *"…wrong by 7 and the previous one by **11**"* | **No forecast here was off by 11.** Eleven was the forecast's *value*. **I named an error magnitude by reusing the number that had just been refuted.** |

Name list also wrong: `s`/`st` came from R655's **shape** table (different population); `sub` was omitted.

## Controls

| control | returned |
|---|---|
| **positive-1** — R656's decided rounds | **3 reproduced, 1 named as an R656 fold, 0 unexplained** — PASS |
| **positive-2** — a local assigned a module-derived path | **CORPUS** — PASS |
| **negative** — a local assigned from a **parameter** | **STILL-LOCAL** — PASS, *not everything with an assignment binds* |
| **placebo** — a local assigned two different paths on two branches | **AMBIGUOUS** — PASS, ⭐ *it refuses rather than taking the first* |
| **g=0** — no local assignment at all | **CORPUS** — PASS, *the binder adds nothing* |

**MULTIPLICITY:** 1 binder × 14 rounds × every glob site + 4 reproduction checks + 4 controls; all
eight outcomes printed, and **every note per round, not `notes[:1]`.**

**IMPOSSIBLE, named:** a local assigned from a parameter needs the call graph, absent across
standalone scripts; a local rebound from runtime data is not static at all.

## The sentence I can no longer write

> *"widening a point forecast to an interval makes it honest."*

**It missed anyway.** An interval drawn by the same procedure inherits the same optimism — the
widening addressed the *precision* of the forecast and not its *direction*.

## NEXT

**Every remaining undecided round is now labelled by mechanism** — `STILL-LOCAL` (traces to a
parameter) versus `STILL-UNRESOLVED` (no binding found at all) — and those are the two ends of the
impossibility register. **Count how many of the STILL-UNRESOLVED bind a name that is assigned inside
a `with` block, a comprehension, or a tuple-unpack**, because `local_bindings` handles only `Assign`
and `For` targets, and if the missing forms account for most of them the residual is *still* an
evaluator gap rather than the structural limit I am about to declare it. **Declaring a structural
limit is the flattering direction and this arc has already retracted one.**
