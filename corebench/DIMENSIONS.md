# CoreBench — the scoring dimensions

**37 dimensions in 9 families.** Every core ever proposed gets all 37. A dimension that cannot be
computed on this release is `REGISTERED` with what it would require — never blank, never omitted,
never "planned".

**Why a matrix and not a metric.** R283 measured the fidelity band this task lives in: two annotators
of the same prompt agree on the exact class **8.0%** of the time, a global constant gets **4.0%**, and
the best available predictor reaches **15.0%**. A single fidelity number on that band is mostly noise.
A core is not one quantity; it is a trade among fidelity, sufficiency, non-degeneracy, stability,
cost, instrument-robustness, subgroup coverage, transfer and provenance.

**Every dimension carries a FLOOR and a CEILING**, so a raw value is never reported alone. Normalized
position is `(x − floor) / (ceiling − floor)`, and a dimension whose `floor == ceiling` on this release
is **degenerate** and is reported as such rather than scored — that is the `control that cannot pass`
failure applied to a metric.

---

## A · FIDELITY — does the core reproduce human judgement?

| # | dimension | floor | ceiling |
|---|---|---|---|
| A1 | exact weak-ordering match vs a held-out annotator | global constant, 0.0402 | modal-of-rest, 0.1500 |
| A2 | pairwise accuracy over the 6 response pairs | 0.5 | inter-annotator pairwise |
| A3 | top-1: is the best response identified | 0.25 | inter-annotator top-1 |
| A4 | bottom-1: is the worst response identified | 0.25 | inter-annotator bottom-1 |
| A5 | Kendall τ-b against the held-out human ranking | 0.0 | inter-annotator τ-b |
| A6 | agreement with the modal human class | global constant | 1.0 |
| A7 | `unacceptable`-set F1 | prevalence-matched random | inter-annotator F1 |

## B · SUFFICIENCY — does the core retain what `coval_full` has?

| # | dimension | floor | ceiling |
|---|---|---|---|
| B1 | retention: core fidelity ÷ full fidelity, same target | 0 | 1.0 |
| B2 | incremental value of the DISCARDED criteria — does adding them back help? | 0 = core is sufficient | full − core |
| B3 | mutual information between core class and full class | 0 | H(full class) |
| B4 | rank correlation of the core's score vector with full's | 0 | 1.0 |

## C · NON-DEGENERACY — is it doing anything at all?

| # | dimension | floor | ceiling |
|---|---|---|---|
| C1 | entropy of the classes the core emits across prompts | 0 = constant | H of human classes |
| C2 | margin above the global-constant baseline | 0 | ceiling − constant |
| C3 | share of prompts where core class ≠ the core's own modal class | 0 | 1.0 |
| C4 | normalized position between constant floor and best-available ceiling | 0 | 1.0 |

## D · STABILITY

| # | dimension | floor | ceiling |
|---|---|---|---|
| D1 | spread across held-out-annotator draws (≥3 seeds) | 0 = perfectly stable | — |
| D2 | prompt-bootstrap spread | 0 | — |
| D3 | rater-subsample spread | 0 | — |
| D4 | tie-tolerance sensitivity — how far the score moves as tolerance sweeps | 0 | — |

## E · COST / PARSIMONY

| # | dimension | floor | ceiling |
|---|---|---|---|
| E1 | `k`, the number of criteria | 1 | `n` |
| E2 | total tokens in the core | — | — |
| E3 | judge calls to evaluate one prompt = `k × m` | 4 | `n × m` |
| E4 | **fidelity gained per criterion** — A1 margin ÷ k | 0 | — |

## F · INSTRUMENT ROBUSTNESS

| # | dimension | floor | ceiling |
|---|---|---|---|
| F1 | **label-order gauge**: score change when response labels permute. **Must be 0** | 0 | 0 |
| F2 | batch/bf16 nondeterminism spread | 0 | — |
| F3 | judge-swap sensitivity | — | — |
| F4 | prompt-format sensitivity | — | — |

## G · SUBGROUP COVERAGE — 6 real demographic axes on 1,012 annotators

`age` · `ai_concern_level` · `country_of_residence` · `education_level` · `gender` ·
`generative_ai_usage`

⚠ The field is **`country_of_residence`**; a plain `country` key exists on no annotator and returns
`None` for all 1,012.

| # | dimension | floor | ceiling |
|---|---|---|---|
| G1 | **worst-subgroup fidelity** across all 6 axes | global constant | pooled fidelity |
| G2 | max−min fidelity spread across subgroups | 0 | — |
| G3 | fidelity on the high-disagreement prompts specifically | constant | — |
| G4 | share of subgroups where the core beats the constant | 0 | 1.0 |

## H · TRANSFER

| # | dimension | floor | ceiling |
|---|---|---|---|
| H1 | held-out-prompt fidelity | constant | in-sample fidelity |
| H2 | cross-block transfer, `world` ↔ `personal` | constant | within-block |

## I · PROVENANCE — is the core traceable to the rubric it compresses?

Measured because the incumbent turned out **not** to be a subset: exact overlap **8%**, ≥0.90
similarity **23%**, median best-match **0.676**. `FULL → CORE` is a **generation** task, and a
generated core can silently import content that was never in the rubric.

| # | dimension | floor | ceiling |
|---|---|---|---|
| I1 | share of core criteria with a `coval_full` counterpart at similarity ≥ 0.90 | 0 | 1.0 |
| I2 | verbatim overlap share | 0 | 1.0 |
| I3 | **novel-content share** — criteria with no counterpart above 0.60 | 0 | 1.0 |
| I4 | median best-match similarity | 0 | 1.0 |

---

## REGISTERED — cannot be computed on this release, with what each would require

| # | dimension | what it would require |
|---|---|---|
| F3 | judge-swap sensitivity | a second judge model held to the same prompt contract |
| F4 | prompt-format sensitivity | a second judge prompt template, pre-registered |
| H3 | cross-release transfer | a second values-annotation release with this schema |
| — | construct validity | an external gold standard for what a core *should* preserve |
| — | causal identification | intervening on how criteria are written, not observing them |
| — | temporal resolution | timestamps the release does not carry |

---

## The scoring contract

1. **The incumbent `coval_core` is scored first** and becomes row 0 of the leaderboard.
2. **Every later version is scored on all 37**, same seeds, same splits, same judge.
3. **No dimension may be dropped** because it is unflattering. A version that wins A1 and loses G1 is
   reported as exactly that.
4. **Floors and ceilings are recomputed per run** and printed beside every value, because a score
   without its band is the failure this whole project is a catalogue of.
