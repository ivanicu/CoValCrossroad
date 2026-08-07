# R596 · The gate meant to keep UNVERIFIED rounds out was letting one through — and its rule was wrong too

**Decision this makes safe:** the provenance gate now actually gates. **7 of 8 spellings stopped, up
from 1 of 8**, verified by exit code on sandbox trees, not by reading the source.

| spelling | before | after |
|---|---|---|
| `UNVERIFIED` | **STOPPED** | STOPPED |
| `unverified` | ⛔ accepted | **STOPPED** |
| `UNVERIFIED ` / ` UNVERIFIED` / `UNVERIFIED\n` | ⛔ accepted | **STOPPED** |
| `UNVERIFIED -- a control did not fire` | ⛔ accepted | **STOPPED** |
| `UNVERIFIED — the instrument was unfit` | ⛔ accepted | **STOPPED** |
| `world: UNVERIFIED` | ⛔ accepted | ⛔ **still accepted** |

**19 gate invocations** — 8 spellings × 2 runs (both agreed every time) + 3 controls.

## ⛔ It was LIVE, not hypothetical
**Cited round R501 carries `world = "UNVERIFIED — the instrument cannot localise oracle_k4 (rank 11
of 23), so the null is silence, not an acquittal"`.** Its own **first word** is `UNVERIFIED`, and the
gate built to exclude exactly that had been passing it — because an em-dash made the string unequal.

## ⭐⭐⭐ And the rule itself was wrong, which tightening the comparison alone would have made worse
`STATEMENT.md` line 197 reads *"That question is `UNVERIFIED`, not closed"* and cites R501 **as
evidence that the question is open.** The document was right all along.

⛔ **So a gate that forbids every citation of an UNVERIFIED round forbids citing a failure as a
failure.** The repaired string match, alone, would have rejected the one sentence in the document
that does this correctly — and pushed the author toward **deleting the caveat to make the gate
green.** *A gate manufacturing the error it exists to prevent.*

**Repair, two parts:** match the **first token**, case-folded and punctuation-stripped · and allow an
UNVERIFIED citation **iff the citing paragraph says so**. No new marker was introduced — the document
already writes the word, and requiring it makes the scope **machine-visible instead of a matter of the
reader's attention**.

## ⛔ The declaration rule was line-scoped first, and that was caught before it ran
R501's citation is on **line 197**; its `UNVERIFIED` marker is on **line 194** of the same wrapped
paragraph. **Line scope would have flagged the one sentence doing this correctly.** Seventeenth
instrument-unit mismatch of the session — **and the first caught before execution rather than after.**

**PROXY LEDGER, stated not hidden:** paragraph scope cannot bind a marker to a *specific* round.
**SOUND:** a flagged citation is genuinely undeclared. **UNSOUND:** an allowed citation may be riding
another round's marker. Tightening needs per-citation syntax the document does not carry.

## ⛔ And P7 is right that the fix is where the new hole is
`"world: UNVERIFIED"` still passes — its first token is `world:`. ⭐ **The obvious patch (match
"UNVERIFIED" anywhere) over-rejects**: a value like `"B — not UNVERIFIED, the control fired"` would be
wrongly flagged, which is the same over-strictness trap in mirror image.

⭐⭐⭐ **This closes the R594→R595→R596 arc: you cannot make a string rule sound over an untyped
field.** R594 measured `world` at 220 distinct values, R595 showed the vocabulary is genuinely open,
and R596 is what that costs — a gate reading it can be made *better* and cannot be made *sound*.
**That is HB8's claim, arrived at from the failure rather than from the doctrine.**

## Controls
| control | returned |
|---|---|
| **g=0** — unplanted sandbox | exit **0** — PASS |
| **positive** — planted exact `UNVERIFIED` | exit **1** — PASS, the harness can produce a rejection |
| **negative** — planted a normal verdict `B` | exit **0** — PASS, the rejection came from the **spelling**, not from planting |
| **placebo** — planted under key `wrld` | exit 1 — expected; no `world` key is also a rejection path |
| **reproducibility** | every cell run **twice**; all 8 pairs agreed |

**DERIVATION, labelled:** that variant spellings pass was **forced by `!=`**, read from source. Only
the exploitation count and the exit codes could have come out otherwise.

**Two populations, named:** the gate's own citation regex `R(\d{3})[,)]` finds **83** rounds; the
looser `R(\d{3})` that R592 used finds **91**. Two instruments, two populations — **the gate is
governed by its own.**

**IMPOSSIBLE, named:** "means unverified" is not decidable from a string without the round's author.
The exploitation count is an **upper bound** via case-insensitive substring.

## The sentence I can no longer write
> *"the deliverable's citations have all been checked against an UNVERIFIED verdict."*

They had been checked against **an exact string**, over a field with 220 distinct values — and one
cited round walked through on an em-dash.

## NEXT
The repaired gate's allowance depends on the citing **paragraph**, which cannot bind a marker to a
specific round — so a paragraph citing several rounds allows all of them. **Count how many paragraphs
in `STATEMENT.md` cite more than one round AND contain the word `UNVERIFIED`**: that is the exact size
of the population where the new rule is unsound, and it is a count rather than a judgement.
