# R1093 — ⛔ **clause ③ is FALSE of the released core**, and the dataset card said so all along.

**The decision this round makes safe:** whether clause ③ — *consumes no prompt-specific human
labels* — holds of the object the definition was written from. **It does not.** And this is a
**VERIFICATION of the object's own documentation**, not a discovery.

## ⚠ Prior art in the card — flagged before the result

`data/DATASET_CARD.md` states how CoVal-core is built. The paper template carries a
`prior_art_in_card` column precisely so a result restating the object's own documentation cannot be
reported as a finding. **This round is a verification.** Its value is that the fact had never been
read into this arc's record.

## Q2 · The card, quoted rather than paraphrased

> **Core rubrics**: … We construct CoVal-core using a combination of **language-model-assisted
> synthesis and human review**. Our process first rewrites all rubric items to have positive weight
> and then merges semantically redundant rubric items … it aims to select up to four rubric items
> with the **highest average ratings** …

> **Rubric item authoring**: Finally, **the annotator wrote down a few rubric items** for this
> prompt … with an associated signed weight from −10 to +10 …

> **CoVal-core rubrics are experimental**: … an experimental, **LM-synthesized distillation of
> CoVal-full**: we merge, negate, and select a small set of highly rated items …

**CoVal-full is annotator-authored and annotator-rated. CoVal-core is a distillation of it, selected
by average rating, with human review. So the core consumes prompt-specific human labels by
construction — clause ③ is false of the instance.**

## Q1 · The schema — the provenance is in prose, not in the data

| key | fields | items |
|---|---|---:|
| `coval_full` | `rubric_item_id`, `criterion`, `scores` | 15,248 |
| `coval_core` | **`criterion` only** | 3,899 |

**No per-item provenance field on the core, over all 986 conversations** — no `rubric_item_id`, no
author, no link back to the full items it was synthesised from. The construction is documented in
prose and **not recorded per item**, so ③ can be read off the card and cannot be audited from the
data.

## ⚠ Why nobody in this arc checked it

The clause table retains ③ as **"provenance, no bar"**, with comparator and criterion both
`invariant`. **That reads as *nothing to measure*.** A clause with no threshold is not a clause with
no truth value — and that reading is what kept it unexamined while eleven rounds went after ②′.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE the scan sees `rubric_item_id` and `scores` on `coval_full` | PASS |
| g=0 a key that exists nowhere returns **0** items, not a default | PASS |
| NEGATIVE the scan covers **all 986** conversations, not the first 200 | PASS |
| SHAM `annotators.jsonl` yields no rubric items rather than an error read as a zero | PASS |
| PLACEBO a second read returns identical field counts | PASS |

**Noise floor: none.** Both questions are deterministic reads; inventing a resampling would be
decoration.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| auditing whether the human review described actually occurred | **N/A** | the review record, which the release does not ship |
| auditing ③ **from the data** | **N/A** | a per-item link from a core criterion to its source items |
| cross-release | **N/A** | a second release |

`run.py` · `results/provenance.json`
