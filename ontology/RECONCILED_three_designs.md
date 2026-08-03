# The typed normative record — reconciled

2026-07-31. Three designs: `ONTOLOGY.md` (mine), and two clean-context designs given the question
and the data and never my field list. This file is the merge. **Where they disagreed the
disagreement was settled by measuring the object, not by taking the majority** — one design's
central objection was checkable, and checking it produced the sharpest result of the day.

Below, `[3/3]` marks a requirement all three reached independently. Convergence from designs that
could not see each other is evidence about the problem; it is not three votes.

---

## 1 · What all three required, independently

| requirement | why it recurred |
|---|---|
| **direction / polarity** `[3/3]` | text can survive a sign flip intact |
| **force: veto vs weighed** `[3/3]` | a rule meant to end the discussion, scored on an additive scale, is destroyed silently and invisibly in the text |
| **scope / domain of application** `[3/3]` | a rule applied everywhere has been changed even if every word survives |
| **exceptions / carve-outs** `[3/3]` | removing a carve-out makes a rule *stricter* than its author licensed — a change in neither party's authorized direction |
| **author-supplied witnesses** `[3/3]` | otherwise "does the response satisfy the rule" is answered by a later interpreter, never by the author |
| **rating ≠ authorship** `[3/3]` | a stranger scoring a rule low is input to aggregation; the author scoring it low is an amendment to the rule. One `scores[]` array cannot be both |

**All three also found, separately, that the release has no way to express a veto on a criterion.**
Every criterion is a scalar in −10..+10. The only dispositive channel in the whole release is
`ranking_blocks.unacceptable`, and it is attached to a **response**, never to a criterion. So the
force distinction is not merely uncollected here — it is **unrepresentable in the schema as
released**, and no amount of re-annotation of the existing files can add it.

---

## 2 · The disagreement, and how it was settled

**The claim.** Design B: a single-valued `author_id` on a rule is a *fabrication*, because up to
15 people score the same criterion text from the moment it is recorded; "the framing presupposes a
clean single-authored source event that the earliest recoverable data has already destroyed."

**The rival.** Design A and mine: authorship is recoverable, because the rater-count distribution
has two disjoint modes. Design A raised its own caveat — the inference "collapses the moment two
annotators independently submit the same wording."

**Both were testable. Both were tested (r142 + this pass, full 986 conversations, no model run).**

| measurement | result | consequence |
|---|---|---|
| items rated by exactly 2 or 3 people | **0** (one-population model expects 1,235) | two disjoint populations |
| pre-seeded item's raters as a share of its panel | mean **99.3%**, exactly all of them for **83.5%** | the n≥4 population really was shown to everyone |
| prohibition share, self-authored vs pre-seeded | **31.1%** vs **16.0%** | independent second signature; "rated by few" predicts no polarity difference |
| within-conversation duplicate-text groups | **169**, n-profiles all `(1, k≥10)` — **zero `(1,1)`** | A's collision case does not occur; a duplicate is a person re-typing a seeded item |
| n=1 wordings recurring across conversations | **9** | negligible |

**Resolution: B is right about 36.5% of the pool and wrong about 63.5%.** The pool is a mixture.
For the 9,684 self-authored items the sole scorer is the author and the record is genuinely
single-authored. For the 5,564 pre-seeded items there is **no author at all** — they are the lab's
own text, and treating them as human normative input is the error B's objection actually catches.

Averaging the three designs would have produced a hedge. Measuring produced a partition.

---

## 3 · What each design contributed that the others missed

**Design A — the transformation is an object.** Model each hop as a first-class **lineage edge**
(`IDENTITY, PARAPHRASE, POLARITY_FLIP, MERGE, SPLIT, SCOPE_NARROW/WIDEN, FORCE_UP/DOWNGRADE,
DROP_BY_RULE, SUPERSEDE`) with `terminal_disposition` **defaulting to `VANISHED`** unless an edge
justifies otherwise. Its strongest single idea: a `DROP_BY_RULE` must name a **re-runnable**
`rule_id`, and *a drop whose rule cannot be re-run and reproduced is downgraded to `VANISHED`*.
That converts "the compiler dropped it for a reason" from a claim into an obligation.

**Design B — dropping is the normal case, and an auditor without a field for it will cry wolf.**
74.4% of items are dropped at synthesis (15.46 → 3.95 per prompt, full set). Most of those drops
are correct: low-rated, redundant with a survivor, contradicted by something better. Without a
first-class `exclusion_reason` (`REDUNDANT_WITH_SURVIVOR` + pointer / `LOW_RATED` / `CONFLICTING` /
`NOT_REVIEWED`), "text gone, effect survives elsewhere" and "text gone, correctly, because the pool
rated it −8" are **indistinguishable** — and an audit will flag the majority of normal pipeline
behaviour as anomalous. This is the schema-level answer to the objection that "maybe dropping was
right" is incoherent as stated: it is not incoherent, it is *unrecorded*.

