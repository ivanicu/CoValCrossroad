# R333 — the annotator axis has 7.6% left in it, and the band needs 13× the release

**Decision this makes safe:** whether the campaign can ever resolve which arms clause ② admits.
**Not on this release.** The admitted set is **structurally unresolvable** — a register entry, not a
to-do.

## W-PROMPT-BOUND

| arm | k | effect | σ_b | σ_w | MDE(968, all) | floor m→∞ | m=16 / floor |
|---|---:|---:|---:|---:|---:|---:|---:|
| `coval_core` | 4 | +0.0160 | 0.1077 | 0.1777 | 0.0106 | **0.0097** | **1.082** |
| `topw_k3` | 3 | +0.0180 | 0.1154 | 0.1921 | 0.0114 | 0.0104 | 1.083 |
| `topw_k4` | 4 | +0.0137 | 0.1110 | 0.1783 | 0.0109 | 0.0100 | 1.078 |
| `topw_k6` | 6 | +0.0208 | 0.1086 | 0.1765 | 0.0107 | 0.0098 | 1.079 |
| `topw_k8` | 8 | +0.0152 | 0.1102 | 0.1737 | 0.0108 | 0.0099 | 1.075 |

**At m=16 the MDE is 1.08× its m→∞ floor.** Infinite annotation buys **7.6%**.

⛔ **Derivation, not a measurement** — `MDE ∝ 1/√N` is forced by the estimator. Required N for the
floor to reach R332's 0.0027 band:

| arm | floor @968 | required N | × release |
|---|---:|---:|---:|
| `coval_core` | 0.0097 | **12,494** | **12.9×** |
| `topw_k3` | 0.0104 | 14,331 | 14.8× |
| `topw_k4` | 0.0100 | 13,269 | 13.7× |
| `topw_k6` | 0.0098 | 12,706 | 13.1× |
| `topw_k8` | 0.0099 | 13,063 | 13.5× |

## ⛔ R332's next-gradient line was false twice, and both refutations were one read away

> *"the release ships a median of 16 annotators per prompt and every A2 here samples **ONE**, so the
> cheapest available precision gain is the annotator axis"*

**①** `load_targets()` returns **every** assessment; R331 and R332 build `H[n]` from all of `tg[p]`
and average over it — **mean 16.1 per prompt, 15,593 annotations.** Nothing samples one.
**②** **R306 performed this exact migration 26 rounds ago**, and says so in its own docstring:
*"every number in this campaign used 3 … use every annotator."*

§4 records that a `next gradient` line is the highest-risk sentence in a report and that its
direction is not systematic — one excuses work, one manufactures it. **This one manufactured it: the
round I proposed would have measured nothing.**

## The MDE surface — `coval_core`, 3 seeds

| N | m=1 | m=2 | m=4 | m=8 | m=16 | m=all |
|---:|---:|---:|---:|---:|---:|---:|
| 97 | 0.0581 | 0.0448 | 0.0382 | 0.0322 | 0.0372 | 0.0332 |
| 242 | 0.0363 | 0.0307 | 0.0258 | 0.0221 | 0.0218 | 0.0207 |
| 484 | 0.0262 | 0.0208 | 0.0174 | 0.0151 | 0.0153 | 0.0155 |
| 726 | 0.0215 | 0.0172 | 0.0144 | 0.0129 | 0.0125 | 0.0123 |
| **968** | 0.0186 | 0.0146 | 0.0126 | 0.0112 | **0.0106** | **0.0106** |
| *sd @968* | 0.00037 | 0.00020 | 0.00022 | 0.00006 | 0.00002 | 0.00000 |

*The non-monotone cells at N=97 (m=8 → m=16) are subsampling noise — the across-seed sd there is
two orders above the N=968 row. Not structure.*

## Controls

| control | result |
|---|---|
| **positive** — reproduce R294's committed `mde2` for the same pair | **5 of 5 exact to 1e-12** |
| **positive @ g=0** — m=1 must exceed m=all | 0.0186 vs 0.0106, **knob alive** |
| **negative · synthetic** — every annotator ← the prompt's mean, so σ_w = 0 *by construction* | σ_w = **1.49e-17**, m-curve spread **0.00e+00** |
| **empirical vs analytic** — the decomposition must describe the subsampler | max deviation **1.9%** |
| **placebo** — subsampler at (968, all) vs the direct computation | **0.0** |
| multiplicity | 5×6 cells × 3 seeds, all printed; **no hypothesis test is performed, so no correction is due** |

The synthetic control is the one that matters: it builds the rival's world — *"the m axis does
nothing because within-prompt noise is negligible"* — rather than arguing against it, and the
instrument correctly reports a flat curve there and a falling one here.

## What this closes

**The admitted set is not a measurable quantity on this release.** R332 found two admitted sets
inside 0.25 MDE; this says the MDE cannot be reduced below ~0.0097 by any analysis of these 968
prompts, and crossing the band needs **~13× more prompts**. No cleverer reference, estimator, or
aggregation reaches it.

> **Register entry:** *resolving which arms clause ② admits — requires a release with ~13,000
> prompts at this annotation depth. Not achievable by re-analysis.*

## Scope

968 CoVal prompts with ≥2 annotators, 15,593 annotations · Qwen3.5-2B-Base under R234's canonical
builder · baseline the k-matched first-k subset of the generic pool (R294's published reference) ·
per-annotator agreement over the 6 pairwise comparisons · 5 arms.

## What this cannot do

Establish σ_b for the **population** rather than for this release — that needs a second release, and
the required-N derivation rests on it. **Direction of error stated:** if these 968 prompts are more
homogeneous than the population, required-N is *understated*.
