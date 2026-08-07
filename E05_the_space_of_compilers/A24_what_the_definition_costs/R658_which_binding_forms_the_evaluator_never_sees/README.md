# R658 · The magnitude missed for the fourth time. The DIRECTION held — and my own bug had flattered the magnitude.

**Decision this makes safe:** whether to keep extending the evaluator's syntax. **No. Missing
syntactic forms are 3.2% of the residual; 85.7% are forms it already inspects whose right-hand side
does not resolve.**

## The number, with its scope

| | n | % |
|---|---:|---:|
| **HANDLED-FORM** — `Assign`/`For`, RHS does not resolve | **108** | **85.7%** |
| PARAMETER | 14 | 11.1% |
| **UNHANDLED-FORM** — `with` / comprehension / tuple-unpack / walrus | **4** | **3.2%** |
| UNBOUND | **0** | 0.0% |

Population: **126 unresolved (round, name) pairs** across **333** rounds · instrument: `ast` +
R657's evaluator unchanged · baseline: R657's 8 undecided rounds, all present · regime: tree
`508bf62a`.

## The pre-registration, written before any code

> **point 20% · interval [5%, 45%]** · **directional:** *the missing forms are NOT the blocker;
> handled forms with unresolvable right-hand sides will dominate* · **kill:** UNHANDLED-FORM > 50%
> retracts the directional prediction.

| | |
|---|---|
| **magnitude** | **3.2% — OUTSIDE [5%, 45%]**, error **−16.8 pts**. Fourth consecutive over-estimate. |
| **direction** | **HOLDS** — 3.2% ≪ 50%, and the kill could have fired. |

⭐ **The split is the finding: my magnitude estimates are unreliable and my directional ones have
been right.** A forecast has two failable parts and I have been reporting them as one.

## ⛔⛔⛔ And my own bug had put the estimate INSIDE the interval

Before the extraction repair the round measured **7.0% — inside [5%, 45%]. The pre-registration
would have passed on a broken instrument.** After the repair: 3.2%, outside.

> **Second time in this arc that fixing my own defect moved a number away from my forecast**
> (R656: 7 → 4). *Defects in my instruments have flattered my forecasts twice, in the same
> direction, and a passing pre-registration is not evidence the instrument was sound.*

## ⛔ Two extraction defects, both caught by controls, both systematic

| | defect | effect |
|---|---|---|
| ① | root-walk descended only `Attribute`/`Subscript`, so a **`BinOp` base** — `(d / "results").glob(...)`, the commonest shape here — fell through a `continue` | **dropped from the population entirely**; `POSITIVE-2` caught it because R337 vanished from its own population |
| ② | for a `Call` it took **the first Name in the subtree**, which for `str(ROOT / X)` is the **callee `str`** | **all 8 `UNBOUND` pairs were that artifact** — a class invented by an extractor, not observed in the corpus. After repair: **UNBOUND = 0** |

**The population more than doubled: 57 → 126.** *An extractor that silently skips a shape reports a
census of the shapes it likes.*

## ⛔ Check #259 — one clause of R657's NEXT is self-undermining

*"every remaining undecided round is now **labelled by mechanism** — `STILL-LOCAL` versus
`STILL-UNRESOLVED`."* **`STILL-UNRESOLVED` means "no binding found" — the absence of a mechanism.**
Measured: **3 of 8 carry one, 5 of 8 do not.** *A sentence that presents a residual bucket as a label
is how a residual stops being counted.*

✓ The other two clauses hold: `local_bindings` does handle only `Assign`/`For`, and the arc did
retract one structural limit (entry 651).

## Controls

| control | returned |
|---|---|
| **positive-1** — `with TemporaryDirectory() as t` | **UNHANDLED-FORM** — PASS, *the class is visible at all* |
| **positive-2** — R657's 8 undecided rounds present | **8/8** — PASS *(caught defect ① at 7/8)* |
| **negative** — a plain `Assign` from an unresolvable call | **HANDLED-FORM** — PASS, *not everything unresolved is a missing form* |
| **placebo** — a name with no binding anywhere | **UNBOUND** — PASS, *its own outcome* |
| **g=0** — a module whose base resolves | **RESOLVED** — PASS, contributes 0 names |

**MULTIPLICITY:** 1 classifier × 126 pairs + 4 controls; **all four classes and every form
combination printed**, including the two `(no binding site)`.

**IMPOSSIBLE, named:** whether extending the evaluator to a form would *resolve* the name depends on
what the form binds — a `with ... as tmp` binds a temp directory, runtime whatever syntax reads it.
**So 3.2% is an UPPER BOUND on what new syntax could buy, not a proof of a limit.**

## The sentence I can no longer write

> *"the residual might be a missing syntactic form."*

**It is 3.2%, and that is a ceiling.** The residual is right-hand sides — parameters, calls, runtime
data — which is where the impossibility register already points.

## NEXT

**`d` alone accounts for 75 of the 126 unresolved pairs — 60%.** It is a for-loop variable over an
iterable the evaluator cannot resolve, and it is one name in one idiom repeated across the corpus.
**Measure what those 75 loops actually iterate over**, because if a single iterable shape dominates
then 60% of the residual is one missing case rather than a structural limit — and I have twice now
declared a limit that a single mechanical fix would have moved. **This is the cheapest remaining
separator and it points at the opposite conclusion to the one this round just reached.**
