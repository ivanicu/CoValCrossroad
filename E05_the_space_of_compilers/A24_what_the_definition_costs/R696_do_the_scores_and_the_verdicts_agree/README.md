# R696 · do the scores and the verdicts agree? — **the agreement is FORCED**

**⛔⛔⛔ `R360/run.py` computes `clause2_admits` **from** `a2_vec` — **② IS an A2 threshold.** So
"②-admitted arms score above ②-rejected ones" is an **arithmetic consequence** wherever the a2 values
share R360's scoring run, and the corpus records nothing about which run any a2 came from. **All
three sources returned percentile 100.0 — the ceiling of the statistic — and that is exactly what a
threshold predicts.****

## THE SPECIFICATION CURVE (G3/G4 — every source, none pooled)

| source | n | admitted | mean rank | percentile | p | resolution floor |
|---|---|---|---|---|---|---|
| `R306:arm_a2` | 10 | 2 | 9.50 | **100.0%** | 0.0444 RESOLVED | 0.0222 |
| `R308:a2` | 11 | 2 | 10.50 | **100.0%** | 0.0364 RESOLVED | 0.0182 |
| `R495:a2` | 7 | 2 | 6.50 | **100.0%** | 0.0952 not resolved | **0.0476 — cannot reach 0.05** |

Registered **A 85 [40,100] → 100.0, INSIDE (+15)** · **B 1 of 3 → 2 of 3 (+1)** · **directional
HOLDS** · kill did not fire.

**Controls:** POSITIVE — top scorers labelled admitted → percentile **100**. NEGATIVE — bottom
scorers → **2**. **g=0** — random labellings average **57** — *the statistic returns both ends*.
PLACEBO — identical.

## ⛔ WHAT I NEARLY REPORTED, AND THE TELL I WALKED PAST
My first verdict read *"the corpus's a2 scores and R360's ② verdicts are consistent — a precondition
for every claim this arc built on that ledger, and it had never been checked."* **That is a
derivation dressed as a check.** ② is defined on A2. **The tell was in the output before the
interpretation: a percentile of exactly 100.0 in all three sources is the statistic's ceiling, and a
saturated statistic is the signature of a forced result.**

**So the reading is:** a **derivation** if the runs are shared, a **consistency check** if they are
not, and **the corpus cannot say which.** The numbers stand as computed and are **not** evidence that
the ledger was independently confirmed.

## ⚠ AND R495 COULD NOT HAVE RESOLVED
Its resolution floor is **p = 0.0476** with n=7, m=2 — **the minimum achievable p is above 0.05 at
two decimal places.** Reporting it as *"not resolved"* without the floor would imply the data
disagreed; the design simply cannot get there.

## ⛔ CHECK #298 · THIRD CLOSING LINE IN A ROW PROPOSING A POPULATION OF ~1
R695's NEXT asked *"which arm of a PAIR scores higher"* — and **R695 itself measured the assemblable
pair count at 1**. R685 proposed a derivation; R694 proposed data that does not exist; this proposed
a pairwise test with one pair. **Reframing it over arms is what made a round possible at all.**

## WHAT WOULD SEPARATE DERIVATION FROM CHECK
An a2 produced by a scoring run **recorded as distinct** from R360's. **R684 measured that 90 rounds
in this arc vary a judge and 9 record which** — so the corpus's inability to answer this is the same
defect, one layer down.

## NEXT
`R495:a2` has a resolution floor of 0.0476 with n=7 and m=2 (`results/scores_vs_verdicts.json`, field
`resolution_floor`). Compute that floor for every clause verdict this arc has reported as "not
resolved" against an exact null, and report how many had a floor above their own threshold. A
non-resolution from a design that could not reach the threshold is silence, and it has been read as
evidence at least once here.
