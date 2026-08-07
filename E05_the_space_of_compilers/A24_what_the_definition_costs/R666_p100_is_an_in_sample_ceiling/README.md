# R666 · p100 IS the in-sample ceiling — R665's severity claim is retracted by its own corpus

**Decision this makes safe:** whether R665's "the definition is empty at its literal reading" can be
quoted as a *finding*. **No — the emptiness at p100 is substantially forced, and the claim that never
needed p100 is the one that survives.**

## What p100 actually is

| | |
|---|---|
| R328 `true_argmax` | **0.55747530882624** |
| R527 p100 `a2` | **0.55747530882624** |
| **identical to 14 decimals** | **p100 IS the in-sample ceiling** — the argmax over all 1,820 subsets **evaluated on the same data** |

R328 also flags `provenance_defect: true`, `equals_true_argmax: false`, `equals_split0_heldout: true`.

> ⛔⛔⛔ **So ②-at-p100 asks: does this arm beat the best subset fitted on the same data?** The arms
> that clear it are close to exactly the arms **with in-sample access** — which is why ③, which
> removes label-readers, removes all four.

## The extension at R328's three committed baselines

| baseline | a2 | brackets | **② ∧ ③ admits** |
|---|---:|---|---|
| budget-0 (20 draws) | 0.5397 | p050–p075 | **[2, 3]** — coval_core, topw_k4 |
| **held-out best of 1,820** | 0.5546 | p095–p100 | **[0, 2]** — *bracketed, not resolved* |
| **in-sample ceiling** | 0.5575 | p100 | **0** |

⚠ **A `[0, 2]` bracket does NOT license "non-empty."** The held-out case is **unresolved**, and
pinning it needs the per-arm `a2` scores that R527's 8-point curve does not carry.

## ⛔ What this retracts in R665

R665 asked *"could this have come out otherwise?"* and answered **"yes — 4 of 42 admitted against
4 of 42 removed; partial overlap was likelier."**

> **That counted ARMS and ignored the MECHANISM.** Against an in-sample argmax, the clearing set is
> substantially structural. **§0's arithmetic trap — committed in the round that quoted it.**

⭐ **What survives, and it never needed p100:** the definition's extension **depends on the
baseline** — **2** at the published percentile, **[2,3]** at budget-0, **[0,2]** at the held-out
best. That is R664's claim (② is a predicate on *(object, baseline)* pairs) and it stands.

## ⛔ Check #267 — all three checkable clauses of R665's NEXT fail

| claim | truth |
|---|---|
| *"the **last** structural question this definition has left"* | **23 lines** of STATEMENT.md flag something unresolved. §4's exact tell. |
| *"`topw_k4` — no core-construction at all"* | **R328 measures `topw_k4`'s SELECTION BUDGET as a lower bound.** It is a *selected* arm. |
| *"no clause removes it"* | True — but the reason I gave for caring rests on p100, which is a fitted quantity. |

## Controls

| control | returned |
|---|---|
| **positive** — R328's own reproduction block vs R287 | **3/3 ok** — PASS |
| **negative** — the three references distinct and ordered | **0.5397 < 0.5546 < 0.5575** — PASS |
| **placebo** — a value below budget-0 maps below p000 | **PASS** |
| **kill** — the held-out best must lie in [p095, p100] | **0.5546 ∈ [0.5511, 0.5575]** — PASS |

**MULTIPLICITY:** 3 reference values × an 8-point curve + 4 controls.

**IMPOSSIBLE, named:** the extension **exactly at** the held-out best needs per-arm `a2` scores;
R527's curve is sampled at 8 percentiles, **so the answer is a bound and is reported as one.**

## The sentence I can no longer write

> *"`② ∧ ③` is empty at its literal reading, and that could have come out otherwise."*

**It is empty against a baseline fitted to the same data, which is close to forced.** The severity
claim was the defect, not the arithmetic.

## NEXT

**The held-out bracket `[0, 2]` is the only cell in this whole curve that is unresolved, and it is
the only baseline in R328's three that is neither fitted nor arbitrary.** Pinning it needs one thing
the corpus has not surfaced: **the per-arm `a2` scores against the 0.5546 threshold.** R527 computed
admissions at 8 percentiles and discarded the scores; R328 holds the threshold. **Recover the per-arm
`a2` vector and evaluate ② at exactly 0.5546**, because the definition's extension at its only
defensible baseline is currently a two-element bracket containing both "empty" and
"{coval_core, topw_k4}" — and those are different definitions.
