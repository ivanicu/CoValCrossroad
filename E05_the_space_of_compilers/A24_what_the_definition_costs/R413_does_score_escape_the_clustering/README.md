# R413 — score offers no escape. The corpus is conversation-limited whatever outcome I target.

**The decision this makes safe:** *can re-scoping onto `score` recover the lost n?* **No. ~8,000 is
the ceiling, and the replication cannot be powered on this corpus at any outcome choice.**

## Result — `W_SCORE_TRAPPED`. Four controls pass. **No GPU.**

| | |
|---|---:|
| **`argmax(score)` = `if_chosen`** | **25,437 of 25,572 = 0.9947** |
| `P(same argmax model \| same conversation)` | **1.0000** over 37,973 pairs |
| `P(same \| different conversations)` | 0.0572 |
| **κ (argmax model)** | **1.0000** — *the chosen model was also 1.0000* |
| ICC of the **within-interaction score gap** | **0.2383** *(raw levels were 0.1978)* |
| DEFF / n_eff / ratio | 3.317 / **8,076** / **2.51×** |

## ⛔ R412's NEXT had a hole of the same shape as the last three

A clause-② test consumes an **ordering**, not raw scores. **If the top-scored response is the same
model all through a conversation, an ordering outcome is exactly as clustered as `if_chosen` was.**
And it is: **κ = 1.0000.**

**Score carries almost nothing beyond the choice** — 99.47% agreement — so targeting it changes the
label and not the information.

## ⚠ And my own cancellation derivation did not hold in the data

I argued that a conversation- or user-level offset enters both responses identically, so a
**within-interaction contrast subtracts it exactly** — the same cancellation R410 verified at
`2.8e-17`, running in the helpful direction.

**The gap's ICC came out at 0.2383, *above* the raw levels' 0.1978.** Differencing did not help; it
slightly hurt. **The derivation was about a purely additive offset, and the data is not purely
additive.** *Labelled a derivation before the run, and it is the derivation that failed — not the
measurement.*

## Controls

| | returned |
|---|---|
| **REPRODUCE (+)** ⭐ | my κ instrument on `if_chosen` model identity returns **1.0000**, matching **R412's committed value** — `PASS`. **A control whose answer was produced by a different round** |
| **SYNTH (+/−)** | ICC 0.80 recovers 0.800; no-structure returns 0.000 — `PASS` |
| **SHUFFLE** | conversation labels destroyed on the **real** gap data → **0.0082** — `PASS` |
| **TIES** ⭐ | **1,579 of 27,151** interactions have a tied top score and are **excluded, never broken by array order** — that would manufacture agreement with whatever the file lists first |

## What this closes

**The second corpus cannot power the replication at any outcome choice.** `if_chosen` → 2.47×;
score-ordering → 2.51×; the ICC = 0 ideal would be 4.57× and is unreachable because the winner is a
conversation-level constant.

> **R412's NEXT was a dead end, and it cost one round to find — which is the cheapest way to find
> one.**

## Register

| criterion | status |
|---|---|
| **an ARM's error clustering** | **N/A** — needs the judge. **This is the step my last three closing sentences each skipped**, and it is named rather than made to sound like a task |
| **a causal reading of ICC** | **N/A** — variance decomposition, not mechanism |
| **a second target corpus** | **N/A** — one |

## The sentence I can no longer write

> *"score is per-response and only 0.1978 clustered, so a score-based design recovers the lost n"* —
> **the design consumes an ordering, the ordering is conversation-constant, and differencing made the
> clustering worse rather than better.**

Artifact: `results/r413_score_clustering.json`, source-stamped.
