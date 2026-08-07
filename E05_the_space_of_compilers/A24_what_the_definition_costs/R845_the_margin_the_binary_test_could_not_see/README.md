# R845 · the MARGIN the binary test could not see

**Arc A24 — what the definition costs.**

## ⛔ WHY THIS IS A GAP AND NOT A RE-RUN

**R711 is correct and is not redone here.** It swept all five base/sham pairs, found clause ②
separates **2 of 5**, and priced that against an *exactly enumerated* null over **445,891,810**
admissions: random admission separates **1.7247** on average and reaches ≥2 with **p = 0.5727**. Six
controls, three admission sizes, two byte-identical runs.

⭐ **But R711 states its own ceiling and never follows it:** *"separation is only POSSIBLE where the
base is admitted — 2 of 5 pairs. So the residual is **2 of 2 possible**."* **A statistic whose
maximum attainable value is 2, scoring 2, is saturated.** R711 says `margin` **zero times**.

⚠ This project has now twice mistaken a resolution limit for a fact about the world — the neutral-gap
bound, and entry 1352's *"undecidable"*. **This is the third check of the same kind.**

## ⭐ CONTROLS

| control | result |
|---|---|
| **PLACEBO** all **17** arms against themselves | **exactly 0 · PASS** — the kill precondition |
| **MAGNITUDE REFERENCE** R711's 3 same-family NON-sham pairs, taken from its committed artifact | `oracle_k4/fit1` **+0.0141**, `random_k12_s0/s1` **+0.0051**, `topw_k1/k12` **−0.0124** |

⚠ **The reference is NOT a null** — those arms genuinely differ, so a non-zero margin is expected. It
bounds how large a margin *mere arm-difference* produces: **|margin| ≤ ~0.014**.

## ⭐⭐ RESULT — world B. Every annotator, no draw, therefore no seed.

| pair | metric | margin | 95% CI | MDE | boot p | R711 binary |
|---|---|---:|---|---:|---:|---|
| `coval_core` | graded | **+0.0709** | [+0.0615, +0.0806] | 0.0137 | 0.0002 | SEPARATED |
| | exact | +0.0265 | [+0.0203, +0.0329] | 0.0091 | 0.0002 | SEPARATED |
| **`full`** | graded | **+0.0483** | [+0.0385, +0.0583] | 0.0141 | 0.0002 | **— not separated** |
| | exact | +0.0167 | [+0.0112, +0.0224] | 0.0080 | 0.0002 | — |
| **`gen`** | graded | **+0.0524** | [+0.0416, +0.0637] | 0.0156 | 0.0002 | **— not separated** |
| | exact | +0.0228 | [+0.0164, +0.0293] | 0.0093 | 0.0002 | — |
| `promptecho` | graded | +0.0122 | **[−0.0067, +0.0302]** | 0.0260 | **0.1920** | — |
| | exact | +0.0130 | [+0.0044, +0.0216] | 0.0124 | 0.0035 | — |
| `topw_k4` | graded | **+0.0733** | [+0.0631, +0.0835] | 0.0143 | 0.0002 | SEPARATED |
| | exact | +0.0286 | [+0.0225, +0.0347] | 0.0088 | 0.0002 | SEPARATED |

**MULTIPLICITY: 10 cells tested · 9 survive BH at q = 0.05** (threshold at rank *k* is `0.05·k/10` —
the largest is `q` itself, not `q/C`). **The single non-survivor is printed: `promptecho` graded,
p = 0.1920.**

⭐ **`full` and `gen` carry resolved positive margins that the binary test scored as nothing** — for
those pairs *both* arms were rejected by clause ②, so separation was **structurally impossible**.
**R711's null measured the ceiling, not the clause.**

## ⭐⭐⭐ POISON CHECK — and it revises R844

`sham − genericpool16` (the arm that reads no prompt at all), graded:

| sham | vs floor | verdict |
|---|---:|---|
| `coval_core_sham` | −0.0466 [−0.0558, −0.0376] | **POISON** |
| `full_sham` | −0.0818 [−0.0919, −0.0718] | **POISON** |
| `gen_sham` | −0.0594 [−0.0691, −0.0502] | **POISON** |
| `promptecho_sham` | −0.0954 [−0.1130, −0.0773] | **POISON** |
| `topw_k4_sham` | −0.0513 [−0.0606, −0.0420] | **POISON** |

⛔ **All five. Misdirection actively hurts for EVERY arm measured** — reading the *wrong* conversation
is worse than reading none.

⚠ **This DOWNGRADES R844's own conclusion.** R844 said the deflation is *"ARM-SPECIFIC"*, from one
arm of mine against one arm of theirs — **n = 1 versus n = 1.** Across five pairs the property is
**uniform**, so `coval_core` is not special. ⚠ **What this does NOT license: calling their A1 the
outlier.** A1 is not among these five and was not measured here.

## ⭐ WHAT IT DOES TO THE FORMULATION — the actionable part

**Clause ② as a BINARY admission test is at chance (R711, correct). The property underneath it holds
for every arm measured (this round).** So what is weak is **the binarisation**, not the property.

⭐ **A clause that asks *"is it admitted?"* discards the margin, and the margin is where the content
is.** The definition should state a **margin against the arm's own wrong-prompt twin**, with its
interval — not an admission verdict.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| causally identified | an intervention on the compiler, not a re-scoring |
| cross-release | a second release |
| construct validated | an external gold standard for the agreement metric |

⚠ **N/A with what each would require — never "planned".**
