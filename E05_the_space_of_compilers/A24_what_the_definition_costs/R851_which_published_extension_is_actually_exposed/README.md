# R851 · which published extension is actually exposed — and what is it?

**Arc A24 — what the definition costs.**

## ⛔ MY OWN NEXT OVERREACHED, AND THE REFUTATION WAS ALREADY IN THE FILE

Entry 1370 closed with *"every extension this project has ever reported may carry a similar free
component."* The clause table at `DEFINITION.md:582-586` already classifies them:

| clause | excludes | evidence type |
|---|---:|---|
| **①** vs a draw of the prompt's own rubric | 0 of 41 | **DERIVED** — region empty by arithmetic |
| **②** vs a prompt-blind set | **33 of 42** | **MEASURED** |
| **③** no prompt labels | 14 of 42 | **DERIVED** — read from the source |
| **④** vs every criterion-free rule | 0 of 42 | **MEASURED** — excludes nothing |

⭐ **A DERIVED clause has no noise floor of R850's kind**: no selection, no interval, no BH, and
shuffling the target cannot move a count obtained by reading which arms consume labels. **④ strict
excludes 0, so it has no extension to inflate.** **Exactly ONE published extension was exposed — ②'s
— and the sweeping version of the worry was wrong.**

## ⭐ CONTROLS

| control | result |
|---|---|
| **PLACEBO** comparator vs itself | **+0.00e+00 · PASS** |
| **POSITIVE** `oracle_k4` satisfies ② | **True · PASS** |
| **NEGATIVE** `random_k4_s0` must not | **True · PASS** — ⚠ not a formality: this same control **failed for ④′ at 7 of 8 class sizes** in R850 |

⚠ **Population not intersected** (R850's bug, not repeated): per-arm sets, min 200, median 968.
⚠ **7 arms unreadable** (`transport_*` — a key shape `load_sat` cannot parse) **and 1 under 200
prompts, both counted and named.** An arm that cannot be read is not an arm that failed the clause.

## ⭐⭐ RESULT — world A

| | |
|---|---:|
| clause ② satisfied on the **REAL** target | **29 of 99** |
| on a **SHUFFLED** target | **16 of 99** |
| **EXCESS** | **13** |
| `coval_core` | **+0.0250 — SATISFIES** |

⭐ **②'s extension is roughly 55% free.** The clause this document calls *"carries the whole boundary
among label-free arms"* carries **13 arms of excess**, not 29.

## ⭐⭐⭐ AND THE TWO MEASURED CLAUSES NOW AGREE

| clause | real | noise | **excess** |
|---|---:|---:|---:|
| **②** — published | 29 | 16 | **13** |
| **④′** — my proposal (R850) | 41 | 30 | **11** |

**Both land in the low teens.** So the definition's *measured* selectivity is on the order of **11–13
arms per clause**, not the 29–41 the raw counts suggest — and **my proposal is neither better nor
worse than the clause it replaces on this axis.** That is a more useful thing to know than either
number alone.

## ⚠ WHAT IS NOT CLAIMED

- **The noise count is not an error rate.** It is what this **procedure** — comparator + BH +
  interval — admits on a target whose pairing has been destroyed.
- **This does not retract ②'s published 33 of 42.** That count is over R360's 42-arm space with a
  different comparator; this is 99 arms against `genericpool16`. **Different populations, reported
  as such.** What transfers is the *shape*: a measured extension carries a free component.
- **①  and ③ are untouched** — they are derived, and this critique does not reach them.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| construct validated | an external gold standard for corehood |
| cross-release | a second release |
| causally identified | an intervention on the compiler |

⚠ **N/A with what each would require — never "planned".**
