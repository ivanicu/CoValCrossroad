# R551 · `DEFINITION.md` was never the per-round log I was treating it as

**Decision this makes safe:** where a round's reasoning is supposed to live, and whether the last
ten rounds lost theirs.

## The number, and the null it is compared against

**`DEFINITION.md` has no section past R541** — ten rounds (R542–R551) have neither a heading nor a
mention. But **it has only ever recorded 39 of 254 rounds = 15%**, so "it stopped" needed a null.

| unit | n gaps | median | max | current tail | percentile |
|---|---|---|---|---|---|
| **section** | 38 | 0 | 71 | 10 | **5.3%** — ordinary |
| **mention** | 139 | 0 | 25 | 10 | **1.4%** — anomalous |

⭐⭐⭐ **The two units disagree, and the weaker one bounds the claim.** A mention is not a record of
reasoning; a section is. **By the unit that matches the claim, a 10-round gap is within this
document's ordinary behaviour.** The instrument's unit and the claim's unit were written as separate
strings before the control was designed, exactly because they are not equal.

## What was actually wrong — and it is not the gap

**P16 names the round README as the home for a round's reasoning. All 9 completed late rounds have
one** (185–306 words). So nothing was lost. **My belief that every round appends to `DEFINITION.md`
was false, and had been false for 215 rounds.**

## ⚠ The real defect, found by the disagreement between two of my own checks

| what a round persisted | rounds |
|---|---|
| source + artifact | **245** |
| **EMPTY `results/`, no `run.py`** | **4** — R543, R544, R545, R546 |
| no `results/` dir | 3 |
| artifact, **no source** | 2 — R444, R472 |

**The four are consecutive, and they are exactly the rounds that read SOURCE instead of running an
experiment.** They created `results/` and left it empty — **which reads as "persisted" to a loose
check, and my first pass tested `results/ EXISTS` and counted them as fine.**

**Backfilled by re-verification, not by filing.** `backfill_reading_rounds.py` re-reads the source
and records what is there **now**, with a sha256 of every file consulted. All **6** claims still
hold — `--batch` present, `do_sample=False`, no `--model` in `generate_core.py`, `FEWSHOT` a module
constant, `--model` present in `judge_core.py`, `device_map="cuda"` in `covalx/judge.py`.

## Controls
- **Positive** — headings found for R539/R540/R541: **3/3**. **PASS.**
- **Negative** — an invented `R999` found by neither detector. **PASS.**
- **Positive (backfill)** — a known-true predicate verifies; **it crashed rather than passed** on the
  first run, catching a wrong `parents[3]` for a file at arc level. **PASS after fix.**
- **Negative (backfill)** — a known-false predicate (`--nonsense`) does not verify. **PASS.**
