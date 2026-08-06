# R814 · the annotator main effect is 9.42%, and the verdict straddles my own threshold

`run.py` · `PREREGISTRATION.txt` · `results/rater_main_effect.json` · 968 prompts × 1,012 annotators
× 15,593 cells · **WORLD C** · two hash seeds byte-identical, md5
`645029e4ea0f99d8560b79f42173f6c1`

## THE DECISION THIS MAKES SAFE

**Annotators do have a main effect, and it is modest.** Clause ③ holds out the annotator; that
holdout can remove **at most 9.42%** of the variance in the leave-one-out agreement table.

| | observed var of annotator means | permutation null | excess | **rater share** |
|---|---:|---|---:|---:|
| **weighted** (pre-registered headline) | 0.004298 | 0.001753 [0.001608, 0.001901] | +0.002545 | **9.42%** |
| unweighted | 0.005203 | 0.002440 [0.002116, 0.002840] | +0.002763 | **10.23%** |

⚠ **The verdict straddles my own threshold.** The preregistration set WORLD B at >10% and WORLD C
below; weighted gives 9.42% (**C**), unweighted 10.23% (**B**). **D3 pre-registered reporting both
because weighting is a defensible-choice axis** — which is the only reason this reads as a boundary
rather than as a result. The honest statement is **~9–10%**, not a side of a line.

**The remaining ~90% is prompt plus interaction.** ⚠ D4, written before the run: on a crossed design
the residual absorbs the interaction, so a modest share means **no large ADDITIVE main effect**, not
that annotators are interchangeable.

## ⛔ CHECK #416 KILLED R813's NEXT WITH A THREE-LINE GAUGE TEST ON ZERO REAL DATA

R813 closed by calling it a **tension** that annotators agree pairwise only 0.551880 of the time
while their errors look independent. Simulating a crossed panel at planted `rater_sd`:

| planted rater_sd | pairwise agreement | rater ICC |
|---:|---:|---:|
| 0.00 | 0.6230 | **0.0002** |
| 0.15 | 0.6244 | 0.1751 |
| 0.35 | 0.6223 | 0.3803 |

**Pairwise agreement is flat while the ICC moves by three orders of magnitude.** The two quantities
are independent; there was never a tension. That is realstat §4's *"the closing sentence is a claim
and never gets a control"* — **committed in a NEXT written one round after this project filed a
ledger entry about that exact mode.** The cost was three lines of simulation to find.

## ⭐ E3 · THE DOSE LADDER, ON BOTH THE OBSERVED AND A RATER-NULLED TABLE

| planted g | observed table | fires | **rater-nulled table** | fires |
|---:|---:|---|---:|---|
| 0.00 | 9.43% | yes | **0.00%** | **no** |
| 0.02 | 10.41% | yes | 0.50% | no |
| 0.05 | 15.59% | yes | 6.16% | yes |
| 0.10 | 29.95% | yes | 22.10% | yes |
| 0.20 | 56.73% | yes | 52.09% | yes |

**Monotone on both.** The rater-nulled column is the control that can fail: **exactly 0.00% at g=0**,
firing from g=0.05.

## ⛔ AND MY FIRST g=0 CHECK WAS MIS-SPECIFIED IN THE MIRROR DIRECTION

It required the **observed** table not to fire at g=0 — which **presumes the real data has no rater
effect, the very thing under test**. It printed FAIL against a real 9.43%. That is §4's *"the control
presupposes a non-null effect"*, inverted: mine presupposed a **null** one. A true zero exists only
on a table whose rater structure has been destroyed, which is why the ladder is now run on both.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R793's `CEIL_H` recomputed from **this round's own assessment table**: **0.551880** vs committed **0.551880** | PASS, else exit 2 |
| PLACEBO | the statistic against **itself**: **0.0e+00** | PASS — exactly 0 |
| POSITIVE | the dose ladder above, monotone on both tables | PASS |
| g=0 | the rater-nulled table at g=0: **0.00%, does not fire**; at g=0.20 it does | PASS **after repair** |
| NEGATIVE | the permutation null itself, 500 draws: mean **0.001753**, sd **0.000075**, 95% **[0.001608, 0.001901]** — it has spread | PASS |
| NOISE FLOOR | 20 half-splits of the annotator panel: **9.71% ± 0.79%** | consistent with the headline |
| POPULATION | prompts carrying the leave-one-out statistic: **968 / 968, 0 dropped** | stated |

⚠ **A second defect, caught by a crash rather than a check**: the noise floor passed a subsetted
`agree` against the closure's full-length `rows_a` and raised `ValueError`. It failed loudly, which is
the only reason it did not silently compute the statistic on mismatched rows.

## WHAT DIED

- **R813's "tension"** — pairwise agreement and the rater main effect are independent, shown on
  synthetic data before any real number was computed.
- **"the annotator panel carries almost no shared error"** — R813's indirect reading, from a
  negative control I had already flagged as weak. Directly measured, the effect is **9.42%** and
  clears its null.
- **my own g=0 criterion**, which presupposed the answer.

## WHAT SURVIVES — AND THIS ROUND ADDS

R813's design effects, now explained rather than inferred: a 9.42% rater share is exactly the size
that produces a design effect of 1.14–1.30 rather than ≥1.5. And a number clause ③ can be written
against: **an annotator holdout is worth at most 9.42% of this table's variance.**

## SCOPE

968 prompts × 1,012 annotators × **15,593 (prompt, annotator) cells**, load median 16 max 32 ·
leave-one-out agreement, so no annotator is compared with itself · label-permutation null, 500 draws
· annotator identity from `metadata.assessments[].annotator_id`, which `load_targets()` discards ·
first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| separating the rater×prompt INTERACTION from the residual | repeated judgements by the same annotator on the same prompt; the release has one per pair — **checked**, and it is why D4 bounds the claim to "no large additive effect" |
| a rater share free of the weighting choice | a balanced design; loads run median 16 to max 32 — **checked**, and both weightings are reported rather than one chosen |
| the same decomposition on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances — **checked** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The rater share is **9.42% weighted / 10.23% unweighted**, straddling the pre-registered boundary, and
the noise floor across annotator half-splits is **9.71% ± 0.79%** — so the estimate is stable and the
threshold was the fragile part, not the measurement. What that leaves is the question clause ③
actually turns on, which this round bounds but does not answer: D4 says the residual absorbs the
rater×prompt interaction, and the release ships one judgement per (annotator, prompt) pair, so the
interaction cannot be separated from noise here. The step is to ask what the definition should say
when a component it depends on is **structurally unidentifiable on its own site**: either clause ③
names the additive effect it can bound at 9.42%, or it names a quantity the release cannot measure
and must say so. That is a writing decision resting on a measured bound, and it needs no further
compute — which is why it belongs to the `DEFINITION`, not to another round.
