# R515 · A per-prompt clause ① binds on 27% of conversations

**Decision this makes safe:** whether clause ① is deletable, or salvageable by re-operationalisation.

**Estimand:** the fraction of prompts on which the clause-① comparator outscores the clause-②
comparator. **Population:** 968 prompts. **Instrument:** per-prompt A2 over all annotators, the
statistic R294's `on()` uses. **Baseline:** the two comparators against each other.
**Regime:** k=4, pool truncated to 4 to size-match.

## Result

| | |
|---|---|
| mean bar₁ (`random_k4_s0`) | **0.4927** |
| mean bar₂ (blind pool[:4]) | **0.5504** |
| mean gap | **+0.0577** |
| **prompts where bar₁ > bar₂** | **26.96%** |
| exact ties | 20.56% |
| sd of per-prompt difference | 0.1597 |

**World B.** The global ordering is an **average that conceals a 27% minority where it reverses**.
Among non-tied prompts the pool wins about 2:1 — a real systematic tilt — but a per-prompt ① has
something to bind on, which the global one does not.

## Controls
- **Negative** — each comparator against itself: max |diff| **0.000000**. PASS.
- **Positive** — the mean gap must reproduce R294's own k=4 arms: **+0.0577 vs +0.0577**. PASS.
- ⚠ **The positive control FAILED TWICE FIRST, catching a different wrong object each time.**

## What the positive control caught — the round's real content
1. **A random-DRAW distribution instead of a fixed comparator ARM.** Clause ① compares against
   `random_k4_s0`, one specific arm *(R294 line 139)* — not against a per-prompt resampling of the
   prompt's own rubric, which is what the phrase "a random draw of that conversation's own rubric"
   invites you to build. Reconstruction gave 0.4171 against a target of 0.4927.
2. **The wrong population.** R294 computes each contrast on *that arm's own* prompt subset, and
   truncates the pool to *that arm's k*, so the aggregate gap is k-dependent: **+0.0470 to +0.0577**
   across arms, and all k=4 arms agree at exactly +0.0577. Comparing a 968-prompt reconstruction to
   a 41-arm average was comparing two different objects.
3. **The wrong release.** R294 loads `sat_{a}.npz`; I loaded `sat08_{a}.npz`. **Both exist**, differ
   in size, and load without error.

**Each failure was a wrong object, not a wrong number, and none would have been visible in the
output** — the first version printed a clean-looking 30% tail.

**Impossible here:** whether a per-prompt ① is the *right* formulation. That is a construct claim
and needs an external standard for what a core must do.
