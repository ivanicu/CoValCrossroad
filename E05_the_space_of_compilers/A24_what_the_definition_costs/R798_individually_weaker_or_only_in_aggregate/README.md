# R798 · the rubric's criteria are individually weaker, and the whole gap is ACCURACY

`run.py` · `PREREGISTRATION.txt` · `results/singletons.json` · 968 prompts · 14,984 `full` instances ×
15,488 pool instances · **WORLD A** · two hash seeds byte-identical, md5 `22d740f6094830500a10869bf934d983`

## THE DECISION THIS MAKES SAFE

**One criterion at a time, `coval_full`'s criteria agree with the human less often than a coin.**

| | `coval_full` | `genericpool16` | gap |
|---|---:|---:|---|
| **singleton agreement** | 0.4664 | 0.5142 | **+0.0490 [+0.0441, +0.0543]**, MDE 0.0078, RESOLVED |
| discrimination (1 − tie) | **0.9526** | 0.9476 | **−0.0053 [−0.0077, −0.0029]**, RESOLVED |
| **accuracy on non-tied pairs** | **0.4805** | **0.5332** | **+0.0538 [+0.0486, +0.0592]**, RESOLVED |

**The entire gap is accuracy.** `full`'s criteria *discriminate more often* — they produce a non-tied
sign 0.9526 of the time against the pool's 0.9476 — and when they do, they are **right 0.4805 of the
time, below a coin.** The generic pool reaches 0.5332.

⭐ **And the singleton gap is LARGER than the aggregate one**: +0.0490 against R797's +0.0335, a ratio
of **1.461**. ⚠ D3, registered before the run: summing k criteria then taking signs is *not* averaging
k singleton classes, so these are different quantities and either could be larger. What the ordering
says is that **summing partially recovers what the individual criteria lack** — it does not say the
two measurements disagree.

## ⛔ AND THE SIZE CONFOUND MAKES IT BIGGER, NOT SMALLER

Registered before the run: a criterion satisfied by none or all four responses is inert regardless of
content. Satisfaction spread — `full` **0.1403**, pool **0.1192**, so `full`'s criteria are the more
spread. Reweighting to `full`'s own spread distribution:

| spread quintile | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| gap | +0.0285 | +0.0418 | +0.0485 | +0.0664 | +0.0892 |

**Spread-matched gap +0.0577**, against the raw +0.0490. The gap **grows** with spread, so the
confound was suppressing it.

## ⛔⛔ MY REGISTERED DERIVATION D1 WAS FALSE, AND ITS OWN PLACEBO CAUGHT IT

D1 stated `composite = (1 − tie) × accuracy`, on the assumption that a tied sign can never agree with
a human. **It can**: `cls()` returns 0 whenever a *human* ranks two responses equally, so a tie-tie
match counts. The placebo returned **worst |Δ| = 3.246e-01** — a third of the scale. Corrected to
`composite = (1 − tie)·acc_nontied + tie·acc_tied`, which checks at **2.220e-16**.

**A derivation written into a preregistration is still a hypothesis, and the only reason this one was
caught is that it had a numerical placebo attached.**

## ⛔ AND MY POSITIVE CONTROL COULD NOT PASS

The first version mirrored the agreement value (`v → 1−v`) on a share of instances and demanded a
0.05 drop. From a base of 0.5142 the *maximum possible* drop is 0.0284 — **the threshold sat outside
the achievable band.** §4's *control that cannot PASS*, sub-kind two. Repaired to a real inversion of
the criterion's **direction**, with the band computed rather than asserted:

| inverted share | 0.0 | 0.1 | 0.25 | 0.5 | 1.0 |
|---|---:|---:|---:|---:|---:|
| pool singleton mean | **0.5142** | 0.4935 | 0.4648 | 0.4136 | **0.3184** |

Floor 0.5142, ceiling 0.3184, achievable drop **0.1958**, criterion set at a quarter of it. **PASS.**

## ⚠ AND WHAT WAS NOT IDENTIFIED, STATED RATHER THAN ESTIMATED

**Each `full` criterion appears on exactly one prompt** (D2). Its singleton agreement is one prompt's
measurement, so **no per-criterion ranking is admissible** and this round declines the per-criterion
question R797's NEXT asked for. The identified estimand is the distribution over criterion
*instances*, and that is what is reported.

⚠ **D4, the precision trap**: the pool's 15,488 instances are **16 criteria seen 968 times**. Clustered
by criterion the half-width is ±0.0085; the **naive independent-instance half-width would be ±0.0025**
— a **3.4× overstatement** avoided by clustering on the right unit.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | summed `full` **0.5087225654** and pool **0.5422329001** against R793's and R789's committed values, to 1e-9 | PASS, else exit 2 |
| PLACEBO | the **corrected** identity: worst \|Δ\| **2.220e-16** | PASS — **after D1 was found false at 3.246e-01** |
| POSITIVE | band **0.5142 → 0.3184**, computed | PASS — **after the first threshold proved unreachable** |
| NEGATIVE | human classes shuffled: `full` **0.4664 → 0.4115**, pool **0.5142 → 0.4103** | PASS |
| CLUSTERING | by prompt (`full`) and by criterion (pool), with the naive figure printed beside | ⭐ 3.4× overstatement shown |
| CONFOUND | spread quintiles + reweighting | ⭐ enlarges the gap |
| NOISE FLOOR | annotator split-half on the pool's singleton mean, 10 draws: **0.001699** | the gap is 29× it |

## MULTIPLICITY

**3 tests** — the singleton gap and the two component gaps — BH at q = 0.05: **3 survive, 0 do not.**
Distributions and the spread quintiles are reported whole.

## WHAT DIED

- **"the loss appears only in aggregate"** — World B is out: the singleton gap is resolved and
  *larger* than the aggregate.
- **my D1**, false as registered, caught by its own placebo at a third of the scale.
- **my first POSITIVE control**, whose threshold was outside the achievable band.
- **the per-criterion question as R797's NEXT posed it** — not identified, since each `full`
  criterion is observed once.

## WHAT SURVIVES

R797's aggregate gap, now with a mechanism one level down: **the rubric's criteria are individually
less accurate about their own prompt's humans than generic ones are, while discriminating slightly
more often.** Both summed aggregates reproduced to 1e-9 — the fourth consecutive round whose object
check is an exact reproduction of a prior committed number.

## SCOPE

968 prompts × all annotators (median 16) · 14,984 `coval_full` criterion instances (mean 15.48 per
prompt, each on ONE prompt) and 15,488 pool instances (16 criteria × 968) · instrument singleton
pairwise-sign agreement with the human annotators · NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| any INDIVIDUAL `full` criterion's power | that criterion appearing on more than one prompt (D2); the release gives each exactly one |
| WHY a criterion predicts badly | its text and a relevance judgement — the construct wall (`corebench/score.py:34`) |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

The mechanism is now two levels deep: the released core beats the rubric at predicting humans
(R794, +0.0578), a generic pool beats it too (R797, +0.0335), and one criterion at a time the
rubric's are **less accurate** while discriminating **more** (this round, accuracy +0.0538, 
discrimination −0.0053). Computed by this round's `run.py`, `full`'s singleton accuracy is **0.4805**,
below a coin. The step is to ask whether that sub-coin accuracy is uniform or concentrated: sort the
14,984 instances by their own accuracy and ask what share of `full`'s criteria are actively
*anti-predictive* — because a rubric whose criteria average below chance either has many mildly bad
ones or a minority that are systematically inverted, and those are different defects with different
repairs.
