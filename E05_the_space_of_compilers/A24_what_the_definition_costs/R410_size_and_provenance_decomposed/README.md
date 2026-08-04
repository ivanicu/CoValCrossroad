# R410 — neither size nor provenance is resolvable. The partial order has no decomposition this design can reach.

**The decision this makes safe:** *what separates R409's tiers?* **Nothing this release can resolve —
and that retires the question rather than leaving it open.**

## Result — `W_NEITHER`. Three controls pass. **No GPU.**

### (A) SIZE — provenance held constant inside `topw_k*`

| arm | k | e vs max-blind |
|---|---:|---:|
| `topw_k3` | 3 | +0.004114 |
| `topw_k4` | 4 | +0.006705 |
| `topw_k6` | 6 | +0.008183 |
| `topw_k8` | 8 | +0.004810 |

| adjacent-k paired contrast | e | 95% CI | |
|---|---:|---|---|
| `topw_k3 − topw_k4` | −0.002591 | [−0.00723, +0.00205] | inside 0 |
| `topw_k4 − topw_k6` | −0.001478 | [−0.00689, +0.00393] | inside 0 |
| `topw_k6 − topw_k8` | +0.003373 | [−0.00119, +0.00793] | inside 0 |

### (B) PROVENANCE — size held constant at k = 4

**`coval_core − topw_k4 = +0.002297`**, paired se **0.003044**, n = 968, CI **[−0.00367, +0.00826]**,
own MDE **0.008528**.

> **The effect is 0.27 of its own MDE.** The design is under-powered for this contrast by ~3.7×.

### Multiplicity — Holm over all four, raw *and* corrected

| contrast | raw p | Holm p | survives |
|---|---:|---:|---|
| `topw_k6−topw_k8` | 1.47e-01 | 5.89e-01 | False |
| `topw_k3−topw_k4` | 2.74e-01 | 8.21e-01 | False |
| `coval_core−topw_k4` | 4.51e-01 | 9.01e-01 | False |
| `topw_k4−topw_k6` | 5.92e-01 | 9.01e-01 | False |

**Not one is close, even raw.**

## ⛔ R409's own NEXT, settled as a DERIVATION rather than measured

*"Size alone cannot explain it"* — **one fact settles it**: `coval_core` and `topw_k4` are **both
k=4** and land in different tiers, and a function of k alone cannot map one input to two outputs.
**Labelled a derivation; it is not this round's evidence.**

## ⭐ The matched-size contrast is NOT a difference of two differences

Both k=4 arms are scored against the **same** per-k maximum reference, so in
`d_a − d_b = (a2_a − ref) − (a2_b − ref)` the reference **cancels**. Verified numerically:
`max|(d_a−d_b) − (a2_a−a2_b)| = 2.8e-17`. *"A covariate raising both arms" is precisely the shape
that has cost this campaign before, so it was measured rather than argued.*

## Controls

| | returned |
|---|---|
| **SEPARATION (+)** | `oracle_k4 − topw_k4` (same k) = **+0.0641**, CI [+0.0573, +0.0709] — `PASS`. **~28× the contrasts of interest**, so the nulls below are not a blind paired test |
| **SELF (−)** | an arm minus itself = **exactly 0.0**, se **exactly 0.0** — `PASS`. A placebo that must return exactly zero, and it can fail if the pairing is misaligned |
| **CANCELLATION** | **2.8e-17** — `PASS` |
| **TWO ESTIMATORS** | analytic paired-t and a 2,000-draw bootstrap at 3 seeds agree to ~3e-4 on every CI. Cheap, and a disagreement would have been a bug |

## ⚠ And this downgrades R409's own summary

R409 reported *"the honest summary is a partial order: `{coval_core, topw_k6}` above
`{topw_k8, topw_k3}`."* **No pairwise contrast supports it.** R409 measured a **joint rank
distribution**, which can carry information while **no individual pair is separable** — both are
correct, but the partial order must be read as *a description of bootstrap rank frequencies*, not as
an established ordering of the arms. R409's README is annotated in place.

## Register

| criterion | status |
|---|---|
| **isolating what "provenance" means** | **N/A** — `coval_core` differs from `topw_k4` in several ways at once; a resolved contrast would name a **bundle**. Separating them needs arms varying one thing, which this release does not ship |
| **a causal claim about k** | **N/A** — the k arms are not randomly assigned; (A) is descriptive |
| **a second release / second judge** | **N/A** — one release; at 0.8B nothing is admitted (R358/R359) |

## The sentence I can no longer write

> *"the released core beats a rubric-weighted set of the same size"* — **the contrast is +0.0023
> against an MDE of 0.0085.** It is not a small effect that was found; it is an effect this design
> could never have resolved, and R409's ranking made it look like one that had been.

Artifact: `results/r410_size_provenance.json`, source-stamped.
