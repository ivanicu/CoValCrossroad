# R377 — the check is deterministic, and my own explanation for its flicker was wrong

**The decision this makes safe:** *is `attack_every_check`'s variation run-to-run noise, or a
function of the tree?* **A function of the tree.** R376's NEXT blamed my shared worktree; that
attribution is **withdrawn**.

## Result — `W_DETERMINISTIC`. Four controls PASS. Two runs byte-identical. **No GPU spent.**

| run | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| exit | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| restore | CLEAN | CLEAN | CLEAN | CLEAN | CLEAN | CLEAN | CLEAN | CLEAN |
| dirty after | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**1 distinct exit code · 1 distinct verdict table · 0 runs left the tree dirty.**

## ⛔ Withdrawing R376's NEXT — and measuring the withdrawal rather than asserting it

R376 closed by blaming a read-isolation hazard: three rounds pointing at `scratchpad/assurance_wt`,
which is also `_isolated.py`'s default worktree.

**`attack_every_check` runs with `cwd=ROOT` — the live tree.** But *"the source says so in one
line"* is exactly the convincing description this campaign distrusts, and the subject **invokes six
other checks** — if any of *those* used the worktree, the coupling would be indirect and my
refutation would be wrong.

> **All seven files were grepped: worktree references = NONE of 7.**

Only then does the withdrawal stand. **R376's NEXT named the wrong mechanism**, and this round is the
correction — R376 is not edited, because it is committed and it was wrong.

## What the variation actually is

I observed exit **1 → 2 → 1** across this session. It is **not** run-to-run noise: 8 consecutive
invocations at one commit are identical. So the check is a **function of tree state**, and the state
changed between those observations.

⚠ **[HYPOTHESIS] The state variable is the corpus, not the worktree.** The exit-2 observations fell
in the window where `every_round_reaches_the_readme` was itself red (R376 not yet on the front page),
and that check is one of `attack_every_check`'s six plant subjects. **This round did not test that** —
it measured determinism, not the cause — and the specific state variable is **UNVERIFIED**.

## What this does to R375

R375 withdrew `attack_every_check`'s breaking commit because its transition was non-monotone.
**That withdrawal was correct, and now for a stated reason:** if the check is deterministic given the
tree, then its non-monotone behaviour across commits is a **real dependence on corpus state**, not
noise in the measurement. Different commits are genuinely different corpora.

**So "the commit that broke it" remains not a well-formed object** — but because the property turns
on and off with the corpus, not because the instrument is unreliable.

## Controls

| | returned |
|---|---|
| **REPEAT (+)** | `consistency` over 8 runs → exits **[0]** — one distinct result, so the harness reports `identical` when the subject is deterministic |
| **REPEAT (−)** ⭐ | a clock-seeded coin flip over 32 runs → exits **[0, 1]**. **Both directions**, because a harness that always says "identical" would pass the positive control |
| **TREE CLEAN** | `git status --porcelain` before the round and after **every** run; non-empty would be recorded and restored, never silently cleaned |
| **ABORT** | a run that could not be cleaned exits 1 — a measurement that leaves the repository damaged is not a measurement |
| reproducibility | two runs **byte-identical** (`0c7f8903ce9d`) |

⚠ **The round's own directory is excluded from the start-clean check** — which is **R376's finding
applied to myself one round later**. `_isolated`'s criterion counted the probe the selftest itself
wrote; a start-clean check counting this round's own uncommitted source would make the same error and
be unrunnable by construction.

## Register

| criterion | status |
|---|---|
| **WHICH internal step varies** | **N/A** — needs tracing inside the subject. This measured **that** it varies with state, never where |
| **the state variable** | **UNVERIFIED** — the corpus hypothesis is labelled and untested |
| **the other five gates** | **N/A** — their bisects rest on the same untested reproducibility assumption. Named as a consequence, not measured: this round ran **one** subject |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"attack_every_check moved from exit 1 to exit 2 across this session and I cannot attribute that —
> I both repaired `_isolated` and used its worktree."*

**The worktree is ruled out by measurement over all seven relevant files, and the check is
deterministic at a fixed commit, so the variation is tree-state dependence and nothing about
`_isolated` is required to explain it.**

Artifact: `results/r377_flicker.json`, source-stamped.
