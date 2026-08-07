# R428 · did the eight tree mutilations cost untracked data? — **yes, 24 files**

**The decision this round makes safe:** whether the assurance suite can be run at all without
risking the repository, and whether yesterday's "restored with zero data loss" was true.
**It was false.** 21 untracked artifacts (~200 MB) and 3 never-committed source versions existed
only in `/tmp`. All 24 are recovered and hash-verified.

## ⛔ The event is not a one-off. It has happened **eight times.**

Yesterday's incident was written up as an accident caused by my own `pueue kill`. `/tmp` holds
**eight** orphaned `attack_rounds_*` stashes dated 08-03 and 08-04:

| stash | epochs | files | when |
|---|---|---|---|
| `nnrhnul9` | 6 | 1,553 | 08-04 12:20 |
| `zkpljpn8` | 6 | 1,421 | 08-04 07:04 |
| `0pwapbm_` | 6 | 1,191 | 08-03 14:57 |
| `zlvyb35h` | 6 | 1,173 | 08-03 15:02 |
| `eoaboun7` · `6vdx1_v2` · `9gfiex0o` · `kjju5abo` | 1 each | 141 · 135 · 60 · 5 | 08-03 |

**Five happened on 08-03 and nobody noticed**, because `run_isolated(restore_first=True)` repairs a
previous interruption on the *next* invocation. The system self-heals on next run; **it does not
self-heal while nothing runs.**

> ⭐ **And the failure was already written into a round's own title.** R389's README reads
> *"...and my tooling deleted the round"* and its artifact carries `"destroyed_and_rewritten":
> true`. A confession is never audited.

## The mechanism, and one correction to yesterday's commit

`attack_the_suite.hide_rounds()` moves every `E\d\d_*` directory to a random `mkdtemp` and restores
in a `finally:`. **`pueue kill` sends SIGKILL, which no `finally` survives.**

⚠ **`dc5c7e3` named `attack_the_suite` AND `attack_every_check`. Only the first does this.**
`attack_every_check` `git clone`s into tmp and never touches the live tree. The `attack_rounds_`
prefix belongs to one file.

## The scripts, and what each returned

| script | question | verdict |
|---|---|---|
| `run.py` | is anything missing from the tree that a stash has? | **`W-SILENT-LOSS`** — LOST-u **37**, DIV-t **57** |
| `what_was_lost.py` | how much of that is real? | **`W-REAL-LOSS`** — 23 irrecoverable, 3 never committed |
| `recover.py` | put it back, and prove each file arrived | **24 recovered, all hash-verified** |
| `assurance/_repair.py --selftest` | does the fix fix the actual event? | **PASS on both channels** |

## Controls, and the two that changed the design

| control | returned |
|---|---|
| PLACEBO — a stash copied verbatim from the tree (408 files) | lost 0 · divergent 0 · **must be 0/0** ✅ |
| NEGATIVE — the same copy, one byte flipped | divergent **exactly 1** ✅ (a real divergence is visible) |
| POSITIVE — 5 impossible paths planted | reported LOST **5/5**, retention 100% ✅ |
| g=0 — nothing planted | planted-LOST **0** ✅ |
| POSITIVE — `git cat-file -e` on a committed file | **True** ✅ (so a `False` means something) |
| NEGATIVE — the same on random bytes | **False** ✅ |
| `verify()` on an identical copy / a corrupted copy | **True / False** ✅ |

## ⛔ The gauge test killed my first design before I wrote it — 3 lines, zero compute

The obvious repair checks `for d in ROOT.glob("E0*"): d.exists()`. Name the transformations leaving
that **measurement** invariant while the **property** is violated:

- an epoch present but **emptied** → `exists()` True — **blind**
- an epoch moved aside with a **bare dir left behind** → True — **blind**
- a single **round** moved, not a whole epoch → not enumerated — **blind**

Measurement invariant + property not ⇒ blind. The instrument is therefore **`git ls-files
--deleted`**, and the selftest's `BLINDNESS` control demonstrates the naive check missing damage
that git reports as **96 missing paths**.

## The two loss channels, and why git only covers one

| channel | what recovers it | measured |
|---|---|---|
| **tracked** | `git checkout -- <path>` **by name from the index** | LOST-t **0** — git covered it |
| **untracked** | nothing, until now | **21 artifacts, ~200 MB** existed only in /tmp |
| **tracked but never committed** | nothing — the bytes are not in the object DB | **3** (all R389) |

Fix: `hide_rounds()` now writes a **breadcrumb** (`assurance/results/.hide_in_progress.json`)
naming the stash *before* the first move, and `_repair.repair_full()` runs at **entry** to
`attack_the_suite.main()`. Breadcrumb first, index second — the stash is the richer copy, and it
**never overwrites an existing file**, because R389 proves the tree's copy is sometimes the newer.

## ⛔ Committed the same error one level up, ten minutes after measuring it

`recover.py` filed R389's only surviving original into `_archive/pre_deletion_original/` — and
**`.gitignore:3` ignores `_archive/`**. The recovery placed a never-committed file into precisely
the class of path this round had just proved gets destroyed. `recover.py` now runs `git
check-ignore` on its own destination and **refuses** rather than reporting success.

## Impossible here, named

- **historical completeness** — a stash reaped before today is invisible. Every count is a **lower
  bound**. Would require a tmp-retention policy that did not exist.
- **attributing a stash to the run that made it** — the mkdtemp name carries no provenance. Would
  require the harness to stamp its own stash; the breadcrumb now does this **going forward only**.
- **ranking the loss by importance** — the instrument's unit is a path; a `.pyc` and a 112 MB
  embedding count the same. Would require a criterion for which artifacts matter, which is a
  judgement, not a measurement.
- **deciding which of two divergent versions is newer** — a hash mismatch has no direction.
  Resolved for R389 only because the tree's own artifact says `destroyed_and_rewritten`.

Findings and their scope live in the top-level README. This file states the design and the round's
own corrections.
