# R749 · three of the five object counts on the deliverable cannot be traced to a computing round

**The page states 5 object counts. Only 2 resolve to a cell of R748's grid, and they resolve to
**different** cells — `46` to `[raw cells × full overlap]` via R524, `81` to `[agg vectors × subset]`
via R730. The other 3 — `2`, `4`, `10` — are **untraceable**: two sit in sentences carrying **no
citation at all**, and one cites a round whose source holds no identity relation. ⛔ And my registered
mechanism was wrong: I predicted the failures would be rounds that *import* their relation. **Zero of
them are.**

## check #351 — and the first thing it checks is a defect in my own last round

⛔ **R748's E2 used one pattern**, `(\d+) tags? are (\d+) objects?`, which matches **3** sentences. A
medium pattern over the same page matches **5**. So R748's `P5 = 2` was a share of a population its
own instrument under-counted — **§4's *a search is an instrument*, committed by me one round after
quoting it** *(ledger 1015)*.

| pattern | sentences | live | in a retracted block |
|---|---|---|---|
| tight *(R748's)* | **3** | 3 | 0 |
| **medium** | **5** | 5 | 0 |
| loose | 50 | 50 | 0 |

⛔ `loose ≥ medium ≥ tight` is **FORCED** by construction. The **order** is algebra; only the **gaps**
are measurements.

## the five, resolved

| count | cites | cell | how |
|---|---|---|---|
| **46** | R524 | `raw cells × full overlap` | relation **defined in its own source** |
| **81** | R730 | `agg vectors × subset` | relation **defined in its own source** |
| **2** *(claim row 8: ③ misses 2 distinct objects)* | R520 | **UNRESOLVED** | the cited round's source holds no identity relation |
| **4** *(the 7 target-reading tags are 4 objects)* | — | **UNRESOLVED** | **the sentence cites nothing** |
| **10** *(13 tags are 10 objects)* | — | **UNRESOLVED** | **the sentence cites nothing** |

⇒ **E3 = 2 distinct cells among the resolved.** **WORLD B**: the rows are not comparable and each
must carry its cell.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 assertions per pattern | ⚠ **SIGHTED**, declared in the preregistration | 3 / 5 / 50 | — |
| P2/E3 distinct cells among resolved | 2, band [1, 4] | **2** | ✓ exact |
| P3 assertions resolving at all | 3, band [0, 5] | **2** | in band, point wrong |
| **P4** resolved rounds that IMPORT their relation | 2, band [0, 10] | **0** | in band, point wrong |
| P5 assertions citing a round with no `run.py` | 0, band [0, 5] | **0** | ✓ |
| **D** the unresolved are the importers | true | **false** | ⛔ **wrong mechanism** |

⭐ **D failing is the finding.** I built the resolver to follow imports because R747 and R748 both
import `same()` and a naive source scan would go blind on them — a real limitation, correctly
anticipated. **It never bit.** The three failures are a different thing entirely: **the page states
object counts in sentences that carry no citation**, which no amount of import-following can fix
*(ledger 1017)*.

⚠ **The resolver takes the FIRST citation, and that is a choice with a measured cost.** Claim row 8
cites `R520, R523, R525`; R520 has no relation, and **R525 is the round that built the partition**.
The NEGATIVE control rotates the citation choice and **2 of 5 cells change** — so *"row 8 is
untraceable"* is a statement about a first-citation resolver, not about row 8. Reported as such.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `R524 → raw cells × full overlap` and `R730 → agg vectors × subset`, both correct **and distinct**. Band computed: a constant-cell resolver separates them **False** (floor), this one **True** |
| **g=0** | an assertion citing nothing → `UNRESOLVED`. **A default cell would have manufactured World A by making everything agree** |
| **NEGATIVE** | rotating the citation choice changes **2/5** cells — the resolver reads the **round**, not the number |
| **SHAM** | ingredient **absent**: of the first 40 rounds, **36** hold no locatable identity relation and every one returns `UNRESOLVED` rather than a cell |
| **PLACEBO** | the same page resolved twice → **0** differing, stated as 0 of 5 |

## ⛔ two derivations, labelled and excluded from the findings

`loose ≥ medium ≥ tight` is construction, not measurement. And **a census has no confidence
interval** — this is every object count on the page, n = 5, so there is no sampling uncertainty and
**no power to generalise**. No interval is reported; one would be manufactured.

## the sentence I can no longer write

*"the page's object counts are traceable."* Three of five are not, and the two that are come from
different cells.

## NEXT

The three untraceable counts have two different causes and only one is a documentation fix. `4` and
`10` need a citation added to their sentences — mechanical, and `assurance/statement_provenance.py`
already resolves citations so a gate could require one on any sentence matching the object-count
pattern. `2` is different: its row cites three rounds and the resolver reads whichever appears earliest, so
the row's cell depends on which citation a reader follows — rotating that choice moved 2 of 5
assignments in this round's NEGATIVE control. The registered quantity is how many object-count
sentences on the page cite **more than one** round, and for those, whether the cited rounds agree on
a cell — because a row citing two rounds from two cells is not under-documented, it is **internally
inconsistent**, and that is a different defect needing a different repair.
