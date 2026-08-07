# R1050 — did six rounds of instrument audit reach the object? ⛔ **Yes. All 16 unattributable facts are cited in the clause region at `0.917` vs a permutation floor of `[0.490, 0.524]`, and the clause is downgraded to unverified-provenance.**

**The decision this round makes safe:** whether R1044–R1049 were cost recovery or production. **They
were production** — the definition rests disproportionately on the facts the currency gate cannot
attribute.

## ⛔ The positive control found something larger than it was checking

Anchoring on the **first** occurrence of `resolvably beats` put the window **~47,000 characters** from
R1037/R1038 — the rounds that wrote the clause's stated form — and the control **failed, correctly**.

⭐ **The phrase occurs 9 times in DEFINITION.md.** The canonical clause **is not locatable by its own
text**. That is R1049's multi-home defect one level up — in the **statement**, not in a gate's pattern
— and it makes **anchor choice a specification axis**, swept over all 9.

## Result — World A, and it clears its own floor

| | |
|---|---:|
| flagged by R1049 | **16** |
| arc round directories | **109** |
| cells (9 anchors × 4 windows) | **36** |
| informative (arc citation density < 0.5) | **36** |
| cells citing ≥1 flagged round | **33** — rate **0.917** |
| **permutation floor**, 3 seeds: a *random* set of 16 arc rounds | **[0.490, 0.524]** |

⭐ **0.917 is nearly double the floor.** A random 16 hits about half these windows, so a non-empty
intersection is *not* forced by breadth. The flagged facts are **disproportionately the ones the
definition cites**.

**All 16 appear**: `R920 R921 R922 R925 R926 R975 R978 R986 R989 R1000 R1001 R1005 R1012 R1027 R1036
R1045`.

## What "downgraded" means, exactly

⭐ **Unverified-provenance, never overturned.** The currency gate cannot show the statement carries
these facts. **It does not follow that the numbers are wrong** — each flagged round's `run.py`
re-derives its value directly.

## Controls

- **POSITIVE** — a round known to have written the clause (`R1037`/`R1038`) must appear in some
  (anchor, window) cell: **True** — *after* the anchor became a swept axis; **False** on one anchor,
  which is what exposed the 9 homes.
- **NEGATIVE** — a non-existent round id appears in no cell: **True**.
- **PLACEBO** — every zero-width window cites nothing, not everything: **True**.
- ⭐ **PERMUTATION FLOOR** — the control missed in six consecutive rounds, and the one that decides
  this verdict. Permuting *which* rounds are flagged, same count, drawn from the arc: **[0.490,
  0.524]** vs observed **0.917**.
- **DENSITY GUARD** — a window citing ≥50% of the arc is excluded as uninformative before the branch;
  **0 of 36 were**.
- **MULTIPLICITY** — all 36 cells computed; all 9 anchors and 4 window sizes reported.

## IMPOSSIBLE here

- **whether a clause is WRONG because a fact under it is unattributable** — unattributable is a claim
  about the gate, not the number. **SETTLES: IN-RELEASE** — re-running each flagged round's `run.py`
  re-derives its value, one run per round; unattempted, not unavailable.

`run.py` · `results/audit_reached_the_object.json`
