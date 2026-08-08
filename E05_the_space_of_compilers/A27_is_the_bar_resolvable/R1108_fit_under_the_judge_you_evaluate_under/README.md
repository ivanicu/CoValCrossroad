# R1108 — refitting recovers **4** arms, and **all 4 are the ones clause ③ excludes**. After ③ it is **0** again. The protocol repair is available only to arms the definition already refuses.

**The decision this round makes safe:** whether R1105's `8B → 0` is a fact about the **judge** or an
artifact of the **fitting protocol**. **Neither reading survives intact.** The protocol does recover
admission — but only for arms that recover it by fitting harder to the target, which is the one thing
clause ③ forbids.

## The three worlds, same 43 arms, same operator, same comparators

| world | admitted | members |
|---|---:|---|
| **2B judge** | **9** | `coval_core`, `greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4`, `oracle_k4_fit1`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` |
| **8B, re-scored** (`_08b` — R1105's cell) | **0** | — |
| **8B, refit** (`_08bR` — fitted under the evaluating judge) | **4** | `greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4`, `oracle_k4_fit1` |
| **8B refit, after clause ③ leakage** | **0** | — |

⚠ **The kill clears by exactly its threshold** — 4 against a pre-registered `≥ 4` (R978's band). On
its own that would be a boundary call. **The second column is what decides**, and it was
pre-registered in the same breath precisely because a recovery made of leaky arms is not a recovery.

⭐⭐ **All four returning arms are target-fitting rules.** `oracle`, `greedy` and `indep` are exactly
the rules R1094's leakage list excludes. **Refitting recovers admission by fitting harder to the
target under the new judge** — so world B is *technically* true and *practically* empty.

## ⭐ And the reason no legitimate arm can return is a DERIVATION, verified byte-for-byte

`select_core.py`'s help states the re-scored and re-run specifications **coincide exactly** for the
satisfaction-blind rules. This round checks it rather than citing it: **`_08b` and `_08bR` are
byte-identical (`meta` and `sat` both `array_equal`) on all 27 satisfaction-blind arms in the
population.**

**So for `topw`, `topabs`, `random` and `full`, the protocol repair is a no-op by construction.** And
`coval_core`, `gen`, `promptecho` and the comparators are fixed criterion texts — re-running *is*
re-scoring for anything that fits nothing.

⛔ **Therefore the fitting-protocol repair is structurally available only to arms clause ③ excludes.**
The definition's legitimate candidates are precisely the ones for which refitting changes nothing.

⚠ **This also retro-validates the axis R1105, R1106 and R1107 all rest on.** Those rounds distinguish
`_08b` from `_08bR` and read consequences off the difference. The identity check confirms the
distinction is exactly where the release says it is — nowhere for blind rules, somewhere for fitted
ones.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE the 2B world reproduces R1105's committed **9-arm set by name** | PASS |
| **PLACEBO `_08b` == `_08bR` byte-for-byte on all 27 satisfaction-blind arms** | PASS |
| REBUILD two committed `_08b` cells reproduced byte-for-byte | PASS |
| INSTRUMENT the analytic inner bound equals the 4,000-draw bootstrap on the 2B world | PASS |
| NEGATIVE the refit world **differs** from the re-scored world | PASS |

**The negative control matters here more than usual**: if refitting had changed nothing, the round
would have been comparing a set with itself and the `0 → 4` would have been impossible to read.

## What this does to the previous three rounds

| round | said | after R1108 |
|---|---|---|
| **R1105** | the definition admits 9 under 2B and **0** under 8B | **the 0 is protocol-sensitive**: 4 return when candidates are fitted under the evaluating judge — and **0 of those 4 survive clause ③** |
| **R1107** | the greedy deficit reverses under refit at 4 of 4 doses | **holds, and is now placed**: the reversal buys admission only for arms ③ removes |
| **R1106** | 5 of 9 flips are compression, `coval_core`'s among them | **untouched.** `coval_core` is not rebuildable, so its cell is the same in both 8B worlds |

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| a refit cell for `coval_core`, `gen`, `promptecho`, the shams, the comparators | **N/A** | a generator; they are fixed criterion texts and re-running **is** re-scoring for an arm that fits nothing — **not a gap, a derivation** |
| a legitimate (③-surviving) arm that benefits from refitting | **N/A structurally** | a rule that consumes satisfaction but **not** the target; the release ships `topvar_k` and `topwvar_k`, and neither is admitted under either judge |
| whether either judge is **correct** | **N/A** | an external gold standard |
| cross-release | **N/A** | a second release |

`run.py` · `results/refit_admitted.json`
