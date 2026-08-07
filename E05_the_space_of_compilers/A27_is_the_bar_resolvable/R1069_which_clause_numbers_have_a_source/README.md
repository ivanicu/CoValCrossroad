# R1069 — which clause numbers have a committed source? ⭐ **Decimals do (`0.789` vs floor `~0.15`). Integers are saturated (`1.000` vs floor `~0.94`) and their share says almost nothing.**

**The decision this round makes safe:** whether R1068's gate can be extended by a membership test.
**For the clause's decimal constants, yes. For its integers, no** — and a pooled number would have
hidden that completely.

## Result, per magnitude class — because a pooled floor lumps them

| class | tokens | sourceable | **its own floor** (3 seeds) | margin | readable? |
|---|---:|---:|---|---:|---|
| **decimals** | **38** | **0.789** | **[0.105, 0.184]** | **+0.605** | ⭐ **yes** |
| integers | 93 | 1.000 | **[0.935, 0.946]** | +0.054 | ⛔ **saturated** |
| *(pooled)* | 131 | 0.939 | [0.672, 0.710] | +0.229 | misleading |

⭐ **With 72,754 distinct values across 872 artifacts, nearly any small integer is "sourceable" by
coincidence.** The integer class clears its floor by 0.054 and its 100% carries almost no
information. **The decimal class — the measured quantities — separates by 0.605 and is the finding.**

## ⛔ Two counting corrections, both mine

1. **My first count was 144 where R1067 counted 121.** The 9 clause homes have **overlapping ±700
   windows**; appending per window counts a shared token once per window, while R1067 keyed by
   absolute offset. Deduplicating by offset is the fix.
2. ⚠ **It still reads 131, not 121, and that is not a bug**: the statement has **grown** between the
   two rounds — each round appends its annotation. **A population that changes between rounds means
   any cross-round count needs the document version attached**, which is exactly the class of error
   R1060/R1061 spent two rounds untangling.

## Controls

- **POSITIVE** — the three constants R1068 declared (`2`, `10`, `15`) must read as sourceable:
  **True**. A test that misses known-sourced values cannot count unknown ones.
- **NEGATIVE** — a constructed-absent value reads as unsourced: **True**.
- ⭐ **NOISE FLOOR, PER CLASS** — random values drawn **matched to each class's own magnitude
  distribution**, 3 seeds. This is the control that decides the round: pooled, the result reads as a
  clean `0.939 vs 0.69`; split, one class collapses.
- **PLACEBO** — an empty token list exits **2**, never 0.

## What no aggregate licenses

**No single token is settled by this either way.** The floor makes the **aggregate** readable; it does
not license *"this number has a source"* for any particular one. That is **one reading per token, and
there are 131.**

## IMPOSSIBLE here

- **distinguishing a citation from a coincidence for a single token** — needs the surrounding sentence
  read against the round it names. **SETTLES: IN-RELEASE**, 131 readings; unattempted.

`run.py` · `results/clause_number_sources.json`
