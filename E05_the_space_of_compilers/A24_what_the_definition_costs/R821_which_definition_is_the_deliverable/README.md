# R821 · Which definition is the deliverable — and can clause ④ exclude anything at all?

**E05 · A24 · R821.** Frontier. Two seeds byte-identical: `6bad4c9f0c76ac8c2ef0937de0b78447`.
Source `a6f045b3cf2d`. Population: 968 usable prompts, 58 arms scoreable.

## The decision this makes safe

`DEFINITION.md` has stated **two incompatible definitions for 80 rounds** and says so about itself.
The head conjoins **②∧③∧④** plus size>1. Line 1820 carries *"the definition is **② ∧ ③**"* (R519,
R599), annotated *"the retirement reached the claim table and not this sentence."* Nothing could be
released until one of them is the deliverable.

## What was measured

| | |
|---|---|
| **E1** ④'s exclusion count on the current arm set | **0 of 58** (1 UNVERIFIED: `full_sham`, +0.0047 [−0.0080, +0.0178]) |
| **E2 ⭐** the falsifiability test no round had run | ④ removes planted arms at δ = 0.10 / 0.05 / 0.01 and **not** at δ = 0 |
| **E3** the contradiction, counted with a calibrated search | **3** statements conjoin ②∧③∧④; **1** says ②∧③ |

E1 replicates R440's `0 of 42` and R803's `0 of 27` on a larger arm set. **E1 is not the finding.**
The artifact records `claim_unit = "a CLAUSE"` and `instrument_unit = "an ARM"`, and they are **not
equal** — §4's search-instrument row in one line. Counting arms measures the ARM SPACE; it cannot
measure whether the CLAUSE can bind. Only planting can, and no round in 380 had planted.

## The verdict

**WORLD A — free-but-real.** ④ excludes nothing at home *and* removes every below-floor arm put in
front of it, at a resolution finer than the noise floor (δ = 0.01 removed; half-split sd 0.0067).
It is a clause that has never had to fire, not a clause that cannot.

**So the retirement's stated reason is wrong.** R519 retired ④ as *"identical to ①"*. It is not:
`DEFINITION.md:127` records ① as **DERIVED** — the region where it could bind is *empty by
arithmetic* (`GAP ≥ SLACK` on every arm) — while ④ is **MEASURED**, and R821 shows its binding
region is non-empty and reachable. Two clauses at `0 of N` for opposite reasons. The same file
already draws this distinction at lines 385–393 about ①: *"excludes nothing BUILT" ≠ "excludes
nothing CONSTRUCTIBLE"*, and `0 of 41` is *"a fact about the ARM SPACE rather than about the
clause."* That sentence was sitting eight lines from the clause table for 300 rounds and was never
applied to ④.

**The head stands. ④ is retained. Line 1820's retirement is overturned.**

## Controls

| control | returned |
|---|---|
| PLACEBO | the floor arm against itself: margin **exactly 0** — ④ cannot admit it. PASS |
| POSITIVE | the planted ladder; fires at δ>0, does **not** fire at δ=0. PASS |
| NEGATIVE | each arm replaced by a synthetic arm resampled from the floor's own per-prompt distribution: **−0.00001 ± 0.00525**, real **+0.08188**, outside the null's whole range. PASS |
| NOISE FLOOR | 20 half-splits of `coval_core`'s margin: sd **0.0067** |
| CALIBRATION | the E3 search run where the answer is known, on both sentences, before use. PASS |

## Two degenerate nulls in one round, both caught by R820's assertion on its first live use

- **v1** counted exclusions under a permuted floor → 0 in every draw by construction.
- **v2** used the mean arm margin → `(A2[a]−fp).mean() = A2[a].mean() − fp.mean()`, and a permutation
  of `floor_v` has the *same mean exactly*. **I replaced one permutation-invariant statistic with
  another.**
- ⭐ **The derivation I should have run instead of either, in three lines:** ④'s statistic is a
  difference of corpus means, so it is permutation-invariant **by algebra** (checked: max |Δ| over 20
  permutations = **0.000e+00**). **A permutation null is structurally unavailable for clause ④** —
  not a coding defect but a fact about the clause: ④ cannot see which prompt the floor came from.
  The admissible negative control resamples the arm, not the floor's pairing.

## Also caught, and worth more than the fix

The first run printed E3's counts **one line below declaring its own instrument uncalibrated** —
§4's *"the verdict string is not a computation"*, committed against a check I had just written. The
counts are now **withheld**, not printed with a caveat. The calibration failed because my literal
carried the asterisks inside the phrase (`the definition is **② ∧ ③**`) where the file has them
outside (`**SUPERSEDED — the definition is ② ∧ ③**`).

## What this round cannot do

| criterion | requires |
|---|---|
| independently replicated | a second release; `--fit-parity` splits annotators, not corpora |
| construct validated | an external gold standard for "core"; A2 is the only target on disk |
| cross-model / cross-dataset | a second site |
| causally identified | ④ is a definitional clause — there is no mechanism to intervene on |
