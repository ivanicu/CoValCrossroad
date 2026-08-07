# R796 · with the floor set to ABSENCE, prompt-matching is worth nothing — and the sign is negative

`run.py` · `PREREGISTRATION.txt` · `results/matched_vs_blind.json` · 968 prompts × 6 k-cells × 2
sources × 20 draws · **WORLD B** · two hash seeds byte-identical, md5 `e1f13511a179cea00c36893a260e09c4`

## THE DECISION THIS MAKES SAFE

**At every target size where it resolves, a prompt-BLIND target matches `coval_core` BETTER than its
own prompt's rubric does.**

| k | matched (subsets of this prompt's `full`) | blind (subsets of `genericpool16`) | gap | |
|---:|---:|---:|---|---|
| 1 | 0.6391 | **0.7175** | **−0.0784 [−0.0890, −0.0686]** | RESOLVED |
| 2 | 0.6928 | **0.7590** | **−0.0663 [−0.0770, −0.0554]** | RESOLVED |
| 4 | 0.7356 | **0.7771** | **−0.0415 [−0.0530, −0.0290]** | RESOLVED |
| 8 | 0.7693 | **0.7848** | **−0.0155 [−0.0285, −0.0014]** | RESOLVED |
| 12 | 0.7805 | 0.7863 | −0.0058 [−0.0201, +0.0086] | unresolved |
| 16 | 0.7842 | 0.7886 | −0.0044 [−0.0196, +0.0111] | unresolved ⚠ **MIXTURE (D3)** |

**0 cells resolved positive, 4 of 5 clean cells resolved NEGATIVE.** So what R794 called *preserving
the rubric's verdicts* is agreement with **any competent target of that size** — and a generic pool
does it better. The clause dies in the form R794 wrote it.

⭐ **The gap is largest where the target is smallest.** One generic criterion already matches the core
better (0.7175) than one of its own rubric's (0.6391), by **−0.0784**. Prompt-specific *writing* is
where the disadvantage lives, and it shrinks as the target grows.

## ⭐ AND THE CONFOUND CONTROL STRENGTHENS IT

Registered before the run: `full` draws from a mean pool of 15.48 while `genericpool16` draws from
exactly 16, so at a given k the matched subsets come from a smaller, prompt-varying pool. Re-run on
the **437 of 968** prompts with ≥ 16 criteria, where both pools are ≥ 16:

| k | gap, all prompts | gap, matched-pool subpopulation |
|---:|---|---|
| 4 | −0.0415 | **−0.0550 [−0.0705, −0.0380]** |
| 8 | −0.0155 | **−0.0311 [−0.0493, −0.0132]** |
| 12 | −0.0058 *(unresolved)* | **−0.0228 [−0.0418, −0.0031]** *(resolved)* |

**Every cell moves further negative and k=12 becomes resolved.** The pool-size asymmetry was masking
part of the effect, not creating it.

## ⛔ MY CONSISTENCY CHECK FAILED, AND THE REPAIR IS EXACT

D4 predicted `coval_core vs generic` (= `POOL[0:4]`, R788) must lie inside the blind k=4 draw
distribution. It returned **0.7856 against a 20-draw range of [0.7727, 0.7803] — OUTSIDE.**

The check was mis-specified: `generic` is one **specific** subset while the dose draws **random**
ones, and 20 draws cannot span a **C(16,4) = 1,820** family. Repaired by computing the family
exactly:

> exact range over all **1,820** blind 4-subsets **[0.7357, 0.8025]**, mean **0.7767** —
> `generic` sits at percentile **76.3**, **INSIDE**
> and the 20-draw mean **0.7771** against the exact mean **0.7767**: the dose is **unbiased**; only
> its range was too narrow, which is what a 20-of-1820 sample does

**A control that fails for its own reasons is repaired by computing the population it sampled, not
by widening the claim.**

## E3 · THE RELEASED CORE IS UNREMARKABLE ON THIS AXIS

`vs full` minus `vs genericpool16`, over 27 named arms:

| arm | preference for the matched rubric |
|---|---|
| `topvar_k4` | **+0.1572 [+0.1424, +0.1723]** |
| `topwvar_k4` | +0.1420 |
| `random_k4_s2` | +0.1231 |
| **`coval_core`** | **−0.0036 [−0.0195, +0.0119]** — rank **15 of 27** |
| `generic` / `generic_reprov` | −0.2076 |
| `genericpool16` | −0.2467 |

⭐ **Arms that genuinely prefer their own prompt's rubric exist, up to +0.1572** — so the instrument
can detect the preference. **The released core shows none of it.** And the blind arms prefer the
blind pool, as they must, which is the population's own built-in positive control.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT (D1) | matched all-criteria **0.7849517906** vs committed (\|Δ\| 2.2e-16); blind k=16 **0.7885674931** vs committed (\|Δ\| **0.0e+00**) | PASS, else exit 2 |
| PLACEBO | `coval_core` against its OWN class **1.000000000000** | PASS |
| POSITIVE (D2) | both doses monotone — matched 0.6391 → 0.7842, blind 0.7175 → 0.7886 | PASS |
| NEGATIVE | `coval_core`'s class shuffled across prompts: matched **0.7842 → 0.5138**, blind **0.7886 → 0.5083** | PASS |
| CONFOUND | pool-size control on 437 prompts — every cell more negative | ⭐ strengthens the finding |
| CONSISTENCY | D4 failed at 20 draws, **repaired exactly**: percentile 76.3, INSIDE | see above |
| NOISE FLOOR | largest draw sd across cells **0.0080** | measured |

## MULTIPLICITY

**33 tests** — 6 gap cells + 27 arm contrasts — BH at q = 0.05 over the union: **23 survive, 10 do
not.** The 12 dose cells are a curve and are reported whole.

## WHAT DIED

- **"a core preserves the rubric's verdicts"**, in R794's form. With the floor set to absence the
  gap is **negative** at 4 of 5 clean sizes.
- **R794's Q1 as evidence for anything about the rubric** — it was matched-vs-poison; matched-vs-blind
  runs the other way.
- **my own D4**, which sampled 20 of a 1,820-member family and asked whether a specific member fell
  inside the sample's range.

## WHAT SURVIVES

R794's **Q2** — the core beats `full` at predicting the human, +0.0578 [+0.0502, +0.0658] — still
untouched, and now the more interesting of the two: the core departs from the rubric *and* predicts
the human better. R795's dose, reproduced here to **2.2e-16**.

## SCOPE

968 prompts (437 with ≥ 16 criteria for the confound cell) · targets from `coval_full` (min 4, mean
15.48, max 39 criteria) and `genericpool16` (exactly 16) · 20 subset draws per cell, plus the exact
1,820-subset class for D4 · NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether a blind criterion is UNINFORMATIVE | it is blind, not empty; separating them needs a criterion-level relevance judgement — the construct wall (`corebench/score.py:34`) |
| a blind pool larger than 16 | the release ships one, of 16 |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

Two clauses have now been tested against a neutral floor and only one survives. Computed by this
round's `run.py`, the released core prefers its own prompt's rubric by **−0.0036 [−0.0195, +0.0119]**
while `topvar_k4` prefers it by **+0.1572** — so the axis is measurable and the core sits at rank 15
of 27. The step is to write the definition around what survived rather than what was hoped for:
**state clause ② as the human-prediction claim R794's Q2 established, drop the rubric-preservation
language, and then ask the question this round makes unavoidable — what distinguishes the
released core from `topvar_k4` — an arm whose rubric-preference is **+0.1608 higher** (+0.1572
against −0.0036; a ratio is meaningless across a sign change) and whose agreement with humans is
**0.0802 lower** (0.4863 against 0.5665).**
