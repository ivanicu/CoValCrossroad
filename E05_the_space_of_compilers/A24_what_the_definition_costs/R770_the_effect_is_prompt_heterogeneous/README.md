# R770 · the effect is prompt-heterogeneous, the annotator lever is worth ≤8.7%, and the extension is not partitioned

**Decomposing every committed pair's per-prompt difference into an **annotator** component and a
**prompt** component: the ratio is **4.99–6.34**, the annotator share is **13.6–16.7%**, so **infinite
annotators would cut the MDE by at most 7.1%–8.7%** — R769's *"annotators exhausted"* now carries a
number from a wholly independent direction. **I² = 0.833–0.864**: the heterogeneity is real. ⭐ And it
does **not** partition the extension: **0 flips** across **90** pre-registered cells, against a sham
of **0.00 [0, 0]**. **WORLD A** — R768's unordered set stands as stated.**

## check #372 — my own NEXT asked for a quantity that does not exist

R769 registered *"the per-prompt difference sd regressed on the strata the release ships."* **The
difference vector holds one value per prompt, so it has no per-prompt sd** — an sd computed *across*
prompts cannot be regressed *on* prompts. **Seventh closing line this arc the next round's first check
had to repair** *(ledger 1090)*.

⭐ **The annotator dimension supplies the well-posed version.** `A2(p)` is a mean over that prompt's
annotators, so `d(p)` has its own SE from the annotator draw — median **0.029264** — and that makes
the decomposition below possible at all.

## ⭐ E1 · the variance decomposition, and what it forbids

| pair | between | within | ratio | within share | **max MDE gain** |
|---|---|---|---|---|---|
| `coval_core`/`topw_k3` | 0.009901 | 0.001867 | 5.30 | 0.1587 | 8.3% |
| `coval_core`/`topw_k4` | 0.008970 | 0.001689 | 5.31 | 0.1585 | 8.3% |
| `coval_core`/`topw_k6` | 0.007637 | 0.001529 | 4.99 | 0.1668 | **8.7%** |
| `coval_core`/`topw_k8` | 0.008982 | 0.001546 | 5.81 | 0.1469 | 7.6% |
| `topw_k3`/`topw_k4` | 0.003657 | 0.000659 | 5.55 | 0.1527 | 8.0% |
| `topw_k3`/`topw_k6` | 0.007135 | 0.001228 | 5.81 | 0.1469 | 7.6% |
| `topw_k3`/`topw_k8` | 0.009287 | 0.001464 | 6.34 | 0.1362 | **7.1%** |
| `topw_k4`/`topw_k6` | 0.004871 | 0.000823 | 5.92 | 0.1446 | 7.5% |
| `topw_k4`/`topw_k8` | 0.007177 | 0.001139 | 6.30 | 0.1370 | 7.1% |
| `topw_k6`/`topw_k8` | 0.003805 | 0.000635 | 5.99 | 0.1431 | 7.4% |

**D1, a derivation:** `total = between + within/n_annot`, so driving annotators to infinity removes
only the within share and the MDE falls by `1 − √(1 − share)` — **7.1% to 8.7%.** R769 counted that
the annotator dimension was consumed; this bounds what consuming *more* of it could ever buy
*(ledger 1091)*.

## ⭐ E2 · the heterogeneity is real, and one reading of it is forced

**I² = 0.833–0.864** across all ten pairs — the between-prompt component is ~85% of the total.

⛔ **D3, declared before the run:** `mean/sd` runs **0.0009–0.0779**, so a near-balanced sign split is
nearly forced and **is not evidence of a partition.** ⚠ And the observed shares of `d > 0` are
**0.16–0.32**, *not* near 0.50 — but the complement includes **exact ties**, which a sign-based A2
over six pairwise comparisons produces often, so *"the minority of prompts carries the mean"* is
**not** a conclusion this round supports and is not drawn.

## ⭐ E3 · no partition — 0 flips in 90 cells

A **flip** = two levels of a stratum whose means have **opposite signs** and whose intervals **both**
clear their own MDE.

