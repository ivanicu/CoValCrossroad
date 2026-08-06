# R826 · The response-only bar saturates, and it saturates ON the released core

**E05 · A24 · R826. Pre-registered verdict: UNVERIFIED — and that is the kill working.**
968 prompts × 4 responses · 9 effort levels × 8 splits · every unsupervised stage fit on the fit
half. Source `25df1bef`. Two seeds byte-identical: `7a8adc5ff5fcbc21d866a5b23b6b4a7b`.

## The decision this makes safe

Three defensible response-only classes had given three verdicts on `coval_core`: 30 hand-built rules
bar 0.4557 (binds on nothing), 14 lexical features 0.5197 (binds on 25, **admits**), plus char
n-grams 0.5723 (**excludes**). Nothing separated them but how many features got built. **If the bar
never saturates, ④ has no verdict at all without a modelling budget nobody can principledly set.**

## The effort curve, held out

| k | bar | rise | sham | excess | paired vs core | verdict |
|---:|---:|---:|---:|---:|---|---|
| 0 | 0.524670 | — | 0.524670 | +0.000000 | −0.042757 [−0.045471, −0.040043] | admits |
| 5 | 0.528836 | +0.004166 | 0.522825 | +0.006011 | −0.038591 [−0.046147, −0.031035] | admits |
| **10** | **0.558620** | **+0.029785** | 0.521704 | +0.036916 | −0.008807 [−0.010880, −0.006733] | admits |
| 20 | 0.564312 | +0.005692 | 0.519149 | +0.045163 | −0.003115 [−0.005872, −0.000357] | admits |
| 40 | 0.570737 | +0.006425 | 0.512967 | +0.057770 | +0.003310 [−0.000193, +0.006813] | indistinguishable |
| 60 | 0.570526 | −0.000210 | 0.510021 | +0.060505 | +0.003100 [−0.000435, +0.006635] | indistinguishable |
| 100 | 0.572551 | +0.002025 | 0.504843 | +0.067708 | +0.005124 [+0.001497, +0.008751] | **EXCLUDES** |
| 150 | 0.572162 | −0.000389 | 0.499425 | +0.072738 | +0.004736 [+0.001474, +0.007997] | **EXCLUDES** |
| 200 | 0.570339 | −0.001823 | 0.493813 | +0.076527 | +0.002913 [−0.000332, +0.006157] | indistinguishable |

**It saturates.** Last rise **−0.001823** against a noise floor of **0.007376**. Most of the gain
arrives by **k = 10** — ten SVD components of character n-grams.

⭐ **The plateau (k ≥ 40) sits ON the core.** Bar **0.571263**, mean paired **+0.003836**, and across
the five saturated cells: **2 exclude · 3 indistinguishable · 0 admit.**

## The world I failed to pre-register

I registered three: *saturates above · saturates below · no saturation*. **The fourth is what
happened — saturates ON the core.** The kill read only k = 200 (`lo` = −0.000332), matched no world,
and printed **UNVERIFIED**.

⭐ **A kill that refuses because the outcome was not in your world list is the kill working.** The
plateau spans five cells and straddles the core; a single endpoint was never the saturated value.
The pre-registered verdict stands as UNVERIFIED and is not being rewritten to fit.

## What it downgrades

⚠ **R825's headline was measured at exactly one k.** *"④ excludes the released core"* holds at
k = 100 — R825's own 12-split paired test gives +0.006197 [+0.003923, +0.008471] there, and this
round reproduces it at 0.572551 — **but k = 100 is not special.** Its neighbours at 40, 60 and 200 do
not resolve. **R825's finding stands at k = 100 and does not generalise across the plateau.**

## Controls

| control | returned |
|---|---|
| **OBJECT** | k=0 → **0.524670** vs R824's 0.519689 ✓; k=100 → **0.572551** vs R825's 0.572335 ✓ (tol 3× mean per-split sd = 0.0221) |
| **PLACEBO** | `coval_core` against itself: **exactly 0** |
| **POSITIVE** | dose vs **the plant**: g=1.0 **0.9875** · 0.5 0.5738 · 0.2 0.5093 · **g=0 0.4974** — monotone, recovers, at chance at zero dose |
| **NEGATIVE** | labels shuffled at fit: **0.452774**, below every real cell |
| **SHAM ⭐** | swept at every k — **declines** 0.524670 → 0.493813 |
| **NOISE FLOOR** | mean per-split sd across k: **0.007376** |

⭐ **The sham is the strongest result here.** Capacity alone makes the held-out bar **worse**, so the
excess over sham grows monotonically to **+0.076527**. Every point of the rise is the features; none
of it is the dimension count. A sham measured at one k would have licensed none of this.

## ⭐ Independent corroboration, on a different axis

A second session swept **feature TIERS** while this round swept **SVD components**, and found the
same shape (`4f484ca9`, strict = every unsupervised stage closed):

| | T1 lexical | **T2 +char** | T3 +word | T4 all |
|---|---:|---:|---:|---:|
| strict bar | 0.523607 | **0.572335** | 0.570582 | **0.566519** |

**Their curve peaks at T2 and falls at both richer tiers** — saturation and turnover, reached along
an axis this round never varied. Their peak **0.572335** against this round's plateau **0.571263**
agrees to 0.001, and **their T4 lands at 0.566519 against `coval_core`'s 0.566477 — a difference of
0.000042.**

⭐ Their audit also eliminates a confound for R825: **closing the leak RAISES the bar** (every
`as_run − strict` is negative from T2 on, all inside their paired floors), so the crossing is not
manufactured by contamination. Their framing is the correct one and worth quoting: *"a confound
eliminated, never a confirmation — the audit could only have killed the verdict, and it did not."*

This is §2.5's convergent-divergent-designs case, which is the strongest evidence form available on
one site.

## What this round got wrong

**My multiplicity test was unusable and I nearly reported its verdict.** The run printed *"BH q=0.05
over 9 paired tests: 3 survive, 6 do not"* — computed from a **sign-proportion p at n = 8**, whose
granularity is 2/8 = 0.25 and which can therefore take only five distinct values. **A statistic with
five possible values cannot rank nine cells for BH.**

Recomputed from the CIs with a t-derived p: **9 of 9 survive.** The coarse version would have
retracted k=100 and k=150 for the wrong reason — **and it failed toward *no effect*, the direction
that gets thanked rather than audited.** Second occurrence this session; the first was comparing a
mean over splits to a per-split floor.

## ⛔ Derivations, labelled

- **D1** In-sample monotonicity in k is **forced** (a k-truncation is nested in k+1). Held out it is
  not — and indeed the curve **falls** at k = 150 and 200, as R823's falling-bar result predicted.
- **D2** **A crossing exists by construction** between k=0 (admits) and k=100 (excludes). Finding one
  is not a finding; only its location, sharpness and the saturation are measurable.
- **D4** Truncated-SVD components are **nested**, so one SVD(200) fit per split serves every k by
  slicing — an exact identity, and why the sweep cost 8 vectoriser fits instead of 72.

## What this round cannot do

| criterion | requires |
|---|---|
| decide the plateau's side of the core | more splits; at n=8 the plateau's se leaves it straddling |
| generalise beyond char n-grams | another feature family; k* is a property of this one (D3) |
| cross-release / cross-model | a second site |
| construct validated | an external gold standard for "core" |
