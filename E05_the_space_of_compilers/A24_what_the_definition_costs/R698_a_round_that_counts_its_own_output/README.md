# R698 · a round that counts its own output

**⭐⭐⭐ R697's admissible population falls **14 → 4** when its own artifact is excluded — **71% of
what it counted was itself.** Its could-not-resolve verdict is **0 in every regime**. **The counts
are retracted; the conclusion stands.****

## CHECK #300 CAUGHT A NUMBER I HAD ALREADY REPORTED
Three populations for one round: my README said **79 / 44 / 8**; its committed artifact said **10**
admissible; a fresh run says **14**. Two causes, both mine to own:

1. **I wrote the README from a PRE-PATCH run and never re-read the artifact the same round had just
   written.** The round's own output was on disk, disagreeing with my prose, and **nothing checks
   prose against artifact.**
2. **R697 sweeps the arc's `results/*.json` and its own artifact is one of them**, so its population
   grows whenever anything is committed — including by itself.

## THE THREE REGIMES (G3 — every count, none hidden)

| regime | co-located | after filter | degenerate | admissible | ⭐ could-not-resolve |
|---|---|---|---|---|---|
| full corpus | 83 | 51 | 37 | **14** | **0** |
| **excluding R697's own artifact** | 53 | 21 | 17 | **4** | **0** |
| excluding R697 and everything after | 53 | 21 | 17 | **4** | **0** |

**Admissible drifts across `[4, 14]`. The verdict is `[0]` — stable.**

Registered **A (drop of 2) [0,8] → 10, OUTSIDE (+8)** · **B (verdict unchanged) HOLDS** ·
**directional (counts drift, verdict stable) HOLDS.**

**Controls:** POSITIVE — excluding R697's artifact reduces the count 83→53, *so self-inclusion **is**
the mechanism*. **g=0** — two runs over an identical corpus are identical, *so the drift is corpus
growth and not nondeterminism*. NEGATIVE — excluding a round with no artifact changes nothing.
PLACEBO — identical.

## ⛔ I REGISTERED A DROP OF 2 AND MEASURED 10
I expected self-inclusion to be a rounding effect. It is **most of the population.** **The direction
of the miss matters: I under-estimated how much of a corpus sweep is the sweeper's own output**, and
that is the same blind spot as R690 (an audit finds its own audit) and R697 (six "at floor" cells
were one measurement copied, including into its own scan).

## WHAT IS RETRACTED AND WHAT SURVIVES
- **RETRACTED:** every population count in R697's README and artifact.
- **SURVIVES:** R697's conclusion — **0 non-resolutions came from a design that could not resolve**,
  in all three regimes. **The kill fired on the world, not on the denominator.**
- R697's README is annotated in place.

## IMPOSSIBLE HERE
Recovering the corpus as it stood when R697 first ran needs a record it never wrote. **R697 stored
its verdict and not its file list** — the same gap R695 named one round earlier.

## NEXT
Three rounds in this arc sweep `results/*.json` across the whole corpus and write an artifact into
it: R690, R692 and R697 (`results/self_inclusion.json`, field `regimes`). Re-run each with its own
output excluded and compare the reported number against the excluded one. R697's dropped 71%; whether
that is typical or extreme decides if the corpus-sweep pattern needs a standing exclusion rule or a
one-off note.
