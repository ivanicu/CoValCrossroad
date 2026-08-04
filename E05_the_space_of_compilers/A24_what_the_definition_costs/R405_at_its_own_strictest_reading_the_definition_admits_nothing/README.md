# R405 — UNVERIFIED. The sweep does not order readings by strictness, so "the strictest reading" is not a cell.

**The decision this makes safe:** *can the emptiness at the top of the reference sweep be reported as
the definition's verdict under its own plain English?* **No — and the reason explains a standing
disagreement between two committed rounds.**

## Result — `UNVERIFIED_SWEEP_NOT_A_STRICTNESS_ORDER`. One control PASSED, one FAILED. **No GPU.**

| control | returned |
|---|---|
| **PUBLISHED (+)** | the published-reference cell reproduces the published five **exactly** — `PASS`. So the sweep and the headline *are* about the same object |
| **MONOTONE** | a stricter reference must admit no **more** arms — **`FAIL`** |

**The break:** `pct 75.0 (n=5)` → `pct 80.0 (n=6)`, **gaining `generic`** — which *is* a blind set.

## The curve that was computed anyway

| pct | n | admitted ∧ ③a |
|---:|---:|---|
| 0.0 | 9 | `coval_core`, `gen`, `generic`, `topw_k1/2/3/4/6/8` |
| 75.0 | 5 | `coval_core`, `topw_k3/4/6/8` |
| **80.0** | **6** | **⚠ `generic` returns** |
| 93.5 *(published)* | 5 | `coval_core`, `topw_k3/4/6/8` |
| 98.5 | 2 | `coval_core`, `topw_k6` |
| **100.0** | **0** | **∅ — survivors are exactly the four label-readers** |

## ⛔ What is blocked, and what is not

**The observation stands:** at `pct = 100` the arms surviving clause ② are exactly
`greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4`, `oracle_k4_fit1` — **the four that read the labels** —
so clause ②∧③a is empty there.

**What is blocked is calling that "the strictest reading's verdict."** A percentile that can *gain*
arms as it rises is not a strictness ordering, so `pct = 100` is not "the strictest cell", it is
merely the last one. **Reporting the emptiness as a verdict would be printing a headline while a
control two lines above says the round is unreadable** — failure-table row, sub-kind ①.

## ⭐ And the failure explains a standing disagreement

R327's reading A — *"better than EVERY prompt-blind set"* — admits **`{coval_core}`**, using the best
**held-out** of 1,820. R360's sweep at `pct = 100` admits **no** non-label arm, using the in-sample
maximum. **A held-out maximum is lower.**

> **So whether the definition admits its own instance or nothing at all turns on held-out vs
> in-sample — a third under-specification, named in neither round and decided by no sentence of the
> definition.** Both rounds are right; they are answering different questions that the same English
> sentence licenses.

## ⛔ The phenomenon is already in the definition; the consequence is not

`DEFINITION.md` records *"at 6 of 9 k, **stronger** references admit blind sets again,"* replicated at
a second judge — and the arm gained at `pct 80` is `generic`, a blind set. **The phenomenon was
known. What is new is that it makes "clause ② at its strictest reading" ill-defined**, which is
exactly the room in which R327 and R360 disagree.

## ⚠ Reporting the diagnostic on a failed control is not moving the goalpost

The pre-registration fixed the **verdict** on failure — `UNVERIFIED`, never `CONFIRMED` — and said
nothing about printing less. **Withholding the reason would make the failure unusable by the next
round**, which is the opposite of what a three-valued verdict is for.

## ⛔ And this round writes NOTHING into `DEFINITION.md`

An `UNVERIFIED` round has not earned a line in the definition. The emptiness is recorded here, in its
own artifact, with the reason it is not yet a claim.

## Register

| criterion | status |
|---|---|
| **deciding held-out vs in-sample** | **N/A** — an act of definition. Adjudicating it here would be tuning the definition to whichever answer I found first |
| **a held-out/in-sample reconciliation** | **NEXT** — needs the 1,820 subset scores under both, which R360's artifact does not carry |
| **re-scoring any arm** | **N/A** — needs the judge; this composes committed cells |

## The sentence I can no longer write

> *"at its strictest reading the definition admits nothing"* — **there is no strictest reading.** The
> ordering I assumed the percentile gave me is not there, and I would have reported a clean, dramatic
> result built on it.

Artifact: `results/r405_universal_reading.json`, source-stamped, verdict `UNVERIFIED`.
