# R505 · There are two ceilings — and `oracle_k4` is resolvably above neither

**Decision this makes safe:** what the withdrawn recommendation actually needs in order to come back.
**Not a better number — a decision about what a core is constrained to emit.**

## The two ceilings, recomputed in one process (968 prompts, 3 seeds)

| quantity | value | vs `oracle_k4` **0.6325** |
|---|---|---|
| **pair-predictor ceiling** — per-pair mode, Bayes-optimal for per-pair 0/1 loss | **0.6466** | **−0.0141** |
| **ranker ceiling** — modal complete sign-vector (R479's estimator) | **0.6230** | **+0.0095** |
| measured noise floor (max seed spread) | **0.0220** | — |

**Both gaps sit inside the floor.** `oracle_k4` is **not resolvably above or below either bound.**

## Why there are two, and why neither round noticed

R479 takes the **modal ranking vector** — the most common complete 6-tuple among the other
annotators. R504 takes the **per-pair mode**, each coordinate independently. Under a loss that
decomposes per pair, the per-pair mode is Bayes-optimal, **so R504's number is necessarily ≥ R479's:
that ordering is a derivation, not a finding.**

But the per-pair mode can be **intransitive** (A>B, B>C, C>A), which no ranking realises. **Measured:
the per-pair mode is realisable by some ranking on only 66.5% of 400 prompts.** In the other third,
**no ranker can attain the pair-predictor bound** — which is exactly why the two numbers differ.

- **0.6230 bounds RANKERS** — predictors constrained to emit a consistent order.
- **0.6466 bounds PAIR PREDICTORS** — unconstrained per-pair sign emitters.

**`oracle_k4` emits a criterion set whose score sums induce a ranking, so the ranker bound is the one
that applies to it.** R504 compared it against the other one.

## What this does to R504's withdrawal

**R504 was right that the two quoted numbers were incomparable, and wrong to imply there is one
ceiling.** The withdrawal stands, but its *reason* changes: not *"`oracle_k4` is below the ceiling"*
but ***"the comparison is unresolvable at this design's resolution, and the applicable ceiling was
never named."***

⭐ **That is a stronger position than either previous round held**, and it is the third revision of
this same comparison in three rounds — each one overturned by a better instrument rather than a better
argument, which is the pattern the standard's own longest failure-mode entry describes.

## What R479's label costs

R479's docstring reads *"BAYES = E[A2(modal human ranking, a HELD-OUT human annotator)]"* and its
verdict text calls it the ceiling for **any predictor under per-pair 0/1 loss**. **It is not — it is
the ceiling for RANKERS.** The per-pair Bayes optimum is higher and unattainable by any ranking on a
third of prompts. Every `headroom = BAYES − best` computed from it is therefore a headroom **to the
ranker bound**, which is the right bound for arms that emit rankings, and the wrong one for anything
that emits pair judgements directly.

## The bound

The recomputed ranker ceiling here is **0.6230** against R479's quoted **0.6132** — still a gap,
smaller than before and plausibly the draw convention (this round draws once per prompt per seed;
R479 averages 20 reps). **Not isolated, and stated rather than smoothed over.**
