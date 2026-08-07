# R823 · ④'s floor was the max over a fifth of its own published family — and it cost nothing

**E05 · A24 · R823. WORLD A.** 968 prompts · 58 arms · R435's published 30-rule family ·
R803's 6-rule subset. Source `2418b74e`.
Two seeds byte-identical: `fd409c2d64e6d0a07fa7542525f243ed`.

## The decision this makes safe

`DEFINITION.md:118` states ④'s scope in its own words: *"a **30-rule** hand-built family standing in
for 'every criterion-free rule'. The family is published in R435's artifact so that **extending it is
how this clause gets refuted**."* R803 built **six**. **All six are members of that thirty.** And R821
— shipped yesterday — retained ④ as *free-but-real* on `0 of 58` measured against that subset's max.

R528 emptied ②∧③ by taking ②'s class maximum literally over 1,820 subsets instead of the published
p93.7 comparator. **Nobody had done it for ④.** So the round was built as a direct attack on
yesterday's commit.

## The attack failed, and the failure is the result

| | |
|---|---|
| best of R803's six | `max_len_chars` **0.455679** |
| best of all thirty | `max_len_chars` **0.455679** |
| **rise** | **+0.000000** |
| ④ excludes at the 6-rule floor | **0 of 58** |
| ④ excludes at the 30-rule floor | **0 of 58** (1 UNVERIFIED: `full_sham`, +0.0047 [−0.0079, +0.0185]) |

**`max_len_chars` is the argmax over the whole family, not merely over the subset.** The next four
are `min_ttr` 0.4492, `first` 0.4421, `max_mean_word_len` 0.4402, `max_len_words` 0.4351.

⭐ **And R803's choice of six was worth something measurable.** A **random** six of the same thirty
reaches only **0.439060 ± 0.018355**; R803's six reaches the full-family maximum. The choice bought
**+0.0166** over an arbitrary six of the same size — because its axes are
{chars, words, position} × {longer, shorter} and length is the known bias, not because it was lucky.

⛔ **A DERIVATION, and it was run as the search's positive control**: a random 6-subset contains the
family argmax **6/30 = 0.200** of the time. Measured over 2,000 draws: **0.208**. The instrument sees
what the algebra says it must.

## Controls

| control | returned |
|---|---|
| **OBJECT** | the six reproduce R803's committed **0.4557** to <5e-5 on this population — validating **30 new feature implementations** against a known answer before any was trusted |
| **PLACEBO** | the floor against itself: **exactly 0** |
| **POSITIVE** | δ = 0.10 / 0.05 / 0.01 all removed; **δ = 0 not removed** — it can fail |
| **NEGATIVE** | synthetic arm resampled from the floor's own distribution: **−0.00028 ± 0.00493** vs real **+0.08188** |
| **SHAM ⭐** | 30 **random** scorers: max over 30 **0.440503**, over a random 6 **0.437091 ± 0.002830**. **Pure selection buys +0.003412 going 6→30 on noise.** |
| **NOISE FLOOR** | 20 half-splits: **0.0051** (m=6), **0.0043** (m=30) |
| **BH** | 58 tests: **57 survive, 1 does not** |

⭐ **The sham is what makes the zero meaningful.** The real 6→30 rise is **+0.000000**, which is
*below* the **+0.003412** a class of that size gets from selection alone on pure noise. **The extra 24
rules add less than nothing** — they add less than random scorers of the same count would.

## The held-out floor goes DOWN

| | in-sample | held-out (20 splits) | optimism |
|---|---:|---:|---:|
| m = 6 | 0.455679 | **0.456094 ± 0.004345** | −0.000415 |
| m = 30 | 0.455679 | **0.454779 ± 0.004791** | +0.000900 |

**Held-out rise 6→30: −0.001315.** Enlarging the class makes the *generalising* bar fall, because the
fit-half max overfits more with 30 candidates than with 6. **Inside its own sd (±0.0048), so this is
a direction, not a value** — reported because it is the opposite of what "a bigger class is a
stronger bar" predicts, and because ④ as written quantifies over rules that must generalise.

## What this round got wrong

**The sham could not have failed.** The first version sorted the 30 random scorers descending and
took the **top six**, so `sham6 == sham30` identically and the rise was `+0.000000` by construction.
It printed a number that looked like a passing control. §4's opening row — *a check that cannot fail*
— built inside the round whose entire subject is selection. A six-subset must be drawn at **random**,
because a random six is precisely what R803's six has to be compared against. **The corrected sham is
the only reason the headline zero is admissible**: without it, `rise = 0` is silence.

## Verdict

**WORLD A — saturated.** R821's retention of ④ stands, and its scope widens from a 6-rule class to
the full 30-rule family the definition names. **④ still excludes 0 of 58, now for a reason rather
than for lack of looking.**

## What this round cannot do

| criterion | requires |
|---|---|
| "every rule computable from the response set alone" | an infinite class; 30 hand-built rules stand in for it, and the register in `DEFINITION.md:118` says so |
| independently replicated | a second release |
| cross-dataset / cross-model | a second site |
| construct validated | an external gold standard for "core" |
