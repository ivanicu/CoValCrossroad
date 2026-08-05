# R701 · what formulation the audit supports — **PRODUCTION**

**⭐⭐⭐ Of 5 clause-positions, **1 survives unchanged** (③). The formulation the audit supports is
**three clauses**: provenance at a named judge, behaviour above a prompt-blind floor, and size as a
bound. **It is now in `STATEMENT.md`.****

## WHY THIS ROUND, AND WHY IT IS LABELLED PRODUCTION
The drift audit returned **five consecutive corpus rounds** at the tail, and **all seven** object
findings were already landed. **The arc had produced a thorough critique of the definition and never
a formulation informed by it** — which is what the standing task asks for. ⚠ **This executes a
decision the audit already made; it separates no live worlds.** §0 permits production when it traces
to gated decisions, and every constraint cites the round that established it.

## THE FIVE CONSTRAINTS, EACH FROM A COMMITTED ROUND

| | from | constraint |
|---|---|---|
| **C1** | R689 | the release ships **one** core; the card gives the **instance's** size → **no clause may name a k** |
| **C2** | R696 | **② IS an A2 threshold** → no clause may be justified by agreement with A2 |
| **C3** | R694 | 95.2% of the discriminating power is **(family, k)** — parameters we chose; the residual is the sham |
| **C4** | R688 | **③ survives §4's falsifier** on the reachable population |
| **C5** | R683/R685 | the ③ separation is **judge-dependent, on n = 1** |

## WHAT SURVIVES

| clause | verdict |
|---|---|
| ① | stays retired |
| **②** | **survives RESCOPED** — the clause stands, **its justification does not** |
| **③** | ⭐ **survives unchanged**, with a scope condition |
| ④ | stays retired |
| size | **must state a bound, never a value** |

Registered **A 1 [0,5] → 1, error 0** · **B 3 [1,6] → 3, error 0** · **directional (subtractive)
HOLDS** · kill did not fire.

**Controls:** POSITIVE — a clause the audit killed (a named k) scores **not surviving**. **g=0** — a
clause the audit preserved (③) scores **surviving**, *the scorer returns both*. NEGATIVE — clauses no
constraint mentions are **unscored**, never counted as surviving. PLACEBO — deterministic.

## ⭐ THE THREE CLAUSES, EACH WITH WHAT IT EXCLUDES
**F1 · PROVENANCE** — selected without reading the outcome labels, checkable from the producer.
*At the 2B judge.* **Excludes:** a label-reading selector emitting textually identical criteria —
R503 measured **100% verbatim overlap on both sides**, which is why no product-side check can exist.

**F2 · BEHAVIOUR ABOVE A PROMPT-BLIND FLOOR** — beats a baseline that never sees the prompt. **Not**
justified by A2 agreement. **Excludes:** `coval_core_sham`.

**F3 · SIZE AS A BOUND** — more than one criterion, **no number**. **Excludes:** `topw_k1`.

## ⚠ THE LIMIT IS THE WHOLE PROJECT
**"Survives" is my judgement against rounds I ran** — bookkeeping of this audit against this
statement, **not a measurement of the world.** Instrument unit: *a constraint-clause pair*. Claim
unit: *a clause that should be written*. **Not equal.** **A second released core is what would test
it, and the release ships one.**

## NEXT
Each of the three clauses names an object it excludes (`results/formulation.json`, field
`formulation`), and each excluded object is in this benchmark. Check the reverse direction for each:
name an object the clause ADMITS that a reader would not call a core. A clause that admits something
obviously wrong is as broken as one that excludes something obviously right, and only the exclusion
side has been tested.
