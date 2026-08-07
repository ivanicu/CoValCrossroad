# R711 · is the core-vs-sham residual F2 is kept for above a same-size random admission?

**No. Clause ② separates `2` of the `5` sham pairs; a uniformly random admission of `9` of `42` arms
separates `1.7247` on average and reaches 2 or more with exact probability `0.5727` — enumerated over
all `445,891,810` admissions, with no Monte-Carlo error. `STATEMENT.md`'s "kept for the residual it
genuinely owns" is DOWNGRADED.**

Population **the 5 sham pairs in R360's 42-arm ledger** · instrument **exact enumeration of the
separation count at fixed admission size** · baseline **uniformly random admission of 9 of 42** ·
regime **this repository at HEAD**.

## check #313 — the counts hold, the closing claim is false

✓ R707/R708/R710 measured the gate, R709 the object; R392/R433/R709 ran the contains-vs-consumed
treatment and none mentions `coval_core_sham`.

⛔ **"That residual is a SINGLE ARM PAIR" is false — it is TWO.** R694's committed artifact names two
mixed cells, `coval_core/none` and `topw/4`. **Fourth false closing-sentence claim in this arc, and
the one the gate could not catch**: it carries no quantifier from any list, only a miscount.

## the object

| base | admits ② | sham | admits ② | |
|---|---|---|---|---|
| `coval_core` | True | `coval_core_sham` | False | ✓ **SEPARATED** |
| `full` | False | `full_sham` | False | ✗ both rejected |
| `gen` | False | `gen_sham` | False | ✗ both rejected |
| `promptecho` | False | `promptecho_sham` | False | ✗ both rejected |
| `topw_k4` | True | `topw_k4_sham` | False | ✓ **SEPARATED** |

⛔ **DERIVATION, not evidence:** separations = 2. Given R360's committed verdicts this could not have
come out otherwise. **The null is the measurement.**

⭐ **And separation is only POSSIBLE where the base is admitted** — 2 of 5 pairs. So the residual is
**2 of 2 possible**, not 2 of 5: a ceiling of two, and reaching a ceiling of two is exactly what makes
the exact p large.

## the exact null — enumerated, not sampled

| separations | 0 | 1 | **2** | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| probability | 0.1053 | 0.3221 | **0.3575** | 0.1756 | 0.0370 | 0.0026 |

**mean 1.7247 · 95th pct 3 · observed 2 · EXACT P(sep ≥ 2) = 0.5727**

## controls — 6 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **POSITIVE** | plant admitting all 5 bases, rejecting all shams → **5** separations, exact p = **0.002581**; floor (null mean 1.7247) < ceiling (5), so the band is real |
| **g=0** | admission drawn only from non-pair arms → **0** separations — the statistic is not free |
| **EXACTNESS** | enumerated vs 60,000-draw sampled null: max \|Δp\| = **0.00154**. *"No Monte-Carlo error" is a resolution CLAIM and is itself checked* |
| **SHAM** | 3 same-family **non-sham** pairs → 0 separations, exact p = 1.0000 — sham-ness is the ingredient, and removing it removes the signal |
| PLACEBO / UNIT | identical enumerations differ by 0 · instrument unit ≠ claim unit |

## specification sweep — 3 admission sizes × 2 pair sets, all reported

| k | pair set | observed | null mean | exact p |
|---|---|---|---|---|
| **9** | the 5 sham pairs | 2 | 1.7247 | **0.5727** |
| 9 | same-family control | 0 | 1.0348 | 1.0000 |
| 5 | the 5 sham pairs | 2 | 1.0743 | **0.2876** |
| 5 | same-family control | 0 | 0.6446 | 1.0000 |
| 14 | the 5 sham pairs | 2 | 2.2764 | **0.7577** |
| 14 | same-family control | 0 | 1.3659 | 1.0000 |

**The exact p never clears 0.05 at any admission size** — at its most favourable (k=5) it is 0.2876.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** *(labelled DERIVED)* separations | 2 | **2**, error 0 |
| **B** null mean | 1.72 [1.0, 2.5] | **1.7247** |
| **C** exact P(sep ≥ 2) | 0.60 [0.25, 0.95] | **0.5727** |
| directional | observed ≤ null 95th pct (3) | **HOLDS** |

## what is downgraded, and what is not

- **Downgraded:** `STATEMENT.md`'s *"Kept for the residual it genuinely owns: the released core
  against its own sham"*. A clause with **no sham sensitivity at all** produces these two separations
  57% of the time.
- **NOT shown:** that the two separations are wrong. **They are real verdicts.** What is unsupported
  is that they are *evidence for* the clause.
- **Untestable here:** *why* they separate. "The prompt was withheld" is an interpretation of a
  verdict, and this release ships no counterfactual over the generator.

## impossible here

| criterion | what it would require |
|---|---|
| why the two pairs separate | a counterfactual over the generator |
| cross-release | one released core, and its sham is ours |
