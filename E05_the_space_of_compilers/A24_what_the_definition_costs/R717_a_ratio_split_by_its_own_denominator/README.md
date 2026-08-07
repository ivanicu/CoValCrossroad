# R717 · a ratio split by its own denominator — the comparison R716 proposed, and why it was biased

**The share IS `m/k` and the split is BY `k`, so the comparison conditions on the statistic's own
denominator. The bias has a **known sign** — identical match counts force a *higher* share at smaller
`k` — and the observed difference runs **against** it. ⛔ But none of it is readable: the MDE at the
true `44/942` imbalance is `0.080`, **2.0×** R716's even-split `0.040`, against an observed
|difference| of `0.0131`.**

## check #319 — the numbers hold, the comparison does not

✓ `942` against `44` confirmed, and no round had split provenance by `k`.

⛔⛔ **But the groups do not share a support:**

| k | n | support of `m/k` |
|---|---|---|
| 2 | 1 | `{0, 0.5, 1}` |
| 3 | 43 | `{0, 0.333, 0.667, 1}` |
| 4 | 942 | `{0, 0.25, 0.5, 0.75, 1}` |

⭐ **DERIVATION, before any data:** at the same match count `m=1` the share is **0.2500** at k=4,
**0.3333** at k=3, **0.5000** at k=2. **Identical counts force a higher share in the smaller-k
group** — the bias has a known **sign**, and it pushes the small group **up**.

## what was observed

| | small (k<4) − big (k=4) |
|---|---|
| share | **−0.0131** |
| raw count | **−0.1052** |

⭐ **Both negative — the small group is lower on both, running *against* the bias's direction.**

## ⛔ and none of it is readable

| | |
|---|---|
| MDE at the true 44/942 | **0.080** |
| R716's even-split MDE | 0.040 |
| **ratio** | **2.0×** |
| observed \|difference\| | **0.0131** |

**power curve:** `0.00:0.06 · 0.04:0.52 · 0.08:0.96 · 0.12:1.00`

⭐ **R716's own caution was right**: an even-split MDE does not carry over to a group of 44. **Second
time in three rounds that computing the resolution first turned a proposed comparison into a bound.**

## controls — 6 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **POSITIVE** | a 0.20 shift into the 44-member group detected at **1.0000**; floor **0.0475** < 0.80 < ceiling **1.0000** — the band is real |
| **g=0** | a shift of exactly 0 rejects at **0.0475** vs 2α = 0.10 |
| **NEGATIVE** | labels permuted at the true 44/942 sizes → 95% `[−0.0388, +0.0464]`, contains 0 |
| **SHAM** | split on conversation-id **parity** at the same imbalance → **−0.0213**, inside the null |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |

⚠ **And the sham establishes less than it looks.** **0 of 6** sweep cells survive their own null —
**including the k-split cells** — so the parity sham landing inside the null does **not** show the
k-split is the ingredient. It shows **no split at this imbalance is readable**, which is weaker and
different. *(This sentence replaced an over-claim caught before the round landed.)*

## specification sweep — 2 statistics × 3 splits, all reported

| split | statistic | diff | null 95% | |
|---|---|---|---|---|
| k=4 vs k<4 | share | −0.0131 | [−0.0388, +0.0464] | inside |
| k=4 vs k<4 | count | −0.1052 | [−0.1528, +0.1802] | inside |
| id-parity sham | share | −0.0213 | [−0.0388, +0.0464] | inside |
| id-parity sham | count | −0.0806 | [−0.1528, +0.1802] | inside |
| random 44/942 | share | +0.0068 | [−0.0388, +0.0464] | inside |
| random 44/942 | count | +0.0137 | [−0.1528, +0.1802] | inside |

**0 of 6 survive.**

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** *(DERIVED)* bias direction / observed sign | higher share at smaller k / — | **AGAINST the bias**, −0.0131 |
| **B** MDE at 44/942 | 0.10 [0.02, 0.40] | **0.080** |
| **C** count difference survives? | predicted NOT to | **does not**, \|diff\| 0.1052 |
| directional | MDE ≥ 2× 0.040 | **HOLDS**, exactly 2.0× |

## limits

- **The bias cannot be analysed away.** Every share with `k` in its denominator inherits it; only the
  raw count avoids it, and R716 measured the count's MDE as **5–7× worse**.
- A difference in a statistic computed **from** `k` cannot by itself be a difference in provenance
  **between** k-groups.

## impossible here

| criterion | what it would require |
|---|---|
| an unbiased share | a statistic that does not divide by the split variable |
| answering the question | more than 44 cores with k < 4 |
