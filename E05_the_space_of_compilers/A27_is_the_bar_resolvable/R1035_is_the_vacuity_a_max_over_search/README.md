# R1035 — R1034's `∅` is **seed-dependent**, and its "exact" is withdrawn

**The decision this round makes safe:** whether ②′'s vacuity is a fact or a coin flip at the
resolution floor. **It is a coin flip** — and the quantile curve, not the endpoint, is what stands.

## ⛔ Two of my own rounds disagreed, and that was the measurement

R1034 reported `∅` at q=100 under seeds (1034, 2068, 3102) and called emptiness **exact**. The same
construction at (1035, 2070, 3105) admits **`coval_core`**. Rather than pick a seed set, I measured
the **margin** across **seven** seeds — including R1034's own three:

| seed | beats % of family | min `lo` | verdict |
|---:|---:|---:|---|
| 1034 | 99.98 | −0.000047 | excluded |
| 2068 | 99.98 | −0.000098 | excluded |
| 3102 | 99.98 | −0.000167 | excluded |
| 1035 | 100.00 | +0.000161 | **admitted** |
| 2070 | 100.00 | +0.000301 | **admitted** |
| 3105 | 100.00 | +0.000113 | **admitted** |
| 4141 | 100.00 | +0.000484 | **admitted** |

**Admitted in 4 of 7.** Min-`lo` range **[−0.000167, +0.000484]** against R923's reference scale
**+0.005736** — **34× larger**.

⭐ **So the extension under closure is neither `∅` nor `{coval_core}` — it is UNRESOLVED.** R1034's
**monotonicity** argument survives (more comparators can only remove arms). **What falls is calling
the measured `∅` exact.**

## ⭐ The quantile curve is what stands (G4 — a curve, not a cell)

| q | \|ext\| | 7 seeds agree |
|---:|---:|---|
| 0 | 73 | ✓ |
| 50 | 12 | ✓ |
| 75 | 12 | ✓ |
| 90 | 11 | ✓ |
| 95 | **9** | ✓ |
| 99 | **8** | ✓ |
| 100 | — | **⚠ seeds disagree** |

**A small, stable, non-empty extension exists over q ∈ {50…99}, seed-identical at all seven.** Only
the endpoint q=100 is unstable — which is exactly where a **maximum over a search** sits.

⛔ **The precedent is R863's, cited not claimed:** it bounded clause ④'s 1,820-member family at
`null_p95`, not its max. What is new here is the curve for ②′, not the device.

## ⛔ My first construction was ill-posed, and its own control caught it

I ranked comparators by **mean A2** and required the arm to beat *"the q-th percentile comparator"*.
q=100 then failed to reproduce R1034 — **correctly**, because R1025 established the **point-estimate
ordering is comparator-invariant** and only the **interval** differs. **Mean A2 does not order
comparators by who defeats an arm.** The well-posed bound is **arm-relative**: beat **≥ q%** of the
family, and q=100 is then exactly R1034's "beats every member".

## Controls

- **POSITIVE** — `{generic, genericpool16}` reproduces R1000's **9**: **PASS**.
- **PLACEBO** — a one-comparator family is quantile-invariant: **PASS**.
- **NEGATIVE** — the sweep must move the answer: q=0 → 73, q=100 → unstable: **PASS**.
- **SEEDS** — **7**, including R1034's own three, so the disagreement is measured rather than
  arbitrated.

## What this cannot say

Whether a quantile bound is the **right** clause. Construct validity needs an external criterion this
release does not carry. This asks only whether a stable non-empty regime **exists**.

`run.py` · `results/quantile_bound_curve.json`
