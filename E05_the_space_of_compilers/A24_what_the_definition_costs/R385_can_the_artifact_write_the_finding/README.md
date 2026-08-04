# R385 — a generated line reaches rank 2 of 46 and names the right round 46% of the time

**The decision this makes safe:** *can the 243 missing findings be filled mechanically?* **As a
draft, not as a publication.**

## Result — `W_PARTIAL`. Four controls PASS. Two runs byte-identical. **No GPU spent.**

| | |
|---|---:|
| top-1 accuracy | **0.457** |
| chance (1/46) | 0.022 |
| **median rank of the true paragraph** | **2 of 46** |
| permutation null | **0.022** — exactly chance |

**21× chance, and still wrong more often than right.** A generated line **narrows the field** without
identifying the finding.

## ⛔ R384's proposed test was void as written

It asked whether *a reader* could tell a generated line from a hand-written one. **I am the reader** —
a judgement I make about text I generated, scored by me, is **self-review, which this campaign treats
as void rather than weak.**

## ⭐ A ground truth already existed

**46 rounds have both a committed artifact and a root-README paragraph that names only them.** So the
question becomes objective: generate a line from the artifact alone, and see whether it can be
**matched back to its own paragraph** among all 46. That answer does not pass through my opinion.

## ⛔ The positive control caught a broken population *before* the measurement

v1 mapped each round to the first paragraph naming it. **A paragraph queried with itself retrieved
itself only 63% of the time** — impossible for a working matcher, so a fact about the **targets**.

Measured: **one root-README paragraph names ten rounds**, and **41 of 84 candidates share their
paragraph** with another. *A retrieval task with duplicated targets has no unique right answer.*
Restricted to rounds whose paragraph names exactly one of them — the only version in which *"its own
paragraph"* is a well-formed object — and the control goes to **1.00**.

## ⛔ My prediction about the arithmetic trap was wrong in magnitude

The docstring says leaving round identifiers in would **force** top-1 to ~1.0.

| | |
|---|---:|
| un-stripped | **0.478** |
| stripped | **0.457** |
| difference | **+0.021** |

**The identifiers were not the dominant signal**, so the precaution changed almost nothing. Taking it
was still right — *a defused trap that turns out to have been small is the only kind you can
measure*, and asserting a magnitude without measuring it is what this round would have published had
the number not been printed.

## Controls

| | returned |
|---|---|
| **RETRIEVAL (+)** ⭐ | a paragraph queried with itself retrieves itself: **1.00** — after the population repair it forced |
| **RETRIEVAL (−)** | random tokens from the corpus vocabulary: **0.022** vs chance 0.022; per seed `[0.022, 0.0, 0.043]` |
| **FORCEDNESS** | the same retrieval without stripping ids, reported **as a number** rather than asserted as a precaution |
| **PERMUTATION** | **0.022** — names the world it excludes: *"any two texts from this corpus overlap enough to match"*. It does not |
| seeds | 3, per-seed values printed |
| reproducibility | two runs **byte-identical** (`0e566ecaa62f`) |

## Register

| criterion | status |
|---|---|
| **the 243 rounds without a paragraph** | **N/A — no ground truth exists for them BY DEFINITION.** Every statement about them is an extrapolation |
| **direction of the bias** | **stated, not left to be found**: these 46 are rounds someone *chose* to write about, plausibly the clearest. **This is an UPPER bound on the 243, never a floor** |
| **whether a generated line is GOOD** | **N/A** — this measures whether it is *about the right round*. Different question, not claimed |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] … take twenty rounds at random, generate the line from their artifacts alone, and
> ask whether a reader could tell it from a hand-written one."*

**The reader is me, so that test was void. Asked objectively, the answer is 46% — enough for a draft
a person corrects, not enough to publish, and an upper bound on the population that actually needs
it.**

Artifact: `results/r385_generation.json`, source-stamped.
