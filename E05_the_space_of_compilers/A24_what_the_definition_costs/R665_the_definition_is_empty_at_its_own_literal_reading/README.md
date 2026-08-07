# R665 · `② ∧ ③` is EMPTY at the definition's own literal reading — and it needed no new compute

**Decision this makes safe:** what the live definition actually admits. **Read literally, nothing.
Its non-emptiness is purchased entirely by the baseline choice.**

## The extension curve — the object-level deliverable

| baseline percentile | ② admits | **② ∧ ③ admits** | the survivors |
|---|---:|---:|---|
| p000 | 8 | **4** | coval_core, gen, generic, topw_k4 |
| p005 · p025 · p050 | 7 | **3** | coval_core, generic, topw_k4 |
| p075 · p095 | 6 | **2** | coval_core, topw_k4 |
| **published (93.74)** | 6 | **2** | **coval_core, topw_k4** |
| **p100 — the class MAXIMUM** | 4 | **0** | — |

> ⭐⭐⭐ **At the class maximum, ②'s four admitted arms are EXACTLY the four clause ③ removes:**
> `greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1`. **The intersection is empty.**

**And `coval_core` is excluded by ② itself at p100** — the released core fails its own definition
read literally, because ② at the maximum selects for arms with **privileged access** (fitted *or*
oracle), which the released core does not have.

⚠ **Could this have come out otherwise?** **Yes** — ② admits 4 and ③ removes 4 out of a 42-arm
space; partial overlap was the likelier outcome. **This is a measurement, not a derivation.**

## ⭐ Zero new compute — and the second consecutive round with that property

P4's prior-art gate, run before any code:

| source | committed | supplies |
|---|---|---|
| **R527** `clause2_spec_curve.json` | 138 rounds ago | ②'s extension at 8 percentiles |
| **R442** `r442_extension.json` | ~223 rounds ago | ③'s removal set |
| **R440** `r440_one_space.json` | ~225 rounds ago | ③'s removal set, independently |

**R664's object fact came from R527. R665's came from R442 and R440.** *Two consecutive object-level
answers were already on disk while 24 rounds went to the apparatus.*

## Controls

| control | returned |
|---|---|
| **positive** — R442 and R440 are independent rounds; removal sets must be identical | **identical** — PASS |
| **g=0** — an empty removal set would make the intersection trivially ②'s own | **\|removal\| = 4** — PASS |
| **negative** — ③'s removal must NOT coincide with ②'s **published** admitted set | published 6 vs removal 4, **not identical** — PASS, *the coincidence is specific to p100* |
| **placebo** — an arm in neither set (`topw_k1`) | **in neither** — PASS |

**MULTIPLICITY:** 2 artifacts × 1 removal set + 8 percentiles + 3 controls; **the whole curve
printed**, including the four cells where the definition is non-empty.

## ⛔ Check #266 — the fact held, one word did not

R664's NEXT: *"the literal reading of 'the best' selects for **fitting**."* ⛔ **Imprecise, and the
imprecision matters:** `oracle_k4` carries no `fit1` marker — **it is an ORACLE arm, not a fitted
one.** Fitting and oracle access are different mechanisms. **The correct statement is that ② at p100
selects for PRIVILEGED ACCESS — fitted *or* oracle** — which is wider and stronger.

**IMPOSSIBLE, named:** **why** ②'s top-ranked arms are exactly ③'s removals is not decided here. It
needs the arms' **construction**, not their scores — and it is the obvious next question.

## The sentence I can no longer write

> *"`② ∧ ③` defines a core."*

**At its own literal reading it defines the empty set.** What it defines at the published baseline is
a two-element set — `coval_core` and `topw_k4` — and the second element is a plain top-weight
baseline, not a core.

## NEXT

**The definition admits exactly two objects at the published baseline, and one of them is
`topw_k4` — a top-weight arm with no core-construction at all.** §4's `name an admissible object
this clause EXCLUDES` inverted: **name what the definition ADMITS that is not a core.** `topw_k4` is
that object, it has been in the extension at every percentile from p000 to p095, and no clause
removes it. **Measure what would.** Because a definition whose extension is {the instance, a
baseline} is a definition with one real member and one witness that the clauses are too weak — and
that is the last structural question this definition has left.
