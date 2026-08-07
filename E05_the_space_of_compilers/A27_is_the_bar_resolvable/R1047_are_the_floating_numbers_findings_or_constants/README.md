# R1047 — before building R1046's gate, what would it fire on? ⛔ **A display-rounding blind spot: R1046's bracket falls from `[0.164, 0.272]` to `[0.057, 0.159]` and its verdict is withdrawn.**

**The decision this round makes safe:** whether to install the README anchoring gate R1046 proposed.
**Not as R1046 stated it** — the defect it measured was **122 parts instrument, 43 parts real**.

## ⛔ The instrument was blind to the dominant case, and its positive control could not see it

A README displays `0.507`; the artifact stores `0.5071…`. **Exact containment calls that unbacked.**
R1046's positive control drew its test value **from the artifact itself**, so it was exact by
construction — **§4's row verbatim**: *a control that shares the instrument's blind spot confirms the
instrument and licenses nothing.* Both of R1046's controls passed. Neither could ever have caught this.

The fix is precision-aware: a README number is backed if some artifact value **rounds to it at the
README's own displayed precision**.

| | exact test | rounding-aware |
|---|---:|---:|
| numbers in no artifact in the arc | **178** | **60** |
| — rescued by rounding alone | — | **122** |
| in the round's own `run.py` | 26 (0.146) | **17 (0.283)** |
| **residue — in neither artifact nor source** | 152 | **43** |

## ⛔ R1046 recomputed, because a retraction that carries no number leaves the wrong one in the record

| R1046 body cell | as committed | corrected |
|---|---:|---:|
| unbacked / total | 289 / 1064 | **166 / 1047** |
| share | **0.272** | **0.159** |
| bracket | **[0.164, 0.272]** | **[0.057, 0.159]** |

**R1046's World B required ≥ 0.25. It no longer clears it, and 0.159 is in neither pre-registered
band.** ⭐ **What survives is the specification curve, not the magnitude**: the h1 and body cells still
disagree, and **READMEs are still guarded by nothing**.

## Result — ⭐ **NEITHER BAND, and that is the honest answer**

In-source share **0.283** over **60** floating numbers; residue **43**. Pre-registered: ≥ 0.50 → the
gate is noise; ≤ 0.20 → build it. **Neither.** What splits it is whether a number shared by source and
README is a **constant** or a **coincidence** — which needs the **line**, not the value.

## Controls

- **POSITIVE** — a value drawn **at runtime** from each round's own `run.py` must read as in-source,
  all **23**: **True**.
- **NEGATIVE** — that value plus a large offset must read as **not** in-source everywhere: **True**.
- ⚠ **AND BOTH ARE INSUFFICIENT BY THE SAME MECHANISM THIS ROUND FOUND** — they draw exact values, so
  they cannot detect a precision mismatch. **They passed under the blind instrument too.** The defect
  was caught by reading the object: `grep` found `0.507` inside R1023's JSON that the checker had
  just called absent.
- **PLACEBO** — a round with no floating numbers contributes no denominator.
- **EMPTY POPULATION** — exit **2**, never 0, at both stages.

## What this round cannot say

Whether a number in **both** source and README is a design constant or a finding that coincides with
one. **43 is a lower bound** on genuinely floating numbers — the only count citation,
pre-registration, rounding or coincidence cannot explain away.

## IMPOSSIBLE here

- **separating constant from coincidence** — needs the **line** each number sits on, not its value.
  **SETTLES: IN-RELEASE** — one reading per number, 43 of them; unattempted, not unavailable.

`run.py` · `results/floating_or_constant.json`
