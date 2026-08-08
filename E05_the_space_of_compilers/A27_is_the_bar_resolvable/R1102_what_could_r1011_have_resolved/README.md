# R1102 — R1011's five nulls are **silence**. Its MDE is **0.008–0.010** and its unresolved effects are **0.0023–0.0033**, a factor of **2.4** under the resolution.

**The decision this round makes safe:** whether the arc's deepest claim — *the definition contains the
released core without singling it out* — is a statement about the **arms** or about the **instrument**.
**The instrument.** R1011 reported no MDE and declared a noise floor of width **0.000000**; measured,
its design could not have seen an effect a quarter the size of what it was looking for.

## ⛔ Two refusals before the round began, and both are mine

**① R1101's NEXT was prior art.** It proposed scoring `coval_core` against `topw_k3/k4/k6/k8` as a
comparator family. **R1011 ran exactly that 91 rounds ago**, at full coverage, 8,000 draws.
**② The same sentence contained a second error.** It called those arms *"the rating-blind selectors"*
— and R1101's own measurement, one paragraph above it, is that **`topw` ranks by human ratings.**

**One closing sentence, two errors, both checkable against the round that wrote it.** Second
consecutive round in which the NEXT line was the defect; the P4 prior-art gate is what caught it.

## ⛔ And the derivation I led with was WRONG, in the flattering direction

R1011's committed table resolves `topw_k8` at Δ=+0.0072 and fails at `topw_k3`'s Δ=+0.0033. **I
derived MDE ∈ (0.0033, 0.0072] from that, and concluded the design was not blind.**

**It rests on `a resolved cell lies above the MDE`. That is false.** The MDE is an **80%-power**
threshold; a single study can cross zero at lower power. **`topw_k8` crossed at Δ=+0.0072 against its
own measured MDE of 0.010** — a lucky cell, not a demonstration of resolution. The derivation credited
the design with resolution it does not have, and the measurement overturned it.

## ⭐ The measurement

**Method:** R1011's estimator, unchanged. The real per-prompt A2 difference vector, mean-removed, is
the noise template; a constant dose `g` is added; **300 resampled studies** each get R1011's own inner
bootstrap; retention = the share whose 2.5th percentile clears zero. MDE = smallest `g` at retention
≥ 0.80. Three seeds.

| rival | Δ observed | resolvable in R1011 | **MDE measured** | analytic 2.8·SE | retention at g=0 | upper bound |
|---|---:|---|---:|---:|---:|---:|
| `topw_k3` | +0.0033 | no | **0.010** | 0.0090 | 0.013 | < +0.0095 |
| `topw_k4` | +0.0023 | no | **0.010** | 0.0085 | 0.028 | < +0.0084 |
| `topw_k4_detA` | +0.0023 | no | **0.010** | 0.0085 | 0.028 | < +0.0084 |
| `topw_k4_detB` | +0.0023 | no | **0.010** | 0.0085 | 0.028 | < +0.0084 |
| `topw_k6` | +0.0024 | no | **0.008** | 0.0079 | 0.024 | < +0.0079 |
| `topw_k8` | +0.0072 | **core better** | **0.010** | 0.0085 | 0.022 | < +0.0130 |

⭐ **The five unresolved effects are 0.0023–0.0033 against an MDE of 0.008–0.010 — a factor of 2.4
under the resolution.** A null at a quarter of the design's resolution is **silence**, and R1011
published it as a finding about the definition.

⚠ **And the one "resolved" row is underpowered too.** `topw_k8` at +0.0072 sits below its own MDE of
0.010, so its crossing is a cell at under 80% power. It is not retracted — a crossing is a crossing —
but it cannot bear the weight R1011's world-selection put on it.

## The downgrade

| | |
|---|---|
| **R1011's claim** | *the definition contains the released core without singling it out* |
| **Status** | **DOWNGRADED** — its five nulls are silence, not measurements |
| **What the data support** | an **inequality**: the core's A2 advantage over each unresolved admitted rival is **bounded above by +0.0079 to +0.0095** |
| **What still stands** | R1011's positive control, its sham, its coverage finding (the twins at 200/968 with 79% imputed A2), and that the definition **contains** the core. Only the **ranking** claim loses its footing. |

**The shape of the error is the §4 row read forwards:** *"I replaced a 6×-inflated number with a
number, when what the design supported was an inequality."* Here R1011 replaced an inequality with a
**qualitative null**, which is the same substitution with the sign of the ambition reversed.

## Controls — 7, all green

| control | result |
|---|---|
| **g=0** a zero-effect template does **not** resolve (retention ≤ 0.10) — measured 0.013–0.028 | PASS |
| POSITIVE at R1011's own core-vs-random effect (+0.0738) the curve saturates at **1.000** | PASS |
| GAUGE prompt order moves retention no further than Monte-Carlo error | PASS |
| SHAM removing per-prompt heterogeneity collapses the MDE to the grid floor | PASS |
| PLACEBO an all-zero template at g=0 returns retention **exactly 0** | PASS |
| SEEDS the seed flag changes the resampling draws | PASS |
| DERIVATION the analytic **2.8·SE** agrees with the measured MDE within one grid step | PASS |

⚠ **The gauge control was rebuilt before it ran.** Its first form demanded *bit-identical* retention
under a permutation of the difference vector — but permuting the data while reusing the same index
draws produces a **different sample**, so exact equality was never the right expectation and the
control would have failed for its own reasons. It now compares against **3× the Monte-Carlo standard
error of 300 draws**, computed rather than eyeballed.

⛔ **And the verdict string was built wrong and caught by its own output.** The first version printed
*"R1011's DESIGN WAS NOT BLIND"* while the branch beside it had computed `in_bracket = False` — the
headline asserting what the control two lines above denied. **Fourth instance of §4's *the verdict
string is not a computation* in this project, and I built it again.** Every comparative in the current
string is computed from the payload.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| whether the core **should** beat these arms | **N/A** | an external criterion. A2 is agreement with this release's annotators; R1011's own caveat stands unchanged |
| an MDE for the twin pair `detA`/`detB` | **N/A** | its difference vector is identically zero, so the design is degenerate there **by construction** — that is R1011's defect, not a gap in this round |
| resolving a +0.0023 effect at this n | **N/A** | ≈ 8× the prompts, since MDE scales as 1/√n — and the release ships 968 |
| cross-release | **N/A** | a second release |

`run.py` · `results/what_r1011_could_resolve.json`
