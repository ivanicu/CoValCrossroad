# R1034 — ②′ is **vacuous** once its comparator set is closed and its operator repaired

**The decision this round makes safe:** whether closing the certified set is a *repair* or a
*refutation*. It is a refutation — **the extension is empty**, and emptiness is exact.

## ⛔ Two derivations, before any compute

1. **②′ requires beating EVERY member**, so under a **closed** set an arm is admitted iff it beats the
   **strictest** member. Closure under R918's `fixed` contains **all 65,535** subsets of pool16's
   criteria, every one already scored (R1033).
2. **Sampling is sound in one direction.** Adding comparators can only **remove** arms, so a sampled
   extension is a **superset** of the true one. **Emptiness is identified; survival is not.**

## Result — ⭐ **World B**

| operator | extension over 4,261 sampled checklists (3 seeds) |
|---|---|
| committed (**imputing**) | `coval_core_2bA`, `coval_core_2bB` — **and `coval_core` is not among them** |
| **R1024-repaired** (no imputation) | **∅** |

Both survivors under the imputing operator are the **twins**, whose A2 is **79% imputed** (R1021) and
which **R1011 already withdrew**. Apply R1024's repair — bootstrap only the prompts an arm actually
covers — and **nothing survives.**

⭐ **So ②′∧③ admits nothing once its own certification predicate is closed AND its own operator repair
is applied.** The 9-arm extension exists only because the set was never closed. **Emptiness is exact:
the remaining 61,274 comparators could only remove more.**

## Controls

- **POSITIVE — three committed anchors** through the vectorised path: full 16-mask = `genericpool16`
  **28**, `generic` **24**, R1033's strictest k=2 **17**. All **PASS**; any drift in the matrix form
  breaks them.
- **NEGATIVE** — enlarging by a member **already present** must change nothing: `{generic,
  genericpool16}` reproduces R1000's extension of **9**: **PASS**.
- **PLACEBO** — a one-member closure of `generic` reproduces its own admitted set: **PASS**.
- **SEEDS** — 3; ∅ under all three.
- **SAMPLE** — pre-registered **by size and seed** (all sizes 1–16, 400/size at seed 77), never by
  outcome, and the direction of the bound was stated **before** the number.
- **Coverage split** — 92 arms full, 4 partial (`coval_core_2bA/B`, `promptecho`, `promptecho_sham`),
  reported rather than silently handled.

## Why this is not R1002 re-run

R1002 is the same structural question **one clause over**: it found clause ④'s reference class **not
closed** and recorded *"a max over a superset is ≥ a max over a subset — only the MAGNITUDE is
empirical."* Its stated limitation: *"says the class is not closed, never that a closed class is
achievable."* **For ②′ that is answerable, because closure is enumerable — and this is the answer.**

## N/A

The exhaustive 65,535-mask closure with a full bootstrap is **~254 GFLOP per seed**. **What it would
require:** the matrix form at float32 on the GPU. The sampled bound is reported instead, in the
direction where sampling is sound.

`run.py` · `results/closure_satisfiability.json`
