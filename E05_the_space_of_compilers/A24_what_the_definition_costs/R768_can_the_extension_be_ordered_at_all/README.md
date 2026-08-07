# R768 · the extension is an unordered SET — the definition admits four arms and cannot rank them

**Of the **10** pairs among the five committed extension members, **0 are resolvably ordered**. The
released core against each alternative it admits: `topw_k3` **+0.0033 [−0.0031, +0.0096]** · `topw_k4`
**+0.0023 [−0.0038, +0.0084]** · `topw_k6` **+0.0024 [−0.0030, +0.0075]** — all **UNRESOLVED** against
MDEs of 0.0079–0.0090. ⭐ **The definition cannot say the released core is better than the arms it
admits alongside it.** **WORLD A.**

## check #370 — R767's NEXT died from my own committed artifact, in one arithmetic step

It said *"the k-curve peaks at k = 6 (eff/MDE 1.311), not at the released core's k = 4 (1.264)."*

| k | eff | MDE | implied sd | eff/MDE |
|---|---|---|---|---|
| **4** | **0.013745** | 0.0109 | 0.1208 | 1.264 |
| **6** | **0.013681** | 0.0104 | 0.1159 | **1.311** |

**On the effect the curve peaks at k = 4.** `MDE = z·sd/√n`, so ranking by `eff/MDE` ranks by
`eff/sd` — **it rewards low variance, not high effect** — and I wrote the line with both effects
printed side by side in my own table. **Sixth NEXT this arc killed by the first check of the round
that acted on it** *(ledger 1084)*.

## ⭐ E1 · the pairwise matrix — the five committed members

| a | b | eff | CI | MDE | verdict |
|---|---|---|---|---|---|
| `coval_core` | `topw_k8` | +0.0072 | [+0.0012, +0.0131] | 0.0085 | BELOW RESOLUTION |
| `topw_k4` | `topw_k8` | +0.0049 | [−0.0001, +0.0101] | 0.0076 | UNRESOLVED |
| `topw_k6` | `topw_k8` | +0.0048 | [+0.0009, +0.0087] | 0.0056 | BELOW RESOLUTION |
| `topw_k3` | `topw_k8` | +0.0039 | [−0.0024, +0.0095] | 0.0087 | UNRESOLVED |
| **`coval_core`** | **`topw_k3`** | **+0.0033** | [−0.0031, +0.0096] | 0.0090 | **UNRESOLVED** |
| **`coval_core`** | **`topw_k6`** | **+0.0024** | [−0.0030, +0.0075] | 0.0079 | **UNRESOLVED** |
| **`coval_core`** | **`topw_k4`** | **+0.0023** | [−0.0038, +0.0084] | 0.0085 | **UNRESOLVED** |
| `topw_k3` | `topw_k4` | −0.0010 | [−0.0048, +0.0028] | 0.0054 | UNRESOLVED |
| `topw_k3` | `topw_k6` | −0.0009 | [−0.0062, +0.0040] | 0.0076 | UNRESOLVED |
| `topw_k4` | `topw_k6` | **+0.0001** | [−0.0041, +0.0044] | 0.0063 | UNRESOLVED |

**`topw_k4` vs `topw_k6` is +0.0001** — the pair R767's NEXT proposed, and the registered quantity.
It is as close to zero as this design can print.

## ⚠ two counts, two questions — stated before the verdict

| | committed pairs |
|---|---|
| resolvable **by verdict** (\|eff\| ≥ MDE **and** CI excludes 0) | **0 of 10** |
| surviving **BH** on the bootstrap p, no MDE floor | **2 of 10** — `topw_k6 vs topw_k8`, `coval_core vs topw_k8` |

**The gap is the MDE floor — the same floor R767 showed decides a 4-member extension from a 5-member
one.** ⛔ My first verdict branch fired off BH survival alone and printed *"ordered in part"* while
the verdict column read 0 of 10. §4's *the verdict string is not a computation*, and the branch now
references the floor this round's own lineage established *(ledger 1085)*.

## ⛔ two results were forced, and one was measured against its own sham

