# R769 · the register gets its number — and "unordered" turns out to have two different causes

**The estimator consumes **968** of the release's **1,078** prompts; all **110** drops fail **both**
coverage clauses at once — absent from the base arm **and** from the pool — and **0 are recoverable**
for the five arms R768 compared. The annotator side is already fully consumed (**median 16, 15,593**,
the release's own figure). ⭐ **The required-n table splits R768's null in two**: three committed
pairs need **1,293–2,376** prompts (1.3–2.5× today) and would resolve with a modestly larger release;
`topw_k4` vs `topw_k6` needs **9,534,441** — a statement that those two arms are the same to any
feasible measurement. **WORLD B.**

## check #371 — §4's remedy, run before any design

*"Before accepting any resolution limit, count what the release actually contains and what your code
actually consumed, and require those two numbers to match."*

| | contains | consumed | |
|---|---|---|---|
| prompts | **1,078** | **968** | 110 dropped |
| annotations | **18,384** | **15,593** | ratio **0.8482** |
| annotators per prompt | median 16 | **median 16** | ⭐ **fully consumed** |

**The ×5 gain §4's row found on a different design is not available here** — that lever is already
pulled, and claiming it would be the flattering direction *(ledger 1087)*.

## ⭐ E1/E2 · why the 110 drop, and whether they are recoverable

| clause | count |
|---|---|
| absent from the base arm only | 0 |
| absent from the pool only | 0 |
| fewer than 2 annotators | 0 |
| **both coverage clauses at once** | **110** |

**Every dropped prompt fails both**, so they were never scored by *any* arm — a property of what the
release scored, not an accident of which arm happened to cover them. **Recoverable for R768's five
arms: 0 of 110.** So the campaign's 968-prompt scope is **correct**, and World A — the version where
every ② number carried an unstated 89.8% scope — is excluded *(ledger 1088)*.

## ⛔ D1 said this round could not rescue R768, and it was stated before running

`MDE ∝ 1/√n`, so 968 → 1,078 multiplies the MDE by **0.947** — recovering all 110 buys **5.2%**.
Against a gap/MDE factor of 3.71 that is nothing. **Declared in the preregistration so a null could
not be read as a discovery**, and the round is **CLOSURE on the headline, FRONTIER on scope**.

## ⭐ E3 · the power curve, with the law asserted rather than fitted

`coval_core` vs `topw_k4`, 50 subsamples per n:

| n | MDE | sd | 1/√n law | ratio | SHAM (with replacement) | NEG / real |
|---|---|---|---|---|---|---|
| 100 | 0.02648 | 0.00304 | 0.02653 | 0.998 | 0.02689 | 2.22 |
| 200 | 0.01871 | 0.00160 | 0.01876 | 0.998 | 0.01864 | 2.23 |
| 400 | 0.01347 | 0.00064 | 0.01327 | **1.015** | 0.01337 | 2.23 |
| 600 | 0.01079 | 0.00038 | 0.01083 | 0.996 | 0.01082 | 2.26 |
| 800 | 0.00935 | 0.00017 | 0.00938 | 0.997 | 0.00932 | 2.26 |
| **968** | **0.00853** | 0.00000 | 0.00853 | 1.000 | 0.00796 | 2.17 |

**Worst deviation from the law: 1.5%.** The law is *asserted and checked*, never fitted — a flat
curve or a wrong exponent fails it.

## ⭐⭐ D3 · the required n, per pair — a DERIVATION, and it splits the null

| pair | gap | MDE | MDE/gap | **n required** | × today |
|---|---|---|---|---|---|
| `topw_k6` vs `topw_k8` | +0.0048 | 0.0056 | 1.16 | **1,293** | 1.3 |
| `coval_core` vs `topw_k8` | +0.0072 | 0.0085 | 1.19 | **1,373** | 1.4 |
| `topw_k4` vs `topw_k8` | +0.0049 | 0.0076 | 1.57 | **2,376** | 2.5 |
| `topw_k3` vs `topw_k8` | +0.0039 | 0.0087 | 2.25 | 4,880 | 5.0 |
| `coval_core` vs `topw_k3` | +0.0033 | 0.0090 | 2.71 | 7,132 | 7.4 |
| `coval_core` vs `topw_k6` | +0.0024 | 0.0079 | 3.33 | 10,761 | 11.1 |
| `coval_core` vs `topw_k4` | +0.0023 | 0.0085 | 3.71 | 13,346 | 13.8 |
| `topw_k3` vs `topw_k4` | −0.0010 | 0.0054 | 5.42 | 28,456 | 29.4 |
| `topw_k3` vs `topw_k6` | −0.0009 | 0.0076 | 8.08 | 63,241 | 65.3 |
| **`topw_k4` vs `topw_k6`** | **+0.0001** | 0.0063 | **99.25** | **9,534,441** | **9,850** |

⭐ **R768's "unordered" is two different facts wearing one word.** For `*_k8` it is a **power
failure** a 1.3–2.5× larger release would fix. For `topw_k4` vs `topw_k6` it is **structural**: nine
and a half million prompts is not a data-collection plan, it is a statement that the two arms are the
same to any feasible measurement *(ledger 1089)*.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | the curve follows `MDE(n) = MDE(968)·√(968/n)` to within **1.5%** across six n. Band: a flat curve fails, a wrong exponent fails — the law is not fitted |
| **g=0** | at n = 968 with no subsampling the curve reproduces **R768's committed MDEs exactly** |
| **NEGATIVE** | pairing destroyed at every n → MDE ratio **2.17–2.26**, stable, so the pairing's benefit is not an artifact of the full sample |
| **SHAM** | drawing n **with replacement** from the same 968 gives the same MDE (ratio at n=400: **0.993**) — **only new prompts move the curve; resampling buys nothing** |
| **PLACEBO** | an arm against itself: MDE **0.0000000000** at every n |
| **CONFOUND** | 0 recoverable, so the difference-sd comparison is **UNIDENTIFIED** — declared, not assumed away |

## what this changes in the deliverable

| carried | stands as |
|---|---|
| the population is **968 prompts** | **correct, and now justified** — the release has 1,078 and all 110 extra fail both coverage clauses; 0 recoverable |
| *"the extension is unordered"* *(R768)* | **stands, with its cause split**: 3 pairs are under-powered at n = 968 and would resolve by **1,373–2,376**; the tightest pair needs **9.5 M** |
| the impossibility register's *"more prompts"* | **has a number per pair now**, instead of a phrase |
| the annotator dimension | **exhausted** — median 16, 15,593 consumed, the release's own figure |

## the sentence I can no longer write

*"the design might not be at its limit."* On annotators it is; on prompts the release holds 110 more
that no arm ever scored, and they buy 5.2%.

## NEXT

The required-n column is a **derivation** resting on one assumption stated in the preregistration —
that the per-prompt difference sd is stable as n grows — and the round could not test it, because the
recoverable subset was empty. ⚠ That assumption is testable *within* the 968 without new data: the sd
is a property of the difference vector, and if it varies systematically across prompt strata already
recorded in the release (annotator count, response-set size), then the required-n figures are
stratum-dependent and the single number per pair is the wrong shape. The registered quantity is the
per-prompt difference sd regressed on the strata the release ships, because a required-n that ignores
its own heterogeneity is the same point-estimate error this arc has now retracted at three levels.
