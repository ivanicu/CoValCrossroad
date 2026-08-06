# R816 · the shift is the tie rate, not the reliability — and my last round's NEXT named the wrong mechanism

`run.py` · `PREREGISTRATION.txt` · `results/shift_decomposition.json` · 293 prompts × 9 arms ×
3 models · **WORLD B** · two hash seeds byte-identical, md5 `da87b78f400dbbe37cfff9fe6566deb6`

## THE DECISION THIS MAKES SAFE

**R815's NEXT proposed one explanation for the uniform +0.005–0.012 shift toward `personal`: that
the target is simply more reliable. It is not the explanation.**

| | mean over 9 arms | arms with a resolved CI |
|---|---:|---|
| **ceiling** slope (test: is it **1**?) | **+0.313** | CI contains 1 in **0 of 9** |
| **tie-rate** slope (test: is it **0**?) | **−0.476** | CI excludes 0 in **9 of 9** |

**The reliability account as posed is refuted**: if the shift *were* the reliability shift, the
ceiling slope would be 1. It is 0.313, and no arm's interval reaches 1.

⚠ **That does not make the ceiling term zero** — every arm's ceiling slope is resolvedly positive
(+0.123 to +0.441). **Both mechanisms are live**; what died is the claim that reliability *accounts
for* the shift.

## ⛔ CHECK #418 · THE INFERENCE R815 PROPOSED WAS NEARLY FORCED, AND A RIVAL WAS UNNAMED

1. **Higher inter-annotator agreement raises A2 for any predictor**, so "does the ceiling point the
   same way" is not evidence. Only the *magnitude* is — which is why this round tests **slope = 1**,
   not slope > 0.
2. ⭐ **[DERIVATION] a strict-signed arm can never match a tied human pair**, so its attainable A2 is
   bounded by `1 − tie_rate`. Measured: tie rate **world 0.145080 · personal 0.124460**, a drop of
   **0.020620** — which makes **more than the whole observed shift** available on its own.
3. The obvious third rival is out **by measurement**: annotators per prompt is **median 12 in both**
   blocks, so the shift is not panel depth.

## ⭐ THE PER-ARM TABLE

| arm | shift | ceiling slope | tie slope |
|---|---:|---|---|
| `coval_core` | +0.0119 | +0.368 [+0.270, +0.457] | **−0.553 [−0.699, −0.415]** |
| `oracle_k4_fit1` | +0.0059 | +0.441 [+0.346, +0.539] | −0.431 [−0.604, −0.238] |
| `greedy_k4_fit1` | +0.0054 | +0.419 [+0.325, +0.519] | −0.435 [−0.602, −0.243] |
| `indep_k4_fit1` | +0.0108 | +0.399 [+0.301, +0.504] | −0.453 [−0.619, −0.281] |
| `topw_k4` | +0.0092 | +0.354 [+0.252, +0.444] | −0.498 [−0.633, −0.348] |
| `genericpool16` | +0.0094 | +0.327 [+0.226, +0.433] | −0.492 [−0.664, −0.289] |
| `random_k4_s0` | +0.0098 | +0.200 [+0.063, +0.338] | −0.426 [−0.613, −0.232] |
| `full` | +0.0099 | +0.188 [+0.062, +0.315] | −0.450 [−0.630, −0.256] |
| `gen_sham` | +0.0105 | **+0.123 [+0.014, +0.238]** | −0.550 [−0.721, −0.369] |

**The joint model is admissible** — `corr(ceiling shift, tie shift) = −0.4314`, below the
pre-registered 0.7 above which coefficients stop being separately interpretable. Jointly:
`coval_core` ceiling **+0.269 [+0.162, +0.351]** / tie **−0.367 [−0.493, −0.244]**; `gen_sham`
ceiling **−0.031 [−0.158, +0.089]** / tie **−0.572 [−0.744, −0.379]**. ⭐ **On the weakest arm the
ceiling term vanishes entirely and only the tie term survives.**

## D3 · THE ORDERING PREDICTION, AND WHY IT IS A WEAK TEST

