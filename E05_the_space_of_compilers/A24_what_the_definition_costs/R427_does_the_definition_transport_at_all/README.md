# R427 · the first number on the second corpus — does a prompt-blind core pick what people picked?

**The decision this round makes safe:** whether the definition has *any* cross-release evidence. Its
own table has said `transfer to another release: RETRACTED` since R398, and nothing had walked
through the opening.

⚠ **This README was rewritten after the round grew.** It shipped describing one design and four
worlds; the round now carries **ten scripts, nine analyses and one self-retraction**, and a design
document that misdescribes its own round is a correctness problem, not a filing one.

## ⛔ Seven rounds read the second corpus. Zero scored on it.

R398 existence · R399 estimand · R400 depth · R402 harness · R403 statability · R412 clustering ·
R413 score-clustering — and **not one** calls `select_core` or `judge_core` on it. **Six rounds of
*"can we?"* and none of *"here is the number."***

## The design

**Estimand:** `ACC` = P(the response the core ranks first is the one a human chose).
**Unit = conversation** — R413: `kappa_chosen = 1.0` *within* a conversation (`deff 3.317`); rows
would shrink every interval by **1.82×**.
**Sample:** 2,200 conversations → 7,344 interactions → 18,512 responses → **74,048 judge calls**, k=4.

⚠ **`generic` is clause ②'s COMPARATOR, not its subject.** Clause ② reads *"better than a
size-matched set that never read the conversation"* — `core_generic.json` **is** such a set. This
measures the **floor** of transport and speaks to **no prompt-specific core**.

## The scripts, and what each returned

| script | question | verdict |
|---|---|---|
| `selftest.py` | can the analysis name a world it is handed? | **PASS** — 3 fixtures, 3 distinct verdicts |
| `baselines.py` | the bar, **before any arm existed** | chance `0.4194` · **longest `0.5096`** · first `0.4375` |
| `run.py` | the arms against the target | **`W-LENGTH`** — `generic 0.4374`, `−0.0722` vs length at 2.85× MDE |
| `speccurve.py` | is that one cell? | **`W-ROBUST`** — generic clears length in **0 of 24** cells |
| `strata.py` | is `+0.0179` a pooling artifact? | **`W-REAL`** — attack **failed**; clears only at n≥3, **at chance at n=2** |
| `target_length.py` | is the **target** length-loaded? | **`W-PARTIAL`** — tau `+0.2113` vs null `−0.0091` |
| `length_dose.py` | anything beyond length? | **`W-ONLY-LENGTH`** at fixed n=2 — never clears MDE in any bin |
| `position.py` | `0.4374` ≈ `0.4375`: structure? | **`W-COINCIDENCE`** — first is at chance on length |
| `arm_agreement.py` | same picks, or same score? | **`W-SAME-ORDERING`** — `0.6976` vs `0.5070` null |
| `criterion_effect_across.py` | judge, or prompt-blindness? | **`W-CORPUS`** — the two k=4 blind cells differ >2× |

## ⛔ The self-retraction, kept where it happened

`response_effect.py` reported **RESPONSE 76.30 % / CRITERION 3.86 %** on one *global* grid.
`criterion_effect_across.py` reported **55.82 % / 31.39 %** on the same file, decomposed **within
interaction**.

> **The global grid's response factor absorbs BETWEEN-interaction variance — which the estimand never
> uses**, because every arm picks a winner *inside* an interaction. `3.86 %` is **retracted**, and
> with it *"satisfaction is overwhelmingly a property of the reply."* **The number was not
> miscomputed; it was scoped wrong.**

**What survives:** the 69.8 % ranking agreement, measured directly from the arms' picks and never
derived from a decomposition. **What fell was the explanation, not the observation.**

⚠ The retracted number **never entered `README.md` or `DEFINITION.md`** — verified by grep, so no
downstream correction is owed.

## Controls that failed and what they cost

| control | failed because | fix |
|---|---|---|
| floor check (`run.py`) | compared to the **arm's** MDE — a perfect arm has `sd=0`, so it **could not pass** | its own paired MDE |
| tiebreak (`run.py`) | argmax resolved by **response-ID string order** under saturation | tiebreak swept 4 ways + kill |
| identity (`target_length`) | wrong tau-b denominator; then **undefined folded into `0.0`** (273 of 7,344) | `sqrt((n0−n1)(n0−n2))`; drop + count |
| RANDOM (`position`, `arm_agreement`) | clustered observed vs **flat** expectation — **twice, verbatim** | same weighting both sides |
| shuffled null (`arm_agreement`) | permuted **ids**, which are unique per interaction → null `0.0000` **by construction** | permute **positions** + zero-variance guard |

⚠ **A third recurrence of the clustered-vs-flat defect must become a shared helper, not a third
patch.**

## Impossible here, named

- **a prompt-specific core** — no rubric on this corpus; generating one is a separate job.
- **clauses defined against `full`** — R403: NOT-STATABLE off the home release (3 of 6 statable).
- **construct validity of `score`** — this release's own human rating; no external gold standard.
- **position randomisation** — no presentation-order field; `first` indexes **storage** order.
- **a causal effect of length** — nuisance-matching, not an ablation.
- **a k-free criterion share** — the statistic depends on k and the cells differ in it.

Findings, with their scope, live in the top-level README and `DEFINITION.md`. This file states the
design and the round's own corrections.
