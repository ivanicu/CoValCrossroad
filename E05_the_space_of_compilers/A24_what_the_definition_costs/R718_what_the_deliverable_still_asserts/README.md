# R718 · what the deliverable still ASSERTS — §0.2's question, asked of the statement not the ledger

**There is a residue, and it is `2` of `12` blocks. Reported first because §0.2 requires it:
`⭐ §4's FALSIFIER DOES NOT FIRE AGAINST ③ (R688)` and `⭐ LINEAGE OF THE EXTENSION — what supports
the number 5 (R676–R682)` are the asserting blocks no later round has amended. ⛔⛔ And the
load-bearing caveat: **standing unamended is not truth — it means unattacked.****

## check #320 — the count is wrong by one, again in a class the gate cannot catch

⛔ *"three consecutive rounds have ended in a bound"* is **false**. R715 produced a **value** — a
separating predicate at 0.0655 — and only R716 and R717 ended in bounds. **It is two.** Seventh false
closing claim in this arc, and the **third** of the precedence/count species the quantifier gate
cannot see.

⛔ **And its proposal needed amending before it ran.** It asked me to count rounds ending in a bound
versus a value. **§0.2 forbids exactly that as a product** — *"never lead with the ledger, never end
on it"* — and a count of my own retractions is the activity metric that section opens by forbidding.
**The admissible question is the one §0.2 demands instead: what stands.**

## ⭐ what stands — reported first

| | |
|---|---|
| ⭐ | `§4's FALSIFIER DOES NOT FIRE AGAINST ③` *(R688)* |
| ⭐ | `LINEAGE OF THE EXTENSION — what supports the number 5` *(R676–R682)* |

## what it cost, in one block

**12 blocks · 4 assert · 3 record a withdrawal · 3 qualify · 3 carry a later round's amendment.**
Two asserting blocks (R701's three-clause formulation, R704's held-out zero) were themselves amended
by later rounds in this session.

## controls — 6 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **POSITIVE** | R701's block → `ASSERTS`, R696's → `WITHDRAWS`, both as independently stateable |
| **g=0** | a block citing no round → `amended=None` — **UNKNOWN, never a silent clean pass** |
| **NEGATIVE** | bodies scrambled against headings → amended counts `[4, 4, 2]` vs the real `3` |
| **SHAM** | the same test on `DEFINITION.md`: **79 blocks, 5 amended = 0.0633** vs the statement's **3/12 = 0.2500** — per block, an append-only record inverts less |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |

## ⛔ my own SHAM failed twice before it was a control

**① It passed on an empty population.** `DEFINITION.md` uses plain `##` headings, not blockquoted
ones, so the extractor returned **0 blocks** and my guard `len(dbs) == 0 or …` let it through —
**§4's *empty population passes*, inside the control written to guard against exactly that.**

**② Then its expectation was mis-specified.** With a document-appropriate extractor it compared **raw
counts** across documents of very different size: 5 > 3 said FAIL, while `0.0633 < 0.2500` says PASS.
**A control comparing two populations must compare rates.** Both defects are recorded in the code
beside the fix.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** claim blocks | 12 [8, 20] | **12** |
| **B** asserting blocks | 4 [2, 10] | **4** |
| **C** asserting blocks later amended | 2 [0, 4] | **2** |
| directional | withdrawals+qualifications > assertions | **HOLDS** (6 > 4) |

## limits

- ⛔⛔ **Standing unamended is NOT truth.** It means **unattacked**. This arc withdrew F2's A2
  justification, its sham residual and its exclusion count in three consecutive rounds, and **every
  one of those blocks stood unamended until the round that killed it.**
- The marker reading is a **convention I wrote**, positive-controlled against two independently
  stateable blocks — a reading, not a measurement.
- The amendment test is exact but **blind to a correction that cites no round**.

## impossible here

| criterion | what it would require |
|---|---|
| whether an unamended block is true | not answerable by any self-audit |
| cross-release | a second release |