D3 predicted stricter arms should be more tie-sensitive. Measured `corr(strictness, |tie slope|) =
+0.4899` — the right sign. ⚠ **But strictness ranges only 0.994–1.000 across the nine arms**, so the
regressor is nearly degenerate and this is a weak test on a variable with almost no spread. Reported
as directional, not as support.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R815's per-arm shifts reproduced exactly: `coval_core` **−0.011944**, `gen_sham` **−0.010529**, both \|Δ\| **0.00e+00** | PASS, else exit 2 |
| PLACEBO | an arm against itself: **0.0e+00** | PASS — identically 0 |
| POSITIVE | planted `c × (ceiling difference)`, c = 0 / 0.5 / 1.0 / 2.0 → recovered increments **+0.000 / +0.500 / +1.000 / +2.000** | PASS — tracks c exactly |
| c=0 | recovers the unplanted slope to 1e-9 | PASS — the control can fail |
| NEGATIVE | regressor-to-outcome pairing destroyed, 200 draws: ceiling null **+0.004 [−0.091, +0.086]** max +0.151 vs real **+0.368**; tie null **−0.004 [−0.141, +0.156]** min −0.196 vs real **−0.553** | PASS **after repair** |
| NOISE FLOOR | 20 half-splits: ceiling slope sd **0.044** | measured |

⛔ **The first negative control destroyed nothing, and overshot the observation.** It permuted only
the **`personal` side** of the outcome, so `y` still carried the un-permuted `world` A2 and `dT` still
carried the un-permuted `world` tie rate — and those are coupled, because an arm scores lower where
humans tie more. The null came back at **−0.870** on the tie slope, *more negative than the real
−0.553*. **A null that overshoots the observation has not removed structure, it has added some.**

⚠ **And one pre-registered family is FORCED, not measured**: BH over the per-arm residual means
returns 0 of 9 surviving because **an OLS residual has mean 0 by construction** (R804's lesson). It
is printed because it was pre-registered and **labelled** because reporting it as a finding would be
the arithmetic trap.

## WHAT DIED

- **R815's NEXT as posed** — the shift is not the reliability shift; the ceiling slope is 0.313 and
  no arm's CI reaches 1.
- **"one mechanism explains it"** — both terms are resolved on eight of nine arms.
- **my own negative control**, which overshot rather than nulled.

## WHAT SURVIVES — AND THIS ROUND ADDS

R815's finding is untouched: the ordering is target-invariant at Spearman 1.0000. What this adds is
*why* the levels move — **principally because `personal` has 0.0206 fewer tied pairs, and a
strict-signed arm cannot score on a tie at all.** That is a property of the question put to humans,
not of any core.

## SCOPE

293 prompts carrying both blocks with ≥2 annotators each × 9 arms × 3 models (ceiling-only,
tie-only, joint) · per-prompt within-pair differences across two blocks about the **same** four
responses · paired bootstrap over prompts, NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| separately interpretable joint coefficients at high collinearity | uncorrelated regressors; measured at **−0.4314**, below the pre-registered 0.7, so the joint model is reported — the rule was written to refuse it, not to license it |
| a strictness test with real spread | arms that tie meaningfully often; the nine span **0.994–1.000** — **checked**, and D3 is reported as weak rather than upgraded |
| a third target | `unacceptable` records ratings, not rankings — **checked** in R815 against the raw record |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The shift is explained: **tie rate primarily, reliability secondarily**, with the joint model showing
the ceiling term falling to **−0.031 [−0.158, +0.089]** on `gen_sham` while its tie term holds at
**−0.572**. Computed by this round's `run.py`, that is a mechanism about the *question* put to
humans, not about any core.

Which raises the thing this arc has never asked about its own instrument. A2 scores a strict-signed
arm against human vectors that are tied **12.4–14.5%** of the time, and on those pairs the arm cannot
score **by construction** — so A2's attainable maximum is not 1 but `1 − tie_rate`, a bound that
differs between targets and between prompts. R804 measured the attainable ceiling over weak orders at
**0.686265**; the tie bound is a different quantity and no round has separated the two. The step is
to re-express each committed A2 as a fraction of **its own prompt's** attainable maximum, then check
whether this arc's orderings survive a per-prompt normalisation that removes the tie handicap.
