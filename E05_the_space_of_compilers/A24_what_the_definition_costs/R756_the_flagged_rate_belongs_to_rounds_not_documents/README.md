# R756 · the flagged rate belongs to ROUNDS — and R753's headline was mostly artifact ABSENCE

**⛔⛔ RETRACTION. R753 reported `FORMULATION.md` at a **0.8000** flagged rate against `STATEMENT.md`'s
**0.1793** and read it as a governance signal. **93 of FORMULATION's 125 figures — 74.4% — cite ONLY
rounds that have no `results/` directory at all**, against DEFINITION's **4.0%** and STATEMENT's
**0.0%**. My matcher scored *"the cited round has no artifact"* identically to *"the artifact does not
hold this value"*. **Almost the whole 0.8000 is artifact ABSENCE.** ⭐ And once artifact-less rounds
are excluded, **the direction REVERSES**: FORMULATION's rounds average **0.2188**, STATEMENT's
**0.4455**.**

## check #358 — my own closing line mis-stated the object, third time in this arc

R755 proposed reading FORMULATION's commits "after its last new citation … a further 41 hours". Its
**own artifact** records `terminal_zero_run = 1`. **There is exactly one such commit.** The 41 hours is
elapsed time *since it stopped*, during which the other documents were edited *(ledger 1037)*.

## two cheap checks then killed the replacement design and exposed the retraction

**① Artifact availability by era is UNIFORM** — 1.00 / 1.00 / 0.98 / 1.00 across the four bins. So a
*rounds-have-no-artifacts* story was dead at the era level. **The rival was killed, correctly.**

**② But at the exact-round level the documents are near-disjoint:**

| | FORMULATION | DEFINITION | STATEMENT |
|---|---|---|---|
| distinct rounds cited by figures | 43 | 61 | 97 |
| figures matching FORMULATION's round set | — | 5 of 125 | **0 of 184** |

**`F ∩ S = 0`.** No matched stratum exists. **A matched document comparison is structurally
unavailable, not under-powered.**

## the estimand that IS identified — the round as the unit

**1,186 (figure, round) pairs from 416 distinct figures.** ⛔ **UNIT:** a figure citing three rounds
contributes to three, so rates are computed over **pairs** and both totals are printed.

⭐ **The g=0 control is what caught the retraction.** **27** cited rounds have no `results/*.json`
— R220–R274 and R320, precisely FORMULATION's range. They return **UNDEFINED** and are excluded **with
their count printed**, never scored `0.0` (which reads as perfect support) nor `1.0` (total failure).
**R753 had no such control and scored them as failures.**

| | all rounds | rounds with ≥3 figures |
|---|---|---|
| n | 138 | 76 |
| between-round variance | **0.1396** | **0.0905** |
| sampling null (5 seeds) | 0.1165 | **0.0394** |
| ratio | 1.20× | **2.30×** |
| share at exactly 0.0 or 1.0 | 0.5000 | 0.1842 |

⛔ **A round cited by ONE figure has a rate of exactly 0 or 1 by construction** and inflates the
variance mechanically. The two columns are never merged.

## ⚠ the SHAM is close, and that bounds the finding

Blocking the same figures by **line number** into blocks of the same sizes gives variance **0.0852**
against the observed **0.0905** — a ratio of **1.06×**, where the random-reassignment null gives
**2.30×**. **The two nulls answer different questions:** random reassignment destroys *all* structure;
line-blocking preserves *positional* clustering, and adjacent figures share support status. **So much
of the clustering is positional rather than specifically about rounds**, and the round effect is
**2.30× a structure-free null but only 1.06× a position-preserving one.** That is reported rather than
resolved in my favour.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | **R392**, chosen by **artifact size** (116,141 bytes) *before* its rate was computed — **not selected on the outcome** — scores **0.2000** against a pooled **0.6233**. Band: an empty artifact gives 1.0 by construction, floor 0.0 |
| **g=0** | 27 artifact-less rounds → **UNDEFINED, excluded, counted** |
| **NEGATIVE** | reassignment preserving group sizes, 5 seeds → variance collapses **0.0905 → 0.0394** |
| **SHAM** | ingredient **absent** — line-blocked, same sizes → **0.0852** |
| **PLACEBO** | variance recomputed, difference exactly **0** |

**CONFOUND, printed not absorbed:** `corr(artifact size, flagged rate)` over rounds with ≥3 figures is
**−0.1382** — weakly negative, so bigger artifacts do hold more of their numbers, but it does not carry
the effect.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 rounds with an artifact | 150, band [50, 400] | **138** | ✓ |
| P2 between-round variance (≥3) | 0.09, band [0, 0.25] | **0.0905** | ✓ near-exact |
| P3 sampling null (≥3) | 0.03, band [0, 0.25] | **0.0394** | ✓ |
| P4 degenerate share | ⚠ band spanned [0, 1] — **cannot fail** | 0.5000 / 0.1842 | **reported, not scored, and labelled** *(R751 made this mistake silently)* |
| P5 rounds in >1 document | 20, band [0, 100] | **36** | ✓ |
| **D** FORMULATION's rounds flag higher | true | **FALSE — 0.2188 vs 0.4455** | ⛔ **inverted** |

## ⛔ what this retracts

| published | stands as |
|---|---|
| `FORMULATION.md` **0.8000** vs `STATEMENT.md` **0.1793** *(R753)* | **74.4% of FORMULATION's figures cite only artifact-less rounds.** The gap is dominated by artifact ABSENCE, not provenance quality |
| "the ungated document is 4.5× worse" *(R753 directional)* | **inverted** at the round level once absence is separated: **0.2188 vs 0.4455** |
| "the rate is a document property" | **it is a ROUND property** — 2.30× its structure-free null |

⛔ **And the document-level implication is ALGEBRA:** with near-disjoint round sets a document's rate is
a **weighted average** of its rounds' rates, so *"documents differ"* **follows** from *"rounds differ"*
plus disjointness. **Only the variance is measured.**

## the sentence I can no longer write

*"`FORMULATION.md` carries 100 unsupported figures."* Most of them cite rounds that have no artifact to
be unsupported by, and a matcher that cannot tell absence from silence was reporting the wrong quantity.

## NEXT

The 27 artifact-less rounds are the residue and they are a different object from a flagged figure: a
round with no `results/` directory either declined to persist one or predates the convention. Both are
checkable from the round directories themselves — what those 27 contain instead, and whether the
campaign's own round template was in force when they ran. The unit is the round directory rather than
the figure, the instrument is a listing rather than a matcher, and the outcome separates *this round
chose not to persist* from *this round predates persistence*, which decide whether the 93 figures are
repairable at all or simply cite a pre-artifact era.
