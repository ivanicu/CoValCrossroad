# R703 · is every clause load-bearing?

**⭐⭐⭐ All three clauses are load-bearing — **and the F3 that R701 wrote had ZERO unique exclusions.**
It was decoration by R519's own test. **R702's ceiling did not tighten a clause; it rescued one the
necessity test would have retired.****

## UNIQUE EXCLUSIONS PER CLAUSE (G3 — every clause, every arm named)

| clause | unique | what only it excludes |
|---|---|---|
| **F1 provenance** | **4** | `greedy_k4_fit1` `indep_k4_fit1` `oracle_k4` `oracle_k4_fit1` |
| **F2 behaviour** | **20** | the shams, the randoms, `gen`, `generic`, `promptecho`, `topabs_k4`, `topvar_k4`, `topwvar_k4`, `topw_k2` … |
| **F3 size (repaired)** | **2** | **`topw_k6` `topw_k8`** |
| ⛔ **F3 as R701 wrote it (floor only)** | **0** | **NOTHING — decoration** |

Registered **A 3 [0,3] → 3, error 0** · **B (F3 unique = 3) → 2, error −1** · **directional HOLDS** ·
kill did not fire.

**Controls:** POSITIVE — the method **reproduces R519's published admitted set** from the ledger, *so
its zeros are measurements and not silence*. **g=0** — F3's floor excludes `topw_k1`, *the method
returns non-zero somewhere*. NEGATIVE — an arm outside the ledger is unscored. PLACEBO — identical.

## ⛔ WHY REGISTERED B MISSED, AND IT IS THE ROUND'S BEST FINDING
I counted **`topw_k1`** as an F3-unique exclusion. **F2 excludes it too**, so it is not unique — and
that arithmetic, followed one step further, says **the original F3 excluded nothing uniquely at all.**
**A clause with a lower bound and no ceiling was, by R519's own criterion, exactly the decoration §4
warns about** — the same criterion that retired ① and ④.

## ⭐ SO THE MIRROR TEST DID MORE THAN TIGHTEN
R702 found F3 admitted `topw_k6` and `topw_k8`. This round shows the ceiling it added is **the only
reason F3 survives necessity**. **Two tests from §4's single remedy, run one round apart, and the
second is what made the first's repair load-bearing rather than cosmetic.**

## ⛔ THE PREVIOUS NEXT'S EXAMPLE WAS WRONG, AND A GAUGE TEST SHOWED IT FREE
It offered `random_k4_s0` as something F1 admits that a reader would refuse. **It is label-free, so
F1 does admit it — but it fails F2, so the conjunction refuses it.** *Naming an object one clause
admits is uninformative when another catches it.* The informative question is **necessity**.

## ⚠ TWO LIMITS
- **Clauses are tested as the LEDGER IMPLEMENTS them**, not as R701's prose states them. Where prose
  and code differ, this measures the code.
- **Necessity here is not necessity in general.** A clause with unique exclusions on this population
  may be redundant on another — and **41 of these 42 arms are ours**.

## IMPOSSIBLE HERE
Whether a clause is necessary in general needs a population we did not build.

## NEXT
F2 carries 20 unique exclusions against F1's 4 and F3's 2 (`results/load_bearing.json`, field
`rows`). That asymmetry has not been examined: R694 measured that 95.2% of the definition's
discriminating power is recoverable from `(family, k)`, so check how many of F2's 20 are recoverable
the same way — if most are, F2's apparent weight is our parameterisation showing through, and the
clause carrying the most exclusions would be the one contributing least that is not ours.

---

## ⚠ ANNOTATED BY R704 (2026-08-05) — two corrections, neither touching this round's numbers

**① This round's own artifact under-reports its own sets.** `run.py:120` builds the verdict string
with `str(r['unique'][:3])`, so `results/load_bearing.json` prints **three** members for F1 and for F2
with no ellipsis and no count, beside `n_unique: 4` and `n_unique: 20` in the same file. The `rows`
field is correct and is the source of record; the `world` string is a lossy display of it. Third
occurrence of this class (R690's set indexing, R698's README vs its JSON, this).

**② The NEXT line below was answered and its premise is REFUTED.** R704 measured the value of the
generator name over the base rate on **all 42 arms**: `+0.000` for F2 under `(family,k)`, `+0.048` at
best across five partitions, and no partition clears its own permutation null. F2's 20 unique
exclusions are a **count**, not a signal — F2 excludes 33 of 42 arms. The line's own framing carried
the defect: measuring on *the clause's own unique exclusions* conditions on the label being
predicted, which fixes the base rate at 1.000 or 0.000 by algebra.
