# R1109 — **0 of 42** cells admit. The fitting-protocol clause has **no possible beneficiary in this release**, and the repair was verified LIVE before the zero was read.

**The decision this round makes safe:** whether R1108's structural result is exhaustive. **It is.**
The one rule the protocol repair could have helped is admitted at no k, under no judge, under either
specification — and the intervention demonstrably happened.

## ⭐ The derivation that picks the candidate, over three committed artifacts

| rule | in ③ leakage list | in ③ authorship list | consumes human ratings (R1101) | consumes target (R1100) | repair live? |
|---|---|---|---|---|---|
| **`topvar_k`** | ❌ | ❌ | **❌** | ❌ | **✅** |
| `topwvar_k` | ❌ | ❌ | ✅ | ❌ | ✅ |
| `topw_k` | ❌ | ❌ | ✅ | ❌ | **no-op** (satisfaction-blind) |

⭐ **`topvar_k` is the unique rule in the release that is clean under *both* readings of clause ③ and
has a live fitting-protocol repair.** `topw_k`'s repair is a no-op by construction; `topwvar_k` reads
the human importance ratings. **Labelled as a derivation** — it is set arithmetic over R1094, R1100
and R1101, not a measurement.

⛔ **And `topvar_k` had only ever been built at k = 4** — one cell of a rule whose entire mechanism is
that `k` controls how much satisfaction spread it can exploit.

## ⭐ The result — 63 cells, all reported

| | admits |
|---|---|
| **`topvar_k`** × 7 k × 3 worlds | **0 of 21** |
| **`topwvar_k`** × 7 k × 3 worlds | **0 of 21** |
| `topw_k` (contrast) under **2B** | k = **3, 4, 6, 8** — exactly R1105's committed set |
| `topw_k` under either 8B world | 0 |

**59 of 63 cells do not admit.** The four that do are the contrast, and they land on the committed
answer — so the operator is not blind and the zeros are measurements.

## ⭐⭐ The kill is a measurement, not a construction — the load-bearing control

A zero obtained because the intervention never happened is not a zero. So the round required the
repair to be **live** for the candidate before reading its result:

| rule | `_08b` == `_08bR`, per k |
|---|---|
| `topw_k` | **True at all 7 k** — the placebo; satisfaction-blind, so the repair cannot move it |
| **`topvar_k`** | **False at all 7 k** — the repair genuinely changes the arm |
| `topwvar_k` | **False at all 7 k** |

**`topvar_k`'s re-scored and re-run files differ at 7 of 7 k values, and it is admitted in none of
them.** The intervention happened and bought nothing.

## Controls — 6, all green

| control | result |
|---|---|
| POSITIVE `topw_k` is admitted under 2B at k ∈ {3,4,6,8}, matching R1105 | PASS |
| REBUILD `topw_k4` and `topvar_k4` `_08b` reproduce the committed npz byte-for-byte | PASS |
| PLACEBO `topw_k` `_08b` == `_08bR` at **every** k | PASS |
| INSTRUMENT the analytic bound equals the 4,000-draw bootstrap on a live cell | PASS |
| **NEGATIVE the repair is LIVE for `topvar_k`** — its two specs differ at some k | PASS (all 7) |
| **COMPLETENESS every one of the 63 cells was actually built** | PASS |

⛔ **The completeness control exists because the first run needed it.** My harness omitted the
`--tag-suffix` for the 2B world and then looked for a suffixed filename, so **all 21 2B cells
silently failed to build and 14 candidate cells were counted as "does not admit" having never been
written.** The round **exited 2** rather than publishing that zero — the POSITIVE control asks whether
`topw_k` is admitted under 2B and it could not be. §4's *empty population passes*, caught by the gate
and now made explicit as its own control.

## What this closes

| round | after R1109 |
|---|---|
| **R1107** | proposed the protocol repair off its negative control |
| **R1108** | showed the repair recovers only ③-excluded arms, **structurally** — no-op for blind rules, undefined for fixed texts |
| **R1109** | **exhaustive**: the one rule for which the repair is live is admitted in 0 of 21 cells. There is nothing left for the clause to help |

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| a rule reading satisfaction, no target and no ratings, **other than `topvar_k`** | **N/A** | the release ships one. A rule invented here would be graded by a benchmark it was designed against |
| `oracle_k`/`greedy_k` across this k grid | **N/A** | out of scope: they consume the target and are excluded by ③ under both readings, which is what R1108 measured |
| whether either judge is **correct** | **N/A** | an external gold standard |
| cross-release | **N/A** | a second release |

`run.py` · `results/protocol_beneficiary.json`
