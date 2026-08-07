# R355 — R332's closure level is the FIRST closed reference, not the lowest SAFE one

**The decision this makes safe:** *may the campaign keep saying "a reference at level L is closed"?*
**Only with an upward-closure test attached.** At 6 of 9 k, references **stronger** than R332's
published closure admit blind sets again.

## Result — `W_NEAR_NEIGHBOUR`. All four controls PASS.

R332's docstring defines closure as *"the LOWEST reference that is closed: **anything stronger is
gratuitous**, anything weaker admits an object the clause exists to exclude."* Its code computes
`closed[0]` — the **first** grid index with rate 0. Those are the same object **only if the closed
region is an upward set.** It is not.

| k | R332 closure | pctile | minimal **safe** | pctile | violations above closure |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.5320 | 75.0 | *unchanged* | | 0 |
| 2 | 0.5528 | 95.8 | *unchanged* | | 0 |
| 3 | 0.5519 | 94.8 | **0.5530** | 96.2 | 2 |
| 4 | 0.5520 | 96.4 | **0.5537** | 98.5 | 3 |
| 6 | 0.5519 | 98.5 | **0.5531** | 99.5 | 1 |
| 8 | 0.5505 | 98.5 | **0.5517** | 99.5 | 1 |
| 12 | 0.5462 | 93.5 | **0.5472** | 96.9 | 4 |
| 13 | 0.5451 | 87.9 | **0.5460** | 94.8 | 7 |
| 15 | 0.5423 | 50.0 | *unchanged* | | 0 |

**18 references above closure admit blind sets, across 6 of 9 k.** Counts are raw blind sets, never
only rates — a rate of 1.2e-4 is **one subset of 8,008** and must be readable as one.

## Why R331 never saw it — the grid is the instrument, again

| grid | cells | total violations |
|---:|---:|---:|
| **9-point** (R331's) | 77 | **0** |
| **45-point** (R332's) | 315 | **18** |
| **91-point** | 591 | **50** |

`IDENTIFICATION` pre-registered that a finer grid can only **add** violations — a coarse grid cannot
see a reference it never evaluates — so the measured safe level is a **lower bound**. Observed
0 → 18 → 50: **CONSISTENT**. This is the third time on this campaign that grid resolution changed a
published number (R331→R332 moved the closure level itself), and the first time it changed a
**qualitative** claim.

## The mechanism is R331's own, on the axis R331 never applied it to

`rate()` admits on `(e > 0) & (|e| >= mde)` where `mde` is the sd of the **per-prompt difference**.
So a reference with a **higher mean** but a different **per-prompt profile** can have a smaller
paired sd against some blind set and admit it. R331 found exactly this and wrote it down —

> *"A paired MDE is a property of the PAIR, not of the design. A near-neighbour has a small paired
> sd, so it clears its own resolution on a tiny gap."*

— **about arms.** R332's instrument runs the same comparison on the **reference** axis and inherited
the property without inheriting the warning.

| k | pairs | observed shared | own-k null | excess | pigeonhole floor |
|---:|---:|---:|---:|---:|---:|
| 3 | 2 | 2.00 | 1.00 | **+1.00** | 0 |
| 4 | 4 | 2.75 | 1.00 | **+1.75** | 0 |
| 6 | 1 | 4.00 | 1.67 | **+2.33** | 0 |
| 8 | 1 | 7.00 | 3.67 | **+3.33** | 0 |
| 12 | 7 | 10.14 | 9.10 | **+1.05** | 8 |
| 13 | 10 | 11.40 | 10.63 | **+0.77** | 10 |

**Pooled excess +1.187 against its own MDE 0.415** (n=25 pairs, sd 0.741) — **RESOLVED**, and
positive at **all six** violating k independently, which is the stronger statement.

## Controls

| | returned |
|---|---|
| **PLACEBO** — every reference against itself, 315 cells | **0** self-admissions |
| **POSITIVE** — the weakest reference (rate 0.982) injected *above* `first0` | **flagged** |
| **g=0** — the class-max reference injected in the *same slot* | **not flagged** — it fires on rate, not position |
| **NEGATIVE / SYNTHETIC** — the rival world **built**: every reference flattened to a constant vector at its own mean, making admission a pure threshold and upward-closure algebraic | **0 violations at all 9 k** |
| reproducibility | two runs **byte-identical** (`6fd2ae84d668`) |
| multiplicity | 77 / 315 / 591 (k, grid, candidate) cells; violating **and** closed cells printed |

The synthetic control is the load-bearing one: it names the world the finding excludes and
**constructs** it rather than imagining it. Violations survive the real profiles and vanish when the
profiles are flattened — so they are caused by the per-prompt profile and by nothing else.

## ⛔ My own kill was unfit, and is replaced rather than retuned

v1's mechanism arm read `shared_violating >= shared_baseline + 1.0`. Two defects, both in the
comparison and **neither in the data**:

1. **Two weightings compared as one object.** The baseline accumulated once per violating
   *reference*; the statistic once per (reference, admitted set) *pair*. v1's own permutation null —
   which carries the statistic's weighting — sat at **7.16–7.36** against the **6.68** the kill was
   using. It was reading a 0.6-criteria weighting artefact as mechanism.
2. **A raw shared count is not comparable across k.** Two k-subsets of a 16-pool share at least
   `2k−16`, so at k=13 every pair shares ≥10 **by pigeonhole** while at k=3 the maximum is 3.
   Pooling raw counts measures *which k violated*, not how similar the pairs are.

The replacement is not a threshold chosen to reach a verdict: it is **this campaign's standing
admission rule** applied to the mechanism statistic — excess over that k's own null, pooled, cleared
against its own MDE. It is **strictly harder to pass** than "+1.0 shared criteria". Per P6 an unfit
check is UNVERIFIED, so **v1's verdict was withdrawn as unearned before v2 was run**, and v2 happens
to reach the same label by a criterion that could have refused it.

**And the third branch was narrowed.** v1 would have printed `W-CHAOTIC` whenever the excess failed
to clear — reading a null as evidence *for* the rival. An excess inside its own resolution is
**silence about the mechanism**. The violation count is a census over an enumerated class and stands
either way; only its explanation was ever at stake in that arm.

## What this does and does not touch

- **Does not touch** R331's headline. R294's published reference sits *below* closure at every k; a
  ceiling that is not upward-closed only makes the safe level **higher**, never lower.
- **Does touch** every "the closure level is L" sentence: at 6 of 9 k, L is **not** the level above
  which the clause is safe.
- **Does touch R354's p99 by direction.** The corrected safe levels sit at p96.2–p99.5, i.e. at or
  **above** p99 at k=6 and k=8. R354 put every k at p99; at two k that is now *below* safe.

## Register — what this site cannot do

| criterion | status |
|---|---|
| **cross-pool / cross-dataset** | **N/A** — one release, one 16-criterion pool. Every level here is a fact about that pool |
| **construct validity** | **N/A** — no external gold standard for "a safe reference" exists; the clause's own words are the only criterion |
| **continuous identification** | **N/A on the grid** — the true minimal safe level over *all* references needs the full class sweep (12,870 rates at k=8). The 91-point result shows the grid has not converged |
| multi-seed | 3 seeds on the permutation null; the enumeration itself is deterministic and reproduces byte-identically |

## The sentence I can no longer write

> *"the closure level is the lowest reference that is closed — anything stronger is gratuitous."*

**Stronger is not gratuitous. At 6 of 9 k it is not even safe.**

Artifact: `results/r355_upward_closed.json`, source-stamped, `sha256[:12] 6fd2ae84d668`.
