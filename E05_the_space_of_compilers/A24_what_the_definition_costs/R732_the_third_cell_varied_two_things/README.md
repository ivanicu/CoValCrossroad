# R732 · the third cell varied two things

**R731's third cell is withdrawn to UNVERIFIED.** It compared `oracle_k4_08bR` against `oracle_k4`
and the `topw` objects as though they were commensurable. **They are not: two factors differ at
once**, and no object on disk separates them.

## ⭐ P4 found this, and it found it in my own round
R731 closed by *proposing* that the margin collapse might be a judge change. **R424 had already
established it**: the `_08b` and `_08bR` families agree with each other and **both disagree with the
default emitter**. (R426 corrected R424's "not on disk" conclusion — a filter bug in R424's own
candidate loop — but the foreignness stands.) **So R731 put a foreign-emitter object in the same
column as default-emitter objects and read a number off the comparison — while writing a round about
units.**

## The two factors
| factor | measurement |
|---|---|
| ① **selection** | identical criteria on **0.0888** of 968 shared prompts |
| ② **emitter** | per-cell satisfaction agreement **0.0354** on 15488 shared cell keys; `_08b` is foreign to the default *(R424)* |

⭐ **The noise floor makes ① unambiguous:** across all **10** same-object tag pairs from R730's
partition, criteria identity is **1.0000 exactly**. So 0.0888 is a real difference, not rounding.

**Their margin gap is a sum of two effects and neither is identified from the gap alone.**

## The 2×2 does not exist
**0 arms** carry `oracle_k4_08bR`'s criteria under a default-emitter score. The cell that would
separate emitter from selection is not on disk.

## What this does and does not do
⛔ **R731's reading — *"construction does not determine behaviour"*, which I used to retract my own
earlier remedy — is NOT supported by that cell.** It is **not refuted either.** The cell cannot carry
it, and **UNVERIFIED is not an acquittal in either direction.** So the "③ needs a predicate over
construction" remedy returns to **untested**, not restored.

⭐ **What survives R731 untouched:** `greedy` and `indep` both sit with the excluded object on both
clauses, and **both are default-emitter arms** — that comparison mixes no instruments.

⭐ **What R731 got right for the wrong reason:** the **rule name is a poor proxy for construction**.
These two share the `oracle_k` rule and agree on **8.9%** of selections. **That is now measured
directly rather than inferred from a margin.**

## ⛔ A wrong instrument, reported rather than hidden
My first probe compared the two arms' **distinct satisfaction values** and returned 0.96 containment.
**That instrument cannot see an emitter difference** — the satisfaction alphabet is a small shared
set by construction. R424 measured **per-cell** agreement, which is 0.0354. *The alphabet is not the
text.*

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: `topw_k4` vs `topw_k4_detA` (proven the same object by R730) → **1.0000** on criteria
*and* cells, with the known-different pair at **0.0021** giving the band · **g=0**: self-comparison
1.0, known-different pair not 1.0 · **NEGATIVE**: criteria permuted across prompts → **0.0** on all
three seeds vs real 0.0888, excluding *"the comparison sees only how many criteria, not which"* ·
**SHAM**: prompt sets alone, criteria **removed** → **1.0000**, so the prompt sets are identical and
carry none of the signal · **PLACEBO**: 1.0.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A criteria identity | 0.09 [0, 1] | **0.0888** | yes |
| B factors differing | 2 [0, 3] | **2** | yes |
| C default-emitter twins | 0 [0, 93] | **0** | yes |
| DIRECTIONAL third cell UNVERIFIED | — | **holds** | — |

## Residue — the experiment that would settle it
**Score `oracle_k4_08bR`'s criteria with the default emitter.** That is a new measurement, not
derivable from any artifact here, and it is in the impossibility register for this site.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r732_confounded_cell.json`.
