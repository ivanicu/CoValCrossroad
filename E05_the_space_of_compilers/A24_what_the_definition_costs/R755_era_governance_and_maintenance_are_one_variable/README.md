# R755 · `UNRESOLVED` on the question asked — and the live document declines just as fast

**`FORMULATION.md`'s citation-adding slope is **−0.0090**; `STATEMENT.md`'s, a document that received
a commit today, is **−0.0074**. The two are indistinguishable. So the decline is not what separates
them — **what separates them is simply that one stopped receiving commits.** ⛔ And the design cannot
go further: **one document stopped, so the treatment is n=1**, and no commit-level sample rescues a
document-level contrast.**

## check #357 — the proposed design died twice before it ran

⛔ **① The arithmetic.** A correlation between commits and flagged rate over **three** documents is not
a measurement — three points always admit a line.

⛔ **② The gauge test, for free.** `git blame` on all three:

| document | lines | oldest | newest | **distinct days** |
|---|---|---|---|---|
| `STATEMENT.md` | 1216 | 2026-08-04 | 2026-08-05 | **2** |
| `DEFINITION.md` | 4726 | 2026-08-04 | 2026-08-05 | **2** |
| `FORMULATION.md` | 2397 | 2026-08-03 | 2026-08-04 | **2** |

**Every line was last touched inside a two-day window.** There is no maintenance gradient in
wall-clock time to measure.

## ⛔⛔ the ontology error that runs back through R753 and R754

| document | commits | first | last | new citations | **max R ever cited** |
|---|---|---|---|---|---|
| **`FORMULATION.md`** | **99** | 2026-08-03 | **2026-08-04** | 105 | **R360** |
| `STATEMENT.md` | 131 | 2026-08-04 | 2026-08-05 | 202 | R754 |

**`FORMULATION.md` is not abandoned.** It has **99 commits** and stopped **41 hours** ago. *Old era*,
*ungated* and *unmaintained* are **not three variables in this repository — they are one**: position
in a three-day burst. **Round ids 164–753 are a LOGICAL clock, and I have been reading them as though
they measured time** *(ledger 1034)*.

⚠ **And the treatment is n = 1.** Exactly one document stopped, so anything correlating with "stopped"
is perfectly collinear with that document's identity. **417 commits do not help** — the treatment is
assigned at the document level. **That is a closed decision, not a gap**: the R753/R754 line cannot be
pushed further inside this repository.

## what IS identified, and what it returned

Within `FORMULATION.md`'s own 99 commits, governance and identity constant:

| | value |
|---|---|
| new citations per commit, mean | **1.0606** (median 1.0, max 15) |
| OLS slope, raw | **−0.0090** |
| OLS slope, per added line | −0.001052 — **same sign**, so not a commit-size artifact |
| shuffled-order slopes, 5 seeds | mean −0.0021, sd **0.0046** |
| first 10 commits / last 10 | **23** / **11** new citations |
| terminal run of zero-adding commits | **1** |

**Neither a reliable slope (−0.0090 vs a −2σ threshold of −0.0092 — it misses by 0.0002) nor a
terminal cutoff.** `UNRESOLVED`, and **the series is published rather than a slope.**

## ⭐ the informative residue is a registered point whose SIGN I got wrong

I registered `STATEMENT.md`'s slope at **+0.05**, expecting a live document to be *adding* citations
at a rising rate. It is **−0.0074** — **the same decline as the stopped document.**

**So "the citing rate declines" is not a property of abandonment.** It is what happens in any document
whose pool of not-yet-cited rounds is consumed faster than it is refilled. **The two streams are
indistinguishable on the axis I built the round to measure** *(ledger 1035)*.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `STATEMENT.md`'s last 20 commits add **23** new citations. Band computed: floor **0** (a counter that never counts), ceiling **202** (its distinct total) — measured value strictly inside |
| **g=0** | **31 of 99** FORMULATION commits add zero citations and are **in the series, not skipped**. A skipped zero would raise the mean and hide the very decline under test |
| **NEGATIVE** | order shuffled ×5 seeds → slopes `[+0.0001, +0.0041, −0.0097, −0.0048, −0.0001]`, mean −0.0021 vs real −0.0090 |
| **SHAM** | ingredient **absent** — added `⛔` markers, a non-citation token: slope **+0.0032** against the citation slope **−0.0090**. **They differ, so the trend is about citing, not commit style** |
| **PLACEBO** | recounted, slope difference exactly **0** |

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 new citations per commit | 3.0, band [0, 30] | **1.0606** | in band, point 3× wrong |
| P2 FORMULATION slope | −0.05, band [−2, +2] | **−0.0090** | ✓ |
| **P3** STATEMENT slope | **+0.05** | **−0.0074** | ⛔ **wrong sign — and that is the finding** |
| P4 zero-adding commits | 40, band [0, 99] | **31** | ✓ |
| P5 max R ever cited by FORMULATION | 360, band [164, 753] | **R360** | ✓ exact |
| D last 10 < first 10 | true | **true** (11 < 23) | ✓ |

⛔ **A derivation I should have labelled in the preregistration and did not:** *new distinct citations
per commit* is partly self-exhausting — the pool of uncited rounds shrinks as a document grows. For
`FORMULATION.md`, whose pool froze at R360, that is close to forced. **The parity with `STATEMENT.md`,
whose pool kept growing, is what makes the comparison informative rather than the slope itself.**

## the sentence I can no longer write

*"`FORMULATION.md` was abandoned."* It has 99 commits, stopped 41 hours ago, and declines at the same
rate as the document I edited today.

## NEXT

The document-level line is closed at n=1, and this round's own residue is that the three deliverables
differ in one observable that is not era, governance or maintenance: **`FORMULATION.md` stopped citing
at R360 while continuing to be edited for a further 41 hours.** Its commits after its last new citation
are readable and are the only place a *decision* would show. Read what those commits changed — whether
they edited claims, removed content, or reorganised — against the same window in `STATEMENT.md`. The
unit is the commit's diff content rather than its citation count, the instrument is the diff rather
than a regex over round ids, and the outcome distinguishes *the document was finished* from *the
document was left mid-edit*, which are different states needing different repairs.
