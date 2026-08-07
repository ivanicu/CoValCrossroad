# R395 — the gauge test discriminates, and it halves the expensive step to one round

**The decision this makes safe:** *which of the two expensive rounds must actually be re-run?*
**One — `R130_judge_gauge`. `R114_demographic_subject` carries no flagged construct at all.**

## Result — `W_GAUGE_DECISIVE`. Both plants pass. **No GPU spent.**

| | |
|---|---:|
| rounds R394 **proved** stable | 13 |
| detector **quiet** on them | **10 / 13** |
| **false positives** | **3 / 13 — 23%** (`builtin_hash` ×1, `fs_order` ×2) |
| censored rounds scanned | 2 |
| **`R114_demographic_subject`** | **quiet** |
| **`R130_judge_gauge`** | **`gpu`** |

## ⛔ The question was not "are the censored rounds risky"

A pattern matching `random` or `time` flags nearly every scientific script ever written, returns
*"both are at risk"*, and reads as an answer. **This campaign has been burned by exactly that five
times.** So the honest estimand is the prior question — **does a source-level detector discriminate at
all?** — and the censored rounds' hit list is *not* the estimand.

## ⭐ The answer key was not made here

**R394 labelled 13 rounds STABLE**, for a different purpose, in a committed artifact. Scoring the
detector against those labels measures its **false-positive rate against ground truth it did not
generate** — rather than against my imagination, which is this campaign's named failure mode for
controls. **Every hit among those 13 is a false positive by construction**, because their output was
*proven* byte-identical across two runs.

## ⚠ CORRECTION — R397: the answer key was audited after the fact

This round's false-positive rate is scored against **R394's 13 STABLE labels**, and R394's instrument
never read a process exit code — so a subject that crashed identically twice would have entered this
answer key as a labelled negative. **The 23% below, and the `W-GAUGE-DECISIVE` verdict that halved the
expensive step, rested on labels that had not been checked.**

[`R397`](../R397_did_the_stable_subjects_actually_succeed) checked them: **13 of 13 exited 0**. **The
key is intact and the verdict below stands.**

## ⚠ The limit that bounds what a hit means: 6 of 7 families were never positively controlled

| family | specificity evidence | **sensitivity evidence** |
|---|---|---|
| `unseeded_rng` | quiet on all 13 | ✅ **caught R394's plant** |
| `gpu` | quiet on all 13 | ❌ **none** |
| `wall_clock`, `builtin_hash`, `set_order`, `fs_order`, `concurrency` | measured | ❌ **none** |

> **So the `gpu` hit on `R130` is a HYPOTHESIS, not a detection.** The only family ever shown to fire
> on a genuinely varying script is `unseeded_rng`. A pattern that has never returned a true positive
> cannot certify that it would — the same asymmetry as a null from an uncontrolled instrument, one
> level up. **The verdict rests on the detector's *quietness*, which is what the pre-registration
> measured; its ability to *catch* is validated for exactly one family of seven.**

## What this actually buys

**The expensive step drops from two rounds to one.** R393 found the censored pair carries 80% of the
gate's cost; resolving whether the cache key is sound *where it matters* no longer needs both.
⚠ And `R114`'s quiet is **not proof of stability** — 3 of 13 proven-stable rounds were flagged, so the
detector's errors run in the false-**positive** direction here, and a quiet round is *unflagged*, never
*cleared*.

## Register

| criterion | status |
|---|---|
| **whether a construct reaches output** | **N/A** — undecidable by grep. Precisely why the false-positive rate is the estimand |
| **a rate over the censored rounds** | **N/A** — n=2. Named constructs only; a rate would be the arithmetic trap in a lab coat |
| **sensitivity of 6 of 7 families** | **UNVALIDATED** — stated above rather than implied by the verdict |
| **proving a round IS deterministic** | **N/A** — neither grep nor two runs can do that |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"grep the expensive rounds for nondeterminism and act on what it finds"* — **without first asking
> what the same grep says about rounds already known to be stable.** 3 of 13 answers it would have
> given were wrong, and I would have had no way to know which.

Artifact: `results/r395_gauge_power.json`, source-stamped.
