# R431 · the announced next step was the arithmetic trap — and the real gap is **10× smaller** than the one I chased

**The decision this round makes safe:** whether the CONV/INTER weighting choice is a *correctness*
problem for every excess number in the campaign. **It is not.** No size confound, and the gap on the
quantity anyone actually reports is **≤ 0.0050**, not the 0.013 R430 measured.

## ⛔ First: the announced experiment could not have failed

R430 closed with *"build a corpus with known agreement structure and see which aggregation is
unbiased."* Rung 2 of the ladder, before any code:

```
E_CONV  = (1/C) Σ_c (1/n_c) Σ_i x_ci   unbiased for a RANDOM CONVERSATION's mean
E_INTER = (1/N) Σ_c        Σ_i x_ci    unbiased for a RANDOM INTERACTION
```

**Each is unbiased for its own estimand — that is algebra.** A synthetic corpus would have returned
those two lines dressed as a result. **This is the third round in a row whose announced next step
presumed its own conclusion**, and the second where the cheap check killed the expensive plan.

## Result — **`W-RESIDUAL`**, *and that world was not pre-registered*

| | |
|---|---|
| **size confound** | **0 of 30** slope cells clear BH(q=0.10) — **none** |
| **the n=2 association** | rho ≈ **−0.19**, but the permutation null sits at **−0.2116 ± 0.0203**; observed is **+1.21 sd** *inside* it |
| **CONV/INTER gap on the EXCESS** | **max \|gap\| = 0.0050** across all 10 pairs |
| **after standardising the stratum mix** | inside its own floor for **7 of 10** pairs — short of the **8** I pre-registered, and for some pairs *larger* than the raw gap |

**Population** 2,200 conversations / 7,344 interactions · sizes 1–13, median 3 · **instrument** the
five committed `sat_transport_*.npz`, Qwen3.5-2B-Base at k=4 · **baseline** the analytic
marginal-matched null, with the **null axis held fixed** (R430: the two nulls agree to ~0.002 — one
factor at a time) · **regime** n ∈ {2,3,4}, shares 0.709 / 0.062 / 0.229.

## ⭐ The number that matters, and why nobody had it

R430 measured the CONV/INTER difference **on the null** at ~0.013. On the **excess** — agreement
minus null, which is what every round reports — it is **at most 0.0050**, because reweighting moves
the agreement and the null *together* and the difference largely cancels.

**R430's 0.013 was never a statement about the excess, and nothing quoted it as one — but the
distinction was not written down**, and a reader would have carried 0.013 into a claim it does not
bound. It also explains why R430's own two headline Δ differ by only **0.0008** (+0.0226 CONV vs
+0.0234 INTER): consistent with ≤0.0050, not with 0.013.

## ⛔ Three control corrections, each caught by the one before it

| # | what I asserted | why it was wrong |
|---|---|---|
| 1 | g=0: unplanted data must give `\|rho\| ≤ 0.10` | **assumed the answer** — that the corpus has no size association, the thing under test. It fired at 0.1871 and was right about my *design*. Replaced by: *a no-op plant must not change the statistic.* |
| 2 | NEGATIVE: relabel whole conversation dicts | **destroyed nothing** — size and agreement moved together, so the "null" came back at −0.1875, *the real association wearing a null's clothes*. Replaced by permuting agreement values with size and stratum counts held exactly fixed. |
| 3 | NEGATIVE: the null "must be centred near 0" | **a claim about the statistic I had no basis for.** A conversation with one stratum-*n* item has a mean of exactly 0 or 1; with a pool mean ~0.77 the small ones sit above it, so size and mean are negatively rank-associated **under independence**. The null is not zero and must not be — *that is why a permutation null exists.* Replaced by: the permutation must move the draws, and an **identity** permutation must reproduce the observed exactly (**−0.187096 vs −0.187096** ✅). |

## ⛔ And the verdict string lied, in the round that catalogues verdict strings

The first version reached `W-BOTH` through its *no-confound* branch and printed *"a size association
survives"* two lines under `surviving BH 0`. Every clause is now gated on the quantity it asserts.

## Controls, final state

| control | returned |
|---|---|
| PLACEBO — a weighting against itself | **0.0e+00** ✅ |
| g=0 — a no-op plant | **0.1871 → 0.1871**, unchanged ✅ |
| POSITIVE — plant g=0.30 in the largest tercile | **0.1871 → 0.1142**, moves ✅ |
| NEGATIVE — 200 link-permutations | 200 distinct · identity reproduces observed exactly ✅ |
| IDENT — strata with no within-stratum size variation | **0 dropped**, counted and printed |

## Why `W-RESIDUAL` is reported and not routed into a declared world

The three declared worlds do not cover *"no size association **and** the standardised gap still
exceeds its floor for 3 of 10 pairs"*. R429's failure was a world in prose with no branch; the
remedy is **not** to invent a branch after the fact but to say the prediction matrix was incomplete.
**The residual 3 pairs are unexplained by this round**, and that is stated rather than absorbed.

## Impossible here, named

- **a causal reading of any slope** — conversation size is not assigned. Requires an intervention on
  length, which the release cannot support.
- **separating size from topic** — long conversations may differ in subject matter and no
  permutation of this corpus holds topic fixed. Requires topic labels the release lacks.
- **which weighting is "right"** — settled by algebra to be a question about the estimand, not the
  estimator. Requires naming the target quantity, which is a decision, not a measurement.
- **generalising past k=4 or this judge** — one model, one criterion count.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
