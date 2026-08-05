# R517 · Clause ④'s independence has never been observable

**Decision this makes safe:** whether the deliverable may cite ④ as an established, load-bearing
clause.

**Estimand:** the count of arms passing ② and failing ④ — the only cell in which ④ adds anything —
**and its expected count under independence**, which bounds what an observed 0 can mean.
**Identification: PARTIAL, and that is the finding.**

## Result

| population | n | ②pass | ④fail | E[both] | cell identified? |
|---|---|---|---|---|---|
| home judge **J** | 56 | 0 | **0** | 0.000 | ⛔ no — **④'s marginal is 0** |
| **second release** | 7 | **0** | 7 | 0.000 | ⛔ no — **②'s marginal is 0** |

**In both populations one marginal is degenerate, so the informative cell is empty BY CONSTRUCTION.**
Where a marginal is 0 the joint is a **DERIVATION**, not a measurement — it could not have come out
otherwise.

## Controls
- **Positive** — the instrument must see exclusion where it exists: ④ excludes **22 of 93** arms
  overall. **PASS.** So a zero at J is about J, not about a blind instrument.
- **Negative** — pair the home population with ④'s *global* fail rate (22/93 = 0.237) and a 50% ②
  pass rate: expected **6.62 arms** in the cell. **PASS** — a non-degenerate pairing would have
  ample power, so the zeros are a property of the **pairing**, not of the arms.

## What this changes

The STATEMENT cites *"④ excludes all 7 arms on the second release — not vacuous"*. **True, and not
evidence.** On that release **② excludes the same 7** *(R434: ② admits 0 of 7)*, so the exclusion
is not work ② was not already doing. At home, ④ excludes **nobody** *(R436: `excluded_at_J == []`,
verdict `W-REDUNDANT-AT-J`)*.

⭐⭐⭐ **④ is UNVERIFIED, not subsumed — and that is the opposite of ①.** ① was *measured* redundant
on 41 arms with a stated mechanism and a margin. ④ has never been placed in a population where its
independence could fail. **Folding UNVERIFIED into OVERTURNED manufactures a false acquittal; folding
it into ESTABLISHED manufactures a false clause.**

**Impossible here:** a population with both marginals non-degenerate. It needs arms that clear the
blind-pool bar **and** are scored against the criterion-free rules on the same release — a scoring
run, not a reanalysis.
