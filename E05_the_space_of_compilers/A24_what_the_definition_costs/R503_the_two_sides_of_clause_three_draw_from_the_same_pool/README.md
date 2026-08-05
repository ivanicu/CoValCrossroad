# R503 · Both sides of clause ③ draw from the same pool — so there is no textual property to check

**Decision this makes safe:** how expensive reading A (drop ③) actually is, and whether the announced
"inspect a label-reader's criteria" round is worth writing. **It is not — it is answered by
construction, and it was withdrawn before being written.**

## The census

| arm | family | criteria | **verbatim from the prompt's own rubric** |
|---|---|---|---|
| `oracle_k4`, `greedy_k4_fit1`, `topw_k4`, … (10 arms) | ③-**excluded** | 3,872 ea. | **100.0%** |
| `random_k4_s0/s1`, `random_k3_s0`, `random_k8_s0` | ③-**admissible** | 2,904–7,670 | **100.0%** |
| `gen` | ③-admissible | 3,868 | **0.0%** |
| `generic`, `genericpool16` | ③-admissible | 3,872 / 15,488 | **0.0%** |
| `promptecho` | ③-admissible | 1,592 | 0.1% |

**Controls.** Placebo: the rubric against itself returns **exactly 1.0** — without it the whole table
is void. Positive: `gen`, a generator, returns **0.0000**. Negative: `generic`, fixed and
prompt-blind, returns **0.0000**. **Two independent ways for the instrument to come back low, so
100% is a measurement and not a tautology.** Specification: three matching rules (exact / stripped /
case-folded), **0 arms move by more than one point.**

## What it settles

⭐⭐⭐ **On this site the two sides of ③ inhabit the same object space and differ only in the
selection map.** A label-reader and a random draw both emit *verbatim human-written rubric items*;
what separates them is **which four** they pick. **That is ③'s irreducibility stated as sharply as
this release allows: there is no textual property to check, because there is no textual difference to
find.** It also localises R465's result — two selectors emitting identical criteria on 9 of 967
prompts is not a coincidence, it is what a shared pool makes likely.

⭐⭐ **And it re-prices reading A.** Dropping ③ admits arms whose criteria are **verbatim items a
human evaluator wrote** — the *right* criteria, selected for the *wrong reason*. **"It admits
label-readers" made A sound like it admits junk. It does not.** The cost of A is a **provenance**
cost, not a quality one, and the fork's A-column is corrected accordingly.

## ⛔ The round this killed, at zero compute

The previous report's next gradient was: *"nobody has asked what a label-reader's criteria LOOK
like — if `oracle_k4`'s are recognisably degenerate, A is cheap."* **Rung 1 of the attack ladder
answers it before any of it runs:** they are not degenerate and cannot be, because they are the
rubric. **Withdrawn before writing, which is the cheapest possible place to lose a round.**

## The bound

Only **verbatim** membership is tested. Whether a criterion is *semantically* in the pool
(paraphrase) is not — that needs an embedding or a judge, and each would be an instrument this round
would then have to validate. `coval_core` has no criterion-text file on this release and is absent
from the table.
