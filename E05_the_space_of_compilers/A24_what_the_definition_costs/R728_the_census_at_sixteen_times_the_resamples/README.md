# R728 · the census at sixteen times the resamples

**The first round in this arc to go back to the object.** Every round from R680 to R727 read R294's
persisted summary; none checked that the summary is what the sat store yields.

## Result 1 — the extension is neither a resample-count nor a seed artifact
Re-running R294's construction from `corebench/results/sat_*.npz` reproduces its committed verdicts
on **41 of 41** arms exactly.

| B | admitted | equals committed | max \|Δ lo\| vs shipped |
|---|---|---|---|
| **1200** *(shipped)* | 5 | ✓ | — |
| 4800 | 5 | ✓ | 0.001354 |
| 19200 | 5 | ✓ | **0.001408** |
| 76800 | 5 | ✓ | 0.001181 |

**64× the resample count changes no admission.** Nor does the seed: 5 seeds at the shipped B, all
identical, with the seed flag verified to move the draws.

⛔ **And most of that is algebra, not evidence.** `mde = ZEFF·sd/√n` does not depend on B; only the
CI lower bound does. The single cell within Monte-Carlo reach of its CI boundary — `random_k8_s0`
clause 1, **t = 2.1458** — is already excluded by the B-invariant half. **Zero was forced.**
**What was NOT forced is the reproduction**, and that is the round's real content.

## Result 2 — ⭐ the census population is a directory glob, and it has grown
The anchor's failure surfaced this; it was not registered.

| | |
|---|---|
| arms in R294's committed census | **41** |
| arms the same glob returns today | **92** (new 51, absent 0) |
| re-running R294's own procedure over today's population admits | **16**, not 5 |

The 11 extra admits are `coval_core_2bA`, `coval_core_2bB`, `greedy_k4_greedy_kA/B`,
`indep_k4_indep_kA/B`, `oracle_k4_08bR`, `oracle_k4_oracle_kA` and others — **arms built by later
rounds for other purposes.**

⚠ **This is NOT a correction to the extension.** Whether those arms are admissible objects is a
separate question this round does not ask. What it establishes is that **the same procedure returns
a different answer depending on when it is run**, because its population is a glob over a directory
that subsequent rounds write into.

## ⛔ My anchor could not pass, and that is the sixth instance in this arc
v1 required `matched == len(V) = 92` when the ceiling is `|committed ∩ rebuilt| = 41`. **A threshold
above what the design can return under a perfect reproduction.** It reported `FAIL — measuring a
different object` while the reproduction was in fact exact on every arm the committed census
contains. Repaired by **computing** the ceiling: `floor 0 < t 41 ≤ ceiling 41`.

*The tell §4 gives is precise and was present: the control failed but nothing else about the run
looked wrong, and the failure did not localise to a mechanism.*

## Controls — 5 PASS, 0 FAIL
**ANCHOR**: 41/41, ceiling computed · **g=0**: same B, same seed → identical extension (else the
code is non-deterministic and nothing else is readable) · **NEGATIVE**: difference vectors rotated
across arms → extension becomes 20 arms, excluding *"admission is insensitive to which arm has which
data"* · **SHAM**: the B-invariant half alone (`|eff| ≥ mde`, CI **absent**, not inverted) → identical
at all 4 B levels, which is the derivation made visible · **PLACEBO**: committed set against itself
→ 0.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A at-risk cells ⛔ derivation | 1 [0, 82] | **1** | yes |
| B changes at B=19200 ⛔ derivation | 0 [0, 41] | **0** | yes |
| C changes from the **seed** alone | 0 [0, 41] | **0** | yes |
| D arms reproduced | 41 [0, 41] | **41** | yes |
| DIRECTIONAL identical at all B and seeds | — | **holds** | — |

## Residue
Whether R294's construction is the **right** one is not addressed here — that needs a different
definition, not a different resample count.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r728_census_rerun.json`; `results/_vectors.npz` (500 K) caches the difference
vectors so a later round can attack this in 2m40 instead of rebuilding for 4m30.
