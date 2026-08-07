# R634 · The corpus holds five incompatible definitions of "a round citation"

**Decision this makes safe:** whether R633's blind spot matters. **It does, and not for the reason
the closing line gave.** The risk is not staleness — it is that **cross-round counts are not
comparable.**

| predicate | rounds with an inline copy | distinct literals | **behaviour classes** |
|---|---|---|---|
| **round citation** | 25 | 5 | **5** |
| verdict / world read | **195** | — | — |
| ledger read | 7 | — | — |
| decimal value | — | 0 | ⚠ **UNVERIFIED** |

| behaviour class | rounds |
|---|---|
| `R(\d{3})` — bare, no delimiter | **18** |
| `\(R(\d{3})[,)]\|R(\d{3})[,)]` | 7 |
| `\(R(\d{3})[,)]` — parenthesis required | 3 |
| `R(\d{3})[,)]` | 3 |
| `R(\d{3})\s*(?:->\|→)\s*R(\d{3})` | 1 |

**Five literals, five distinct behaviours.** The bare form matches `R123` inside `R1234`; the
paren-required form misses a citation in prose. **Any two rounds counting "citations" may be counting
different things**, which is what makes R633's staleness figure a floor rather than the whole story.

## ⛔ The g=0 control failed, and the reason is the fourth self-contamination
My probe string `zzq_no_such_literal` appeared in **exactly one round — this one** — because I wrote
it into the source the scan then reads. **A control's own probe contaminated the corpus by being
written into it.** R601, R604, R621, now this: the class recurs because *every* round here lives
inside its own population. Fixed by excluding self and assembling the probe at runtime.

## ⚠ And I nearly committed check #233's own lesson inside the round recording it
`decimal value` returned **0 literals**. **That is my extractor failing, not an absence** — reporting
it as a measured zero would have been exactly the *unmeasured ≠ measured-zero* error the check had
just caught one screen earlier. **It is reported `UNVERIFIED`.**

## Controls
| control | returned |
|---|---|
| **positive** — the canonical citation literal is present | PASS |
| **g=0** — a literal appearing nowhere (self excluded) | **0 rounds** — PASS |
| **negative** — 284 rounds carry no citation literal and are not counted | PASS — the extractor is not matching everything |
| **placebo** — a probe no variant can match | all agree (empty), **and the classes are not collapsed by it** |

**MULTIPLICITY:** 309 rounds × 4 predicate families + behavioural grouping over an 8-probe set + 4
controls.

**IMPOSSIBLE, named:** behavioural equivalence is decided on a **fixed probe set**, so two literals
agreeing here may diverge on an unprobed input. **The class count is a LOWER bound on divergence.**

## ⛔ Check #233
*"the **one** confirmed stale conclusion"* — R632 moved **two**. *"the sharpest thing it produced"* —
uncomputed. ⛔⛔ *"a class this round measured at zero by construction"* — **R633 never measured it;
unmeasured is not measured-zero**, and writing it up as an empty result is a false acquittal.

## The sentence I can no longer write
> *"inline copies are a staleness risk."*

**They are a comparability risk.** 195 rounds read a verdict key inline and 25 define their own
citation pattern in five mutually incompatible ways; staleness is the smaller half.

## NEXT
The 195 rounds reading a verdict key inline are the untested bulk of this, and R632 showed one such
reader was wrong in a way that moved two conclusions. **Group those 195 by the KEY SET they accept**
— `world` only, `world`+`verdict`, or something else — because R600 widened the canonical reader to
accept both and any round predating that reads a settled round as unsettled. That grouping turns
"195 inline copies" into a count of conclusions actually at risk.
