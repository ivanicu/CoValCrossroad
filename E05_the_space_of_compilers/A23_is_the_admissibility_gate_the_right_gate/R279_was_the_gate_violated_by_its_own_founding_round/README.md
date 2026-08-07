# R279 — was the gate violated by the round that proposed it?

**Design only.** The finding, its scope and its caveat live in `E05/FORMULATION.md` and
`RETRACTIONS.md`. One home per fact.

## How the question became answerable

R278 left the gate `C(n,k) ≤ a(m)` **undefined**: two readings of `n` giving 0% and 91.7% violation.
Its closing note said the tie is broken by a *fact about code already run*, not a preference.

Read from the source with an **AST walk**, not a grep:

| round | pool | bounds | k |
|---|---|---|---|
| R248 | `coval_full` | `NMIN,NMAX = 6,14`, `NPROMPT=250` | `[1,2,3]` |
| R252 | `coval_full` | same | `[1,2,3]` |
| R253 | `coval_full` | same | `[1,2]` |

⚠ **The grep was wrong and the AST was not.** `NMIN, NMAX, NPROMPT = 6, 14, 250` is a tuple
assignment, so the obvious pattern `NPROMPT *= *[0-9]+` returns **6** — the fourth loose pattern of
the day. It surfaced only because a 250-round population reported as 6 prompts is absurd on sight,
which is not a method.

That fixed the pool as `coval_full` and made a sharper question free: **R248's own artifact records
`C` for every cell it studied.** The founding round wrote down whether its own gate held.

## Estimand, named before the method

Cells in R248's own study population — its 250 prompts × its own `k ∈ {1,2,3}` — with
`C(n,k) > a(4) = 75`. Count and share, beside cells tested.

**DERIVATION conditional on the artifact**, per the arithmetic trap: given the recorded `n` the
predicate is arithmetic. What is *measured* is nothing; what is *read* is R248's population.

## Worlds

| | violating | means |
|---|---|---|
| **A** | 0 | the gate held in its own round; R278's 91.7% comes only from cells R248 excluded |
| **B** | > 0 | the gate was never satisfied by the evidence offered for it |
| **C** | — | the artifact's `C` is not `C(n,k)`; the round says nothing |

## Kill — a conditional, never a bare threshold

```
if C_matches_comb and negative_control_moves: evaluate(violations == 0)
else:                                         verdict = UNVERIFIED
```

## Controls

| | what it does | returned |
|---|---|---|
| **POSITIVE ①** | the artifact's `C` must equal `math.comb(n,k)` in **every** cell — two independent code paths on a quantity with a fixed right answer | **750/750** |
| **POSITIVE ②** | band: fires at `n=10,k=5` (252), silent at `n=6,k=4` (15) | PASS |
| **POSITIVE ③** | fails at g=0: silent at `n=k` (C=1) | PASS |
| **POSITIVE ④** | the baseline is **R248's own** `capacity` constant (75), not one I chose | PASS |
| **NEGATIVE** | destroy the count, `n → n+6`, by transforming the real artifact rather than inventing cases | **moved 834 → 1412** |
| **PLACEBO** | `k=1` under `a(5)`: `C = n ≤ 14 < 541`, must be exactly zero | **0** |
| **SHAM** | same cells, ingredient `a(m)` replaced by `a(3)`, `a(5)` | in curve |
| **NOISE FLOOR** | **N/A, stated**: a comparison of two integers already on disk. Nothing to resample; a measured floor would be identically zero. R248's population selection is *taken as given* — that is the point of the round, not a gap in it |

## Specification curve

`k ∈ {1,2,3}` × `m ∈ {3,4,5}` × n-source ∈ {artifact, artifact+6}. **2,250 cells tested, 834
violating.** Printed whole.

⚠ **The `k=1` zero is a DERIVATION and must not be read as evidence the gate holds there.**
`C(n,1) = n ≤ 14 ≤ 75`, so zero is forced by algebra. The smallest `n` that *can* violate at
`a(4)=75` is **13** at k=2 and **9** at k=3 — so the k=1 column could not have come out otherwise.

## Seeds, reproducibility

Seeds **N/A and deliberately absent** — no draws. Two `PYTHONHASHSEED`s, artifact **byte-identical**.

## What this site structurally cannot meet

| criterion | what it would require |
|---|---|
| **k=4** | R248 never ran it; this round cannot invent the cells. Would require re-running R248's selection at k=4 |
| cross-release | a second values-annotation release |
| causally identified | intervening on how many criteria an annotator writes |

## Artifact

`results/founding_round_gate.json` — the full `(k, n, C)` table plus the source hash, so a rival can
recompute every cell without reading R248.
