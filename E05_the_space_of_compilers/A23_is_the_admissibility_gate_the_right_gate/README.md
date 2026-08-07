# A23 — is the admissibility gate the right gate

**28 rounds, R248–R275.** Per P16 this file is a **table of contents only**: the sub-round → what it
asked. Every finding, its interval and its scope live in `E05/FORMULATION.md` and `RETRACTIONS.md`.
**One home per fact** — a number stated twice drifts, and the copy is never the one that gets fixed.

---

## ⚠ THIS DIRECTORY IS THREE ARCS AND SHOULD HAVE BEEN THREE DIRECTORIES

P16: *an arc closes when a **decision becomes safe**, and the count is **discovered, never chosen**.*
By that rule A13 holds **three** closed decisions, and I discovered that by writing this file rather
than by planning it.

| what it should have been | rounds | the decision, and where it closed |
|---|---|---|
| **A13** is the admissibility gate the right gate? | R248–R253 | **Closed at R253**: no. `A_real` predicts recovery no better than the criterion count, so the gate reverted to `C(n,k) ≤ a(m)` — two steps behind where it started. |
| **A14** what does the instrument do to these numbers? | R254–R266 | **Closed at R266**: draw noise is 1/16 of the largest term. Three unrelated axes — label order, batch bf16, `PYTHONHASHSEED` — all say R231's central comparison was never a comparison. |
| **A15** what can this release resolve at all? | R267–R275 | **Closed at R274/R275**: MDE `[0.1250, 0.1250]` ⚠ **for THIS detector only** (R277), every substantive effect 3–30× below it, and the two corrections that produced that number **interact more strongly than either acts alone**. |

**Not restructured, annotated** (L81: annotate, never rewrite; `mv`, never `rm`). Renaming 28
directories late in a long session risks the references in 28 docstrings for a gain that is
navigational only. **The finding is recorded here; the move is a separate action with its own
verification.**

---

## R248–R253 · is the gate the right gate?

| round | what it asked |
|---|---|
| `R248` capacity versus realised alphabet | does the gate's right-hand side predict when recovery fails? |
| `R249` which printed criteria do work | the `representative` field, by exhaustive leave-one-out |
| `R250` can provenance be reconstructed | a dose curve on 298 verbatim ground-truth items |
| `R251` substitution is the dose that can kill | the perturbation deletion could not perform |
| `R252` was it redundancy or the marginal | claim 8 against its strongest confound |
| `R253` is `A_real` just `n` in a costume | **the meta-separator** — does the gate's quantity carry information? |

## R254–R266 · what does the instrument do?

| round | what it asked |
|---|---|
| `R254` targeted substitution · where the real core sits | concentration vs noise, and the crossover |
| `R255` is the redundancy lexical at all | lexis vs discrimination, clustered by prompt |
| `R256` is the rubric rank one | a common factor, against a **measured** null |
| `R257` label-order gauge propagation | R234's `r = 0.77` pushed into four load-bearing claims |
| `R258` size-matched rank one | R256's own gap, at matched subset size |
| `R259` does the rate survive noise | `U(k)` at the release's own rater noise |
| `R260` instrument-noise intervals | resampled batch noise onto every published quantity |
| `R261` hash-seed sweep | 13 of 19 E05 seeds keyed on a string |
| `R262` the floors R261 said it could not reach | two of three needed no GPU; one `grep` said so |
| `R263` the remaining salted rounds | R241's conclusion flips with an environment variable |
| `R264` how often does R241 hold | the flip as a **rate**: 15 of 24 |
| `R265` is R241's control validated by noise | a control that improving the instrument breaks |
| `R266` which noise actually binds | the hierarchy of three error sources on one number |

## R267–R275 · what can this release resolve?

| round | what it asked |
|---|---|
| `R267` what this release can resolve | first MDE attempt — **refused its own reading** |
| `R268` a calibrated detector and the real MDE | α calibrated and held out |
| `R269` a sham that can fail | the void sham, and why the obvious repair is also void |
| `R270` the arc chose the coarser statistic | the human-ranking statistic's floor |
| `R271` the clustering inflation with a number on it | 93,558 rows over 968 clusters |
| `R272` the inflation with a calibration that takes | the check R271 omitted |
| `R273` the inflation as an interval | a point estimate off a grid is a bracket-read |
| `R274` the site MDE at fine resolution | R268's number, at 0.005 and 3000 draws |
| `R275` what a replication can and cannot catch | the 2×2 that prices what R269 held fixed |

---

## The one thing a later reader should take from the shape rather than the contents

