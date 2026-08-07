# R1012 · the cut survives the imputation; the counts do not

**THE DECISION THIS MAKES SAFE.** Whether the number every round in this arc pins its wiring control
to — R922's cut, checked at 1e-9 — was set by arms whose A2 is 79% fabricated. **It was not.** The
counts beside it were.

---

## The recomputation

Same operator, same seed (921), same 8,000 draws. **One population change.**

| comparator | population | cut | n | argmin |
|---|---|---:|---:|---|
| `generic` | full | **0.5593110792** | 24 | `topw_k8` |
| `generic` | minus partial-coverage | **0.5593110792** | **22** | `topw_k8` |
| `genericpool16` | full | **0.5513543392** | 28 | **`generic`** |
| `genericpool16` | minus partial-coverage | **0.5513543392** | **26** | **`generic`** |

⭐ **Δ = 0.0000000000 under both comparators**, and the argmin is a full-coverage arm in each.
**The arc's calibration number is not an artifact of the imputation.**

⛔ **The counts are.** `24 → 22`, `28 → 26` — **two of each committed count are partial-coverage
arms** (`coval_core_2bA`, `_2bB` at 200/968). Any statement quoting *"24 admitted"* is quoting a count
with two imputed members.

## ⭐⭐ A cross-check nobody designed

Under `genericpool16` the argmin — **the arm that sets the cut** — is **`generic`**, the prompt-blind
arm R1009 found admitted. Two rounds, different routes, same object: **the arm that should not qualify
is the one defining the boundary.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | the full-population recomputation reproduces R922's cut **and** count at 1e-9 under **both** comparators. Without this, no difference below would mean anything |
| **PLACEBO** | excluding the **empty set** reproduces the full result exactly |
| **NEGATIVE** | excluding the two **highest-A2** arms (`oracle_k4`, `oracle_k4_oracle_kA` — never the argmin) leaves the cut **exactly** unchanged. This is what separates *"removing arms moves the cut"* from *"removing **these** arms moves the cut"* |

**Noise floor: n/a**, labelled — this is a recomputation, not an estimate. Seed and draw count are
held identical so the population is the only moving part.

## Why this round and not a broader sweep

A census over **1,229 committed artifacts** found **69** naming a partial-coverage arm, with
result-bearing fields among them (R921's `admitted_by_at_least_one_legitimate`, R978's
`full_admitted`, R992's `clause2_passers`, R1000's `conjunction`). ⭐ **The cut is the one that
propagates**, because every round's wiring control pins to it. Checking it first is the cheapest way
to find out whether the defect is bounded or systemic. **It is bounded.**

## ⚠ Impossible here

**Recomputing what the partial arms' A2 *would* be with real scores.** Those 768 prompts were never
scored for them — **that is the defect, not a gap in this round.** It would require scoring them on
the full corpus.

## Alternatives considered

**Re-run every one of the 69 affected artifacts.** Refused for now: the cut is the quantity the others
inherit, so it is the correct first target, and it came back clean. The remaining question is about
**counts**, which this round answers for the two that matter and names for the rest.

**Report "the imputation does not matter".** Refused — it does, to the counts, by exactly 2 arms per
comparator. The finding is that it does **not** reach the cut, which is a narrower and checkable claim.
