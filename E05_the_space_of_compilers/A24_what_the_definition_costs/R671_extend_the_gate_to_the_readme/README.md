# R671 · The gate now reads the 80 README `## NEXT` sections it never looked at — and that surface is worse

**Decision this makes safe:** whether the gate's "structural" unit gap was really structural.
**Half of it was not. The README half is a file, and it is now read.**

## The population the gate had never opened

| | |
|---|---|
| README `## NEXT` sections | **80** |
| flagged (unsourced quantifier over our own work) | **34 — 42.5%** |
| commit-body rate (R670) | **37.2%** |
| ⭐ **difference** | **+5.3 pts** |

> **The surface where the failures actually land was the unpoliced one.** Ledger **715** (R665's
> README) and **720** (R666's README) both live in a README `## NEXT` — **and the gate had never
> read a single one of the 80.**

## Pre-registration, written before any code

> **point 40% · interval [20%, 60%]** · **directional:** *the README rate is HIGHER than 37.2%* ·
> **kill:** > 60% blocks the extension.

**Measured 42.5% — INSIDE, error +2.5 pts** (the closest magnitude of the nine). **Directional
HOLDS.** Under the 60% line, so the extension is applied.

## Controls

| control | returned |
|---|---|
| **positive** — ledger 715 & 720, known-false, living in README NEXT sections | **both FLAG** — PASS |
| **negative** — a NEXT citing its instrument (`run assurance/residue_debt.py`) | **clean** — PASS, *the provenance escape transfers to the new population* |
| **placebo** — a quantifier with no artifact noun | **clean** — PASS |

## What is now live

`assurance/next_line_quantifiers_are_computed.py` reads **both** populations and prints both:

```
quantified NEXT lines: 100   frozen: 167
README `## NEXT` sections: 80   quantified: 34   frozen: 34
PASS -- no new quantified NEXT line, in commit bodies or READMEs.
```

The 34 are frozen as a baseline in `KNOWN_QUANTIFIED_README_NEXT.json`, **exactly as the commit-body
half works** — known, not hidden, and **any NEW one fails.**

## ⛔ Check #272 — the retracted number reappeared in the round that retracted it

| claim | truth |
|---|---|
| *"three of this arc's **four** quantifier failures"* | **R670 itself established there are THREE in scope** (725 is a different class) — **and I wrote "four" one paragraph later.** |
| *"three of them reached a README `## NEXT`"* | **Two.** 715 and 720 did; **723 did not.** |
| *"the README half is a file, and a file can be read"* | ✓ — 80 of 340 READMEs carry the section. |

**MULTIPLICITY:** 1 rule × 80 README sections + 3 controls; **both base rates reported side by side.**

**IMPOSSIBLE, named:** the **terminal** report is never written to disk and stays unreadable. This
extension **narrows** the unit gap from *"reports"* to *"reports minus the terminal half"* — **it does
not close it**, and the residue is named rather than quietly dropped.

⚠ **And the gate polices unsourced quantification, not truth.** A flag is not a false claim; that has
always been its scope and this extension does not widen it.

## The sentence I can no longer write

> *"reports go to the terminal, not to disk, so no gate can read them."*

**Half of every report is a README section, and 42.5% of them carry the failure.**

## NEXT

⭐⭐⭐ **This section is the gate's first live catch, and it caught this round — twice.**

**First catch.** The sentence that stood here asserted that the freeze baseline had not been paid
down and that no entry had been removed — an unsourced quantifier over our own work, **which I had
not measured.** The gate flagged it, and the correct response was to **fix the line, not freeze it**.
That is the whole point of the extension, demonstrated on its author within a minute of going live.

**Second catch, and it is a real limit.** The replacement paragraph *quoted* the offending words to
explain them — and **the gate flagged it again. It cannot distinguish use from mention.** No pattern
can; a round that discusses a flagged quantifier trips on the discussion. **Named here rather than
worked around**, because the escape hatch a future round will reach for is the citation, not silence.

**The freeze baselines hold 167 commit shas and 34 README rounds** (both printed by the gate).
**Measure the freeze's own history — whether entries are ever retired, and how many of the 34 README
sections could be repaired by adding a source citation instead of dropping the quantifier** (the
gate's own `PROVENANCE` escape, `run assurance/next_line_quantifiers_are_computed.py`). A baseline
that only accumulates would be hard to tell from suppression, and **which of those this one is has
not been checked.**
