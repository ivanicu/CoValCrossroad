# R1054 — change the unit from WINDOW to SENTENCE. ⛔ **R1050's claim does not survive: the clause's declared dependencies are flagged at the base rate (`0.667` vs `0.676`, MDE `0.202`).**

**The decision this round makes safe:** whether the definition's clause depends *disproportionately*
on unattributable work. **It does not** — the enrichment is `−0.010` against an MDE of `0.202`.

## ⭐ The sentence unit does not saturate, and that is why it can answer

R1053 showed the window statistic pinned at its ceiling. A 12,000-character window catches every
round the document mentions nearby; **a sentence containing both a clause component and a round id is
an assertion that the component rests on that round.** §4's remedy applied *before* the fact for once:
the instrument's unit and the claim's unit must match, and the claim's unit is a sentence-level
relation.

| | |
|---|---:|
| sentences in DEFINITION.md | **4511** |
| **ceiling** — distinct arc rounds cited in *any* sentence | **70 of 113** |
| **declared** — cited in a *clause-component* sentence | **21** |

**21 ≪ 70 ≪ 113.** The unit does not saturate, so the set is a real, nameable dependency list.

| clause component | sentences | rounds |
|---|---:|---:|
| `resolvably beats` | 9 | 3 |
| comparator family / prompt-blind / certified | 88 | 12 |
| the `q` parameter | 21 | 5 |
| no prompt-specific human labels | 1 | 2 |
| coverage, not imputed | 20 | 10 |

## ⛔⛔ The enrichment test — and it withdraws R1050's claim

| | |
|---|---:|
| declared set flagged (corrected `any` predicate) | **14 of 21 = 0.667** |
| **registry-wide** flagged rate — what a clause-blind set shows | **46 of 68 = 0.676** |
| difference | **−0.010** |
| SE / **MDE (1.96 SE)** | 0.103 / **0.202** |
| resolvable | **False** — the difference is **0.05 of the MDE** |

⭐ **The clause's declared dependencies are flagged at essentially the base rate.** R1050 claimed the
clause *rests disproportionately* on unattributable work; R1053 preserved that as a direction on a
**saturated** window statistic. **At the unit that matches the claim, there is nothing.**

⚠ **And this is a null, not a proof of no enrichment.** The design could not have seen a difference
below **0.202**. What stands is the unconditional fact, which is worse than the one withdrawn:
**`0.676` of the whole registry is unattributable, clause or no clause.**

## Controls

- **POSITIVE** — R1037/R1038 must appear in a sentence about `q`, known from their own committed
  commit bodies rather than invented: **True** (5 rounds in 21 `q`-sentences).
- **NEGATIVE** — a non-existent round id appears in no sentence: **True**.
- **CEILING** — **measured** (70), because R1053 was burned by not measuring one. The declared set is
  well below it.
- **PLACEBO** — a component term appearing nowhere contributes no sentences; reported per component.
- **MULTIPLICITY** — all five components reported with their own sets, not only the union.
- ⚠ **2 registry patterns are not statically readable — reported, never dropped.**

## What this round cannot say

**Declared ≠ necessary.** A sentence citing a round asserts a relation; it does not show the clause
would fail without it.

## IMPOSSIBLE here

- **whether a cited round is NECESSARY to the clause** — **SETTLES: IN-RELEASE**: restate the clause
  without it and re-run the admission operator, one run per cited round. Unattempted, not unavailable.

`run.py` · `results/declared_dependencies.json`
