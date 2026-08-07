# R858 · how often does my own NEXT line point at nothing?

**Arc A25 — can the instrument be run at all.** ⚠ **The instrument here is me.**

## ⛔ WHY, AND THE ROUND THAT PROVOKED IT

This round's planned work — *"compute the three clause bars on the second corpus"* — **was blocked by
prior art**: R603 already found the second file is **a second DATASET, not a second RELEASE** (WORLD
B, **different KIND**, 2 of 5 requirements unsatisfiable, 0 shared top-level keys). **Row 5 of the
impossibility register is not discharged.**

**That was the fourth blocked NEXT of the session.** §4 names the NEXT line as *"the highest-risk
sentence in a report: written last, the one a later round acts on, and the only one with no control
attached"*, and its remedy is literal: **"before writing a closing sentence that quantifies, run the
count."** So I ran the count on myself.

## ⚠ THE INSTRUMENT FAILED FIRST, AND THAT IS RECORDED

The first extractor matched `NEXT` anywhere in a commit body and returned **87 of 89** — implausible
on its face, and the strings were body fragments. **A grep is a measuring instrument, committed live.**
Corrected: **anchored at line start** (`^NEXT\b[^:]*:`), scoped to commits since the pre-session head,
with a **positive control** — a commit known to carry a NEXT must match. **29 of 31 · PASS.**

## ⭐⭐ RESULT — 26 NEXT lines of my own

| outcome | n | share |
|---|---:|---:|
| **BLOCKED or already answered** | **7** | **27%** |
| question **FORCED** by algebra (caught by the arithmetic check) | 2 | 8% |
| not run · redirected · superseded · partial | 5 | 19% |
| **executed as written** | **11** | 42% |

**The seven, with what blocked each:**

| NEXT | blocker |
|---|---|
| add a fitted-combiner class | **prior art** — R824/R825 had done it |
| draft both wordings and compute extensions | **already in R824** |
| noise component for clauses ①②③ | **refuted by the file's own table** — ① and ③ are DERIVED |
| intersect with the clause-③ set | **population** — only 3 of 9 in that space |
| recompute the conjunction on 99 arms | **clause ③ unmeasurable there** |
| domination test on the other clause pairs | **already committed in R347's verdict string** |
| the three bars on the second corpus | **R603 — different KIND** |

## ⭐⭐⭐ THE FINDING IS ABOUT *WHEN* THE CHECK RUNS, NOT WHETHER IT EXISTS

**Every one of the seven was caught** — by the prior-art check at the **start of the following
round**. So the check works. ⛔ **But it runs one round too late: the NEXT is written, committed, and
becomes the next round's framing before anything tests it.** Four of the seven cost a round's opening
to discover.

⭐ **The remedy is not a new check. It is moving the existing one:** *the prior-art check belongs
before the NEXT line is written, not after it is acted on.* **A NEXT is a claim that something is
undone — and this project treats every other claim as needing a check before publication.**

## ⚠ WHAT THIS IS NOT

- **Not machine-verifiable.** The classification is **mine, by hand, from the committed record**. A
  different reader could classify `REDIRECTED` and `SUPERSEDED` differently. **The population is
  reported whole and every row is named** so the disagreement is locatable.
- **Not a claim that 27% is a rate.** One session, one operator, one project. **It is a count, not an
  estimate**, and no interval is offered because none is identified.
- **Not that the blocked NEXTs were worthless** — two of them (`the clause-③ intersection`, `the
  conjunction on 99`) produced real findings *about why they were blocked*.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| an independent classification | a second reader over the same commit bodies |
| a rate rather than a count | many sessions, and a stable definition of "blocked" |
