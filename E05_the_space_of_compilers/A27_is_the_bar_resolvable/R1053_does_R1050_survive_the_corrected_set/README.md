# R1053 — R1050 used the wrong set. ⭐ **The direction survives (`0.917` vs floor `[0.719, 0.750]`) — but the statistic is at its CEILING, so the magnitude does not.**

**The decision this round makes safe:** whether R1050's downgrade of the clause stands after R1052
corrected the flagged set from 21 to 45. **It stands, and only as a direction.**

## The recomputation

| predicate | n flagged | observed | permutation floor (3 seeds) | separable |
|---|---:|---:|---|---|
| **`any` — corrected** | **45** | **0.917** | **[0.719, 0.750]** | **True** |
| `all` — R1049's, wrong | 21 | 0.917 | [0.557, 0.608] | True |
| R1050 as published | 16 | 0.917 | [0.490, 0.524] | True |

⭐ **The floor had to be recomputed at the new size.** Comparing a 45-round observation against
R1050's 16-round null would be a null priced at the wrong level, which is the error this round exists
to fix. The floor rose from ~0.51 to ~0.75; the observation did not move.

## ⛔ And the observation did not move because it is at the CEILING

| | |
|---|---:|
| **ceiling** — every arc round in the set | **0.917** |
| **floor at g=0** — empty set | **0.000** |
| observation (corrected set) | **0.917 — AT the ceiling** |

⭐ **Both predicates returned exactly `0.917` on sets of size 45 and 21. That identity was the tell.**
Three of the 36 cells cite so little that **no set can reach them**, so 0.917 is the maximum the
design can return. §4's *control that cannot PASS*, in its `floor == ceiling` form applied to the
observation: **a saturated statistic supports a direction and never a magnitude.**

## ⛔⛔ And saturation is carried by 11 rounds, of which only 5 are flagged

The smallest set reaching the ceiling: `R1000 R1005 R924 R1004 R923 R1026 R1009 R1010 R1034 R1036
R1037` — **11 rounds**. Flagged under the corrected predicate: **5 of 11** (`R1000 R1005 R1009 R1010
R1036`).

⭐ **So the corrected set's saturation is not carried by flagged work specifically** — 6 of the 11
load-bearing rounds are *not* flagged. What the design licenses: **the flagged set contains enough
clause-proximate rounds to saturate, and a random set of the same size usually does not.** It does
**not** license *"the clause depends on unattributable work"* at any stated strength.

## Verdict

**World A, heavily qualified.** R1050's downgrade **stands as a direction** — the clause region cites
flagged work more than chance — but **R1050's `0.917` should never have been read as an effect size**,
and cannot be now.

## Controls

- **POSITIVE** — a round known to have written the clause appears in some cell: **True**.
- **NEGATIVE** — a non-existent round id appears in none: **True**.
- **PLACEBO** — a zero-width window cites nothing: **True**.
- **g=0** — the empty flagged set returns **0.000**, so the statistic is not satisfied before anything
  is planted.
- **CEILING** — measured, **0.917**, and the observation sits on it.
- **NOISE FLOOR** — recomputed **at each set size**, 3 seeds.
- **MULTIPLICITY** — both predicates and R1050's published cell reported side by side; 2 registry
  patterns remain statically unreadable and are reported, never dropped.

## IMPOSSIBLE here

- **whether citation near the clause means the clause DEPENDS on that round** — proximity in a
  document is not a dependency graph. **SETTLES: IN-RELEASE** — the clause's own text names what it
  rests on, at one careful reading; unattempted, not unavailable.

`run.py` · `results/recomputed_dependence.json`
