# R605 · Clause ②'s comparator cannot be rebuilt from this repository — and neither can 97% of the evidence

**Decision this makes safe:** whether R604's open question can be closed by reading code. **It cannot
— the code is not here.**

| | |
|---|---|
| scored artifacts in `corebench/results/sat_*.npz` | **101** |
| with a builder anywhere in the tree | **3** |
| **without** — including **②'s comparator** | **98 (97.0%)** |

**WORLD B UNBUILDABLE, TYPICAL.** `sat_genericpool16.npz` has no builder here — **and neither do
`sat_coval_core.npz`, `sat_gen.npz`, `sat_generic.npz` or 94 others.** ⭐ **This is not a defect
specific to ②: the construction step for the whole scored evidence base lives outside this
repository.**

## ⚠ The instrument is weak, and that changes how the 97% reads
The positive control passed by finding **3** builders — enough to prove the detector *can* see one,
**not** enough to prove it sees most. Indirect construction (an f-string, a loop over stems) is
invisible to it.

⭐ **So 97% is an upper bound reported by a proven-able-to-see detector, not by a proven-sensitive
one** — and the honest claim is *"the construction is not locatable here"*, never *"no construction
exists"*. The distinction is the same one §4 draws between a zero and silence, applied to my own
search rather than to a corpus.

## What this does to R604
R604 found `POOL[0:4]` in **0** scoring artifacts against `genericpool16` in **13**, and left open
whether they name one arm. **Reading the construction was the proposed route to close it. That route
does not exist in this tree.** ⭐ And R454's docstring already distinguishes the objects:
> *"`genericpool16` k=16 on all 968 prompts; **`full` is the RUBRIC (prompt-SPECIFIC)**"*

**So the page describes ②'s baseline as the released pool's first four, while the scored comparator is
a generic 16-criterion pool whose assembly is not in the repository.** Whether those are the same
object is now **UNVERIFIABLE HERE** — not merely unverified.

## ⛔ Check #204
R604 closed with two unchecked claims. *"assembled **in corebench**"* — **a location I never
verified, and wrong: nothing in the tree assembles it.** And *"the **scorer** can settle what a search
cannot"* — **reading construction code settles the construction, never that the committed numbers
came from it.** That is §4's *determinism read as currency*, elided in one clause.

## Controls
| control | returned |
|---|---|
| **positive** — the detector must find ≥1 builder | **3 of 101** — PASS, and reported as the weakness it is |
| **negative** — an invented artifact name | **0 builders** — PASS, absence is detectable |
| **placebo** — a file certainly written in-tree (`baseline_name.json`, written by R604's own `run.py`) | **1 builder** — PASS, the detector sees a producer it should |

**MULTIPLICITY:** 101 artifacts × 779 scripts + 3 control checks.

**IMPOSSIBLE, named:** even a *found* builder proves the **construction**, not that the **committed
bytes** came from it. That needs a write-time hash **these artifacts do not carry.**

## The sentence I can no longer write
> *"read how `genericpool16[:4]` is assembled and compare it to the page's wording."*

**There is nothing in this repository that assembles it** — and that is true of 98 of its 101 scored
matrices.

## NEXT
Three artifacts **do** have builders, and they are the only place where a construction and a committed
matrix sit side by side in this tree. **Check whether those three carry a recorded source hash** — if
they do, the corpus already has the mechanism that would make the other 98 checkable, and the gap is
adoption rather than design; if they do not, then even where the code is present the bytes are
unattributable, and that is a different and larger claim about the evidence base.
