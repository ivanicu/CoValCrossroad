# R743 · a derived population is a timestamp — and the expiry is at the root, not in the rows

> ⛔ **CORRECTED BY R744, THE ROUND AFTER THIS ONE** *(ledger 995, 996)*. The headline below first
> said *"11 of the remaining 16 never load an arm artifact"*. The artifact says **6 `NO_ARMS` + 5
> `NONE`** — the 11 is their sum and means *no identifiable population*. **And the 6 is an upper
> bound**: following named cache edges, **5 of those 6 reach the arm store**, only `R558` does not.
> `NO_ARMS` measured **files**; the sentence asserted **rounds**.

**The claim table's one population constant, `R294's 41 arms`, is inherited by rounds that mostly do
not establish it: of the 18 rounds the ten rows cite, 2 carry no code and 11 of the remaining 16 name
no arm population in their own source. Only 5 have an arm population and 4 of those hand-enumerate it. The single round
that DERIVES one is R294 itself — the round the constant is named after — and its glob returns 101
files today against the stated 41. ⛔ I registered ≥60% of citing rounds would glob; the measured
figure is 20%, outside my own band.**

## check #345 — the previous NEXT holds on its instrument and is REFUTED on its unit

✓ `assurance/statement_provenance.py` does not check whether a cited round's verdict still supports
the citing sentence — its own docstring says *"this checks the CITATIONS, not the sentences."*

⛔ But the proposed **unit — the claim block — is the one R719 already measured blind**: 2 of the 3
blocks touching a retracted literal never cite the retracting round, so a block-scoped amendment test
cannot see a retraction filed elsewhere. Proposing it again 24 rounds later is *(ledger 990)*.

## P4 ran first and moved the round twice

| layer | result |
|---|---|
| **L1** live code | `assurance/arm_population_is_derived.py` — **same axis, opposite sign**: it certifies `DERIVED` as the SAFE side |
| **L2** archive + git | `git log --all -S"verdict still supports"` → nothing |
| **L3** this project | R560 (does a row *state* a population), R590 (is the *value* in the cited artifact), R718/R719 (block amendment + its blind spot), R606, R728 |
| **L4** framework | N/A — no framework answers "is this stated population true of that round" |
| **L5/L6** siblings, external | N/A — the object is this repository |
| ⇒ | **REUSE the classifier · TRUE GAP for the question** |

## ⛔ the gauge test killed the first estimand for free — third time this arc

I first proposed reading each cited round's recorded population **from its artifact**. Measured:
across **465** artifacts a population size is spelled **19** ways, and the commonest (`n_arms`) covers
**35**. That instrument would have measured **spelling** and returned a low count reading as a finding
about the rounds. **Not identified from artifact fields; identified from source.** Zero compute
*(ledger 991)*.

## the grid — 3 detectors × 2 populations, all six cells

| detector | population | DERIVED | TYPED | DECL | NO_ARMS | NONE | n_pop | f |
|---|---|---|---|---|---|---|---|---|
| loose | cited | 2 | 4 | 0 | 6 | 4 | 6 | 0.3333 |
| loose | complement | 49 | 38 | 1 | 262 | 53 | 88 | 0.5568 |
| **medium** | **cited** | **1** | **4** | **0** | **6** | **5** | **5** | **0.2000** |
| medium | complement | 26 | 41 | 1 | 262 | 73 | 68 | 0.3824 |
| tight | cited | 1 | 4 | 0 | 6 | 5 | 5 | 0.2000 |
| tight | complement | 25 | 41 | 1 | 262 | 74 | 67 | 0.3731 |

⭐ **The SHAM has the ingredient ABSENT, not inverted.** Ingredient = being cited by a claim row.
Globbing is **more** common outside the cited set (0.3824) than inside it (0.2000), so it is not a
property of the tree that citation inherits.

## registered vs measured — two failures, reported as failures

| | registered | measured | |
|---|---|---|---|
| P1 rounds cited | 17 [12, 24] | 18 | ✓ |
| P2 glob fraction (medium) | 0.60 [0.30, 0.90] | **0.2000** | ⛔ outside the band |
| P3 globs returning ≠ 41 today | ≥ 1 | 1 of 1 | ✓ |
| P4 detector agreement | ≥ 0.70 | 0.9375 | ✓ |
| D directional | true | **false** — exactly one derived round | ⛔ |

## controls — 5 PASS, 0 FAIL, and ⛔ two of them failed for their own reasons first

| control | returned |
|---|---|
| **POSITIVE** | `R728 → DERIVED`, `R477 → TYPED`; band **computed** `0 < 2 ≤ 16` |
| **g=0** | no-arm-code source → `NO_ARMS` |
| **NEGATIVE** | globs deleted from R728, rest kept → `DERIVED → TYPED` |
| **SHAM** | the complement population, ingredient absent |
| **PLACEBO** | 410 READMEs → 0 DERIVED, stated as **0 of 410**; 21 mention arms in prose |
| **UNIT** | 0 rounds map to >1 `run.py`; the 2 mapping to zero are named and excluded by construction |

**① The positive control's second case was wrong, not the instrument.** I expected `R719 → TYPED`
because it runs on the literal `PUBLISHED_FIVE`. It returned `NO_ARMS` — correctly: R719 works on
published arm *names from a card* and never loads a `sat_*.npz`, so the classifier's gate is not
reached. §4 form ③, a control aimed at a different statistic. The replacement's expectation is grounded
**outside** this instrument, in `arm_population_is_derived.py`'s own docstring recording that R477
hand-bounded its class.

**② The unit control demanded exactly one `run.py`** and failed on `R580`/`R581`, which carry a README
and results and no code — a known category (R592) with nothing to do with the estimand *(ledger 993)*.

## ⛔ my own verdict string would have reported the algebra as evidence

The confound written before the run: class might be a function of **era**, not of the claim. The script
computed separability of the two round-number sets and printed `True`. At `|DERIVED| = 1` that is
**forced** — one point is separable from every set. It now prints `UNINFORMATIVE` and states the
confound is **uncontrolled** *(ledger 994)*.

## the ontology shift my world list did not contain

I named three worlds: the constant is a scope (A), a timestamp (B), or mixed (C). The answer is A on
the number and **none of them in substance**:

> **the constant's SOURCE is derived and expired; its INHERITORS are stable and mostly have no
> population of their own.** The fossil is at the root.

⚠ Whether R294's raw **101** and R728's post-filter **92** are the same quantity is **`UNVERIFIED`**
from a source search — it needs the construction step, not a pattern.

⭐ And it puts two gates on one axis with opposite signs: `arm_population_is_derived.py` treats
`DERIVED` as the safe side (nothing hand-omitted) while this round shows `DERIVED` is what makes a
*stated* population expire. **Both are right about different properties**, and neither says so.

## the sentence I can no longer write

*"the ten claim rows hold over R294's 41 arms."* Eleven of the sixteen with code name no arm
population in their own source; the constant is inherited, and its source no longer returns 41.
⛔ *"six of them never touch an arm artifact"* is also now unwritable — R744 reaches the store from
**5 of those 6** through named cache edges.

## NEXT

The rows inherit a population without establishing it, and this round measured only whether they
*derive* one — it did not measure **which data each source loads**. That is a different instrument
with a different unit: the file opened, not the round. Enumerate the data paths each cited round's
source opens, and ask how many of the ten rows rest on a round that reads the arm store versus one
that reads a persisted summary of it. R728's README records that the rounds from R680 to R727 read
R294's persisted summary rather than the sat store, so *paths opened* is the population that decides
whether a row is grounded in the object, and it is readable from the same ASTs parsed here.
The quantity to register is the share of the ten rows whose supporting rounds open the arm store —
measured, not assumed, since this round found 11 of 16 naming no arm population in their own source.
⛔ **R744 ran exactly this and inverted it**: the flat detector is blind to indirection, and 5 of the
6 `NO_ARMS` rounds reach the store through a cache they name.
