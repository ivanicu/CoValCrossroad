# R772 · prompts do differ in how much they separate arms — and about a quarter of that is noise amplitude

**The scale is real and large: the **15 disjoint** |d| pairs co-move at **+0.2974** against an
independence reference of **+0.0000 [−0.0314, +0.0323]**, calibrating to a lognormal width of
**≈0.55**. Leave-one-pair-out normalisation drops the leading eigenvalue share **0.3791 → 0.3298**,
below a matched random-divisor sham of **[0.3541, 0.4090]** — so the scale explains real structure.
⛔ **But the registered confound fires**: `corr(c, within-prompt SE) = +0.5278` against a
pre-registered line of **0.50**. **WORLD B**, by a margin of **+0.0278**.**

## check #374 — R771's own algebra refuted R771's NEXT

R771 closed by naming a shared nuisance: *"a prompt whose annotators disagree more depresses each
arm's A2 together."* **That is an ADDITIVE COMMON term, and R771 proved — and its own failed plant
demonstrated at four loadings — that such a term cancels exactly in every difference.** So the
registered partial correlation was aimed at the one object the instrument cannot see.
**Eighth closing line this arc needing repair, and the first refuted by the round that wrote it**
*(ledger 1097)*.

⭐ What does **not** cancel is a **multiplicative** scale: `d_ab(p) = c(p)·δ_ab + noise` predicts all
three of R771's observations at once — small positive disjoint correlations, ~zero excess among
arm-sharing pairs, and extra spectral concentration.

## ⭐ E1 · the co-movement, with only the admissible block counted

| block | mean \|d\| correlation |
|---|---|
| **15 disjoint pairs** *(admissible)* | **+0.2974** |
| 30 arm-sharing pairs *(D2: co-move with no scale at all)* | +0.4560 |
| **independence reference**, 200 simulations | **+0.0000 [−0.0314, +0.0323]** |

**D2, declared before the run:** `|d_ab|` and `|d_ac|` share arm *a*, so their magnitudes co-move for
the same reason their signed values do — **the arm-sharing block is not evidence** and is reported
only so the contrast is visible.

**Calibrated against the plant's dose curve** (width 0.25 → +0.0950, 0.50 → +0.2731, 1.00 → +0.5204):
the observed +0.2974 interpolates to a **lognormal width ≈ 0.55**.

## ⭐ E3 · leave-one-pair-out, because the obvious normalisation is circular

**D3, declared before the run:** dividing by a `c(p)` computed from the same ten pairs is
**conditioning on the outcome**, and shrinks correlations mechanically whether or not a scale exists.
A quick probe gave **0.3791 → 0.3330** that way; **that number is inadmissible and is not reported as
evidence.** Under leave-one-pair-out — pair *i* normalised by the mean |d| of the **other nine**:

| | leading eigenvalue share |
|---|---|
| raw | **0.3791** |
| **LOPO-normalised** | **0.3298** |
| **SHAM** — normalise by a random draw from `c`'s own distribution, ×200 | **0.3822 [0.3541, 0.4090]** |
| NEGATIVE — normalise by a **permuted** `c`, ×200 | 0.3826 [0.3528, 0.4099] |

⭐ **The sham and the negative both RAISE the share; only the aligned scale lowers it.** So dividing
by *any* vector of that distribution is not what does it — the alignment is *(ledger 1098)*.

## ⛔ E2 and the confound — the verdict, and how close it sits to its own line

| quantity | value |
|---|---|
| corr(`c`, per-prompt **annotator agreement**) — R771's nuisance, in the form the algebra permits | **+0.1246** |
| corr(`c`, per-prompt **within-SE**) — the registered confound | **+0.5278** |
| registered threshold | **0.50** |
| **margin** | **+0.0278** |
| r² — the share of `c`'s variance the noise SE explains | **0.2786** |

**WORLD B fires**, and it fires by 0.028. ⚠ **The label overstates what the number says**: r² = 0.279
means **~72% of the scale is not noise amplitude.** The registration drew a binary line at 0.50 and
the round reports the verdict that line gives — but prints r² beside it so the magnitude is visible
rather than the label *(ledger 1099)*. R771's specific nuisance, annotator agreement, is **not** the
driver even multiplicatively: **+0.1246**.

## controls — 4 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | a **multiplicative** plant, swept: 0.00 → −0.0002 · 0.25 → +0.0950 · 0.50 → +0.2731 · 1.00 → **+0.5204**. Monotone; detected at 0.25 and above, not at 0. ⚠ Multiplicative **because that is the object under test** — the defect R771 caught was planting an additive factor the instrument cannot see |
| **g=0** | width 0 → −0.0002, inside the reference band |
| **SHAM / NEGATIVE** | as tabled — a random or permuted divisor **raises** the share |
| **PLACEBO** | `topw_k4` vs `_detA`: max \|d\| **0.0000000000**, excluded by construction |

**D4 honoured:** `c(p)` quantiles **[0.0000, 0.0055, 0.0333, 0.0667, 0.3042]** with **223 zeros** —
reported as quantiles, never as a min/max ratio, and the divisor floor (5th percentile of the
positive scales, **0.00893**) is stated.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| R771's split — spectrum says structure, pairwise says none | **reconciled by a multiplicative scale**: prompts differ in how much they separate arms, which inflates every pair's difference together without changing arm-sharing correlations |
| *"which prompts separate cores"* | **has a partial answer** — a per-prompt scale of lognormal width ≈0.55 — and **~28% of it is heteroscedastic noise**, so the separability reading is bounded, not clean |
| R771's registered nuisance *(annotator agreement)* | **refuted twice**: by algebra as an additive term, and measured at **+0.1246** as a multiplicative one |
| 223 prompts | have `c(p) = 0` — they separate **none** of the five arms at all |

## the sentence I can no longer write

*"a shared nuisance in the annotations could explain the disjoint correlation."* An additive one
cancels, and the multiplicative candidate the data actually supports correlates with annotator
agreement at only +0.12.

## NEXT

**223 of 968 prompts have `c(p) = 0`** — the five extension members score identically on them, so
they contribute nothing to any pairwise comparison while counting fully in each denominator. That is
**23% of the population carrying zero information about the ordering**, and it is a property of the
prompts, not of the arms. R769's required-n figures were computed over 968; if
the informative population is really ~745, those figures are **understated by the same factor the
zeros represent** — but in the other direction, dropping them changes the estimand from *"the average
over this prompt population"* to *"the average over prompts that discriminate"*, which is the G1 error
this campaign has made at three levels. The registered quantity is the paired MDE and the required-n
recomputed on the discriminating subset, reported **beside** the full-population figures as a
different estimand rather than a correction to the same one.
