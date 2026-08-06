# R807 · the fitted arms are not copies of the leak — and my own g=0 control killed the estimand first

`run.py` · `PREREGISTRATION.txt` · `results/copy_of_the_leak.json` · 968 prompts × 5 arms + 3
synthetic · **WORLD C** — the pre-registered branch that kills the round · two hash seeds
byte-identical, md5 `16fb6d7abeef5fc9f3e8fca1572aa2ad`

## THE DECISION THIS MAKES SAFE

**On a scale where a pure copy of the leak scores 1.000 by derivation and honest arms sit at ~0.34,
the fitted arms sit at 0.50–0.65. No fitted arm's interval reaches 1.0.**

| arm | disattenuated slope on `_perfect_leak` | |
|---|---:|---|
| **pure copy of the leak** | **1.000** | a DERIVATION — the ceiling, not a measurement |
| planted half-honest/half-leak | 0.651 | ⭐ POSITIVE control, predicted 0.659 |
| `oracle_k4_fit1` | **0.650 [+0.558, +0.751]** | |
| `greedy_k4_fit1` | 0.611 [+0.520, +0.719] | |
| `indep_k4_fit1` | 0.504 [+0.407, +0.606] | |
| `coval_core` (honest) | 0.349 [+0.246, +0.454] | never saw a parity-1 label |
| `topw_k4` (honest) | 0.338 [+0.237, +0.457] | |

> **fitted − honest, disattenuated: +0.245 [+0.154, +0.333]**

## ⛔ BUT THE ROUND RETURNS WORLD C, AND I AM NOT OVERTURNING IT

My preregistration's **first** branch — the one I put first precisely because it kills the round —
reads *"if honest slope CI overlaps fitted slope CI → WORLD C"*. It does: `indep_k4_fit1`'s
**[0.407, 0.606]** overlaps `coval_core`'s **[0.246, 0.454]** between 0.407 and 0.454.

**CI overlap between two separately estimated quantities is not a test of their difference** — two
intervals can overlap while the paired difference excludes zero, which is exactly what happens here
(**+0.245 [+0.154, +0.333]**). So the branch that fired is the weaker test, and **it fired because I
wrote it that way.** The preregistration binds: **WORLD C stands, the paired difference is reported
beside it, and the defect is in the record so a later round uses the paired contrast instead.**

## ⛔⛔ AND THE ORIGINAL ESTIMAND WAS UNIDENTIFIED — THE g=0 CONTROL FOUND IT

R806's NEXT asked for the **residual**; R804 had already established an OLS residual mean is 0 by
construction, so I used the **intercept** — the arm's margin where the leak's margin is zero. The
g=0 control is the same predictor scored on two independent halves, **with nothing planted**. It
returned intercept **+0.0271**.

> **errors-in-variables**: noise in `x` attenuates the slope to λ and forces
> `intercept = (1 − λ)·mean(y)`.
> **Derivation check**: `(1 − 0.4774) × 0.0512 = +0.026772` vs observed **+0.027134**, |diff|
> **0.000362**.

**So "content = fitted intercept − honest intercept = +0.0213" was mostly the fitted arms having
larger mean margins** — R806's scale trap reappearing in a new coordinate, one round later. The
intercept is abandoned, not rescued: **λ is measured directly from the leak's own split-half
reliability and the estimand becomes the disattenuated slope**, on which a pure copy is exactly
1.000.

## ⭐ THE SHARED-DRAW FIX, MEASURED RATHER THAN ARGUED

R806's NEXT as posed scores leak and arm on the **same** parity-0 annotators, so their sampling
errors are correlated. Scoring the leak on half A and the arm on half B breaks it:

| arm | E1 slope (same draw) | E2 slope (split draw) | **inflation** |
|---|---:|---:|---:|
| `oracle_k4_fit1` | +0.5727 | +0.2970 | **+0.2757** |
| `greedy_k4_fit1` | +0.5361 | +0.2768 | +0.2593 |
| `indep_k4_fit1` | +0.4592 | +0.2359 | +0.2233 |
| `coval_core` | +0.2834 | +0.1506 | +0.1328 |
| `topw_k4` | +0.2901 | +0.1529 | +0.1372 |

