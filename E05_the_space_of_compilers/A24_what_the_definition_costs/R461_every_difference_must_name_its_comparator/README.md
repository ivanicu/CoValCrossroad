# R461 · the announced audit was a grep — rebuilt as an enforced declaration, and its suspicion was false

**The decision this round makes safe:** whether R460's class defect — *a difference is a joint
statement about the arm and its comparator* — reached the deliverable. **It did not.** `W-WINDOW`.

## ⛔ Two ways to run this were rejected before it ran

**① The announced form is an uncontrolled search.** R460 closed proposing to *"walk `DEFINITION.md`
for every ρ, gap or share defined as a difference."* §4: **a grep is a measuring instrument.** This
one has no positive control and no unit equality — its unit is *regex hits in prose*, the claim's unit
is *numbers that ARE differences*, and those are different sets.

**② The obvious alternative is forced.** Re-measuring each difference across R460's comparator census
would be arithmetic: **R455's comparator is *the best* one by construction**, so every weaker
comparator necessarily yields a larger gap. Rung 2.

*Twenty-ninth announced step checked; its instrument replaced before running.*

## ⭐ The enforceable form: declare, then check

`assurance/comparator_scope.py` maps each anchor to **the names of what its number was differenced
against**, or marks it absolute. **An anchor with no declaration is reported UNDECLARED and can never
pass silently.** Prose is not enforcement; a declaration is.

## Result — the window swept, not chosen

| window | declared diff | absolute | **FLAGGED** | undeclared |
|---|---|---|---|---|
| 200 | 18 | 9 | **3** | 230 |
| 400 | 18 | 9 | **0** | 230 |
| 800 | 18 | 9 | **0** | 230 |
| 1600 | 18 | 9 | **0** | 230 |

Flagged at w=200 only: `r456_gap16`, `r456_ratio16`, `r460_iqr`. **Zero at every defensible window.**

> **The suspicion is false: every declared difference-based claim names its comparator.** The three
> tight-window flags are a **window artifact**, and *the sweep is the only thing that distinguishes
> that from a real defect* — a single chosen window would have reported either "3 defects" or "all
> clean" with equal confidence.

## Controls

| control | returned |
|---|---|
| **POSITIVE** — comparator planted at 300 chars | FLAGGED at w=200, PASS at w=1600 ✅ |
| **POSITIVE** — planted at 1200 chars | FLAGGED at w=200, PASS at w=1600 ✅ |
| g=0 — a declared-**absolute** claim | never flagged at any window ✅ |
| NEGATIVE — the sweep itself | a window that passes everything is blind; w=200 *does* flag, so it is not |

**Four positive-control cells, both plant distances × both extreme windows.** Without them, "0
flagged" would be indistinguishable from an instrument that cannot flag anything.

## ⚠ The number this round must NOT report as a finding

**Declaration coverage is 27 of 257 anchors (10.5%).** The 230 undeclared are **not passes** — but
that count measures **my declaration coverage**, not a property of the document. **Reporting 230 as a
document defect would be exactly the error this round exists to avoid**, and it is the kind of number
that reads as a finding because it is large.

## What this round produces

- **An instrument that outlives it:** a future difference-based anchor **cannot be added without
  declaring what it was measured against**, and an undeclared one is visible in the count.
- **A clean result on a real suspicion**, which is worth reporting precisely because the previous two
  rounds both found defects and the prior was that this one would too.

## Impossible here, named

- **declaring all 257 anchors in one round** — each declaration requires reading the round that
  produced the number. 27 are declared; the rest are coverage, not passes.
- **checking claims that are not anchored** — the gate's unit is an **anchor**; unanchored prose is
  outside it. That is §4's unit-equality point applied to this gate.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
