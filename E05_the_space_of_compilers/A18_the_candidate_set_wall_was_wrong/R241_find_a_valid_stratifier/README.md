# R241 — no valid stratifier exists, and that is the answer

**Arc E05·A18.** R238 used **separation** to match R233's arms without first checking that
separation predicts anything, and its own positive control killed it. The lesson is not *try
another one* — it is that **a stratifier must be validated as a predictor before it is used to
match**. So this validates every per-prompt variable this release carries, and reports the failures
beside the pass, because **testing seven and reporting the one that worked is exactly how a
stratifier gets chosen by the outcome.**

## The grid — all 16 cells, Bonferroni `α = 0.00313`

| stratifier | original ρ (p) | fresh ρ (p) | |
|---|---|---|---|
| separation | −0.008 (0.894) | +0.021 (0.743) | fails |
| criterion count | +0.005 (0.935) | +0.098 (0.124) | fails |
| length dispersion | −0.010 (0.875) | +0.020 (0.764) | fails |
| score entropy | +0.024 (0.711) | −0.055 (0.393) | fails |
| top-2 margin | −0.012 (0.870) | −0.042 (0.491) | fails |
| mean \|w\| | −0.013 (0.830) | +0.105 (0.094) | fails |
| **the floor itself** | **−0.203 (0.0010)** | **−0.216 (0.0010)** | **valid — and disqualified** |
| random vector | −0.021 (0.754) | −0.100 (0.124) | fails |

Continuous Spearman at the prompt level against a 2,000-draw permutation null — **not binned**,
because a bin count is a researcher degree of freedom and R238's four bins were one.

## Controls

- **positive** — the floor is *definitionally* related to `core − floor`, so it **must** come back
  significant. It does, at p = 0.0010 in both arms, which is the permutation resolution floor
  `1/(N+1)`. The machinery works. **⚠ And it is disqualified from use for precisely that reason:
  circular.**
- **negative** — a random per-prompt vector is not significant in either arm.

## The verdict

> **No valid stratifier exists among the seven per-prompt variables this release carries.**

R233's arms **cannot be matched by stratification here**. That is *the answer to that line*, not a
gap in it. The difference between original and fresh responses is not tracked by separation,
criterion count, length dispersion, score entropy, top-2 margin or mean weight — and if the cause is
a property of the **generator** rather than of the **prompt**, no per-prompt variable can reach it
in principle.

## What this settles about R233

R233's `+0.095` difference-in-differences stays **`UNVERIFIED`**, and now permanently so *by this
route*. Two rounds tried to control it and the honest position is:

- the floors differ by ≈0.026 — real
- **no measured per-prompt property explains that difference**
- so the transport signal is neither confirmed nor confounded-away; **it is uncontrolled, and the
  variables needed to control it are not in the release**

That belongs in the register as a named limitation with what it would require: **a second candidate
set generated to match the original's diversity**, so the arms are comparable by construction rather
than by adjustment. The generator, seed and parameters for that are recorded in
`a12_fresh_generations.json`.

## The sentence that can no longer be written

*"R233's confound can be controlled."* Seven variables, fourteen cells, none survives — and the one
that does is circular by construction.
