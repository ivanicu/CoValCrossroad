# R282 — is the 75-of-75 saturation forced by sample size?

**An attack on my own claim, made minutes earlier in R281.** Per §3 an attack is a full round, because
a cheap attack that appears to succeed retracts something true.

## The claim under attack

R281 reported all 75 weak orderings realised, and I wrote: *"the class space is fully used, so no
counting gate can separate a good core from a bad one."* With 18,384 rankings over 75 classes, a class
must have probability below ~1/18,384 to stay unseen. **The observation may be a coupon-collector fact.**

## Estimand

`n*` = the sample size at which the expected distinct-class count first reaches the observed support,
by **rarefaction**; and `n*/N`.

## Kill, pre-registered

```
if montecarlo_matches_closed_form and negative_control_plateaus:
    evaluate(n_star / N < 0.10)      # world A -> retract
else:
    verdict = UNVERIFIED
```

## Controls — all seven passed

| | returned |
|---|---|
| **POS estimator vs algebra** — Monte Carlo against the closed form `E[S(n')] = Σ(1 − C(N−nᵢ,n')/C(N,n'))`, a different code path with an **exact** answer | max dev **1.1604** vs tol 3.6099 |
| POS floor — `n'=1` | exactly 1 |
| POS ceiling — `n'=N` equals observed support | 75, 75 |
| POS fails at g=0 — single-class population | stays at 1 |
| **NEG** — 10-class synthetic at the same N must plateau at 10, never 75 | **10.0000** |
| SHAM — `unacceptable` block | 0 parsed |
| PLACEBO — `n'=0` | exactly 0 |
| **NOISE FLOOR measured**, 3 seeds × 8 reps | sd **1.2033** classes |

## Result

| n′ | world | personal |
|---:|---:|---:|
| 10 | 9.23 | 9.12 |
| 100 | 51.19 | 50.02 |
| 250 | 64.66 | 61.54 |
| 500 | 72.18 | 69.03 |
| 1000 | 74.73 | 73.26 |

| block | N | observed | `n*` | `n*/N` |
|---|---:|---:|---:|---:|
| world | 18,384 | 75 | **1,175** | 0.0639 |
| personal | 4,901 | 75 | **1,767** | 0.3605 |

**Verdict as pre-registered: WORLD C — split.**

## ⚠ The pre-registered statistic was the wrong one, and that is reported rather than swapped

`n*/N` differs 5.6× between blocks (0.064 vs 0.361) while **`n*` in absolute terms differs only 1.5×**
(1,175 vs 1,767). The ratio is driven by `N`, which is the quantity that varies — **normalising by it
manufactured a split that the underlying curves do not show.** The two rarefaction curves are nearly
superimposed at every `n'`.

The pre-registration's reading is reported as it stands (WORLD C). The correction is stated, not
substituted: **~1,200–1,800 rankings suffice to observe all 75 classes**, and both blocks far exceed
that. A threshold defined on a ratio whose denominator is the design variable is not a commitment.

## Register

| criterion | what it would require |
|---|---|
| out-of-distribution | rankings from a second elicitation |
| causally identified | intervening on annotator count |
| construct validated | an external answer to how many classes *should* occur |
