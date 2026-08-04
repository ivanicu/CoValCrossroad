# R406 — "better than EVERY prompt-blind set" was tested against the 99th percentile

**The decision this makes safe:** *why do two committed rounds disagree about whether the definition
admits its own instance?* **Because one of them called a p99 bar "every".**

## Result — `W_EVERY_WAS_A_TAIL`. Three controls pass. **No GPU, and no run at all.**

| | |
|---|---:|
| R327 reading A, *"better than **EVERY** prompt-blind set of that size"* | reference `0.5546019830` |
| **max** over the 1,820 blind subsets (R331) | **`0.5574753088`** |
| p99 over the same subsets | `0.5546396620` |
| **gap (max − ref)** | **`+0.0028733259`** |
| ref_A brackets to | **(p90, p99)** — *below* the committed p99 |

**Between 1% and 10% of the 1,820 subsets beat the bar the word "EVERY" was tested against** —
between **18 and 182** of them.

> ⚠ **A bracket, not a count.** R331 committed **seven order statistics**, not 1,820 scores, so
> "18 subsets" would be precision the artifact does not carry.

## ⛔ R405's NEXT said this needed a run. It did not.

R405 closed with *"needs the 1,820 subset scores under both, which R360's artifact does not carry."*
**But R331 committed the blind distribution's order statistics — including `max` — over the same
1,820 subsets, and R327 committed the reference it used.** Two rounds, neither citing the other, both
numbers on disk.

**This is the campaign's own recurring lesson, one more time: before paying for a measurement, count
what the committed artifacts already contain.**

## ⚠ The unit discipline is the point, not a caveat

| | |
|---|---|
| **the claim's unit** | *the **maximum** over 1,820 blind subsets* |
| **the instrument's unit** | *the best **held-out** of 1,820* |

**Not the same object.** And **no control in R327 could have caught it** — its controls were all
about **ordering** its three readings, and *an ordering can be perfectly correct while every rung is
mislabelled.* The failure table's remedy is exactly this: write the two units as separate strings and
require them to be **equal**, before the control is designed.

## ⭐ It resolves R405's disagreement exactly

R327 admits `coval_core` **because it cleared a 99th-percentile bar**. R360's top cell does not,
**because it did not clear the maximum.** Both rounds are internally correct; the gap between them is
`0.0029` in A2 units, and it decides whether the definition admits its own instance or nothing.

## Controls

| | returned |
|---|---|
| **MONOTONE (+)** | `min < p25 < med < p75 < p90 < p99 < max` — `PASS`. A non-increasing order-statistic vector is not one, and every percentile claim would be meaningless |
| **CROSS (+)** ⭐ | R331 records the published reference at pctile **93.74**; using **only** the stored statistics it brackets to **(p90, p99)** — `PASS`. **Two artifacts checked against each other, not one against itself** |
| **ABSURD (−)** | a value below `min` brackets to `(None, 'min')` — `PASS`, so the bracketer can return an extreme rather than always landing mid-grid |

## ⚠ This does NOT retract R327

**Its reading B and C results stand. Its finding that the readings DIVERGE stands and is
strengthened.** What is corrected is the **name of one rung**: reading A is not the universal
reading, **it is a p99 reading**, and the genuinely universal reading has never been run.

## Register

| criterion | status |
|---|---|
| **an exact count above ref_A** | **N/A** — R331 committed order statistics, not scores. Bracketed |
| **deciding which reference is correct** | **N/A** — an act of definition, not a measurement |
| **re-scoring the subsets** | **N/A** — and the point of the round is that it was unnecessary |

## The sentence I can no longer write

> *"reading A is the plain-English universal reading"* — **it is a p99 reading wearing the word
> every.** The universal reading of clause ② has not been tested by anyone, including me, and the one
> round that claimed to had a reference `0.0029` short of it.

Artifact: `results/r406_universal_not_universal.json`, source-stamped. Labelled a **DERIVATION**:
`max − ref` on two committed scalars could not have come out otherwise; what was not forced is
whether they coincide.
