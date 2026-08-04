# R416 — R415's "re-run pairs" scored different criteria. Its framing was wrong one round after I published it.

**The decision this makes safe:** *is R415's 0.116 a scoring floor?* **No — it is a rule-level floor,
and the disjunction R415 offered resolves onto the branch it listed and never tested.**

## Result — `W_DIFFERENT_CRITERIA`. **5 of 5.** **No GPU.**

| arm | `core_*_08b` | `core_*_08bR` | identical | **prompts whose criteria changed** |
|---|---|---|---|---:|
| `greedy_k4_fit1` | `710cb87cbb57` | `4193a6629498` | False | **99.1%** |
| `indep_k4_fit1` | `90aa6a73d99b` | `97e47fe6ba68` | False | **98.9%** |
| `oracle_k4` | `22c61b3aefbe` | `635698235fd1` | False | **91.1%** |
| `topvar_k4` | `7f0c03d330ea` | `c448f26ee8e3` | False | **99.4%** |
| `topwvar_k4` | `0efec4beccc7` | `7a7b85361838` | False | **99.6%** |

**Not a whitespace difference — a near-total re-selection.**

## ⛔ The check was one line and I published before running it

R415 called the pairs *"same arm, same judge, **same code**, different run"* and offered a disjunction
for the cause: *the pipeline is wildly unstable* **or** *two configurations share a filename*. **Each
arm has a committed core JSON — the criterion set that was scored — and they differ.** The second
branch was true, checkable against committed files, and **I listed it without testing it.**

## The ledger

| | |
|---|---|
| **SURVIVES** | the **magnitude** — re-running the same *rule* end to end shifts mean A2 by up to **0.116489**, still **13×** the effect |
| | that these files are **not usable as replicates** — now **established** rather than offered as a disjunction |
| | the **2B floor is still UNMEASURED** — unchanged |
| **DOWNGRADED** | *"the pipeline is wildly unstable"* is **not supported**. The shift is fully compatible with different criteria and **no scoring instability at all** |
| | *"same arm, same code, different run"* corrected in **R415's README, `DEFINITION.md` and the front page** |
| **RESIDUAL** | **selection vs scoring cannot be split** without re-scoring *identical* criteria — that needs the GPU, and it is the honest remainder |

## ⚠ Ruling out one branch's evidence is not evidence for the other

**This does not show the pipeline is stable.** It shows R415's measurement never bore on that
question. *That inversion is the easy error and it is named rather than left available.*

## Controls

| | returned |
|---|---|
| **SELF (=)** | a core JSON hashed against itself is equal — `PASS`. A hash returning different values for the same bytes would make every *"differs"* meaningless |
| **SHAPE** | both members of every pair are structurally comparable — `True`. Otherwise the round would be differencing incomparable objects |
| **QUANTIFIED** ⭐ | a hash mismatch says only *"not identical"* — compatible with one byte of whitespace **or** a total rewrite, which imply different corrections. **The per-prompt change share is computed: 91–99.6%** |

## Register

| criterion | status |
|---|---|
| **splitting selection from scoring** | **N/A** — needs a re-score of identical criteria, i.e. the GPU |
| **the 2B floor** | **UNMEASURED** — unchanged by this round |
| **a claim that the pipeline is stable** | **NOT MADE** — ruling out one branch is not evidence for the other |

## The sentence I can no longer write

> *"same arm, same judge, same code, different run"* — **the criteria changed on 91–99.6% of prompts.**
> I wrote "same code" from a filename and published a floor that measured something else.

Artifact: `results/r416_criteria_differ.json`, source-stamped.
