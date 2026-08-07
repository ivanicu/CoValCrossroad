# R794 · the WORLD A / WORLD B fork was an artifact of comparing two different targets

`run.py` · `PREREGISTRATION.txt` · `results/two_targets.json` · 21 distinct objects × 968 prompts ×
all annotators · **WORLD C** · two hash seeds byte-identical, md5 `05ee3429cab9b5e27b476370b6519f00`

## THE DECISION THIS MAKES SAFE

**A core preserves the rubric's verdicts AND beats the rubric at predicting the human. Both. The
dichotomy was produced by one cross-target comparison, not by the object.**

| question | both sides scored against | `coval_core` | verdict |
|---|---|---|---|
| **Q1** does it preserve the RUBRIC's verdicts? | `coval_full`'s class | 0.7850 vs a shuffled-rubric floor of 0.4888 → excess **+0.2961 [+0.2744, +0.3166]** | **YES** |
| **Q2** does it track the HUMAN better than the rubric does? | the human annotators | 0.5665 vs `full`'s 0.5087 → **+0.0578 [+0.0502, +0.0658]**, MDE 0.0111 | **YES** |

**Neither comparison uses a ceiling.** R793's undecidable normalisation was needed only to compare
`vs HUMAN` (ceiling 0.5519) with `vs FULL` (ceiling 1.0) — two proportions of *different* targets.
Ask two same-target questions instead and the choice never arises. **D2, written before the run, is
why this was possible: nothing in the algebra forced Q1 high to imply Q2 low**, because the rubric is
a poor predictor of the human (`full` vs HUMAN = 0.5087, barely above `random_k4_s0`'s 0.4927).

## ⛔ THE WALL FELL IN THREE LINES

R793 closed with *"the first thing in this arc that no further computation can decide."* §4: an
unchecked wall is UNVERIFIED, never SETTLED — and four walls have fallen in this arc's last seven
rounds. **What decided it: two same-target comparisons, both computable from data R793 itself
loaded.** Cost: three lines, zero new instruments. **Fifth wall.**

## ⛔ AND MY REGISTERED CONFOUND WAS REFUTED BY ITS OWN CONTROL — IN THE CONSERVATIVE DIRECTION

D3 said `core vs FULL` is inflated because both track the human. Regressing `vs FULL` on `vs HUMAN`
over the 20 objects (`full` excluded by D4, being 1.0 by construction):

> **slope −0.4825** — arms that track humans *better* agree with `full` **less**.

**The confound runs the other way.** `coval_core`'s residual is **+0.0286 [+0.0199, +0.0377]** — above
what its A2 predicts, and resolved against prompt resampling. ⚠ **But it is only +0.64 of the
across-arm residual sd (0.0450)**, so it is resolved against sampling noise and *not* exceptional
among arms. Both uncertainties are reported because they answer different questions.

## ⚠ THE SCOPE OF Q1, STATED PRECISELY

| what is resolved | what is not |
|---|---|
| **prompt-matched rubric vs SHUFFLED rubric**: +0.2961 [+0.2744, +0.3166] | **specificity** — `full` rather than *any* arm's class: the gap to the random-arm sham is **+0.0487** and this round computes **no interval for it** |

So Q1 is resolved for *matching* and a point statement for *specificity*. The clause "preserves ITS
verdicts" is supported in the sense that the core tracks **its own prompt's** rubric far above a
mismatched one; whether it tracks the rubric rather than merely tracking what any competent arm
tracks is **not settled here**.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R793's `vs FULL` and `vs HUMAN` columns reproduced: worst \|Δ\| **0.000e+00** over its 7 arms | PASS, else exit 2 |
| PLACEBO | every arm against its OWN class: worst \|1 − v\| **0.0e+00** | PASS |
| POSITIVE | the plant alone on Q2: δ=0 → **does not resolve** (the floor fails, as required) · 0.005 → resolves · 0.05 → resolves | PASS, band admissible |
| NEGATIVE | `full`'s class shuffled across prompts: Q1 **0.7850 → 0.4888**; **Q2 unchanged to 0.0e+00** — a derivation, since Q2 never touches `full`'s class | PASS |
| SHAM | Q1 against a random arm's class instead of `full`'s: **0.7363** | see the scope note |
| D3 | the regression, **which refuted its own confound** | ⭐ conservative direction |
| NOISE FLOOR | annotator split-half on the human column **0.003523** | measured |

## MULTIPLICITY

**41 tests** — Q1 over 21 arms, Q2 over 20 — BH at q=0.05 over the **union**, which is the stricter
reading since both families involve the same arms. **40 survive, 1 does not.**

## WHAT DIED

- **the A/B fork itself** — not adjudicated, *dissolved*. `whose_verdicts`'s two worlds were never
  exhaustive, and D2 says nothing forbade both being true.
- **R793's wall** — "no further computation can decide" survived one round.
- **my own D3** — the confound I registered runs backwards, so Q1 was conservative, not inflated.
- **"the core preserves the rubric's verdicts" as an unqualified claim** — resolved for matching,
  a point statement for specificity.

## WHAT SURVIVES

Everything `whose_verdicts` measured; only its framing changes. And R793's numbers, reproduced to
**0.000e+00** — the third round in a row whose object check is an exact reproduction of a prior
artifact by different code.

## SCOPE

population 21 distinct objects × 968 prompts × all annotators (median 16) · instrument pairwise-sign
agreement, against the human annotators for Q2 and `coval_full`'s deterministic class for Q1 ·
baseline a shuffled `full` and a random arm's class for Q1, the arm `full` for Q2 · NBOOT 1,200 ·
first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether preserving the rubric is DESIRABLE | a stated purpose for the benchmark; both questions resolve without settling what a core is FOR |
| Q1's specificity with an interval | a null distribution over comparison arms — buildable, and the next round's work |
| construct validity | an external gold standard — `corebench/score.py:34` |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The clause can now be written in a form that says what was measured: *a core is a rewriting whose
verdicts track its own prompt's rubric far above a mismatched one, and which predicts the human
better than that rubric does.* Computed by this round's `run.py`, both halves are resolved —
+0.2961 [+0.2744, +0.3166] and +0.0578 [+0.0502, +0.0658]. The step is the one thing this round left
as a point estimate: **build the null distribution for Q1's specificity**, comparing `vs full` against
the distribution of `vs (any other arm's class)` over the 20 objects, so the phrase "its own rubric"
carries an interval instead of a gap of +0.0487.
