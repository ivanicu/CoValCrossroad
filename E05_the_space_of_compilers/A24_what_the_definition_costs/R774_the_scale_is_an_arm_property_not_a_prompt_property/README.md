# R774 · the "separability scale" is 28% prompt and the rest is which arms you picked

**Two **disjoint** arm families' scales correlate at **+0.2438** against a measured attenuation
ceiling of **0.8620** — **0.283× the ceiling**. Splitting the *committed* five into **overlapping**
halves gives **+0.5097**, so **sharing arms buys 2.09×** of what looks like prompt structure.
⭐ Calibrated on the plant's dose curve the prompt-level component is a width of **≈0.18**, against
the **0.59** R772 read off the spectrum — **R772's "separability scale" overstates the prompt part by
~3×**. Registered A needed ≥0.5× the ceiling and B ≤0.2×; **0.283 is neither, so no world is claimed.**

## check #376 — R773's registered ratio is contaminated, and the arithmetic said so first

`c(p)` **is** the committed-pair A2 distance, and the ratio's **denominator** is the committed-pair
satisfaction distance — the same quantity in another metric. **corr(c, committed) = +0.2042**, so
`sham/committed` must fall in `c` whether or not the sham varies. Run as **two curves**, the reading
inverts:

| c(p) quartile | n | c | committed | **sham** | ratio |
|---|---|---|---|---|---|
| Q1 | 242 | 0.0003 | 0.0047 | **0.0354** | 7.47 |
| Q2 | 237 | 0.0200 | 0.0059 | **0.0376** | 6.32 |
| Q3 | 244 | 0.0486 | 0.0061 | **0.0313** | 5.15 |
| Q4 | 245 | 0.1124 | 0.0078 | **0.0340** | 4.34 |

**corr(c, sham) = −0.0212** — the sham distance is **flat across the whole range**, while the committed
distance rises 1.7×. **The ratio's decline is entirely its denominator**, and R773's *"those prompts
compress everything"* is not what the full population shows *(ledger 1103)*.

## ⭐ E3 · the ontology test, and D3's ceiling

If `c(p)` is a property of the **prompt**, a scale from a **disjoint** arm family must agree with it.
Disjointness asserted; the round exits 2 otherwise.

| | |
|---|---|
| split-half reliability, committed family | **0.8806** |
| split-half reliability, comparison family | **0.8438** |
| **attenuation ceiling** (geometric mean) | **0.8620** |
| **corr(c, c′) across disjoint families** | **+0.2438** = **0.283× ceiling** |
| **SHAM** — the committed five split into **overlapping** halves | **+0.5097** = **2.09×** the disjoint value |
| NEGATIVE — 200 one-sided permutations | −0.0021 **[−0.0654, +0.0665]** |

**D3, declared before the run:** two noisy estimates correlate at most at the geometric mean of their
reliabilities, so the cross-family number is read against a **measured** ceiling and never against 1.0.
The ceiling is **healthy (0.86)**, so World C — *"the question is unanswerable at this n"* — is
excluded *(ledger 1104)*.

## ⭐ the calibration, and the disagreement it exposes

The plant's dose curve (a prompt-level scale multiplying **both** families): width 0.00 → −0.019 ·
0.25 → **+0.338** · 0.50 → **+0.608** · 1.00 → **+0.858**, monotone, detected from 0.25.

**The observed +0.2438 interpolates to a planted width of ≈ 0.18.** R772 read **λ ≈ 0.59** off the
leading eigenvalue share. ⭐ **Those differ by ~3×, and the sham says why**: R772's spectral estimate
was computed within a *single* family, where arm-sharing inflates the co-movement 2.09×
*(ledger 1105)*.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **DISJOINT** | families share **0** members; the round exits 2 otherwise, because a shared arm manufactures the correlation E3 measures |
| **POSITIVE** | planted prompt-scale, swept, monotone; detected from width 0.25, not at 0 |
| **g=0** | width 0 → **−0.0192**, inside the negative band |
| **NEGATIVE** | 200 one-sided permutations → **[−0.0654, +0.0665]**, so +0.2438 is far outside — *"any two \|d\| vectors correlate"* is excluded |
| **PLACEBO** | a family against itself → **1.000000** |
| **CONFOUND** *(registered)* | mean A2 committed **0.5635** vs comparison **0.4910**; `c` quartiles committed [0.0055, 0.0333, 0.0667] vs comparison [0.0416, 0.0856, 0.1479] — the comparison family is a different regime, and the numbers are printed rather than assumed away |

## what this changes in the deliverable

| carried | stands as |
|---|---|
| *"a per-prompt separability scale"* *(R772)* | **~28% of the reliable signal is prompt-level**; the rest is a property of which five arms were chosen. The name overstates it |
| R772's **λ ≈ 0.59** | ⛔ **inflated ~3×** — measured within one family, where arm-sharing buys **2.09×**. The disjoint-family estimate is **≈0.18** |
| R773's *"the prompts compress real arms more than a bad one"* | ⛔ **not the population's behaviour** — the sham distance is **flat** in `c(p)` (−0.0212); only the committed distance moves |
| *"which prompts separate cores"* | **has a small real answer** — a prompt component exists, far outside the permutation band — but it is a third of what the within-family reading suggested |

## the sentence I can no longer write

*"prompts differ in how much they separate arms."* They differ a little; mostly `c(p)` measures how
close **these five** happen to be, and a disjoint family agrees with it at less than a third of what
the instrument's own reliability permits.

## NEXT

The registered bands did not cover **0.283**, so no world was claimed — and that gap is the thing to
close, not by widening the bands but by asking what a *third* disjoint family says. Two families give
one number with no interval; **three give a distribution**, and the release carries enough arms to
build a third disjoint set (`greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4_fit1`, `gen`, `generic` —
sharing no member with either family used here). ⚠ And that set is **rule-heterogeneous** where both
current families are rule-homogeneous, which is a confound the present design cannot see: if the
prompt component is really an artifact of arms built by *similar rules*, a mixed family would show a
lower cross-correlation, not a higher one. The registered quantity is the pairwise cross-family
correlation matrix over three disjoint families, each against the same measured ceiling.
