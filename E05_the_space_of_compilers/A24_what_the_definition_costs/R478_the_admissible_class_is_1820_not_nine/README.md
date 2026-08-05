# R478 · The admissible class has 1,820 members, not nine

**The decision this made safe.** Whether R477's *"③ is cheap"* survives a comparator drawn from the
**whole** rival class rather than the nine arms that happened to have `.npz` files. **It does, and the
number tightens: `topw_k4` − best prompt-blind subset = +0.0071, against a floor of 0.0122.**

## The premise that sent me here was wrong

`DEFINITION.md:337` records `generic` at **percentile 0.000** of a 1,820-member census — so R477's
comparator looked like the weakest member of its family. **That percentile is about the *replication*
statistic (0.8114 against a census of 0.8226–0.8675), not about A2.** On A2, `generic` sits at
**percentile 94.4**. Same arm, two censuses, opposite readings. The round ran anyway and measured it.

## The census — all 1,820 4-subsets of `genericpool16`, published whole

| min | p25 | median | p75 | **MAX** |
|---|---|---|---|---|
| 0.5049 | 0.5198 | 0.5261 | 0.5320 | **0.5433** |

- `generic` **0.5377** → percentile **94.4**
- `topw_k4` **0.5475** → percentile **100.0** — above every one of the 1,820

## Cross-fitting, because a max over 1,820 is an order statistic

Select the argmax on a random half of prompts, score it on the other half, ×20 splits.

| | |
|---|---|
| MAX_IN (in-sample) | 0.5433 |
| **CV_OUT (held-out)** | **0.5404** ± 0.0061 |
| **selection inflation** | **+0.0029** — small; the best subset is genuinely selectable |
| random subset, same splits | 0.5260 |

**`topw_k4` − cross-fitted best = +0.0071** (R477 reported +0.0098 against `generic`). **Still inside
the 0.0122 floor. ③ stays cheap, and the margin is smaller than R477 thought, not larger.**

## Controls

| control | returned | |
|---|---|---|
| POSITIVE — selection beats a random subset out-of-sample | **+0.0145** > floor | ✓ |
| g=0 — selection on *shuffled* targets | **+0.0071** | ⚠ not zero — see below |
| PLACEBO — A2 vs shuffled rankings | 0.4325 vs R477's measured chance 0.428 | ✓ |

⚠ **The g=0 residual is reported, not rounded away.** Shuffling the ranking *within* a prompt leaves
that prompt's own difficulty intact, so a shuffled-target argmax still inherits real structure. The
genuine selection edge (+0.0145) is **2.0×** the residual — a ratio, not a clean zero.

## Specification curve — every subset size, whole census each time

| k | C(16,k) | min | median | MAX_IN | CV_OUT | `topw_k`<sub>k</sub> pct |
|---|---|---|---|---|---|---|
| 2 | 120 | 0.4960 | 0.5204 | 0.5430 | 0.5364 | 90.8 |
| 3 | 560 | 0.5004 | 0.5244 | 0.5437 | 0.5393 | 100.0 |
| 4 | 1,820 | 0.5049 | 0.5261 | 0.5433 | 0.5386 | 100.0 |
| 5 | 4,368 | 0.5064 | 0.5271 | 0.5430 | 0.5381 | — |
| 6 | 8,008 | 0.5082 | 0.5277 | 0.5423 | 0.5371 | — |

⭐ **CV_OUT is flat at ~0.538 from k=2 to k=6 while the census median rises.** The prompt-blind class
has a **ceiling near 0.54 that more criteria do not raise** — the best small set is as good as the
best large one. `topw_k5` / `topw_k6` have no matching arm, so those cells are `—`, stated not dropped.

## What this corrects in R477

R477 closed with *"from this side `topw_k4` does not clear ②"*. **Too strong.** `topw_k4` is above
**every** member of the reference class in-sample; its margin over the best *selectable* one is
+0.0071, which is **inside the floor**. ② is **UNRESOLVED** for `topw_k4`, not failed — and folding
unresolved into failed is the false-retraction direction.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R478_the_admissible_class_is_1820_not_nine/run.py

Compute-free · 14,876 subsets evaluated across the k-sweep · 20 cross-fit splits · artifact
`results/r478_class_census.json`.