**D1** — `eff/MDE` ranks by `eff/sd`. Algebra.
**D2** — `var(a−b) = var(a)+var(b)−2cov(a,b)` with both arms on the same prompts, so the paired MDE
is **small** and the pairwise verdicts cannot be predicted from the marginal MDEs in either
direction. **NEGATIVE control confirms the mechanism: destroying the pairing inflates the MDE
×2.25 [2.18, 2.32].** The pairing halves the floor, and even so nothing resolves.
**D3** — the matrix is antisymmetric: **31** unordered pairs, not 62, and BH corrects over 31.

## ⭐ E4 + SHAM · the "peak at k = 6" is exactly one sd-driven inversion

| ordering | result |
|---|---|
| by **eff** | k4, k6, k3, k8, k2, k12, k1 |
| by **eff/MDE** | **k6, k4**, k3, k8, k2, k12, k1 |
| by eff / **pooled** sd *(SHAM: the per-arm sd removed)* | k4, k6, k3, k8, k2, k12, k1 |

Transpositions against the eff order: **1** for eff/MDE, **0** for pooled. **Removing the per-arm sd
removes the inversion** — D1 measured rather than asserted.

## controls — 4 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `coval_core` vs `gen_sham`: **+0.0837 [+0.0733, +0.0936]**, MDE 0.0153 → **BEATS**. Band: a BEATS-everything instrument also fires on g=0 and PLACEBO; a BEATS-nothing one fails here |
| **g=0** | `coval_core` vs **itself**: eff **0.000000** → UNRESOLVED |
| **PLACEBO** | `topw_k4` vs `_detA`: eff **0.000000** — one object under R730, and the placebo uses exactly that |
| **NEGATIVE** | pairing destroyed ×200 → MDE **×2.25 [2.18, 2.32]** |

## ⚠ the registered confound is answered, and in the opposite direction

Does resolution track criterion **overlap** rather than quality? **corr(overlap, \|eff\|/MDE) =
−0.3949** over 27 pairs — **negative**. More shared criteria means *less* resolution, not more, which
is what nesting predicts: two nested arms differ on few prompts, so the difference is small even
though its variance is too. **World C excluded** *(ledger 1086)*.

**Multiplicity**: 31 cells tested, **17 surviving BH at q = 0.05** — and all 17 are k-family pairs
involving `k1`, `k2` or `k12`, the arms that LOSE outright. Non-survivors printed in the artifact.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| the extension is `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` | **an unordered set of 4** *(R767)*, and **no pair within it is resolvably ordered** |
| the released core as *the* core | **not measurably better** than `topw_k3`, `topw_k4` or `topw_k6` — all three UNRESOLVED against it, at MDEs of 0.0079–0.0090 |
| *"the k-curve peaks at k = 6"* *(R767's NEXT)* | ⛔ **retracted before it was published** — on the effect it peaks at k = 4, and the inversion is one sd |
| *"3 to 8 are indistinguishable"* | **confirmed pairwise for the first time**: k3/k4, k3/k6, k4/k6 all UNRESOLVED, and k8 differs from none of them |

## the sentence I can no longer write

*"the released core is the best arm the definition admits."* It is not measurably better than any of
the three alternatives admitted with it.

## NEXT

An unordered extension of four is a *result* about the definition, but it rests on one estimand — A2
against a single human draw — and the register has carried *"whether A2 is the right thing to order
by"* as needing an external criterion since the beginning. What is **not** in the register, and is
reachable, is the other direction: this round measured that a paired arm-vs-arm comparison has an MDE
of **0.0054–0.0090** while the observed gaps are **0.0001–0.0072**, so the design is short by roughly
a factor of two. **The release ships a median of 16 annotators per prompt and this estimator averages
over all of them at n = 968 prompts** — the same shape as the failure recorded in §4's sham row, where
a bound was published from 3 of 16 annotators and dissolved when all 16 were used. The registered
quantity is the paired MDE as a function of the number of prompts and annotators actually consumed,
because *"unordered"* is only a fact about the definition if the design was at its limit when it said so.
