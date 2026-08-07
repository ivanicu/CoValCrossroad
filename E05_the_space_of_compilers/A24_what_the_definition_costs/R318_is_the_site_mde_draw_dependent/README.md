# R318 — the site MDE is a property of a draw, not of the site

**Decision this makes safe:** whether `FORMULATION.md` may quote *"the site's own MDE —
[0.1250, 0.1250]"* as a fact about the release. **It may not — but R274's conclusion survived an
independent judging, which is a severity test nobody designed.**

## How it arose

R317 ended on six rounds reading `_archive/r257_first_pass/instruments_retyped_prompt.npz` —
gitignored, and **no committed code writes it**: six readers, zero writers, grepped over every
`.py`. Five are cited by `FORMULATION.md`.

**The obvious fix was wrong.** R257's committed `results/instruments.npz` is the same size with the
same keys — but the two have **byte-identical `meta`** (45,204 rows, 250 conversations, same index)
and **different `sat`**. They are **two independent judgings of one grid**. Substituting one for the
other does not restore a missing input; it asks a different question, and asking it is this round.

## Controls, before anything is believed

| control | result |
|---|---|
| **positive** — `meta` byte-identical (same grid) | True (required) |
| **positive** — `sat` differs (two distinct judgings) | True (required) |
| **placebo** — replay R274 on its own input vs the artifact **on disk** | **16 of 16 keys identical** |

The placebo is what makes the rest readable: it establishes the published artifact came from the
published code. **Compared against disk, not against a second fresh run** — two fresh runs agreeing
certifies determinism and says nothing about what was committed.

## The swap — identical grid, second judging

| quantity | draw A (published) | draw B | moved |
|---|---:|---:|---|
| **mde_bracket** | **[0.125, 0.125]** | **[0.105, 0.125]** | YES |
| tau | 0.428 | 0.424 | YES |
| alpha_holdout | 0.03767 | 0.04567 | YES |
| cal_mean | 0.37992 | 0.38012 | YES |
| cal_sd | 0.02807 | 0.02778 | YES |
| shamA | 0.025 | 0.035 | YES |
| shamB | 0.005 | 0.0175 | YES |

**7 of 7 quantities moved.** The admitted set did not:
`['R249 minimal-size move under label order']` in both.

## W-DRAW-BOUND

*"The site MDE is [0.1250, 0.1250]"* is **one draw's answer, reported without naming the draw** —
the scope failure this campaign has retracted for more than any other. Over the two draws available
the lower bound is in **{0.1050, 0.1250}** and the upper in **{0.1250}**.

**n = 2 draws. That is a RANGE, not an interval.** No sd is computable and none is reported.

**And the conclusion is stronger than it was.** R274's verdict, its admitted set and its retraction
of R268 all survive an independent judging. **The number weakened; the finding held.**

## ⚠ My admitted-set extractor manufactured the worst verdict on the menu

The first version took the **first** bracketed span in the verdict string — which is the *MDE
bracket*, not the admitted set. So it "differed" for exactly the reason the round was measuring, and
printed **W-VERDICT-MOVES**: *every claim downstream must be re-opened*.

`a search is an instrument and has no positive control`, and shipping it would have been a
**fabricated crisis**. The admitted set is the span naming *rounds*, so it is the one containing a
letter. The extractor now has a refusal: no round-naming span → the round exits 2, because **two
`None`s comparing equal is not agreement.**

## ⛔ CORRECTION, one round later: "two independent judgings" was not earned

R318 called A and B *"two independent judgings of one grid"*. That phrase implies **exchangeable
draws of one instrument**, and the round never measured what they differ BY. Measured afterwards:

| | |
|---|---:|
| identical cells | 8,245 of 45,404 (18.2%) |
| median \|diff\| | 0.0462 — **21% of the quantity's own sd (0.2182)** |
| max \|diff\| | 0.6293 |
| **corr(A, B)** | **0.9508** |

**That is not sampling noise and it is not bf16 jitter**, which would sit near 1e-3. Against this
project's own reference points, from R234 via R257's docstring:

| comparison | r |
|---|---:|
| faithful re-implementation of the **same** prompt | **0.998** (MAD 0.008) |
| **A vs B (this pair)** | **0.9508** |
| label-order flip, *"Answer Yes or No"* → *"No or Yes"* | **0.77** |

A and B differ **far more than a faithful rebuild and far less than a label flip**. And both files
carry `default` / `flipped` / `sham` in equal counts (15,068 each), so **the difference is not the
variant axis** — it is something applied across all three.

**What is NOT established:** that the difference is specifically the prompt retyping the archived
filename names. **The npz stores `meta`, `sat`, `n_tasks` and no prompt text**, so the attribution
cannot be checked against the object. It is consistent with the filename and with the correlation
sitting between the two reference points — that is D5, not a measurement.

> **The corrected statement: A and B are two INSTRUMENT STATES differing by an unrecorded change,
> calibrated between a faithful rebuild and a label flip. The site MDE's spread across them is
> therefore NOT a sampling range — it is instrument sensitivity to a change nobody wrote down.**

Which makes the range **harder** to shrink, not easier: a third judging would add a draw of one
state, and the quantity that moved is not a draw. And it makes R257's own stance the right one to
inherit — *"neither instrument is privileged"* — so neither bracket may be preferred.

## Scope

250 prompts of R274's calibration · judgings A (archived first pass) and B (R257's committed rerun)
· class-agreement statistic at R274's calibrated threshold · one release.

## What this site cannot do

- **a third draw**, which would turn the range into an estimate — needs a GPU judging run through
  pueue
- **knowing which draw the release's own numbers were built from** — the archived pass is undated
  in the repo
- **a negative control**: destroying the structure under test means judging the grid again. Named
  here rather than improvised.
