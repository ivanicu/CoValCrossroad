# R458 · the per-prompt advantage is **replicable and unexplained** — 4.4% of its own ceiling

**The decision this round makes safe:** whether the definition can earn a scope line naming *where*
clause ② holds. **Not from the release's own observables.** `W-OPAQUE`.

## ⛔ The announced step overclaimed its own null

R457 closed: *"a null there would be the strongest statement available: the advantage varies by
prompt in a way **nothing observable** predicts."* **A null on three hand-picked covariates says
those three.** "Nothing observable" quantifies an unenumerated population — §4's *closing sentence*
row names this exactly, and its tell is the word *nothing*. *Twenty-sixth announced step checked;
framing corrected before running.*

**And a stronger design cost the same:** fit a cross-fitted predictor from a whole target-free
feature set and report out-of-fold R² against R457's measured ceiling. That turns *"does covariate X
matter"* into *"how much is explainable at all"*, and makes the null **quantitative rather than
rhetorical**.

## Result — out-of-fold R², by feature block

| block | ncol | R²_oof | share of ceiling |
|---|---|---|---|
| **all** | 17 | **+0.0384** | **0.044** |
| core only | 5 | +0.0135 | 0.015 |
| sham only | 5 | +0.0170 | 0.019 |
| pool only | 4 | +0.0167 | 0.019 |
| lengths only | 3 | −0.0040 | −0.005 |

> **17 target-free features explain 4.4% of a quantity that replicates at 0.8812.** The core's
> advantage is prompt-specific, **replicable**, and **unexplained** by them.

⚠ **The scope is these features, named, not "observables":** `core_mean, core_sd, core_range,
core_respsd, core_k, sham_mean, sham_sd, sham_range, sham_respsd, sham_k, pool_mean, pool_sd,
pool_range, pool_respsd, len_mean, len_sd, len_range`.

## ⭐ The both-arms diagnostic caught §4's trap in the act

| feature | r(f, core) | r(f, sham) | r(f, **d**) | raises both? |
|---|---|---|---|---|
| `core_range` | **+0.4520** | **+0.3676** | **+0.0636** | **YES** ⚠ |
| `core_respsd` | **+0.4542** | **+0.3752** | **+0.0578** | **YES** ⚠ |
| `core_sd` | +0.2857 | +0.2137 | +0.0599 | YES ⚠ |
| `pool_respsd` | +0.2055 | +0.2615 | −0.0704 | YES ⚠ |
| `sham_respsd` | +0.0950 | +0.2352 | −0.1528 | no |
| `pool_mean` | +0.2576 | +0.0920 | +0.1599 | no |
| `len_mean` | −0.0469 | −0.0028 | −0.0438 | no |

**8 of 17 features raise both arms.** `core_range` correlates **+0.45 / +0.37** with the two arms and
only **+0.064** with their difference. **A naive stratification on satisfaction spread would have
shown a large-looking arm gap driven entirely by both arms rising** — the manufactured differential,
observed rather than assumed. This table is why the announced three-covariate design was the wrong
instrument even before its framing was corrected.

## Controls

| control | returned |
|---|---|
| **POSITIVE** — a planted `d + noise` column | R²_oof **+0.9170** ✅ *the pipeline recovers signal* |
| …fails at g=0 — a pure-noise column | **+0.0374** vs unplanted **+0.0384** ✅ *does not fire* |
| NEGATIVE — outcome shuffled against features | **−0.0227** ✅ *out-of-fold R² can go negative, which is what makes it an honest null* |
| CEILING — R457's reliability of `d` | **0.8812**, so R²_oof is read as a **share** and never as an absolute |

**The positive control at 0.9170 is what makes 0.0384 a measurement rather than silence:** the same
pipeline recovers a planted signal at 24× the observed value.

## What this means for the definition

- **The definition gains no scope line from these observables.** Clause ②'s advantage varies by
  prompt, replicably, and nothing computable from the release without a second instrument predicts
  where.
- ⭐ **That is a positive result about the object, not a failure of the round:** a quantity with
  reliability 0.88 and explainability 0.04 is *structured but not by anything on this site* — which
  is a sharper statement than either "it's noise" or "it depends on X".
- ⚠ **It is bounded by the feature set.** A semantic representation of the prompt is the obvious next
  instrument, and it is deliberately outside this round.

## Impossible here, named

- **a statement about features not in the set** — no finite design makes it; the announced
  *"nothing observable"* was exactly that.
- **semantic features of the prompt** — needs an embedding model, i.e. a second instrument. This
  round is confined to what the release yields on its own.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
