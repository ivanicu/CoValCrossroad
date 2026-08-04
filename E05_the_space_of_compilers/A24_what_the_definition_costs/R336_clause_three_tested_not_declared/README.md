# R336 — clause ③'s detector is a QUALITY meter, and this retracts R335

**Decision this makes safe:** whether clause ③ can cite a measurement. **It cannot.** R295's slope
correlates with arm quality at **r = +0.934**, and once quality is removed there is **no residual
leak signal at all**. **W-QUALITY-METER.**

## The blind test — 41 arms, threshold built only from arms I manufactured

| arm | A2 | slope | detector | page says | |
|---|---:|---:|---|---|---|
| `oracle_k4_fit1` | 0.6142 | 0.0337 | FIRES | LEAKY | ✓ |
| `greedy_k4_fit1` | 0.6106 | 0.0297 | FIRES | LEAKY | ✓ |
| `indep_k4_fit1` | 0.5941 | 0.0252 | FIRES | LEAKY | ✓ |
| `oracle_k4` | 0.6283 | 0.0215 | FIRES | LEAKY | ✓ |
| **`topw_k6`** | 0.5641 | 0.0111 | **FIRES** | clean | **✗** |
| **`topw_k8`** | 0.5593 | 0.0092 | **FIRES** | clean | **✗** |
| **`coval_core`** | 0.5665 | 0.0085 | **FIRES** | clean | **✗** |
| **`topw_k3`** | 0.5632 | 0.0064 | **FIRES** | clean | **✗** |

Sensitivity **1.000** (4/4) · specificity **0.886** (31/35). **All four false positives are exactly
the campaign's admitted set, and all four are borderline.**

## ⛔ The confound control, and it refutes the instrument

**`corr(slope, A2) = +0.934` across the 35 annotated-clean arms.** Regressing slope on quality and
asking what leakage adds:

| arm | A2 | actual | quality-predicted | excess | / resid sd |
|---|---:|---:|---:|---:|---:|
| `oracle_k4_fit1` | 0.6142 | 0.0337 | 0.0319 | +0.0018 | **+0.35** |
| `greedy_k4_fit1` | 0.6106 | 0.0297 | 0.0303 | −0.0006 | **−0.12** |
| `indep_k4_fit1` | 0.5941 | 0.0252 | 0.0229 | +0.0023 | **+0.45** |
| **`oracle_k4`** | 0.6283 | 0.0215 | 0.0382 | −0.0168 | **−3.25** |
| `topw_k6` *(clean)* | 0.5641 | 0.0111 | 0.0095 | +0.0016 | +0.36 |
| `coval_core` *(clean)* | 0.5665 | 0.0085 | 0.0105 | −0.0020 | −0.39 |

> **The two classes overlap completely on the adjusted statistic** — leaky `[+0.45, +0.35, −0.12,
> −3.25]` against false-positive `[+0.36, +0.32, −0.39, −0.52]`. And **`oracle_k4`, the *maximally*
> leaky arm, sits 3.25 sd BELOW what its quality predicts.**
>
> **There is no residual leak signal to detect.**

## ⛔ This retracts R335, which I committed an hour ago

R335 found the manufactured classes disjoint at **32.9 across-seed sd**. But **higher dose → better
fit → better arm**, so it separated **dose-induced quality**, not provenance. Its wrong-prompt
negative control is consistent with the quality story too: that arm is *worse*, so its slope is
lower. **The separation was real and it was not about labels.**

**Clause ③ has no validated instrument.** Its annotations stand as a careful reading of
`select_core.py` — which is what they always were.

## ⚠ And my own boundary re-introduced the defect R335 caught

The five label-free rules I used to set the threshold are all **weak** arms (top-variance *is*
R294's `topvar_k4` at A2 **0.4863**), so `floor` was a bad-arm floor and `t` sat below every good
arm. **Same quality confound, one round later, in the control designed to avoid circularity.**

## Controls

| control | result |
|---|---|
| **positive** — reproduce R295's committed slopes | `+0.008547932270` · `+0.004579883562`, exact to 1e-12 |
| **band** — `floor < t < ceiling` must be non-empty | −0.0088 < **+0.0063** < +0.0214 |
| **positive @ g=0** — manufactured clean arms below `t`, by the same comparison | PASS |
| **negative** — R335's wrong-prompt f=1 arm | −0.047, −0.048, −0.049, none fire |
| **confound** — regress slope on A2 across clean arms | **r = +0.934**, classes overlap |
| multiplicity | 39 arms, every verdict computed; the confusion matrix *is* the statement |

## What this does NOT say

**The four annotated-leaky arms are not exonerated.** Clause ③ excludes them by source-reading and
that stands. What is refuted is the claim that an *instrument* corroborates it. And a disagreement
here identifies **that the pair disagrees** — the page's annotations are a reading of source, not a
ground truth, so which member is wrong needs a construction log the release does not carry.

## Scope

968 CoVal prompts with ≥1 annotator in **each** parity · Qwen3.5-2B-Base under R234's canonical
builder · size-matched first-k blind reference · k as published per arm, scored on parity 0 ·
5 label-free boundary rules · 39 of 41 arms returned a slope.

## What this cannot do

Separate quality from provenance **at all**, on this release. The two are entangled by construction:
fitting on labels makes an arm better, and better arms have steeper slopes. Breaking that would need
arms matched on quality and differing only in provenance — which is exactly what fitting produces
and therefore cannot supply.
