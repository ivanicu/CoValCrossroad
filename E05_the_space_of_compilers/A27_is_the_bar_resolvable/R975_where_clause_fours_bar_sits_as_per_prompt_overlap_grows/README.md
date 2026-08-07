# R975 · clause ④'s bar is variance-limited, and the level it was celebrated for is the one overlap defeats

**THE DECISION THIS MAKES SAFE.** Whether clause ④'s exclusion power can be stated as a bound on
the *mean*. It cannot — the binding region depends on per-prompt shape, so any statement of ④'s
reach has to carry an overlap scope or it is unscoped.

---

## What the previous round's closing sentence said, and what its code did

`54bab0e3` closed with: *"The plants were built by subtracting a CONSTANT from the floor, so they
are below it uniformly. Whether ④ removes an arm below the floor on average but ABOVE it on some
prompts is not measured."*

Read from the object — `R821 run.py:146-152` — the plant is `v[hurt] = 0.0` on a random subset. It
**zeroes** a fraction and leaves every other prompt **exactly equal** to the floor. Not a constant
subtraction, and not uniform. **The sentence mis-describes its own round twice**, and the gap it
names is narrower than it says: *equal to* is not *above*, and prompts strictly above the floor were
never built. Building to that description would have replicated an existing plant.

## The design

At a **fixed** mean deficit δ, sweep φ — the share of prompts on which the plant is **strictly
above** the floor — with the deficit restored by stepping other prompts down. Plants live on the
**constructible lattice {0, 1/6, …, 1}**, because a per-prompt A2 is agreement over 6 pairs and an
off-lattice plant is an object no scoring function can emit.

⚠ **The point estimate is a DERIVATION, not a measurement.** ④'s statistic is `mean(v − floor_v)`;
pinning `mean(v)` pins it exactly. It could not have come out otherwise. **Only the bootstrap
interval was free to move**, so the whole question is whether ④'s power is mean-determined or
variance-limited.

## The result — WORLD B, VARIANCE-LIMITED

**59 of 63 cells removed. Four survivors, every one at δ = 0.01:**

| δ | φ | seeds surviving | prompts strictly above floor | margin | `hi` |
|---|---|---|---|---|---|
| 0.01 | 0.40 | 1 of 3 | 387 | −0.00999 | **+0.00034** |
| 0.01 | 0.50 | **3 of 3** | 484 | −0.00999 | +0.00138 … +0.00207 |

At δ = 0.02 and δ = 0.05 removal holds through φ = 0.50, so **φ\* is δ-dependent** and for δ = 0.01
sits between 0.30 and 0.50.

**The mechanism, and it is monotone at every δ** — CI half-width against φ:

| φ | δ=0.01 | δ=0.02 | δ=0.05 |
|---|---|---|---|
| 0.00 | 0.00255 | 0.00339 | 0.00471 |
| 0.10 | 0.00551 | 0.00588 | 0.00686 |
| 0.30 | 0.00844 | 0.00881 | 0.00933 |
| 0.50 | **0.01136** | 0.01208 | 0.01424 |

**4.5× at δ = 0.01**, with the mean pinned to **6.94e-18**.

⭐ **The sharpest version.** `54bab0e3` singled out δ = 0.01 as the achievement — *"finer than the
design's own half-split noise floor of 0.0067."* **That is exactly the level overlap defeats.** An
arm that beats the floor on half the corpus and still carries a 0.01 mean deficit is not removed by
④ on this release.

## Controls, and what they returned

| control | result |
|---|---|
| **OBJECT** | 968 prompts, floor `0.455679` — reproduces R821's committed value exactly. ⛔ Caught a real defect on first run: without R821's `p in base` filter the population was **1,078** prompts at floor `0.451517`. |
| **POSITIVE** | R821's zeroing ladder reproduced — δ ∈ {0.01, 0.05, 0.10} all removed, δ=0 kept |
| **PLACEBO** | floor vs itself: margin exactly 0, not removed |
| **NEGATIVE (the derivation)** | margin spread across φ within a δ: **6.94e-18** |
| **NOISE FLOOR** | measured half-width at φ=0, δ=0.01: **0.002583** |
| **SEEDS** | 3, reported per seed, never averaged — and they disagree at φ=0.40, which is the finding's own boundary |

⛔ **The negative control failed on the first run, and it failed for its own reasons.** v1 compared
the *achieved* margin to the *nominal* −δ at 1e-9. The lattice makes that impossible: 0.05·968·6 =
**290.40 steps**, an arm can take 290, so the achieved deficit is 0.04993113 and the "drift" of
6.89e-05 matched the quantisation arithmetic to the digit. **Its two sides were not the same
object.** The claim is about φ, so the control had to be about φ: within each δ, the margin must not
move as φ grows. The script printed `UNVERIFIED` rather than the world until that was repaired,
which is the conditional-kill form working as intended.

## What this now rests on

- R803's judge-free floor, rebuilt from `data/comparisons.jsonl` and checked against its committed value
- the lattice constraint, which is what makes the plant an admissible object rather than an arbitrary vector
- one release. **Whether φ\* is a property of clause ④ or of this corpus's per-prompt variance is
  not identified here** and needs a second release.

## Alternatives considered

**Sweep δ finer around 0.01 to locate φ\* precisely.** Deferred: the seeds already disagree at
φ = 0.40, so the boundary is inside the design's own seed spread and a finer δ grid would report
precision the seeds do not support.

**Push φ above 0.5.** Rejected as uninformative: an arm above the floor on most prompts with a
negative mean is increasingly a pathological object, and the clause's failure is already
demonstrated at φ = 0.5.
