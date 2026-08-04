# R347 — clause ① has never excluded anything clause ② admits

**The decision this makes safe:** *may the page keep printing the definition as two independent
tests?* **No — not without saying which of the two is doing the work.**

## Result

Over all **41** judged arms of R294's census, the cell **(clause ① fails, clause ② passes)** is
**empty**. Clause ② excludes **8** arms that clause ① admits. Every arm that clears ② clears ① by
**≥ 5.36× its own MDE** — nothing is near the boundary from the wrong side.

| | ② pass | ② fail |
|---|---:|---:|
| **① pass** | 9 | **8** |
| **① fail** | **0** | 24 |

## The mechanism — and it could have come out the other way

| reference | level |
|---|---:|
| ① a random draw from **this prompt's own rubric** | **0.4922** |
| ② a size-matched **prompt-blind** set | **0.5462** |

**② − ① = +0.0540, and the minimum over all 41 arms is +0.0470 — never negative.**

**A criterion set that never reads the conversation beats a random draw of that conversation's own
criteria, on every arm.** That ordering is why clause ② is the binding one. Nothing forced it: a
blind reference *could* have been the weaker baseline, which is what one would naively expect, and
then clause ① would have been the harder test.

## ⛔ The empty cell is part derivation and part measurement, and the split is the honest answer

Write `c1 = arm − ref₁`, `c2 = arm − ref₂`, so `c1 − c2 = ref₂ − ref₁`.

```
IF   ref₂ ≥ ref₁   (measured: true on 41 of 41)   →  c1 ≥ c2
AND  mde₁ ≤ mde₂   (measured: true on 23 of 41)   →  c1 ≥ c2 > mde₂ ≥ mde₁
THEN clause ② implies clause ① BY ALGEBRA.
```

| | arms | status |
|---|---:|---|
| **FORCED** — both premises hold | **23** | the implication is a **derivation**; the empty cell there is arithmetic |
| **CONTINGENT** — premise B fails, so a window `[mde₂, mde₁]` exists | **18** | the empty cell there is a **measurement** that could have come out otherwise |
| arms actually inside a window at 1.0× | **0** | |

Window width across the contingent arms: **median 0.00196, max 0.01217**.

Reporting "clause ① never binds" as one number would have merged a theorem with an observation.

## Specification curve — the 1.0× threshold is a choice, so it is swept

| × MDE | counterexamples | forced | contingent | in window |
|---:|---:|---:|---:|---:|
| 0.50 | 0 | 23 | 18 | 0 |
| 0.75 | 0 | 23 | 18 | 0 |
| **1.00** | **0** | 23 | 18 | 0 |
| 1.25 | 0 | 23 | 18 | **3** |
| 1.50 | 0 | 23 | 18 | **2** |
| 2.00 | 0 | 23 | 18 | 0 |

**No multiplier produces a counterexample.** At 1.25× and 1.5× arms do enter a window — so the
design has resolution near the boundary and the zero is not an artifact of nothing ever getting
close.

## Controls

| | returned |
|---|---|
| **POSITIVE**, planted inside the window | caught |
| **g=0**, the same arm placed outside | not caught |
| **NEGATIVE**, `(c1, c2)` pairing permuted, 3 seeds | **6, 5, 6 counterexamples appear** |

The permutation is the load-bearing one. **Destroying the pairing fills the cell**, so the emptiness
is a property of *which arm has which margin* — not of the two marginal distributions. The world it
excludes is named: arms whose clause-① and clause-② margins are unrelated. Without it, "0
counterexamples" would be a number from an instrument never shown able to return one.

## Verdict — `W2_CONTINGENT`

Clause ① is a **real constraint that this arm space never exercised.** Not a theorem (18 arms could
have broken it), and not doing work either (none did).

**What the page must stop implying:** that the definition's two clauses each contribute an
exclusion. On this arm space **clause ② carries the entire boundary**, and clause ①'s only
demonstrated role is on arms clause ② has already rejected.

**What the page must not do:** delete clause ①. It is not redundant *by construction* — only on the
41 arms this benchmark contains — and the window arithmetic says exactly how narrow a
counterexample would have to be.

## Register

| criterion | status |
|---|---|
| multi-seed | 3 seeds on the permutation control; the census itself is deterministic |
| multiplicity | one family, one cell, swept over 6 thresholds; every cell reported |
| **cross-dataset** | **N/A** — one release. "Clause ① never binds" is a claim about *these 41 arms* |
| **the constructed counterexample** | **not attempted.** An arm that beats the blind reference while failing against its own prompt's rubric is constructible in principle; building one is the test this round does not perform |

## The sentence I can no longer write

> *"the definition's two clauses each do work."*

Artifact: `results/r347_clause_one_binding.json`, census `sha256[:16] ac06c51261654769`.
