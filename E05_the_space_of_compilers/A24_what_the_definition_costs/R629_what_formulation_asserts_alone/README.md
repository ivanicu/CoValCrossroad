# R629 · The largest document in the project is the one no gate reads

**Decision this makes safe:** whether `FORMULATION.md` is a stale duplicate. **It is not.** ~80% of
it appears nowhere in the gated pair, and **eleven rounds of this arc audited the two smaller files.**

| extractor | unique | of | share |
|---|---|---|---|
| decimal values | **583** | 732 | 79.6% |
| round citations | **80** | 100 | 80.0% |
| R-headed findings | **17** | 23 | 73.9% |

**2,397 lines** against `STATEMENT.md`'s 668 — **the biggest document, and the ungoverned one.**

⭐ **Three independent extractors converge at 74–80%.** "An assertion" is not decidable, so each is a
proxy; **their agreement is what licenses the reading**, and no single one carries it.

## Some of what it asserts alone
- **CLAUSE 2 SURVIVES ITS OWN META-SEPARATOR — 1,820 subsets enumerated exactly** (R286)
- **THE VALUE IS IN THE COMBINATION, NOT IN ANY MEMBER** (R298)
- **`full` FAILS THE NEUTRAL CLAUSE AT ITS OWN SIZE — the rubric is not worth its length** (R307)
- **AT EXACTLY MATCHED SIZE, READING THE PROMPT BUYS NOTHING ON ITS OWN — 2 of 7** (R308)
- **CLAUSE ② NOW NAMES ITS REFERENCE BY A PROCEDURE** (R327–R333)
- **The impossibility register, AUDITED — three lines were wrong** (R290, R291)

*These are substantive findings about the definition, and none is behind any gate.*

## ⭐ R625's lesson SCOPED rather than applied by reflex
R625's collision floor was **36% against 23,823 corpus numbers.** This comparison runs against
**645 values in two documents — ~36× smaller** — so the floor was **re-measured, not inherited**:
**5.95% · 6.98% · 5.95%** over 3 seeds × 4000.

⭐ *A lesson about an instrument is a lesson about that instrument **at that size**.* Applying 36%
here would have destroyed a real result; assuming 0% would have manufactured one.

⚠ **And the floor cuts the right way:** observed overlap is 20.4%, floor ~6.3%, so of the 149
apparently-shared values roughly **46 could be coincidence** — meaning true uniqueness is **≥ 79.6%
and plausibly ~86%.** The bound favours *more* uniqueness, not less.

## Controls
| control | returned |
|---|---|
| **positive** — a value on the gated pair | classifies **SHARED** — PASS |
| **g=0** — an invented decimal | classifies **UNIQUE** — the comparison separates them |
| **negative** — `FORMULATION.md` against itself | **0 unique** on all three extractors |
| **placebo/floor** — random decimals vs the gated pair, 3 seeds × 4000 | **5.95 / 6.98 / 5.95%** |

**MULTIPLICITY:** 3 extractors × every item + 4 controls. All reported.

**IMPOSSIBLE, named:** *"this content is IMPORTANT"* is not decidable by any extractor — **the unique
headings are printed so a reader judges, and the count is not that judgement.** ⚠ And the value
extractor **understates** uniqueness: a number can be shared while the sentence around it differs.

## ⛔ Check #228 — the twelfth overstatement, against my own prior warning
*"outside **all six gates**"* — R621 measured 0 flips **under one mutation** and called `n_flip` **a
lower bound on coverage** in its own README. **I quoted my own upper-bounded measurement as an
absolute, one round after writing the bound that says not to.**

## The sentence I can no longer write
> *"the deliverable is `STATEMENT.md`, and `DEFINITION.md` anchors it."*

**The deliverable is three documents, the largest carries 80% of its content alone, and the assurance
suite has never opened it.**

## NEXT
The arc's remaining work is now clearly located, and it is not another gate. **Nine of the seventeen
unique findings cite rounds in the 280–360 band**, which predates every round in this arc —
so the question is whether they were **superseded and never marked** or **still live and never
carried**. Take the six that name a clause (②, ③, the register) and check each against the current
`② ∧ ③`: a finding that contradicts the live definition is a retraction owed, and one that supports
it belongs in the gated pair.
