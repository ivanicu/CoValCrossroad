# R1098 — the two comparator families **NEST**. Blind-family statements are upper bounds.

**The decision this round makes safe:** whether the arc's synthetic-family numbers transfer to the
released family. **They do — as one-directional bounds** — and the mechanism is measured.

## ⛔ Two things refused before the round began

**Prior art.** R1055 **already** excludes comparators from candidacy — `COMPARATORS = ["generic",
"genericpool16"]`, `if nm in comps: continue`. **So R1095's obstruction was never one for the
released family**, and the synthetic scoping was a choice rather than a necessity.

**A derivation.** Admission is **per-arm**: whether arm X beats the family does not depend on which
*other* arms are candidates. So *"does removing `generic` from candidacy change the block?"* is
forced — by exactly the two removed arms. Reporting it would be bookkeeping.

## The two ②′ sets, same operator and target, differing only in the family

| | |
|---|---:|
| released family (2 comparators) | **24** |
| blind family (15), comparators removed | **33** |
| intersection | **24** |
| **released-only** | **0** |
| blind-only | **9** |

`blind-only` = `gen`, `generic_reprov`, `greedy_k12_fit1`, `greedy_k4_fit1_08bR`, `indep_k12_fit1`,
`indep_k4_fit1_08bR`, `topw_k1`, `topw_k12`, `topw_k2`.

⭐ **The released set is a strict SUBSET of the blind set.** So **every blind-family statement in this
arc is an upper bound on released-family membership** — the scoping was conservative in a nameable
direction, not a different world. **R1095's scope caveat is weaker than it reads.**

## ⭐ And the nesting is mechanistic, measured rather than assumed

| comparator | mean score |
|---|---:|
| `generic` | 0.5514 |
| `genericpool16` | **0.5422** ← the weaker released one |
| all 15 blind subsets | **[0.4622, 0.5023]** |

**Every blind subset scores below the weaker released comparator.** The blind family is uniformly
weaker, so it admits more — exactly what R1088's proximity result predicts, now confirmed at the
family level.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE the three released cores are in **both** sets | PASS |
| g=0 the released set contains **neither** of its own comparators — candidacy really was excluded | PASS |
| NEGATIVE the two sets are **not identical**, so the family choice mattered | PASS |
| SHAM cutting the released family to **one** comparator changes the set by **0** (R1055's own committed row) — so the nesting is not an artifact of family *size* | PASS |
| PLACEBO each set against itself is empty | PASS |

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| a family certified, disjoint **and not weaker** than the released one | **N/A** | R1097 established text-blindness over prompt-specific rubrics means a fixed external rubric — the release ships exactly two, and they are the released family |
| cross-release | **N/A** | a second release |

`run.py` · `results/families_nest.json`
