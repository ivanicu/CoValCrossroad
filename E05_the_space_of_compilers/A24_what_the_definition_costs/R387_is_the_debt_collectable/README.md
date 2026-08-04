# R387 — the debt is collectable: 9 of 9 decided rounds still re-run, none fail

**The decision this makes safe:** *is the missing-findings debt payable, or is it a loss?*
**Payable.** The 243 is a backlog with a known unit cost — re-run, read, write.

## Result — `W_COLLECTABLE`. Both controls PASS. Two runs byte-identical. **No GPU spent.**

| round | outcome |
|---|---|
| R21 · R24 · R28 · R29 · R30 · R31 · R32 · R33 · R34 | **RAN** (exit 0) |
| R23 · R26 · R27 | **TIMEOUT** (>90 s — *not* a failure) |
| — | **FAILED: 0** |

**RAN 9 · FAILED 0 · TIMEOUT 3** — decided 9 of 12, and every decided one runs.

## ⛔ R386's proposed test was my judgement again

It asked whether a finding is still *recoverable* from what was persisted. **I would be the one
deciding whether a JSON blob supports a sentence** — self-review, void rather than weak, the same
trap R385's NEXT walked into. Replaced by a question the machine answers:

> **Can the round still be re-run?**

That is the strongest form of recoverability: if `run.py` executes, its output can be read and the
finding written. **The estimand is an exit code, not an opinion.**

## ⛔ Three of my own defects, all caught by the controls before any subject was scored

**① The worktree was at an old commit.** It sat where R375 left it (`487c794`), so every round
committed since **did not exist in it** — and both controls returned `MISSING`, which is **not**
`FAILED`. Had the classes been merged, twelve subjects would have scored as broken corpus.

**② The negative probe was erased before it could run** — and `_isolated`'s own docstring warns of
exactly this:

> *"restore_first=False EXISTS BECAUSE THE SELFTEST SILENTLY DID NOTHING … the saboteur probe, which
> is untracked by construction, was erased before it could execute."*

**I quoted a confession from a different gate one round ago and then walked into its twin.**

**③ The negative control re-implemented the classifier and disagreed with it.** A broken import
returns `EXC ModuleNotFoundError`, which the real classifier maps to **FAILED** and my inline copy
mapped to itself. *A control that re-implements the check it validates tests the copy, not the
check.* Factored so both controls and every subject go through **one** path.

## Controls

| | returned |
|---|---|
| **HARNESS (+)** | `R384` — written and executed **this session** — returns **RAN** |
| **HARNESS (−)** | a deliberately broken import returns **FAILED** (`EXC ModuleNotFoundError`). Both directions, because a harness reporting RAN for everything would pass the positive control |
| **ISOLATION** | every subject runs in a git worktree restored between subjects — these scripts **write to their own `results/`**, so running them live would rewrite committed artifacts and the measurement would damage what it measures |
| **TIMEOUT** | its own class. **A slow round is not a dead one**, and folding the two would have manufactured the uncollectable verdict |
| reproducibility | two runs **byte-identical** (`62e36b898b5e`) — including the timeout set, which was the real risk |

## Register

| criterion | status |
|---|---|
| **whether a runnable round yields a READABLE finding** | **N/A** — executability is **necessary, not sufficient**, and sufficiency is the judgement I may not make alone. *This measured that the door opens, never what is behind it* |
| **the other 217** | **N/A** — these are the **12 oldest of 229**, chosen because age is the strongest reason to expect rot. A failure rate here is a **lower bound on health, upper bound on damage** |
| **the 3 timeouts** | **UNVERIFIED, not failed** — they exceeded a 90 s budget, which is a fact about my budget |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] … if the artifact no longer supports stating what the round found, then the debt is
> not merely unpaid but uncollectable."*

**Zero of nine decided rounds fail to execute. The artifact does not have to support it — the code
still runs, and the finding can be read off a fresh run.**

Artifact: `results/r387_rerunnable.json`, source-stamped.
