# R451 · the extension is a **ball around one point** — and R450's optimism was too kind

**The decision this round makes safe:** whether R450's *"the extension of 1 is a fact about which
arms were built"* survives. **It does not, as written.** `W-BALL`.

## ⛔ The announced step was forced by a table I committed last round

R450 closed proposing *"score `r=4` with `a=4..12`, see whether admission survives padding to 8."*
Its own grid has `r=4, a=4` → m=8, share **0.9793** against m=4's **0.9841**. **Padding to 8 is
admitted and the size caveat holds.** *Nineteenth announced step checked.*

## ⭐ What R450 was not entitled to

R450 read a graded neighbourhood as evidence of strictness. **But every admitted object in that grid
shares criteria with the released core** — `r > 0` by construction. *A ball around one point is not
a category with members.* The question ~50 rounds never asked:

> **has anything DISJOINT from the released core ever been admitted?**

⚠ A bare *no* would be **silence**, because nothing established that a disjoint object *can* be
admitted. That control is the round's centre of gravity.

## Controls — the oracle is what makes the zero a measurement

| control | returned |
|---|---|
| **POSITIVE** — oracle pool pick (overlap 0, *uses the answer*) | **1.0000** ✅ *a disjoint object CAN be admitted* |
| …fails at g=0 — same selector, objective destroyed | **0.0932** [0.0599, 0.1286] ✅ |
| NEGATIVE — anti-oracle (worst pick) | **0.0000** vs floor 0.2198 ✅ |
| BAND — floor < threshold < ceiling | 0.2198 < 0.80 < 1.0000 ✅ |

## Result — every disjoint object, m=4, admitted or not

| object | share | basis |
|---|---|---|
| `generic` | 0.7154 | provenance ⚠ **prompt-BLIND** |
| `pool_fixed_s0` / `s1` / `s2` | 0.6247 / 0.3038 / 0.0033 | by-construction, prompt-blind |
| `pool_random_perprompt_s0..2` | 0.1286 / 0.0912 / 0.0599 | by-construction, prompt-**varying but random** |
| **`gen`** | **0.0038** | provenance — **the only content-driven one** |
| `core_criteria_wrong_prompt_s0..2` | 0.0000 | by-construction (sham) |
| `gen_sham` | 0.0000 | provenance |
| *ORACLE* | *1.0000* | *control, not evidence* |

**The only hindsight-free, content-driven, disjoint object ever built scores 0.0038 — while the
oracle over that identical space scores 1.0000.** The space contains admissible objects. Nothing we
can build finds one.

## ⚠ The pre-registered threshold is mine, so the verdict is swept rather than defended

| t | all objects | prompt-varying candidates |
|---|---|---|
| 0.50 / 0.60 / 0.70 | W-DISJOINT | **W-BALL** |
| **0.80** *(pre-registered)* | **W-BALL** | **W-BALL** |
| 0.90 | W-BALL | W-BALL |

**The `all objects` verdict is threshold-sensitive and hinges entirely on `generic` at 0.7154 — which
is prompt-BLIND, a member of the same family as the reference class, so its share is a within-family
comparison and near-circular.** The candidate-core verdict is **W-BALL at every threshold tested**.
That is the robust half and it is the one the conclusion rests on.

## ⛔ Two defects in my own instrument, caught in-round

1. **The g=0 control was unreadable and wrong**, returning `W-BLIND` on controls that are fine. It
   permuted the objective and then indexed through the permutation. **An argmax over a shuffled
   objective *is* a uniformly random index** — destroying the objective and picking at random are the
   same operation. Saying it once, simply, was the fix.
2. **A category label was inflated.** `pool_random_perprompt` varies per prompt, but by a random
   index, not by the prompt's **content**. Calling it prompt-specific widened the class. Both are
   reported: the looser one is *conservative* here (it scores higher), so W-BALL surviving under it
   is the stronger statement.

## What this does and does not overturn

- **Overturns:** R450's *"a fact about WHICH ARMS WERE BUILT"*. Prompt-specific arms **were** built.
  They fail. The neighbourhood is real but it is entirely a neighbourhood **of one released point**.
- **Survives:** R450's measurement itself — the `r`-ladder, the 98.6%/1.0% split, both anchors.
  The perturbations *are* admitted; they are just not independent members.
- **Does not establish:** that no disjoint core exists. The oracle proves the space is non-empty.
  **What is measured is our generators, not the category** — R433's verdict, now with the ceiling
  attached.

## Impossible here, named

- **text-level overlap for `gen`/`promptecho`** — needs criterion *texts* aligned across files; the
  satisfaction npz carries indices only. Reported as provenance-disjoint with the caveat attached.
- **whether a disjoint object is "really" a core** — needs a standard outside this definition.
- **a second released core to test disjointness against** — the release ships exactly one.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
