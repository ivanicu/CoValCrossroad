# R987 · the size reading is decided, and it needs no provenance

**THE DECISION THIS MAKES SAFE.** Which of the three readings of *"its size"* clause ① takes.
**Nominal size = the maximum realised size over prompts** — pool-independent by argument,
**artifact-recoverable by measurement (40 of 40)**. The definition has **exactly one** provenance
clause, not two.

---

## The choice had two constraints, and only one needed measuring

**① Pool capping is a property of the PROMPT** — R986 measured it: 28 of 34 variable arms explained
entirely, with every `k12`/`k8`/`k6` family sharing a byte-identical per-prompt profile. A definition
whose verdict moves because one prompt offered fewer criteria is answering a question about the
corpus. **The reading must quotient it out. Argument, not measurement — stated as such.**

**② Whatever survives must be recoverable from the artifact**, or clause ① joins ③ (R979) outside
what a third party can check. **That is measurable, and it is this round's estimand.**

## The measurement

| subset | `max_p size(p) == recorded k` |
|---|---|
| **trivial** (k ≤ min pool 4, never capped — vacuous) | 28 of 28 |
| **NON-TRIVIAL** (k > 4, the pool genuinely binds) | **12 of 12** |

⚠ **And it is partly a DERIVATION, labelled.** If realised size is `min(k, pool)`, the max equals `k`
whenever one prompt has `pool ≥ k` and the arm does not under-select there — forced by the capping
model R986 measured. **What is not forced** is whether it survives the six arms with a **residual**:

| arm | recorded | max | min | residual | `max == k` |
|---|---|---|---|---|---|
| `coval_core` | 4 | 4 | 2 | 43 | **True** |
| `coval_core_sham` | 4 | 4 | 2 | 43 | True |
| `gen` / `gen_sham` | 4 | 4 | 1 | 2 | True |

**The under-selection does not lower the maximum.** That is the part the algebra did not hand me.

## Controls

| control | result |
|---|---|
| **POSITIVE** | the non-trivial subset is non-empty — **12 arms** where the pool actually binds, so the test is not vacuous |
| **NEGATIVE** | `full` (no nominal k) is excluded **by classification, not by name** — R986's object-based rule |
| **PLACEBO** | `topw_k1`: nominal 1 against a minimum pool of 4, max == 1 exactly |
| **REPRODUCIBILITY** | two runs byte-identical (`3590aad3…`) |

⭐ **The trivial subset is reported separately and does not count toward the verdict.** 28 arms whose
k ≤ the minimum pool can never be capped, so `max == k` is true of them for no reason. Folding them
in would have made the headline "40 of 40" rest on 28 vacuous cells.

## What landed in the statement

Registered in the currency gate and checked **red first** — both facts genuinely absent at HEAD —
then written into `DEFINITION.md`:

| gate | before → after |
|---|---|
| currency | **1 → 0** (now 14 facts) |
| anchoring, 343 assertions | **0 → 0** — annotated, not edited (L81) |

The annotation records the ambiguity, its two causes, the adopted reading **with both its reasons
labelled by kind**, and that `gen`'s verdict turns on it while `coval_core`'s does not.

## What this does not settle

- **Recoverability says the reading CAN be checked, never that it is right.** The remaining choice —
  *whether SIZE is the right property for a definition of `core` at all* — stays authorial and is
  recorded as open in the statement.
- **One release.** On a corpus whose pool is uniformly large, `max == k` would hold trivially and
  this test would have no non-trivial subset at all.

## Alternatives considered

**Adopt "min per-prompt size" as the strictest reading.** Refused on the argument in ①: it makes
`gen` fail clause ① because two prompts of 968 offered fewer criteria — a verdict driven by the
corpus, not the arm.

**Leave the reading open and report the three.** Refused: R986 already did that, and its NEXT said
the danger is the question being settled by whichever reading a later script implements. Leaving a
decidable part open is how that happens.
