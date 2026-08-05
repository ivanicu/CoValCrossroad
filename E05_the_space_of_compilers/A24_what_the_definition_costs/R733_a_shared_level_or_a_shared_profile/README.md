# R733 · a shared level or a shared profile

**Both admitted target-reading objects track the EXCLUDED object's per-prompt profile beyond the
shared-subtrahend floor, and more than they track the label-blind arms. The clause's omissions are
not merely the same SIZE as what it excludes — they move with it prompt by prompt.**

## ⭐ P4 supplied the precondition and the principle
- **R457 (W-STRUCTURED)** — the per-prompt gap is reliable: split-half ρ_full **0.8311**, shuffled
  null **0.0168**. Without this the whole round would be correlating noise.
- **R284** — established that a **shared subtrahend inflates `r` with no shared mechanism**, so a raw
  correlation is uninterpretable. ⚠ **But its floor of 0.53 is over `generic` (R284:24), a different
  baseline.** Reproducing its *number* was a mis-specified positive control; its *principle* is what
  transfers.

## The floor, computed in this round's own units
| floor pair (shared subtrahend, no shared mechanism) | r |
|---|---|
| `random_k4_s1` ‖ `random_k4_s2` | 0.4686 |
| `random_k4_s1` ‖ `random_k8_s0` | 0.5206 |
| `random_k4_s2` ‖ `random_k8_s0` | 0.5211 |
| **FLOOR** | **0.5034** |
| **CEILING** — `topw_k4` ‖ `topw_k4_detA`, one object under two tags *(R730)* | **1.000000** |

## The result — excess over the floor, Pearson, both clauses
| object | to the **EXCLUDED** object | to the **BLIND** arms | nearest |
|---|---|---|---|
| `greedy` | **+0.4632** | +0.1592 | **EXCLUDED** |
| `indep` | **+0.3965** | +0.1966 | **EXCLUDED** |

**Clause ① and clause ② agree on the ordering.** BH over all **48** cells: **48 survive** at q=0.05.

⚠ **This excludes unrelatedness. It does not identify a mechanism.** Correlation of outcomes cannot,
and the intervention that could is in the impossibility register.

⚠ **The disattenuation column exceeds 1 and must not be read as a correlation.** `greedy` vs the
excluded object is raw **0.9747** against an attenuation ceiling of **0.8311**. A raw `r` above
`√(rel·rel)` means R457's reliability — measured on a different arm and quantity — does not transfer
here, or the shared subtrahend inflates past it. **Either way the disattenuated number is not a
correlation and is reported as a diagnostic only.**

## ⛔ Three of my own instruments failed first
1. **I borrowed a floor from a different quantity.** `random_k4_s0` *is* the clause-① subtrahend, so
   its own margin is identically zero and its correlation is undefined — the control returned `nan`
   and the floor with it. R284's pairs are over `generic`. **Fixed by computing the band in this
   round's units, with a ceiling from an object correlated with itself under two tags.**
2. **The SHAM asserted a false monotonicity.** v1 claimed a shared addend *can only raise* `r`. It
   cannot: a common term raises the covariance *and* both variances, so the direction is not fixed.
   Measured, removing the subtraction *lowered* it (0.9690 vs 0.9747). **The control now reports the
   quantity instead of asserting its direction.**
3. ⛔⛔ **My reproducibility check printed PASS on files a crashed run never wrote.** The artifact
   write was failing on a numpy-2 bool (whose class is literally named `bool`, so `json`'s own check
   misses it), and the two-hash-seed comparison happily compared two stale copies. **That is
   "determinism read as currency" in its purest form** — a gate certifying that two files it did not
   produce are identical. **Fixed by requiring each run to have written before the comparison runs.**

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: band computed, `FLOOR 0.5034 < signal ≤ CEILING 1.0000` · **g=0**: self-correlation
exactly 1.0 · **NEGATIVE**: prompt order shuffled → |r| 0.0046 / 0.0262 / 0.0030 against R457's
0.0168, excluding *"the correlation is a property of the marginals"* · **SHAM**: subtraction removed
→ 0.9690, reported not asserted · **PLACEBO**: 1.0.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A floor pairs measured | 3 [0, 3] | **3** | yes |
| B `greedy` vs excluded, ① | 0.70 [−1, 1] | **0.9747** | yes |
| C admitted vs blind, ① | 0.55 [−1, 1] | **0.7608** | yes |
| D excess larger toward excluded | 2 [0, 2] | **2** | yes |
| DIRECTIONAL clauses agree | — | **holds** | — |

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, **with both runs verified to
have written**.
**Artifact:** `results/r733_profile_or_level.json` · all 48 cells with permutation p and BH rank.
