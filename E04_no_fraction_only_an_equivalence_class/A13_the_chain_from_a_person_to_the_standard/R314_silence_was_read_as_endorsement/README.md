# R314 — silence was read as endorsement, and the check that noticed blamed the wrong round

**Decision this makes safe:** whether R150's published veto numbers may be cited. **The
distribution numbers may not, at all. `served_delta` may, at 3.4× its published magnitude.**

## How it surfaced

`assurance/consistency.py` had been exiting 1 on every run with:

```
[FAIL] full-rejection rate: r150 distribution vs r151 direct count
       0.0105 vs 0.03895   |diff| 0.02845   tol 0.003
       "…a larger gap means one of them filtered silently"
```

Neither filtered silently. `0.0105 × 18562 = 194.9`, and r151 reports **195** full rejections.
**Same numerator, two denominators.** The check compared two rates as if they shared a
population, and its message accused r151 — the *corrected* round. A reader acting on it would
have repaired the correction back into the bug.

## The defect, in the docstring of the function that has it

R150's `parse_unacceptable` says:

> *"an empty set because the person said nothing is unacceptable is a JUDGEMENT; a missing block
> is a MISSING ANSWER, and collapsing them would turn silence into an endorsement"*

and the line beneath it is `if blk is None: return set(), False`. In this release **not-asked is
an empty list, never a missing key** — so that branch fires **zero** times. R150 stated the
distinction exactly and then implemented a test that cannot detect it.

Measured from `data/annotators.jsonl`:

| | |
|---|---:|
| assessments | 18,678 |
| `unacceptable == []` — never posed | 13,672 |
| asked | 5,006 (26.8%) |
| key absent (what R150 tested for) | **0** |
| full rejections, all inside the asked set | 195 |

R150's own header says 18,562 — **116 short of the file**, a third and separate discrepancy.

## Positive control — the decisive one, against a published target

This round's pipeline, run with the defect **re-injected**, scored against R150's committed
artifact rather than against my expectation:

| quantity | R150 published | reproduced | |
|---|---:|---:|---|
| coverage | 1.00000 | 1.00000 | ok |
| testable prompts | 1091 | 1091 | ok |
| change rate | 0.06140 | 0.06141 | ok |
| served_delta | −0.01557 | −0.01557 | ok |

**The reimplementation is faithful, so every difference below is the population, not my code.**

## What changes

| quantity | R150 (all rows) | corrected (asked) | change |
|---|---:|---:|---:|
| P(vetoed nothing) | 0.8285 | 0.3642 | −0.4644 |
| P(rejected all four) | 0.0105 | 0.0390 | +0.0284 |
| coverage | 1.0000 | 0.2680 | −0.7320 |
| testable prompts | 1091 | 322 | −769 |
| change rate | 0.0614 | 0.2081 | +0.1467 |
| **served_delta** | **−0.0156** [−0.0203, −0.0108] | **−0.0528** [−0.0682, −0.0374] | **−0.0372** |

**W-DILUTION.** The 13,672 never-posed rows acted as consent and diluted the veto signal. R150
**understated** the cost of respecting vetoes by 3.4×.

## The distribution numbers are wrong whatever the verdict

`P(vetoed nothing) = 0.83` is not a fact about what people judged — it is a fact about **how
often the question was asked**. Over the asked population it is 0.36. Any sentence of the form
*"N% of people vetoed nothing"* built on R150 is a statement about form-routing.

## Controls

| control | result |
|---|---|
| POSITIVE defect re-injected | reproduces all four published numbers |
| g=0 corrected run | does **not** reproduce them |
| PLACEBO plurality vs itself | exactly 0 |
| NEGATIVE label permutation, 200 seeds | −0.2756, envelope [−0.3037, −0.2509]; observed −0.0528 is **outside**, on the less-harm side |

The negative control's reading is itself a small finding: a chooser blind to which response was
vetoed costs −0.28 of service. The real veto channel costs −0.053, so **vetoes land on responses
people already rank low.**

## ⚠ The negative control was wrong twice, in opposite directions

Both are kept in `run.py` because they are the round's most transferable content.

1. **A no-op.** Permuting *which person* held each veto set leaves the statistic unchanged — it
   reads per-response veto **counts**, invariant to relabelling people. It returned the observed
   value at **sd exactly 0.00000** and printed *"INSIDE the permutation floor"*: a **false
   retraction** of a live result. The zero sd is the tell.
2. **The wrong tail.** The criterion `|observed| > |permuted| + 1.96·sd` presupposes a null near
   zero. This null sits at **−0.276**, because a label-permuted chooser picks low-ranked
   responses by construction. A one-sided operator aimed at the wrong tail reported FAIL on a
   result the same numbers decisively separate.

The live version is a two-sided test against the measured envelope, and it **gates** the verdict
— a post-hoc tightening, recorded as one, that can only make the verdict harder to obtain.

## What was repaired outside this round

`assurance/consistency.py`, both rows, with the reasoning inline:

- the full-rejection row now compares **counts** (194.9 vs 195, tol 3) instead of rates.
- the coverage row is annotated: it asserts `1.0` and **passes**, and the pass *is* the finding
  — 1.0 is the signature of the defect. Any correct implementation returns 0.268 and would have
  been reported as a failure. **A check whose pass condition is satisfiable only by the defect is
  worse than absent.** R150's artifact is annotated, not rewritten (L81).

## Scope

CoVal `annotators.jsonl` · no model instrument, human veto blocks and rankings only · baseline
plurality chooser · prompts with ≥6 rankings and ≥3 **asked** veto responses.

## What this site structurally cannot do

**Know why the question was not posed** — the release carries no field for it. If it was withheld
non-randomly, the asked population is itself selected; this round corrects the arithmetic without
being able to correct that.

## Still open

`consistency.py` exits 1 on one remaining row: r144/r145 unserved rate, 0.2831 vs 0.3404 against
a 0.03 tolerance. Untouched here.
