# R419 — the scoring-only floor is exactly zero, and that locates R415's 0.116 entirely in selection

**The decision this makes safe:** *does the scoring pipeline add noise to any A2 number?* **No. Two
runs of identical criteria are bitwise identical on all 200 prompts.**

## Result — `W_FLOOR_ZERO`. Pair check + self control pass. **`--limit 200`, 3,168 calls each.**

| | |
|---|---:|
| mean difference | **+0.000000000** |
| mean \|difference\| | **0.000000000** |
| sd | **0.000000000** |
| **max \|difference\|** | **0.000000000** |
| against R408's effect `+0.009002` | **0.00e+00** |
| against R415's rule floor `0.116489` | **0.00e+00** |

## ⛔ What it settles, across four rounds

| round | claim | fate |
|---|---|---|
| **R415** | `0.116489` is a *pipeline noise floor* | **located entirely in SELECTION** — scoring contributes exactly nothing |
| **R416** | the pairs' criteria differed on 91–99.6% | **confirmed as the whole cause** |
| **R417** | source has no stochastic step → floor *inferred* near zero | **inference promoted to measurement** |
| **R419** | — | **every A2 number in this campaign is a fixed quantity given its criteria** |

## ⭐ Why the pair could be trusted at all

`--core coval_core` reads criteria **deterministically from the rubric**, so two runs share them **by
construction** — and the provenance field added two rounds ago **proves** it rather than assuming:
both artifacts carry `criteria_sha256 = d9a198b61aef23d5` over **3,828 criteria**.

## ⛔ An override was available and was not taken

The first `B` run carried a **different `producer_sha256`** than `A`. The only difference between
those producer versions is **where a hash is computed** — provably untouchable by a score — so waiving
the pre-registered pair check was defensible.

**It was not waived. `B` was re-run on the current code, at a cost of one minute.**

> **A rule written one turn earlier should not be bent when honouring it is cheap. That is the whole
> content of a pre-registration.**

## Controls

| | returned |
|---|---|
| **PAIR (=)** ⭐ | same `producer_sha256` (`1c6bbfeb…`) **and** same `criteria_sha256` (`d9a198b6…`), **re-read from the files** rather than trusted from the requeue |
| **SELF (−)** | `A` against itself → `max\|d\| = 0.0e+00` — distinguishes a pipeline floor from a noisy loader |
| **SCALE** | the floor is placed on **both** scales the campaign uses — R408's effect and R415's rule-level number — rather than left bare |
| **PROMPT MATCH** | 200 shared prompts, printed |

## ⚠ Scope — and it is now *statable* rather than guessed

**One batch (32), one judge, 200 prompts.** Batching is a known mover R417 flagged, and it is held
**fixed** here. **This is the floor at this configuration** — which is exactly the scope the
provenance field now makes expressible, and could not have been stated at all three rounds ago.

## Register

| criterion | status |
|---|---|
| **the floor at other batch sizes** | **N/A** — one batch. Named, and now recorded in the artifacts |
| **generalisation from 200 to 968 prompts** | **N/A** — these runs used `--limit 200` |
| **other judges** | **N/A** — one |

## The sentence I can no longer write

> *"the committed artifact is one draw"* — **given its criteria, it is the value.** The draw-to-draw
> spread I spent four rounds worrying about is exactly zero, and all of the movement was in which
> criteria got selected.

Artifact: `results/r419_scoring_floor.json`, source-stamped, with both runs' full provenance embedded.
