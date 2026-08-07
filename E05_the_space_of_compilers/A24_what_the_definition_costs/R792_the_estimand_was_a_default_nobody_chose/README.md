# R792 · the arc's estimand was a default nobody chose — and exactly one of four cells separates

`run.py` · `PREREGISTRATION.txt` · `results/estimand.json` · 18,384 judgements × 1,012 annotators ×
36 subgroups · **WORLD C** · two hash seeds byte-identical, md5 `04d29cc0d2c9e974d7349cc06d01a528`

## THE DECISION THIS MAKES SAFE

**`coval_core` − `topw_k4` separates in exactly 1 of 4 estimand cells, and it is the corner a prior
round happened to run.**

| weighting | resampling unit | eff | 95% CI | p | |
|---|---|---:|---|---:|---|
| pooled | prompt *(the arc's silent default)* | +0.002297 | [−0.002203, +0.007005] | 0.2917 | not separable |
| pooled | annotator | +0.002297 | [−0.000163, +0.004650] | 0.0683 | not separable |
| subgroup | prompt | +0.004107 | [−0.002590, +0.010857] | 0.2267 | not separable |
| **subgroup** | **annotator** | **+0.004107** | **[+0.000424, +0.007765]** | **0.0300** | **SEPARABLE** |

**Neither factor alone flips it.** The prior round's `SEPARABLE` rests on a **conjunction** of a
re-weighting *and* a change of resampling unit, and it was reported as one result.

## ⛔ CHECK #394 FOUND TWO ERRORS BEFORE ANY DESIGN

**① A wall cited four times whose citation points at a different round.** R791's NEXT sent the arc to
"the construct question R631 registered as impossible here." **R631 is `the_unrecorded_retraction`** —
about clause ③'s testability bound living in an ungated document. The register actually lives at
**`corebench/score.py:34`**. R787, R789, R790 and R791 all carry the false citation; **all four
READMEs are corrected in this commit**, because a correction that does not reach the artifact that
provoked it is not a correction.

**② The pair had already been separated, and the artifact sat unopened.**
`corebench/results/subgroup_coval_core_vs_topw_k4.json` — 328 bytes, on disk since 2026-08-03 —
reads `verdict: SEPARABLE`. Its round (commit `42362e0b`) states plainly: *"on a subgroup-weighted,
annotator-resampled estimand the hand-built core is separably ahead… On a prompt-weighted,
prompt-resampled estimand they tie."* **So R789/R790/R791's "not separable" was true only of the
prompt-weighted estimand and none of them said so.** ⭐ And that round's own NEXT — *"every A-family
comparison today was prompt-weighted by default, and nobody chose that"* — was never acted on.

## ⭐ AND A THIRD DEFAULT NOBODY CHOSE, FOUND BY THE CODE FAILING

The judgement table spans **1,078 prompts**; the arms share **968**; the prior round used whatever
each arm had. So the two rounds differ on **population** as well as weighting and resampling. Both
populations are carried here: the reproduction uses each arm's own availability, the grid uses the
common set.

## THE DEFINITION-LEVEL ANSWER: IT CHANGES NOTHING

| cell | pairs resolved of 190 | admits |
|---|---:|---:|
| pooled / prompt | 166 | **14** |
| pooled / annotator | 180 | **14** |
| subgroup / prompt | 161 | **14** |
| subgroup / annotator | 177 | **14** |

**The four clause-② admitted sets are IDENTICAL.** 11 of 190 pair verdicts flip between the arc's
default and the prior round's cell, and **`corr(pooled eff, subgroup eff) = 0.9993`** across the 190
pairs — D4's threshold for a reparameterisation. **The estimand choice moves individual verdicts and
does not move the definition.**

## ⚠ AND THE SHAM WEAKENS THE "UNANIMOUS ACROSS SIX AXES" READING

Random groups of the same 36 sizes give a decisive difference of **+0.002586 [+0.001073, +0.005076]**
against the real subgroup-weighted **+0.004107**. So **most of the uplift over the pooled +0.002297 is
produced by re-grouping at all**, not by *these* groups, and the sham's range contains values close
to the real one. The real structure adds roughly **+0.0015** over random grouping, against a sham sd
of **0.000974**.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | **the committed artifact REPRODUCED**: 36 subgroups vs 36 · mean 0.004107 vs 0.004107 · win_rate 0.833333 vs 0.833333 | PASS, else exit 2 |
| PLACEBO | 9 alias pairs, worst per-judgement difference **exactly 0.0** | PASS — expected value fixed by D3 |
| POSITIVE | δ=0 → **0 of 4** cells separate (the floor fails, as required) · δ=0.002 → **4 of 4** | PASS, band admissible |
| POSITIVE (subgroup-specific) | ratio (subgroup move)/(pooled move) by planted group size: `country_of_residence=Switzerland` n=155 → **3.870** · `generative_ai_usage=A few times a month` n=2,125 → **1.053** · `gender=Male` n=9,535 → **0.948** | PASS — **monotone**, as D2 requires |
| NEGATIVE | demographics permuted across annotators: pooled estimate unchanged to **0.0e+00** (a derivation, checked); the subgroup-weighted decisive difference moves **0.000581** | PASS |
| SHAM | random groups of the same 36 sizes | ⚠ see above |
| NOISE FLOOR | sd of the sham over 20 random assignments: **0.000974** | measured |

### ⛔ MY SUBGROUP CONTROL FAILED FOR ITS OWN REASONS, AND MY OWN D2 SAID WHY

The first version planted on the **largest** subgroup and returned subgroup **0.024743** < pooled
**0.026102** → FAIL. But **D2, written before the run, says the 36 subgroups are six *overlapping*
partitions of one judgement set** — so a plant on a large group of one axis contaminates every other
axis's groups in proportion, and the two estimators *must* agree by construction. A criterion
presuming disjoint groups is malformed here. Repaired to a **dose over group size**, whose
expectation is derivable without the result: pooled weights a group by its size and subgroup-
weighting does not, so the ratio must **fall** as the planted group grows. It does: 3.870 → 1.053 →
0.948.

## MULTIPLICITY

190 pairs × 4 cells = **760 verdicts**, BH at q=0.05 over the whole 190 within each cell. Resolved
166 / 180 / 161 / 177; non-survivors 24 / 10 / 29 / 13. The decisive pair's verdict is reported
inside that correction, not on its own — the registered confound was that 36 subgroups is a
multiplicity surface and the prior round tested one pair.

## WHAT DIED

- **"`coval_core` is not separable from `topw_k4`", unscoped** — true of the prompt-weighted
  estimand only. R789, R790 and R791 all state it without the scope; corrected here.
- **"the construct-validity wall (R631)"** — four rounds, one false citation, all corrected at the
  artifact.
- **the prior round's `SEPARABLE` as a standalone result** — it is one corner of four, and neither
  factor alone reaches it.
- **my own subgroup-specific control**, mis-specified against my own D2.

## WHAT SURVIVES

The prior round's numbers, reproduced exactly by different code on a different day (36 / 0.004107 /
0.833333) — which is the strongest object check this arc has available. Its honest framing survives
too, and this round sharpens it: *"the hand-built core is more evenly good across groups than it is
better on average"* — now with the qualifier that random regrouping reproduces most of the gap.

## SCOPE

population 20 distinct objects · 18,384 judgements · 1,078 prompts in the table, **968** shared by
all arms · 1,012 annotators · 36 subgroups at n ≥ 100 across 6 demographic axes · NBOOT 1,200 ·
3 seeds · first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| which estimand is CORRECT | a stated purpose for the benchmark — it is a choice about whose average matters, not a measurement |
| construct validity | an external gold standard for what a core should preserve — `corebench/score.py:34`, **not R631** |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

The arc has now attacked clause ②'s threshold, its dimensionality and its estimand, and the answer is
stable: **the definition's admitted set does not move.** Computed by this round's `run.py`, all four
estimand cells admit the same 14 named arms and the two weightings correlate 0.9993. What moved
instead is the confidence attached to one pair, and this round found that by opening an artifact
nobody had read. So the next step is not another statistic and not another estimand — it is to
enumerate, by listing `corebench/results/` against the file paths this arc's `run.py` files actually
open, which artifacts have been read and which have not. This round's own E4 is the argument for it:
its cheapest correction came from a 328-byte file that had been sitting there for three days.
