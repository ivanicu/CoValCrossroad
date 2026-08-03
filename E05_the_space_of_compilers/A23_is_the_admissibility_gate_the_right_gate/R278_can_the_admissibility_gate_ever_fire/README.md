# R278 — can the admissibility gate ever fire?

**The design.** The finding, its interval and its scope live in `E05/FORMULATION.md` and
`RETRACTIONS.md`. This file states what was asked and how, per P16.

## Why this and not the contradiction already on the page

`FORMULATION.md` carries a warning that the gate `C(n,k) ≤ a(m)` contradicts its own claim 5
(`H_eff ∈ [1.02, 3.45]` bits against the gate's `log₂75 = 6.23`). That warning was found by a
clean-context adversary and is not what this round tests.

This round comes from the **unit test** that R240's retraction produced the same morning:

> write the instrument's unit and the claim's unit as two strings, and require them **equal**.

| symbol | what it counts | unit string |
|---|---|---|
| `C(n,k)` | k-subsets of a prompt's n criteria | **candidate representatives** |
| `a(m)` | weak orderings of m responses | **behaviour classes** |

`"candidate representatives" != "behaviour classes"`. The gate compares a count of *criterion
subsets* to a count of *response orderings*, which makes one question decisive and nearly free:
**on this release, can it fail at all?**

## Estimand, named before the method

The number of `(prompt, k)` cells with `C(n_p, k) > a(m)`, over all 968 prompts, `k ∈ {1,2,3,4}`
and `m ∈ {3,4,5}`, plus the maximum of `C(n_p,k)` on that grid.

**Labelled a DERIVATION conditional on one measurement.** Given `n_p`, the predicate is forced by
arithmetic and could not have come out otherwise. The only measured input is the distribution of
`n_p`, so the round is reported as *what the release's criterion counts imply about the gate*, and
never as evidence about cores in general.

## Worlds and the prediction matrix

| | violating cells | max `C(n,k)` | the gate |
|---|---|---|---|
| **A** discriminating | 1–99% | > 75 | does real work |
| **B** vacuous | exactly 0 | ≤ 75 | a check that cannot fail |
| **C** over-strict | > 50% | ≫ 75 | rejects the release that produced it |

## Kill, pre-registered, as a conditional and not a threshold

```
if positive_control_fires and negative_control_moves: evaluate(violations == 0)
else:                                                 verdict = UNVERIFIED
```

A kill that can fire on a broken instrument is an automated way to publish an artifact.

## Controls

| | what it does | returned |
|---|---|---|
| **POSITIVE** | must fire where the answer is known by hand: `n=10, k=5 → C=252 > 75` | PASS |
| **ceiling/floor band** | must be *silent* at `n=6,k=4 → C=15`, so the threshold sits inside a real band | PASS |
| **fails at g=0** | silent at `n=k → C=1`, i.e. not already satisfied before anything is planted | PASS |
| **NEGATIVE** | destroy the criterion count, keep everything else: `n_p → n_p+6`. Excludes *"the answer is an artifact of a predicate that never reads n"* | moved, 7025 → 8549 |
| **PLACEBO** | `k=0 ⇒ C(n,0)=1`; must return exactly zero at every m | PASS |
| **SHAM** | the identical grid at `a(3)=13` and `a(5)=541` — same operation, ingredient `a(m)` replaced | see curve |
| **NOISE FLOOR** | **N/A, stated not skipped.** `C(n,k)` is arithmetic on an observed integer; there is nothing to resample and a measured floor would be identically 0. What carries uncertainty is the join — 966 canonical + 2 fuzzy, 18 unmatched — so that is reported instead |

## Specification curve

Axes: `k ∈ {1,2,3,4}` × `m ∈ {3,4,5}` × `n`-source ∈ {`coval_full`, seed-6, `coval_full`+6}.
**11,616 cells tested, 7,025 violating.** Printed whole, including the cells that kill world B and
the cells that kill world C.

## Seeds and reproducibility

**Seeds N/A and deliberately absent** rather than present-and-ignored — a seed argument that changes
nothing is a claim that it might. The computation is deterministic arithmetic with no draws.
Reproducibility is checked where this project has actually been bitten: **two `PYTHONHASHSEED`s,
artifact byte-identical** (13 of 19 E05 seeds once keyed on `hash()` over a string).

## What this site structurally cannot meet

| criterion | what it would require |
|---|---|
| cross-dataset / cross-release | a second values-annotation release with this schema. There is one. |
| causally identified | intervening on how many criteria an annotator writes — a property of the elicitation, not of us |
| construct validated | an external answer to *how many classes should a core distinguish*, which is the open question this arc exists inside |

## Artifact

`results/gate_grid.json` — carries the full `n_p` vector, so a rival can recompute every cell
without re-running the join, and the source hash of the script that made it.
