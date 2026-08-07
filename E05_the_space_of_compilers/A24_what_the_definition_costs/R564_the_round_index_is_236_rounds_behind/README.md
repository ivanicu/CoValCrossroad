# R564 · The round index was 237 rounds behind, and I read the tail of the output a third time

**Decision this makes safe:** the campaign's navigation. **265 rows written; the gate now clears.**

**WORLD B.** My NEXT line said the README was un-updated *"since R555"* and that the work was
*"those seven rows."* **Both false.** The index's high-water mark was **`R327`**; the gate flagged
**127** rounds, not 7.

⭐⭐⭐ **I read the tail of the gate's output — the same error R561 logged two rounds earlier.** And
then did it **again** inside this round: after the rebuild I ran `tail -5`, saw two lines, and
reported "127 → 2". The true count was **1**. **Three times in one round, on the same instrument.**

| | |
|---|---|
| rounds with results | **263** |
| index high-water mark | **R327** |
| rounds behind | **237** |
| rows written | **265** |
| rounds with **no README**, so carrying **no invented description** | **6** |

## L80 honoured
Every description is taken **verbatim** from that round's own README first heading. **6 rounds have
no README and got no description** — `*(no README — description not invented)*` — because a machine
may not invent a WHY.

## ⚠ Two structural findings I recorded rather than fixed
- **There are TEN arcs (A16–A25) and I had been treating A24 as the epoch.** `R428` lives in `A25`.
- **`A25` holds exactly one round.** **P16: an arc containing a single `R` is a mis-cut arc**, since
  an arc is a decision made safe and one belief update rarely does that. **Recorded, not
  restructured** — re-cutting an arc is a decision, not a repair.

## Controls
- **Positive** — `R327`, the index's last existing row, reads as present, so "missing" is a
  measurement rather than a blind parse. **PASS.**
- **Negative** — an invented round id reads as absent. **PASS.**
