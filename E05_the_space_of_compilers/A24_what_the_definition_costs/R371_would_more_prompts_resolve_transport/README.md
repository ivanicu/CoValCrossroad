# R371 — R370's transport verdict is a specification choice, and the GPU job is justified for a different reason than I gave

**The decision this makes safe:** *should the 718-prompt job run?* **Yes — but not for the reason
R370's NEXT line gave, and R370's own verdict does not survive sweeping the specification it fixed.**

## Result — `W_N_BOUND_FIXED_S`. Three controls PASS. Two runs byte-identical. **No GPU spent.**

R370 closed with *"the binding constraint is now n."* Its MDE is
`ZEFF · sd(per-stratum contrasts) / √n_STRATA` — a **between-strata** error over **four points**.
More prompts shrink *within*-stratum noise, which is **not the denominator**. So the job was priced
here, for free, before any GPU.

| metric | S | contrast | obs sd | null sd | ratio | MDE |
|---|---:|---:|---:|---:|---:|---:|
| exact | 2 | +0.1002 | 0.0058 | 0.0308 | 0.19 | **0.0114** |
| exact | 3 | +0.0572 | 0.0516 | 0.0514 | 1.01 | 0.0835 |
| exact | 4 | +0.0810 | 0.0657 | 0.0679 | 0.97 | 0.0920 |
| exact | 5 | +0.0625 | 0.0325 | 0.0865 | 0.38 | **0.0407** |
| exact | 6 | +0.0650 | 0.0864 | 0.0917 | 0.94 | 0.0988 |
| exact | 8 | +0.0762 | 0.1073 | 0.1089 | 0.98 | 0.1062 |

**Median ratio 0.98** — the between-stratum spread **is sampling noise**, not structure.

## ⛔ The finding R370 did not look for: its verdict moves with S

On `exact` the contrast **RESOLVES at S = 2 and 5** and does **not** at S = 3, 4, 6, 8.

> **R370 reported S = 4 alone and called it `W-COLLAPSES`.** That verdict is a **specification
> choice**, not a property of the data — and R370 did not say so **because it never swept S.**

The honest statement is the **curve**, not the cell. (On `pair` the contrast is inside the MDE at
every S, so that metric is stable and negative throughout.)

## Why the job is justified — and why my reason was wrong

The MDE **rises** with S (0.0114 → 0.1062), because smaller strata get noisier faster than √S
recovers. Combined with ratio ≈ 1:

> **More prompts help by shrinking WITHIN-stratum noise at FIXED S — never by permitting more
> strata. Adding strata makes it worse.**

That is a precisely different recommendation from *"the binding constraint is n"*, which implied
scale alone.

## ⛔ Two of my own defects, both caught before publishing

**① The null was malformed and its ratio was nearly forced.** v1 resampled each stratum **from
itself**, which adds sampling noise *on top of* the real spread — so `observed_sd ≤ bootstrap_sd`
almost by construction, and the ratio could only land below 1. It returned **0.65** and I would have
published `W-OVERFIT`. **A control that can only come out one way is not a control.** Rebuilt as the
*no-heterogeneity* world — every stratum drawn from the **pooled** prompts at its own size — the
ratio moves to **0.98** and the verdict inverts.

**② The verdict string contradicted the line above it.** The else-branch printed *"and the MDE falls
with S"* while the printout said it does **not**. The kill simply had **no branch** for the world
that obtains: ratio ≈ 1 **and** MDE rising. **Fifth verdict-string failure this session** — both
facts are now computed and printed, and the reading follows from them.

## Controls

| | returned |
|---|---|
| **NULL** — no-heterogeneity world, built | non-degenerate at every cell; ratio 0.98 median |
| **PLACEBO** — S=1 | between-stratum sd **UNDEFINED, not 0**, and the code says so |
| **RANGE** | 6 values of S evaluable |
| reproducibility | two runs **byte-identical** (`c59c1330db8a`) |

## Register

| criterion | status |
|---|---|
| **the MDE at n=968** | **N/A** — that is the job's *output*, not its price. Every statement about it is an **extrapolation** and labelled one |
| **whether the S-dependence is about difficulty** | **N/A** — the strata are difficulty quantiles, but nothing here isolates difficulty from what co-varies with it |
| **a second judge** | **N/A** — pool labels are 2B only |

## The sentence I can no longer write

> *"the pool floor's MDE is 0.0920, so the design is close to resolution and the binding constraint
> is n."*

**The MDE is a 4-point between-strata error; the spread is sampling noise; the verdict moves with S;
and more prompts help only at fixed S.**

Artifact: `results/r371_power.json`, source-stamped.
