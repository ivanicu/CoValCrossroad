# R637 · The observer in the population — three ways I measured myself instead of the object

**Decision this makes safe:** whether R636's twelve are a verdict. **They are.** The clean re-run
passes all three controls.

| control | first pass | **clean re-run** |
|---|---|---|
| POSITIVE — byte-identical | 38 PASS | **38 PASS** |
| **NEGATIVE — tree restored** | ⛔ **FAIL** | **PASS** |
| PLACEBO — files outside `results/` | 0 PASS | **0 PASS** |
| verdict | `UNVERIFIED` | **`B SOME MOVE` — 12 of 38** |

⭐ **Check #237's exclusion is SUPPORTED, not assumed**: with the operator still, the code restores
correctly, so the contamination was the operator.

## ⛔ ① `exit 1` is a VERDICT, and four "failures" were verdicts
R433 `EXIT 1 = W-LOSES` · R437 `W-INVERT` · R441 `W-DECORATION` · R442 `W-INSTANCE`. Only R431 has no
convention. **Corrected: 42 ran, at most 1 failed** — not "38 ran, 5 failed."
**15 of the 43 rounds encode their world in the exit code.**

## ⛔⛔ ② World C can fire on nothing — a DERIVATION
**15 verdict-encoding rounds vs a `≥1/3` threshold of 14.33. 15 ≥ 14.33.** If every one returned a
non-zero **verdict**, the harness would count 15 "failures" and **declare the corpus unreproducible
while it ran perfectly — by two-thirds of a round.**

> **The mirror of "a check that cannot fail" is a WORLD THAT CAN FIRE WITHOUT ITS STATED CONDITION
> EVER OBTAINING.**

⚠ Labelled a derivation: it follows from two measured counts and a fixed threshold.

## ⛔⛔⛔ ③ A wait-loop whose predicate matches its own command line never terminates
```
until ! pgrep -f "R636_.../run.py"; do sleep 5; done
```
**The shell running that loop carries the pattern in its own `argv`, so `pgrep` always finds it.**
It was waiting for itself to disappear.

**Sixth self-contamination in this arc, and the purest.** Not the round's artifact inside its
population (R601, R604, R621, R634), not the operator acting on the population (R636) — **the
instrument matching itself.**

### And it is why every timing claim this turn was wrong
| I reported | measured |
|---|---|
| "~10 minutes, 2× the first pass" | parent at **150 s**, on schedule |
| "exceeded 750 s" | **622 s** |
| "the second pass is much slower" | **288 s vs 284 s — the same speed** |

**Three wrong elapsed-time claims from one root, in the turn whose subject is measuring instead of
assuming.** *I was timing the observer.*

**IMPOSSIBLE, unchanged:** **determinism of output says nothing about correctness of output.** That
twelve conclusions moved is now a verdict; that any of them is now *right* is not.

## The sentence I can no longer write
> *"the second pass is slower, which is itself a signal."*

**It ran in 288 s against 284 s.** The signal was my own `sleep 5`.

## NEXT
World C is reachable without its condition obtaining, and the fix is one line: **classify a round's
exit by its declared convention, not by `returncode != 0`.** But before writing it, **count how many
of the 312 rounds declare an `EXIT` convention at all** — the 15 figure is from the 43-round at-risk
subset, and applying a subset's rate to the corpus is the error R635 made when it carried 195 forward.
