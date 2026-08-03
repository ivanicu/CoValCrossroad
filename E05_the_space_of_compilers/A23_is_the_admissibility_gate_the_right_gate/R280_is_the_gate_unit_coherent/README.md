# R280 — is the gate unit-coherent, and was the mismatch introduced or always there?

**Design only.** Findings live in `E05/FORMULATION.md` and `RETRACTIONS.md`.

## The decision this closes

R278 (undefined LHS) and R279 (violated by its own founding data) both leave one thing open, and the
two answers imply **different actions**:

| | repair |
|---|---|
| the mismatch was **introduced** by the revisions | **revert** |
| it was **always there** | **rebuild** |

## Why this round does not judge

The three canonical forms, extracted from git rather than memory:

| | form | occurrences |
|---|---|---:|
| **G1** | `log₂\|H(Q)\| ≤ H_eff` | 190 |
| **G2** | `C(n,k) ≤ A_real` | 221 |
| **G3** | `C(n,k) ≤ a(m)` | 421 |

⛔ *"Do these two sides count the same kind of thing"* is a **judgement**, and my judgement about my
own definition is void — sampled from the weights that wrote it. So the round runs a **gauge test**,
which is mechanical:

> **Two quantities are the same kind of thing only if they respond to the same transformations of the
> underlying sets.**

Change the criterion count, hold responses fixed (`T_n`); change the response count, hold criteria
fixed (`T_m`). Each quantity moves or does not. **The signature is computed, not classified.**

## Estimand

For each quantity, `(responds to T_n?, responds to T_m?)`, measured as the **share of prompts whose
value changes**; and per gate form, whether the two sides' signatures are equal.

## Identification — partially identified, and the split is stated rather than blurred

| | quantities | status |
|---|---|---|
| **MEASURED** | `C(n,k)`, `a(m)`, `A_real` | computable exactly on this release |
| **DERIVED** | `\|H(Q)\|`, `H_eff` | class space of m responses, and a capacity over that same space; neither is a function of `n`. **From the definitions — not evidence** |

Because G1's verdict rests on two derived signatures, **G1's verdict is reported DERIVED and G2/G3's
MEASURED.** Not averaged, not merged.

## Kill — a conditional, not a bare threshold

```
if positive_controls_fire and negative_control_separates:
    evaluate(G1_coherent and not G3_coherent)
else:
    verdict = UNVERIFIED
```

A gauge test that calls everything coherent — or everything incoherent — has no discriminating power
and its verdict on the real gates is void.

## Controls — all eight passed

| | what it does | returned |
|---|---|---|
| **POS floor** | a quantity against itself must be COHERENT | PASS |
| **POS ceiling** | a hand-known mismatch *not under test*, `C(n,k)` vs `m`, must be INCOHERENT — so `floor ≠ ceiling` and a real band exists | PASS |
| **POS g=0** | under the **identity** gauge every quantity must show **zero** response | all zero |
| **NEG** | a constant (42) has signature `(F,F)` by construction; `C(n,k)` vs `42` must separate. Excludes *"the classifier reads names, not measured responses"* | PASS |
| **PLACEBO** | `C(n,k)` vs `C(n,k)`, exactly coherent | PASS |
| **SHAM** | the same machinery on **permutation** gauges — reorder criteria, reorder response labels. These change no set's *size*, so every response must be zero | zero |
| **SEEDS** | 3 seeds control which criterion `T_n` drops and which response `T_m` drops; signatures must agree across all three | identical |
| **NOISE FLOOR** | **measured, not assumed**: max response under identity + both permutation gauges | **0.0000** |

Two `PYTHONHASHSEED`s, artifact byte-identical.

## Result

| quantity | signature | |
|---|---|---|
| `C(n,k)` | `(True, False)` | measured |
| `a(m)` | `(False, True)` | measured |
| `A_real` | `(True, True)` | measured — responds to **both** |
| `const42` | `(False, False)` | negative control |
| `\|H(Q)\|`, `H_eff` | `(False, True)` | **derived** |

**Signature distance, computed not typed:**

| | | distance |
|---|---|---:|
| **G1** | `(F,T)` vs `(F,T)` | **0** — coherent |
| **G2** | `(T,F)` vs `(T,T)` | **1** |
| **G3** | `(T,F)` vs `(F,T)` | **2** — disjoint |

⚠ **Three points in revision order, not a law.** The sequence 0 → 1 → 2 is exactly the three
revisions; it is a description of what happened, not a trend with a fourth point to predict.

## An independent corroboration worth recording

`A_real` measures `(True, True)` — it responds to `T_n`. R253 reached the same defect by a completely
different route: *"the gate had `n` on both sides."* **Two independent instruments, one conclusion**,
and neither knew about the other.

## What this site structurally cannot meet

| criterion | what it would require |
|---|---|
| `H_eff`, `\|H(Q)\|` **measured** rather than derived | re-running R237's estimator under both gauges — a separate round, and NOT claimed here |
| construct validated | an external answer to *what the gate should compare*, which this field has no gold standard for |
| cross-release | a second release |
