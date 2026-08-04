# R386 — a finding's numbers are 9% in the artifact that produced it

**The decision this makes safe:** *should drafts be generated for the 243 rounds with no finding
site?* **No.** A generated draft would be quantitatively empty. **The 243 is a debt only writing can
pay.**

## Result — `W_NUMBERS_COMPUTED_IN_PROSE`. Two controls PASS. Two runs byte-identical. **No GPU spent.**

| per-round recall of a paragraph's numbers in its own artifact | |
|---|---:|
| **median, numbers ≥ 3 characters** | **0.091** |
| permutation null (random other artifact) | **0.000** |
| median over **all** numbers | 0.500 |
| rounds sharing **no** long number with their artifact | **18 of 41 · 44%** |
| rounds where every long number is present | 3 of 41 · 7% |

`p10 0.00 · p25 0.00 · p50 0.09 · p75 0.40 · p90 0.67`

## ⛔ R385's proposed design is not constructible here, and the reason is leakage I caused

It asked me to **hand-write** findings from artifacts without seeing the generated line. **I would
write them — and I have been appending to the root README all session**, the document that holds the
targets. That arm is contaminated by knowledge of the answer and would win by construction; worse,
*"I did not use what I remember"* is **unverifiable from outside**, which this project treats as void.

A clean-context writer would fix it and is not available here. **The arm is named as impossible, not
approximated.**

## ⭐ The decision was still answerable without writing anything

The question behind it: *can generation carry a finding's content, or only gesture at it?* **A
finding's checkable content is its numbers.** So: what share of a paragraph's numbers appear in the
artifact? No vocabulary of mine, no text produced.

## ⛔ The collision control is the whole result

| | recall |
|---|---:|
| over **all** numbers | **0.500** |
| over numbers **≥ 3 characters** | **0.091** |

**Without the split I would have reported 50% and called generation a partial success.** Small
integers — `0`, `1`, `2`, `3` — collide by accident between any two numeric texts. Long decimals do
not. **Both printed, neither hidden.**

And the permutation null lands at **exactly 0.000**: pairing a paragraph with a *random* artifact
shares no long number at all. So the 0.091 is **provenance, not collision** — it is small *and* real.

## What this does to R385

R385 read 46% top-1 as *"a draft a person corrects."* **A draft carrying 9% of the finding's numbers
is not a draft of the finding.** The retrieval accuracy came from vocabulary and verdict strings, not
from quantitative content — which is exactly the gap between *being about the right round* and
*stating what the round found*, and R385 said it was not claiming the second.

## Controls

| | returned |
|---|---|
| **PERMUTATION** ⭐ | median recall **0.000** across 3 seeds against observed **0.091** — names the world it excludes: *"any artifact contains any paragraph's numbers, because numbers are common."* It does not |
| **COLLISION** ⭐ | 0.500 all vs 0.091 long — the control that decides the reading |
| **POPULATION** | 6 rounds excluded for having only short numbers, 0 for having none — **counted, not dropped silently** |
| **SELF** | this round excluded, standard since R382 |
| reproducibility | two runs **byte-identical** (`01a42b39f453`) |

## Register

| criterion | status |
|---|---|
| **the hand-written arm** | **IMPOSSIBLE here** — I would write it, having edited the target document all session. Needs a clean-context writer |
| **whether an absent number is WRONG** | **N/A** — absence bounds what generation can **carry**, nothing about correctness. It may have been computed while writing or cited from another round |
| **the 243 without paragraphs** | **N/A** — no ground truth by definition; this population is the flattering one |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"a generated line … supports a DRAFT for a person to correct."*

**It supports a draft of the round's *identity*, not of its *finding*: 9% of the numbers, with 44% of
rounds sharing none at all.**

Artifact: `results/r386_numeric_recall.json`, source-stamped.
