# R981 · 340 of the 343 anchoring assertions guard the evidence record; 3 reach the definition

**THE DECISION THIS MAKES SAFE.** How much of `DEFINITION.md` a green `definition_matches_the_record`
actually certifies. **The 9,128-line evidence record.** The 693-line statement a reader reads as the
definition is reached by **3** assertions.

---

## Production first — three rounds reached the statement

R978, R979 and R980 were all absent from the statement. Registered in the currency gate, checked
**red first** (all three genuinely unmatched at `HEAD`), then written into the scopes section:

| | |
|---|---|
| currency gate | **1 → 0**, now 12 facts, all present |
| anchoring gate | **0 → 0**, 343 of 343, unchanged |

⭐ **That unchanged 0 is the round.** I added 23 numerals and the 343-assertion gate's verdict did
not move — because none of them is in its table. Currency without consistency, the exact mirror of
what R977 found.

## The census

| | whole | statement | record |
|---|---|---|---|
| lines | 9,821 | 693 | 9,128 |
| assertions matching | **343/343** | **3** | **340** |

The three that reach the statement are `r441_withk`, `r441_k1`, `r441_redundant`.

⚠ **This is a DERIVATION, and labelled as one.** The coverage of a fixed regex set over a fixed
document could not have come out otherwise once both are fixed. Its value is that nobody had run it —
the gate names its unchecked remainder in its own proxy ledger every run and has never counted it.

## ⛔ Two controls failed before one passed, and both failures were MINE

**① Wrong population.** v1 ran the census over the statement region alone: 1 numeral covered of 459.
That is not a coverage finding, it is a population error — `0.009103` *is* in the statement, but the
assertion anchoring it matches its occurrence in the **record**. The round printed **UNVERIFIED**.

**② The control was validated on an imagined case** — §4's own row. I then asserted `0.009103` was
"in the table by construction." **It is not**: 0 of 343 spans contain it, 0 captures equal it. The
control failed because *the control was wrong*, not the instrument, and the round printed
**UNVERIFIED** a second time.

⭐ **The repair: derive the control's target from the instrument.** Take the first numeral an
assertion actually captures — `45`, from `r838_npairs` — and require it to read covered. **A control
whose target comes from my memory tests my memory.**

| control | result |
|---|---|
| **POSITIVE** (derived) | `45` from `r838_npairs` reads covered — **True** |
| **NEGATIVE** | a runtime-assembled numeral reads uncovered — **True** |
| **PLACEBO** | 348 matched spans ≥ 1 covered numeral; no numeral counted by zero spans |

**This is the third time this session an object-level check caught a population I had assumed** —
R975's floor (1,078 prompts vs 968), R978's operator (mean threshold vs resolvable beat), and this.
In all three the round refused to publish rather than reporting the wrong-population number.

## What this does and does not say

- **It does not say the statement is wrong.** Coverage means an assertion *locates* the numeral,
  which implies it is re-derived from an artifact. The reverse is not implied: an uncovered numeral
  is **unchecked, not incorrect**.
- **It does say what `343 of 343` means.** It is a statement about the evidence record. A reader who
  takes it as certifying the definition is reading the pass in a direction the gate never supported —
  and the gate's own ledger says so, without the number that makes it concrete.
- **One document, one release.** Nothing here generalises to another project's anchoring ratio.

## Alternatives considered

**Write 340 new assertions for the statement region.** Not attempted here: the statement's numerals
are mostly *reported* values whose artifacts this arc produced in the last week, and bulk-adding
assertions inside a production round is how an unvalidated instrument enters a gate — the same
objection R977 raised against automatic fact discovery.

**Report the 99.8% uncovered figure from v1.** Refused: it is the wrong-population number, and its
only correct use is as the record of a control that fired.
