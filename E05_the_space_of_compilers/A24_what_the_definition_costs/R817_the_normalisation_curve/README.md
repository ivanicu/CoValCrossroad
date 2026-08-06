# R817 · removing the tie handicap changes nothing — six normalisations, one ordering

`run.py` · `PREREGISTRATION.txt` · `results/normalisation_curve.json` · 968 prompts × 9 arms ×
6 normalisations · **WORLD A** · two hash seeds byte-identical, md5
`697fe35c32d7719c0806df6cd56574cf`

## THE DECISION THIS MAKES SAFE

**R816 showed A2 penalises strict arms on tied human pairs. Removing that handicap — six defensible
ways — does not move a single arm.**

| normalisation | Spearman vs raw | margins flipping sign |
|---|---:|---:|
| raw | +1.0000 | 0 of 4 |
| ÷ att (shared annotators) | **+1.0000** | 0 of 4 |
| ÷ att (**split-half**, identified) | **+1.0000** | 0 of 4 |
| ÷ (1 − tie) | **+1.0000** | 0 of 4 |
| subtractive (A2 − att) | **+1.0000** | 0 of 4 |
| ÷ √att | **+1.0000** | 0 of 4 |

**Six normalisations, zero reorderings, zero sign flips.** And the shared-annotator and split-half
versions agree at Spearman **+1.0000** with each other.

## ⛔ CHECK #419 · THIS ARC HAD BEEN BURNED BY THIS EXACT OPERATION TWICE

1. **R793 swept three ceiling normalisations and got WORLD A / B / A** — the verdict flipped with
   the choice, and it flagged a "fraction of ceiling" of **1.0264** as proof the quantity was not a
   proportion. So a single normalisation was never going to be an answer; the estimand is the curve.
2. **R807's g=0 control caught a denominator estimated from the numerator's own data.** Measured
   here: `corr(A2, att)` is **+0.6138** with shared annotators and **+0.3798** with disjoint halves
   — **+0.2340 of the coupling is shared annotator noise**, which dividing would inject, not remove.
   That is why the split-half version is the identified one and the shared one is reported as the
   confounded contrast.

⭐ **And R793's pathology does not recur, for a reason worth stating**: R793 divided by a *pooled*
`CEIL_H` = 0.5519, **below** the arms' own scores, so ratios exceeded 1. Per-prompt `att` has mean
**0.686265** — above every arm — and **no normalisation produced a value above 1** (D3, checked).

## ⭐ THE VALUES

| arm | raw | ÷att shared | ÷att split-half | ÷(1−tie) | subtractive | ÷√att |
|---|---:|---:|---:|---:|---:|---:|
| `oracle_k4_fit1` | 0.6142 | 0.8896 | 0.8780 | 0.7116 | −0.0721 | 0.7373 |
| `greedy_k4_fit1` | 0.6106 | 0.8850 | 0.8730 | 0.7073 | −0.0756 | 0.7333 |
| `indep_k4_fit1` | 0.5941 | 0.8612 | 0.8481 | 0.6882 | −0.0922 | 0.7135 |
| `coval_core` | 0.5665 | 0.8226 | 0.8132 | 0.6566 | −0.1198 | 0.6809 |
| `topw_k4` | 0.5642 | 0.8200 | 0.8059 | 0.6542 | −0.1221 | 0.6785 |
| `genericpool16` | 0.5422 | 0.7895 | 0.7764 | 0.6291 | −0.1440 | 0.6526 |
| `full` | 0.5087 | 0.7416 | 0.7266 | 0.5899 | −0.1775 | 0.6126 |
| `random_k4_s0` | 0.4927 | 0.7196 | 0.7016 | 0.5714 | −0.1936 | 0.5939 |
| `gen_sham` | 0.4828 | 0.7082 | 0.6925 | 0.5599 | −0.2035 | 0.5832 |

⭐ **`coval_core` reads 0.8132 of its prompts' attainable maximum** on the identified normalisation —
a number the arc could not previously state, because R804's 0.686265 was a pooled ceiling and this
is per-prompt and split-half.

## ⛔⛔ THE SAME POSITIVE CONTROL WAS MIS-SPECIFIED THREE TIMES IN THIS ONE ROUND

- **① built from an arbitrary level.** "An arm proportional to `att`" was `att × 0.8`; whether it
  changes *rank* depends on the constant 0.8 I picked, not on whether normalising does anything.
