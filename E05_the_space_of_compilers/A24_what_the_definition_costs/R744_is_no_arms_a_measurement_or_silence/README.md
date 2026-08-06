# R744 · is `NO_ARMS` a measurement or silence? — an attack on the round committed before it

**`NO_ARMS` is SILENCE. Of the 6 cited rounds R743 reported as loading no arm artifact, **5 reach the
arm store** through a cache file they name that was written by a store-reading round; only `R558` does
not. The 6 is an **upper bound on a FILE-level property**, and R743 published it as a ROUND-level
count. ⛔ And my registered mechanism was wrong: **0** of the gain comes from imports — it is entirely
cache edges.**

## check #346 — it holds, and P4 then killed the round it proposed

✓ R728's README says verbatim *"Every round from R680 to R727 read R294's persisted summary."*

⛔ **But R743's NEXT — enumerate the data paths each source opens — is R650, already built.** R650
measured *"172 of 364 file-read sites (47.3%) state their own read population statically"* and
concluded **the question as posed is undecidable**. Running it again would have been R729's failure a
second time. **P4 first is the only reason this round is not that.**

## what P4 found instead: a defect in the round pushed ten minutes earlier

R743's `NO_ARMS` comes from a **regex over each round's own file**. Its positive control validated the
`DERIVED`-vs-`TYPED` split **among rounds that already pass that gate** — it never asked whether the
gate can MISS. P5's ★ rule: a measured `not found` is inadmissible until the instrument has passed a
positive control **in the direction of absence**. 163 A24 `run.py` files touch `sys.path`, so
indirection is not hypothetical.

## the grid — 4 levels × 3 populations, all twelve cells

| level | NO_ARMS(6) | all cited(16) | complement(404) |
|---|---|---|---|
| **L0** own file only *(= R743's detector)* | **0/6** | 10/16 | 142/404 |
| **L1** + locally imported modules | **0/6** | 10/16 | 145/404 |
| **L2 tight** + caches naming their round dir | **5/6** | 15/16 | 165/404 |
| ⛔ L2 loose *(uncontrolled, kept for contrast)* | 6/6 | 16/16 | 259/404 |

⛔ **`L0 ≤ L1 ≤ L2` is FORCED** — each level is a superset. **A DERIVATION, not evidence.** Only the
size of the gain is measured.

## per round, with the files each level examined

| round | L0 | L1 | L2 tight | L2 loose | files examined |
|---|---|---|---|---|---|
| R519 | ✗ | ✗ | **✓** | ✓ | 1 / 1 / 2 / **156** |
| R520 | ✗ | ✗ | **✓** | ✓ | 1 / 1 / 2 / **156** |
| R529 | ✗ | ✗ | **✓** | ✓ | 1 / 1 / 2 / 2 |
| R530 | ✗ | ✗ | **✓** | ✓ | 1 / 2 / 3 / 3 |
| R534 | ✗ | ✗ | **✓** | ✓ | 1 / 1 / 2 / 2 |
| **R558** | ✗ | ✗ | **✗** | ✓ | 1 / 1 / 1 / 2 |

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 reach at L1, of 6 | 2, band [0, 5] | **0** | in band, point wrong |
| P2 reach at L2 tight, of 6 | 3, band [0, 6] | **5** | in band, point wrong |
| P3 L0 reproduces R743 exactly | 16/16, hard requirement | **16/16** | ✓ |
| P4 cited rounds with an import edge | ≥ 5 | **8** | ✓ |
| **D** gainers all carry an import edge | true | **false** | ⛔ **the mechanism was wrong** |

⭐ **D failing is worth more than the bound.** I predicted indirection through **code**; the tree
shares data through **artifacts**. Imports contributed **0** to the gain across every cell.

## controls — 6 PASS, 0 FAIL, and ⛔ two of my own instruments were broken first

| control | returned |
|---|---|
| **POSITIVE** | R294's `sat_` literals moved into an imported constant → flat goes **blind** (`False`) while L1 still reaches. Band computed: floor = flat on untouched R294 = `True`, ceiling = L1 on refactored = `True`, and the refactor is **asserted to parse** |
| **g=0** | importing a helper with no store reference adds **no** reach — the detector counts data, not edges |
| **NEGATIVE** | import graph emptied → L2 equals L0 on **16/16**, exactly |
| **SHAM** | ingredient **absent**: L1 gain on the **8** import-free cited rounds = **0** |
| **PLACEBO** | L0 recomputed differs by exactly **0** |
| **P3** | L0 is R743's instrument, not a lookalike — 16/16 |

**① The positive control failed on its own construction.** v1 *deleted* the store-touching lines from
R294; the remainder did not **parse**, so the import resolver found nothing and the control condemned
the detector for my refactor's failure — §4's dominant mode, twice in one session. Repaired by
substituting the literals into an imported constant and **asserting the result parses** before the
control is allowed to mean anything *(ledger 997)*.

**② The L2 detector I built to attack a loose search was a loose search.** v1 matched any `.npz`/
`.json` literal **by basename** across every round directory: one shared basename resolved to **155**
directories and produced a **6/6** headline. Requiring the literal to name its round directory gives
**5/6**. Both columns are printed *(ledger 998)*.

## what this retracts in R743

| R743 said | stands as |
|---|---|
| *"11 of 16 never load an arm artifact"* | **6 name no arm artifact + 5 name one without a classifiable population** *(ledger 995)* |
| the 6 as a count | **an upper bound**; ≥5 of 6 reach the store *(ledger 996)* |
| `NO_ARMS` as a round property | **a file property**. Unit of instrument ≠ unit of claim |

⚠ **The bound is one-directional.** Static closure only ADDS reach, so **≥5 of 6** is what stands.
Non-reachability is not establishable here — it needs execution tracing, and even then a runtime path
is constructible.

⚠ **One self-reference artifact, reported not hidden.** This round's own `run.py` contains the literal
`"sat_` (it builds the positive control's helper), so it classifies as store-reaching and adds **+1**
to the complement column between the pre-repair and post-repair runs. It touches no cited-population
number.

## the sentence I can no longer write

*"six cited rounds never touch an arm artifact."* Five of them do, through a cache they name.

## NEXT

L0, L1 and L2 are static, and this round's impossibility register names **execution** as what beats a
static bound. `assurance/what_did_each_check_actually_read.py` already runs a CPython `sys.addaudithook`
over the assurance gates and records the repo files each process opens — the same hook pointed at a
round's `run.py` returns the files it *opens* rather than the files it *names*. The registered quantity
is the gap between named and opened, per round, across the 16. The design question to settle before
building: a round that writes into `results/` also touches files, and the hook sees writes as well as
reads, so the population has to separate the two or it measures authorship rather than dependence.
