# R656 · The forecast said 11 would resolve. Four did — and fixing my own bug moved the number *away* from it.

**Decision this makes safe:** whether R655's residual decomposes into two independent fixes.
**No. The subsets overlap, and the residual is 21, not 14.**

## The pre-registered forecast, and its verdict

> R655's NEXT: *"it should shrink the residual from 25 to 14"* — i.e. **11 resolve.**

| | |
|---|---|
| **measured** | **4 resolve · residual 21** |
| verdict | **RETRACTED** — replaced by the measured number, not reinterpreted |

⭐ **And the number moved away from the forecast when I fixed my own bug.** The first run reported
**7**; stopping two residual-folds gave **4**. *Absorbing a residual flatters a forecast, and it does
so silently.*

## The 25, with the API dispatched

| | n | % |
|---|---:|---:|
| CORPUS-DEPENDENT | **2** | 8.0% |
| OUTSIDE-BOTH — resolves to neither the corpus nor its own dir | **2** | 8.0% |
| OWN-SCOPE · MIXED | 0 · 0 | — |
| **PARTIAL-UNDECIDED** — some sites decided, some not | **3** | 12.0% |
| **FUNCTION-LOCAL** — the base is assigned inside a function | **14** | 56.0% |
| STILL-UNRESOLVED | **4** | 16.0% |

Population: R655's 25 undecided rounds · instrument: `ast` + a symbolic `pathlib` evaluator
**dispatched on the call's API** · baseline: 306 already-decided rounds, **0 moved** · regime: tree
**`6375f9d4`**, persisted in the artifact.

## ⛔⛔ Two residuals were being folded into a decided class — in the round whose placebo forbids it

| | v1 printed | v1 returned | why |
|---|---|---|---|
| `R353`, `R354` | `ARG -> OTHER` | **OWN-SCOPE** | `OTHER` means *neither* corpus nor own. A wildcard like `E0*` never literally contains `E05_the_space_of_compilers`, so the prefix test fails — and the final `if seen` swept it into OWN. |
| `R390`, `R393` | `RECV unresolved` | **OWN-SCOPE** | a round with a decided site *and* an undecided one returned decided. **A round is decided only if ALL of its sites are.** |

> **The placebo I wrote for this round fires correctly in its own branch and both leaks were
> elsewhere.** A control guards the path it is pointed at, not the property.

## ⭐ The decomposition underneath R655's NEXT was wrong

R655 partitioned the 25 into **"11 easy (API) + 14 hard (function-local)"**. **5 rounds carry both**
— `R517`–`R521` all resolve their `glob.glob` argument from a lowercase `root` that is
function-local. **The subsets are not disjoint, so the residual does not split into independent
fixes.**

## ⛔ Check #257 — the premise was a generalisation from n=1

*"their argument is `str(ROOT / CENSUS)`-shaped"* was written from **one** example (R347). Checked
before use: **all 11 are `Call(str)` — the generalisation held.** It was still n=1 when written,
**and that is the habit, not the outcome.**

## Controls

| control | returned |
|---|---|
| **positive-1** — the dispatch must not un-decide any of the **306** already-decided rounds | **0 moved** — PASS |
| **positive-2** — `glob.glob(str(A24 / 'R*'))` scored by its **argument** | **CORPUS** — PASS |
| **negative** — `glob.glob(str(HERE / '*.json'))` | **OWN** — PASS, *a wide-LOOKING pattern is not automatically corpus-wide* |
| **placebo** — an argument base defined only **inside** a function | **FUNCTION-LOCAL** — PASS, *named, not reached into* |
| **g=0** — no glob at all | **NO-GLOB** — PASS |

**MULTIPLICITY:** 1 dispatching classifier × 25 rounds × every glob site + 306 reproduction checks
+ 4 controls; **all seven outcomes printed**, including the three zeros.

**IMPOSSIBLE, named:** a function-local base needs intra-procedural binding of assignments; a base
from a parameter needs a call graph that does not exist across standalone scripts. Neither attempted.

## The sentence I can no longer write

> *"the API mis-dispatch was the blocker for those 11."*

**It was the blocker for 4.** For 5 more it is one of *two* blockers, and the residual is now
**better characterised (14 named function-local) without being smaller.**

## NEXT

**14 of the 21 remaining are FUNCTION-LOCAL, and 12 of those bind a single name — `root`, `d`,
`work`, `RES`, `wt`, `p`, `s`, `st` — by a plain `X = <path expression>` assignment inside one
function.** That is intra-procedural binding of module-shaped assignments, not a call graph.
**Extend `PathEval` to bind function-local assignments in the enclosing scope and re-measure**, with
the same non-folding discipline: *a round decided only if every site is.* And **pre-register the
number before running it** — this round's forecast was wrong by 7 and the previous one by 11, so a
third estimate is worth recording precisely because my forecasts here have been poor.
