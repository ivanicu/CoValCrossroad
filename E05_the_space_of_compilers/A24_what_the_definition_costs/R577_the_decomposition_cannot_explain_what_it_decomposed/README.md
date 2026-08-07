# R577 · The decomposition cannot explain the thing it was decomposed from

**Decision this makes safe:** stop decomposing the cap. **The line is closed.**

⛔ **DERIVATION, not a measurement.** Per-spawn cost is `secs ÷ spawns` on two numbers already in
hand. **It cannot come out otherwise** — §0's arithmetic trap, caught before running anything.

| gate | caps | secs | spawns | s/spawn |
|---|---|---|---|---|
| `attack_scope_reaches_the_reader` | no | 0.20 | 5 | **0.040** |
| `attack_every_check` | no | 1.50 | 11 | **0.136** |
| `attack_outcome_variable_declared` | no | 3.94 | 5 | **0.788** |
| `attack_no_withdrawn_framings` | no | 6.18 | 7 | **0.883** |
| **`what_did_each_check_actually_read`** | ⏱ yes | 25.0† | 60† | **0.417** |
| `attack_the_suite` | ⏱ yes | 25.0† | 22† | 1.136 |
| `backfilled_findings_are_rederivable` | ⏱ yes | 25.0† | 9† | 2.778 |

**A capper sits at 0.417 while two non-cappers sit at 0.788 and 0.883. Per-spawn cost does not
separate.** († both numerator and denominator truncated at the window, so this ratio is not even a
clean bound — reported anyway, because the overlap does not depend on it.)

## ⭐⭐⭐ The finding
**Fleet size does not separate *(R576)*. Per-spawn cost does not separate *(here)*. Their product is
`fleet × cost = total time` — which is what R571 measured and which separates by construction.**

**I spent three rounds factoring a measurement and asking which factor explained it.** Neither does,
and neither could have on its own: **the product was the observation.** A decomposition inherits all
of its explanatory power from the thing decomposed and can only redistribute it.

⚠ **What this does NOT establish:** that no property separates the two groups. Only that **these two
factors, which exhaust the product, do not** — and that any further factor must come from outside
the `time = fleet × cost` identity.

## Controls
- **The overlap is its own control**: it is a strict inequality between measured values on the same
  scale, and it holds regardless of the truncation caveat.
