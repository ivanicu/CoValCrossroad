# R373 — the definition's transport MDE averaged FOUR strata, and the campaign did not record that anywhere

**The decision this makes safe:** *does R372's denominator collapse reach beyond the stratum family?*
**Yes, to exactly one round — and it is the one `DEFINITION.md` cites.** The debt it exposed is
**paid, not frozen.**

## Result — `W_CONTAMINATED_RECORD_SHARE_UNVERIFIED`. Five controls PASS. Two runs byte-identical. **No GPU spent.**

| | |
|---|---:|
| MDE call sites in the campaign's source | **55** across **38** rounds |
| sites whose denominator counts aggregated units, not the sample | **5** |
| of those, outside the stratum family R370–R372 | **R355, R368** |
| of those, with **resolved** k < 10 | **R368 only, at k = 4** |
| P(sd lands below half its true value) at k = 4 | **13.9%** |

**R368 is the round `DEFINITION.md` cites for transport** (`+0.0992` vs MDE `0.0654`). That verdict
is **not refuted — it is under-priced**, and the difference matters because nobody re-examines a
cell that reported RESOLVED.

## (a) The derivation, labelled as one

`sd_hat² (k−1)/σ² ~ χ²_{k−1}`, so `P(sd_hat < f·σ) = chi2.cdf(f²(k−1), k−1)`. **Algebra — it could
not have come out otherwise.**

| k | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 20 | 200 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P(sd < σ/2) | .383 | .221 | .139 | .090 | .060 | .028 | .006 | .000 | ~0 |

## (b) The assumption is tested, not assumed away

The ratio **p10/median of the MDE carries no free parameter** — it is a pure function of k. R372
measured it at 6 values of k in 4 specifications, so the prediction faces **24 cells it could have
missed**:

**max abs error 0.0642, mean 0.0213**, tolerance 0.10 — while the prediction itself ranges
0.186 (k=2) to 0.668 (k=8). *Not a wide net.*

## ⛔ Three instruments in this round, two of which I had to correct before publishing

**① The obvious census would have manufactured a scandal.** 479 of 1,542 stored MDEs have a sibling
key named `k`, `n`, `kept` or `arms` — but **`k` in this campaign means CORE SIZE.** R301 stores
`{'k': 4, 'n': 968}` beside an MDE whose denominator is √968. A census keyed on `k` would have
reported R301 as a 4-unit design. **A key that looks like the quantity is worse than a missing key:
absence prompts a check and a plausible name does not.**

**② A word list I wrote here had no positive control, and its number is withdrawn.** v1 measured
*"what share of rounds record their denominator's count"* against a whitelist of key names, got
**2 of 38 (5.3%)**, and that would have been the headline. **R355 stores it as `n_pairs_pooled` and
R368 as `len(strata)`** — both false negatives. *A guessed word list cannot prove an absence.* The
share is **UNVERIFIED**, and the pre-registered branch that rested on it reports UNVERIFIED rather
than being re-derived from a better list after the fact.

**③ The flag is not the severity, and resolving k ran against my own finding.** The parser classifies
what a denominator *counts*, not how many. **R355 was flagged and its k is 25**, where the collapse
probability is 0.0001. Judging "contaminated" on the flag would have convicted a round that is fine.
**Only k decides — and after resolving k the contamination is one round, not two.**

## Controls

| | returned |
|---|---|
| **CHI MODEL** ⭐ | 24 cells, no free parameter, max err **0.0642** vs tolerance 0.10 |
| **PARSER (+)** | must classify R372 as small-k (a stratum count) and **R301 as sample** (√968, its `k=4` being core size) — both known independently. Both correct |
| **PARSER (−)** | a source with no estimator yields **0** call sites |
| **PLACEBO** | at k=200 the collapse is **1.7e-29**; at f=1 it is **0.5133** — the median, known independently of this code |
| **RANGE** | spans 0.383 (k=2) to 0.028 (k=8) |
| reproducibility | two runs **byte-identical** (`32760077858e`), stdout identical |

## The pre-registration, kept verbatim

Two of its three branches did not survive contact with their own instruments. **Both changes are
reported in the output rather than folded back into the kill block** — a pre-registration edited
after the data is not a pre-registration.

## ⭐ The debt is PAID, not frozen

`assurance/an_mde_records_its_denominator.py` — a round computing `ZEFF·sd/√k` over **aggregated
units** must record k in its artifact. It flagged **R368 and R370**, the exact two rounds whose k had
to be hand-traced out of JSON. Rather than freeze them, both were re-run with `n_units` recorded:

**Only `n_units` and `source_sha256` changed in either artifact.** Every published number is
untouched. **5 of 5 compliant, frozen debt 0.**

⚠ **Why a word list is legitimate in the gate and was not in ②:** the gate **specifies** acceptable
names going forward; a specification cannot be wrong about absence because it defines what counts.
The same list is invalid as a measurement and valid as a convention.

## Register

| criterion | status |
|---|---|
| **whether any published verdict FLIPPED** | **N/A** — needs the per-unit vectors the artifacts do not store. The same wall the census measures |
| **the share of the campaign that records its denominators** | **UNVERIFIED** — the only instrument available was a word list with no positive control. Not low; unmeasured |
| **call sites this parse cannot see** | bounded by the parser's positive control, not by hope |
| **a second release** | **N/A** — one release |

## The two units, which no wording closes

This round counted **55 CALL SITES**. It did **not** count published numbers, and the link between
them is precisely what the artifacts do not carry. **Every sentence here is about call sites; none
is about how many verdicts would change.**

## The sentence I can no longer write

> *"R372's denominator collapse is a quirk of the stratum family."*

**It reaches R368, at k=4, which is the transport row of the definition itself — and the campaign
had no record from which to notice.**

Artifact: `results/r373_resolution_audit.json`, source-stamped.