⚠ **The first version of this paragraph said "twelve of these 28" and "nine of those". Both were
typed, not counted** — in a file whose whole subject is numbers that were typed rather than counted.

Counted, by a stated rule — *a round is corrective iff its opening docstring block names an earlier
round AND contains a defect word* (`wrong|void|refus|defect|could not|retract|failed|no-op|
impossible|mis-scaled|omitted|inherited|over/understated`):

| | |
|---|---:|
| rounds with a `run.py` | **28** |
| **corrective by that rule** | **24** |
| of those, the earlier round is **also in A13** — same directory, same day | **20** |

**The rule is generous** and I am not hiding that: it counts a round that merely *cites* an earlier
round while using a defect word about something else.

⚠ **I then said "the honest figure is between my typed 12 and this rule's 24". That interval is
also wrong, on both ends.** Sweeping the rule itself — *corrective iff an earlier round-id occurs
within `W` characters of a defect word* — gives a specification curve:

| W | corrective | self (A13) | share of 28 |
|---:|---:|---:|---:|
| 20 | **16** | 12 | 0.57 |
| 40 | 19 | 14 | 0.68 |
| 60 | 21 | 15 | 0.75 |
| 100 | 22 | 16 | 0.79 |
| 200 | 25 | 19 | 0.89 |
| 400 | 27 | 21 | 0.96 |
| 800 | **28** | 24 | **1.00** |
| whole docstring | 28 | 26 | 1.00 |

**The range is 16 to 28 of 28 — 57% to 100% — and at every window ≥ 800 characters it is all of
them.** My lower bound of 12 was too low and my upper bound of 24 was too high.

> **The width is the finding. "How corrective is this arc" has no rule-free answer**, and any single
> number I quote is a statement about the window I chose. That is more honest than the interval I
> gave and much more honest than the point I typed first.

What survives either reading: **the arc is not a sequence of findings with corrections appended. It
is mostly corrections, and the findings are what survived them.** That is the honest description of
what an audit at this severity produces, and it is worth knowing before starting one.

The dependency chain is also visible in the counts: `R268 → R269 → R270 → R271 → R272 → R273 → R274
→ R275`, each opening by naming its predecessor. **Eight rounds to settle one MDE, and the last one
found that fixing two of its defects interacts more strongly than either acts alone.**

---

## ⚠ SCOPE REPAIR 2026-08-03 (R277) — the word `site` in the A15 row was an overshoot

The row above once read **`site MDE [0.1250, 0.1250]`**. Read as written, that forbids quoting any
paired arm comparison anywhere in E05. It does not, and the reason is the scope, not the number:

| | R274's MDE | the paired arm comparisons |
|---|---|---|
| estimand | `g = P(force class agreement)` | paired A2 difference between two arms |
| comparand | a subset-core vs **the full rubric** | an arm vs **human classes** |
| statistic | A1-style exact class agreement | pairwise accuracy over 6 pairs |
| n | 250 prompts | 968 prompts |
| test | one-sample calibrated detector | paired cluster bootstrap |

**Four differences, any one of which breaks the transfer.** The measurement was correct; the noun
was too big. `site` names a property of the release when the number is a property of **one detector
on one statistic at one n** — frontier §2's overshoot, and the variety that propagates hardest
because a hard limit is exactly the kind of sentence nobody re-derives.

The MDE of the paired design is **[0.0100, 0.0200]** (R277), i.e. **6–12× smaller**. That does not
rescue everything: two of the four claims A16 was quoting still sit at or below it. It means the
number that governs a claim has to be measured **for that claim's design**, and A13 never was.

---

<!-- ROUND-INDEX:BEGIN — generated by assurance/generate_round_index.py, do not hand-edit -->

**35 rounds.** Regenerate with `.venv/bin/python assurance/generate_round_index.py --apply`; everything outside the two markers is left untouched.

