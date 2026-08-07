# R141 — ⚠ diagnosis added at R340: `delta_mean` and `ci` are different estimators

**This round has no README of its own; this file is a later annotation, not a rewrite.** The artifact
and `run.py` are untouched (L81). What follows is what a coherence gate found once it could see, and
what the source says about it.

## The defect, read out of `run.py` rather than inferred

`run.py:261–275` builds the two published numbers from **different objects**:

```python
ds = [v[neg].mean() - v[matched_positive(scheme, s)].mean() for s in SEEDS]   # all 5 seeds
# cluster bootstrap over prompts for the same contrast, first seed only
mp = matched_positive(scheme, SEEDS[0])                                       # ONE seed
...
"delta_mean": float(np.mean(ds)),                       # mean over 5 seeds
"ci":         [percentile(bs, 2.5), percentile(bs, 97.5)]   # bootstrap around SEED 0's matching
```

> **`delta_mean` averages five matched samples; `ci` brackets one of them.** They are not a point
> estimate and its interval — **they are two estimators of the same contrast, reported as a pair.**
> The source says so in its own comment: *"first seed only."*

## What that costs, measured across `finding_A`'s 14 cells

Displacement of the mean from its own interval's centre, in units of that node's
`delta_sd_over_seeds`:

| sub-node | n | range | median | all one sign? | flagged by the gate |
|---|---:|---|---:|---|---:|
| `length` | 14 | −0.88 … −0.62 | −0.72 | negative | 0 |
| `magnitude` | 14 | −1.80 … +0.15 | −1.22 | no | 0 |
| **`raters`** | 14 | **+4.48 … +9.53** | **+6.40** | **all positive** | **6** |

**The sign is not forced by the construction** — the two continuous covariates come out negative
from the same code path. So it is a property of the `raters` covariate.

## ⛔ And the gate undercounts it by design

`assurance/artifacts_are_internally_coherent.py` fails on *"mean outside the interval"*, which
catches only the **6 of 14** whose displacement exceeds the CI half-width. **All 14 are displaced at
more than 3 sd.** Six is how many the threshold happened to catch, not how many are wrong. The check
now prints the displacement from the centre alongside, and says so.

## What is established, and what is not

**D8, from the source:** the mean and the interval are computed from different objects, so the pair
is not internally coherent by construction — regardless of which number one prefers.

**HYPOTHESIS, not measured:** *why* it bites only `raters`. `matched_positive` bins on covariate
quintiles, and `nr` (rater count) is a **small integer** — tie-heavy bins mean the matched sample
varies far more across seeds than for continuous `length`/`magnitude`, so seed 0 is unrepresentative.
**The artifact stores only the mean and the seed sd, not the per-seed values, so this cannot be
settled without re-running R141.** Stated as a hypothesis rather than folded into the finding.

**Not established:** which of the two numbers is right. Both are committed; choosing needs a re-run
with the CI bootstrapped over *all* seeds' matchings, or the mean restricted to seed 0.

## Why it survived this long

The gate that would have caught it had a **broken positive control** — `fixture_dir` accepted a
fixture name (`rZZ_plant`) that the round-discovery regex `^[Rr]\d+_` rejects, so the planted
violation was invisible and the check reported `outside=[] contradict=[] -> FAIL` rather than a
green zero. Repaired at R340; the check found this on its first sighted run.
