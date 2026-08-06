# R838 · all 45 pairs measured, because the filter I built rested on an unmeasured bound

**The decision this made safe:** whether R835's ordering contains a ranking. **It does not — it
contains two groups**, with exactly **one** resolvable boundary in 45 adjacent pairs.

Design in `PREREGISTRATION.txt`, committed before `run.py` ran.

## The filter I rejected, and why

R837 measured three true MDEs (0.0118 · 0.0104 · 0.0221). I immediately built a filter — *"a pair
can only separate if gap > 2 × 0.0104"* — leaving **2 of 45** worth measuring and calling the rest
forced.

⛔ **That assumes `MDE ≥ 0.0104` for every pair, and I never measured it.** `MDE = ZEFF·sd(d)/√n`, so
two arms differing **systematically but slightly** have a small `sd(d)`, a small MDE, and could
separate on a small gap. **R836 retracted a null resting on an unmeasured resolution; this is the
same move one round later, in the opposite direction.** The recomputation costs seconds per arm.

## Result

| | |
|---|---|
| pairs measured | **45** |
| **SEPARABLE at the true MDE** | **1** — `gen` vs `random_k12_s0`, gap **+0.0347**, MDE **0.0118** (**2.9×**) |
| pairs the filter would have skipped that separate | **0** |
| **smallest measured MDE** | **0.0000** — the filter assumed ≥ 0.0104, **assumption FALSE** |
| **pairs whose true MDE is below 0.0104** | **27 of 45** — ⚠ **corrected from 25**, which was the count with `mde > 0` and silently excluded the two zero-MDE pairs while the sentence said *below* |
| controls | `oracle_k4` vs `generic` **+0.0759 / 0.0106 SEPARABLE** ✓ · arm vs itself **sd exactly 0** ✓ · three seeds byte-identical ✓ |

**W-FILTER-WAS-SAFE.** ⭐ **The filter's premise is false for 56% of the population and its conclusion
is right for 100% of it** — because where the MDE is small the gap is small too. That is the cleanest
available demonstration of *right by luck*, and the smallest-MDE check is what turns "by luck" from a
hedge into a measurement.

## Two degeneracies, checked and harmless here

`random_k4_s1` vs `random_k4_s1_ctlS1` and `random_k4_s0` vs `random_k4_s0_ctlS0` give **sd exactly 0
over 968 prompts** — they are **duplicate arms** in R835's ordering. Their gap is also exactly 0, so
`|gap| > 2·MDE` is `0 > 0` → False. **Pairs with a degenerate MDE and a nonzero gap: 0**, so the test
never fires spuriously — but a future ordering containing near-duplicates would need that guard.

## The substantive finding

**One separable boundary in 45.** The ③-admissible ordering is **not a ranking** — it is the
substantive label-free arms above the random cluster, and everything inside each group is noise at
this design's true resolution.

## NEXT

R835's published table carries bounded MDEs for all 45 pairs; the measured ones now exist beside it
in this artifact. Replacing them in place would make the two tables agree, and the pairs where they
disagree by more than 2× are the ones a reader would otherwise have to reconcile by hand.
