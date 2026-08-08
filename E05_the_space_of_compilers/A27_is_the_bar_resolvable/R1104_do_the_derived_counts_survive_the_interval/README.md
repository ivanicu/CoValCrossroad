# R1104 — the three derived counts split. **Nesting survives** (as a near-derivation), **the slack does not** (9 → [7, 17]), and **the ladder's terminal zero was never a measurement**.

**The decision this round makes safe:** which of the composed numbers this arc publishes still mean
anything after R1103 put an interval on the set they are computed from. **One of three, and not for
the reason it was published.**

⛔ **The answer was not deducible from R1103.** A difference of two unstable sets can be **more**
stable than either — if both move together, the common noise cancels — or **far less**, if they move
independently. R1103 measured the marginals; the covariance decides, and it had not been measured.

## ⭐ The result — 750 bootstrap resamples of the 968 prompts, 3 seeds

| derived quantity | published | resampled | verdict |
|---|---:|---|---|
| **R1098 nesting** `released_only` | **0** | **0 in 750/750**, max 0 | ✅ survives |
| **R1099 slack** `blind_only` | **9** | **10.48 [7, 17]**, min 6, **max 23** | ⛔ point estimate |
| **R1101 ladder** | **24 → 9 → 6 → 0** | **22.86 → 7.94 → 5.22 → 0.00** | mixed, below |

### The ladder, step by step

| step | published | mean | 2.5–97.5% | min | max |
|---|---:|---:|---|---:|---:|
| `released` | 24 | 22.86 | [17, 26] | 14 | 26 |
| − leakage | 9 | 7.94 | [3, 10] | **0** | 10 |
| − authorship | 6 | 5.22 | [0, 7] | 0 | 7 |
| − authorship − `topw` | 0 | **0.00** | [0, 0] | 0 | 0 |

⛔⛔ **The terminal zero is STRUCTURALLY FORCED, not measured.** It is non-empty in **0 of 750**
resamples. At the point estimate `released − authorship` contains **only** `topw` arms, so
subtracting the `topw` arms empties it **by construction** — and R1101, which I committed three
rounds ago, reported it as a measurement. **The arithmetic trap, in my own ladder.**

⚠ **And the leakage step reaches 0 too**, in the lower tail below the 2.5th percentile. R1101's
headline contrasted authorship (*admits nothing*) with leakage (*admits 9*); under resampling, the
leakage reading's admitted set also falls to zero, just rarely. **The contrast is a matter of
frequency, not of kind.**

## ⚠ The nesting survives — and saying only that would overstate it

`released_only = 0` in **every one of 750** resamples, MC SE 0.0000. But this was pre-labelled in the
run before it executed, because a perfect share is the shape of a derivation:

> **R1098 already measured the mechanism** — all 15 blind subsets score **below the weaker released
> comparator**. An arm that beats the strong pair therefore beats the weak fifteen, on **any**
> resample. So nesting holding at 1.000 is largely **forced by that ordering**, not evidence that
> resampling is kind to it.

**The honest form: R1098's nesting is robust because its mechanism is, and the resampling confirms
the mechanism rather than the claim.**

## ⛔ R1099's slack is a point in a range

**10.48 [7, 17]**, min 6, max 23, against a published **9**. Span **10** against the threshold of 4
(R978's registered band, the same yardstick R1103 used). ⚠ And the mean sits **above** the point
estimate, the opposite direction from `|admitted|` (22.77 vs 24) — because the slack is a difference,
and the blind family sheds fewer arms under resampling than the released one does.

**So *"the bound's slack is 9 arms"* is one draw from a distribution reaching 17 at the 97.5th
percentile**, and R1099's per-arm classification of those 9 is a classification of one particular
sample's 9.

## Controls — 6, all green after one repair

| control | result |
|---|---|
| POSITIVE the point estimate reproduces R1098's committed sets **by name** — 24 / 33 / 0 / 9 | PASS |
| PLACEBO the identity draw returns exactly the point estimate | PASS |
| NEGATIVE a family minus itself is empty in every resample | PASS |
| INSTRUMENT the analytic inner bound equals the 4,000-draw bootstrap on **both** families | PASS |
| SHAM R1055's inner-seed control gives a **degenerate** interval — `(0, 9)` at all 3 seeds | PASS |
| SEEDS the outer seed flag changes the draws (checked on `blind_only`, which varies) | PASS |

⛔ **The SEEDS control failed on the first run, for its own reasons, and the diagnosis is this
round's own finding.** It compared the first ten `released_only` values across seeds — and
`released_only` is **0 in every resample**, so all three seeds were trivially identical and the
control declared the seed flag dead. **It presupposed a non-null quantity, on precisely the quantity
this round measures as null.** §4's *the control fails for its own reasons*, sub-kind ②. Repaired to
run on `blind_only`, which varies.

⭐ **And the SHAM is R1055's control one level up:** holding the prompt sample fixed and varying only
the inner bootstrap seed returns `(released_only, blind_only) = (0, 9)` at all three seeds — a
**degenerate** interval on quantities whose real intervals are `[0, 0]` and `[7, 17]`. The seed
control cannot see the slack moving at all.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the **true** sampling distribution | **N/A** | a second independent draw of 968 prompts; the bootstrap approximates it and is labelled throughout |
| whether the blind family is the **right** comparator family | **N/A** | R1097's standing limit. This round prices the published numbers; it does not re-choose the family |
| a stable slack at this n | **N/A** | ≈ 8× the prompts, since the cut's resolution scales as 1/√n and R1102 measured the MDE at 0.008–0.010 |
| cross-release | **N/A** | a second release |

`run.py` · `results/derived_counts.json`
