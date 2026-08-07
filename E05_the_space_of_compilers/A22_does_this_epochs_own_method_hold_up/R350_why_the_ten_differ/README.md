# R350 — seven of the ten are real drift

**The decision this makes safe:** whether R344's *"25% do not reproduce"* is a defect count or a
composition. **It is a defect count for 7 of the 10.**

## Result — `W2_REAL_DRIFT`. All four controls PASS.

| verdict | n | rounds |
|---|---:|---|
| **CODE DRIFT** | **7** | `R102_margin_calibration`, `R107_joint_resample`, `R115_shrink_is_one_parameter`, `R121_is_the_advantage_the_metric`, `R328_the_three_readings_are_one_budget`, `R34_global_rater_crossfit`, `R36_channel_shapley` |
| NONDETERMINISTIC | 2 | `R221_contamination`, `R227_two_currencies` |
| CORPUS-DEPENDENT | 1 | `R242_self_audit` |

**Seven published numbers their own deterministic, corpus-blind code no longer produces.**

The other three are not defects: two draw without a seed (a design choice — but their committed
numbers were never reproducible and no re-running gate can ever certify them), and one counts rounds
in a corpus that has grown from 23 to 124.

## ⭐ The pre-registered cross-instrument prediction held — 2 of 2

R345 had flagged exactly two of these ten as **STALE**, from a completely different instrument: a
`sha256` of the round's own source recorded in its artifact. The prediction written before this run:
*if CODE DRIFT lands anywhere it should land there.*

| round | R345 (recorded hash) | R350 (re-execution) |
|---|---|---|
| `R115_shrink_is_one_parameter` | **STALE** | **CODE DRIFT** |
| `R121_is_the_advantage_the_metric` | **STALE** | **CODE DRIFT** |

**2 of 2.** A static hash comparison and a live re-run, sharing no code and no assumption, agree on
both. **And 5 of the 7 drifters carry no stamp at all** — the coverage gap R344 and R345 both
measured, now with named victims.

## How each verdict is decided — mechanically, not by reading intent

```
run1 != run2                       -> NONDETERMINISTIC   (the source is not a function)
run1 == run2 != committed, reads   -> CORPUS-DEPENDENT
run1 == run2 != committed, blind   -> CODE DRIFT
run1 == run2 == committed          -> R344 was unstable, and that is a finding about R344
```

## Controls

| | returned |
|---|---|
| **DETERMINISM, positive** | `R78_tokeniser_robustness` — a round R344 found reproducing → `run1 == run2 == committed` |
| **DETERMINISM, negative** | a planted round drawing from an **unseeded** rng → NONDETERMINISTIC |
| **CORPUS-READ, positive** | `R242` (counts rounds) → **True** |
| **CORPUS-READ, negative** | `R347` (reads **one named** census) → **False** |
| **ISOLATION** | of **766** artifacts present at the start, **0 changed, 0 vanished** |

### ⛔ The corpus-read control failed twice first, and both failures were mine

**v1 asked a regex** whether the source globs rounds. It was wrong **in both directions**: `R242` —
which globs `A*/R*/run.py` through a variable prefix — came out **BLIND**, and `R347`, which reads
**one named** census via `results/*.json`, came out **READS**. R242 was filed as CODE DRIFT while
direct measurement already showed it corpus-dependent (23 → 124 rounds), **inflating the count to 8**.

A tighter regex fixes both cases, and that is not enough: **a regex `blind` is a negative from a
search**, and a miss is not an acquittal. So the property is now **measured** — plant `N_PLANT = 24`
synthetic rounds and re-run; a round whose output depends on how many rounds exist moves.

**v2 planted them in `E99_fixtures`.** `R242` globs **E05 only**, so the probe was invisible to the
very round it was built to detect and R242 came out blind *again*. The plant now lands in E05.

> The same unit-equality rule in a third costume: **the instrument's population and the claim's
> population must be the same set before the control is designed.**

## Register

| criterion | status |
|---|---|
| what `CORPUS-DEPENDENT` still cannot see | a round keyed to a *specific arc*, which 24 planted rounds do not perturb — **misfiles as CODE DRIFT**, over-counting the defect rather than hiding it |
| `NONDETERMINISTIC` ≠ wrong | it says the committed number was never reproducible, not that it is false |
| `CODE DRIFT` ≠ wrong either | the committed number may still be correct; what is established is that **the code beside it produces something else** |
| population | the ten R344 found completing-but-differing — a census of that set, **not** of the corpus |

## The sentence I can no longer write

> *"a quarter of the corpus does not reproduce, and that is mostly design choices."*

**Seven of ten are drift.** Three are design.

Artifact: `results/r350_why_the_ten_differ.json`.