| round | what it asked | results files |
|---|---|---|
| [`R248`](R248_capacity_versus_realised_alphabet) | - the definition's own admissibility gate, tested as a PREDICTOR rather than quoted. | 1 |
| [`R249`](R249_which_printed_criteria_do_work) | - the `representative` field has been FAILED since R236. This measures what goes in it. | 1 |
| [`R250`](R250_can_provenance_be_reconstructed) | - `provenance` has read 0.00 since R232. That is a fact about a FIELD, not about the data. | 2 |
| [`R251`](R251_substitution_is_the_dose_that_can_kill) | - R250's dose axis could not kill the text route. This one can, and that is the point. | 2 |
| [`R252`](R252_was_it_redundancy_or_the_marginal) | - R248's rival was a UNIFORM tensor. That confounds redundancy with the marginal. | 1 |
| [`R253`](R253_is_A_real_just_n_in_a_costume) | - the meta-separator. Is the gate's quantity real, or is it the criterion count renamed? | 1 |
| [`R254`](R254_targeted_substitution_and_where_the_real_core_sits) | - R251 called its substitution ADVERSARIAL. It was not. This one is, and it has a crossover. | 2 |
| [`R255`](R255_is_the_redundancy_lexical_at_all) | - R249 concluded the redundancy comes from GENERIC TEXT. If lexis predicts nothing, it can't. | 1 |
| [`R256`](R256_is_the_rubric_rank_one) | - the third property. If the rubric is rank-1, a core is a noisy estimator of one number. | 1 |
| [`R257`](R257_label_order_gauge_propagation) | - the judge is not label-order symmetric. This propagates that into every E05 claim. | 2 |
| [`R258`](R258_size_matched_rank_one) | - R256's core-vs-full rank-1 gap is 4 rows against 11. This is the size-matched cell. | 1 |
| [`R259`](R259_does_the_rate_survive_noise) | - R253 killed A_real. It never tested U(k), which is what FORMULATION still stands on. | 1 |
| [`R260`](R260_instrument_noise_intervals) | - every published E05 number lacks an instrument line. The noise to put in it is measured. | 1 |
| [`R261`](R261_hash_seed_sweep) | - RETRACTIONS calls this class "rare: 2 in 83 rounds". E05 was never swept. It is not rare. | 1 |
| [`R262`](R262_the_floors_R261_said_it_could_not_reach) | - R261 said these floors need a GPU. They do not. One turn later, I checked. | 17 |
| [`R263`](R263_the_remaining_salted_rounds) | - the five salted cache-only rounds nobody has swept, and one of them concluded a NULL. | 33 |
| [`R264`](R264_how_often_does_R241_hold) | - R241's null is a coin flip. Four seeds established THAT; this measures the RATE. | 49 |
| [`R265`](R265_is_R241s_control_validated_by_noise) | - R241's positive control may be validated BY the noise it is meant to see through. | 32 |
| [`R266`](R266_which_noise_actually_binds) | - three noise sources are stacked under one number. Only one of them is fixable by effort. | 2 |
| [`R267`](R267_what_this_release_can_resolve) | - thirteen rounds established what is not resolvable. This asks what WOULD be. | 1 |
| [`R268`](R268_a_calibrated_detector_and_the_real_MDE) | - R267 refused to read an MDE. Both reasons were mine; this fixes both and reads it. | 1 |
| [`R269`](R269_a_sham_that_can_fail) | - R268's sham was void AS CONCEIVED, not merely as coded. Two shams that can fail. | 1 |
| [`R270`](R270_the_arc_chose_the_coarser_statistic) | - the arc used a statistic 13x coarser than one sitting in the same release. | 1 |
| [`R271`](R271_the_clustering_inflation_with_a_number_on_it) | - R270 built the weak version of the effect it existed to measure. This is the strong one. | 1 |
| [`R272`](R272_the_inflation_with_a_calibration_that_takes) | - R271's pooled arm printed CALIBRATION DID NOT TAKE and my kill never looked at it. | 1 |
| [`R273`](R273_the_inflation_as_an_interval) | - R272 said the inflation is grid-bound at 2.0x. This replaces the grid with an interval. | 1 |
| [`R274`](R274_the_site_MDE_at_fine_resolution) | - R273 showed a coarse grid biases an MDE LOW. R268's site MDE was read the same way. | 1 |
| [`R275`](R275_what_a_replication_can_and_cannot_catch) | - R269 replicated R268 and shared two of its defects. A 2x2 says which one it could catch. | 1 |
| [`R277`](R277_is_necessity_tolerance_free) | - R249's "36.7% necessary" is defined by EXACT class equality. Sweep the tolerance. | 1 |
| [`R278`](R278_can_the_admissibility_gate_ever_fire) | can the admissibility gate ever fire? | 1 |
| [`R279`](R279_was_the_gate_violated_by_its_own_founding_round) | was the gate violated by the round that proposed it? | 1 |
| [`R280`](R280_is_the_gate_unit_coherent) | is the gate unit-coherent, and was the mismatch introduced or always there? | 1 |
| [`R281`](R281_does_the_coherent_gate_admit_this_release) | does the coherent gate admit this release at all? | 1 |
| [`R282`](R282_is_the_saturation_forced_by_sample_size) | is the 75-of-75 saturation forced by sample size? | 1 |
| [`R283`](R283_is_there_headroom_above_a_constant) | is there headroom above a constant | 1 |

<!-- ROUND-INDEX:END -->
