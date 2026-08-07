# R449 · judge-stability is a **real** axis and **not** a statable clause — the two halves disagree

**The decision this round makes safe:** whether R448's proposed fifth clause gets written.
**It does not** — but not for the reason the check was aimed at.

## The announced step survived identification; two premises in the sentence did not

*Seventeenth announced step checked.* 13 arms carry both judges, so an arm-level test exists.

⛔ **Premise 1 was false as written.** R448 said judge-stability is *"measurable without picking a
favourite judge"*. True and **irrelevant**: it changes the definition's type from `core(J)` to
`core(J₁,J₂)`. Clause ② needs one judge; this needs a **pair**, and the register already records
that no third judge exists. **A heavier requirement, sold as a lighter one.**

⛔ **Premise 2 was untested, and it was cheaper to test than the regression.** A clause is a predicate
on a *core*. If X barely varies across arms it describes the **judge pair** and there is no clause to
write, whatever a regression says. So that ran first.

## ⛔ And my own GATE 0 was the wrong instrument — caught before it was believed

The first version compared between-arm sd to a within-arm bootstrap SE and thresholded at
`ratio > 3`. It returned **3.1 (all_pairs) / 2.8 (drop_ties)** — the two tie rules landing on
**opposite sides of a number derived from nothing.** The arms share prompts, so the within-arm SE is
not the null for between-arm spread. Replaced with a permutation of arm labels **within each
prompt** — no free parameter:

| tie rule | between-arm sd | null median | p |
|---|---|---|---|
| all_pairs | 0.0251 | 0.0063 | **0.0000** |
| drop_ties | 0.0234 | 0.0065 | **0.0000** |

**4× the null.** X varies across arms decisively; the knife-edge was my statistic, not the data.

## ⭐ The identified contrast the variance test was too blunt to ask

Five arms carry their **own sham** — the same criteria pointed at the wrong prompt. That is a paired
manipulation of exactly the ingredient in question, and it removes every arm-level nuisance (k,
difficulty, satisfaction level) by construction.

| pair | Δ (all) | Δ (drop ties) |
|---|---|---|
| `coval_core` − sham | +0.0486 | +0.0477 |
| `full` − sham | +0.0408 | +0.0363 |
| `gen` − sham | +0.0361 | +0.0277 |
| `promptecho` − sham | +0.0560 | +0.0530 |
| `topw_k4` − sham | +0.0271 | +0.0284 |
| **pooled** | **+0.0417** [+0.0306,+0.0524] vs MDE 0.0152 | **+0.0386** [+0.0275,+0.0496] vs MDE 0.0156 |

**5 of 5, RESOLVED under both tie rules.** ⚠ The exact two-sided sign test over 5 pairs is
**p = 0.0625** and does *not* clear 0.05 — reported because direction and magnitude are different
evidence and neither is quoted without the other. The power is in the n=398 paired magnitude test.

## ⛔ Is X a reparameterisation? The arm-level answer was too weak to use

All 10 regression cells return adjusted R² ≤ 0 and none survives BH — **but this design's MDE is
R² = 0.40**, an enormous bar. That licenses only *"no linear relation with true R² ≥ 0.40"*.
Quoting it as independence would be a null with no power.

The same question at **n = 398 prompts** instead of 13 arms, using the paired sham differences:

| tie rule | corr(ΔX, ΔA2@2B) | 95% CI | shared variance |
|---|---|---|---|
| all_pairs | −0.0431 | [−0.1424, +0.0578] | **≤ 2.0%** |
| drop_ties | −0.0552 | [−0.1515, +0.0429] | **≤ 2.3%** |

> **X and clause ②'s own score gap share at most ~2% of their variance.** X is not a
> reparameterisation of "does this criterion set score above the floor".

## Controls

| control | returned |
|---|---|
| POSITIVE — planted `X = 2ΔA2 + k` | adjR² 1.0000, percentile **1.0000** ✅ |
| …fails at g=0 — pure-noise X | percentile 0.7889 < 0.95 ✅ |
| FLOOR — 60 noise draws | **91.7%** below threshold (want ~95%) ✅ |
| CEILING — 0.95 strictly inside | (0.513, 1.000) ✅ |
| MDE — simulated, n=13 | **R² = 0.40** — reported *because* it is bad |
| GATE 0 permutation | p = 0.0000 both rules ✅ |

## ⭐ The verdict is split, and that is the finding

- **MEASURED:** X is a real axis. It varies across arms (p = 0.0000), responds to a content
  manipulation (+0.0417, RESOLVED, 5/5), and shares ≤ 2% of its variance with the published score gap.
- **STRUCTURAL:** it still **cannot be a clause of this definition.** `n_judge_pairs = 1`. A predicate
  on a judge *pair*, validated on the only pair in existence, is a description of that pair.

**A property can be real and unstatable at the same time**, and the second half is not a weaker
version of the first — it is a different kind of fact, and no amount of measurement moves it.

## ⚠ Population changed, stated rather than buried

**968 → 398 prompts.** The 13-arm intersection is far smaller than the 3-arm one R448 used. X for
`coval_core` reads 0.6057 here vs 0.6044 there, `gen` 0.6360 vs 0.6302 — consistent, but **R448's and
R449's numbers are on different populations** and are not interchangeable.

## Impossible here, named

- **a second judge pair** — needs a third judge; no resampling creates one.
- **construct validity of X** — needs to know which judge is right; nothing here does.
- **more arms** — 13 is every arm on disk carrying both judges. The ceiling is the release's.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
