# R463 · both orderings eliminated — the order is arbitrary, and this round says so

**The decision this round makes safe:** the basis for the remaining declaration work. **There isn't
one, and that is the finding.** `W-FORCED`.

## ⛔ The announced replacement is forced by the document's own construction

R462 proposed ordering by load-bearingness, made mechanical as *"count, per anchor, how many
clause-sections cite its round."* Measured on the object: **21 round-markers, each round's paragraph
living in exactly one section** → `sections_citing(round)` is **min 1, max 1 over 21 rounds**.
**Flat, by construction, and it cannot discriminate.** *Thirty-first announced step checked.*

Combined with R462 (age **refuted** by measurement), **two proposed orderings, both eliminated.**
This round declares the next **contiguous** block for convenience and **says that is arbitrary**,
rather than inventing a third story about where defects live.

## ⛔ Two bugs in this round's own instrument, both caught by running it

**① The verdict branch tested a different statistic than its estimand named.** It branched on
`len(sections_containing_markers)` — which is **2** (`### ②` holds 19 markers, `### ③` holds 2) —
while the estimand is `sections_citing(round)`, which is **1 for every round**. §4 sub-kind ③. The
first run returned `W-DISCRIMINATES` on the wrong quantity.

⚠ **And the same mismatch had already reached my prose:** an exploratory command matching `## `-level
headings reported **1** section; the round matching any `#` found **2**. *The instrument's unit
changed between the check and the round* — R460's mixed-object class, one round later.

**② An aliasing bug.** `runs.append(run); run.clear()` **empties the list just appended**, so every
completed run was recorded as empty and the longest chain came out as **1 paragraph / 0.1%**. Fixed
by starting a new list: the true answer is **4 paragraphs over 10 lines = 0.9%** of 1,053.

**Both bugs flattered a conclusion I had already stated in prose.** ⚠ Neither was found by reading —
both were found because the round recomputed what the exploratory command had reported.

## ⭐ A real fact the corrected census gives, which the estimand did not ask for

**Clause ② carries 19 of 21 round-markers; clause ③ carries 2, and every other clause carries none.**
That is a measurement of where this campaign's attention actually went — 90% into one clause — and it
is *rounds-per-section*, a different statistic from the one that was forced. Reported as its own fact,
never merged with the ordering result.

## ③ The work — a third independent block, and the cumulative negative

| block | declared diff | w=200 | w=400 | w=800 | w=1600 |
|---|---|---|---|---|---|
| **R430–R441** *(new)* | 21 | 3 | **0** | **0** | **0** |
| R442–R454 | 32 | 0 | **0** | **0** | **0** |
| R455–R462 | 18 | 3 | **0** | **0** | **0** |

w=200 flags by block: `r438_gap2, r438_gap3, r437_home_gap` (new) · none (middle) · `r456_gap16,
r456_ratio16, r460_iqr` (recent).

> **71 declared differences across three independent blocks; 0 flagged at every defensible window.
> The comparator defect is not in this document.** Coverage **154 of 265 (58.1%)**.

⚠ **It says nothing about the 111 still undeclared.** Undeclared is not a pass, and three clean
blocks license nothing about a fourth.

## Controls

| control | returned |
|---|---|
| **EMPTY POPULATION** | if no markers are found the round exits **2**, never 0 — a census over an empty set would report *"1 section, 0% chain"* and read as a result |
| POSITIVE — comparator planted at 300 / 1200 chars | FLAGGED below, PASSING above, all four cells ✅ |
| g=0 — a declared-absolute claim | never flagged at any window ✅ |
| **PROVENANCE** | flags printed **with their block**, so 3→6 cannot be read as the new block being worse |
| WINDOW sweep | retained; a flag only at w=200 is a window artifact |

## Impossible here, named

- **a claim about the 111 undeclared anchors** — three clean blocks license nothing about a fourth.
- **an ordering basis** — both proposed have been eliminated and this round supplies no third. **That
  is the finding, not a gap in it.**

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
