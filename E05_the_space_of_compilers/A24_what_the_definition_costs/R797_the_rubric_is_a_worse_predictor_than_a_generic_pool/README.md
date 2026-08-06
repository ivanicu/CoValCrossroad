# R797 · the prompt's own rubric predicts its own prompt's humans WORSE than a generic pool does

`run.py` · `PREREGISTRATION.txt` · `results/target_quality.json` · 968 prompts × all annotators ·
**WORLD A** · two hash seeds byte-identical, md5 `eb922fd8f2c8a27a82f52d16e032a783`

## THE DECISION THIS MAKES SAFE

**A generic 16-criterion pool, written for no prompt in particular, predicts a prompt's own human
rankings better than that prompt's own rubric does.**

> `genericpool16` vs HUMAN **0.5422** · `coval_full` vs HUMAN **0.5087**
> **gap +0.0335 [+0.0251, +0.0420], MDE 0.0118, p 0.0008 — RESOLVED**

Both sides are proportions against the **same** target, so no ceiling enters (D1, R794's construction
reused). This is a statement about the release, and every clause built on "preserving the rubric"
inherits it: **the thing a core is asked to preserve is not the better predictor of what the core is
scored against.**

## ⭐ AND IT SURVIVES THE REGISTERED SIZE CONFOUND

`full` has a mean of 15.48 criteria but ranges 4–39, while the pool is fixed at 16 — so the gap could
have been a size-variance effect. Stratified by the prompt's own criterion count:

| criteria | n | gap | | |
|---|---:|---|---|---|
| 4–8 | 80 | +0.0268 [+0.0019, +0.0527] | mde 0.0368 | unresolved |
| 9–12 | 222 | **+0.0361 [+0.0194, +0.0558]** | mde 0.0258 | RESOLVED |
| 13–16 | 299 | **+0.0292 [+0.0160, +0.0429]** | mde 0.0204 | RESOLVED |
| 17–20 | 206 | **+0.0450 [+0.0269, +0.0634]** | mde 0.0266 | RESOLVED |
| 21–39 | 161 | +0.0267 [+0.0054, +0.0475] | mde 0.0295 | unresolved |
| **12–20 matched-size** | **573** | **+0.0369 [+0.0244, +0.0454]** | mde 0.0155 | **RESOLVED** |

**Same sign in all five strata**, three resolved individually, and the matched-size stratum — where
the two targets are closest in size — gives the *largest* clean estimate. BH over the 6 tests:
**6 survive, 0 do not.** The confound does not explain it.

## ⛔ AND R796's CLOSING SENTENCE DOES NOT SURVIVE ITS OWN TEST

R796 closed by proposing to ask what distinguishes `coval_core` from `topvar_k4`, generalising an
inverse relation from that pair. Check #399 found the pair is **not a live question** — they differ
by 0.0802 on A2 against an MDE near 0.011, and R789 already put them in different levels. Tested
properly:

| | |
|---|---|
| corr(rubric-preference, A2), 27 names | −0.2550 |
| **on the 20 distinct objects** (D3: aliases inflate n) | **−0.3138** |
| permutation p | **0.1820** |
| ⭐ **MDE — the smallest \|r\| this design detects at 80% power** | **0.6** |

**The observed 0.3138 is well below what the design can resolve.** So the closing sentence
generalised from the two arms at the ends of a scatter — §4's *the closing sentence is a claim and
never gets a control*, in my own previous round.

## ⛔⛔ AND THE CORRELATION'S SIGN WAS FORCED ANYWAY

D4, written before the run: if arms were mixtures of `full`-like and pool-like classes, an inverse
relation would arise **by construction** whenever the pool is the better predictor. Built:

> synthetic mixtures: corr **−0.6872 [−0.8817, −0.4018]** · observed **−0.3138**

**The sign is not evidence — it is arithmetic given E1.** Only the magnitude could have been a
finding, and it is unresolved. ⚠ Note the observed value is *weaker* than the forced construction,
which if anything argues the arms are **not** simple mixtures; that too is unresolved and is stated
rather than used.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | `full` vs HUMAN **0.5087225654** vs R793's committed; `genericpool16` **0.5422329001** vs R789's committed — both to 1e-9 | PASS, else exit 2 |
| PLACEBO | a target against itself: gap **0.000000000000** | PASS |
| POSITIVE | plant on `full`'s human column: δ=0 **does not resolve** (the floor fails, as required) · 0.01 / 0.02 / 0.05 resolve | PASS, band admissible |
| NEGATIVE | human classes shuffled across prompts: `full` **0.5087 → 0.4266**, pool **0.5422 → 0.4255**, gap **−0.0011** | PASS |
| CONFOUND | the size stratification above | ⭐ does not explain it |
| NOISE FLOOR | annotator split-half **on the gap**, 20 draws: **0.002832** | measured — the gap is 12× it |
| E3 MDE | \|r\| = **0.6** at 80% power, n = 20 | reported with the result, per D2 |

## WHAT DIED

- **R796's NEXT** — the pair it named is well separated, and the relation it generalised is
  unresolved at p 0.1820 against an MDE of 0.6.
- **the inverse relation as a finding** — its sign is forced by D4 given E1.
- ⚠ **and, gently, the framing of every "preserves the rubric" clause in this arc**: the rubric is not
  the better predictor of the human rankings the benchmark scores against.

## WHAT SURVIVES — AND THIS ROUND ADDS RATHER THAN SUBTRACTS

**+0.0335 [+0.0251, +0.0420]**, resolved, size-controlled, with a measured noise floor 12× smaller
than the effect. Together with R794's Q2 (**+0.0578 [+0.0502, +0.0658]**, the core beating `full` at
predicting the human) the picture is consistent and now has a mechanism: **`full` is a weak predictor
of its own prompt's humans, so both a released core and a generic pool beat it.**

## SCOPE

968 prompts × all annotators (median 16) · instrument A2, pairwise-sign agreement with the human
annotators · baseline `coval_full`, the prompt's own rubric · strata by `full`'s own criterion count
(min 4, mean 15.48, max 39) · NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| WHY the rubric predicts worse | the criteria's text and a relevance judgement — the construct wall (`corebench/score.py:34`) |
| a second generic pool | the release ships one, of 16 |
| a correlation resolved at n = 20 | more distinct arms than the release has |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The mechanism is now stated and measured: `full` predicts its own prompt's humans at 0.5087 while a
prompt-blind pool reaches 0.5422, gap +0.0335 [+0.0251, +0.0420]. Computed by this round's `run.py`,
that gap holds in all five size strata and is 12× its own annotator noise floor. The step is to ask
what `full` is doing with the criteria it has: it carries a mean of 15.48 of them and loses to 16
generic ones, so the question is whether its criteria are individually weaker predictors or whether
the loss appears only in aggregate — a per-criterion comparison of the two pools against the human
target, which is the first question in this arc that examines the RUBRIC rather than the cores built
from it.
