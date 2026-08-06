# R761 · baseline-robustness is A2 rank, and one arm proves the published causation backwards

**Over the **full 1,820-reference class** and a **27-arm** population, an arm's ②-robustness inverts
against its mean A2 in **4 of 351 pairs** — against **131.3 [89, 174]** for a random ordering. ⭐ **All
four inversions are one arm**, `oracle_k4_08bR`: it **reads the target and is not robust**. R527
published *"the label-readers are baseline-robust **because** they read the answer"*; the arm that
separates the two says the causation runs through **A2**, not through reading.**

## check #363 — the proposed round was prior art in THREE places

R760's NEXT proposed sweeping the admitted set over ②'s reference class. **R527** swept 7 percentiles
× 16 arms, **R446** swept all 1,820 on 3 arms, **R353** swept 400 pool orderings. **Sixth rebuild the
gate has stopped in this arc** *(ledger 1057)*. What was open is R527's *sharp finding*, and two
things attack it that R527 could not have seen.

## ⭐ the population could not have contained the counterexamples

R527 drew its arms from R294's census. **Measured here before the run: none of R729's seven
target-reading tags is in that census, though all seven have `sat_*.npz` on disk.**

| | R527 | R761 |
|---|---|---|
| arms | 16 | **27** |
| target-reading arms visible | **4** | **11** |
| references | 7 percentiles | **all 1,820** |

**Seven of the eleven counterexamples were invisible to the round that concluded the target-readers
are the robust ones.** Not a defect of R527's reasoning — a defect of the census it drew from.

## ⛔ two results were forced, and one is asserted rather than assumed

**D1 — robustness is monotone in A2 up to the paired SE.** Admission is `mean(x−y) − z·se > 0`, so
with `se` constant `rob` would be a strictly increasing function of mean A2 and the **ordering would
be algebra**. *"The highest-scoring arms are the most baseline-robust"* is not a finding. **The
measurement is the inversion residual.**
**D2 — the full 1,820-wide bootstrap is exactly computable at marginal cost.** Under a shared index
matrix the bootstrap mean is linear, and `var(x−y)` needs one matrix product. **45,500 exact cells
cost what 1,845 marginals cost**, so the grid's size is not effort — and D2 is **asserted at four
probe cells against the direct computation**, not trusted.

## ⭐ the whole residual is ONE ARM

| inverting pair | ΔA2 | Δrob |
|---|---|---|
| `oracle_k4_08bR` vs `topw_k3` | +0.0017 | **−0.0302** |
| `oracle_k4_08bR` vs `topw_k4` | +0.0007 | **−0.0434** |
| `oracle_k4_08bR` vs `topw_k6` | +0.0008 | **−0.0462** |
| `topw_k4` vs `topw_k6` | +0.0001 | −0.0027 |

Three of four are `oracle_k4_08bR`; the fourth is a ΔA2 of **0.0001**, below any resolution this
design has. **`rob` carries essentially no information that mean A2 does not** — 4 of 351 against a
random-ordering **131.3**.

## ⭐⭐ and R527's ③ could not have detected its own finding

