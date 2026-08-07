# R697 · how many non-resolutions were silence? — **zero, after three instrument repairs**

**⭐⭐⭐ The kill fired: **no** co-located cell in this arc reports a non-resolution from a design whose
floor exceeded 0.05. R495 is **singular**, and R696's closing claim narrows to it. **The trajectory
is the finding: 23 → 38 → 0 across three successive filters, and the first two would each have
supported "a class".****

> **⛔ COUNTS RETRACTED BY R698 (check #300). CONCLUSION STANDS.** Every population figure in the table below is wrong in two ways. **① I wrote them from a PRE-PATCH run and never re-read the artifact this round had just written** — 79/44/8 in prose against 10 admissible in the JSON. **② This round sweeps the arc's `results/*.json` and its own artifact is one of them**, so its population grows whenever anything is committed. R698 measured it: **admissible falls 14 → 4 when R697's own output is excluded — 71% of the population was itself.** ⭐ **The verdict is 0 in every exclusion regime**, so the kill fired on the world and not on the denominator. Read the conclusion; do not quote the counts.

## THE THREE FILTERS, EACH A GENUINE CORRECTION

| filter | cells | what it removed |
|---|---|---|
| co-located `(n, p, resolve)` | 79 | — |
| **p must be an integer multiple of `1/n`** | 44 | 35 where `n` is a **sample size**, not a null cardinality (`R431` n=2 beside p=0.87) |
| **p = 1.0 is a multiple of everything** | **8** | 49 **degenerate** cells where the filter cannot discriminate — **UNVERIFIED as to instrument, reported separately, never counted** |

**Intermediate counts of "could not have resolved": 23, then 38, then 0.** *Both earlier numbers were
inflated by `n` fields that are not null cardinalities.* **The `n` field in this corpus is not a
stable quantity — that is the round's real result.**

## THE RESULT

| | |
|---|---|
| admissible cells (0 < p < 1) | **8** |
| reported not resolved | 2 |
| ⭐ **could not have resolved** (two-sided floor > 0.05) | **0** |
| one-sided sensitivity | **0** |
| cells at their own floor | 6 occurrences, **1 distinct** `(n=126, p=0.0159)` |

Registered **A 18 [3,60] → 8, INSIDE (−10)** · **B 2 [0,10] → 0, INSIDE (−2)** · **directional
FAILS** · **kill FIRES.**

**Controls:** POSITIVE — R361's 0.8B cell found (n=126, p=0.2857) and **correctly not flagged**
(floor 0.0159 ≪ 0.05). **g=0** — a synthetic n=10, p=0.3 cell **is** flagged (floor 0.20) — *the
detector returns both values*. NEGATIVE — a resolve flag with no p is not counted. PLACEBO —
identical.

## ⭐ THE "AT FLOOR" CELLS ARE ONE MEASUREMENT, COPIED
6 occurrences, **1 distinct `(n, p)`** — R361's `2B` cell at `p = 0.0159 = 2/126`, re-quoted in R683,
in this round's own artifact, and back into its own scan. **R680's copy finding, live and
self-referential.** *And R361's 2B result sitting exactly at its floor means it is the most extreme
outcome that design permits — informative in itself, and not something a count of 6 conveys.*

## ⚠ CO-LOCATION WAS MY OWN DISCRIMINATING RULE, AND IT WAS NOT SUFFICIENT
R695's lesson was *"a loosened search succeeds at something else"*. I named co-location as the fix in
this round's **pre-registration** — and it still admitted 35 sample-size `n`s and 49 degenerate cells.
**One round after naming the failure mode, a stricter rule chosen in advance was still two notches
too loose.**

## IMPOSSIBLE HERE
Whether a round's `n` counted draws or exact cells is **not recorded anywhere**. The multiple-of-`1/n`
test infers it; it cannot read it.

## NEXT
The `n` field resolved to three different quantities across this arc — null cardinality, sample size,
and spec count (`results/floors.json`, fields `n_dropped_not_multiple` and `n_degenerate_p1`). Check
whether the rounds that store a null cardinality use a distinguishable key name from those storing a
sample size, by tabulating key name against the multiple-of-`1/n` outcome. A key name that predicts
the outcome would make this a gate; one that does not means the ambiguity is unremovable by
convention.
