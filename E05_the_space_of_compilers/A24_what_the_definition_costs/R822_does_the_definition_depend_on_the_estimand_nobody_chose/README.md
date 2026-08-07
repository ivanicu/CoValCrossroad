# R822 · Does the definition's verdict depend on the estimand nobody chose?

**E05 · A24 · R822.** Frontier. **WORLD B.** 968 prompts · 1,012 annotators · 15,593 judgements ·
33 demographic subgroups · 58 arms · 6 estimand cells.
Two seeds byte-identical: `735e2a3222f7739bb0aae8a76383de00`. Source `54bab0e3`.

## The decision this makes safe

R821 retained clause ④ on the strength of a plant test, and *derived* that ④'s statistic is a
difference of **corpus means**. **That aggregation was never chosen.** R792 found the identical
defect in the arc's A-family comparisons — *"every A-family comparison today was prompt-weighted by
default, and nobody chose that"* — and showed a decisive pair separates in **1 of 4** cells. Nobody
had ever run that grid on a **clause verdict**. So the definition I shipped yesterday might have
been resting on a default.

Grid: weighting {prompt, annotator, subgroup} × resampling {prompt, annotator}. Weighting fixes the
estimand; resampling fixes its SE.

## Result

| clause | over the 6 cells | verdict |
|---|---|---|
| **④** better than every criterion-free rule | **0 of 58 in all six** | **invariant** |
| **③** no prompt labels | **23 of 58 in all six** | **invariant — as D3 requires** |
| **②** better than a prompt-blind set | **29 / 30 / 31** | **moves** |

**②'s boundary is estimand-dependent, and it moves at exactly two arms of 58.**

| arm | prompt-wt | annotator-wt | subgroup-wt | inside the noise floor (0.0057)? |
|---|---:|---:|---:|---|
| **`gen`** | −0.0071 | −0.0049 | −0.0077 | **No** |
| `topw_k12` | −0.0042 | −0.0000 | +0.0010 | Yes — sign unresolved |

⭐ **`gen` is not an incidental arm. It is the arm the definition's own open question rests on.**
`DEFINITION.md:524` states *"Settling ②∧③ needs a better ③-admissible arm than `gen` (p32.6),"* and
`gen` is named in **55** round READMEs as the third-source object. Its ② margin moves **57%** across
weightings (−0.0049 → −0.0077) — a swing larger than the design's own noise floor — and that swing
straddles the exclusion threshold. **So the ②∧③ question four rounds cited as open for lack of
power is also open for lack of a named estimand**, which no amount of additional data fixes.

## Controls

| control | returned |
|---|---|
| **OBJECT** | the judgement-level rebuild reproduces R821's per-prompt route to **1.11e-16**, and the floor to 0.455679 vs the committed 0.4557. This validates the annotator-id reconstruction, which `score.py` does not expose. |
| **PLACEBO** | every arm against itself, every weighting: **exactly 0.0** |
| **POSITIVE** | the δ=0.10 plant removed in all 3 weightings, **and** the δ=0 plant removed in none — the control can fail |
| **NEGATIVE** | synthetic arm resampled from the floor's own distribution, per weighting: **+0.00048 ± 0.00539** / **+0.00056 ± 0.00532** / **−0.00042 ± 0.00592**, against real margins **+0.08188** / **+0.08471** / **+0.08123**. On zero, and the real margin outside the null's whole range, in all three. |
| **SHAM** | subgroup weighting with **random groups of matched size**: corr with the real subgroups **0.99988**, with prompt-weighting **0.99938** |
| **NOISE FLOOR** | 20 half-splits per weighting: **0.00515 / 0.00556 / 0.00569** |
| **BH** | 348 tests over the whole grid: **343 survive, 5 do not** (printed, not hidden) |

⭐ **The sham is a finding.** Random groups of matched size reproduce the real demographic subgroups
at **corr 0.99988**. The ingredient in "subgroup weighting" is **not which groups** — it is that
grouping happens at all, and even that is a near-reparameterisation of prompt weighting (0.99938).
**The subgroup column of this grid is nearly free**, and any future round proposing a
demographically-weighted estimand should be shown this number first.

## Derivations, run before any compute

- **D1** Resampling cannot move a point estimate, only its CI. **6 cells carry 3 distinct
  quantities.** Any verdict change at fixed weighting is precision, never estimand.
- **D2** Under any weighting, ④'s margin is `mean_w(arm − floor)` — a reweighting of the same
  per-prompt differences. Measured: max |Δmargin| **0.0086 / 0.0053 / 0.0076**, pairwise
  corr **≥ 0.99904**. Distinct, not a reparameterisation, so the grid is not WORLD C.
- **D3** ⭐ **③ reads the arm's source, not its score, so it cannot move.** It did not (23 of 58 in
  every cell). This is a **free falsifier on the grid instrument itself** — had ③ moved, the
  instrument would have been broken and E1 inadmissible.

## What this round got wrong

- **The kill did not implement this round's own preregistration.** It branched to WORLD B on
  `not c2_same` alone, without separating *"differs across weightings"* from *"differs only across
  resampling"* — a distinction the preregistration states explicitly and D1 makes load-bearing.
  Conflating them reports a **precision** effect as an **estimand** effect. §4's *"the verdict string
  is not a computation"*, in the kill itself. The corrected branch also demands that at least one
  flipping arm lie **outside** the noise floor; `gen` does, so WORLD B survives on evidence.
- **`agg` closed over the full-length index arrays**, so every resampled call raised — and had it
  not raised, pooling by original prompt id would have silently collapsed a twice-drawn prompt back
  to weight one, quietly destroying the bootstrap. Callers now pass draw-indexed labels.
- **The subgroup cell's negative control was computed under *prompt* weighting** while compared to a
  subgroup-weighted real margin — R818's mixed-weighting defect, inside the control built to guard
  this very grid.

## What this round cannot do

| criterion | requires |
|---|---|
| independently replicated | a second release |
| cross-dataset / cross-model | a second site |
| construct validated | an external gold standard for "core" |
| temporally resolved | judgement timestamps the release does not carry |
| more weightings | the release exposes 33 subgroups at n≥200; a finer axis needs a larger annotator pool |
