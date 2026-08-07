# R1022 — the loader's `< 200` guard is a constant nobody chose. What does it actually decide?

**The decision this round makes safe:** whether any committed count in this arc has to be re-run at a
different coverage threshold. It does not — and the reason is algebra, not a measurement.

## What provoked it

R1021's NEXT. R1021 showed the guard **admits** arms whose scores are 79% imputed; nobody had asked
whether it **excludes** anything, or whether removing partial arms moves the admission of arms that
stay. The guard is one bare literal in **22 round scripts** (21 with no nearby comment), so there is
no single place it could ever have been reviewed.

## Two derivations, done before any compute — the second killed this round's first design

- **① The regime count.** Coverage over the 98 arms this round loads takes exactly **four** distinct
  values — `{4: 1 arm, 200: 2, 398: 2, 968: 93}`. A threshold can only ever partition this population
  four ways, so the curve is **complete, not sampled**.
- **② A threshold cannot flip a retained arm.** An arm's imputed vector is `nan_to_num(v,
  nan=nanmean(v))` — it depends only on that arm's **own** observed values. And each comparator is a
  **single scored arm** loaded from its own `sat_*.npz`, not a pool recomputed over surviving
  candidates. So `admitted(τ) = admitted(τ=1) − removed(τ)` is **forced**.

  ⛔ My first design forked on exactly the mechanism ② rules out. Running it and reporting the
  surviving world would have been *1+1=2, therefore 2<3*. It is kept below as a **bookkeeping check**
  — it confirms the code matches the algebra and is **not evidence about the guard**.

## The question that survived

The guard exists to stop imputation manufacturing an admission. **Does it?** The release ships the
extreme case already: `provenance_probe`, **4 real prompts of 968**.

⚠ It is **not** in R1000's population and **not** in ③'s size record, so the coverage guard was never
the filter that excluded it, and it could not enter a committed extension at any τ. It is inserted in
front of the operator as a **declared counterfactual on the OPERATOR**.

## Result — **World C, neither world as written: the answer is target-dependent**

| target | comparator | `lo` (2.5%) | seed spread | admitted |
|---|---|---:|---:|---|
| `A2` | `generic` | −0.1335 | 0.0002 | No |
| `A2` | `genericpool16` | −0.1247 | 0.0001 | No |
| `A1·consensus` | `generic` | **+0.3476** | 0.0005 | **Yes** |
| `A1·consensus` | `genericpool16` | **+0.3528** | 0.0005 | **Yes** |

**Dose–response — the margin is monotone in how much of the vector is real:**

| arm | real | imputed | `A2` | `A1·consensus` |
|---|---:|---:|---:|---:|
| `provenance_probe` | 4 | 99.6% | −0.1335 | **+0.3476** |
| `coval_core_2bA` | 200 | 79.3% | +0.0095 | **+0.0020** |
| `coval_core` | 968 | 0.0% | +0.0078 | **−0.0042** |
| `topw_k4` | 968 | 0.0% | +0.0054 | **−0.0021** |

Under the exact-match target, **broadcasting an arm's own mean over unmeasured prompts is worth more
than any real signal it could carry.** ⭐ This is the mechanism behind R1020 and R1021 rather than a
separate curiosity: the twins reproduced it at 200/968, this arm at 4/968 at a 50× lower coverage and
a far larger margin. Three coverage levels, same target, same direction — so **the R1021 finding
generalises beyond the two arms it was measured on.**

## The complete curve (four regimes, both targets, all 16 cells)

| target | τ=1 | τ=200 | τ=398 | τ=968 |
|---|---:|---:|---:|---:|
| `A2` | 9 | 9 | 7 | 7 |
| `A1·consensus` | 4 | 4 | 2 | 2 |

## Controls

- **POSITIVE** — two committed extensions, from two **different** rounds, recovered by one code path:
  R1000's 9 at τ=200 **PASS**, R1011's 7 at τ=968 **PASS**. Both can fail.
  ⚠ The first attempt read one key for both and printed FAIL against a membership that was already
  correct — *the control failed for its own reasons*. Cost: one run.
- **RANGE** — the pool must gain `provenance_probe` at τ=1 and not before: **PASS**.
- **PLACEBO** — coverage held constant at 968: extension identical at all four τ: **PASS**.
- **NEGATIVE (this round's own falsifier)** — `admitted(τ) = admitted(τ=1) − removed` at all 8
  (target, τ) cells, or derivation ② is wrong and every verdict here is void: **PASS**.
- **SEEDS** — 3; every membership call stable, `lo` spread ≤ 0.0005.

## What this closes and what it does not

- ✅ **R1021's NEXT is answered.** Raising the guard to full coverage changes membership **only** by
  deleting the arms it deletes. No committed count in this arc is at risk beyond the twins R1011
  already withdrew.
- ❌ **The guard is still undeclared.** `200` in 22 scripts, 21 with no comment. A finding about the
  **programme**, not the release.
- **N/A cross-release** — whether four coverage levels is this benchmark's accident or a general
  property needs a second release. Not planned; nothing here bears on it.

`run.py` · `results/coverage_threshold_curve.json`
