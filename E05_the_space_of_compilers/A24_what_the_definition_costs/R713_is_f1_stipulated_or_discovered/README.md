# R713 · is F1's exclusion set stipulated by construction, or discovered?

**Stipulated. The predicate `/oracle|_fit1/` reproduces F1's exclusion set EXACTLY — miss `0` of 42
arms — while F2's best predicate misses `5`. So F1's `p = 0.0003` measures that we built 4
label-reading arms AND a clause that excludes label-reading arms. R712's "the only clause above
chance" must be re-read: F1 is the most CONSTRUCTED of the three, not the most informative.**

⚠ **This is not a defect in F1.** A clause saying *"selected without reading outcome labels"* SHOULD
exclude exactly the arms built to read labels — exact agreement is **the clause working**. **What is
void is the p, not the clause.**

## check #315 — two defects, one of them work already done

✓ p = 0.0003, ceiling 7, and the four exclusions are oracle/label-fitted arms.

⛔ *"the ONE THING IN THE DELIVERABLE whose count beats its own null"* — an **unverified superlative,
the fifth in this arc**. True within R712's 9-cell grid, unchecked against every other claim on the
statement. Withdrawn to: *the only cell in that grid at its observed size*.

⛔ *"recomputed under the REPAIRED size clause rather than the one R360 committed"* — **R712 already
used the repaired clause.** *A closing sentence can be wrong by asking for what is already on disk.*

## the gauge test, run first per §3's ladder, at zero compute

F1 excludes **exactly** `{greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1}` — and **nothing
else in the 42-arm ledger**. `/oracle|_fit1/` returns exactly that set: 4 of 4, no false positive, no
false negative.

## the sweep — 3 clauses × 5 predicates, miss counts, all reported

| clause | best predicate | miss | polarity |
|---|---|---|---|
| **F1 provenance** | `/oracle\|_fit1/` | **0** ⭐ | matches exclusions |
| **F2 behaviour** | `/oracle\|_fit1/` | **5** | matches ADMISSIONS |
| **F3 size (repaired)** | `k` 1<k≤4 | **0** ⭐ | matches ADMISSIONS |

⚠ **F3's exact match is a DERIVATION** — F3 *is* the predicate `1 < k ≤ 4`, so a k-predicate
reproducing it is forced. Labelled, not counted as evidence.

⛔ **A polarity defect in my own sweep, caught and fixed.** The first version compared each predicate
only against the **exclusion** set, so F3's own k-predicate — which *is* F3 — scored `miss = 42` and
looked like the worst fit on the board. **A predicate matching the exact complement reproduces the
clause perfectly.** The miss is now the minimum over both polarities, and the polarity is printed so
the reader knows which.

## controls — 5 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **POSITIVE** | a predicate known wrong for F1, `/topw/`, misses by **13** — the matcher does not match everything |
| **g=0** | 3000 random 4-arm subsets reproduce F1's exclusions **0** times; the exact chance is **1/111,930** |
| **NEGATIVE** | names scrambled against verdicts at fixed multisets → exact match in **0** of 3000. *Excludes "any predicate can be made to fit 4 of 42 strings"* |
| **SHAM** | the same test on F2 and F3 — the operation minus the clause under study, and it is what produced the contrast |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |
| **REPRODUCIBILITY** | ⛔ **FAILED on the first attempt** — `list(arms)` over a *set* made the seeded shuffle depend on `PYTHONHASHSEED`, and two runs returned 1 and 0. Fixed by sorting first; now byte-identical across runs **and across a changed hash seed** |

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** F1 miss | 0 [0, 2] | **0** |
| **B** F2 best miss | 4 [0, 20] | **5** |
| **C** F3 best miss | 0 [0, 5] | **0** *(derivation)* |
| directional | F1 miss < F2 miss | **HOLDS** |

## what this re-reads

R712 found F1 the only clause whose exclusion count beats its null (p = 0.0003). That number stands
as computed; **its reading does not**. A uniform random admission is a meaningful null for a clause
whose exclusions are **discovered** and an empty one for a clause whose exclusions are **stipulated**,
and the exact name match is what tells them apart here.

## limits

- **Exact name agreement is EVIDENCE about construction, never PROOF.** That the arms were *built* to
  be excluded is a fact about our history, not about the ledger.
- This round **measures reproducibility** and **reasons about** null admissibility. It does not test
  admissibility, and (ii) in its estimand is labelled a judgement.

## impossible here

| criterion | what it would require |
|---|---|
| proving construction | a record of intent outside the ledger |
| cross-release | 41 of 42 arms are ours, which is the whole problem |
