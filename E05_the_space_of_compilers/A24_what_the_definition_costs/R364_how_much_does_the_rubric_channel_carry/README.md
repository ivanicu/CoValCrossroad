# R364 — the rubric channel is open and carries nothing measurable

**The decision this makes safe:** *does R363's channel compromise the published five?* **No, to a
stated bound.** The wording of clause ③ was wrong and stays corrected; the arms are not.

## Result — `W_CHANNEL_EMPTY`. Four controls PASS. Two runs byte-identical.

R363 showed the channel **exists** (95.3% annotator overlap, sham 0.016, 58×) and deliberately
named its size **unmeasured**. This is the measurement: `topw_k4`'s weights are averaged over a
weight-set that overlaps the evaluation annotators in a controlled fraction, and the arm is scored
against those evaluators only.

| dose | realised overlap | margin (seed 0 / 1 / 2) |
|---:|---:|---|
| 0.00 | 0.000 | +0.0101 / +0.0152 / +0.0164 |
| 0.25 | 0.266 | +0.0122 / +0.0115 / +0.0139 |
| 0.50 | 0.531 | +0.0125 / +0.0139 / +0.0154 |
| 0.75 | 0.803 | +0.0115 / +0.0141 / +0.0158 |
| 1.00 | 1.000 | +0.0136 / +0.0153 / +0.0128 |

**Paired headline, `margin(d=1) − margin(d=0)`:** +0.0035 / +0.0001 / −0.0036 across seeds,
**mean −0.0000 against its own MDE 0.0096.** The three seeds **straddle zero**, which is a stronger
null signature than one point.

## ⚠ This is a BOUND, not a zero

`topw_k4`'s own margin at dose 0 is **+0.0139**. An MDE of **0.0096** rules out a channel larger than
**~69% of the whole margin** and says **nothing** about a smaller one.

## The instrument that made this unaskable

`corebench/score.py:88 load_targets()` reads `aid = asm.get("annotator_id")` on line **103** and
returns `(ranking, demographics)` — **the id is dropped.** Every round in this campaign uses that
loader, so **no round could have aligned a ranking to the person who wrote the rubric.**

> The question was not overlooked. **The standard instrument had no column for it.**

This round carries its own loader that keeps the id, and that is the only reason the estimand is
identified.

## Controls — and the one I nearly shipped without

| | returned |
|---|---|
| **POSITIVE** — plant a person-specific channel of strength g in the evaluators' own scores | g=0: **+0.0033 not detected** (floor) · g=0.5: +0.0297 **DETECTED** · g=1: +0.0428 · g=2: +0.0537 (ceiling) |
| **SHAM** ⭐ — permute *which annotator's scores carry which id*, within the prompt | **−0.0021 vs MDE 0.0101 — inside.** The dose needs identity |
| **SPLIT** — a dose that does not move never ran | overlap **0.000** at d=0, **1.000** at d=1 |
| **PLACEBO** — same seed, same dose, twice | identical vectors |
| reproducibility | two runs **byte-identical** (`d15bbec2841a`) |

⛔ **v1 had placebo, sham and split — and no positive control.** *A zero from an instrument never
shown to return non-zero is silence, not an acquittal*, and I was one commit from publishing a null
with no demonstrated power. The plant now shows the design **can** see a person-specific channel and
**does not** at g=0.

⚠ The smallest **plant** that was detected is +0.0297, ~3× the MDE. So the formal bound is the MDE
(a calculation from the paired sd); the **demonstrated** sensitivity is at 3× it. Both are stated
rather than the flattering one alone.

## The sham is what makes the null readable

Permuting which annotator's scores carry which id destroys the person-link while preserving the
score distribution, the panel sizes and the arithmetic exactly. It lands **inside** the MDE — so the
dose was measuring identity, and its flatness is a fact about identity rather than about a dose that
never varied.

## What this changes, and what it does not

- **Stays corrected:** clause ③'s wording. R363's census is a fact and the clause as written did not
  describe what the code excludes.
- **⛔ Retracted:** any implication that the published five are compromised. **They are not, at a
  resolution of 0.0096.**
- **Mechanism:** importance scores behave as **prompt-level** information — what this conversation
  calls for — not as person-level. Whose scores are averaged does not move `topw_k4`.

## Register

| criterion | status |
|---|---|
| **a channel smaller than the MDE** | **N/A** — needs more prompts or a lower-variance contrast |
| **other arms** | `coval_core` is not built by this selection rule; not implied by this round |
| **a second judge** | the channel is judge-free (R363) but this **measurement** runs through A2, so it is 2B-scoped — stated, not silently generalised |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"the rubric channel means `topw_k` is not producible from the conversation alone, so the
> published five inherit it."*

**The channel is open and carries nothing detectable at 0.0096. The first half stands; the second
does not follow from it.**

Artifact: `results/r364_channel_size.json`, source-stamped.
