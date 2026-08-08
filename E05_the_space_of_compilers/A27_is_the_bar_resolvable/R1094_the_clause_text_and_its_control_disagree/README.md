# R1094 — ⛔ **R1093's verdict is RETRACTED.** Clause ③'s text and its own control name different properties.

**The decision this round makes safe:** whether the released core violates clause ③. **The question
has two answers and the clause cannot choose between them** — and the two readings disagree on
*exactly* the three released cores and on nothing else.

## The witness, read from the generator rather than from a name

`corebench/select_core.py:19`

> `oracle_k` — **the k that best fit the human target. LEAKY BY CONSTRUCTION**

and line 102 loads **`data/comparisons.jsonl`** — the held-out pairwise rankings — for
`greedy_k`, `indep_k`, `oracle_k`, **and for no other rule**. The definition's own committed control
is *"`oracle_k4` fails ③"*. **So ③ operatively excludes consuming the EVALUATION TARGET**, not "a
human was involved in authoring the criteria".

## ⛔ What R1093 got wrong

| | R1093's unit | the clause's operative unit |
|---|---|---|
| ③ excludes… | *a human was involved in authoring the criteria* | *the arm consumes the evaluation target* |

**Same words, different referents.** That is this arc's one error class — representation for
referent — committed one round ago, in the round whose whole point was quoting the card rather than
inferring from it.

**RETRACTED: the verdict "clause ③ is FALSE of the released core".**
**STANDS: R1093's card quotes and its schema measurement** — `coval_core` items carry `criterion`
alone over all 986 conversations, `coval_full` carries `rubric_item_id`/`criterion`/`scores`, and
there is no per-item provenance link. Those were measurements and they are unaffected.

## ⭐ The finding that replaces it — the two readings, and where they part

Over R1090's 35-arm `always` block:

| reading | source | excludes |
|---|---|---:|
| **(a) LEAKAGE** — consumes the held-out rankings | the generator's rule list | **19** |
| **(b) AUTHORSHIP** — consumes any prompt-specific human label | the dataset card | **22** |
| **they disagree on** | | **3** |

**The three arms they disagree on are `coval_core`, `coval_core_2bA`, `coval_core_2bB` — the released
cores, and nothing else.**

⭐⭐ **And the clause's own control cannot separate the readings, because `oracle_k4` fails under
both.** A control that both candidate readings pass is not a control between them. **So the
definition's instance is admitted or excluded depending on a choice the definition never makes.**

**A definition whose text and whose test disagree on its own instance is not yet a definition.**

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE `oracle_k4` is excluded under **both** readings — a reading admitting it is not a candidate | PASS |
| POSITIVE the generator names the leaky rules **and** the target file | PASS |
| g=0 `generic` — a fixed rubric reading neither target nor prompt — is admitted under both | PASS |
| NEGATIVE the two readings are built from **different sources** (generator vs card), not one wearing two names | PASS |
| PLACEBO each reading against itself excludes an identical set | PASS |

**Noise floor: none.** Both readings are membership rules over a committed list.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| which reading was intended | **N/A** | the author's state at the time; the round reports the ambiguity rather than adjudicating |
| whether the human review the card describes occurred | **N/A** | the review record, not shipped |
| cross-release | **N/A** | a second release |

`run.py` · `results/two_readings.json`
