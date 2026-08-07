# R397 — the defect was real, and it was not load-bearing

**The decision this makes safe:** *do R394 and R395 stand?* **Yes — measured, not assumed. 13 of 13
subjects exited 0.**

## Result — `W_LABELS_SOUND`. Both plants pass. **No GPU spent.**

| | |
|---|---:|
| subjects R394 called STABLE | 13 |
| **exited 0, no traceback** | **13 / 13** |
| NOT-OK | **0** |

## ⛔ The defect, found by writing a different round's docstring

While writing **R396** I had to name the failure it must not commit — *a crash is byte-identical
twice*. Writing that sentence down made it obvious that **R394, committed an hour earlier, has that
defect**: it reads `p.stdout + p.stderr` and **never `p.returncode`**. A round that cannot run emits
the same traceback on both draws, the number multisets match, and the comparison prints `STABLE`.

**R393 is worse in the same direction** — its timing loop discards the `CompletedProcess` entirely,
so `COMPLETE` means *"finished inside 90 s"*, **not** *"succeeded"*. A round crashing in 0.4 s was
recorded COMPLETE and became one of R394's subjects.

**And it propagates to R395**, which is what made this urgent rather than tidy: R395 scored its
detector against *"13 rounds R394 measured as STABLE"*, calling every hit among them a false positive
**by construction**. Had any never executed, the **23% false-positive rate was measured against a
corrupted answer key**, and the `W-GAUGE-DECISIVE` verdict that halved the expensive step rests on it.

## ⚠ There was a named mechanism, not a generic worry

**R393 reset the worktree between subjects with a hard checkout and a recursive untracked-file
purge.** R390 had already established that the release data under `data/` is **untracked** and had to
be linked in by hand. So R393's own hygiene step plausibly removed the inputs its later subjects
needed — a mechanism written **before** the run, predicting failures concentrated in data-reading
rounds.

**It did not happen.** The prediction was specific enough to be wrong, and it was.

## Controls

| | returned |
|---|---|
| **PLANT (+)** | a script exiting 3 is classified **FAILED** — `PASS`. Without it, *13 of 13 exited 0* is silence from an instrument never shown to detect a failure |
| **PLANT (−)** | a clean script is classified **OK** — `PASS`. The detector is not a constant that condemns everything |
| **REGIME** ⭐ | R394's **own worktree, unreset**. A claim about R394's measurement needs R394's conditions; resetting would silently have answered a different question |

## What this does and does not license

| | |
|---|---|
| **R394's `W_KEY_VALID`** | **STANDS** — its 13 subjects genuinely ran |
| **R395's `W_GAUGE_DECISIVE`** | **STANDS** — its answer key is intact |
| **the defect in R393/R394** | **REAL, and uncorrected in those two rounds** — it was not load-bearing *for this population*, which is a fact about these 13 rounds, **not a property of the code** |
| **the fix** | **R396's `UNRUNNABLE_HERE` class**, already committed. It applies from now on — it does not retroactively excuse the two rounds that lacked it |

## Register

| criterion | status |
|---|---|
| **a round exiting 0 while doing nothing** | **PARTIAL** — the traceback signal covers some of this gap, not all of it |
| **re-deciding R394's STABLE comparison** | **N/A** — this measured whether the subjects *ran*, not whether their numbers matched. Separate questions, deliberately not merged |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"the outputs were identical across two runs, therefore the round is stable"* — **without checking
> the process succeeded.** Two identical failures are the most identical outputs available.

Artifact: `results/r397_subject_exit_codes.json`, source-stamped.
