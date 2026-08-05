# R727 · the zone width is a resample count

**R726's disagreement zone is set by `NBOOT = 1200` — a constant in `R294:117` — not by any property
of the arms.** A synthetic **normal** world at n = 968 and B = 1200, containing no skew and no
arm-to-arm variation whatsoever, reproduces `sd(r) = 0.027699` against the observed **0.027341** —
ratio **1.0131**. The asymptotic quantile-error derivation independently gives **0.027821**.
**Two routes, one answer.**

## DOSE–RESPONSE — the control that makes this Monte-Carlo error and not a coincidence
| B | sd(r) normal | MC err | sd(r) lognormal |
|---|---|---|---|
| 300 | 0.052859 | 0.001049 | 0.053429 |
| **1200** *(shipped)* | **0.027699** | 0.000526 | 0.027653 |
| 4800 | 0.013368 | 0.000878 | 0.013414 |
| 19200 | 0.006840 | 0.000689 | 0.006959 |

**Fitted log–log slope −0.4951** — the −0.5 of Monte-Carlo error. **Raising the resample count
shrinks the zone.** So R726's *"the spread would have to double before a cell entered a zone"*
describes **a choice**, not a property of the data.

## ⛔ The control failed first, and splitting it is the round's second result
v1 gated the round on `|corr(r,asym)| moved > 3sd`, ANDed with a mean-asymmetry check. **It FAILED.**
Diagnosed rather than believed:

- **The two halves target different statistics.** Mean asymmetry moved `−0.00007 → +0.02383`, far
  beyond 3sd — **the instrument sees planted skew.** `corr(r,asym)` moved only 0.0730 against a
  threshold of 0.1309.
- **That threshold was three times a 3-seed spread — 2 degrees of freedom.** Not a threshold; noise
  wearing one.
- **The sweep shows why:** at B = 19200 the same contrast is `−0.0678 → +0.1928`. **The detector's
  power grows with B; at B = 1200 the resample noise swamps the skew.**

⛔ **So any null from `corr(r,asym)` here is silence, not an acquittal** — and v1's directional rested
on exactly that. Restated on the statistic the positive control **proves** can see planted skew:

| | |
|---|---|
| observed mean asymmetry | **−0.00410**, SE 0.00296 |
| z vs the zero-skew world | **−1.38** |
| z vs the planted lognormal world | **−9.43** |

**No detectable skew, by a test whose power is established rather than assumed.**

## ⚠ And `n` cannot be tested here at all
`n` takes two values across 41 arms — **4 of 82 cells** at the minority level (398). Any coefficient
would rest on 4 points. **Reported as UNIDENTIFIED-IN-PRACTICE, never as a null.** R726's NEXT line
asked for this regression; the honest answer is that the release cannot support it.

## Controls — 7 PASS, 0 FAIL
POSITIVE (skew-detection via mean asymmetry) · **CORR-POWER** (reports the corr detector as
UNDERPOWERED rather than hiding it) · g=0 (zero-skew world's mean asymmetry within 3sd of 0) ·
DOSE (monotone, slope −0.4951) · NEGATIVE (permuting r against asym; observed |corr| 0.1342 sits
inside a null of mean 0.0888, p = 0.2275) · SHAM (random covariate matched in mean and sd → 0.1740,
*higher* than the real one, which is itself the point) · PLACEBO (r against a constant → undefined,
as it must be).

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A observed / asymptotic *(disclosed non-blind)* | 0.98 [0, 10] | **0.9828** | yes |
| B simulated sd(r) at B=1200 | 0.0278 [0, 1] | **0.027699** | yes |
| C fitted exponent vs B | −0.50 [−2, 0] | **−0.4951** | yes |
| D corr(r,asym) in the zero-skew world | 0.00 [−1, 1] | **0.0202** | yes |

⚠ **A, and the two inputs to it, were DISCLOSED as non-blind in the preregistration** — computed
inline before the round was written. What stayed failable: the simulation, the exponent, the skew
controls, and every control. **One of them failed.**

## Residue
The true skewness of the per-prompt differences needs the raw difference vectors, which the census
artifact does not carry. Only a re-run of R294 would supply them.

**Artifact:** `results/r727_resample_count.json` · 4 B-levels × 2 distributions × 3 seeds.
