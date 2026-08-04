# R462 · "oldest first" was an untested claim — and doing the work *was* the test

**The decision this round makes safe:** the ordering for the remaining declaration work.
**Not by age.** `W-EQUAL`.

## ⛔ The announced ordering was an assertion about where defects live

R461 closed: *"work it in blocks by round, **oldest first** — the oldest numbers have survived the
most rewrites of the sentences around them and are therefore where a comparator is most likely to
have gone missing."* **Nothing measured that.** §4's *closing sentence* row exactly: the last sentence
written, the one the next round acts on, and the only one with no control attached.

**And the ledger already pointed the other way.** Every anchor defect the value-gate has caught —
R450 (named for r=3, pointed at r=0), R454 (matched R450's ladder), R455 (sign outside the capture
group), R461 (self-referential count stale on commit) — was in a **newly written** anchor. There is a
mechanism: **every anchor is re-checked on every gate run, so an old anchor has passed hundreds of
checks and a new one has passed one.**

⚠ **But that argument does not transfer.** The comparator gate is *new*, so **no anchor has ever been
protected on that axis** — age predicts nothing about comparator presence, in either direction. **The
announced ordering had no basis, and neither did its opposite.** Which is why it had to be measured.

## ⭐ Doing the work was the test

Declaring the whole **R442–R454** block — the anchors the announced step called riskiest — costs
exactly what the announced step asked for, and settles its premise as a side effect.

| window | OLD flagged (R442–R454, n=32) | NEW flagged (R455–R461, n=18) | undeclared |
|---|---|---|---|
| 200 | **0** | **3** | 181 |
| 400 | 0 | 0 | 181 |
| 800 | 0 | 0 | 181 |
| 1600 | **0** | **0** | 181 |

**Flag rate at w=1600: OLD 0/32 = 0.000, NEW 0/18 = 0.000.**

> ⛔ **The announced ordering is refuted.** The block called riskiest flags at exactly the rate of the
> newest one — **both zero**. And at the tight window the flags are **all** from the new block
> (`r456_gap16`, `r456_ratio16`, `r460_iqr`) and **none** from the old: the direction the ledger's
> catch history predicted, opposite to the one announced.

## Controls

| control | returned |
|---|---|
| POSITIVE — comparator planted at 300 / 1200 chars | FLAGGED below the plant, PASSING above, all four cells ✅ |
| g=0 — a declared-**absolute** claim | never flagged at any window ✅ |
| WINDOW sweep | retained, because a flag appearing only at w=200 is a **window artifact** and would otherwise read as a block difference |
| **PROVENANCE** | the w=200 flags are printed **with their block**, so "3 flags" cannot be attributed to the newly declared block without checking |

**The provenance control is what makes this round readable.** Without it, "3 flagged at w=200" beside
"53 anchors newly declared" invites exactly the wrong inference.

## ⚠ What this does not establish

- **That the remaining 181 undeclared anchors are clean.** They are **undeclared**, which is not a
  pass — the gate reports a count instead of a clean bill precisely so this cannot be misread.
- **A correct ordering.** The only proposed basis has been refuted, and nothing here supplies a
  replacement. **The ordering is now an open question**, and the honest next move is to order by
  something measurable — load-bearingness for the definition's clauses — rather than by another
  untested story about where defects live.

**Coverage 80 of 261 (30.7%), up from 27 (10.3%).**

## Impossible here, named

- **a randomised comparison of blocks** — blocks are defined by when they were written; that cannot
  be assigned.
- **declaring the remaining 181 in this round** — each needs the round that produced it read.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