| stratum *(fixed before the run, a property of the PROMPT)* | flips |
|---|---|
| S1 annotator count (quartiles) | **0** |
| S2 response-set size | **0** |
| S3 the **baseline's** A2 — admissible because the baseline is neither arm | **0** |

**90 cells tested, 0 flips**, sham **0.00 [0, 0]**, negative **0.00**. ⚠ Any stratum derived from
`d(p)`, `A2_a(p)` or `A2_b(p)` was **excluded by construction**, not by care — §4's
*conditioning on the outcome*.

## ⛔ the POSITIVE control could not pass, and the fix was not a bigger plant

First construction: plant `±delta` with `delta = 2 × mde(d0)` — the **full**-sample MDE — while
`flips()` evaluates each level against its own **half**-sample MDE, **√2 larger**. So "2× MDE" was
really 1.41× the relevant one, and the uncentred baseline (`d0[~half].mean() = +0.0060`) pushed the
negative side to **|m2| = 0.01107 against MDE2 = 0.01234** — just under. **§4's *control that cannot
PASS*: the threshold sat above what the design returns under the plant I chose** *(ledger 1092)*.

Repaired by sizing the plant against **the MDE the test uses**, **centring** it, and **sweeping** it:

| planted delta | flip recovered |
|---|---|
| 0.0 × half-sample MDE | **False** *(g=0)* |
| 0.5 × | False |
| 1.0 × | False |
| **2.0 ×** | **True** |

⚠ **And my code had required recovery at 1× — which the preregistration never said.** 1× is the
test's own detection threshold, i.e. its **50%-power point**, so demanding a hit there demands 100%
power where the design has 50% by construction. The registered band is *"0× must not fire, 2× must"*,
and restoring it is **matching the registration, not loosening a control** *(ledger 1093)*.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | monotone dose-response; recovered at 2×, not at 0× — the registered band |
| **g=0** | delta = 0 on the same machinery finds no flip |
| **PLACEBO** | an arm against itself: variance **0.0000000000**, flips 0 |
| **SHAM** | 200 **random** equal-sized partitions: flips **0.00 [0, 0]** |
| **NEGATIVE** | 200 label permutations of S1: flips **0.00 [0, 0]** |

⚠ **The sham returning exactly 0 is a statement about the test's conservatism, not a triumph.** The
dose curve says a flip needs ≳2× the half-sample MDE ≈ **0.024** — so the honest conclusion is **no
partition detectable at this resolution**, with the resolution named.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| *"the annotator dimension is exhausted"* *(R769, a count)* | **bounded**: even infinite annotators buy **≤8.7%** of MDE. The count and the bound agree from independent directions |
| *"the extension is an unordered set"* *(R768)* | **stands, and is now also not a PARTITION** — 0 flips in 90 cells at a resolution of ~0.024 |
| the per-prompt effect | **~85% between-prompt** (I² 0.833–0.864). The difference is a property of prompts, not one number measured with annotator noise |
| inverse-variance weighting | **would change the estimand**, not tighten this one — computed and labelled, never substituted *(D2)* |

## the sentence I can no longer write

*"more annotators might resolve it."* At most 8.7% of the MDE is available there, against gaps needing
a factor of 1.2 to 99.

## NEXT

The between-prompt component is **~85%** of the variance and this round showed it does not sort by
any stratum the release ships — annotator count, response-set size, or baseline difficulty. What has
**not** been asked is whether it sorts by anything at all, or is irreducible: `d(p)` is a 968-vector,
and its **autocorrelation with a second arm pair** is computable with no new data. If
`d(coval_core, topw_k4)` and `d(coval_core, topw_k6)` are strongly correlated across prompts, the
heterogeneity is a property of the **prompt** (some prompts separate arms and some do not) and is a
single latent factor; if they are uncorrelated, it is pair-specific noise and no stratification could
ever help. The registered quantity is the correlation matrix of the ten difference vectors and its
leading eigenvalue share, because that decides whether "which prompts separate cores" is a question
with an answer.
