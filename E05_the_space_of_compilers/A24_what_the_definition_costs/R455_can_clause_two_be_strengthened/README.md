# R455 · clause ② **can** be strengthened — and the released core still clears it, barely

**The decision this round makes safe:** whether R453's 59.6% within-family weakness is repairable by
a stronger baseline, or has to be lived with. **Repairable.** `W-STRONGER`.

## The announced step was demoted, not killed

R454 closed proposing to read the pool's 16 criterion **texts** and, if they "span recipes", treat the
transfer question as partly answered. **Spanning recipes textually does not establish behaving as
multiple families** — *a label is not a description*, and R454's own behavioural handle (breadth
saturation) is stronger evidence than any reading of the texts. *Twenty-third announced step checked;
demoted for answering a weaker question than the previous two rounds set up.*

## The definitional move

R453: a fixed **prompt-blind** set reaches **59.6%** of the way from class floor to the released core.
R454: that saturates in breadth. **So ②'s baseline — "a size-matched prompt-blind set" — is weak:
most of what ② demands is reachable without reading the prompt.** The repair is to strengthen the
*baseline*, not the clause: require a core to beat **the best prompt-blind set that generalises.**

⚠ **Rung 2 says this is not forced, which is what makes it severe.** Full-sample A2: core **0.5715**,
best fixed prompt-blind subset **0.5618** — a gap of **+0.0097**, at this design's resolution.

## Result — 10-fold cross-fitted, every prompt scored out-of-fold

| seed | GAP | MDE | 95% CI | | distinct fold-picks |
|---|---|---|---|---|---|
| 0 | **+0.0139** | 0.0135 | [+0.0044, +0.0236] | RESOLVED | 4/10 |
| 1 | **+0.0142** | 0.0137 | [+0.0051, +0.0236] | RESOLVED | 5/10 |
| 2 | **+0.0141** | 0.0136 | [+0.0047, +0.0235] | RESOLVED | 3/10 |

**Seed spread 0.0001 against |gap| 0.0141 — spread/|gap| = 0.01.**

> ⚠ **Resolved at 1.04× its own MDE.** That is the edge of what this design can see. **The interval
> is the claim, not the point:** the released core beats the best generalising prompt-blind set by
> **+0.0047 to +0.0236**, and quoting "+0.0141" as a value would overstate what was measured.

## Controls — and two of them carry the round

| control | returned |
|---|---|
| g=0 — the baseline against itself | **+0.000000** ✅ |
| **POSITIVE** — ORACLE − baseline | **+0.1034** vs MDE 0.0108, CI [+0.0959,+0.1108] ✅ *the design has power* |
| SHAM — wrong-prompt core − baseline | **−0.0558** [−0.0666,−0.0451] ✅ *loses* |
| **NEUTRAL** — `generic` − baseline | **−0.0020** [−0.0086, +0.0045] — *unresolved* |
| **LEAKAGE** — the same test with an **in-fold** baseline | **+0.0011** |

⭐ **The NEUTRAL control is what makes the finding about the core.** An ordinary prompt-blind arm does
**not** beat the cross-fitted baseline — it sits at zero. So the result separates *"the core is good"*
from *"anything beats a cross-fitted pick"*, which nothing in R453 could.

⭐ **And the LEAKAGE control inverts the usual worry.** An in-fold baseline gives **+0.0011**,
unresolved — the naive design would have found **nothing**. The leak is **−0.0130**, nearly ten times
the honest gap, and it runs *against* the finding. **Cross-fitting did not inflate this effect; it
revealed one that an in-sample baseline was hiding by being unfairly strong.**

## A note the concentration finding predicts

The cross-fitted baseline uses only **3–5 distinct subsets across 10 folds** — the same near-stable
object R452 found winning 33.57% of prompts. **That stability is what makes "the best generalising
prompt-blind set" a well-defined thing to write into a clause** rather than a fold-dependent artifact.

## What this changes

- **② can be restated with a strictly stronger baseline** and the released core still satisfies it.
- **R453's 59.6% objection dissolves** as an objection to the *definition*: the core beats not merely
  the prompt-blind class but its best cross-fitted member. The 59.6% remains a true and useful fact
  about *how weak the original baseline was*.
- ⚠ **Scope**: stated against **this** prompt-blind family; exactly one with breadth exists (R454).

## Impossible here, named

- **a prompt-blind family other than this pool** — exactly one has breadth.
- **whether this is the RIGHT strengthening** — that is a choice. This round measures only whether it
  is *satisfiable* by the one object the release ships.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
