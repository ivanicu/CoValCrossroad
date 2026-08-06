# R764 · ③-any is not empty — `generic` is a core under the clause's strictest reading, below the published comparator

**On **86 arms** (R534 measured 41), the extension of ② ∧ ③-any is **non-empty in 4 of 8 baseline
cells**: `generic` at **p005, p025, p050**, and `gen` joins it at **p000**. ⭐ **The page's "the
extension is EMPTY" is true at the published comparator and above, and false below it** — so it is a
claim about one cell of a (reading × baseline) grid, stated without the cell. **WORLD B.**

## the stopping rule bound, and this round moved the definition

R763 registered *1 object headline in 24 → R764 may not be another apparatus round.* This is the
object round: it changes what the deliverable says about clause ③'s second reading.

## ⛔ D1 — I corrected R534's nesting BEFORE writing code, from R534's own text

R534 computed `ext_any` and `ext_judge` with the **same** expression (`klass(a) == "neither"`),
annotated *"same here; stated, not assumed"*. Its own headline paragraph says the opposite:

> *"an arm can read the responses' judged satisfaction while reading no human input at all — a class
> ③-any's phrase does not cover, because **a judge is not an annotator**."*

Under that sentence the **sat** class is **admitted** by ③-any. Corrected readings:

| reading | excludes | admits |
|---|---|---|
| ③-rank | rank | weight, sat, weight+sat, neither |
| **③-any** | rank, weight, weight+sat | **sat**, neither |
| ③-judge | rank, weight, sat, weight+sat | neither |

Nesting `judge ⊆ any ⊆ rank` is **algebra**; whether the smallest is zero is the measurement.

⚠ **AND THE CORRECTION CHANGED NOTHING IN FACT.** ③-any equals ③-judge in **every one of the 8
cells**, because all three sat-class arms (`topvar_k4`, `_08b`, `_08bR`) fail ② at every baseline.
The repair was right in principle and **null in effect on this population** — reported as a null,
not as a finding *(ledger 1069)*.

## ⭐ the grid — 3 readings × 8 baselines, tags (objects)

| baseline | \|②\| *(SHAM: no clause)* | ③-rank | ③-any | ③-judge |
|---|---|---|---|---|
| **p000** | 24 | 11 (9) | **2 (2)** | **2 (2)** |
| **p005** | 23 | 10 (8) | **1 (1)** | **1 (1)** |
| **p025** | 21 | 9 (7) | **1 (1)** | **1 (1)** |
| **p050** | 21 | 9 (7) | **1 (1)** | **1 (1)** |
| p075 | 18 | 7 (5) | 0 | 0 |
| p095 | 16 | 6 (4) | 0 | 0 |
| **published** | 17 | **6 (4)** | **0** | **0** |
| p100 | 10 | 0 | 0 | 0 |

**The arms:** `generic` at p005/p025/p050; `gen` **and** `generic` at p000.
**The confound registered before the run is answered by the `|②|` column**: at p050, ② admits 21 of
86 — it is not permissive, so ③-any's single member is not an artifact of ② admitting everything.

**E1 · the partition over 86 arms** — rank **17** · weight **20** · sat **3** · weight+sat **3** ·
neither **42** · UNPARSED **1**. R534 saw 4 / 10 / 1 / 1 / 25.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **PROVENANCE** | R534's 41-arm partition reproduced **exactly** — `{rank 4, weight 10, sat 1, weight+sat 1, neither 25}`; the round exits 2 otherwise, because a classifier that cannot reproduce the partition it extends is not the same instrument |
| **POSITIVE** | `oracle_k4`→rank, `topw_k4`→weight, `topvar_k4`→sat, `random_k4_s1`→neither. Band: all-`neither` fails the first three, all-`rank` fails the last |
| **g=0** | `zzz_k4` is **UNPARSED**, not `neither` — and `neither` is the class that *grows* ③-any, so a silent assignment there would have manufactured World B |
| **NEGATIVE** | 200 random 5-class partitions give ③-any at published **6.90 [4, 11]** against the real **0**. So an arbitrary partition does *not* yield an empty ③-any — the emptiness at the published cell is a property of the source's classes |
| **PLACEBO** | 3 `*_sham` arms, entering **0** extensions in **0** cells |
| **SHAM** | ② with no clause at all is the `\|②\|` column — ③ is binding in every cell (17 → 6 at published) |

