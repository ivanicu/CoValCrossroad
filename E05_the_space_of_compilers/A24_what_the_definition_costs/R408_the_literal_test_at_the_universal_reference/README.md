# R408 — read literally, clause ② admits all five. Every one of them inside its own noise.

**The decision this makes safe:** *is "better than every prompt-blind set" satisfiable without label
access?* **Yes under the sentence's own wording — and by margins none of them can distinguish from
zero.**

## Result — `W_LITERAL_ADMITS`. Reproduction control passes **arm for arm**. **No GPU.**

| arm | k | **e** | se | `e / (ZEFF·se)` | strict | literal |
|---|---:|---:|---:|---:|:--:|:--:|
| **`coval_core`** | 4 | **+0.009002** | 0.003703 | **0.87** | ✗ | ✓ |
| `topw_k6` | 6 | +0.008183 | 0.003589 | 0.81 | ✗ | ✓ |
| `topw_k4` | 4 | +0.006705 | 0.003853 | 0.62 | ✗ | ✓ |
| `topw_k8` | 8 | +0.004810 | 0.003704 | 0.46 | ✗ | ✓ |
| `topw_k3` | 3 | +0.004114 | 0.003839 | 0.38 | ✗ | ✓ |
| `oracle_k4` *(reads labels)* | 4 | **+0.070828** | 0.003785 | **6.68** | ✓ | ✓ |
| `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` *(read labels)* | 4 | +0.037 … +0.057 | ~0.004 | 3.4 – 5.5 | ✓ | ✓ |

| label-free admitted | |
|---|---|
| under **STRICT** (`e>0` **and** `\|e\| ≥ ZEFF·se`) | **∅ — n = 0** |
| under **LITERAL** (`e>0`) | **all five: `coval_core`, `topw_k3/4/6/8`** |

## ⛔ What this does to R407

**R407's emptiness was partly an artifact of a significance term the definition does not contain.**
Read as written, clause ② at the universal reference **is** satisfiable without label access.

**But the honest report is not "a core was found."** It is that **the definition as written has no
error control**: every label-free arm clears the bar by less than its own `ZEFF·se`, the best of them
(`coval_core`) reaching **0.87** of it. The four label-reading arms clear by **3.4× to 6.7×** — an
order of magnitude apart, which is what the significance term was separating.

## ⛔ The re-implementation was the risk, and it was controlled before it was used

R360's `build`/`ref_at`/`admits` are nested inside its `main()` and cannot be imported. So:

| | |
|---|---|
| **the scoring layer** | **imported** from the module R360 itself uses (`load_sat`, `load_targets`, `yvec`, `cls`) — never copied, because *a re-implemented classifier tests the copy* |
| **REPRODUCE (+)** ⭐ | my **strict** variant returns R360's committed `p=100` cell **exactly** — `PASS`. **A control whose answer was produced by a different round for a different purpose** |
| **SUPERSET** | `literal ⊇ strict` — **forced by construction**, so asserted as a sanity check on the code and **not reported as a finding** |
| **K RESTRICTION** | only the k values the 9 tested arms need were built. Declared: `ref_at` is per-k, so restricting k **cannot** change any tested arm's verdict — it is a cost saving, not a scope change |

## ⚠ One release

**An unguarded positive mean is precisely the quantity that would not survive a second release**, and
this round cannot speak to that. Five effects between `+0.004` and `+0.009`, each with `se ≈ 0.0037`,
are exactly what a replication is for.

## Register

| criterion | status |
|---|---|
| **whether `e > 0` replicates** | **N/A** — one release, and this is the quantity most at risk |
| **a second judge** | **N/A** — at 0.8B nothing is admitted at any safe reference (R358/R359) |
| **deciding which rule the definition means** | **N/A** — an act of definition. **Both are reported** |

## The sentence I can no longer write

> *"nothing satisfies clause ② at the universal reference"* — **five things do, under the definition's
> own words.** What none of them does is clear its own noise, and the definition never asked them to.

Artifact: `results/r408_literal_test.json`, source-stamped.
