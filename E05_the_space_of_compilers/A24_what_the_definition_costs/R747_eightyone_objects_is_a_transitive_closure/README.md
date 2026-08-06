# R747 · 81 objects is *not* a transitive-closure artifact — the attack failed and the number stands

**Every one of R730's 8 multi-tag classes is a CLIQUE. The clique partition returns 81, identical to
union-find's 81, at every guard threshold from 0.0 to 1.0. My registered prediction that ≥1 class
would be a chaining artifact is refuted, and the registered `P4 ≥ 1` failed outright at 0. ⭐ What
stands: the object counts in R730, R745, R746 and the deliverable do not inherit a non-transitivity
defect.**

## check #349 — the previous NEXT was prior art, and so was half the round before it

⛔ **R730's committed artifact already holds what R746 proposed to compute:** `r729_seven_tags` are
exactly the seven, `objects_of_the_seven` is **4**, `n_tags` **93**, `n_objects_exact` **81**.

⛔⛔ **And worse — R746's own identity half was a rebuild of the same artifact.** R730's
`multi_tag_classes` already lists `['coval_core', 'coval_core_2bA', 'coval_core_2bB']` and
`['topw_k4', 'topw_k4_detA', 'topw_k4_detB']`. I ran P4 on R746's *coverage* question and not on its
*identity* question, so the rebuild went through. **Third rebuild P4 has stopped in this arc, and the
first one it stopped only after the fact** *(ledger 1008)*.

## what reading R730's source turned up instead

```python
same(A, B):  equal on the prompts they SHARE, provided
             len(shared) >= 0.5 * min(len(A.pids), len(B.pids))
```
…and the partition is built by **union-find**. Equality on a shared subset **is not transitive**:
A≈B on their shared set, B≈C on theirs, A≢C on theirs. Union-find takes the closure regardless. Since
**81 is the denominator R730, R745, R746 and the deliverable all rest on**, that is worth attacking.

## the measurement — and the attack failed

| | registered | measured | |
|---|---|---|---|
| P1 non-clique multi-tag classes | 1, band [0, 8] | **0** | in band, point wrong |
| P2 clique-partition object count | 83, band [81, 93] | **81** | at the floor, point wrong |
| P3 reproduce R730's 81 with its own code | yes *(hard)* | **81 = 81** | ✓ |
| **P4** pairs rejected **only** by the guard | **≥ 1** | **0** | ⛔ **FAILED** |
| D every violation involves a low-coverage tag | true | **n/a — 0 violations** | vacuous |

**8 multi-tag classes, 4 of size ≥ 3, 0 not cliques.**

⛔ `E2 ≥ union-find count` is **FORCED** — the clique partition refines the closure. *"The count went
up"* could never have been a finding; only the **size of the increase**, which is **0**, is a
measurement.

## the specification curve — flat, and the reason is a derivation

| guard | objects | multi | non-clique | clique count |
|---|---|---|---|---|
| 0.00 | 81 | 8 | 0 | 81 |
| 0.25 | 81 | 8 | 0 | 81 |
| **0.50** *(R730's)* | **81** | **8** | **0** | **81** |
| 0.75 | 81 | 8 | 0 | 81 |
| 1.00 | 81 | 8 | 0 | 81 |

⛔ **The flatness is not robustness — it is arithmetic, and it is why `P4 = 0`.** The guard is
`len(shared) ≥ g·min(|A|, |B|)`. For a **strict subset** pair, `len(shared) = min(|A|, |B|)`, so the
test is `min ≥ g·min`, which **holds for every g ≤ 1**. The guard can therefore only ever reject a
**partial** overlap — and this population contains none. Sweeping it was always going to be flat.

## ⭐ but the subset rule IS load-bearing — the SHAM shows where

**Ingredient absent** (require **identical** prompt sets rather than a shared subset): **83 objects**,
still 0 non-cliques. So the subset rule merges **2** pairs that full-overlap equality would keep
apart — precisely the `coval_core`/`_2b*` case R746 measured at 200 of 968 prompts.

⇒ **the count depends on the modelling choice (81 vs 83), and not on chaining.** R730's own residue
already said the choice is a choice: *"whether NEAR-identical objects should merge is a modelling
choice, not a measurement"*. **This round does not adjudicate it** — it establishes only that the
published number is the one the stated relation yields.

## controls — 6 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | a **synthetic** non-transitive triple (A≈B, B≈C, A≢C, built by construction): union-find merges to **1** class, the clique test flags **1**. Band computed — a never-flagging checker flags **0** (floor), this one flags 1 |
| **g=0** | a synthetic **clique** triple → **0** flagged. **Flagging every multi-tag class would have manufactured World B** |
| **NEGATIVE** | `same()` forced False → **93** singletons, **0** violations |
| **SHAM** | ingredient **absent**: identical prompt sets → 83 objects, 0 non-cliques |
| **PLACEBO** | 73 singleton classes → **0** violations, stated as **0 of 73** |
| **P3** | the instrument is R730's, not a lookalike — 81 = 81 |

⭐ **The positive control is the part that makes the zero admissible.** A checker that has never
flagged anything returns silence, not an acquittal — so it was pointed at a triple built to violate,
and it fired.

## the sentence I can no longer write

*"81 objects may be a chaining artifact."* It is not, at any guard level, and the mechanism is that
the guard cannot bind on subset pairs.

## NEXT

The count is now known to be well defined and known to depend on one modelling choice worth 2 objects
— subset-merging versus full-overlap. R730's residue names that choice and no round has priced it.
The registered quantity is what the *deliverable's own claims* do under each rule: the extension, the
③-admitted set and claim row 9's "56 tags are 46 objects" recomputed under full-overlap identity,
reported as a pair of numbers rather than one. That is a different unit from this round — the claim,
not the class — and it is the step that turns a partition into something a reader can act on, since a
count that moves with a rule nobody stated is a count with a hidden parameter.
