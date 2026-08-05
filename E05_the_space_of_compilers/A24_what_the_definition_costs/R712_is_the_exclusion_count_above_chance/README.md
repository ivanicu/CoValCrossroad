# R712 · is a clause's unique-exclusion count above a same-size random admission?

**F2's last leg falls — its `20` unique exclusions sit against an exact null mean of `18.0714`,
`P = 0.1405`. ⭐⭐⭐ And the asymmetry R703 reported is INVERTED: priced against its own ceiling, the
clause with the FEWEST unique exclusions is the only one above chance — `F1 4/7 p=0.0003`,
`F2 20/23 p=0.1405`, `F3 2/5 p=0.5956`. F1 clears BH over the whole 9-cell grid; F2 and F3 do not.**

Population **the 42 arms of R360's ledger, three clauses** · instrument **exact hypergeometric
enumeration at fixed admission size** · baseline **uniformly random admission of the same size** ·
regime **this repository at HEAD**.

## check #314 — it holds, with one number of mine corrected before use

✓ `STATEMENT.md:166` does say F2 "stands on its exclusions" — written by R711 itself.
✓ Four rounds touch a unique-exclusion count (R494, R678, R703, R704); **none gives the COUNT a
null**. R704 came closest — *"a count, not a signal"* — but argued it from the base rate rather than
testing against one.
⚠ **I estimated F3 admits ~20 arms. It admits 27.** Recomputed from the ledger, not carried forward —
and the ceiling depends on it.

## the structure, derived before the run

A clause's **unique** exclusions are the arms the **other two** admit and it does not. So the ceiling
is `|others|`, and F2's 20 is **20 of 23 possible**, not 20 of 42.

| clause | admits | ceiling | observed | null mean | q95 | **exact p** |
|---|---|---|---|---|---|---|
| **F1 provenance** | 38 | 7 | **4** | 0.6667 | 2 | **0.0003** ⭐ |
| **F2 behaviour** | 9 | 23 | **20** | 18.0714 | 20 | **0.1405** |
| **F3 size (repaired)** | 27 | 5 | **2** | 1.7857 | 3 | **0.5956** |

⛔ **DERIVATION, not evidence:** the counts are forced by R360's committed verdicts. **The nulls are
the measurement.**

⭐⭐⭐ **The inversion is the round's largest finding.** A clause admitting only 9 of 42 arms reaches
**18.1** of a 23-ceiling by admission arithmetic alone. *"F2 carries the most exclusions" was a
statement about its admission size* — and the clause whose count actually beats its null is the one
R703 ranked **last** on the raw count.

## controls — 5 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **POSITIVE** | a clause admitting 9 arms all **outside** the ceiling set → **23** unique, exact p = **0.000207**; floor (18.0714) < ceiling (23), so the band is real |
| **g=0** | a clause admitting 9 arms drawn **only from** the ceiling set → **14** unique, **below** the null mean — *the statistic can move down as well as up* |
| **EXACTNESS** | enumerated vs 60,000-draw sampled: max \|Δp\| = **0.00097**. *"No Monte-Carlo error" is a resolution CLAIM and is itself checked* |
| **SHAM** | the identical machinery on F1 and F3 — same operation, different clause. **It is what produced the inversion** |
| PLACEBO / UNIT | identical enumerations differ by 0 · instrument unit ≠ claim unit |

## specification sweep — 3 clauses × 3 admission sizes, all reported

| clause | k | observed | null mean | exact p |
|---|---|---|---|---|
| F1 | **38** | 4 | 0.6667 | **0.0003** |
| F1 | 5 | 4 | 6.1667 | 0.9985 |
| F1 | 14 | 4 | 4.6667 | 0.8472 |
| **F2** | **9** | 20 | 18.0714 | **0.1405** |
| F2 | 5 | 20 | 20.2619 | 0.7627 |
| F2 | 14 | 20 | 15.3333 | **0.0028** |
| F3 | **27** | 2 | 1.7857 | **0.5956** |
| F3 | 5 | 2 | 4.4048 | 0.9998 |
| F3 | 14 | 2 | 3.3333 | 0.9647 |

**BH q=0.10 over all 9 cells → 2 survive: `F1@k=38` and `F2@k=14`.** ⚠ `F2@k=14` is a
**counterfactual** admission size, not F2's actual — it is in the sweep to show how the p moves with
strictness, and it is not F2's result.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** *(DERIVED)* F2 unique / ceiling | 20 / 23 | **20 / 23**, error 0 |
| **B** F2 null mean | 18.07 [15.0, 21.0] | **18.0714** |
| **C** exact P(F2 ≥ 20) | 0.25 [0.05, 0.70] | **0.1405** |
| directional | F2 observed ≤ its null q95 (20) | **HOLDS** |

## what falls

⛔ **`STATEMENT.md`'s "F2 stands on its exclusions" — which I wrote ONE ROUND AGO — is withdrawn.**
After R696 took the A2 agreement as circular and R711 put the sham residual at chance, this was the
clause's last support, and it is admission arithmetic.

⚠ **What this does NOT say:** that F2 is wrong, or that its exclusions are the wrong arms. **It says
the COUNT is not evidence.** Whether the excluded arms are the *right* ones is construct validity and
needs a standard outside this repository.

⚠ **The null's own choice is named:** randomising one clause while holding two fixed asks whether
*this* count is surprising **given the others**, not whether the triple is.

## impossible here

| criterion | what it would require |
|---|---|
| whether the excluded arms are the right ones | an external standard |
| cross-release | 41 of the 42 arms are ours |
