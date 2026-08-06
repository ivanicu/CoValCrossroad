# R806 · the relative test is blind, so the leak verdict stands — and R805's WORLD A must narrow

`run.py` · `PREREGISTRATION.txt` · `results/scale_artifact.json` · 968 prompts × 7 arms × 2 binning
variables · **WORLD A** · two hash seeds byte-identical, md5 `8c6ad6838e23c5682eb5b4be9e886e41`

## THE DECISION THIS MAKES SAFE

**R805 and R295 were both in the record and they contradicted each other. R295 is right, and R805's
headline has to be narrowed to the prompts where the annotators agree.**

| | |
|---|---|
| R805 committed | *"fitting a core to a prompt's own humans has real content"* — **+0.0553 [+0.0456, +0.0653]** pooled |
| R295 committed | the fitted margin is **−0.0054** in the quintile where the two annotator halves disagree |

Both were headlines. R805 cited R295 for a lower-bound caveat and **never reconciled them** — the
tension was mine to create and mine to resolve.

## ⭐ THE INSTRUMENT FINDING, WHICH IS WORTH MORE THAN THE VERDICT

I attacked R295 on a real weakness: it subtracts the honest arm's slope **additively**, while the
confound — *prompts where annotators agree are prompts where any predictor scores better* — is
plausibly **multiplicative**. The test is each arm's quintile margin divided by **its own** pooled
margin.

| arm | pooled | Q1 | Q2 | Q3 | Q4 | Q5 | relative slope |
|---|---:|---:|---:|---:|---:|---:|---|
| `oracle_k4_fit1` | +0.0471 | −0.11 | 0.43 | 1.35 | 1.60 | 1.73 | +0.7165 [+0.5553, +0.8889] |
| `greedy_k4_fit1` | +0.0461 | 0.02 | 0.42 | 1.39 | 1.52 | 1.65 | +0.6433 [+0.4809, +0.8124] |
| `indep_k4_fit1` | +0.0343 | −0.05 | 0.31 | 1.31 | 1.67 | 1.76 | +0.7345 [+0.4987, +0.9807] |
| `coval_core` (honest) | +0.0154 | 0.53 | 0.16 | 0.51 | 1.71 | 2.09 | +0.5541 [+0.0720, +1.0861] |
| `topw_k4` (honest) | +0.0133 | 0.49 | −0.06 | 1.41 | 1.79 | 1.36 | +0.3438 [−0.2484, +0.9585] |
| **`_perfect_leak`** | +0.0512 | −0.24 | 0.31 | 1.23 | 1.63 | 2.07 | **+0.9076 [+0.6784, +1.1362]** |

> **fitted − honest: +0.2491 [−0.1838, +0.6804] — the CI holds 0.**

**And that is NOT an acquittal, because the same statistic cannot separate a PERFECT LEAK either.**

> ⭐ **relative-scale positive control** — `_perfect_leak` (parity-1's own modal class used as the
> predictor) **minus honest: +0.4499 [−0.0447, +0.9647]. Holds 0.**

**A statistic that cannot distinguish a maximal leak from an arm that never saw a human label has no
power to exonerate anything.** E2 returns **UNVERIFIED**, never OVERTURNED. ⛔ **My first kill branch
read that same CI as WORLD B** — because the gate validated `perfect_leak is steepest` on the
**absolute** slope while the branch fired on the **relative** one. That is realstat §4's *"the
control targets a different statistic than the one being reported"*, verbatim, in the round written
to catch exactly this class.

## ⛔ AND I VIOLATED MY OWN IDENTIFICATION CLAUSE IN THE SAME ESTIMAND

The preregistration says E2 needs a denominator far from zero and **names** `coval_core` and
`topw_k4` for that reason. The first run put **`generic`** in the honest set — and `generic` *is*
`POOL[0:4]`, so its margin against the k=4 pool is **+0.0011**. Its relative profile is a ratio to
zero (1.78, −0.62, **3.07**, 0.94, −0.16; slope −0.2969 [−1.5903, +0.9204]) and it dominated the
honest mean, moving the headline from **+0.4977** to **+0.2491**. Excluding it is applying the
pre-registered clause, not moving the goalpost — and it is reported in the table rather than deleted.

## ⭐ E3 · SO E3 DECIDES — AN INDEPENDENT BINNING VARIABLE

R295's binning variable is agreement between parity-1 and parity-0, while its outcome is scored on
parity-0 — a shared term R295 named in its own docstring and left. Re-binned on agreement **within
parity-1 only**, which never touches the outcome:

