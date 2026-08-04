# R459 · R457's reliability survives without a partner — and the component table shows why the paired design works

**The decision this round makes safe:** whether R457's ρ_full = 0.8812 is a property of the **prompt**
or of **which wrong partner** the sham happened to draw. **It survives partner-free.** `W-CLEAN`.

## ⛔ The announced step's decision rule was half-valid

R458 closed proposing a bag-of-words overlap between each core's criteria and its own prompt: *"if it
reaches zero, the semantic hypothesis is weaker than it looks."* **Lexical overlap and semantic
relevance are different things** — an embedding captures what BOW cannot, so a BOW null is weak
evidence against the semantic hypothesis. The other direction (positive BOW → the GPU is worth it) is
sound. *Twenty-seventh announced step checked; half-valid, and not the most load-bearing thing
available.*

## ⭐ And checking it exposed a confound in my own most recent headline

R457's estimand is `d[p] = A2(core,p) − A2(sham,p)`, and **the sham applies another prompt's criteria
to p's responses.** Which partner was drawn is **fixed per prompt** in the release file — so a
split-half over *annotators* holds the partner constant, and **partner-driven variance counts as
perfectly "reliable" while being no property of prompt p at all.** R457 called 0.8812 *"the value of
having the RIGHT criteria on this prompt"*. Part of it could be the value of not having *that
particular* wrong set.

## ⚠ This round cannot decompose that variance, and says so rather than working around it

Because the partner is fixed per prompt, **no annotator-split can separate partner variance from
prompt variance.** What *is* testable: whether a **partner-free** estimand reaches the same
reliability. `generic` is a single fixed criterion set — **verified inside the run, not inherited:
exactly 1 distinct criterion-index tuple across all 968 prompts**, and the round exits 2 if it is not.

## Result — components first, so each difference's source is visible

| quantity | ρ_half | ρ_full | CI | seed sd | |
|---|---|---|---|---|---|
| core | +0.7209 | +0.8378 | [+0.8144, +0.8589] | 0.0116 | |
| sham | +0.7534 | +0.8593 | [+0.8440, +0.8815] | 0.0092 | |
| generic | +0.7232 | +0.8394 | [+0.8176, +0.8629] | 0.0047 | |
| oracle | +0.6608 | +0.7958 | [+0.7702, +0.8292] | 0.0146 | *positive control* |
| **d_sham** | +0.7876 | **+0.8812** | [+0.8452, +0.8956] | 0.0084 | R457's, **partner-confounded** |
| **d_gen** | +0.7186 | **+0.8363** | [+0.7684, +0.8474] | 0.0194 | **partner-free** |

**Δ = −0.0449**, well inside the ±0.15 band. **R457's committed 0.8812 reproduced exactly** through an
independent code path.

> **A partner-free estimand reaches essentially the same reliability, so R457's conclusion does not
> depend on which wrong partner was drawn.**

## ⭐ What the component table shows that neither difference alone could

**`d_sham` (0.8812) is MORE reliable than either of its components** (core 0.8378, sham 0.8593). A
difference exceeding both its parts happens when their *noise* is positively correlated — shared
annotator noise cancels in the subtraction. **That is the paired design working, observed rather than
assumed**, and it is the reason R457's estimand was a better measurement than the components it was
built from.

**And `d_gen` (0.8363) ≈ `core` alone (0.8378)** — subtracting a *fixed* prompt-blind set neither adds
nor removes reliability, which is what one expects when that set's per-prompt variation is mostly
shared prompt-difficulty.

## Controls

| control | returned |
|---|---|
| **POSITIVE** — the oracle's per-prompt A2 | ρ_full **+0.7958** [+0.7702, +0.8292] ✅ |
| NEGATIVE — prompt labels of half B shuffled | **−0.0114** ✅ |
| g=0 — a component against itself | ρ = 1.0 **by construction**; printed as a **DERIVATION**, licensing nothing |
| PARTNER-FREE verification | `generic` distinct tuples = **1**, asserted in-run; otherwise UNRUNNABLE |

⚠ **The oracle reads 0.7958 here and 0.8311 in R457 — different quantities, not a discrepancy.** R457
measured the oracle's *gap against the cross-fitted baseline*; this round measures the oracle's *A2
alone*.

## Impossible here, named

- **decomposing partner variance** — the partner is fixed per prompt in the release. Would require
  re-judging each core's criteria against several different partner prompts.
- **whether `generic`'s fixed criteria are representative** — one fixed set is one draw, and
  R450/R453 measured that fixed prompt-blind sets vary widely in strength (shares 0.0033 to 0.6247).

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
