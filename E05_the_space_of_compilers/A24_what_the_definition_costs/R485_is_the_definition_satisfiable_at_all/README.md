# R485 · Is the definition satisfiable at all?

**The decision this made safe.** The extension is 0 (R475) and ③ costs nothing to keep (R477). Both
are facts about the *release*. Neither asks what a definition lives or dies by: **can anything satisfy
it?** An empty extension because the world happens to contain no member is fine. **An empty extension
because the clauses conflict is a defect.** They conflict.

## The estimand

`GAP = max{ A2(a) : a is ③-admissible AND prompt-aware } − CEILING`, where CEILING is R478's
**cross-fitted** best prompt-blind 4-subset (**0.5404**) — not its in-sample max, because ② says *the
best* prompt-blind set and a max over 1,820 is an order statistic.

⚠ **Prompt-aware is the load-bearing restriction.** A prompt-*blind* arm cannot satisfy ② against the
prompt-blind class — it is a member of it, so the comparison is degenerate. `generic`,
`genericpool16` and `promptecho` are therefore excluded from the numerator and reported separately.

| arm | A2 | ③ | prompt | clears ceiling + floor |
|---|---|---|---|---|
| `oracle_k4` | **0.6282** | EXCLUDED | aware | **YES** |
| `greedy_k4_fit1` | **0.6071** | EXCLUDED | aware | **YES** |
| `indep_k4_fit1` | **0.5915** | EXCLUDED | aware | **YES** |
| `coval_core` | **0.5640** | EXCLUDED | aware | **YES** |
| `topw_k4` | **0.5618** | EXCLUDED | aware | **YES** |
| `generic` | 0.5505 | admissible | *blind* | no (and degenerate) |
| `genericpool16` | 0.5416 | admissible | *blind* | no (and degenerate) |
| **`gen`** | **0.5337** | **admissible** | **aware** | **no** |
| `full` | 0.5077 | admissible | aware | no |
| `topwvar_k4` | 0.5023 | EXCLUDED | aware | no |
| `random_k4_s0` | 0.4920 | admissible | aware | no |
| `topabs_k4` | 0.4887 | EXCLUDED | aware | no |
| `topvar_k4` | 0.4854 | admissible | aware | no |
| `promptecho` | 0.4540 | admissible | *blind* | no |

**GAP = 0.5337 − 0.5404 = −0.0067**, inside the 0.0122 floor.

## The finding

**Every arm that clears the prompt-blind ceiling is one ③ excludes.** Five of five. The routes are
reading the prompt's **rankings** (`oracle`, `greedy`, `indep`), reading its **ratings** (`topw`), or
being built by a pipeline that does (`coval_core`, R475).

⛔ **② and ③ pull against each other.** On this site, the only way anyone has beaten the best
prompt-blind set is by consuming the human labels ③ forbids. **The extension is 0 not because the
release omits a member, but because the clauses conflict.**

⭐ **And the sharper half:** the best rating-blind *prompt-aware* arm (`gen`, 0.5337) is
**indistinguishable from a set that never sees the prompt at all** (`generic`, 0.5505;
cross-fitted class 0.5404) — the gap sits inside the floor. **Seeing the prompt, without reading what
humans said about it, buys nothing measurable here.**

## Controls

| control | returned | why it matters |
|---|---|---|
| **POSITIVE ⭐** — some ③-EXCLUDED arm clears the ceiling | **5 do** | makes the admissible null **evidence**, not silence: the bar is demonstrably reachable |
| g=0 — `random_k4_s0` must not clear | 0.4920, no | a bar a random arm clears is not a bar |
| PLACEBO — `topw_k4` vs shuffled rankings | **0.4309** ≈ chance 0.428 | |
| SCOPE — prompt-blind admissible arms held out of the numerator | 3 named | their comparison against their own class is degenerate |

## Scope

968 prompts (the `genericpool16`-covered population, as R477/R478 — **not** R479's 1,078, so levels
here are not comparable to that round's). Qwen3.5-2B only: **five admissible arms have no `_08b`
build**, so the second judge cannot host this comparison. That is a limit, not a result.

⚠ **What this cannot show:** that ②∧③ is unsatisfiable *in principle*. That would require enumerating
all prompt-aware rating-blind selectors, which is not a finite object. **This bounds what has been
built here** — which is what the definition's author can act on.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R485_is_the_definition_satisfiable_at_all/run.py

Compute-free · deterministic (crc32) · artifact `results/r485_satisfiability.json`.
