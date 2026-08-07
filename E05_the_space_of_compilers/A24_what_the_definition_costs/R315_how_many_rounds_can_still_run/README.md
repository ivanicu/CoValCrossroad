# R315 — how many rounds can still run at all?

**Decision this makes safe:** whether this repository's artifacts can be *attacked* or only
*cited*. **25 of 278 probed rounds (9.0%) cannot resolve their inputs**, and one moved directory
accounts for 44% of them.

## How it surfaced

R314's next-gradient pointed at the last failing consistency row, r144 vs r145. Two defects
appeared before any statistics did, and the second is far larger than the row that led here.

**① The check invents the quantity it compares.** `u144 = r144["mean_residual_G0"] / 15.6`, and
`15.6` appears in **neither** round's artifact. r144 computes the mean panel size as
`pan = mean(n_criteria)` and **prints** it — it never persists it. The constant was transcribed
from a printout: unverifiable from any committed file, and silently stale the moment r144's
population moves. Worse, r144's own `analyse` already returns `residual_G0_frac` per prompt —
the mean-of-ratios estimator, i.e. exactly what r145 reports — and r144 aggregates it nowhere.

**② And r144 cannot be re-run**, which is why ① was never caught:
`base = ROOT / "E01" / "R04_rebuild_satisfaction" / "results"` — the pre-migration epoch and arc
names. **A repository whose rounds are not re-runnable has artifacts that cannot be attacked,
only cited.**

## Result — W-MIGRATION

Population: 300 rounds at HEAD. 22 excluded as GPU-touching (pueue rule), counted separately and
never folded into "intact".

| class | n | what it licenses |
|---|---:|---|
| **BROKEN-INPUT** | **25** | decisive: an input does not exist |
| REACHED-WRITE | 207 | inputs resolved — **not** a pass |
| TIMEOUT | 40 | **UNVERIFIED** — says nothing either way |
| OTHER-ERROR | 6 | needs inspection; unclassified |
| SKIPPED-GPU | 22 | not probed — UNVERIFIED, not intact |
| COMPLETED | 0 | |

**Cause concentration — 5 distinct missing inputs across 25 broken rounds:**

| n | missing input |
|---:|---|
| 11 | `E01/R04_rebuild_satisfaction/results/a04_full.npz` |
| 6 | `_archive/r257_first_pass/instruments_retyped_prompt.npz` |
| 6 | *(raised `FileNotFoundError` from a subprocess; path unrecorded)* |
| 1 | `rounds/R04_rebuild_satisfaction/results/a04_full.npz` |
| 1 | `E01/R04_rebuild_satisfaction/results/a04_core.npz` |

Two dead prefixes (`E01/`, `rounds/`) name the **same** file across three naming eras.

## Controls

| control | got | |
|---|---|---|
| synthetic round reading a MISSING file | BROKEN-INPUT | ok |
| **g=0**: synthetic round reading a PRESENT file | COMPLETED | ok |
| placebo: an empty script | COMPLETED | ok |
| r144 (the case that motivated this) | BROKEN-INPUT | ok |
| R313 (known to run) | REACHED-WRITE | ok |
| **negative**: `git status` byte-identical before/after | **True** | ok |

The synthetic control is the one that matters. r144 alone would only show the instrument agrees
with the case that motivated it — *a control that shares the instrument's blind spot*.

## ⚠ The pre-registered discriminator was the wrong prediction

`W-MIGRATION` was pre-registered as *"breakage clusters in round id"*. That is not a migration's
signature — **many rounds failing on the same moved input** is, and ids need not cluster at all.
The id test is reported because it was pre-registered (U = 0.356 vs envelope [0.385, 0.615] →
clustered), but **cause concentration is what separates**, and it was added after seeing that the
id test could not have distinguished the worlds. Recorded as a post-hoc addition.

## ⚠ Four defects in my own instrument, three caught before reporting

1. **27% over-count.** The first sweep returned 15 broken, of which **4 were the instrument**:
   three rounds "failed" on `.venv/…/markupsafe-3.0.3.dist-info/entry_points.txt` and one on a
   `__pycache__` `.pyc` not yet written. Both are libraries probing optional files; both sit
   under ROOT because the venv is in-tree.
2. **The write block does not reach subprocesses — and it did damage.** Nine rounds shell out,
   and child processes have no audit hook. The first sweep **modified seven committed
   artifacts** (R220, R221, R238, R241, R244, R245, R265) while its own docstring promised it
   wrote nothing. Restored from git. **The negative control caught it** — `git status` was not
   byte-identical, the verdict went UNVERIFIED, and that is the only reason this is a paragraph
   and not silent corruption. The sweep now runs in a **git worktree**.
3. **The worktree was stale**, sitting at a HEAD from earlier in the session — 294 rounds, no
   R313. A worktree that is not moved to HEAD measures the past.

## ⚠⚠ And a fourth, in the shared harness, which is the round's most reusable output

`assurance/_isolated.py` declared `UNTRACKED_INPUTS = ("data",)` and linked the **directory**
under `if not dst.exists()`. **`data/` always exists in a fresh worktree**, because
`data/fetch.py` is tracked. So the guard was true every time, **the symlink was never created,
and every isolated run this harness has ever done executed against a `data/` holding one 3.9 KB
script and none of the 69 MB release.**

The cost is not the missing files — it is the **misattribution**. The harness's own comment
records two subjects dying on `data/comparisons.jsonl` and reads it as *"a statement about what
the repo alone can reproduce"*. It was a statement about that function. Repaired to link per
**entry**, so a directory git has already materialised for a tracked file is filled in rather
than skipped.

## Scope

Every `E*/A*/R*/run.py` at HEAD `418612b` · instrument a `sys.addaudithook` on `open` · 60 s wall
clock per round · no GPU, no network · executed in a detached worktree.

## What this cannot do

**Prove a round is correct by running it.** REACHED-WRITE means inputs resolved, nothing more —
it is named that way so it cannot be read as a pass. Proving correctness would require re-running
each round's own controls and comparing to its committed artifact: a different, much larger
instrument.

## Still open

- the 6 OTHER-ERROR rounds (R58, R99, R165, R197, and two more) are unclassified
- 40 TIMEOUT and 22 SKIPPED-GPU are **UNVERIFIED**, so "9.0% broken" is a floor, not the rate
- none of the 25 broken rounds is repaired here; this round measures
