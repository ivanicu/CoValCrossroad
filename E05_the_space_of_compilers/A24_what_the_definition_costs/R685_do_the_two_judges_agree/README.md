# R685 · do the two judges agree? — **NOT IDENTIFIED, n = 1**

**⭐⭐⭐ Of the 7 rounds recording two judges, exactly ONE exposes a per-judge verdict about the
object: R361's `rank_resolved`. It splits. So "instrument-dependent" rests on **n = 1** and cannot be
attributed to the clause OR to the benchmark — and the pre-registered kill fired before I could quote
the 100%.**

## THE COUNTS (G3 — all seven printed)

| round | verdict pairs | |
|---|---|---|
| **R361** | 1 | **DISAGREE** — `rank_resolved {2B: True, 0.8B: False}` |
| R362 R365 R477 R479 R481 R540 | 0 | EXCLUDED — no per-judge verdict field |

scored **1** of 7 · DISAGREE **1** · AGREE **0** · **kill FIRED (<4 scored) → counts only, no share**
Registered **A 3 [1,6] → 1, INSIDE (−2)** · **B 40% [15,70] → 100.0%, OUTSIDE (+60.0)** — and **B is
not reportable**, because a share over one pair is not a share.

## ⭐⭐⭐ MY INSTRUMENT COUNTED MY OWN CONTROLS AS VERDICTS
The first run found **10** verdict pairs across 3 rounds and reported **10.0% disagreement**. Nine of
those ten were `controls.positive`, `controls.g0`, `controls.placebo`, `controls.sham`. **A control
flag passes at both judges by design — that is what makes it a control.** So the "agreement" being
measured was *my own controls passing*, and it diluted the one real split from 100% to 10%.

**Instrument unit was "a per-judge boolean"; claim unit is "a per-judge verdict about the OBJECT".**
Not equal — §4's canonical failure — and the gap manufactured **90%** of the population. A fifth
control now exercises the exclusion.

## THE TWO DESIGN DECISIONS THAT WERE NAMED BEFORE THE RUN, AND BOTH MATTERED
- **Continuous values excluded.** A per-judge dict of means differs at every judge by construction;
  counting that as disagreement returns 100% and measures nothing. Control: `{2B: 0.51, 0.8B: 0.47}`
  → 0 pairs.
- **Rounds with no verdict field EXCLUDED, never scored AGREE.** Six of the seven land here. Scoring
  them as agreement would have produced *"6 of 7 rounds agree across judges"* — a clean, quotable,
  entirely manufactured result.

## ⛔ THIS DOWNGRADES WHAT R683 AND R684 PUT IN `STATEMENT.md`
The scope condition itself stands: R361's exact null does resolve at 2B and not at 0.8B. **What does
not stand is the generalisation.** One verdict pair cannot tell a clause property from a bench
property, and the wording implied a pattern. `STATEMENT.md` is annotated with the n = 1 caveat rather
than rewritten.

## IDENTIFICATION LIMIT
Agreement between **these two** judges is not agreement in general. Two is what the release ships;
**a rate over two bounds nothing about a third.**

## NEXT
One per-judge object verdict exists in the whole corpus (`results/judge_agreement.json`, field
`n_pairs`), and 81 rounds vary a judge without recording it (R684). The cheapest way to raise that
from one is not a new experiment: R683 showed R361's own exact null is re-derivable from committed
per-arm ranks. Check how many of the 81 unrecorded rounds store per-judge ranks or means from which
a verdict could be recomputed without re-running anything — that is the difference between a corpus
that lost its scope and one that merely did not print it.
