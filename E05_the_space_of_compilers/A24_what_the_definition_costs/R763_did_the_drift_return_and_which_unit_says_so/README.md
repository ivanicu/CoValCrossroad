# R763 · the drift returned — and both instruments I built to prove otherwise failed their own shams

**Over R739–R762, R664's keyword rule finds **1 object headline in 24**. I built **two** structural
classifiers to fix that rule's declared blind spot, and **both sit inside their own random-block
bands** — the definition block (36.7% of the page) fires **9** against a sham of **[4, 12]**, the
clause bullets (3.1%) fire **2** against **[0, 2]**. ⭐ **The only admissible number is 1 of 24**, so
R664's verdict stands for a second era: **48 rounds, 1 object headline**, and the registered stopping
rule binds R764.**

## check #365 — two findings before R762's proposed round could run

**① The arithmetic in my own NEXT line was wrong.** It said *"if those two intervals cross"* — but
**two overlapping MARGINAL intervals do not imply a non-significant PAIRED difference**, and both
Jaccards are computed against the *same* resampled robust set, so they are paired by construction.
*(The direction is not forced — checked over 2,598 robust-set shapes with the name set a subset of the
rule set, `J(rule) < J(name)` in **15.4%**. The question is fine; the test I specified was wrong.)*

**② P4 surfaced a gate I should have run first.** R676 opens by noting *"of R672–R675, zero make a
claim about the object"*, and **R664 measured exactly this**: `0 of 24`, R640–R663, committed, with
controls, verdict — *"the loop is the defect, and the next round must move the definition or not
run."* **The gate has not been run since**, and R664's glob is hardcoded `R6[0-9][0-9]_*`, so **the
instrument cannot see this era** *(ledger 1066)*.

## the instrument's unit and the claim's unit are not equal — so I built the second unit

R664's own README declares its rule a **lower bound**: a keyword test on a headline, *"the direction
flatters me."* §4's remedy is to name the two units and require them equal.

| | unit |
|---|---|
| **instrument** | a headline STRING (C1) → a DIFF HUNK (C2, C3) |
| **claim** | did the round change what the page says a core IS |

## ⭐⭐ G4 · the unit is a specification, so each was priced against its OWN sham

| unit | % of page | count | sham 95% | admissible |
|---|---|---|---|---|
| **C1** keyword on the headline | — | **1 / 24** | *(R664's controls)* | **YES** |
| C2 edited the definition block | 36.7% | 9 / 24 | **[4, 12]** | ⛔ **NO — inside its own sham** |
| C3 edited a clause bullet | 3.1% | 2 / 24 | **[0, 2]** | ⛔ **NO — inside its own sham** |

**23 of 24 rounds edited `STATEMENT.md` somewhere.** A positional unit covering *p* of the page
therefore catches ≈ *p* of them by chance: C2 caught 9 of 23 = **39%** against a block that is
**36.7%** of the page. **The instrument was measuring its own size** *(ledger 1067)*.

⚠ **So this round did NOT establish that two units disagree.** It established that **the second and
third units are UNVERIFIED**, which is not a disagreement and is not an acquittal either.

## controls — 5 for C1, all PASS; the shams are what killed C2 and C3

| control | returned |
|---|---|
| **POSITIVE-1** | C1 re-run on **R664's own era** returns **exactly 0 of 24**, matching its committed `A_object_headlines: 0, n_rounds: 24`. Band: a rule matching nothing also returns 0 there — excluded by POSITIVE-2; one matching everything returns 24 |
| **POSITIVE-2** | C1 fires on R527 and R519 (R664's known object pair); **C2 fires on R760**, whose commit is known to have amended the ② bullet |
| **NEGATIVE** | C1 does **not** classify R654 as OBJECT; of the 1 round touching no `STATEMENT.md`, C2 fired on **0** |
| **g=0** | an empty headline is not OBJECT; an empty diff is not C2 |
| **PLACEBO** | a keyword-free headline is not OBJECT |
| **SHAM ×2** | as tabled — **both structural units inside their bands** |
| **CONFOUND** *(registered before the run)* | rounds editing `STATEMENT.md` **at all: 23 / 24**. C2 (9) is below that, so it is not *purely* the convention — but the sham shows what remains is chance |

⛔ **AND THE VERDICT STRING ASSERTED WHAT ITS OWN CONTROL FORBADE.** The first version branched on
`|C1 − C2| >= 6` and printed **WORLD C** while the SHAM two lines above said C2 was inside its band.
§4's *the verdict string is not a computation*, and the remedy is the one that row gives: **the branch
must reference every control the round declared.** Repaired — the verdict now computes an
*admissible-unit list* first and reports `C1` alone *(ledger 1068)*.

## the 2×2, with every disagreeing round named

| | C2 OBJECT | C2 apparatus |
|---|---|---|
| **C1 OBJECT** | 1 *(R760)* | 0 |
| **C1 apparatus** | 8 | 15 |

The 8: `R739 · R740 · R741 · R742 · R745 · R746 · R761 · R762`. **C1-only is empty** — no round in the
window claimed the object in its headline without touching the definition block.

## ⭐ what this leaves standing, and it is a production item rather than a retraction

**"Did this round move the definition?" is not reconstructible from the page's diffs.** Two positional
units, two sham failures, and the reason is arithmetic: a round's `STATEMENT.md` edit is large and
scattered, so any positional unit is hit at roughly its own size share. **What it would take is a
per-round DECLARATION recorded at the time** — each README naming the clause it moves, or naming
NONE — because the label is a fact about the round's intent and intent is not in a diff.
That is a signpost at the decision point, and it is the only version of this measurement that can
ever have a positive control.

## the sentence I can no longer write

*"the definition block was edited, so the round moved the definition."* A random block of the same
length is edited just as often.

## NEXT

The registered stopping rule binds and it is not advisory: **C1 = 1 of 24, so R764 may not be another
apparatus round.** R664 said the same thing 99 rounds ago and the loop did not obey it, which is why
this round registered the constraint rather than recommending it. The object-level question that is
open and cheapest is the one R762 was pointing at *before* my NEXT line specified the wrong test:
`③rule` and `③name` differ on **11 vs 4** arms and the extension over today's population is **5**
under the rule and **9** under the list, and no round has asked **which arms a reader of the page
would actually admit** — the deliverable states ③ in prose, and that prose has not been executed
against the 92-arm population: **8 of 68** rounds both read `STATEMENT.md` and load the population,
and all 8 — computed by `grep -l STATEMENT.md */run.py` intersected with `load_sat` — read the page
for **pins or provenance** rather than as a specification. The registered quantity is the admitted set produced by the
page's own words, and the PAIRED difference against the code's, over the same bootstrap.
