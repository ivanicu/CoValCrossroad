# R341 · Is the 5,186-node blind spot a blind spot?

**The decision this makes safe:** whether to spend a day reading the population R340's closing
sentence named. It should not be spent. Two source reads retire the question, and the sentence that
proposed it was wrong on a quantifier it never counted.

## What R340 closed with, and why that sentence is the risky one

> "those 5,186 skipped nodes are now the largest unexamined population in the repo … the scanner
> declines a pair when the CI's stem names another key … Nobody has ever measured which."

realstat §4 names this exact shape: *the closing sentence is a claim and never gets a control.* It
is written after the round's controls have fired, it is the sentence a later round acts on, and its
tell is a quantifier over my own work — **"the largest"**, **"nobody has ever"**. Both were typed,
neither was computed.

## Estimand, before method

Among the nodes the guard records in `skipped_ci_spoken_for`, the fraction the sole-candidate route
**would actually have paired** but for that predicate. A node with three mean-like keys, none, or an
existing stem match was never going to be paired; recording it as *skipped* attributes to the
predicate a refusal the surrounding conditions had already made.

The same defect is already fixed one predicate above, in the guard's own words
(`assurance/artifacts_are_internally_coherent.py:128-130`): *"Testing `sole_is_null` before the CI
condition counted 201 nodes that would never have been paired at all, which overstates what the
guard refuses."* `sole_is_null` carries `and len(cks) == 1 and not stem_hits`; `ci_spoken_for`
carries nothing. Whether that asymmetry mattered is the measurement.

## Result

| | |
|---|---|
| recorded by the guard's banner | **5,186** |
| **genuinely declined** | **5,157** — decline rate **0.9944** |
| never pairable anyway | 29, all "several/zero mean keys" |
| **rounds containing them** | **1** — `R235_independent_B` |
| **distinct key triples** | **1** — CI `eta_ci` → owner `eta`, declined mean `mean` |

**The count survives. The breadth does not.** The bookkeeping defect did *not* recur — the predicate
refuses 99.4% of what it records. But *"the largest unexamined population in the **repo**"* asserts
breadth, and the breadth is one round's `C_grid`.

## The proxy, and its measured failure

To avoid 5,186 reads I reused R340's instrument on a new population:
`offcentre = (v − (lo+hi)/2) / ((hi−lo)/2)`, comparing the stem-named owner against the declined
mean — whichever sits closer to the centre is the likelier owner.

| margin | CORRECT | SUSPECT | AMBIGUOUS | UNEVIDENCED |
|---:|---:|---:|---:|---:|
| 0.00 | 4488 | 96 | 0 | 573 |
| 0.10 | 4374 | 26 | 184 | 573 |
| **0.25** | **4198** | **18** | 368 | 573 |
| 0.50 | 3946 | 8 | 630 | 573 |
| 1.00 | 3364 | 6 | 1214 | 573 |

**All 9 distinct SUSPECTs are false positives, and the source settles it in two lines.**

- `R235/run.py:675` — `eta=float(np.nanmean(eta)), eta_ci=ci(eta)`. Same array. The naming is as
  unambiguous as naming gets; the guard's decline is **correct for all 5,157**.
- `R235/run.py:503` — `ci(x) = (percentile(x, 2.5), percentile(x, 97.5))`, and `x` here is a
  **bootstrap** array (`:636`, `:644`). So `eta_ci` is a genuine percentile CI — **of a ratio**,
  `d_core / gap`, whose denominator approaches zero.

**A ratio estimator's bootstrap mean is not a location estimate.** With a near-zero denominator the
replicate distribution is Cauchy-like and the mean can sit far outside its own central 95% with
nothing wrong. 13 distinct cells do, up to |offcentre| **2.48**.

So the proxy's own ledger row, which I wrote as *"owner far outside AND mean centred ⇒ suspect —
SOUND-ish"*, is refuted at **9/9**. *SOUND-ish* was carrying the whole claim.

## What this hands the guard, which is the part that outlives the round

**A named exception class for invariant 1.** `point inside its interval ⇒ coherent` is stated
**SOUND** in the guard's own proxy ledger and gated on. It is not sound for a ratio summarised by
its bootstrap mean. The guard has never fired on R235's 13 cells only because `eta` is not a
`MEANISH` name — **if a ratio ever gets a MEANISH name, invariant 1 will fail a correct artifact.**
That is the false-**conviction** direction, and a false retraction is as permanent as a false
acquittal because nobody re-examines a claim its own author withdrew. Written into the ledger at
`artifacts_are_internally_coherent.py`.

**583 intervals with `lo == hi`.** `inverted` tests `lo > hi` *strictly*, so an interval asserting
zero uncertainty passes it silently and nothing else in the suite looks at one. Now counted in the
banner, **reported not gated** — a parameter pinned at a grid boundary legitimately has `lo == hi`
(`eta = 1.0`, `eta_ci = [1.0, 1.0]`). The two counts measure different populations: **573** is
within the 5,157 declined nodes, **583** is over every CI key in the corpus.

## Controls

| | returned |
|---|---|
| **POSITIVE**, planted through the *same walk* as the census | `P+` recorded 1 / declined 1; `P−` recorded 0; `P+` at g=0 recorded 0 — **PASS** |
| **g=0**, predicate forced False over the whole corpus | recorded **0** — **PASS** |
| **CLASSIFIER**, mirrored plants | centred-owner → CORRECT, centred-mean → SUSPECT — **PASS** |
| **EXPIRED**, reported not gated | r16's `min_segment_ci`: 12 recorded, **0** genuine declines |

**The expired control is a finding, not a nuisance.** v1 asserted that r16 — the case the guard's
comment at `:134-138` says the predicate was written for — must appear as a genuine decline. It
does not and cannot: that comment describes the instrument as it was when `MEANISH` had been
*extended*, and `:55-62` of the same file record the extension being **reverted**. Under the
reverted regex r16's node matches **zero** mean-like keys, so no pairing was ever on the table.
That is §4's *the control fails for its own reasons* — it printed FAIL while the thing under test
was fine, and the first run of this round was correctly UNVERIFIED because of it.

## Register — what this site structurally cannot do

| criterion | status |
|---|---|
| multi-seed · seed-robust | **N/A** — a deterministic census over committed files; no rng. Two runs byte-identical (`3a32715c536a`). |
| uncertainty-quantified | **N/A** — a complete-population count has no sampling error. Declared as a census, not an estimate. |
| multiplicity | family size **1**. One census, one classification, no per-cell testing. |
| cross-dataset / cross-model | **N/A** — one release; would require a second corpus of artifacts. |
| construct-validated | **N/A** — "does this CI belong to this key" has no external gold standard here; only the source settles it, which is what was done. |

## Verdict

`COUNT_REAL_BREADTH_RETRACTED`. The population is real and is one round. The decline is correct
throughout. **The day of reading is not owed.**

## The sentence I can no longer write

> *"those 5,186 skipped nodes are the largest unexamined population in the repo, and nobody has ever
> measured which are correct declines."*

Artifact: `results/r341_skipped_population.json`, guard `sha256[:12] e999f149d5ce`.
