# R281 — does the coherent gate admit this release at all?

**Design only.** Findings live in `E05/FORMULATION.md` and `RETRACTIONS.md`.

## Why this round exists

R280 found G1 `log₂|H(Q)| ≤ H_eff` is the only unit-coherent gate, so the repair is a revert.
**The revert is not free.** Claim 5 measures `H_eff ∈ [1.02, 3.45]` bits. If the release's own target
needs more, the coherent gate rejects this release. That has to be **computed**, because *"the revert
probably works"* is exactly the flattering reading.

**Unit check first** — `log₂|H(Q)|` is *bits about a class*; `H_eff` is *bits about a class*. Equal.
That is why G1 is the form being priced.

## Estimand — two, because two are defensible and they are not the same quantity

| | |
|---|---|
| `log₂\|support\|` | the uniform bound the gate literally writes |
| `H(target)` | the entropy of the realised class distribution — what a channel argument actually requires |

## The estimator hazard, declared before the run

**Plug-in entropy is biased downward at finite sample, and the bias is in the flattering direction** —
it makes the release look more admissible than it is. So both plug-in and **Miller-Madow** are
reported and the gap is printed rather than buried. `|support|` is likewise a **lower bound** (unseen
classes), stated as such.

## Kill — a conditional, and the threshold is the *unflattering* end

```
if positive_recovers and negative_moves and not degenerate:
    evaluate(max_over_readings(requirement) < 1.02)   # H_eff's LOW end
else:
    verdict = UNVERIFIED
```

Using H_eff's high end would be choosing the arm that flatters the conclusion. The bracket is reported
whole and read against both ends.

## Controls — all eight passed

| | returned |
|---|---|
| **POS floor** — degenerate plant | exactly `0.0000` |
| **POS ceiling** — uniform over 75 classes | `6.2288` vs `log₂75 = 6.2288`, **retention 1.0000** |
| **POS band** — `floor < 1.02 < ceiling`, so a threshold is admissible | PASS |
| **POS MDE** — smallest plant separable from 0 | `K=2 → 1.0000` bits |
| **PLACEBO** — entropy of a constant column | exactly `0.0000` |
| **SHAM** — the `unacceptable` block carries *ratings*, so it cannot express an ordering | **0 of 4,901** parsed |
| **NEG pooled** — permute each annotator's labels independently | `5.953→5.999`, `5.836→5.962` |
| **NEG per-prompt** — ⚠ the load-bearing one | **+0.4640 to +0.5558** over 6 seed×block cells |
| **NOISE FLOOR — measured**, 198 bootstrap resamples | **sd = 0.0058 bits** |

⚠ **The pooled negative control is at ceiling and therefore weak** — all 75 classes are already
realised, so permutation has nowhere to move. **A control with no room is not a control.** The
per-prompt arm has room (`|support| ≈ 10` of 75) and is where the destruction is actually tested:
its effect is **80–96× the measured floor**.

## Specification curve — 8 cells, printed whole

| block | aggregation | estimator | `H(target)` | `log₂\|sup\|` | `\|support\|` |
|---|---|---|---:|---:|---:|
| world | pooled | plug-in | 5.9532 | 6.2288 | 75.00 |
| world | pooled | MM | 5.9561 | 6.2288 | 75.00 |
| world | per-prompt | plug-in | 3.0884 | 3.3021 | 10.36 |
| world | per-prompt | **MM** | **3.5128** | 3.3021 | 10.36 |
| personal | pooled | plug-in | 5.8362 | 6.2288 | 75.00 |
| personal | pooled | MM | 5.8471 | 6.2288 | 75.00 |
| personal | per-prompt | plug-in | 2.8391 | 3.0005 | 8.58 |
| personal | per-prompt | MM | 3.2821 | 3.0005 | 8.58 |

**0 of 8 cells fall below H_eff's low end (1.02). 3 of 8 fall below its high end (3.45).**

## Seeds, reproducibility

3 seeds for permutation and bootstrap, verified to change the draws. Two `PYTHONHASHSEED`s,
artifact byte-identical.

## What this site structurally cannot meet

| criterion | what it would require |
|---|---|
| `H_eff` re-measured under this round's parse | re-running R237; its bracket is taken as given |
| construct validated | an external answer to what the downstream system must distinguish |
| cross-release | a second release |
