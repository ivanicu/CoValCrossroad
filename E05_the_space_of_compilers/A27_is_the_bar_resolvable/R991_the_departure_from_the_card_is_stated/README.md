# R991 · the departure from the release's own card is now stated

**THE DECISION THIS MAKES SAFE.** Whether this definition's disagreements with the card that defines
its object are deliberate. **They are now** — three departures, written down, each with the
measurement behind it.

---

## Why this and not R990's NEXT

R990 asked for a semantic instrument. Real work, and not the highest-leverage act available:
**R988, R989 and R990 all produced findings and none was in `DEFINITION.md`.** R988's own words were
that the departure *"is currently stated nowhere"* — so a round that leaves it unstated repeats the
defect it found. A semantic instrument refines a measurement; **writing the departure down changes
what the deliverable says.**

## What was written in

| the card | this definition |
|---|---|
| size: **up to four** — an **upper** bound | clause ①: **greater than one** — a **lower** bound |
| **non-redundant** | *no clause* |
| **non-conflicting** | *no clause* |

- **The missing upper bound admits 4 objects the release could not produce** (R988) — `greedy_k8_fit1`,
  `indep_k8_fit1`, `topw_k6`, `topw_k8`, sizes 6–8.
- **Non-redundancy is real, so the missing clause is a real gap** (R990) — DiD **−0.0084**, 3 of 3
  seeds, with the lexical one-directionality carried into the statement rather than dropped.
- **Non-conflict is unreachable here** (R989) — no core weights, 7.8% verbatim match. And the 80%
  sign-disagreement figure is carried **with its null**, 93.3%, so a later reader cannot quote it in
  the direction it superficially reads.

## The before/after

| fact | parent `HEAD` | working tree | verdict |
|---|---|---|---|
| R988 cap + missing clauses | absent | present | **REAL** |
| R989 sign-coherence vs null | absent | present | **REAL** |
| R990 redundancy DiD | absent | present | **REAL** |

**Controls.** POSITIVE — R921's fact present in **both** revisions, so "absent everywhere" cannot be
a load failure · NEGATIVE — runtime-assembled sentinel absent from both · the "before" is read with
`git show`, not recalled. Gate transition **1 → 0** (17 facts); anchoring gate **0 → 0**, so this was
**annotated, not edited** (L81).

## ⚠ What this does not show

**That the departure is right.** The card calls core *"a proof of concept … an invitation for others
to develop and validate better synthesis and aggregation methods."* Departing may be correct. What
changed is that it is **deliberate rather than silent** — and the statement now carries the
measurement a reader would need to disagree with it.

## Alternatives considered

**Build the semantic instrument first.** Deferred, not abandoned: R990's proxy ledger is carried into
the statement verbatim, so the lexical bound travels with the claim instead of being lost between
rounds.

**Also add an upper bound to clause ①.** Refused, twice now: R988 refused it as changing the
extension by fiat in the same breath as discovering the gap, and that reasoning has not changed. The
gap is stated; closing it is an authorial decision with its own round.