| ③ | Jaccard with { rob = 1.0 } | vs the sham band |
|---|---|---|
| **③name** *(R527's blocklist)* | **0.400** | **INSIDE [0.105, 0.500]** |
| random size-11 blocklist *(SHAM S2, 200 draws)* | 0.254 [0.105, 0.500] | — |
| **③rule** *(R760)* | **0.909** | **outside** |

**R527's identity, measured with the blocklist, is statistically indistinguishable from a random
blocklist of the same size.** The identity is real; **the instrument that found it had no resolution
to find it** *(ledger 1058)*. `③name` misses **six** robust arms — exactly the six of R729's seven
that R527's census could not see.

## ⭐ the one arm that separates the two stories — WORLD C

`③rule` excludes **11**; **10** of them have `rob = 1.0`. The exception:

| arm | A2 | rob | reads target | robust |
|---|---|---|---|---|
| `oracle_k4` | 0.6283 | **1.0000** | ✓ | ✓ |
| `oracle_k4_oracle_kA/kB` | 0.6283 | **1.0000** | ✓ | ✓ |
| **`oracle_k4_08bR`** | **0.5649** | **0.9401** | **✓** | **✗** |
| `coval_core` | 0.5665 | 0.9978 | ✗ | ✗ |

**A degraded oracle reads the target and is *less* baseline-robust than `coval_core`, which does
not.** Under *"robust because they read the answer"* this arm should be robust. Under *"reading the
answer raises A2, and A2 buys robustness"* it should not be, and it is not.

## G4 · the `rob = 1.0` cut is a specification, so the whole curve is reported

| t | \|robust\| | ③name J | ③rule J |
|---|---|---|---|
| **1.00** | 10 | 0.400 | **0.909** |
| 0.99 | 11 | 0.364 | 0.833 |
| 0.95 | 14 | 0.286 | 0.667 |
| 0.90 | 15 | 0.267 | 0.733 |
| 0.75 | 17 | 0.235 | 0.647 |

**Set equality holds at NO threshold** — World C is not a knife-edge. **③rule clears the sham's upper
bound (0.500) at all five; ③name clears it at none.** The *ordering* is specification-robust; the
*equality* never was.

## controls — 6 PASS, 0 FAIL, and one was repaired in flight

| control | returned |
|---|---|
| **PROVENANCE** | R294's stored `c2` reproduced **16/16 at 1e-6**; the round exits 2 otherwise |
| **POSITIVE** | R527's committed `coval_core_by_spec` reproduced **8/8 keys**. Band computed: admit-everything → 7/8, admit-nothing → 1/8; 8/8 unreachable from either end |
| **g=0** | planted null (reference + mean-zero noise) admitted **0.0050 of 200**. Band [0, ~0.50] |
| **NEGATIVE** | `coval_core` real **0.9978** vs 200 pairing-permutations **0.8422 [0.8242, 0.8599]** — outside. `oracle_k4` **1.0000 vs 1.0000** — its gap is too large for pairing to matter. Reads only as *did the pairing matter* |
| **SHAM S1/S2** | random ordering **131.3**; random size-11 blocklist Jaccard **0.254** |
| **PLACEBO** | all four `*_sham` arms **rob = 0.0000** |

⛔ **g=0 as REGISTERED was a control that cannot PASS.** It demanded the published reference be
admitted at **0 of 1,820** — but 1,819 of those cells compare it against *other* references, and a
reference at percentile 93.7 beats most of them by construction. **Measured: 1350/1820.** The
threshold was unreachable, so the control carried no information whichever way it came out — §4's
*control that cannot PASS*, **fifth instance, and the first written into a preregistration rather
than only into code** *(ledger 1059)*. Repaired to a **planted null**; and the exact self-cell is
now labelled a **DERIVATION** (`eff=0, sd=0 → lo=hi=0 → UNRESOLVED` by `verdict()`'s first branch),
asserted rather than reported as a measurement.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| *"the label-readers are baseline-robust **because** they read the answer"* *(R527)* | ⛔ **the causation is retracted.** `rob` inverts against A2 in 4/351 pairs; the one target-reading arm with ordinary A2 is **not** robust |
| *"the four arms admitted at every specification are exactly the four ③ excludes"* *(R527)* | **true of its population and undetectable by its instrument** — Jaccard 0.400, inside a random blocklist's band |
| *"the extension moves 4 → 8 across the class"* *(R527)* | **stands**, and is now stated over 1,820 references rather than 7 percentiles |

## the sentence I can no longer write

*"the label-readers are baseline-robust because they read the answer."* They are robust **because
they score highest**, and reading the answer is how they got there — `oracle_k4_08bR` reads it, scores
0.5649, and is less robust than `coval_core`.

## NEXT

`rob` is 98.9% a rank statistic of A2, so **the reference-class sweep is not an independent axis** —
it re-measures A2 ordering at 1,820× the cost, and three rounds (R353, R446, R527) have now spent
budget on it. What is NOT re-measurable that way is the single residual: `oracle_k4_08bR` is the sole
arm (computed by `run.py`, `E2_inverting_pairs`) whose robustness and score disagree — **4 of 351
inverting pairs, 3 of them this arm** — and **its A2 (0.5649) sits inside the committed
extension's range (0.5593–0.5665) while its rule marks it target-reading**. The registered quantity
is what makes that arm different from `oracle_k4` — same rule, same target access, **0.0634 less A2**
— because whatever costs a target-reader that much is the thing ③ is trying to name and ② cannot see.
