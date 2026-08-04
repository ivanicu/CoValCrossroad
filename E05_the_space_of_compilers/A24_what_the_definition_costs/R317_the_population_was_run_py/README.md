# R317 — R315 measured `run.py` and said "rounds"

**Decision this makes safe:** whether R315's runnability numbers may be quoted as being about
rounds. **They may not — and the files it excluded broke at 2.37× the rate of the files it
measured.**

## The scope error

R315 globs `E*/A*/R*/run.py` and reports *"how many **rounds** can still run"*. There are **341**
`.py` files directly in round directories; 302 are `run.py`. **39 files — 11.4% of the population —
were never asked.** The instrument's unit was *file named run.py*; the claim's unit was *round*, and
nothing ever required them to be equal.

Fourteen of the 39 are `independent_A.py` / `independent_B.py` — the **triple-blind
implementations**, which `realstat §2.5` calls the only evidence that survives a framing error.

## W-WORSE, at the pre-repair revision `9f33bf2`

| unit | broken | rate |
|---|---:|---:|
| per FILE, `run.py` only | 19 of 278 | **6.8%** |
| per FILE, everything else | 6 of 37 | **16.2%** |
| per ROUND (any file broken) | 24 of 310 | 7.7% |
| | **ratio** | **2.37×** |

**Triple-blind layer: 5 of 14 files BROKEN-INPUT.**

Above the pre-registered `[0.5×, 2.0×]` band → **W-WORSE**. A file nothing ever executes is a file
nothing ever checks. R315 both mislabelled its unit *and* understated the problem.

## Controls

| control | result |
|---|---|
| synthetic planted MISSING read | BROKEN-INPUT ✓ |
| **g=0** synthetic PRESENT read | COMPLETED ✓ |
| **exact-subset** vs `sweep_F` | **301 files, 0 disagreements** |
| negative: `git status` byte-identical | True |
| noise floor | quoted from R316: 2/300, all `TIMEOUT↔REACHED-WRITE`, 0 BROKEN |

## ⚠ Three defects in this round, all caught before the verdict

**① The first run measured a population I had already repaired.** It swept HEAD and returned
*"0 of 37 non-`run.py` broken"* — after the previous commit fixed 14 stale sites in 8 of those very
files. The three pre-registered worlds are all about the **pre-repair** rate; HEAD cannot answer any
of them. **The tell is that the flattering number arrived immediately after the work that would
produce it.** The round now refuses the world call at HEAD and returns `W-UNIDENTIFIED`, naming it a
design defect rather than a data limit. git still held the pre-repair tree, so the comparison was
recoverable rather than lost.

**② The subset control failed for its own reasons, twice.**
- First: it counted *any* disagreement as failure and flagged 3 of 302 — **all three involving
  `TIMEOUT`**, which means *the sweep did not find out* and cannot contradict anything. It ignored
  the churn floor this campaign had already measured, in the same class. Corrected to: no
  disagreement may have a **decided class on both sides**.
- Second: at `9f33bf2` it compared against **sweep E**, which is *post*-repair. And sweep A is not
  the partner either — A ran before `.venv` was added to the isolation harness, so it reports 25
  broken where this reports 19, and **the 6 are exactly the `.venv` cohort**. Neither differs by
  noise; each differs by a deliberate change. **A subset control is only a control against a sweep
  sharing both the tree and the instrument**, so the matched pre-repair sweep (F) was run rather
  than substituted. It then passed 301/301.

**③ `ensure_worktree()` returns an existing worktree untouched** — it does not honour its `rev`
argument, and a worktree left at an earlier HEAD measures the past. Forced and **asserted** locally
rather than in the shared harness, since R315 and R316 stand on that harness.

## The repair's effect, at HEAD

| unit | pre-repair | post-repair |
|---|---:|---:|
| `run.py` broken | 19 of 278 | 6 of 279 |
| other `.py` broken | 6 of 37 | **0 of 37** |
| triple-blind broken | 5 of 14 | **0 of 14** |
| per ROUND | 24 of 310 | 6 of 311 |

Both arms are on disk as `results/population_9f33bf2.json` and `results/population_HEAD.json` — the
first two runs of this round overwrote each other, and a round whose two arms cannot both be read
from disk cannot be attacked on the comparison that is its whole point.

## Scope

Every `E*/A*/R*/*.py` at each named revision · R315's probe (`sys.addaudithook` on `open`) in a
detached git worktree · 60 s wall clock · no GPU, no network.

## What this cannot do

Prove any file **correct** by running it — `REACHED-WRITE` means inputs resolved, nothing more. And
the 25 GPU-touching files are excluded by the pueue rule, counted separately, and are **UNVERIFIED,
never folded into intact**.
