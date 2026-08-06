# R853 · does clause ② reward CONTENT or FORMAT? — **UNVERIFIED**, and the failure refutes R852

**Arc A24.** ⚠ **This round reports NO extension count. Its pre-registered kill fired.**

## ⛔ THE PREMISE, AND WHY κ WAS THE RIGHT INSTRUMENT FOR IT

R852 found that a **pair-label shuffle** — which destroys *which pair is which* but preserves each
prompt's marginal verdict mix — still leaves **14.3 of 99 arms** clearing clause ② on A2, while two
proper nulls give **exactly 0**. **I explained that as marginal-FORMAT agreement.**

Cohen's **κ** is *defined* to subtract the agreement expected from the two marginals alone. So the
explanation made a sharp, failable prediction, and it was pre-registered as the round's **key
control**: *under N1 the κ-extension MUST be ≈ 0.*

## ⛔⛔ THE KEY CONTROL FAILED — and that is the result

| | A2 (R851/R852) | **κ (this round)** |
|---|---:|---:|
| **REAL** | 29 | **30** |
| **N1 pair-shuffle** | **14.3** `[16,12,15]` | **15.7** `[18,14,15]` |
| N2 cross-prompt | 0.0 | **0.0** `[0,0,0]` |
| N3 uniform | 0.0 | **0.0** `[0,0,0]` |

**Placebo:** identically 0 by construction. **Positive:** `oracle_k4` satisfies ② under κ — **PASS**.

⭐ **κ removes marginal-expected agreement and the pair-shuffle count does not move — it rises
slightly.** ⛔ **So what survives N1 is NOT marginal-format agreement, and R852's mechanism claim is
refuted by the instrument built to confirm it.**

## ⭐⭐ WHAT N1 ACTUALLY IS — an ontology correction, stated as a hypothesis

**N1 is not a null at all: it is a comparison against a DIFFERENT BUT FIXED target.** Permuting the
six pairs produces a new well-defined per-prompt target — one that is generally not realisable by any
ranking, but is *the same target for every arm*, and is still **a function of this prompt**. Arms
whose outputs happen to align with it beat the comparator resolvably.

**N2 and N3 give 0 because they sever the prompt-level coupling entirely** — another prompt's
ranking, or a random one, has no relation to *these* responses. **N1 keeps it.**

⚠ **Stated as a hypothesis, not a finding**: this round's kill fired, so **it is entitled to report
its control and nothing else.** The mechanism above is `[HYPOTHESIS — untested]` and is what the next
round must separate.

## ⚠ WHAT IS RETRACTED AND WHAT IS NOT

| claim | status |
|---|---|
| R852: *"what survives the pair shuffle is marginal-format agreement"* | ⛔ **RETRACTED** — κ subtracts exactly that and the count is unchanged |
| R852: *"two proper nulls return exactly 0"* | ⭐ **STANDS** — reproduced here under κ, 3 seeds each |
| R852: *"R850/R851's excesses were artifacts of a bad null"* | ⭐ **STANDS** — N1 remains the wrong null; **why** it is wrong has changed |
| this round's content-vs-format verdict | ⚠ **NOT REPORTED** — the kill fired |

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| construct validated | an external gold standard for corehood |
| cross-release | a second release |

⚠ **N/A with what each would require — never "planned".**

⭐ **The round's value is that it could fail and did.** A control designed to confirm an explanation
refuted it instead, one round after the explanation was published — which is the only way a mechanism
claim in this project has ever been caught.
