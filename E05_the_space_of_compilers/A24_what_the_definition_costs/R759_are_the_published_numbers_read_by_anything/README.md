# R759 · the arc is WRITE-ONLY — 13.6% of its numbers are read by anything, so the sub-arc closes

**Of the **110 distinctive numbers** R748–R756 published, **15 (13.6%)** appear in any strictly later
round. The recomputation debt R757 and R758 named is **near zero**, and the honest output is to
**close the provenance sub-arc** rather than pay it. ⭐ And the four most-read values are all R753's
`0.8000 / 0.3814 / 0.1793 / 0.6207` — **the numbers that got read are the numbers that were
retracted.****

## check #361 — the design was built to be able to return the unwelcome answer

§0.2: *do not let the ledger become the product.* If this arc's figures are read by nothing, sixteen
rounds of provenance work have been accumulating numbers nothing consumes. **World B was the
uncomfortable branch and it is the one that fired.**

| class | era | n | **read by a later round** | in a deliverable |
|---|---|---|---|---|
| **distinctive** | **R748–R756** | **110** | **0.1364** | 1.0000 |
| NON-distinctive *(SHAM)* | R748–R756 | 65 | **0.6154** | 1.0000 |
| distinctive | R700–R747 | 174 | **0.1954** | — |

⛔ **"In a deliverable" is NEAR-FORCED** — every round appends its own numbers to `DEFINITION.md`.
Printed, and **excluded from the verdict**.
⛔ **A number published in round N can only be read by rounds > N**, so decline toward the present is
partly mechanical. **That is why the older era was measured**: with eight more rounds of exposure it
reaches only **0.1954**.

## ⭐ the SHAM prices the instrument's known flaw directly

Non-distinctive values (< 4 dp) are "read" at **0.6154** against the distinctive **0.1364** —
**4.51× inflation**. That is the spurious-match effect R756 and R757 established, measured on this
corpus rather than assumed. **Restricting to distinctive values is what makes 13.6% a measurement.**

## ⚠ the confound bounds the reading, and it was written before the run

| | later rounds citing the round's **ID** | later rounds reading one of its **values** |
|---|---|---|
| **total, R748–R756** | **30** | **9** |

**Round IDs are cited 3.3× more often than values are reprinted.** A later round can act on a finding
while restating it in words, so the value-trace **under-counts influence by roughly 3×**. `13.6%`
measures *numbers reprinted*, not *findings used* — and the report says so rather than converting one
into the other.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `0.8000` (published R753) read by **[754, 756, 757, 758]**. Band computed: floor **0** (a tracer finding nothing), ceiling **6** (the later rounds that exist); threshold 2 strictly inside |
| **g=0** | fabricated `0.847362` read by **0** rounds |
| **NEGATIVE** | publishing round shuffled ×5 → shares `[0.4818, 0.4909, 0.4909, 0.4455, 0.4636]` vs real **0.1364**. Readership depends on the publishing round's **position**, not on the value alone |
| **SHAM** | as above, **4.51×** |
| **PLACEBO** | the same trace twice → 0 differing, 0 of 110 |

⛔ **g=0 failed on its first run, and the cause was self-contamination.** The tracer scanned every
round's `run.py` **including this one**, where the fabricated constant is written as a literal — so it
detected its own test value, and POSITIVE was inflated by counting R759 as a reader of itself. **The
instrument was part of its own corpus** *(ledger 1049)*. Repaired by excluding the current round.

⛔ **And the two-seed reproducibility check caught a real non-determinism.** `published()` returns a
**set**; string-set iteration order is hash-seed dependent, so the *first-publisher-wins* tie-break
resolved differently under seeds 0 and 31415 and the artifacts were **not** byte-identical. **A
different value could win a tie and carry a different reader set** — not cosmetic *(ledger 1050)*.
Repaired by sorting.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| **P1** read share, distinctive | 0.15, band [0.00, 0.60] | **0.1364** | ✓ near-exact |
| P2 deliverable share | ⚠ **near-forced, no band, not scored** | 1.0000 | reported |
| P3 SHAM, non-distinctive | 0.70, band [0.30, 1.00] | **0.6154** | ✓ |
| P4 older-era base rate | 0.25, band [0.00, 0.80] | **0.1954** | ✓ |
| P5 read by ≥2 later rounds | 8, band [0, 120] | **4** | in band, point 2× wrong |
| D read share rises with age | true | **true** (0.1954 > 0.1364) | ✓ |

## ⭐ what the read numbers actually are

| value | published | readers |
|---|---|---|
| `0.8000` | R753 | 754, 756, 757, 758 |
| `0.3814` | R753 | 754, 756, 757, 758 |
| `0.1793` | R753 | 754, 756, 757, 758 |
| `0.6207` | R753 | 754, 756, 757 |

**All four are R753's, and all four were subsequently corrected or re-attributed.** The numbers this
arc actually reused are the ones that turned out to be wrong — which is what a working retraction
chain looks like, and it is the arc's clearest positive result.

## the sentence I can no longer write

*"the recomputation debt from R748–R756 must be paid."* 15 of 110 numbers have any downstream reader,
and the four with the most readers are already corrected on the page.

## NEXT

**The provenance sub-arc closes here.** What stands from it is three instrument findings that outlive
their numbers: an artifact lookup scoped to one arc of ten *(R757)*, a population that must be pinned
to the **parent** commit because a round edits the document it measured *(R758)*, and a value-trace
whose spurious-match rate is **4.51×** on non-distinctive values *(this round)*. Those are reusable;
the rates they produced are not, and 13.6% is why. **The next gradient is back on the object** — the
definition is `② ∧ ③` with a 5-member extension, and the last substantive question left open about it
is R746's: whether the 7 target-reading tags admitted by the census are 7 objects or fewer, which
R730's satisfaction-vector partition can answer on today's population and which no round since has
run.
