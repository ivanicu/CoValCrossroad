# The typed normative record — my design

Written 2026-07-31, before the two independent designs land. Under the triple-blind rule this file
is one of three; the other two were given the question and the data and never this file. Where the
three disagree, the disagreement is the finding and gets tested, not averaged.

---

## What the record is for

A rule written by one person must survive nine arrows:

```
N --A--> G --C--> R --J--> S --D--> Y
```

`N` individual normative statement · `A` aggregation/selection · `G` collective specification ·
`C` compiler · `R` executable rubric · `J` judge · `S` per-criterion scores · `D` decision ·
`Y` chosen behaviour.

**The record exists so that "did N survive?" is a computation and not a reading.** Every field
therefore carries a falsification test: the concrete thing you compute to show *this field was not
preserved*. A field with no such test is decoration and is not in the table.

**Three failures the record must tell apart**, because prose cannot:

| | text downstream | force downstream |
|---|---|---|
| survived | present | present |
| **hollowed** | **present** | **absent** |
| **rerouted** | **absent** | **present** (carried by a different item) |

A pipeline that reports "your criterion is in the rubric" is answering the text column only.

---

## The fields

`•` = present in the CoVal release · `○` = recoverable by inference (r142) · `×` = must be collected

| # | field | type | members / range | falsification test | rel. |
|---|---|---|---|---|---|
| 1 | `text` | text_free | — | verbatim; never encoded away. Any typed field disagreeing with `text` is a schema failure, not a data point | • |
| 2 | `author_id` | id | — | two records with the same `author_id` and contradictory `polarity` on the same object ⇒ identity is not being tracked | ○ |
| 3 | `provenance_class` | enum | `self_authored` `pre_seeded` `unknown` | count raters per item; a population with an empty n∈{2,3} band is two populations (r142) | ○ |
| 4 | `rating_population` | enum | `author_only` `panel` | a selection rule that ranks `author_only` means against `panel` means without stratifying is comparing a draw to an average | • |
| 5 | `polarity` | enum | `require` `prefer` `permit` `discourage` `forbid` | flip it in the source; the downstream score on a witness must move in the predicted direction. No move ⇒ not preserved | • (sign only) |
| 6 | `normative_type` | enum | `preference` `principle` `veto` `right` `procedure` `uncertainty` | a `veto` whose downstream contribution can be offset by any combination of other criteria has been converted to `preference` | × |
| 7 | `compensable` | boolean | — | search for a response violating the rule that still wins. Exists ⇒ `compensable=false` was not preserved | × |
| 8 | `scope` | jsonb_structured | `{applies_when[], excludes_when[]}` | score matched in-scope and out-of-scope witnesses. Equal movement ⇒ scope discarded | × |
| 9 | `exceptions` | jsonb_structured | list of `{condition, effect ∈ suspend/soften/reverse}` | build a witness satisfying an exception; if it is still penalised, the carve-out was dropped | × |
| 10 | `priority` | scalar_with_range | 0–3 ordinal | pair two rules with declared precedence, build a witness where they conflict; the loser winning ⇒ precedence lost | • (as −10..+10 weight, conflated with importance) |
| 11 | `witness_pos` | jsonb_structured | ≥2 behaviours the author says satisfy it | judge must score these above `witness_neg`. Fails ⇒ the rubric item is not this rule | × |
| 12 | `witness_neg` | jsonb_structured | ≥2 behaviours the author says violate it | as above, inverted | × |
| 13 | `subjectivity` | enum | `factual` `contested` `personal` | a `personal` rule aggregated by majority has been silently promoted to `contested` | • |
| 14 | `author_confidence` | enum | `certain` `probable` `tentative` | property of the author, not the rule — see the boundary below | × |

**Weight is deliberately not a field of the rule.** CoVal's −10..+10 conflates *direction*
(field 5), *importance* (field 10) and *how strongly this person feels* (field 14) into one scalar,
and the compiler then reads that scalar as importance. Three things on one axis cannot be
disentangled downstream, and this is where I expect the largest preservation loss.

---

## The boundary that must not be crossed

| belongs to | fields | why it matters |
|---|---|---|
| **the rule** | 1, 5, 6, 7, 8, 9, 11, 12 | invariant under who wrote it |
| **the author** | 2, 10, 13, 14 | two people can attach different priority to the *same* rule; storing priority on the rule destroys that and makes disagreement unrepresentable |
| **the pipeline** | 3, 4 | facts about how the record was produced, not about its content |

Putting an author property on a rule is the error that makes "whose values are these?"
unanswerable, because the aggregate then has no slot to disagree in.

---

## What this schema cannot represent

1. **Rules about other rules** — "never let a safety item be outvoted" has no home here; it is a
   constraint on `A`, and `A` is not typed by this record.
2. **Rules whose content is a procedure over time** — "ask before assuming" is a sequence
   constraint; `witness_pos` can only sample it, never characterise it.
3. **Interaction** — a set of individually satisfiable rules that are jointly unsatisfiable is
   invisible field-by-field. Detecting that needs the joint-repair experiment, not this table.
4. **Silence** — a person who never wrote a rule about X is indistinguishable from one who thinks X
   does not matter. The release cannot tell these apart and neither can this record.

---

## Where the release actually stands

Of 14 fields, **4 are present, 2 are recoverable by inference, 8 must be collected.** The eight
missing are exactly the ones that carry *force* rather than *content* — type, compensability,
scope, exceptions, both witness sets, and confidence. Which is the programme's first prediction:

> **A pipeline that records only content will preserve content and lose force, and the loss will be
> invisible to any audit that reads text.**

The prediction is falsifiable. If typed and untyped compilers behave identically on the mutation
suite, this schema is unnecessary and the memo's Stop C fires.
