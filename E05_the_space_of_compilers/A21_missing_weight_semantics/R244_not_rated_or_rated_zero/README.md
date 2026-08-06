# R244 — "not rated" and "rated zero" are indistinguishable, and every weighted number here picked one

**Arc E05·A21.** The blind arm (R235, seed 29, no sight of E05) reported the weight matrix is
sparsely filled and that an exact `0` is essentially never used, so a criterion someone **did not
rate** and one they **rated zero** cannot be told apart. **A number from another arm is a hypothesis,
not a fact** — this verifies it first, then tests what it does to my own central claim.

## (a) Verified independently

| | R235 said | measured here |
|---|---|---|
| fill rate | 0.397 | **0.3786** (102,147 filled of 269,806 criterion×rater cells) |
| exact zeros | 1 in 102,147 | **1 in 102,147** — exactly |

Most common values: `+10 ×13,048 · +5 ×10,025 · +8 ×8,532 · +6 ×7,905 · +4 ×7,599`. **People use the
scale, and they never use its midpoint.** Verified.

## (b) What it does to R231, E05's central measurement

| reading | core | floor | core − floor | floor [min,max] |
|---|---:|---:|---:|---:|
| **exclude missing** (what every E05 round used) | 0.3864 | 0.3842 | **+0.0021** | [0.3796, 0.3923] |
| **missing = 0** | 0.4380 | 0.3319 | **+0.1061** | [0.3262, 0.3388] |

**The two readings move the answer by `0.1040` against a floor draw spread of `0.0127`.**

Under one reading the official core is *at* its floor; under the other it is **clearly above it.**
Nothing about the data changed — only what an empty cell is taken to mean.

## The bug this round found in itself, and how

The first run gave a floor of **0.1826** where R231 measured **0.3836** on a nominally identical
design. The core cell reproduced R231 *exactly*, so the fault had to be the floor — and it was:

```python
W[list(rg.choice(...)), None] * S[list(rg.choice(...))]     # TWO independent draws
```

`rg.choice` called **twice in one expression**, so the "random 4-criterion arm" multiplied one random
subset's **weights** by a **different** random subset's **satisfactions**. Not a random arm — a
scrambled object. **An arithmetic check against a prior round's number is what surfaced it**, and it
is now printed before any result is read.

## Verdict

> **E05's scope lines are incomplete.** Ten rounds — R220, R221, R222, R223, R228, R230, R231, R237,
> R239, R243 — use `W = mean of the scores that exist`. That is a **choice**, it is worth `0.1040` on
> the central quantity, and **no round declared it.**

`realstat` G1: *"State population · instrument · baseline · regime for every number. Eleven of twelve
retractions in one audited programme were a correct number reported without the scope over which it
held."* **This is the twelfth shape of that, found by an arm that could not see any of them.**

## What cannot be settled

**Which reading is correct.** The release does not say, and no analysis of the release can — that is
partial identification, and the honest output is **both numbers**, not a preference. R235's grid
shows the choice is worth more still under a signed baseline (η 0.10 vs 0.25), a configuration E05
never used.

## The sentence that can no longer be written

*"The official core scores 0.3864 against a floor of 0.3836."* — without adding **"treating an
unrated criterion as absent rather than as zero."*
