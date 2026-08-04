# R430 · I blamed the null. It was the **weighting** — and I had committed the wrong diagnosis two hours earlier

**The decision this round makes safe:** whether the R427↔R429 ranking disagreement is a defect in a
null construction (which would need a synthetic corpus to adjudicate) or a declared-nowhere choice
of aggregation weight (which needs nothing but arithmetic). **It is the weight.**

## Result — **`W-WEIGHTING`** · **`W-STABLE`** · **`W-NULL-NOISE`**

The R427↔R429 comparison changed **two** things at once:

| | R427 | R429 |
|---|---|---|
| aggregation | **CONV** — mean over conversations of per-conversation means (`lib/cluster.py`) | **INTER** — pooled over interactions |
| null | **PERM** — one realised within-stratum permutation | **ANLY** — the closed-form expectation |

A conversation with 8 interactions counts **once** in one and **eight times** in the other. The 2×2,
scored by whether each cell reproduces R427's committed per-pair null:

| cell | reproduces R427 |
|---|---|
| **CONV/PERM** (R427's own method, both axes) | **8 of 10** |
| **CONV/ANLY** | **9 of 10** |
| INTER/PERM | 2 of 10 |
| INTER/ANLY | 2 of 10 |

**The two nulls agree to ~0.002. The two weightings differ by ~0.013.** R429's `W-BIAS` attribution
is **retracted**.

## ⛔ Why the reproduction control is the load-bearing one

`CONV/PERM` **is** R427's method on both axes. Had it failed to reproduce R427, no other cell's
agreement would mean anything and the correct output would have been `W-THIRD` — *the decomposition
is incomplete* — rather than the closest cell. **Picking the closest cell is how a decomposition
becomes a narrative.** It passed at 8/10 against a pre-registered threshold of 8.

## What survives, checked *before* the retraction was written

R429's headline was computed with the pooled weighting — so if the weighting is the mechanism, the
headline used one. Recomputing under both, **in the same commit as the retraction**, because a
correction that does not carry the corrected number is this campaign's `retraction obliges a re-run`
failure:

| weighting | rank 1 vs rank 2 | Δ | resolved |
|---|---|---|---|
| **CONV** | `generic\|vacuous` vs `randblind_s0\|randblind_s2` | **+0.0226 [+0.0083, +0.0374]** p=0.0027 | **yes** |
| **INTER** | *same pair* | **+0.0234 [+0.0107, +0.0367]** p=0.0003 | **yes** |

**`W-STABLE`: R429's headline survives; only its attribution was wrong.** ⚠ The two Δ are *not*
equal — the number is weighting-dependent and must be quoted with its weighting, which R429 did not.

## ⛔ And "ranks 5–10 are not quotable" was itself a subtraction, not a measurement

R429 wrote it from a comparison where **both** axes moved. Measured per axis:

| axis | ranks that move |
|---|---|
| **weighting** (null fixed at ANLY) | **2 of 10** — positions 9, 10 |
| **null** (weighting fixed at CONV, 30 draws) | **median 4**, IQR 2, range 0–6 |

Per-position movement over 30 permutation draws: **positions 1, 2, 3 never move.** Position 4 moves
**10/30**; 5 → 16/30; 6 → 7/30; 7 → 16/30; 8 → 16/30; 9 → 13/30; 10 → 13/30.

**`W-NULL-NOISE`.** The mid-table ordering is *permutation-draw* noise: a different draw of the
*same* null reorders it. R429's own sentence named the wrong boundary (**4**, not 5) and the wrong
cause (**the draw**, not the construction).

## Controls, and what each returned

| control | returned |
|---|---|
| SEEDS — 60 permutation seeds | **60 distinct** values ✅ (the flag is wired) |
| g=0 — identity permutation | **0.767182** = raw agreement **0.767182** ✅ |
| PLACEBO — ANLY cell vs itself | **0.0e+00** ✅ |
| NEGATIVE — subsample to 25% | band sd **0.00593 → 0.01237**, widens ✅ |
| REPRODUCTION — `CONV/PERM` must reproduce R427 | **8/10 ≥ 8** ✅ |
| PLACEBO / POSITIVE / g=0, under **both** weightings | 0 exactly · resolves at g=0.5 · does not at g=1.0 ✅ |
| rank counter — g=0 / reversed / same-seed draws | 0 · **10** · 0 ✅ |

## The methodological point, which is the transferable part

**R429 ran the gauge test and it did not save it.** The gauge test asks *what transformations leave
the measurement invariant* — and I applied it to the repair in R428, not to the estimator here. The
failure was one level up: I compared two pipelines that differed on **two** axes and attributed the
difference to the axis I happened to be thinking about. *A two-factor difference has no single
mechanism until you hold one factor fixed*, and that costs one 2×2 and no new data.

## Impossible here, named

- **which null is correct** — both are defensible against real data by construction. Requires a
  corpus with **known** agreement structure. Still open, and still the next step.
- **which weighting is correct** — a choice about the estimand. R413 bears on the **variance** (the
  conversation is the independent unit), not on which weighting *defines* the quantity. Naming a
  winner here would be the same overreach this round is correcting.
- **recovering R427's exact permutation** — the artifact stores the result, not the draw, so the
  reproduction test is distributional and says so.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
