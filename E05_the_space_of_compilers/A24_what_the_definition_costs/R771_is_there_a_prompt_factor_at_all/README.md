# R771 · the two estimands split — no world is claimed, and the factor is sized instead

**Registered worlds A and B each required **two** conditions and reality gave one of each. The
**pairwise** excess over the independence prediction is **−0.0074** (arm-sharing |observed| 0.4864 vs
|predicted| 0.4938) — that is World B. The **spectrum** puts the leading eigenvalue share at
**0.3791** against a simulated independence band of **[0.2974, 0.3172]** — that is World A.
⭐ **Neither is claimed.** What the round produces instead is a **calibration**: interpolating the
observed share on the positive control's monotone dose curve sizes the differential loading at
**λ ≈ 0.59 × the residual sd**.**

## check #373 — the arithmetic repaired the registered quantity before any code ran

**① The rank is forced.** Ten pairwise differences among **five** arms span a 4-dimensional space.
Measured rank **4**; eigenvalues **[3.791, 2.957, 1.771, 1.481, 0, 0, 0, 0, 0, 0]**. **So the uniform
reference is 1/4 = 0.25, not 1/10** — comparing against 1/10 would have manufactured a finding.

**② My first analytic null was wrong and was replaced before the run.** Predicting the arm-sharing
correlation from the **raw** arm variances gave **+0.9271** against an observed **+0.2687** — the raw
variance is dominated by prompt difficulty, which differencing removes. The null needs the **residual**
variances *(ledger 1094)*.

## ⭐ E1 · the residual variances are identifiable, and the fit is a test in itself

Ten equations `var(d_ab) = v_a + v_b`, five unknowns, least squares:

| arm | `v` |
|---|---|
| `coval_core` | 0.005878 |
| `topw_k3` | 0.004042 |
| `topw_k8` | 0.003799 |
| `topw_k4` | 0.002273 |
| `topw_k6` | 0.001864 |

Relative fit residual **0.1748**, **all positive** — admissible. ⚠ Registered in advance: a negative
`v` would have **refuted** the model at that arm, and the round would have said so rather than
clipping to zero, because clipping hides exactly the failure the fit exists to detect.

## ⭐ E2 vs E3 · the split, which is the round's actual content

| estimand | observed | reference | verdict |
|---|---|---|---|
| **pairwise excess**, arm-sharing (n=30) | \|obs\| **0.4864** | \|pred\| **0.4938** → excess **−0.0074** | **B** (\|excess\| < 0.05) |
| disjoint pairs (n=15) | **+0.0312** | predicted **0** | small, same-signed |
| **leading eigenvalue share** | **0.3791** | sham **[0.2974, 0.3172]** | **A** (above the band) |

**D2, declared before the run:** arm-sharing pairs correlate at ~0.5 **under pure independence** —
`v_a/(v_a+v_b)` — so a positive mean correlation is **not** evidence of a common factor. The
measurement is the excess, and the excess is ~0. **Yet the spectrum is more concentrated than
independent residuals at the fitted variances produce.** The reconciling detail is the disjoint
column: 15 pairs at **+0.0312**, individually negligible and all the same sign, which tilts the
leading eigenvector without moving the arm-sharing mean *(ledger 1095)*.

## ⛔ the POSITIVE control failed first, and the reason was algebra I should have derived

A factor loading **equally** on every arm — `R_a + λ√v_a·f` — **cancels in every difference**:
`d_ab = (R_a − R_b) + λ(√v_a − √v_b)·f`, which vanishes when the variances match. Measured: the
leading share sat at **0.308–0.312 at every loading including 1.0**, and was not even monotone.
**Differencing removes what is common — that is exactly why R770 used differences to strip prompt
difficulty — so a common factor is invisible here by construction** *(ledger 1096)*.

The plant was rebuilt with **differential** loadings `[+1.0, +0.5, 0, −0.5, −1.0]`, summing to zero,
so the factor *separates* arms rather than shifting them together — which is what *"some prompts
separate cores"* actually means:

| λ | leading share | detected (> sham 97.5) |
|---|---|---|
| 0.00 | 0.3121 | **False** *(g=0)* |
| 0.25 | 0.3183 | True |
| 0.50 | 0.3556 | True |
| 1.00 | **0.4843** | True |

Monotone, registered band satisfied (0.00 must not detect, 1.00 must). **This is correcting the plant
to be the thing under test, not loosening a criterion.**

## ⭐ the calibration the dose curve makes possible

Observed **0.3791** interpolates on that monotone curve to **λ ≈ 0.59 × the residual sd**, between
the 0.50 and 1.00 rungs. ⚠ **This sizes the factor; it does not establish it** — the registered kill
is what decides, and it is two-conditional and split.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | monotone dose-response on a **differentially**-loading factor; detected from λ = 0.25, not at 0 |
| **g=0** | λ = 0 → leading share 0.3121, inside the sham band |
| **SHAM** | 200 simulations of **independent** residuals at the fitted variances → **0.3072 [0.2974, 0.3172]**. Same rank, same variances, no shared prompt structure |
| **NEGATIVE** | 200 independent prompt permutations → **0.1164 [0.1127, 0.1207]**, excluding *"any ten vectors give this share"* |
| **PLACEBO** | `topw_k4` vs `_detA`: sd **0.0000000000**, excluded by construction rather than dividing by zero |

## what this changes in the deliverable

| carried | stands as |
|---|---|
| R770's fork — one latent factor, or pair-specific noise? | **neither branch is claimed.** The pairwise test says noise, the spectrum says structure, and the registration required both for either |
| *"the heterogeneity might sort by something"* | **weakly, and not by anything the release labels** — the excess lives in the disjoint pairs (+0.0312) and the spectrum, not in arm-sharing correlations |
| the size of whatever is there | **λ ≈ 0.59 × residual sd**, calibrated against a plant, not asserted |

## the sentence I can no longer write

*"a common prompt factor would show up in the difference vectors."* A factor loading equally on all
arms is removed by differencing — only a **differential** one survives, and that is a different
hypothesis from the one R770's NEXT named.

## NEXT

The split is the finding and it has a testable cause: the spectrum's excess concentration sits in the
**15 disjoint pairs at +0.0312**, where independence predicts exactly 0. That is 15 numbers sharing a sign
— computed by `run.py` as the disjoint block of the correlation matrix — each individually inside its
own noise — the classic shape of either a real weak factor
or a **single shared nuisance**, and the release ships one obvious candidate the round did not
control for: **each arm is scored against the same human annotations — one target set per prompt,
computed by `load_targets()` — so a prompt whose annotators disagree more depresses each arm's A2
together and can induce same-signed disjoint correlation without structure in the arms themselves.**
⚠ R770's S1 stratum used annotator *count*, not annotator *agreement*, and those are different
variables. The registered quantity is the partial
correlation of the disjoint pairs after conditioning on per-prompt annotator agreement, because if
+0.0312 is that nuisance then the spectrum's excess is too, and both worlds collapse to B.
