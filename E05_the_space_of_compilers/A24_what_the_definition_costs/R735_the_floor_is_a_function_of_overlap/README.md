# R735 · the floor is a function of overlap

**The floor is not a constant. It tracks criteria overlap at r = +0.9264 across 153 pairs, and the
k-matched floor for the comparisons R733 and R734 rest on is 0.6458, not the 0.5034 they used.**

## ⛔ This corrects R734 in the OPPOSITE direction from R734's own conclusion
R734 measured a **subtrahend-only** floor of 0.3062 and concluded R733's floor was **too high**, so
its excesses were **understated**. That comparison strips *all* overlap structure. But the arms being
compared (`greedy`, `indep`, `oracle`) are all **k = 4**, and two unrelated k=4 arms already reach
**0.6458**. **So for the comparison that matters the floor was too LOW and the excesses were
OVERSTATED.**

| object | @R733 0.5034 | @R734 0.3062 | **@R735 k-matched 0.6458** | verdict |
|---|---|---|---|---|
| `greedy` | +0.4713 vs +0.2413 | +0.6685 vs +0.4385 | **+0.3289 vs +0.0989** | **EXCLUDED** at all three |
| `indep` | +0.4205 vs +0.2735 | +0.6177 vs +0.4707 | **+0.2781 vs +0.1311** | **EXCLUDED** at all three |

**The verdicts survive every floor. The margins shrink by roughly half.**

## The relation
| k-stratum | pairs | mean overlap | mean floor |
|---|---|---|---|
| k=2 | 3 | 0.291 | **0.4003** |
| k=3 | 3 | 0.672 | 0.4322 |
| k=4 | 3 | 2.103 | **0.6458** |
| k=6 | 3 | 2.664 | 0.5967 |
| k=8 | 3 | 4.511 | 0.6901 |
| k=12 | 3 | 8.794 | **0.8438** |

**Pooled r = +0.9264** over 153 pairs. Mean floor is **not** monotone in k (k=4 exceeds k=6), which
is itself informative: overlap, not k, is the better-ordered predictor.

⛔ **But the confound I named before the run is NOT resolved.** Overlap rises with k by construction,
and **each same-k stratum holds only 3 pairs**, so a within-stratum correlation rests on 3 points.
**This design cannot separate "function of overlap" from "function of k"** — reported as
**UNDERPOWERED, not refuted.**

## ⛔ Two of my own defects, both caught by controls
1. **I excluded the subtrahend by NAME and not by OBJECT.** `random_k4_s0_ctlS0` is an alias of
   `random_k4_s0` *(R730's partition, which was on disk and which I did not use)*, so its clause-①
   margin is identically zero and its correlation undefined — that produced `nan` through the whole
   k=4 stratum. **The partition existed precisely to prevent this.**
2. **My positive control's threshold was mis-specified.** It demanded `|measured − analytic| < 3 SE`;
   at n=968 the SE of mean overlap is ~0.01, so **any** model bias reads as many SE (mean |z| 9.52).
   And the pool size used is the **union of observed selections — a lower bound**, which biases the
   analytic value *up*, so a ratio **below** 1 is the predicted direction. **The control was testing
   the pool-size proxy, not the overlap instrument.** Split: the instrument now gets an **exact**
   control (`overlap(a,a) = k`), and the model gets a reported ratio with its bias direction stated.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: instrument exact on `overlap(a,a)`; model ratio **0.9694**, 124/153 pairs in the
predicted band · **g=0**: the lowest-overlap pair (k=2, overlap 0.281) returns the **minimum** floor
over all pairs, 0.3876 · **NEGATIVE**: pair→overlap permuted → real +0.9264 vs null 99th pct
**0.2023** · **SHAM**: floor vs the arms' **seed indices** (no overlap information) → **−0.0722** ·
**PLACEBO**: 1.000000.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A usable pairs | 171 [1, 500] | **153** | yes |
| B floor ~ overlap Pearson | 0.85 [−1, 1] | **+0.9264** | yes |
| C measured/analytic overlap | 1.00 [0, 5] | **0.9694** | yes |
| D k=4 matched floor | 0.47 [0, 1] | **0.6458** | yes |
| DIRECTIONAL within-strata | — | **UNDERPOWERED** | — |

⚠ **A was 171 and is 153** — because dropping the subtrahend's alias removed one arm and its 18
pairs. The registered number was computed *before* that defect was found.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, **both writes verified**.
**Artifact:** `results/r735_floor_vs_overlap.json` · all 153 pairs with overlap, analytic and floor.
