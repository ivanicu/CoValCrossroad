# R225 — do raters add identification bits?

**Arc E05·A04.** R224 published a bound making the decision-preserving definition of `core`
NOT IDENTIFIED. The whole bound rests on **one sentence I asserted and never measured**:

> *"Adding raters does not raise `H_have`. Every rater orders the same `m` responses; their
> disagreement is information about raters, not about which criteria are right."*

This attacks it. `realstat` §3: the attack must be a full round, **hardest when it might succeed**,
because a cheap attack that appears to kill a true claim retracts something real.

## Three estimands, and the first two were mine

| attempt | statistic | positive control | why it failed |
|---|---|---|---|
| 1 | tied subsets at the optimum; raters planted as **weight dispersion** | 1.000 → 0.927 → 0.931 → **0.965** | non-monotone, and **>1 at k=2** |
| 2 | same statistic; raters planted as **sparsity** | 1.000 → 0.942 → 0.957 → **0.997** | non-monotone again |
| 3 | **recovery of a known generating subset** | monotone in noise, exact at zero | ✔ |

**Two different plants, the same shape of failure ⇒ the fault was not the plant, it was the
estimand.** Tie-count saturates from *both* ends: when raters agree, everything matching consensus
ties; when raters are maximally diverse, everything is equally bad and ties again. A statistic that
returns to 1 at maximum signal cannot measure that signal.

The correction is `realstat` G2 read literally — *plant a known effect; require **recovery***.

## And the arithmetic check caught the decisive bug, not a control

The first recovery run gave **12/12 cells** outside the seed spread, `recov_A 0.355` vs
`recov_B 1.000` at zero noise. But at `eps = 0` every rater is identical, so objective B's score is
*exactly* R× objective A's — the two are algebraically the same and **must** agree. They did not.

The cause: `psign(np.mean(raters))`. `raters` are 6-element **pair-sign** vectors; `psign()` expects
a 4-element **score** vector and indexes `y[i]−y[j]` over `range(4)`. It read four of the six pair
signs as if they were scores. **Objective A was being fitted to garbage.**

*"Could this have come out otherwise?"* — no, and that is what exposed it. No control would have.

## Result, after the fix

Recovery of the known subset, `K=2`, 300 prompts, 5 seeds, 1,500 distinct draws per cell:

| eps | R=2 | R=5 | R=14 |
|---|---|---|---|
| 0.00 | **+0.0000** ✔ | **+0.0000** ✔ | **+0.0000** ✔ |
| 0.10 | +0.0853 | −0.0040 | +0.0080 |
| 0.25 | **+0.1013** ⚠ | −0.0053 | +0.0127 |
| 0.50 | **+0.1120** ⚠ | −0.0080 | +0.0187 |

⚠ = outside the seed spread. **2 of 12 cells, and both are at `R=2`.**

### The verdict, scoped

At `R=5` the difference is **negative at every noise level**. At `R=14` it is +0.008 to +0.019 and
inside the spread. The two firing cells are at `R=2`, where the majority-sign consensus is itself
degenerate (two voters, ties everywhere) — so what fires there is the *consensus* being lossy, not
the raters being informative.

> **The release has ~14 raters per prompt. In that regime, keeping every individual ranking instead
> of collapsing to the consensus buys +0.019 of recovery against a seed spread of 0.06.**
> **R224's assumption survives at the release's own rater count**, and fails only at `R=2`.

R224's bound stands as written. Its deficit is not overstated in the regime it was applied to.

## The sentence that can no longer be written

*"Tie-count at the optimum measures how much the raters identify."* It saturates at both ends and
is non-monotone in the signal — twice, with two different plants, before I stopped blaming the plant.
