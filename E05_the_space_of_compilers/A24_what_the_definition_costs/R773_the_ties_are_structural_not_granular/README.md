# R773 · the 223 ties are structural, and R772's registered recomputation was answerable by algebra

**On the **223** tied prompts the five committed members are not merely equal in A2 — their
**satisfaction vectors** are near-identical: cosine distance mean **0.0046**, quantiles
**[0.0002 … 0.0185]**, **99.69%** below 0.05 and **0.00%** above 0.20. A magnitude-sensitive
estimator separates **0 of 10** pairs there. **WORLD A — the arms genuinely do the same thing on
23% of prompts**, and A2's coarseness is not what hides a difference. ⭐ And R772's registered
recomputation is a **derivation**: `eff/MDE` is invariant to dropping exact zeros — measured ratios
**0.9998–1.0008**, **0 of 10** verdicts move.**

## check #375 — the registered quantity was fixed by algebra, and it was run first

Dropping prompts whose difference is exactly 0 scales the **effect** by `n_f/n_d` and the **MDE** by
`sd_ratio·√(n_f/n_d)` — the same factor to O(μ²/σ²), with μ/σ = 0.024 here.

| pair | eff/MDE @968 | @745 | ratio | verdict moves |
|---|---|---|---|---|
| `coval_core`/`topw_k3` | 0.3684 | 0.3684 | 1.0000 | no |
| `coval_core`/`topw_k4` | 0.2693 | 0.2693 | 0.9999 | no |
| `topw_k4`/`topw_k6` | 0.0101 | 0.0101 | 0.9998 | no |
| `topw_k6`/`topw_k8` | 0.8653 | 0.8660 | 1.0008 | no |
| *(all ten in the artifact)* | | | 0.9998–1.0008 | **0 of 10** |

`n_required` scales by exactly **745/968 = 0.7696** — **the same information in a different unit**,
not less data needed *(ledger 1100)*.

## ⭐ E2 · what the ties actually are

| | on the 223 tied prompts |
|---|---|
| sign vectors identical | **0.9740** mean over 10 pairs [0.9596, 0.9910] |
| satisfaction cosine distance | **0.0046** mean [0.0014, 0.0082] |
| distance quantiles (5/25/50/75/95) | **0.0002 · 0.0008 · 0.0021 · 0.0051 · 0.0185** |
| share > 0.20 *(World B's line)* | **0.0000** |
| share < 0.05 *(World A's line)* | **0.9969** |

**D2, declared before the run:** a tie in A2 is a tie in the **sign pattern**, and two different
criterion sets can induce the same ordering — *"the arms are identical there"* does **not** follow
from a tie and had to be measured. It measures true *(ledger 1101)*.

## ⭐ E3 · and the finer statistic separates nothing

**D3, declared before the run:** a magnitude-sensitive statistic retains strictly more information,
so *"it separates arms A2 ties"* is nearly forced and is **not** the finding — the question is whether
any separation clears its **own** floor. It does not:

| pair | eff | its own MDE | eff/MDE |
|---|---|---|---|
| `coval_core`/`topw_k8` | 0.0023 | 0.0064 | 0.352 |
| `topw_k3`/`topw_k4` | 0.0006 | 0.0010 | **0.570** *(largest)* |
| `topw_k4`/`topw_k6` | −0.0003 | 0.0025 | −0.117 |
| *(all ten)* | | | **0 of 10 separate** |

⚠ **And this is a different estimand** — *"does the arm order the responses like the human"* vs
*"does its sign pattern match"* — so even a separation here would not have been evidence that A2 is
wrong. The round says so rather than promoting the statistic.

## ⛔ two controls could not have passed as first written

**① `g=0` and `PLACEBO` required `== 0.0` on a cosine distance.** For identical vectors that computes
`1 − (u·u)/(|u||u|)` and lands at **−8.46e-18** and **−4.98e-19** in floating point. **Requiring exact
zero of a floating-point identity is a check that cannot pass.** Repaired with a stated tolerance of
1e-9.

**② `POSITIVE` required `> 0.05`, a number I picked without computing what the known-different pair
returns on this subset.** It returns **0.0358** — §4's *control that cannot PASS*, sixth instance.
**The repair is not a lower number chosen to pass**: the criterion is now computed and non-tunable —
the known-different pair must exceed **the largest committed-pair distance on the same prompts**
(0.0082). It does, by **4.36×** *(ledger 1102)*.

## controls — 5 PASS after the repair

| control | returned |
|---|---|
| **POSITIVE** | `coval_core` vs `gen_sham` on tied prompts **0.0358** vs the largest committed pair **0.0082** — **4.36×**. Band computed on this subset: floor −8.46e-18, ceiling 0.2794 |
| **g=0** | an arm against itself **−8.46e-18** (tol 1e-9) |
| **PLACEBO** | `topw_k4` vs `_detA` **−4.98e-19** |
| **SHAM** *(ingredient = the tie)* | the same distance on the **745 discriminating** prompts: **0.0066** vs tied **0.0046**, ratio **0.696** |
| **NEGATIVE** | 200 random subsets of the same size: **0.0062 [0.0055, 0.0069]** vs tied **0.0046** — tied sits below the band, so the tie tracks smaller distance, but modestly |

⭐ **And the POSITIVE's own value is a finding**: even a *sham* arm is only **0.0358** away on the
tied prompts, against a ceiling of 0.2794 elsewhere. **Those prompts are ones where the four responses
are hard to separate at all** — a property of the prompts, not of the extension.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| R772's NEXT — recompute MDE and required-n on the discriminating subset | ⛔ **a DERIVATION**: `eff/MDE` invariant (0.9998–1.0008), 0 of 10 verdicts move, `n_req` × 0.7696 |
| *"223 prompts carry no ordering information"* | **and the reason is structural** — the members' satisfaction vectors are 0.0046 apart there, 99.69% under 0.05 |
| *"A2's coarseness might hide a difference"* | ⛔ **refuted** — a magnitude-sensitive statistic separates **0 of 10** pairs on exactly those prompts |
| the extension's unorderedness | **partly a fact about the arms**: on 23% of prompts the five behave identically, and a sham arm is only 4× further away than they are from each other |

## the sentence I can no longer write

*"the tied prompts might be hiding differences the estimator cannot see."* A finer estimator sees
nothing there, and a deliberately bad arm is barely further away than the real ones.

## NEXT

The POSITIVE control produced the sharpest number in the round and it was not the registered
quantity: on the tied prompts a **sham** arm sits **0.0358** from `coval_core` while the committed
members sit **0.0046** from each other — a factor of **7.8** — yet the ceiling across all pairs
anywhere on those prompts is **0.2794**. So the tied prompts are not uniformly degenerate; they
compress *real* arms together far more than they compress a bad one. ⚠ That is a claim about the
prompts' **discriminative capacity**, and this round measured it only on the 223 it had already
selected **by** the arms tying — which is selection on the outcome *(§4)*. The registered quantity is
the sham-to-committed distance ratio computed across the whole 968 as a function of `c(p)`, so the
relationship is estimated on a population that was not chosen by the thing being tested.
