# R552 · The register's cost column measured the LAST obstacle, not the FIRST

**Decision this makes safe:** what the register is a specification *for*.

**WORLD B: 0 of 3 on-site rows have compute as their first blocker.**

| row | first blocker | still blocking | compute-bound |
|---|---|---|---|
| 2 — offload | missing flag (`device_map` hard-coded at `covalx/judge.py:169`) | ✔ | **no** |
| 2 — quantise | an install (`bitsandbytes` absent) | ✔ | **no** |
| 3+4 *(nested, R546)* | missing flag (`generate_core.py` has no `--model`) | ✔ | **no** |

**The column was denominated in what you must RUN.** §2 says the register doubles as the
specification for the next site — and a specification denominated in the last obstacle tells a
reader nothing about whether the row is reachable.

⭐⭐⭐ **The asymmetry the old unit could not express:** `judge_core.py` **does** expose `--model`,
which is why R536's cross-judge replication and R537's dose-curve replication were **reanalyses
rather than edits**. **Existing flags decide which questions are cheap.**

## ⛔ This round shipped a check that could not fail, and it was caught before committing

The first loop did `compute_bound += 0` — hard-coded, so **WORLD A was unreachable and the
pre-registered kill was decoration.** Built in the round *about* measurement units.

**Fixed to a computation:** a row is compute-bound exactly when its non-compute blocker **stops**
holding — the flag is already there, or the package already installed. **Proven fireable:** simulate
row 3+4's flag existing → `compute-bound = 1` → **WORLD A**.

## Controls
- **Positive** — row 5's blocker is another site and must not be reclassified. **PASS.**
- **Negative** — an invented flag resolves nowhere. **PASS.**
- **Falsification** — the kill fires under a simulated blocker removal. **PASS.**

⭐ **Also repaired here:** R551's backfill persisted **evidence with no verdict**, and
`statement_provenance` refused three citations because of it. Artifacts now carry a `world`
**computed** from whether every claim verified — never typed.
