# R535 · The third reading is remote — and the release's own selection rationale does not survive measurement

**Decision this makes safe:** how far ③-judge is from being distinguishable, and whether
satisfaction-spread selection does what its author argued.

## Result — WORLD B

| arm | reads | A2 | c2 | shortfall (MDE) | ② |
|---|---|---|---|---|---|
| `coval_core` | weights | **0.5665** | +0.0160 | −1.51 | **True** |
| `topw_k4` | weights | **0.5642** | +0.0137 | −1.26 | **True** |
| `topwvar_k4` | weights+sat | 0.5040 | −0.0465 | 3.24 | False |
| `topvar_k4` | **sat** | **0.4863** | −0.0641 | **4.24** | False |

### ① ③-judge is remote, not nearly-live
The satisfaction class is **4.24 MDE** from clearing ②, against `gen`'s **1.29** for ③-any
*(R530)*. **Distinguishing ③-any from ③-judge needs a satisfaction-reading arm to improve by more
than three times what the ③-any world needs to become non-empty at all.**

### ② ⭐⭐⭐ The documented rationale is refuted
`select_core.py` argues, in a comment labelled *"DERIVATION, not a hunch"*:

> *"a criterion whose satisfaction is IDENTICAL across the four responses … is arithmetically
> **INERT** no matter how important it is. `topw_k` selects on importance and is blind to this.
> Selecting on the **spread** of satisfaction across responses is **the direct fix**."*

**Measured: `topw_k4` 0.5642 vs `topvar_k4` 0.4863 — spread is LOWER by 0.0779.** And the hybrid
`topwvar_k4` at 0.5040 sits between, **still 0.0602 below weights alone.**

⭐ **The mechanism in the comment is correct** — an inert criterion adds a constant and flips no
pairwise sign. **The error is the inference from it:** selecting *for* spread optimises the wrong
quantity, because **high spread with low importance is noise**. Even multiplying the two
(`topwvar_k`) loses to importance alone.

## Controls
- **Source read** — the rationale confirmed verbatim in `select_core.py`.
- **Positive** — `ok2` reconstructed from each stored `(eff, lo, hi, mde)` via `report.verdict`
  matches the census for **41 of 41** arms, so the shortfalls sit on the census's scale.
- **Negative** — at least one compared arm must **clear** ②, else "shortfall" is measured only
  among failures and its scale is unanchored: **`topw_k4` and `coval_core` clear it.** PASS.

⚠ **Scope, and it corrects R534:** the satisfaction class holds **one arm in THIS census**;
`topvar_k4_08b` and `topvar_k4_08bR` exist on the second release and are outside this population.
**R534's "exactly one" was unscoped.**

⚠ **Impossible here:** whether spread selection would win under a **different judge**. The
satisfaction it reads is one model's output — **register row 2.**