- **② the g=0 check contradicted a derivation the round had already written.** "An arm independent
  of `att` must not move" — but a **constant** arm divided by a per-prompt divisor has
  `mean(c/att) > c/mean(att)` by **Jensen's inequality**, so it moves. D1 had already said a
  per-prompt divisor reorders after averaging *because the weights change*; the control asserted the
  opposite of the round's own derivation.
- **③ the direction was asserted, not derived.** Repaired to a dose ladder — add `c × (att − mean
  att)`, which leaves the raw mean **unchanged by construction** — I then asserted the normalised
  mean must *rise*. It falls. Two lines settle it:
  `mean((v + c·cen)/att) = mean(v/att) + c·mean(cen/att)` and
  `mean(cen/att) = 1 − mean(att)·mean(1/att) < 0` by Jensen.

> **derived slope −0.02183537 · observed −0.02183537 · |Δ| 1.46e-16**

**Three failures of one control, all of §4's dominant mode, and each fixed by deriving instead of
asserting.** The final form is worth more than the original would have been: it predicts its own
slope to machine precision.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | mean per-prompt attainable max **0.686265** vs R804's committed **0.686265**; `coval_core` **0.5664774812** vs committed | PASS, else exit 2 |
| PLACEBO | a **constant** divisor: Spearman vs raw **1.000000000000** | PASS — exactly unchanged |
| POSITIVE | dose ladder, raw mean fixed at **0.5664774812** at every c; normalised **0.822608 → 0.820424 → 0.816057**, matching the derived slope to **1.46e-16** | PASS **after three repairs** |
| g=0 | at c=0 the normalised value equals the un-doped arm exactly | PASS — the control can fail |
| NEGATIVE | `att` permuted across prompts, 200 draws: Spearman vs raw **+1.0000 [+1.0000, +1.0000]** | PASS — reverts to raw |
| NOISE FLOOR | 20 annotator half-splits of the split-half cell: sd **0.0046** | measured |
| D3 | normalisations producing a value above 1: **none** | the denominator is a ceiling |

⚠ **The negative control is weak here and I am not upgrading it.** Because *every* normalisation
leaves the ordering at Spearman 1.0000, permuting `att` also leaves it at 1.0000 — the control cannot
distinguish "the normalisation does nothing" from "the permutation destroyed it". Its pass is
uninformative, and the load-bearing control in this round is the positive one, which predicts its own
slope.

## WHAT DIED

- **the worry R816's NEXT raised** — that the tie handicap might be driving the arc's orderings.
  It is not: six normalisations, zero reorderings.
- **the fear that R793's flip would recur** — it does not, and the reason is measurable: R793's
  divisor sat below the arms, this one sits above them.
- **my own positive control, three times.**

## WHAT SURVIVES — AND THIS ROUND ADDS

Every ordering and every margin this arc has published, now robust to the removal of the tie
handicap. And a number in the arc's own terms: **`coval_core` achieves 0.8132 of what is attainable
on its prompts**, split-half, per-prompt, with no shared-noise inflation.

## SCOPE

968 prompts × 9 arms × 6 normalisations · per-prompt attainable max over the **75 weak orders** ·
split-half normalisation uses **disjoint annotator halves** for numerator and denominator · bootstrap
over prompts, NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a normalisation free of shared noise without splitting | more annotators per prompt; the split halves the panel and its cost is reported as sd **0.0046** — **checked**, not assumed |
| an informative negative control on this outcome | an ordering that some normalisation *does* change; every one leaves it at 1.0000, which is the finding and also what makes the control uninformative — **named rather than glossed** |
| the same curve on `personal` | 293 prompts carry both blocks; this round runs the full 968 on `world` — feasible, and simply not this round's estimand |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The instrument's scale is now settled from both ends and through six normalisations, so scale is no
longer where the uncertainty lives. Computed by this round's `run.py`, `coval_core` sits at **0.8132**
of attainable and `gen_sham` at **0.6925** — a spread of **0.1207** on the identified normalisation,
against a half-split sd of **0.0046**.

What has never been tested is the other side of that comparison: **`gen_sham` is the arc's floor arm,
and it reaches 69% of what any scoring function could achieve on these prompts.** A sham built from
criteria that never see the prompt should not be three-quarters of the way to the ceiling unless a
large part of A2 is available without any prompt-specific content at all. The step is to price that
directly — construct the best arm that uses **no** per-prompt information (a single fixed weak order
applied to every prompt, optimised over the 75) and put it on this normalised scale. If it lands near
`gen_sham`, the floor is a property of the metric; if it lands far below, `gen_sham` carries content
nobody has attributed.
