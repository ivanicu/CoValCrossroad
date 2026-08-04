# R360 — clause ③ is the one part of the definition that is unsubstitutable

**The decision this makes safe:** *which clauses may the page present as doing independent work?*
**Clause ③ only — and it is unsubstitutable.** Clause ① excludes nothing; clause ②'s exclusions are
real but no strengthening of it can do clause ③'s job.

## Result — `W_3_IRREPLACEABLE_MAXIMAL`. Both controls PASS. Two runs byte-identical.

§4 states the test mechanically, per clause: *name an admissible object this clause EXCLUDES.* The
campaign had never run it across all three at once.

| clause | excludes | status | the objects |
|---|---:|---|---|
| **①** | **0** | **DERIVED** (R347) | none — the cell *① fails, ② passes* is empty by arithmetic |
| **②** | **33 of 42** | **MEASURED** | arms that fail the blind-reference contrast |
| **③** | **4** | **DERIVED** | `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` — forced: clause ③ *is* "no prompt labels" |

**Two of the three rows are derivations and could not have come out otherwise.** Only clause ②'s
count is a measurement. Clause ② alone admits **9**; ② ∧ ③ admits exactly the published **5**.

## The measurement: can a stricter clause ② do clause ③'s job?

That was the only non-forced question here, and nothing in the construction fixes its answer.

| reference percentile | admitted | label-users left | published five left |
|---:|---:|---:|---:|
| 0 | 13 | **4** | 5 |
| 50 | 11 | **4** | 5 |
| 93.7 *(published)* | 9 | **4** | 5 |
| 96 | 7 | **4** | 3 |
| 99 | 6 | **4** | 2 |
| **100** | **4** | **4** | **0** |

**Across all 45 swept levels the label-user count never falls below 4.** At the strongest reference
the class contains, the only arms still admitted are:

> `greedy_k4_fit1` · `indep_k4_fit1` · `oracle_k4` · `oracle_k4_fit1`
> — **every one an arm that reads the prompt's own labels.**

⭐ **Strengthening clause ② arbitrarily removes the arms the definition exists to admit and leaves
exactly the arms it exists to exclude.** So clause ③ is not merely load-bearing — no reference in
this class can substitute for it.

On a definition whose **clause ① never binds** (R347) and whose **clause ② is emptied by a change of
judge** (R358/R359), **clause ③ is the one part measured to be irreplaceable.**

## ⛔ My branches had no home for this, and the else-text asserted its opposite

I pre-registered `W-3-PARTIAL` as *"some label-users purged, some of the five retained."* Observed:
**no level purges any label-user.** That is not *"at most partly replaceable"* — it is the **maximal**
form of irreplaceable, and the default branch printed the reverse of the data.

This is the third time in five rounds that an else-branch has asserted less than, or the opposite
of, what the run measured. The remedy that works is the one applied here: **when the observed world
is not one of the pre-registered ones, name it explicitly rather than let a default catch it.**

## Controls

| | returned |
|---|---|
| **POSITIVE** — the sweep can distinguish levels | weakest admits **13**, strongest **4** |
| **g=0** — a reference against itself is not admitted | **0** self-admissions |
| **MONOTONE** — ⚠ checked, not assumed (R355 measured admission is *not* monotone in the level) | published-five count rises at **0** of 45 levels — monotone here |
| **PLACEBO** | at the weakest reference 13 of 42 admitted; the residue are arms that lose even to the worst blind set — a fact, not a failure |
| multiplicity | 45 levels × 42 arms = **1,890** admission cells, sweep persisted whole |
| reproducibility | two runs **byte-identical** (`cd9438f88e4e`) |

The monotonicity control matters because R355 established the closed region is **not** an upward
set. Here the published-five count happens to be monotone, so *"the first level that purges"* is a
boundary rather than merely a first — but that was **measured, not presumed**.

## Register — what this site cannot do

| criterion | status |
|---|---|
| **the second judge for Part B** | **N/A, and stated rather than run as a false replication** — at 0.8B nothing is admitted at any safe reference (R358/R359), so `retained_at_purge` is 0 there for reasons having nothing to do with clause ③ |
| **a reference outside this pool** | **N/A** — R331: the threshold is a fact about this 16-criterion pool |
| **between-grid levels** | conservative in a stated direction: a finer grid can only find more intermediate levels, so the measured answer cannot move *below* 0 |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"the definition's three clauses each contribute a test."*

**One excludes nothing, one is judge-emptied, and one is unsubstitutable — and they are not the ones
the ordering suggests.**

Artifact: `results/r360_clause_ledger.json`, source-stamped.
