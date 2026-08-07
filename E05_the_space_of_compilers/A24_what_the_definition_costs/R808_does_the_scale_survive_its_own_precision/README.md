# R808 · the scale survived a 2.3× sharpening of its own instrument, and the leak proxy's identity matters

`run.py` · `PREREGISTRATION.txt` · `results/precision_sweep.json` · 968 prompts × 5 arms × 4 k × 4 j
× 20 splits · **A-STABLE · B-SPECIFIC** · two hash seeds byte-identical, md5
`60b19ed18e351cc3a45cef13a7168199`

## THE DECISION THIS MAKES SAFE

**R807's scale is not an artifact of one λ estimate.** Sharpening the instrument more than doubled
λ and the raw slope, and moved the corrected estimate by **0.0154** — an eighth of its own noise.

| k (parity-0 annotators on the x-side) | λ | RAW slope | **DISATTENUATED (fitted mean)** |
|---:|---:|---:|---:|
| 1 | 0.2094 | 0.1292 | **0.561** |
| 2 | 0.3477 | 0.2175 | **0.572** |
| 3 | 0.4291 | 0.2671 | **0.569** |
| 4 | 0.4864 | 0.3077 | **0.576** |

> **λ ×2.32 · raw slope ×2.38 · corrected estimate spread 0.0154, against 3× its across-split sd of
> 0.1281.** → **A-STABLE**

This is realstat §4's *"a control validated by its own instrument's noise"* remedy aimed at my own
headline: **if an estimate moves as the instrument sharpens, the correction was never correcting
anything.** It did not move.

⭐ **And the two pre-registered derivations both held**: λ rises with k (**D1**) and the RAW slope
rises with it (**D2**) — so the raw drift that would look alarming is exactly what attenuation
predicts, and only the *corrected* number drifting would have been evidence.

## ⛔ CHECK #410 · R807's NEXT ASKED FOR THE WRONG SWEEP, AND IT WAS MY SWEEP

R807 closed by proposing *"recompute at 2, 3, 4 and 8 parity-1 annotators … as the leak proxy
sharpens."* Reading R807's own definition: **λ is the slope of the leak's margin on parity-0 half B
against half A** — the reliability of the **evaluation draw**, not of the proxy. More parity-1
annotators change **what the leak is**; more parity-0 annotators change **how noisily it is
measured**. The NEXT conflated them, so this round separates them into two axes with **different**
pre-registered predictions.

## ⭐ B-AXIS · THE LEAK PROXY'S IDENTITY MATTERS, AND IT MATTERS MORE TO THE FITTED ARMS

The leak's modal class built from **j** parity-1 annotators — this changes the object, not its
measurement error:

| j | λ | `oracle_k4_fit1` | `greedy_k4_fit1` | `indep_k4_fit1` | `coval_core` | `topw_k4` |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.5834 | 0.403 | 0.387 | 0.339 | 0.231 | 0.231 |
| 2 | 0.5658 | 0.402 | 0.384 | 0.340 | 0.242 | 0.240 |
| 4 | 0.5546 | 0.467 | 0.436 | 0.381 | 0.256 | 0.239 |
| 8 | 0.4954 | **0.617** | 0.578 | 0.492 | 0.314 | 0.332 |

| rise, j = 1 → 8 | |
|---|---|
| fitted mean | **+0.186** |
| honest mean | **+0.092** |
| ⭐ **contrast** | **+0.094** vs a pre-registered threshold of **0.079** → **B-SPECIFIC** |

**The fitted arms track the specific labels they were fitted to.** As the proxy converges on the
actual fit target, they follow it twice as fast as arms that never saw a parity-1 label.

⚠ **The honest arms rise too (+0.092), and that is not a defect — it is the floor.** A modal class
built from more annotators is a better estimate of the population ordering, which *any* good arm
tracks. That is precisely why the estimand is the **differential** and not the level.

