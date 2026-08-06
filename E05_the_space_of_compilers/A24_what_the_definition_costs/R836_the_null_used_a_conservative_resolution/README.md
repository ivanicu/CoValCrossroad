# R836 · the resolution R835 used is conservative by construction

**The decision this made safe:** how far R835's null travels. **Not as far as it reads** — its
"unresolved" is scope-dependent, and the scope is a correlation assumption it never stated.

Design in `PREREGISTRATION.txt`, committed with `run.py` before it ran.

## What R835 did, and the direction it errs in

R835 flagged its MDE as *"arm-vs-BAR, not arm-vs-arm — an approximation."* ⛔ **It never said in
which direction the approximation errs, and it errs toward the null.**

Both arms are scored as differences against the **same** bar, so

```
d_AC = d_AB − d_CB       sd(d_AC)² = sd_A² + sd_C² − 2·ρ·sd_A·sd_C
with sd_A ≈ sd_C:        MDE_AC = MDE_A · √(2(1−ρ))
```

**Using `MDE_A` directly IS the assumption ρ = 0.5.** For any ρ > 0.5 the true resolution is
**finer**. Two arms scored against a common bar share that bar's noise, so ρ > 0.5 is the expected
case — R825 measured `corr(bar, core) = +0.8377` for a comparable pairing on this site.

## Controls

| control | result |
|---|---|
| **SIMULATION on the derivation itself** — 4000 replicates of n=968 at ρ ∈ {0.0, 0.5, 0.84, 0.95} | empirical `sd(d_AC)` **1.4138 / 1.0002 / 0.5656 / 0.3162** vs closed form **1.4142 / 1.0000 / 0.5657 / 0.3162** — **match <1% at all four** |
| positive (application) — `oracle_k4` vs `generic` | ρ* = **−5.18** → separable for every admissible ρ ✓ |
| negative — arm against itself, looked up **twice** | ρ* = **1.0000** exactly → never separable below ρ=1 ✓ |
| three seeds (1, 2, 7) | byte-identical |

## Result — a sensitivity curve, not a re-verdict

**3 of 45** adjacent pairs become separable below the borrowed ρ = 0.8377:

| upper | lower | gap | **ρ\*** |
|---|---|---|---|
| `gen` | `random_k12_s0` | +0.0267 | **0.334** |
| `generic` | `gen` | +0.0182 | **0.692** |
| `promptecho` | `topvar_k4_08b` | +0.0229 | 0.822 |

⭐ **`gen` vs the random cluster flips at ρ = 0.334** — barely above independence. So *"the label-free
class does not separate from random"* is the claim most at risk from R835's unstated assumption.

**W-CONSERVATIVE.** R835's null is scope-dependent, and its scope is **ρ ≤ its own implicit 0.5**.

> ⚠ **CORRECTED BY R837 — the ρ\* above use the 1× criterion, while R835's verdict used 2×.**
> So this table **over-predicts** how many pairs flip at R835's own bar. Recomputed at 2×, the
> thresholds are **0.719 · 0.956 · 0.923**, and R837's measured **ρ = 0.870 · 0.899 · 0.835**
> predicts **SEPARABLE · not · not** — which is exactly what R837 measured, **3 of 3**.
> **The derivation was right; the threshold it was evaluated at did not match its parent round.**

## What this round does not do

⚠ **ρ is not measured here** — the per-prompt difference vectors were never persisted — so **no pair
is re-labelled SEPARABLE**. ⚠ **R835's pre-registered verdict is not rewritten**: its kill fired as
written, and a verdict is not reopened because a later round prefers a different resolution model.
It is **annotated**. ⚠ **0.8377 is borrowed** from a *different* pairing and is recorded in the
artifact as such.

## NEXT

The curve is a function of ρ and ρ is the one quantity this site has not persisted for arm pairs.
Measuring it means re-scoring two arms on the same prompts and keeping the per-prompt difference
vectors — a re-run whose cost is one scoring pass, and whose result decides three of these pairs
rather than arguing about them.
