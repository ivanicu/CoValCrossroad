# R640 · The repair is 5 sites, not 7 — and my two size claims were wrong in opposite directions

**Decision this makes safe:** how large the prohibition's installation actually is. **Five sites.**

| harness | rc compared? | fail var? | reaches output? | **classifies** |
|---|---|---|---|---|
| R319 | ✓ | ✓ | ✓ | **YES** |
| R322 | ✓ | ✓ | ✓ | **YES** |
| R388 | ✓ | ✓ | ✓ | **YES** |
| **R390** | ✓ | ✓ | ✗ | no |
| **R394** | ✗ | ✓ | ✓ | no |
| R396 | ✓ | ✓ | ✓ | **YES** |
| R636 | ✓ | ✓ | ✓ | **YES** |

**R390 forms the judgement but never emits it; R394 never compares a returncode at all.** Editing
either would change nothing.

## ⭐ The pattern this arc keeps producing, now with both ends measured
| claim | measured |
|---|---|
| *"only one harness runs rounds"* | **7** |
| *"one predicate and seven call sites"* | **5** |

**Wrong in opposite directions, two rounds apart, about the same object.** ⭐ *Neither error was
toward caution — one understated the scope by 7×, the other overstated the work by 40%. There is no
safe direction to guess in; there is only measuring.*

## Controls
| control | returned |
|---|---|
| **positive** — R636, which computes `failed` and branches on it | **classifies** — PASS |
| **g=0** — a harness that never compares a returncode | **R394 excluded** — PASS, the marker can exclude |
| **negative** — a marker appearing only in a docstring | **stripped via AST** — PASS |
| **placebo** — a marker no harness uses | **0** — PASS |

⭐ **Docstrings are stripped by AST before scanning**, because every round in this corpus writes
`fail`, `unrunnable` and `returncode` into its prose — **the marker would have matched all seven on
documentation alone.**

**MULTIPLICITY:** 7 harnesses × 3 markers + 4 controls. Full per-harness table printed.

**IMPOSSIBLE, named:** **classification could be implicit in a consumer this scan never reads**, so
5 bounds the repair from **BELOW**, not above.

## ⛔ Check #241
*"Six of the seven predate **this arc**"* — **false; all seven are in A24.** What I meant was
*predate the R630s*. Twenty-seventh, and the same class as the last four: **a claim about my own
corpus written from narrative position rather than from the object.**

## The sentence I can no longer write
> *"the prohibition is one predicate and seven call sites."*

**Five.** And the two harnesses excluded were excluded for **different reasons** — one never emits
its judgement, one never forms it.

## NEXT
Five sites is small enough to repair and verify in one round, but **R319, R322, R388 and R396 all
predate the R630s and their conclusions are committed** — so the repair changes what their code
would say without changing what their artifacts do say. **Before editing, re-run those four under the
prohibition and diff only their failure counts**, because if none of the four counts changes, the
repair is preventive rather than corrective, and that distinction belongs in the commit body rather
than being discovered by whoever reads it next.