**Mine — the weight axis is three things stacked.** CoVal's −10..+10 conflates *direction*,
*importance*, and *how strongly this person feels*, and the compiler then reads the scalar as
importance. Three quantities on one axis cannot be separated downstream. Plus `provenance_class`
and `rating_population`, because a mean over one person and a mean over seventeen are different
measurements that this pipeline ranks against each other.

---

## 4 · Structural facts about the release, measured on all 986 conversations

1. **`coval_core` items carry exactly one key — `criterion` — in 3,899 of 3,899 cases.** Force is
   not weakened by compilation; it is **deleted by construction**. No weight, sign, rank or
   provenance survives into the compiled rubric for any rule.
2. **7.8% of core items match a source criterion verbatim; 30.8% at ≥0.80 similarity.** So **69.2%
   of surviving rules have no recognisable source**, and text-similarity lineage recovery — the only
   method available without stored edges — is the weakest link in any audit of this artefact.
3. **74.4% of items are dropped**, with no field anywhere distinguishing a licensed drop from a
   vanished one.
4. **The judge and decision stages do not exist in the release.** Responses are ranked by humans
   directly; nothing is ever scored against `coval_core` programmatically. So `J`, `S`, `D` in the
   chain are **ours**, not theirs, and every claim routed through them is a claim about our
   instrument. Both independent designs reached this separately.

---

## 5 · The merged record

Three record types, because one cannot carry them: **RULE** (invariant under who touches it),
**PERSON** (invariant under which rule), **EVENT** (one row per hop, invariant under which rule
passed through). Putting a person-fact on a rule is the error that makes "whose values are these?"
unanswerable, since the aggregate then has no slot to disagree in.

| record | field | type | members | present |
|---|---|---|---|---|
| RULE | `text` | text_free | verbatim, always retained | • |
| RULE | `polarity` | enum | `require prefer permit discourage forbid` | sign only |
| RULE | `force` | enum | `veto hard_constraint strong_default soft_preference` | **unrepresentable** |
| RULE | `compensable` | boolean | — | × |
| RULE | `scope` | jsonb | `{applies_when[], excludes_when[], generality ∈ this_prompt/topic_class/general}` | × |
| RULE | `exceptions` | jsonb | `[{condition, effect ∈ suspend/reverse/narrow}]` | × |
| RULE | `witness_pos` / `witness_neg` | jsonb | ≥2 each, author-supplied | × |
| PERSON | `author_id` | id | — | ○ (63.5%) |
| PERSON | `importance` | scalar 0–3 | split out of the −10..+10 axis | conflated |
| PERSON | `confidence` | enum | `certain probable tentative` | × |
| PERSON | `subjectivity` | enum | `factual contested personal` | • |
| ENDORSEMENT | `(rater_id, statement_id, rating)` | — | points **at** a rule, never mutates it | • (undifferentiated) |
| EVENT | `input_rule_ids` | set | many→one, supports merges | × |
| EVENT | `edge_type` | enum | the 11 above | × |
| EVENT | `exclusion_reason` | enum | `redundant_with(ptr) low_rated conflicting not_reviewed` | × |
| EVENT | `rule_id` | fk | must be **re-runnable and reproduce the drop** | × |
| EVENT | `stage_run_id` | id | model/build version of this hop | × |
| DERIVED | `terminal_disposition` | enum | `survived_intact survived_paraphrased merged dropped_by_rule` **`vanished`(default)** | × |

`provenance_class ∈ {self_authored, pre_seeded}` sits on RULE as a pipeline fact, and is the field
that decides whether `author_id` exists at all.

---

## 6 · What the reconciled schema still cannot represent

- **Rules about rules** — "never let a safety item be outvoted" constrains the aggregator, and the
  aggregator is not typed by this record.
- **Joint unsatisfiability** — a set of individually satisfiable rules that cannot all hold is
  invisible field-by-field. That is the joint-repair experiment, not this table.
- **Silence** — someone who never wrote a rule about X is indistinguishable from someone who thinks
  X does not matter.
- **Emergent force** — three soft preferences that together function as a hard constraint. The
  schema can only sum or order what was declared.
- **Contested scope evaluation** — whether a context satisfies a condition can itself be a value
  judgement, and there is no field for how contested that judgement is.
- **Merge editorial acts** — when two merged sources disagree on force, which one was overridden and
  why is new information, not reducible to a preserved/not-preserved check.

---

## 7 · The prediction this schema exists to test

> **A pipeline that records only content preserves content and loses force, and the loss is
> invisible to any audit that reads text.**

Fact 1 above is already one-directional evidence: force is deleted by construction at compilation.
What is not yet established is whether that deletion *changes behaviour* — a rule may lose its
recorded force and still be honoured, if the compiler's prose carries it. That is the mutation
suite's job, and it is the first thing the flagship experiment must answer.

**Stop C stays armed:** if a typed compiler and a prose compiler behave identically on the mutation
suite under matched conditions, this schema is unnecessary and the finding is that typing does not
matter.