| arm | Q1 | Q2 | Q3 | Q4 | Q5 | slope |
|---|---:|---:|---:|---:|---:|---|
| `oracle_k4_fit1` | **−0.0122** | +0.0358 | +0.0625 | +0.0728 | +0.0761 | **+0.0302 [+0.0217, +0.0392]** |
| `greedy_k4_fit1` | −0.0066 | +0.0370 | +0.0622 | +0.0695 | +0.0685 | +0.0251 [+0.0165, +0.0344] |
| `indep_k4_fit1` | −0.0143 | +0.0286 | +0.0483 | +0.0569 | +0.0520 | +0.0213 [+0.0124, +0.0309] |
| `coval_core` | −0.0030 | +0.0099 | +0.0194 | +0.0223 | +0.0284 | +0.0084 **[−0.0001, +0.0164]** |
| `topw_k4` | −0.0018 | +0.0099 | +0.0183 | +0.0208 | +0.0195 | +0.0049 **[−0.0029, +0.0127]** |
| `_perfect_leak` | −0.0099 | +0.0342 | +0.0556 | +0.0839 | +0.0919 | +0.0350 [+0.0231, +0.0475] |

**All three fitted slopes are resolved; both honest slopes hold zero.** Fitted mean **+0.0256**,
honest **+0.0067**, excess **+0.0189**. **BH q = 0.05 over 6 slopes: 4 survive, 2 do not** — the two
non-survivors are the honest arms, and naming them is the finding, not an omission.

⚠ **D3, registered before the run**: `corr(within-parity-1, R295's half-agreement) = +0.7790`. These
two variables are **correlated**, so E3 is a **weaker instrument**, not an independent replication.
It removes some of the shared term, not all of it.

## ⭐ E4 · THE RECONCILIATION

> bottom quintile, where annotators disagree most: **fitted −0.0110 · honest −0.0024**

The fitted arms go **negative** exactly where the parity-1 labels stop predicting parity-0; the
honest arms sit at zero. Across the independent binning the fitted margin runs **−0.0143 → +0.0761**.

**So R805's +0.0553 is real and is not a property of the fitted arms in general — it is a property of
high-agreement prompts.** R295's W-LEAK stands.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R295 reproduced on its own population: N **968**, half-agreement **0.552048**, `oracle_k4_fit1` slope **0.033719**, floor **0.008548**, and its full quintile vector | PASS, else exit 2 |
| PLACEBO | the k=4 pool against **itself**, all five quintiles: **0.0e+00** | PASS — exactly zero |
| POSITIVE (absolute) | synthetic perfect leak, slope **+0.046491 [+0.034749, +0.058202]**, steepest of all 7 arms (next +0.033719) | PASS |
| ⭐ POSITIVE (**relative**) | perfect leak − honest on the relative scale: **+0.4499 [−0.0447, +0.9647]** | **FAILS — and that failure is the finding** |
| NEGATIVE | binning variable permuted across prompts: −0.0021 [−0.0122, +0.0059] · −0.0013 [−0.0118, +0.0068] · −0.0015 [−0.0109, +0.0057] | PASS — all hold 0 |
| POPULATION | 968 prompts carry the independent variable, **0 dropped** | printed, never silent |

## WHAT DIED

- **R805's NEXT** — R295 had already run the stratification and committed `killed = True`.
- **R805's WORLD A as stated** — narrowed: fitting has content **where the annotators agree**, and
  none where they do not.
- **my own attack on R295** — the multiplicative test is blind, and its own positive control says so.
- **World B and World C.**

## WHAT SURVIVES — AND THIS ROUND ADDS

R295's W-LEAK, now under a binning variable that does not contain the outcome, with the honest arms
as a floor that holds zero. And an **instrument fact that forecloses a class of future attacks**: the
relative-profile statistic cannot distinguish a perfect leak from an honest arm on this data, so no
future round should read a null from it as an exoneration.

## SCOPE

968 prompts × 4 responses · annotators split by index parity · 7 arms (3 fitted-held-out, 1 leaky,
2 honest, 1 synthetic perfect leak) + 1 degenerate reported separately · outcome = arm − `POOL[0:4]`
on parity-0, R295's estimand exactly · two binning variables · bootstrap over prompts, NBOOT 1,200 ·
first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a binning variable fully independent of annotator consensus | a per-prompt difficulty measure not derived from the labels; every candidate on disk is a function of them — **checked**, and D3's +0.7790 is reported instead of assumed away |
| a PROMPT-held-out fitted arm | selecting this prompt's criteria from other prompts' labels; each prompt has its own rubric and only a rule transfers — `topw_k4` **is** that rule-transfer arm and sits here as an honest comparison |
| the same test on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances — **checked** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The fitted route's margin is now located — computed by this round's `run.py`, it is **−0.0110** in
the bottom agreement quintile and **+0.0655** in the top, while neither honest arm has a resolved
slope. The fitted excess over the honest floor under the independent binning is **+0.0189**, against
a perfect-leak ceiling of **+0.0350** — so the fitted arms sit at roughly **half** the maximal-leak
profile, which is neither "content" nor "pure label access". What that leaves unresolved is **what
fraction of the fitted margin the perfect-leak arm accounts for prompt by prompt**: this round
computes both per-prompt vectors and does not regress one on the other. The step is to regress each
fitted arm's per-prompt margin on `_perfect_leak`'s and report the residual — a slope near 1 with no
residual means the fitted arms are a noisy copy of the leak, and a resolved positive residual is
content the leak cannot explain. That is one regression on vectors this round already computes, and
its outcome is not forced.
