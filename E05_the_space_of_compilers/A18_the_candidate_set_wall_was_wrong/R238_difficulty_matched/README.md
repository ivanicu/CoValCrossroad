# R238 — the control I proposed for R233, and it does not control anything

**Arc E05·A18.** R233 measured a transport signal and I refused it, naming a confound: *the fresh
responses are more homogeneous, therefore easier, and the floors prove it.* R238 tests that
explanation. **It does not survive.**

## The positive control failed, so the kill is `UNVERIFIED`

Difficulty was operationalised as **separation** — the smallest pairwise gap in Full's own score
vector, normalised by its range, on the reasoning that a well-separated ordering is robust to
dropping criteria and a bunched one flips. For that to be a control, difficulty must **predict**
`core − floor` within an arm.

| arm | `core − floor` by stratum (easiest → hardest) | monotone in |
|---|---|---|
| original | −0.022 · −0.077 · +0.013 · −0.047 | **1 of 3 steps** |
| fresh | +0.118 · +0.006 · −0.016 · +0.138 | **1 of 3 steps** |

**It does not predict.** So stratifying on it is not a control, and the negative control confirms the
stratification did nothing at all: shuffled difficulty labels give `+0.0945` against the
unstratified `+0.0946`, and the matched estimate is `+0.0947`. **Shrinkage: −0%.**

## And my stated mechanism for the confound is not supported

| | median separation |
|---|---|
| original | **0.0961** |
| fresh | **0.0901** |

**The fresh responses are not better separated — they are marginally *worse*.** The homogeneity story
I gave for R233's floor difference has no support from this measure.

> I named a confound, gave it a mechanism, and the mechanism does not hold. The floors do differ
> (≈0.026), so *something* makes fresh easier for random selection. **It is not separation, and I do
> not know what it is.**

## What this changes about R233

R233 stays **`UNVERIFIED`** — but the reason is now different and weaker than the one I published one
round ago:

- **what I said:** the floors caught a confound, and the arms are not comparable
- **what is true:** the floors differ, I proposed a mechanism, **and the mechanism failed its own
  test.** R233 is unverified because **no valid control has yet been applied**, not because a control
  killed it

That is a meaningful downgrade of my own reasoning, not of R233's number. The difference-in-differences
of **+0.095** is still there and still unexplained in either direction.

## What a real control would need

A difficulty measure that **passes its own positive control** — i.e. one that demonstrably predicts
`core − floor` within an arm before being used to match across arms. Candidates not yet tried:
criterion count `n`, response length dispersion, the entropy of Full's score vector. **Each must be
validated as a predictor first.** Using an unvalidated stratifier is how a control becomes theatre,
and this round is the demonstration.

## The sentence that can no longer be written

*"The fresh responses are easier because they are more homogeneous."* They are not more separated,
and the mechanism I asserted for R233's floor gap does not hold.