⚠⚠ **And the B verdict is MARGINAL: +0.094 is 1.19× its threshold.** A paired CI on the contrast was
**not** pre-registered and this round does not quote one — so **B-SPECIFIC should be read as the
pre-registered rule firing, not as a resolved interval.** The next round's first job is that CI.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R807's λ **0.459704** and all five disattenuated values (**0.649690 / 0.611484 / 0.503511 / 0.348934 / 0.337862**) reproduced on its own fixed split | PASS, else exit 2 |
| PLACEBO | the leak regressed on **itself** at every k: **1.000000000** ×4 | PASS — exact |
| g=0 | the pure leak copy, disattenuated, at every k: **1.000000000** ×4 | PASS — the scale's ceiling holds at every precision |
| POSITIVE | the planted half-honest/half-leak arm against its predicted midpoint **at every k**: 0.660/0.659 · 0.656/0.662 · 0.656/0.662 · 0.663/0.661, |diff| ≤ **0.006** | PASS — calibrated across the whole sweep, not at one point |
| NEGATIVE | permutation null (200) at both ends: k=1 max **+0.0481** vs real **+0.1467**; k=4 max **+0.0679** vs real **+0.2867** | PASS |
| NOISE FLOOR | across-split sd of the disattenuated slope: **0.0427** | measured over 20 splits per cell |

⭐ **The positive control is the load-bearing one here.** A calibration that held at one k and failed
at another *is* the drift this round was looking for; it held at all four to within 0.006.

## POPULATION, STATED RATHER THAN ASSUMED

968 prompts. Parity-0 per prompt: median **8**, min **2**, max **23**; parity-1 median **8**, min
**2**. **620 of 968** carry ≥ 8 parity-0 annotators, so at k=4 the x-side is capped by each prompt's
own count on the remaining 348 — the A-axis uses each prompt's own cap rather than dropping prompts,
and the counts are printed at run time.

## WHAT DIED

- **R807's NEXT as posed** — it swept the axis λ does not measure.
- **"R807's 0.50–0.65 is an artifact of one λ estimate"** — the instrument sharpened 2.3× and the
  estimate moved 0.0154.
- **B-GENERIC** — the leak proxy's identity is not interchangeable with general annotator consensus,
  though only at 1.19× the pre-registered threshold.

## WHAT SURVIVES — AND THIS ROUND ADDS

R807's scale, now with the one property that makes a disattenuated number trustworthy: **invariance
to the precision of the thing it divides by.** And a new differential test — sensitivity to the
proxy's identity — on which fitted arms move **twice** as far as honest ones.

## SCOPE

968 prompts × 4 responses · annotators split by index parity; y-side a fixed half of parity-0,
x-side k ∈ {1,2,3,4} from the complement · leak's modal class from j ∈ {1,2,4,8} parity-1
annotators · 5 named arms + 3 synthetic · outcome = arm − `POOL[0:4]` · 20 independent splits per
cell · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| k beyond 4 with a fixed y-side | more parity-0 annotators per prompt; the median is 8 and the y-side takes half — **checked**, and the per-prompt cap is printed rather than silently truncating |
| j beyond the full parity-1 set | more annotators; at j=8 the proxy already **is** the arms' fit target, which is why the B-axis is read as a trend and not as a level |
| a paired CI on the B contrast | it was not pre-registered; quoting one now would be choosing a statistic after seeing the result — **named here as the next round's first job** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The scale is precision-invariant and the fitted arms are proxy-identity-sensitive at roughly twice
the honest rate. Computed by this round's `run.py`, the B contrast is **+0.094** against a threshold
of **0.079** — a ratio of **1.19**, which is the weakest link in the round. The step is to put an
interval on exactly that contrast: bootstrap the fitted-minus-honest rise over prompts, pre-register
it as the estimand rather than a threshold rule, and report whether it excludes zero. If it does,
"the fitted arms track the specific labels they were fitted to" becomes a resolved claim the
definition's clause ③ can be written against; if it does not, the B-axis returns UNVERIFIED and the
only surviving statement is the A-axis invariance.
