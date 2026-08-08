# R1091 — clause ③ is **NOT EVALUABLE** for the released cores. The record lacks the artifact.

**The decision this round makes safe:** whether the definition contains any clause that separates a
core from the baselines it shares the `always` block with. **Unanswerable from the committed record**
— and the wall was checked, not asserted.

## The wall, named and located

Clause ③ is *consumes no prompt-specific human labels*. Its only sound mechanical proxy is the arm's
**criterion-TEXT selection** across the 968 prompts — R1056's `n_distinct` over `core_<arm>.json`.

⛔ **The three released cores have no such file.** `core_coval_core_sham.json` exists;
`core_coval_core.json`, `core_coval_core_2bA.json` and `core_coval_core_2bB.json` do not. The proxy
types **31 of the 35** `always` arms and cannot reach the objects the question is about.

**UNVERIFIED — never "the clause does not separate."** A proxy that cannot see the subject licenses
nothing in either direction.

**What it would require:** a committed `core_<arm>.json` for each released core.

## ⛔ And my substitute measured a different quantity — the cross-check is what caught it

Finding the file missing, I substituted `sat_<arm>.npz`, which every round in this arc already reads.
**It holds POSITIONAL indices (0…k−1), not criterion text.**

| arm | distinct **text** selections | distinct **index** patterns |
|---|---:|---:|
| `generic` | **1** | 1 |
| `greedy_k12_fit1` | **968** — a different rubric on every prompt | **9** |

**An arm that rewrites its selection on all 968 prompts looks nearly fixed under the index count.**
A cross-check between the two routes agreed on **2 of 31** arms, and that disagreement is the only
reason a wrong number was not reported. Two instruments claiming the same quantity and disagreeing on
94% of the population is not a discrepancy to average — one of them is measuring something else.

## The proxy ledger, stated before it was used

| | |
|---|---|
| **PROPERTY** | clause ③ — consumes no prompt-specific human labels |
| **PROXY** | `n_distinct` criterion-**text** selections across the prompts |
| **SOUND** | `n_distinct == 1` ⇒ the arm cannot be reading the prompt |
| **UNSOUND** | high diversity ⇏ *reads the conversation* — reported as *not prompt-blind by this test* |
| **WITNESS** | `generic`, `genericpool16` = 1 (R918's `fixed` set, recovered) |

## What the round did establish

Where the proxy reaches, it behaves: the two released comparators sit at **1**, and
`greedy_k12_fit1` — which shares the `always` block with the cores — sits at **968**. So the block
spans the full range of prompt-specificity, and **clause ②′ admits both ends of it.** That much
stands; what cannot be said is where the cores fall.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| clause ③ for the released cores | **N/A** | a committed `core_<arm>.json` per core |
| whether a varying selection varies *because of* the prompt | **N/A** | the proxy's unsound direction; an intervention on the generator |
| clause ①'s separating power | **N/A here** | it is a size clause; R987 settled it |
| cross-release | **N/A** | a second release |

`run.py` · `results/clause_separation.json`