## ⛔ three instrument defects, two of which ran in the page's favour

**① `parses()` was stricter than the classifier it extends.** The first version accepted only a rule
prefix, marking `gen`, `generic`, `gen_sham`, `coval_core_sham` **UNPARSED** — while R534 assigns
exactly those to `neither`, and **`neither` is ③-any's entire candidate pool.** A stricter parser
emptied the class the round exists to measure. Repaired to *rule prefix OR named in R294's census*;
`③-any` went **0 → non-empty in 4 cells** *(ledger 1070)*.

**② the object map covered 4 groups, not 8.** I loaded R730's `objects_of_the_seven`; every other tag
mapped to itself, so the **objects column was silently reporting tags** and the UNIT control this
round declared was decorative. Repaired to `multi_tag_classes` (8 cliques): the published cell is
**6 tags = 4 objects**, not 6 = 6 *(ledger 1071)*.

**③ my registered branch was unit-inconsistent.** I registered `UNPARSED >= 1 → WORLD C`, whose
stated world is *"the partition does not extend to today's **population**"* — a claim in the
**object** unit — while `UNPARSED` counts **tags**. R730 settles the one case: `generic_reprov` is a
re-provenance run in the object class `[generic, generic_reprov, provenance_probe]`, so the count is
**1 tag, 0 objects**, and the two units give **different registered verdicts (C vs B)**. The round
**states the conflict before its verdict line, names the object unit as the one its own UNIT control
mandates, and prints the tag-unit verdict rather than discarding it** — the remedy owed since
ledger 1065 *(ledger 1072)*.

## ⚠ and 12 artifacts were excluded, on evidence, named

**7** carry a **foreign key schema** (`load_sat` splits on `|` into 3 fields and gets more) — they are
another corpus: `transport_{gen, gen_sham, generic, randblind_s0/s1/s2, vacuous}`. **5** do not cover
all 968 prompts: `coval_core_2bA/2bB`, `promptecho`, `promptecho_sham`, `provenance_probe`. Excluded
by what they *are*, not by a name pattern, and counted.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| *"③-any — the extension is **EMPTY**"* | **true at the published comparator and above; FALSE below it.** Non-empty in 4 of 8 cells, and the members are named |
| *"③-rank is what the code implements, extension **5 arms**"* | unchanged as a claim about the committed population; **on today's 86 arms the published cell is 6 tags = 4 objects** |
| ③-any and ③-judge are different readings *(D1)* | **true by construction, null in effect here** — identical in all 8 cells because the sat class never clears ② |

## the sentence I can no longer write

*"the extension under ③-any is empty."* It is empty **at and above the published comparator**, and
`generic` is admitted at three baselines below it.

## NEXT

③-any is non-empty exactly where ② is weakest, so the two clauses trade off along one axis and the
page reports the single cell where the trade lands at zero. What is **not** yet asked is whether
`generic` — the arm that makes ③-any non-empty — is admissible **as a core at all**: it is the
comparator's own family, `sat_genericpool16`, and ② is *"scores better than a strong generalising
prompt-blind set"*. If `generic` is a subset of the pool the baseline is drawn from, then at low
baselines ② is comparing the pool to itself and ③-any's non-emptiness is a **self-comparison**, not
a core. The registered quantity is the overlap between `generic`'s criterion set and the baseline
subsets it clears, computed by `select_core`'s own core JSONs — which decides whether this round
found a second live reading or a degenerate cell.
