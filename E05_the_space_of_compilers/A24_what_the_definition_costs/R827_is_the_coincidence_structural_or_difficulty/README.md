# R827 · Is the core-on-ceiling coincidence structural, or item difficulty?

**E05 · A24 · R827. Pre-registered verdict: UNVERIFIED — the positive control failed, and it failed
because I mislabelled one of its pairs at design time.** 968 prompts · 58 arms · 1,596 null pairs ·
8-fold cross-fitting. Source `2587c030`. Two seeds byte-identical: `c8d14f9f9e47999cda71293470e51bd8`.

## The decision this was to make safe

R826 found the response-only bar saturating **on** `coval_core` (0.571263 vs 0.566477). Does that
mean the core *behaves* like a response-only rule, or do two unrelated quantities merely meet?

## ⛔ The premise: a raw correlation is forced

Every arm's per-prompt score is an accuracy against the **same** human labels on the **same** items.
A prompt where humans tie caps every arm. So any two arms correlate through **item difficulty**,
mechanism or not — measured on pairs sharing none:

| pair | r |
|---|---:|
| `random_k4_s0` × `oracle_k4` | **+0.5132** |
| `gen_sham` × `oracle_k4` | **+0.3873** |

Both reproduce exactly as this round's OBJECT check. `raw r(core, bar) = +0.4495` is therefore a
**derivation-grade number and not evidence**.

## The estimand, and what it returned

Partial correlation, residualising both on a difficulty index (mean arm A2 · human tie rate ·
log annotator count) built from arms **excluding both** members of every pair — rebuilt per pair
inside the null loop, so no arm's own noise ever appears on both sides.

| | |
|---|---:|
| **partial r(core, bar \| difficulty)** | **+0.1278 [+0.0605, +0.1935]** |
| null over 1,596 arm pairs | median −0.0064 · 5th **−0.3053** · 95th **+0.5588** |
| percentile of the core–bar pair | **75.4** |

**Direction, not verdict:** +0.1278 sits inside the null band, pointing at **WORLD B — the
coincidence is in level, not in profile.** The gate blocks it and that stands.

## Why the gate failed

| positive-control pair | partial r | vs null p95 |
|---|---:|---|
| `topw_k4` × `topw_k6` | **+0.5739** | **passes** |
| `random_k4_s0` × `random_k4_s1` | **+0.0905** | fails |

**Mean Jaccard of the actual selected criterion texts (n = 968):**

| pair | Jaccard |
|---|---:|
| `random_k4_s0` × `random_k4_s1` | **0.1931** |
| `topw_k4` × `topw_k6` | **0.6696** |
| `random_k4_s0` × `topw_k4` *(cross-family reference)* | **0.1868** |

⭐ **The random pair overlaps at essentially the cross-family rate.** They share a *procedure*, not
*content* — and my preregistration called them *"pairs KNOWN to share mechanism"*. **That was my
error at design time.** The gate required all positive pairs to pass, so **UNVERIFIED stands**;
reclassifying the pair now would be bending the kill to the answer.

`topw_k4 × topw_k6`, which genuinely shares selected content, **does** clear the null — so the
statistic can see shared mechanism when there is content to share.

## ⚠ My first diagnosis used an instrument blind by construction

I initially "showed" the random pair picks different criteria by computing Jaccard on the **sat-file
criterion indices** and got **1.0000**. That number supports nothing: `select_core.py` **re-indexes
selections to `0..k−1` on emit**, so the sat index Jaccard is 1.0 for *every* k=4 pair. It measured
labels, not identity — the same defect class as R810's degenerate null.

**The conclusion survived; the evidence I first offered for it did not.** The instrument that can see
is `core_*.json`, which stores the criterion texts, and it is what the table above uses.

## Controls that passed

| control | returned |
|---|---|
| **OBJECT** | both premise correlations reproduce to 4 dp |
| **PLACEBO** | core vs a **permutation** of the bar: **+0.0083** |
| **SHAM** | residualise on **random** vectors: **+0.4525** vs raw **+0.4495** — removes nothing, as required |
| **NEGATIVE** | index from a different 19-arm subset: **+0.1354** vs +0.1278, inside the bootstrap width |
| **CROSS-FITTING** | 8 folds × fit 847 / score 121; **each prompt scored exactly once** by a model that never saw it |

## Two defects the round's own asserts caught before any number

1. **Out-of-fold had no coverage guarantee.** Reusing R826's random 50/50 splits leaves a prompt in
   `fit` all eight times with probability (1/2)⁸ — ~3.8 of 968 never scored, and `acc/cnt` would
   have divided by zero. Replaced with k-fold; a second assert now requires `cnt.max() == 1`.
2. **My k-fold patch deleted the loop body.** The loop ran eight times doing nothing and `cnt` stayed
   all-zero. **The assert fired instead of publishing 0/0** — §4's *empty population* row working.
   Restored with per-fold logging so a silent deletion is visible in the log, not only in an assert.

⚠ **Scope change stated:** k-fold trains on 7/8 = 847 prompts where R826's halves trained on 484, so
this bar's **level** is not comparable to R826's. Only its per-prompt **profile** is used here.

## D3, written before the run, and it still binds

A high partial r would show the two **agree on which prompts they win** beyond difficulty. That is
consistent with shared mechanism **and** with a third common cause the index misses. **This round
could only ever speak about profile agreement, never about mechanism** — and it did not get to speak
at all.

## What this round cannot do

| criterion | requires |
|---|---|
| a verdict | a positive control whose pairs actually share content — re-registered from the measured Jaccard, not from what a name implies |
| mechanism | an intervention on the core's criteria, not a correlation |
| cross-release | a second release |