**D4 held: every arm's same-draw slope exceeds its split-draw slope.** The shared annotator draw was
worth roughly **half** of the apparent association.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | ⚠ R806's slopes are binning-dependent, so the anchor is **binning-free**: pooled margins **+0.051224409** (`_perfect_leak`) and **+0.047060767** (`oracle_k4_fit1`) vs R806's committed values, exact | PASS, else exit 2 |
| PLACEBO | `_perfect_leak` regressed on **itself**: slope **1.000000000**, intercept **+0.000000000** | PASS — exact |
| POSITIVE (repaired estimand) | planted half-honest/half-leak arm lands at **0.651** against a predicted `0.5×(0.318 + 1.000) = 0.659`, |diff| **0.008** | PASS — the scale is calibrated at a point neither end determines |
| g=0 | the pure-leak copy on the **intercept**: **FAILS**, and that failure is the round's main finding | the estimand is abandoned, not rescued |
| NEGATIVE | **permutation null, 200 permutations**: slope null **+0.0031 [−0.0492, +0.0561]**, max **+0.0843**; the real slope **+0.5727** lies outside the entire null | PASS **after repair** |
| NOISE FLOOR | 20 independent half-splits: slope sd **0.0136 / 0.0121 / 0.0109 / 0.0098 / 0.0112** | measured |

⛔ **The negative control failed first for its own reasons.** It bootstrapped around **one** permuted
draw — which measures that permutation's precision, not the null — and reported +0.0843 [+0.0308,
+0.1346] as a failure for a pairing that had in fact been destroyed. A permutation null is a
distribution **over permutations**; with 200 of them the observed +0.0843 turns out to be the null's
own **maximum**.

## MULTIPLICITY

5 arms × {same-draw, split-draw} × {slope, intercept}, all reported. BH q = 0.05 over the intercept
family: **5 of 5 survive** — and that family is reported **only** to show that surviving BH is
worthless when the estimand itself is unidentified, which is the round's point.

## WHAT DIED

- **the intercept as a measure of content** — unidentified, killed by this round's own g=0 control,
  with the errors-in-variables arithmetic matching to 0.000362.
- **R806's NEXT as posed** — the same-draw regression inflates every slope by ~0.13–0.28.
- **my negative control**, and **my kill's first branch**, both for their own reasons.

## WHAT SURVIVES — AND THIS ROUND ADDS

A **calibrated scale for "how much of an arm is the leak"**: honest floor ~0.34, pure copy 1.000 by
derivation, with a planted arm landing within 0.008 of its predicted midpoint. On it the fitted arms
read **0.50–0.65**, and no interval reaches 1.0 — so **the fitted route is neither a copy of the leak
nor free of it**, which is the first quantitative statement this arc has about *how much*.

## SCOPE

968 prompts (**0 dropped**; all carry a parity-0 half-split) × 5 named arms + 3 synthetic
(`_perfect_leak`, `_leakcopy`, `_planted`) · outcome = arm − `POOL[0:4]`, R806's estimand · leak on
parity-0 half A, arm on half B, one fixed split for the intervals and 20 splits for the split-noise
sd · λ estimated on the same split · bootstrap over prompts, 1,200 draws · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a leak proxy that is not itself noisy | more annotators per prompt; λ = 0.4597 is what the release supports, and disattenuating by it is the whole repair — **checked** against the median of 16 |
| separating "content" from "a smoother estimator of the same target" | an external gold standard for the prompt's true ordering — `corebench/score.py:34`'s open register |
| the same test on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances — **checked** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The scale exists and the fitted arms read 0.50–0.65 on it, against an honest floor of 0.34 and a
pure-copy ceiling of 1.000. Computed by this round's `run.py`, the paired gap is **+0.245 [+0.154,
+0.333]** while the pre-registered branch fired on CI overlap instead. Two things follow, and the
second is the step. First, the contrast should be re-run as a **paired** test, which this round
reports but did not gate on. Second and larger: **λ = 0.4597 means the leak proxy is itself less than
half reliable**, so each of the five disattenuated numbers above is divided by a quantity this round
estimated from a median of 8 parity-1 annotators per prompt. The step is to measure how the whole scale moves as λ improves — recompute it at 2, 3, 4
and 8 parity-1 annotators and see whether the fitted arms' 0.50–0.65 is stable or drifts toward the
ceiling as the leak proxy sharpens. If it drifts, the fitted arms are copies of a *better* leak than
this release can measure, and the ceiling is the artifact.
