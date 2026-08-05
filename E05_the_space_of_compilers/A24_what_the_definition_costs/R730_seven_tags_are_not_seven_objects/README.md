# R730 · seven tags are not seven objects

**This round corrects the one I committed immediately before it.** R729 reported that **7** admitted
arms are built by a target-reading rule and clause ③ excludes **none**. That count is over **tags**.
At exact satisfaction-vector identity they are **4 objects**, clause ③ **already excludes 1**, and it
admits **3**.

## ⭐ P4 found this, and P4 is what I skipped last round
R523 had already established — on a 56-tag universe — that `oracle_k4_oracle_kA/kB` are **exact
aliases of `oracle_k4`, which IS on the blocklist**, and that all three A/B pairs are internally
identical. R524 partitioned 56 tags into 46 objects. **Running the prior-art gate first is the only
reason this correction exists.**

## R729's seven tags, resolved
| object | ③ |
|---|---|
| `greedy_k4_greedy_kA` = `greedy_k4_greedy_kB` | ⭐ **admits** |
| `indep_k4_indep_kA` = `indep_k4_indep_kB` | ⭐ **admits** |
| `oracle_k4` = `oracle_k4_oracle_kA` = `oracle_k4_oracle_kB` | ⛔ **EXCLUDES** — it carries a blocklisted tag |
| `oracle_k4_08bR` | ⭐ **admits** |

**So the clause does not fail to exclude the oracle object. It fails to recognise two of its tags** —
a real defect, and a different and smaller one than either R520 or R729 stated.

## The partition on today's population
93 tags → **81 objects**, 8 multi-tag classes:
`[coval_core, _2bA, _2bB]` · `[generic, generic_reprov, provenance_probe]` ·
`[greedy_kA, greedy_kB]` · `[indep_kA, indep_kB]` ·
`[oracle_k4, oracle_kA, oracle_kB]` · `[random_k4_s0, _ctlS0]` · `[random_k4_s1, _ctlS1]` ·
`[topw_k4, topw_k4_detA, topw_k4_detB]`

⭐ **The partition is identical at every tolerance in `{0, 1e-12, 1e-9, 1e-6}`**, and the smallest
non-zero difference anywhere in the population is **4.762e-02**. **Exact equality is not a knife-edge
choice here** — a tolerance rule would have to exceed that gap to change anything.

⚠ **Computed but NOT registered:** R729's population-wide **13 tags** resolve to **10 objects**, of
which ③ excludes 1 and admits **9**. Reported because leaving a corrected number's sibling
uncorrected is how a half-fixed page drifts; labelled because it was not preregistered.

## ⛔ The unit error is mine, and it is the third in three rounds
- **R728**: the anchor demanded a denominator the design could not return (92 vs a ceiling of 41).
- **R729**: registered agreement at a **9-way rule** unit when the claim was **binary**.
- **R730**: counted **tags** when the claim is about **objects**.

⚠ **And note the direction.** This one **inflated a defect I was attributing to someone else's
definition** — the flattering direction, and the one I am least likely to audit unprompted.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: R523's five findings reproduced **5/5**, band `floor 0 < t 5 ≤ ceiling 5` — *an
identity instrument that cannot reproduce identities a prior round established licenses nothing about
new ones* · **g=0**: `topw_k4` vs `random_k4_s0` **not** identical (max\|Δ\| 0.6508) · **NEGATIVE**:
a **one-ulp** perturbation breaks identity (max\|Δ\| 1.110e-16), excluding *"the comparison is
insensitive to the values"* · **SHAM**: every arm against itself, the second object **absent** ·
**PLACEBO**: 0 new merges.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A distinct objects among the 7 tags | 4 [1, 7] | **4** | yes |
| B objects ③ excludes | 1 [0, 7] | **1** | yes |
| C target-reading objects ③ admits | 3 [0, 7] | **3** | yes |
| D R523's findings reproduced | 5 [0, 5] | **5** | yes |
| DIRECTIONAL tags strictly overstate objects | — | **holds** | — |

## Residue
Whether two **near**-identical objects should merge is a modelling choice, not a measurement. Exact
equality is used, as R523 used it, and the near-miss floor is reported so the choice is visible.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r730_object_partition.json`; `results/_satvecs.npz` caches the satisfaction
vectors.
