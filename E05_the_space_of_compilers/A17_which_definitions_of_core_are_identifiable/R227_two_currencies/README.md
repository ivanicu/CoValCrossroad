# R227 — two currencies, and a capacity that is not usable

**Arc E05·A17.** Two corrections to R226, one round old, both mine.

## 1 · The price list mixed two currencies — `WITHDRAWN`

R226 priced per-criterion satisfaction at **60 bits** against the ordering's 5.96 and wrote *"closes
the gap ten times over"*. Those are bits about **different unknowns**:

| | | question |
|---|---|---|
| **T** | which criteria the norm actually uses | a **value** question |
| **S** | which criteria each response satisfies | a **fact** question |

`H_need = log₂C(n,k)` is denominated in **T**-bits. A ranking carries T-bits, because T generated
it. Per-criterion satisfaction carries **S**-bits — and in this repository **S is already
reconstructed**; every round since r04 uses the cached tensor. A human-reported S would **replace
the judge**, which is a real and large benefit, **on the instrument axis, not this one**.

> *"Per-criterion satisfaction closes the gap ten times over"* is withdrawn.

## 2 · The capacity that survives the currency check is not usable at human noise

The graded-score row *is* in the right currency. But R226 priced it by **capacity** and never
checked the bits were **usable**. Recovery of a planted subset, `K=2`, 300 prompts, 5 seeds, ties
credited `1/|ties|` so a tie cannot be cashed as skill:

| eps | const | rank | g3 | g5 | g10 | exact |
|---|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.0182 | 0.2083 | 0.2716 | 0.4743 | **0.7577** | 0.9993 |
| 0.10 | 0.0182 | 0.1002 | 0.1181 | 0.1493 | 0.1787 | 0.2033 |
| **0.25** | 0.0182 | **0.0527** | 0.0718 | 0.0779 | **0.0690** | 0.0820 |
| 0.50 | 0.0182 | 0.0358 | 0.0390 | 0.0458 | 0.0450 | 0.0487 |

**Controls, both exact:** negative (`const`) → 0.0182, *identical* to chance `1/C(n,K)`; positive
(`exact`) → 0.9993.

### The calibration that decides which row is the recommendation

The release's own human–human agreement on the top choice is **47.8%** (r179). Simulated:

| eps | 0.00 | 0.10 | **0.25** | 0.50 | 1.00 |
|---|---:|---:|---:|---:|---:|
| two raters agree on top choice | 100.0% | 71.3% | **48.4%** | 35.7% | 29.6% |

**Real raters sit at `eps ≈ 0.25`.** And there:

```
eps=0.00   g10 − rank = +0.5607   seed spread 0.0276   OUTSIDE
eps=0.10   g10 − rank = +0.0866   seed spread 0.0663   OUTSIDE
eps=0.25   g10 − rank = +0.0118   seed spread 0.0296   inside      <-- the release's regime
eps=0.50   g10 − rank = +0.0118   seed spread 0.0171   inside
```

**A 47× difference between the noiseless regime and the real one — and the noiseless row is the one
R226's capacity argument implicitly assumed.** At `eps = 0.25` the whole richness axis past `g3` is
within its own seed spread, and `g10` (0.0690) sits *below* `g5` (0.0779): past a point the extra
precision fits the noise.

## The conclusion this arc has been converging on

> **Precision does not close the gap. Independence does.**

Asking the *same* people a *finer* question fails, because their own disagreement — measured on this
release, not assumed — eats the extra resolution before it reaches the estimand. R224's `m = 6`
works because more candidates add **independent observations**, not finer ones.

## The sentence that can no longer be written

*"The cheapest fix is a question with more room in the answer."* It is the cheapest **in capacity**
and it buys `+0.012` at the noise level that applies, against a floor of `0.030`.

## Register

Whether a human could *supply* a 10-level score reliably is not tested here — that is a measurement-
error question about people and needs new elicitation. The simulation assumes the noise enters the
underlying utility, not the reporting scale; if humans are *additionally* noisy in reporting, the
gain is smaller still, never larger.
