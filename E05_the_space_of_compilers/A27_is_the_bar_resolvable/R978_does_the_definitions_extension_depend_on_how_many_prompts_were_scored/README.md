# R978 · the definition's extension moves with the prompt count

**THE DECISION THIS MAKES SAFE.** Whether `core`'s membership can be stated as a list of arms. It
cannot — **at a quarter of the corpus, 10 of the 24 admitted arms change.** Any published extension
has to carry the N it was computed on, exactly as clause ④ now carries N and δ.

---

## The result

**Median churn** `|admitted(N) Δ admitted(968)|`, three seeds each, both legitimate comparators:

| N | `generic` (3 seeds) | `genericpool16` (3 seeds) | registered band |
|---|---|---|---|
| 242 | **10 / 4 / 10** | **2 / 2 / 3** | 13 · 7 |
| 484 | 2 / 1 / 2 | 2 / 0 / 0 | 6 · 5 |
| 726 | 0 / 0 / 1 | 0 / 0 / 0 | 5 · 4 |
| 968 | 0 / 0 / 0 | 0 / 0 / 0 | 4 · 4 |

Pre-registered: world A required median churn **≤ 1** at N=242. Observed **10** and **2**. **World A
is dead.** Monotone in N for both comparators, and bracketed above by the band count — the number of
arms within `z·sd/√N` of the cut, **computed from the full data before any subsample was drawn**.

⚠ **Report the spread, not the median.** Seed 202 gave 4 where the other two gave 10. The direction
is solid; the magnitude at N=242 is not a point.

## Controls

| control | result |
|---|---|
| **POSITIVE** | re-derives R923's committed extension **exactly**: `generic` cut 0.5593110792 / 24 arms, `genericpool16` 0.5513543392 / 28 arms |
| **PLACEBO** | admitted(968) against itself: churn **0** |
| **NEGATIVE** | arm labels shuffled → churn **52 and 62**, so the statistic can register instability |
| **NOISE FLOOR** | the band count, registered from full data before the sweep |

**24 cells tested, all 24 reported.**

## ⛔ The positive control caught a FRAMING error, which is the only kind a re-run cannot catch

My first operator was `mean(arm) > mean(comparator)`. It returned **26 and 30** against the committed
**24 and 28**, and the round printed **UNVERIFIED** rather than a world — even though the churn
numbers it produced (≤1 everywhere) would have read as a clean "the extension is stable."

Read from the object (`R923 run.py:145-151`), admission is `lo > 0` — the 2.5th percentile of the
**bootstrapped paired difference** against the comparator. It is a **resolvable** beat, not a mean
comparison. And the reported `cut` is `means[adm].min()`, the lowest admitted arm — which is why the
committed `generic` cut `0.5593110792` turned out to be **the mean A2 of `topw_k8`**, an arm I had
no reason to expect there.

⭐ **The error ran in the flattering direction for the null.** A plain threshold has no interval to
widen with N, so it would have *understated* the very effect this round exists to measure. A re-run
of my own algorithm would have reproduced it perfectly.

## What this means for the definition

Clause ② is a **resolvable** beat, so its admitted set inherits the CI width, which scales as
`1/√N` — the same mechanism R976 found under clause ④. Two clauses, one cause.

- **The extension is not a list; it is a list-at-an-N.** Publishing "these 24 arms are cores" without
  N is the same error as publishing ④'s reach without N and δ.
- **`generic` churns 5× more than `genericpool16`** at N=242 (10 vs 2), which is the comparator with
  the *higher* cut and the *smaller* admitted set — so a stricter bar is not a more stable one.
- Combined with the known comparator fragility (2 of 12 admitted arms flip between the two
  legitimate comparators), **membership is contingent on two design choices at once.**

## What this round cannot say

- **Subsampling confounds "fewer prompts" with "different prompts."** N is varied on one corpus; a
  second release would be required to separate them.
- **It measures whether the extension MOVES, not whether either extension is right.** Construct
  validity for `core` needs an external gold standard this site does not have.
- **The band is an upper bracket, not a fitted predictor** — 13 against a measured 10. It was
  registered rather than tuned, and it is reported as the bracket it is.

## Alternatives considered

**Raise NBOOT to shrink the interval and stabilise the set.** Refused: that changes the definition's
own operator to make its extension look stable, which is fitting the instrument to the answer. R923's
8000 draws are the committed setting and were kept.

**Report only `genericpool16`, where churn is 2.** Refused — that is the multiplicity failure with
manners. Both legitimate comparators are reported, and the disagreement between them is part of the
finding.
