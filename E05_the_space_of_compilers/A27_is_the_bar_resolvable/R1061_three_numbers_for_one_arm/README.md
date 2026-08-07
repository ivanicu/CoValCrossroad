# R1061 — three numbers for one arm, reconciled exactly. ⛔ **R1060 compared against the wrong object; its bound binds ~5× harder than it reported.**

**The decision this round makes safe:** whether R1059's and R1060's scales can be quoted against each
other. **They can now** — every number is placed in a 2×2, and one committed comparison is retracted.

## The 2×2 — every committed number lands in exactly one cell

| source | aggregation | value | |
|---|---|---:|---|
| **read `sat_generic.npz`** | per-annotator | **0.5514** | ✓ **R1059's committed number** |
| **read `sat_generic.npz`** | consensus | **0.6632** | ⭐ **the cell nobody computed** |
| reconstructed `sat_full[0:4]` | per-annotator | **0.5023** | ✓ R1060's 3-line reimplementation |
| reconstructed `sat_full[0:4]` | consensus | **0.5880** | ✓ **R1060's committed number** |

**All three published values reproduce to 4 decimals.** The discrepancy is fully explained, and it is
**not** aggregation alone: it is **two causes at once**, source and aggregation, which is why no single
hypothesis fitted it.

## ⛔⛔ World B — R1060's comparator was not the comparator

R1060 **reconstructed** `generic` as `sat_full` restricted to criteria `[0,1,2,3]`. R1059 **read**
`sat_generic.npz`. The two disagree on **764 of 968 prompts**.

⭐ **Under R1060's own consensus aggregation the true comparator scores `0.6632`, not `0.5880`.** So
R1060's margins — best held-out ≈ 0.58 against a stated 0.589, shortfall ~0.015 — are measured against
an arm that is not the comparator. **Against the real one the shortfall is ≈ 0.08.**

**R1060's numbers are retracted; its conclusion survives and hardens.** The bound still binds — it
binds **about five times harder** than reported.

## Controls

- **POSITIVE** — both committed numbers **read from artifacts**, never remembered. A reconciliation
  against a remembered figure reconciles nothing.
- **NEGATIVE** — the two sources must be shown to **differ**, or the object hypothesis is untestable
  and must be dropped rather than assumed: they differ on **764 of 968** prompts.
- **PLACEBO** — a cell against itself is exactly 0.
- **MULTIPLICITY** — all four cells reported, not only the ones that match.
- **NOISE FLOOR** — N/A: deterministic means over a fixed prompt set. Stated, not omitted.

## ⭐ What this says about the third number

R1060's `0.5023` was a **three-line guess at another round's code**. It lands in a real cell — but as
*"the reconstructed object under the read object's aggregation"*, a combination **neither round
intended**. It was never a measurement of anything. **R1060 was right to refuse to reason from it, and
that refusal is the only reason this round exists rather than a silently-wrong cross-round gap.**

## IMPOSSIBLE here

- **which aggregation the CLAUSE should use** — a definitional question this round does not touch.
  **SETTLES: IN-RELEASE** via the admission operator, which is what the clause actually uses and
  which takes neither of these means as input.

`run.py` · `results/reconciliation.json`
