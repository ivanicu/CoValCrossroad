# R715 · does any per-instance predicate separate, and is it F1? — yes, and no

**Across the `986` cores the release ships, F3's instance form admits `1.0000` with **one** distinct
value — DEGENERATE, it separates nothing. A per-instance PROVENANCE predicate does separate: mean
verbatim overlap between a core and its own full rubric is `0.0655`, `794 of 986` have **zero**
overlap, and exactly `1` core is drawn wholly from its rubric. ⛔⛔ And it is **NOT F1** — written
down before the run.**

## check #317 — it holds

✓ 1 of 3 clauses evaluable on the 986, and F3 admits 1.0000 there. Both from R714's artifact.

## the instance predicates

| predicate | mean | min | max | distinct | separates? |
|---|---|---|---|---|---|
| **F3 size `1<k≤4`** | 1.0000 | 1.00 | 1.00 | **1** | ⛔ **DEGENERATE** |
| **PROVENANCE `core∩full`** | **0.0655** | 0.00 | 1.00 | **7** | ⭐ **SEPARATES** |
| `k == 4` *(control)* | 0.9554 | 0.00 | 1.00 | 2 | ⭐ separates |

**Provenance distribution:** `{0.0: 794, 0.25: 132, 0.5: 46, 0.75: 7, 0.33: 5}` — and exactly **1 of
986** cores is a subset of its own rubric.

⭐ **So the released cores are NOT selections from the full rubric; they are written fresh.** That is
what §4's retired clause *"drawn from a rubric"* asserted, and what nothing here had measured **per
instance**.

## ⛔⛔ and it is NOT F1 — recorded in the preregistration before the run

F1 says the criteria were selected **without reading the outcome labels**. The full rubric **is not
the labels**, and the labels are not in this file at all. **Naming this predicate "F1 restated" would
be the a-label-is-not-a-description error.** It is a different predicate, and **F1 remains without an
instance form.**

## controls — 6 PASS, 0 FAIL, byte-identical across runs and a changed hash seed

| control | returned |
|---|---|
| **POSITIVE** | `k == 4` (the card's ~95%) → mean **0.9554**, 2 distinct — a known split registers |
| **g=0** | "the core is non-empty" → **1.0000**, 1 distinct, reported **DEGENERATE**, not passing |
| **NEGATIVE** | core vs a **different** conversation's rubric → mean **0.0000** — the overlap is a property of the **pairing**, not of criteria vocabulary |
| **SHAM** | `coval_full` against **itself** (cross-field ingredient removed) → exactly **1.0000** |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |

## specification sweep — 3 matchings × 2 comparisons, all reported

| matching | comparison | mean | zero-overlap share |
|---|---|---|---|
| verbatim | own | 0.0655 | 0.8053 |
| verbatim | shifted | **0.0000** | 1.0000 |
| casefold+strip | own | 0.0778 | 0.7708 |
| casefold+strip | shifted | **0.0000** | 1.0000 |
| first-40-chars | own | 0.1777 | 0.5213 |
| first-40-chars | shifted | **0.0003** | 0.9990 |

⚠ Verbatim is the **strictest** matching, so a looser one can only **raise** overlap — **the sweep
bounds the answer from both sides** rather than reporting one cell. Even at the loosest, mean overlap
is 0.1777 and the shifted control stays at 0.0003.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** F3 admission | 1.0000 [0.80, 1.00] | **1.0000**, degenerate |
| **B** zero-overlap share | 0.70 [0.30, 0.95] | **0.8053** |
| **C** mean overlap | 0.10 [0.01, 0.40] | **0.0655** |
| directional | provenance separates where F3 does not | **HOLDS** |

## limits

- **Separating is not being right.** Whether this predicate is the one a definition of "core" should
  use is **construct validity**, and it is impossible here.
- The predicate is a property of **this release's** instances, not of cores.

## impossible here

| criterion | what it would require |
|---|---|
| restating F1 | the outcome labels, which are not in this file |
| whether the separating predicate is the right one | an external standard |
