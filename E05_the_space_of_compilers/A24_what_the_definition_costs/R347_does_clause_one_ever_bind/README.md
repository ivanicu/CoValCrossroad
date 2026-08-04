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

## ⛔ The empty cell is a DERIVATION — and my first reading of it was wrong

An arm `A` is a counterexample iff `A > ref₂ + mde₂` (② passes) and `A ≤ ref₁ + mde₁` (① fails).
That region is non-empty **iff**

```
GAP < SLACK        GAP = ref₂ − ref₁ = c1 − c2        SLACK = mde₁ − mde₂
```

**Measured: min GAP 0.0470, max SLACK 0.01217 — GAP exceeds SLACK by 3.9× on the tightest arm, and
`GAP ≥ SLACK` on all 41.** The counterexample region is **empty for every arm size this benchmark
contains**. Clause ② implies clause ① by algebra here; it could not have come out otherwise.

### What v1 of this round got wrong

It tested **`mde₁ ≤ mde₂`** — which *forces* the implication but is **not required** for it. A
sufficient condition standing in for a necessary-and-sufficient one. Consequences:

- 18 arms were called **CONTINGENT**; none of them can host a counterexample.
- `in_window` compared `c2` against the thresholds and **ignored GAP entirely**, so it reported 3
  and 2 arms inside a window that does not exist.
- The round closed that a counterexample was *"constructible in principle"* and named building one
  as the next step. **There is none to build here.**

The arithmetic that settles this is step 2 of the attack ladder and belonged **before** the count,
not deferred to a next round. Note the direction: the wrong condition made the finding look
**weaker and more contingent** than it is.

⚠ And it is a derivation **about this release**, resting on `ref₂ − ref₁ ≈ +0.05` against MDEs of
0.011–0.013 — not about the definition in general. A release with a weaker blind reference, or a far
more precise design, could break it.

## Specification curve — the 1.0× threshold is a choice, so it is swept

| × MDE | counterexamples | forced | contingent | in window |
|---:|---:|---:|---:|---:|
| 0.50 | 0 | 41 | 0 | 0 |
| 0.75 | 0 | 41 | 0 | 0 |
| **1.00** | **0** | **41** | **0** | 0 |
| 1.25 | 0 | 41 | 0 | 0 |
| 1.50 | 0 | 41 | 0 | 0 |
| 2.00 | 0 | 41 | 0 | 0 |

**No multiplier produces a counterexample, and none makes the region non-empty either** — doubling
the threshold does not open a gap wide enough, because GAP scales with nothing and SLACK scales with
the multiplier but starts 3.9× too small.

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

## Verdict — `W1_DERIVATION`

**On this release, clause ② implies clause ①.** Not a measurement: the region where they could
disagree is empty by arithmetic.

**What the page must stop implying:** that the definition's two clauses each contribute an
exclusion. On this arm space **clause ② carries the entire boundary**, and clause ①'s only
demonstrated role is on arms clause ② has already rejected.

**What the page must not do:** delete clause ①. The implication rests on a **measured reference
gap**, not on the definition's own logic, so a release with a weaker blind reference would restore
clause ①'s bite.

## Register

| criterion | status |
|---|---|
| multi-seed | 3 seeds on the permutation control; the census itself is deterministic |
| multiplicity | one family, one cell, swept over 6 thresholds; every cell reported |
| **cross-dataset** | **N/A** — one release. "Clause ① never binds" is a claim about *these 41 arms* |
| **the constructed counterexample** | **shown impossible here**, not merely unattempted — `GAP ≥ SLACK` on all 41 arms. Constructing one requires a release where the blind reference is weaker or the design is ~4× more precise |

## The sentence I can no longer write

> *"the definition's two clauses each do work."*

Artifact: `results/r347_clause_one_binding.json`, census `sha256[:16] ac06c51261654769`.
