# R232 — auditing every wall this arc asserted

**Arc E05·A22.** `realstat` §4, last row: *"a wall never checked — one was a query never run, and the
falsifying arithmetic was in the author's own sentence. **An unchecked wall is UNVERIFIED, never
SETTLED.**"*

E05 asserted **five** structural impossibilities across six rounds and **ran a query for none of
them**. They are load-bearing — R224's entire bound rests on `m = 4`, R223's lineage stratification
rests on there being no source id, every register entry since R220 rests on `Y` being absent. **An
asserted wall that turns out false does not weaken a conclusion; it deletes it.**

## The audit

| wall | verdict | evidence | what rests on it |
|---|---|---|---|
| `m = 4` for every prompt | **HOLDS** | `num_candidates` = 4 on **18,384/18,384** assessments; 4 responses on **1,078/1,078** prompts | R224's bound, every `k_max`, the `m = 6` recommendation |
| no criterion-by-response satisfaction | **HOLDS** | rubric item fields are exactly `criterion · rubric_item_id · scores{annotator_id, score}` | r04's judge rebuild and every instrument caveat since |
| no `source_criterion_id` | **HOLDS** | `coval_core` items across **all 986** rubrics carry exactly one field: `criterion` | R223's lineage strata, R222's provenance axis |
| no `Y` | **HOLDS** | 14 top-level fields, none of them a model output | C4 in the paper, every register entry since R220 |
| `unacceptable` is long-form only | **HOLDS** | non-empty on **4,901/18,384 = 0.2666**, reproducing R220's independently measured 0.2666 | R220's veto axis, R231's human population |

**No sampling.** Every row of every file — `head -N` is a stratum, not a sample, and this repository
has been caught by that before.

## The audit's own controls

- **positive** — a wall known to be **false** was included on purpose: *"the release ships no
  demographics."* The audit flagged it **FALSE** (present on 18,384/18,384 rows). **An audit that has
  only ever confirmed is not an audit.**
- **negative** — a wall previously measured independently (R220's 0.2666) reproduces to four
  decimals. The reader is not broken.

## The result

**5 of 5 hold. Not one moved.** And that is still worth the round:

> They were asserted across six rounds and this is the **first query run against any of them**. Their
> status changes from **UNVERIFIED to VERIFIED** even though their values do not. Those are different
> things, and a project that cannot tell them apart is the one that publishes a permanent limit
> which was a query nobody ran.

The `coval_core` finding is the sharpest of the five: **across all 986 rubrics, every core item
carries exactly one field — `criterion`.** No weight, no source, no type, no scope. Everything R222
and R223 inferred about the compilation was inferred because that is the entire artifact.

## Register

Whether a wall is **insurmountable** rather than merely true *here* is a claim about future releases
and **no query can settle it**. This audit establishes only that the five hold of these files.

## The sentence that can no longer be written

*"The release structurally cannot support X."* — as an assertion. It now can be written as a
citation, which is a different sentence.
