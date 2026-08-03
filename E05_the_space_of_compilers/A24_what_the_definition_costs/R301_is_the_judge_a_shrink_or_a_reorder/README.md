# R301 — is the judge dependence a SHRINK or a REORDER?

**Pre-registered 2026-08-03, written and committed BEFORE the 0.8B satisfaction files existed.**
The GPU job producing them (pueue 627/628) was submitted first; this file names the kill before
any of its numbers can be seen. That ordering is the only thing that makes the threshold below a
commitment rather than a description.

---

## The gap

A20 closed with *the partition is judge-dependent — `{coval_core, topw_k4}` at 2B, `{}` at 0.8B*
(R290). That was measured on **three arms**. R294 then ran the census on **41**. So the strongest
statement in `FORMULATION.md`'s scope line rests on a sample of 3 while the census it scopes rests
on 41, and **nothing in the campaign has ever asked what KIND of dependence it is.**

Two kinds have completely different consequences:

- if 0.8B **shrinks** every effect toward zero, the definition is judge-bound **through
  resolution** — the ordering of arms is intact and a judge-relative threshold recovers it;
- if 0.8B **reorders** the arms, the two judges measure different objects and no re-thresholding
  rescues anything.

`FORMULATION.md` currently asserts neither and is read as the second.

---

## What is dead before the run — an arithmetic kill, not a measurement

The obvious first world is **W-LEVEL**: *the judges differ by an additive offset.*
It is already dead, and no data is needed to kill it.

Both clauses are a **difference between two arms scored by the SAME judge**. If
`A2(a, 0.8B) = A2(a, 2B) − c` for every arm `a`, then

```
[A2(a,0.8B) − A2(b,0.8B)]  =  [A2(a,2B) − c] − [A2(b,2B) − c]  =  A2(a,2B) − A2(b,2B)
```

— the offset cancels **exactly**, so every clause effect would be judge-invariant. R290 measured
`coval_core` clause ② at **+0.0151 → −0.0072**. A pure level shift cannot produce that.

**W-LEVEL is refuted by algebra.** Labelled a DERIVATION, not evidence: it could not have come out
otherwise. Its value is that it removes the cheapest explanation before any GPU is spent, and it
tells the design what to measure instead — the **slope**, not the intercept.

---

## Live worlds

| | claim | prediction for `eff_08B` regressed on `eff_2B` over 41 arms |
|---|---|---|
| **W-SHRINK** | 0.8B is the same instrument with more noise; it compresses differences toward 0 | slope `β` resolvably in (0, 1), intercept ≈ 0, **R² ≥ 0.5**; no arm with resolvably opposite signs |
| **W-REORDER** | 0.8B measures a different thing; arm ordering is not preserved | **R² < 0.25** or `β` CI includes 0; ≥1 arm resolvably opposite in sign |
| **W-SELECTIVE** | the compression is not uniform — it eats clause ② (small, aboutness) and spares clause ① (large, quality) | `β₁` and `β₂` fitted separately have **non-overlapping CIs**; equivalently the shrink is a function of effect magnitude |

W-SELECTIVE is the one R290 actually hinted at (*"clause ① is judge-ROBUST, clause ② is
judge-BOUND"*) but could not test: with 3 arms there is no slope to fit.

**This quantity did not exist at the old arm width.** That is the reason to run it and not a
restatement of R290.

---

## Pre-registered kill

Fitted by cluster bootstrap over **prompts** (all 41 effects recomputed inside each resample, so
the CI on `β` respects that the arms share a baseline and a population).

```
if positive_control_fires and negative_control_is_null:
    if R2 >= 0.50 and beta_lo > 0 and beta_hi < 1:  -> W-SHRINK
    elif R2 < 0.25 or (beta_lo <= 0 <= beta_hi):    -> W-REORDER
    else:                                            -> UNRESOLVED, band published
else:
    verdict = UNVERIFIED     # never OVERTURNED, never CONFIRMED
```

The conditional wrapper is not decoration: three kills in this project fired on instruments their
own controls had already invalidated.

> ⚠ **AMENDED before the run, and the amendment makes the threshold HARDER.** The `R2` above was
> written as the pooled fit over all arms. The arms are not independent points: `random_k*_s{0,1,2}`
> is one rule at three seeds and `topw_k1..k12` is one rule at seven budgets, so the between-family
> spread is large, the within-family spread is small, and **a pooled R² can be carried almost
> entirely by the gap between families** — which would read as *the judges agree on the ordering of
> arms* while saying nothing about agreement **within** a family, where every admitted arm sits.
> The prompt bootstrap cannot see this; it resamples prompts, not arms. So `R2` in the kill now
> means `min(pooled, worst leave-one-family-out)`, and the within-family Spearman is reported
> beside it. Recorded here because an amendment written after seeing a number is a narrative, and
> the only defence is that this one is timestamped before the artifacts it judges existed.

**What each outcome costs me.** W-SHRINK ⇒ `FORMULATION.md`'s instrument line is **too strong** and
must say the ordering survives while the resolution does not. W-REORDER ⇒ it is **right and
currently under-stated**, and clause ② needs a judge named inside its text. Either way a published
sentence changes.

---

## Controls

| | |
|---|---|
| **POSITIVE — construction parity** | `topw_k4` and `random_k4_s0` exist at 0.8B by **two independent paths**: judged directly by `judge_core.py` (R290), and rebuilt by subsetting `sat08_full.npz`. **This is the control for the whole round**, because 34 of the 41 arms reach 0.8B only by the subset path. Failure localises exactly: the subset property is false under the new judge and the 34 rebuilt arms are void, while R290 stands. ⚠ **Threshold amended before the run** — the first draft demanded agreement to float precision, which would have been a control that fails for its own reasons: the two paths batch differently and a bf16 forward pass is not batch-invariant, so it would have voided 34 arms over arithmetic noise the campaign already measured (R307, 0.0009 at the mean). The criterion is now stated in the unit the round reports — the clause-① effect must agree **within that cell's own MDE** — and is floor/ceiling-checked by handing it a mismatched pair, which it must reject. |
| **POSITIVE — the judge is not blind** | `generic − random_k4_s0` resolvably positive at BOTH judges (R290: +0.0587 at 2B, +0.0692 at 0.8B). Fails at g=0 by construction: two arms that are the same object return 0. |
| **NEGATIVE** | the shams excluded at 0.8B, as everywhere. |
| **PLACEBO** | an arm against itself: exactly 0. |
| **NOISE FLOOR** | per-cell MDE computed in-cell at each arm's own `n`, never pooled. |
| **MULTIPLICITY** | 41 arms × 2 clauses at 0.8B = 82 new cells, BH q=0.05 over the whole grid, non-survivors printed. |
| **POPULATION** | per-arm, never intersected — R294's defect: `promptecho` covers 398 and intersecting made every other arm's MDE 1.6× wider. |

## Impossible here

| | would require |
|---|---|
| a third judge scale | a third model held to the same prompt contract — the template is byte-identical between `covalx/judge.py` and `E01/R04/run.py`, so a third is a drop-in, and this is **not-attempted, not impossible** |
| whether the shrink generalises to another release | a second values-annotation release |
