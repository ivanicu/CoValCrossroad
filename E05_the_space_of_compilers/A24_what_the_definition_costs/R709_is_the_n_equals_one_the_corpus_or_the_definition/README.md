# R709 · is F1's `n = 1` a fact about the corpus, or about the definition that counted it?

**Both, and the qualification is what matters. R685's count is reproduced EXACTLY — `1` pair under
its own rule. Widened to numeric sign there are `15` comparisons at `0.800` agreement, and `6` of
them bear on the separation (`2` disagree, `4` agree). ⛔ But all `6` come from **one round**
(`R361`), so widening added FIELDS, not independent ROUNDS. **Deeper is not wider: F1's
generalisation still rests on exactly one round.****

Population **the 7 non-self rounds carrying both judge keys** · instrument **a JSON walk for dicts
keyed by both `0.8B` and `2B`** · baseline **R685's committed `n_pairs = 1`** · regime **this
repository at HEAD**.

## check #311 — the citation resolves, the superlative does not

✓ `STATEMENT.md:141-142` does say F1's scope *"rests on one verdict pair (R683, R685)"*.

⛔ **"the weakest load-bearing claim in the deliverable since R685" is withdrawn.** I never ranked the
deliverable's claims by strength. §4's closing-sentence failure, **third time in this arc**. F1's
scope is *a* claim resting on n=1, not demonstrably the weakest.

## §4's own remedy, applied: what the release CONTAINS vs what the code CONSUMED

| | |
|---|---|
| rounds with both judge keys | **11** (12 once this round writes its own artifact) |
| R685 examined | **7** |
| the 4 skipped | R683–R686 — **the instrument rounds themselves**. Self-inclusion control, correct, **not a miss** |

**World B was nearly dead before the run and was registered anyway** — a world I expect to die is
exactly the one I should not quietly drop.

## the three nested definitions

| | pairs | agree | disagree | agreement |
|---|---|---|---|---|
| **D1** R685's rule (bool + closed-set string) | **1** | 0 | 1 | 0.0000 |
| **D2** + numeric SIGN | **15** | 12 | 3 | **0.8000** |
| **D3** + vector ORDER | 17 | 13 | 4 | 0.7647 |

⚠ `D1 ⊆ D2 ⊆ D3` is a **derivation** (nesting), not evidence. The counts are the evidence.

## ⭐ the decisive distinction — computed, not typed

**6 pairs have a separation-bearing field, 5 of them new at D2** — and every one is in `R361`:

| round | level | field | verdict |
|---|---|---|---|
| R361 | D1 | `rank_resolved` | **DISAGREE** |
| R361 | D2 | `min_labels` | **DISAGREE** |
| R361 | D2 | `mean_five_rank` · `mean_label_rank` · `rank_sd.five` · `rank_sd.label` | AGREE |

⛔⛔ **All six from one round.** Correlated measurements of a single comparison are not a second
comparison. *Deeper is not wider.*

## controls — 6 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| POSITIVE | R361's `rank_resolved` `{0.8B: False, 2B: True}` re-found by D1 — a known-present object |
| g=0 | synthetic artifact with both judge keys and no comparable value → **0** pairs |
| NEGATIVE | judge keys stripped → **0** pairs; the finder responds to the **keying**, not to field names |
| SHAM | keying requirement dropped: 97 top-level fields vs 17 judge-keyed pairs |
| PLACEBO / UNIT | identical walks differ by 0 · instrument unit ≠ claim unit |
| SELF-INCLUSION | R683–R686 excluded **by name and counted** — the whole 11-vs-7 difference |

## ⛔ my own instrument regressed to a bug the round under audit had already fixed

My first run returned **D1 = 10**, "refuting" R685. **9 of the 10 were `controls.*`** — my own
positive/g0/placebo/sham flags, which pass at both judges **by design**. R685 had already found and
excluded exactly this. **I reimplemented the walk from scratch, read R685's verdict string and not
its exclusion logic, and reintroduced its closed defect.** With the exclusion wired in, D1 = 1 and
R685 replicates exactly.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** D1 pairs | 1 [0, 3] | **1** — R685 replicated exactly |
| **B** D2 pairs | 5 [1, 15] | **15**, at the interval's edge |
| **C** D2 sign agreement | 0.60 [0.20, 0.95] | **0.800** |
| directional | D2 > D1 | **HOLDS** |

## what changes on the deliverable

`STATEMENT.md`'s *"rests on one verdict pair"* **understates the corpus** — six separation-bearing
comparisons exist, not one. **It does not overstate the conclusion**: all six are in one round, so
the generalisation still rests on n = 1 **round**, and the phrase is corrected to say so.

## limits

- "Separation-bearing" is a **field-name judgement and it is mine**; every field is printed so a
  later round can reject the operationalisation without redoing the walk.
- A sign agreement is **weaker evidence** than a verdict pair.
- Two judges remain two.

## impossible here

| criterion | what it would require |
|---|---|
| a third judge | the release ships two; no rate over 2 bounds anything about a third |
| construct validity of "informative about the separation" | a criterion outside this repo |
