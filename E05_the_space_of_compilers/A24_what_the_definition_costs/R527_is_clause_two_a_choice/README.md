# R527 · Clause ②'s baseline is a choice, and the arms robust to it are the ones ③ excludes

**Decision this makes safe:** whether the definition's extension survives the arbitrariness of
②'s comparator, and with what scope the released core's admission may be stated.

**Estimand:** for each k=4 arm, the percentile of ②'s own reference class at which it stops
clearing ②. **Population:** the 16 k=4 arms with full coverage in R294's census.
**Instrument:** A2 over all annotators, paired cluster bootstrap, exactly R294's.
**Baseline:** ⭐ **the swept axis.** **Regime:** first release, home judge, 968 prompts.

## The specification curve

| baseline | A2 | n | admitted |
|---|---|---|---|
| **p0** | 0.5144 | **8** | + `gen` |
| p5 · p25 · p50 | 0.5242–0.5391 | **7** | + `generic` |
| p75 · p95 · **PUBLISHED (0.5504, pct 93.7)** | 0.5446–0.5511 | **6** | `coval_core`, `topw_k4`, + the four below |
| **p100** | 0.5575 | **4** | `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` |

**WORLD B — the extension moves from 4 to 8 across the class.** The published pick is `POOL[0:4]`,
chosen by **file order**, and it lands at **percentile 93.7** — a strict, conservative comparator.

## ⭐⭐⭐ The sharp finding

**The four arms admitted at EVERY specification are exactly the four ③ excludes.** The label-readers
are baseline-robust *because* they read the answer. **Every arm whose admission is contingent on the
pick — `coval_core`, `topw_k4`, `generic`, `gen` — is a ③-admissible one.**

⭐ **`coval_core` clears ② at 7 of 8 specifications**, failing only against the single strongest of
1,820 subsets — and per §4, a max over 1,820 draws is an extreme order statistic, so **comparing to
it is over-strict**. The released core's admission is robust; its *scope* is not "beats the
prompt-blind pool" but **"beats it at every baseline below the maximum of the reference class."**

## Controls
- **Positive** — the sweep must be on R294's scale: **16/16** k=4 arms reproduce R294's stored `c2`
  at **Δ ≤ 1e-6**. PASS.
- **Negative** — a subset against itself: max |d| = **0.0e+00**. PASS.
- ⚠ **The first version of this round FAILED its own positive control and returned UNVERIFIED**,
  because it targeted R439's `published_ref_a2` = 0.5537. **That is a different annotator draw.**
  This round's 0.5504 is exactly R514's measured bar₂ maximum, i.e. R294's all-annotator scale.
  **The control was comparing two different objects — failing for its own reasons.**
- **Multiplicity** — 128 cells over 8 specifications, whole grid printed.

## What the formulation owes

**②'s "best generalising prompt-blind criterion set" hides a choice.** The record should say which
subset, that it was picked by file order, and that it sits at p93.7 of its class.

**Impossible here:** whether the pool's 16 criteria are the right universe at all — a construct
claim needing an external standard for what "prompt-blind" should span.
