# R716 · what a quantised statistic can resolve — the provenance share, priced against its own quantum

**Fine enough for groups, never for an instance. The share is quantised: with `k ∈ {2,3,4}` it can
take exactly `7` values, and the smallest non-zero one is `0.2500` — **`3.82×` the population mean of
`0.0655`**. So no single instance can express a value near the mean. But the group mean IS resolvable:
bootstrap SE `0.00469`, and the MDE for a 493/493 split is `0.040` — **below** the quantum.**

## check #318 — one claim false, one a derivation I reported as a measurement

⛔ *"the FIRST per-instance quantity in this campaign that varies"* is **false**. `k` varies — 2, 3
and 4 over the 986 — and **R714 measured it one round earlier**. **Sixth false closing claim in this
arc**, and the second (after *"a single arm pair"*) carrying **no quantifier a word list could
catch**: it is a **precedence** claim, not a count.

⛔ *"seven distinct values"* was reported as an observation. It is a **DERIVATION**: with `k ∈ {2,3,4}`
the share `m/k` can take exactly `{0, ¼, ⅓, ½, ⅔, ¾, 1}`, forced before any data is read. **That all
seven are observed is the measurement; that there are seven is arithmetic.**

## the resolution, in three parts

| | value |
|---|---|
| support | `{0, 0.25, 0.3333, 0.5, 0.6667, 0.75, 1.0}` — 7 values, all 7 observed |
| **quantum** (smallest non-zero one instance can take) | **0.2500** |
| population mean | **0.0655** |
| **quantum ÷ mean** | **3.82×** |
| bootstrap SE of the mean (4500 resamples) | **0.00469**, 95% `[0.0566, 0.0749]`, width 0.0183 |
| **MDE**, 493/493 split, 80% power | **0.040** |

⭐ **No single instance can express a value near the mean** — the mean is carried entirely by the
minority that overlap at all. ⭐⭐ **But a between-group difference smaller than one instance's
smallest step is still detectable in aggregate.** That is the whole distinction, and it is the one
R705 had to make for the gain statistic: **a precise MEAN does not make a per-instance value
informative.**

## the power curve — planted shift → detection rate

| shift | 0.00 | 0.02 | 0.04 | 0.06 | 0.08 | 0.10+ |
|---|---|---|---|---|---|---|
| power | **0.06** | 0.71 | **0.99** | 1.00 | 1.00 | 1.00 |

## controls — all PASS (`controls_ok: true`), read from the artifact

| control | returned |
|---|---|
| **POSITIVE** | a planted 0.10 shift detected at **1.00**, with floor (no shift) **0.07** < 0.80 < ceiling (0.50 shift) **1.00** — the band is real |
| **g=0** | a shift of exactly 0 rejects at **0.07** vs 2α = 0.10 — not anti-conservative |
| **NEGATIVE** | labels shuffled at fixed sizes → 95% `[−0.0171, +0.0181]`, contains 0 — no split of these 986 shows a difference by itself |
| **SHAM** | `coval_full` against **itself** (identically 1.0) → bootstrap SE **0.000000** — a degenerate statistic has no resolution question |
| PLACEBO / SEEDS / NOISE FLOOR | identical runs differ by 0 · 3 bootstrap streams differ · spread measured over 4500 resamples |

## specification sweep — 3 splits × 2 statistics, all reported

| split | statistic | MDE |
|---|---|---|
| 493/493 | share | **0.040** |
| 493/493 | raw match count | 0.200 |
| 200/786 | share | 0.040 |
| 200/786 | raw match count | 0.200 |
| 100/886 | share | 0.040 |
| 100/886 | raw match count | 0.280 |

⚠ The **raw count** is swept because dividing by `k` is what creates the quantum, so **the count
bounds the share's resolution from the other side.** Its MDE is 5–7× worse, and it degrades with the
split while the share's does not.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** *(DERIVED)* support / quantum | 7 / 0.25 | **7 / 0.2500**, exact |
| **B** bootstrap SE | 0.005 [0.001, 0.02] | **0.00469** |
| **C** MDE | 0.04 [0.01, 0.15] | **0.040** |
| directional | quantum > mean | **HOLDS**, 3.82× |

## limits

- **A precise mean does not make a per-instance value informative.**
- **No analysis choice can improve the quantum** — it follows from `k ≤ 4`, the release's own bound.
  Only a release shipping larger cores could.

## impossible here

| criterion | what it would require |
|---|---|
| a finer statistic | a release whose cores carry more than 4 criteria |
| cross-release | a second release |
