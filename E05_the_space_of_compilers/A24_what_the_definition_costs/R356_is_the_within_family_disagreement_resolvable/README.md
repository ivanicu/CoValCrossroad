# R356 — the judges genuinely reorder one family, and the family that "agreed" was never evidence

**The decision this makes safe:** *how should R301's UNRESOLVED be read?* **Not as "the judges
mostly agree and one family is noisy."** The disagreement is real and localised; the agreement is
close to forced.

## Result — `W_EXCESS_DISAGREEMENT`. All three controls PASS. Two runs byte-identical.

| family | n | clause | sep (se) | sep (MDE) | ρ | null band `r=0.6` | null pctile | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `random_k` | 17 | ① | 2.21 | 0.79 | **−0.512** | [+0.59, +0.94] | **0.00%** | **BELOW** |
| `random_k` | 17 | ② | 2.14 | 0.76 | **−0.429** | [+0.46, +0.91] | **0.00%** | **BELOW** |
| `topw_k` | 8 | ① | 5.74 | 2.05 | +0.810 | [+0.66, +1.00] | 20.16% | inside |
| `topw_k` | 8 | ② | 5.79 | 2.07 | +0.667 | [+0.54, +0.98] | 9.72% | inside |
| `sham` | 3 | ①② | — | — | +0.500 | — | — | **DEGENERATE** |

**`random_k` sits at 0.00% of its own null — 0 of 12,000 draws — at the *most forgiving* shared-noise
level**, and survives Bonferroni over the 4 live cells (0.025/4 = 0.0063).

## I expected the opposite, and the separation is why I was wrong

The round was designed on the hypothesis that `random_k`'s ρ = −0.51 was **noise from an
unidentified ordering** — 17 random subsets whose true effects might be indistinguishable, both
judges ranking nothing. **That hypothesis is dead.** The family is separated by **2.2 standard
errors**, so there is a real ordering there, and the judges invert it.

⚠ **The unit nearly hid this.** v1 printed `sep = 0.79` — *below one resolution unit, therefore
noise* — because it divided by the **MDE**, while the null's noise is `se = MDE / ZEFF` with
`ZEFF = 2.80`. Both units are now printed, because they license different sentences: the MDE unit
answers *could one arm be called better* (no, 0.79), the se unit answers *is there an ordering to
agree about* (yes, 2.21). **Reading the first as the second would have confirmed my prior.**

## The arithmetic trap fired exactly as pre-registered — on the number that looked like good news

`topw_k`'s **+0.81** reads as strong between-judge agreement. It is not evidence of agreement: at
**5.7 se** of separation, two noisy readings of the same ordering agree almost surely, and the null
band's own floor is **+0.66**. The observed value sits at the **20th percentile of what is forced** —
*below* the middle of its band, not above.

> **Neither ρ was interpretable until it was priced against its own family's separation.** One looked
> like disagreement and is; one looked like agreement and carries no information.

**No family lands above its band.** `W-EXCESS-AGREEMENT` — the confound where the two judges' shared
errors inflate every agreement in the campaign — is **not observed**, and that is the outcome that
would have invalidated the other two readings.

## Controls

| | returned |
|---|---|
| **PLACEBO** — every family against itself | ρ = 1.0 exactly, all cells |
| **POSITIVE** — dose-response, fraction of arms shuffled → fraction flagged | 0.00 · 0.05 · 0.28 · 0.59 · 0.87, **monotone** |
| — floor | g=0 → **0.00**, so it can fail |
| — ceiling | the **maximal** plant (exact reversal, ρ=−1) caught in **4/4** |
| **g=0** — the exact null (0.8B = β·2B, no noise) | not flagged, 4/4; lands at null percentile **100%**, i.e. at the top |
| reproducibility | two runs **byte-identical** (`9d1cef3a4423`) |
| multiplicity | 4 live cells (2 degenerate, excluded); shared-noise levels are a **specification curve over one test**, not three tests |

## ⛔ Three control defects, all found by reading the output, all the control's own fault

The round printed **UNVERIFIED** twice before it printed a verdict. Each failure localised to
nothing about the data, which is the tell.

1. **The planted reversal was an arbitrary permutation.** v1 used `(β·t)[::-1]` — the reversed
   **array**. `t` is not sorted, so that is not a reversed **ranking**; it is a random permutation of
   17 arms, which lands anywhere. A true reversal is `−t`, ρ = −1 exactly. Retention 2/6, and
   nothing was wrong.
2. **The control's population was not the verdict's population.** The n=3 `sham` cells are excluded
   from the verdict as degenerate but were still scored in the control — and at n=3 a shuffle can
   only reach ρ=−1 one time in six, so those cells capped retention regardless of detector quality.
3. **`g=1` is not a maximal plant.** A full shuffle gives ρ≈0, not −1. Requiring it to be caught 95%
   of the time set the bar **above what the design can return** — the *control that cannot pass*.

Corrected to `floor < t < ceiling`: retention **0.00** at g=0 (it can fail), **monotone** in dose,
and the **exact reversal** caught 4/4 (the true ceiling, 1.0 here because the reversal is unique).

⚠ The `n<5 → DEGENERATE` rule was declared **after** seeing the cells, so it is a repair and is
labelled one. It changes nothing: both `sham` cells were `inside` before it was applied.

## What this does to R301 — and what it does not

**R301's amendment is not retracted.** It was right that a pooled R² can be carried by between-family
spread, and it is the only reason this question could be asked. What changes is the **reading of its
failure**:

- **not** *"the judges mostly agree; one family was noisy"* —
- **but** *"the judges resolvably invert one family's ordering, while the family that agreed was
  separated enough that agreement was nearly forced."*

That is **sharper** than UNRESOLVED, not a resolution of it toward SHRINK. `REORDER` survives, and it
now has an address.

## Register — what this site cannot do

| criterion | status |
|---|---|
| **a third judge** | **NOT ATTEMPTED, not impossible** — R301 records the prompt contract as byte-identical between `covalx/judge.py` and `E01/R04/run.py`, so a third model is a drop-in |
| **the true separations** | **N/A** — the null uses the 2B effects *as* the true ordering, which is the best available and is not the same thing. A real answer needs a third reading to estimate truth independently of either judge |
| **between-family relations** | **refused, not caveated** — only 3 families have n≥3, so a regression of ρ on separation would have n=3 points |
| **families with n<5** | 10 of 13 are singletons or pairs; Spearman is undefined or 4-valued there |

## The sentence I can no longer write

> *"the two judges broadly agree on the ordering of arms, with one noisy family."*

**They invert `random_k` at 0.00% of its own null, and their agreement on `topw_k` is what 5.7 se of
separation forces.**

Artifact: `results/r356_within_family.json`, source-stamped. Input: R301's `judge_slope.json`,
`sha256[:16] 4041dd0bdc6077f6`.
