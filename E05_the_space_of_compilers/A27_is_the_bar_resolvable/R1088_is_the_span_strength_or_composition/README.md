# R1088 — the driver is **proximity**, not strength; and **no single subset** carries the span.

**The decision this round makes safe:** whether resolvability's `[2, 14]` span calls for a repair
aimed at comparator *quality* or at comparator *identity*. **Neither.** Both plants at the extremes
of the score range flip **0** arms, and removing any one of the 15 subsets leaves the maximum at 14.

## ⛔ First, the regression R1087 proposed is a trap, and the round says so before running it

R1087's NEXT proposed regressing each family's exclusion count on the mean score of its members.
**The 32,767 families are subsets of the same 15 objects — `n_eff = 15`, not 32,767.** A correlation
over the family space would quote a CI narrower than the design supports by ~√2185.

**MDE for |r| at n = 15 is 0.669** (Fisher z, two-sided α = .05, power = .80). Stated before the
number, and it governs the reading.

⭐ **An exact route needs no inference at all.** Under the every-comparator rule admission is an
**intersection** over members, so `d_res(F) = |∩ relaxed_j| − |∩ strict_j|` is a **deterministic**
function of the 15 per-subset columns — there is no family-level randomness to model. That is a
derivation, labelled, and it is why the decomposition below is exact rather than estimated.

## ⭐⭐ The finding: a flip needs PROXIMITY, and my own world A had the wrong mechanism

A "flip" is an arm the **point estimate** admits and the **2.5th percentile** does not — so it
requires the arm to sit *close enough* to the comparator that the bootstrap interval straddles zero.

| plant | position | solo flips |
|---|---|---:|
| **far** | constant at the minimum of the whole score matrix | **0** |
| **near** | constant just below the arms' mean | **8** |

**Both extremes flip nobody**: a comparator far below every arm is beaten *resolvably* by all of
them; one far above is beaten by none. **"Weaker admits more" was never the mechanism** — the plants
are what showed it, and the first two versions of this control could not have.

## Q1 · Exact decomposition — world C

Full space: `[2, 14]` over 32,767 families. **Removing any single subset leaves the maximum at 14.**

| removed | strength | size | solo flips | max without it |
|---|---:|---:|---:|---:|
| `(3,)` — **the weakest** | 0.4622 | 1 | 2 | **14** |
| `(0,)` | 0.4828 | 1 | **14** | **14** |
| `(1,2)` | 0.4883 | 2 | **14** | **14** |
| `(1,3)` | 0.4848 | 2 | **14** | **14** |
| `(0,1,2,3)` — the strongest | 0.5023 | 4 | 7 | **14** |

⭐ **World A (strength) is KILLED** — removing the weakest changes nothing. **World B (identity) is
KILLED too** — the carrier list is **empty**, because **three** subsets reach 14 solo, so no single
removal can lower it. **World C: the span is a redundant joint property of the space.**

## Q2 · The correlation, underpowered by design and reported against its MDE

| quantity | value |
|---|---:|
| `r(strength, flips)` | **+0.3246** |
| MDE at n = 15 | 0.6689 |
| permutation band (95%, 2000 perms) | `[−0.5344, +0.5173]` |
| **verdict** | ⚠ **UNRESOLVED at this n** |
| SHAM `r(size, flips)` | +0.0504 |
| CONFOUND `r(strength, size)` | **+0.8390** |

⚠ **Below the MDE and inside its own permutation band — that is UNRESOLVED, never "no
relationship".** And note the point estimate's **sign is positive**: *stronger* comparators
associate with *more* flips, the opposite of world A's prediction — consistent with the proximity
mechanism, since the stronger subsets sit nearer the arms.

⚠ **Strength and size are confounded at +0.84**, measured rather than named, which is why the SHAM
against size is reported beside it.

## Controls — 6, all green, after two rebuilds

| control | result |
|---|---|
| POSITIVE a NEAR plant flips arms; a FAR one flips none | PASS (8 vs 0) |
| POSITIVE the near plant lands inside the real flip range | PASS |
| g=0 adding a column never lowers the space maximum (a superset) | PASS |
| g=0 identical comparators give identical flip counts | PASS |
| PLACEBO the strict variant against itself flips nobody | PASS |
| NEGATIVE the permutation band brackets zero | PASS |

⛔ **Two of these could not fail as first written.** ① *"a strong plant does not raise the space
maximum"* — adding a column makes the space a strict **superset**, so the maximum can only rise or
stay, and the criterion held whatever the plant was. ② Rebuilt as a solo comparison, both extreme
plants returned **0**, which looked like a broken control and was in fact the mechanism. §4's
*control that cannot PASS*, twice, in the round that needed the plants to mean something.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| a well-powered correlation | **N/A** | more than 4 universally-available criteria; `2⁴−1 = 15` is a hard cap on the population |
| any statement about the **released** comparators | **N/A** | they are not blind subsets (R1087's standing limit) |
| separating strength from size | **N/A here** | they correlate at +0.84 in this space; it would need subsets that vary one while holding the other |
| cross-release | **N/A** | a second release with its own blind space |

`run.py` · `results/span_strength_or_composition.json`
