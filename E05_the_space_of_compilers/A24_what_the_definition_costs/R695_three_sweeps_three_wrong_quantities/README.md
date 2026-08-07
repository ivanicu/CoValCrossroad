# R695 · three sweeps, three wrong quantities

**⭐⭐⭐ R694's sham-ceiling question is **not answerable** from committed artifacts: **1 of 5** sham
pairs has an A2-named value for both members, and it is `gen/gen_sham` — **not** one of the two ②
separates. **Finding that out took four probes, and three of them printed "5/5 COMPLETE PAIRS" while
matching a different wrong quantity.****

## ⛔ THE THREE FALSE POSITIVES

| probe | what it actually matched | what it reported |
|---|---|---|
| "a top-level dict of ≥30 arms" | **`k`** — the arm's **criterion count** | a hit |
| "numeric values keyed by ≥2 arms" | **`k` again** | **5/5 pairs complete** |
| "a FLOAT in [0,1] keyed by arms" | **`P_arm`** — a **pool-order probability** | **5/5 pairs complete** |
| **"a field whose NAME contains `a2`"** | `arm_a2` / `a2` | **1/5** |

**None was a bug.** Each was the right query for a *different* question, and each was a **superset**
of the right test — so each matched something **real and wrong**. *§4's "a search is an instrument",
three times inside one feasibility hunt.*

## THE FEASIBILITY (G3 — every pair, strict test beside loose)

| | |
|---|---|
| arms in the ledger | 42 |
| ⭐ arms with a value in an **a2-named** field | **12** |
| loose "float in [0,1]" coverage | **42** |
| ⭐ sham pairs assemblable | **1 of 5** — `gen/gen_sham` |
| pairs ② separates | `coval_core/coval_core_sham`, `topw_k4/topw_k4_sham` — **neither assemblable** |

Registered **A 12 [4,30] → 12, error 0** · **B (the assemblable pair is not one ② separates) HOLDS** ·
**directional (strict < loose) HOLDS, 12 vs 42.**

**Controls:** POSITIVE — `arm_a2` is known to hold A2 and the name test finds it, *so a zero would
have been silence*. **g=0** — `k` is **not** classified as a score, the test that failed three probes
ago. NEGATIVE — `P_arm` is **not** classified as A2. PLACEBO — identical.

## ⚠ THE NAME TEST IS STILL A PROXY
A field **named** `a2` is not guaranteed to **be** A2. Instrument unit: **a field name**. Claim unit:
**an A2 mean**. **Not equal** — and the three false positives are what that gap looks like when the
instrument is loosened by one notch at a time.

## IMPOSSIBLE HERE, NAMED WITH ITS PRICE
Answering R694 needs A2 for **10** arms. Producing the missing ones means **re-scoring the sham arms
through the judge** — and **re-running a round destroyed its artifact once in this arc.** So the cost
is not compute; it is an artifact whose source hash would no longer match.

## WHAT THIS DOES TO R693's "2 of 5"
It stays as measured and **cannot currently be interpreted**. Whether the other three pairs are
unseparated because ② misses a real difference, or because their shams score identically to their
arms, is **exactly the quantity the corpus lacks.**

## NEXT
The a2-named coverage is 12 arms of 42 (`results/feasibility.json`, field `n_a2_named`), and the two
pairs ② separates are outside it. Before any re-scoring, check the reverse direction: for the 12
covered arms, compare their a2-named values against the ② verdicts already in R360's ledger, and
report how many disagree in sign about which arm of a pair scores higher. A disagreement there would
mean the corpus's A2 values and its ② verdicts came from different scoring runs.
