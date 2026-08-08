# R1092 — ⛔ **R1091's wall is RETRACTED.** The file was in the release the whole time.

**The decision this round makes safe:** whether clause ③ is permanently unevaluable here. **It is
not, and it never was.** R1091 searched a *derived* directory and stopped.

## The retraction

R1091 reported that the released cores have no committed criterion-TEXT selection, so clause ③ could
not be evaluated for them. It searched `corebench/results/core_<arm>.json`.

⛔ **`data/conversation_rubrics.jsonl` carries a top-level `coval_core` key on 986 of 986
conversations**, holding the core's criterion texts for that conversation. **The artifact R1091
declared absent is in the release, one directory from where it looked.**

**R1091's own NEXT named this gap** — *"a wall checked in one directory is not a wall checked in the
release"* — and it was right. §4's *a wall never checked*, committed by me and caught one round later
**by the sentence I wrote warning about it.** That is the loop working, and it is also the reason the
warning had to be written rather than felt.

**Status: RETRACTED, not downgraded.** R1091's identification claim was a universal negative and one
file refutes it.

## What the file says

| | |
|---|---:|
| conversations | **986** |
| carrying `coval_core` | **986** |
| **distinct TEXT selections** | **986** |
| rubric sizes | `{4: 942, 3: 43, 2: 1}` |
| criteria shared by the first 50 conversations | **0** |
| SHAM — `coval_full`, same file, different key | 986 |

**The core rewrites its rubric on every conversation** — a different criterion set each time, with
nothing in common across the first fifty. Its `k` is 4 on 942 of 986, which is where the definition's
retired "four criteria" clause came from.

## ⚠ And clause ③ is STILL not settled — for a different reason than R1091 gave

**The units are not equal.** `n_distinct` measures **prompt-specificity**; clause ③ names **human-label
consumption**. A *generated* per-prompt rubric is maximally prompt-specific and consumes **no human
labels at all**, so 986 distinct selections neither establishes nor refutes ③.

**What settling it would require:** a record of which criteria came from a human. The rubric file does
not carry one.

⭐ **So the correct state of ③ moves from *"not evaluable — the artifact is missing"* to *"not
settled — the available proxy measures a different property."* Both are UNVERIFIED and they are not
the same UNVERIFIED**, and the difference decides what the next round would have to build.

## Controls — 4, all green

| control | result |
|---|---|
| POSITIVE a known per-prompt criterion-text file is found (`core_generic.json`) | PASS |
| g=0 a key that does not exist yields **0** conversations, not a default | PASS |
| NEGATIVE `annotators.jsonl` is not reported as a selection table | PASS |
| PLACEBO re-reading the file returns identical counts | PASS |

**Noise floor: none.** This is a deterministic file read, and the round says so rather than inventing
a resampling for it.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| clause ③ itself | **N/A — for a new reason** | a record of which criteria came from a human |
| the earlier reason (*the artifact is absent*) | **RETRACTED** | — it was never absent |
| cross-release | **N/A** | a second release |

`run.py` · `results/the_wall_retracted.json`
