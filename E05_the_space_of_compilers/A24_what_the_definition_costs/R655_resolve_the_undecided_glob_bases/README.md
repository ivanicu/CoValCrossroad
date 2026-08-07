# R655 · 0 of 25 resolved, and the reason is that the remedy was aimed at a mechanism that is not there

**Decision this makes safe:** whether R654's census can be closed to a point value. **No — it ships
a bound permanently: `[94, 119]`, unchanged in width. And 11 of the 25 were never "undecided" at
all; they are mis-shaped.**

## The result, with its scope

| after one level of caller binding | n |
|---|---:|
| CORPUS-DEPENDENT · OWN-SCOPE · MIXED | **0 · 0 · 0** |
| **STILL-UNRESOLVED** | **25 (100%)** |

**The uncertainty's width went 25 → 25.** Population: R654's 25 UNRESOLVED-BASE rounds · instrument:
`ast` + a symbolic `pathlib` evaluator + one level of caller binding · baseline: R654's own
classification of the other **115** rounds, reproduced with **0 disagreements** · regime:
**tree `888e08f4`** — persisted in the artifact, the arc's own conclusion applied for the first time.

## ⛔ Why the residual survived — and it is not "the resolver failed"

**0 resolved AND the notes column empty for all 25: the interprocedural branch never found a
parameter to bind.** A zero with a *passing synthetic control* means the mechanism works and is
**absent** — a different fact from "it failed", and only looking at the bases tells them apart.

| shape of the blocking base | n | example |
|---|---:|---|
| **`glob.glob(...)` — the stdlib MODULE** | **11** | `glob.glob(str(ROOT / CENSUS))` |
| a `x / literal` expression | 5 | `(d / "results").glob("*.json")` |
| a function-**local** name (`RES`, `d`, `work`, `WT`, …) | 9 | `RES.glob("sat_*.npz")` |

⛔ **11 of 25 have no path base at all.** The classifier reads `Name(glob)` — a *module* — as a
path; their corpus-dependence lives in the **pattern argument**. **They are not undecided, they are
mis-shaped, and no amount of caller binding would ever decide them.** The other 14 are
function-local assignments, and `PathEval` binds only module-level names.

## ⛔ Check #256 — two clauses of R654's NEXT

| claim | truth |
|---|---|
| *"R653 showed **16 of 59 such bindings** are statically supplied"* | R653's 16 was the blocking **parameter of a D1 read site**. These are **glob bases**. **A number is not evidence for a question it was not asked.** |
| *"93 is an **undercount** by an unknown amount"* | **The direction was not known.** An undecided round can resolve OWN-SCOPE. The honest form is a two-sided bound. ⭐ *Naming an uncertainty is worth nothing if you also name its sign for free* — and in the event **0 went either way**, so neither side was right. |

## Controls

| control | returned |
|---|---|
| **positive-1** — reproduce R654 on all **115** already-decided rounds | **0 disagreements** — PASS |
| **positive-2** — a base bound to the collection dir at its only call site | **CORPUS** — PASS |
| **negative** — a base bound to the round's **own** dir | **OWN** — PASS, *not every resolved base is corpus-dependent* |
| **placebo** — a base never resolvably passed | **UNRESOLVED** — PASS, ⭐ *it stays undecided rather than being defaulted* |
| **g=0** — no glob at all | **UNRESOLVED** — PASS |

⭐ **The placebo is the one that earned its cost:** a resolver that defaults its failures into a
class turns an unknown into a finding, and the residual here is 100% — precisely the case where a
default would have manufactured an answer.

**MULTIPLICITY:** 1 resolver × 330 rounds (reproduction on 115, decision on 25) + 4 controls; the
residual is reported, never absorbed, and the shape census names every blocking form.

**IMPOSSIBLE, named:** a base bound from a parameter **two or more frames up** needs a call graph
across a corpus of standalone scripts, which does not exist.

⚠ **And this round is itself corpus-dependent** — it globs the collection directory, so R654's 93
reads as **94** here: R654 excluded itself from its own census and this round does not. **Corpus
growth, predicted this time, and the tree sha is in the artifact.**

## The sentence I can no longer write

> *"the 25 undecided rounds are undecided."*

**11 of them are mis-shaped** — measured against a rule that does not apply to `glob.glob`. The
census's residual is not one thing.

## NEXT

**The 11 `glob.glob(...)` sites are decidable and by a rule I already have**: their argument is
`str(ROOT / CENSUS)`-shaped, so the *pattern string* resolves with the same `PathEval` that the base
does. **Classify those 11 by their first argument rather than their receiver.** This is not more
interprocedural machinery — it is the recognition that two different APIs were being scored by one
rule, and it should shrink the residual from 25 to 14 without touching the hard cases. The remaining
14 need function-local binding, which is a different and larger change.
