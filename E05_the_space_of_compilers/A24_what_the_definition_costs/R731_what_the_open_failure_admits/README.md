# R731 · what the open failure admits

**SPLIT, and the split is the finding: the rule name does not determine the behaviour.**

## ⭐ Prior art, named before the estimand — P4 was run first and found four overlapping rounds
- **R520** found the provenance literal misses label-readers.
- **R521** priced the hazard on the 56-arm population: 6 disagreements, all above the ② bar.
- **R522** computed those six arms' clause-② contrasts with CI, MDE, verdict — all **BEATS**.
- **R523** established the aliasing. **R525 produced the SAME EIGHT object classes R730 reports.**

⛔ **R730 credited only R523 for its partition. That partition is R525's**, on a wider population —
R730 differs on exactly two classes, both explained by the wider population (it merges `coval_core`
with its two 2b variants, and folds `provenance_probe` into the generic class). **Corrected here and
in the record.**

## Object-level margins — every object counted once
| object | group | clause ① | clause ② | ②/mde |
|---|---|---|---|---|
| `greedy` | **admitted, target-reading** | 0.129959 | **0.072210** | 6.85 |
| `indep` | **admitted, target-reading** | 0.110428 | **0.052679** | 5.06 |
| `oracle08bR` | **admitted, target-reading** | 0.072232 | **0.014483** | **1.04** |
| `oracle` | ⛔ **excluded**, target-reading | 0.135616 | **0.077867** | 7.29 |
| `topw_k3/k4/k6/k8` | label-blind | 0.066–0.071 | 0.0137–0.0208 | 1.26–1.95 |
| `coval_core` | the released core | 0.073790 | 0.016042 | 1.51 |

## Distance in within-topw spreads — because "sits with" has no absolute meaning
| object | clause | to oracle | to topw | nearest |
|---|---|---|---|---|
| `greedy` | ① / ② | 2.46 / 1.81 | 26.03 / 17.71 | **ORACLE** |
| `indep` | ① / ② | 10.94 / 8.07 | 17.55 / 11.45 | **ORACLE** |
| `oracle08bR` | ① / ② | 27.52 / 20.30 | 0.96 / 0.78 | **topw** |

⭐ **The DIRECTIONAL held: clause ① and clause ② agree on the nearest group for every object.** The
split is not disagreement between clauses.

## What this kills — including my own proposed remedy
- **`greedy` and `indep` carry the excluded object's size.** ③'s omissions are not harmless; a
  longer list would not fix a clause that has no predicate.
- ⛔ **But `oracle_k4_08bR` is oracle-ruled by construction and behaves like a label-blind arm** —
  ②/mde **1.04**, barely clearing its own resolution, against `oracle_k4`'s **7.29**. **So a
  predicate over construction alone — which is exactly what R729's and R730's next-lines
  prescribed — would wrongly exclude it.** Construction and behaviour come apart.

⚠ **This is a comparison of OUTCOMES, not of mechanisms.** A margin near the oracle's does not
establish that the same construction produced it; that needs an intervention, and it is in the
impossibility register.

## ⚠ B and C are nearly equal, and that is why they are the wrong summary
Mean \|②gap\| to oracle **0.0314** vs to topw **0.0312** — indistinguishable, because `08bR` drags
the mean across. **The per-object table in spread units is the reportable form; the two means are
not.** Registered as points, reported as a caution against themselves.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: R522's six published clause-② effects reproduced **6/6 to 4 decimals**, band
`floor 0 < t 6 ≤ ceiling 6` · **g=0**: object against itself → gap exactly 0 · **NEGATIVE**:
permutation over all non-oracle objects — real separation ① **−0.002787** vs null median
**+0.036190** (p = 0.0377), ② **+0.000249** vs **+0.036407** (p = 0.0580), excluding *"any partition
shows this separation"* · **SHAM**: the same separation on `n`, which carries no clause information →
**+0.000000**, ingredient **absent** · **PLACEBO**: topw against topw at the within-group floor ·
**NOISE FLOOR**: within-topw spread ① 0.002303, ② 0.003122, measured.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A R522 reproduced | 6 [0, 6] | **6** | yes |
| B mean \|②gap\| to oracle | 0.02 [0, 1] | **0.0314** | yes |
| C mean \|②gap\| to topw | 0.04 [0, 1] | **0.0312** | yes |
| **D admitted closer to oracle** | **3 [0, 3]** | **2** | yes |
| DIRECTIONAL clauses agree | — | **holds** | — |

⭐ **D's point prediction was wrong and that is the round's content.** I predicted all three would
sit with the excluded object. Two do. The one that does not is named after the rule that should have
made it the most inflated of all.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r731_what_the_failure_admits.json`.
