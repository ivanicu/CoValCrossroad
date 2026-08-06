# R765 · `generic` IS `POOL[0:4]` — and the pipeline's variance splits into three objects, one of them exactly zero

**`core_generic.json[p] == core_genericpool16.json[p][:4]` on **968 of 968** prompts. **The arm that
made ③-any non-empty is the published comparator**, entered in the census as a candidate. With it
excluded, R764's *"non-empty in 4 of 8 cells"* becomes **1 of 8** — `gen` at **p000** only.
⭐⭐ And the identical-criteria pairs this census turned up give the pipeline's variance
**decomposition**: scoring alone **0.0000** (10 pairs, exact), judge alone **0.0969 [0.0597, 0.1799]**
(38 pairs), re-selection alone **0.1165** (R415). **WORLD B.**

## check #367 — one object read, zero compute

R764's NEXT asked whether `generic` is admissible as a core. It is the comparator:

| arm | k | prefix of pool16 | subset | mean overlap |
|---|---|---|---|---|
| **`generic`** | 4 | **1.0000** | 1.0000 | **1.0000** |
| `gen` | 4 | 0.0000 | 0.0000 | **0.0010** |
| `full` | 12 | 0.0000 | 0.0000 | 0.0000 |
| *(84 more, all in the artifact)* | | 0.0000 | | |

**Exactly one of 88 arms is comparator-identical.** `gen`, which sounds like the same thing, shares
**0.1%** of its criteria with the pool.

## ⛔ the forced part is labelled, and it is most of R764's headline

**D1.** `POOL[0:4]` sits at **percentile 93.7** of its own 1,820-subset class *(R527, committed)*.
A subset at percentile *q* beats every subset below *q* **on the point estimate**. So *"`generic`
clears ② at p000–p050"* is **algebra**, not a measurement — the only non-forced part is whether it
clears **resolvedly**, and R764 reported the bare admission.

## ⭐ E2 · what survives when the comparator is excluded

| baseline | ③-any (as R764 ran it) | ③-any (comparator excluded) |
|---|---|---|
| **p000** | `gen`, `generic` | **`gen`** |
| p005 | `generic` | — |
| p025 | `generic` | — |
| p050 | `generic` | — |
| p075 · p095 · **published** · p100 | — | — |

**1 of 8 cells, not 4** — and the survivor has pool-overlap **0.0010**, so it is a genuine
non-comparator admission at the **class minimum** *(ledger 1073)*.

## ⭐⭐ E3 · the floor R415 wanted, and it is three different objects

The census found **34 identical-criteria groups**. Splitting them by whether the judge also changed:

| class | pairs | \|Δ A2\| mean | min | max |
|---|---|---|---|---|
| **same judge, identical criteria** | **10** | **0.0000** | **0.0000** | **0.0000** |
| **different judge, identical criteria** | **38** | **0.0969** | 0.0597 | 0.1799 |
| same judge, re-selected criteria *(R415, committed)* | — | **0.1165** | — | — |

**The scoring step is exactly deterministic**: `topw_k4` = `_detA` = `_detB`, `random_k4_s0` =
`_ctlS0`, `random_k4_s1` = `_ctlS1`, `oracle_k4` = `_oracle_kA` = `_oracle_kB`, and the rest —
**identical on 968/968 prompts, |Δ| = 0 to every printed digit.**

⇒ **R415's 0.116 was never a "pipeline noise floor."** It is the *re-selection* term, and it sits
inside the judge term's range, which is why it read as generic instability. R416 established the
pairs were not scoring replicates; **this round says what they were instead, and prices the two
components separately** *(ledger 1074)*.

⚠ **One anomaly, named rather than absorbed.** `generic` vs `genericpool16[:4]` gives
**|Δ| 0.0009 [−0.0006, +0.0024]**, identical on **896/968** — not 968/968, although the criteria are
identical strings and the judge is the same, and 10 other same-judge pairs are exact. Two candidates:
the pool tensor sums columns by **index order** while the core JSON lists by **string order**, or the
two artifacts scored different response sets. The registered confound check passed on every pair it
could evaluate (**0 failures**) but cannot evaluate this one, because `genericpool16[:4]` is a tensor
slice and not a tag. **Reported as open** *(ledger 1075)*.

## controls — 5 PASS, and two of them had to be repaired first

| control | returned |
|---|---|
| **PROVENANCE** | R764's grid reproduced on **all 8 × 3 cells**; exits 2 otherwise |
| **POSITIVE** | `generic` prefix **1.0000** *and* `gen` overlap **0.0010**. Band: an always-contained test gives `gen` 1.0, a never-contained test gives `generic` 0.0 — both needed, unreachable from either end |
| **g=0** | `generic` vs a per-prompt **shuffled** pool → prefix **0.0000**, so the test reads *order*, not membership |
| **SHAM** | random size-4 subsets of the pool → prefix **0.0000**, subset **1.0000**. The **prefix structure** is the ingredient; membership alone is not the claim |
| **PLACEBO** | `full` prefix **0.0000** |
| **CONFOUND** *(registered, implemented here)* | pairs whose scored **response set** differs: **0** |

⛔ **The placebo was a defaulting `.get` and could only fail.** I wrote
`cen.get("coval_core", {}).get("prefix_rate", 1.0)` — and **there is no `core_coval_core.json`**
(R441 recorded exactly this: *"arms with no core file → UNKNOWN, never 0, never dropped"*, with
`coval_core` on its list). **Absence returned the default 1.0**, i.e. *"the released core IS the
comparator"* — the most alarming possible reading of a missing file *(ledger 1076)*.

⚠ **And the NEGATIVE is uninformative by construction, which is the reading, not a pass.** Deranging
the prompt pairing leaves the prefix at 1.0000 because **`generic` has exactly 1 distinct criterion
set across all 968 prompts** — it is prompt-blind, which is what ② asks of a comparator. The SHAM
carries the identification instead, and the round says so rather than counting a vacuous pass.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| *"③-any is non-empty in 4 of 8 cells"* *(R764, one commit ago)* | ⛔ **1 of 8** — `gen` at p000. Three of the four were the comparator competing in its own competition |
| *"`generic` is a core admitted under ③-any"* | ⛔ **retracted** — it is `POOL[0:4]`, prefix-identical on 968/968 |
| *"the pipeline's own noise floor is 0.116"* *(R415)* | **three objects, not one**: scoring **0.0000**, judge **0.0969**, re-selection **0.1165**. Only the third is R415's |
| the page's *"③-any → EMPTY"* | still needs a qualifier, but a **much narrower** one: empty everywhere **except the class minimum** |

## the sentence I can no longer write

*"`generic` is an arm."* It is the comparator, and every ② number in this campaign was computed over
a population that contains its own baseline.

## NEXT

The anomaly is the cheapest thing left and it is not cosmetic: if the pool tensor's **column order**
is not the core JSON's **list order**, then `POOL[0:4]` — the comparator every ② verdict in this
campaign is measured against, at percentile 93.7 — is **not the four criteria the page names**. The
72 disagreeing prompts are the whole evidence either way, and the check is one comparison between
`sorted(idxs)` and `core_genericpool16.json[p][:4]` at the same prompts. The registered quantity is
the identity of the four criteria the estimator actually sums, against the four the deliverable
prints, per prompt.
