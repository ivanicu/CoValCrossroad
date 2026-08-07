# R466 · ③'s two instruments range over **disjoint id spaces** — the join, not the clause, is the defect

**The decision this round makes safe:** whether *"`coval_core` survives ③"* is supported.
**Not by measurement.** `UNVERIFIED` — never OVERTURNED.

## ⭐ Asking the instrument, not the document, found where it bites

`clause3_as_written.partition` over every arm with a satisfaction file: **39 EXCLUDED, 43 ADMITTED,
19 UNKNOWN** — and **`coval_core`, the object the definition was written from, is UNKNOWN.** The
definition's own paradigm case cannot be classified by the instrument that implements ③.

The document resolves that with a **second** instrument: *"only **0.0779** of its criteria appear
verbatim in its own prompt's rubric"* (R443). ⛔ But ③ **as derived by R444 from `select_core.py`**
forbids consuming the **human rankings** and the **annotator importance scores**. **Containment
measures copying of the rubric's TEXT — a third thing.** §4: *name the instrument's unit and the
claim's unit as two separate strings and require them to be EQUAL.*

## Result — the join fails before the units can even be compared

| | |
|---|---|
| rubric-text ids (`conversation_rubrics.jsonl`) | **986** |
| ranking ids (the targets ③ forbids consuming) | **1078** |
| **intersection** | **0** |

> ⛔ **Disjoint id spaces.** Containment lives entirely in the rubric's id space; the rankings live in
> another. **They cannot be joined on disk without a mapping, and none was used.** So containment is
> not a weak proxy for ③ — **it is computed over a population that does not intersect the one ③'s
> predicate ranges over.**

**The decisive construction was therefore unrunnable**: a label-reading arm needs rankings to read,
and there are none for these prompts. **Reported as UNVERIFIED, not as a refutation.**

## Controls — all PASS, which is what makes the negative readable

| control | returned |
|---|---|
| **ANCHOR** — reproduce R443's committed containment | **0.0778** vs **0.0779** ✅ *independent path* |
| **FLOOR** — cross-prompt sham | **0.0000** ✅ |
| **POSITIVE** — an arm copied verbatim from the prompt's own rubric | **1.0000** ✅ *without it, a low number is silence* |
| g=0 — containment against its own texts | 1.0 **by construction** — printed as a DERIVATION |
| **EMPTY POPULATION** | the first parser guessed the schema, found **0** prompts, and the round **exited 2** rather than reporting a containment over an empty set |

**The instrument works and simply cannot be pointed at ③'s population.**

## ⛔ Three defects in this round, all caught by running it

1. **A NaN routed to a substantive verdict.** `nan <= threshold` is `False`, so the branch fell
   through to `W-EQUIVALENT` on a value that does not exist. **A NaN must hard-fail to UNVERIFIED**;
   it now does.
2. **The parser guessed the schema** and found 0 prompts. The real layout —
   `{conversation:{id}, coval_full:[{rubric_item_id, criterion, scores}], coval_core:[{criterion}]}` —
   came from **asking the object**. ⭐ And that layout is itself worth noting: **the released core
   ships in the same record as the annotator scores ③ forbids consuming.**
3. **The exploratory id-check ran outside the round**, and only moving it inside turned "my
   construction failed" into "the two instruments cannot be joined" — retraction 276's remedy,
   applied.

## What this changes

- **Not overturned:** clause ③, or the released core's status under it. The finding is a **defect in
  the join**, and UNVERIFIED is never folded into OVERTURNED.
- **Downgraded:** the document's *"`coval_core` survives ③"* now rests on an instrument whose
  population does not intersect ③'s. It must be restated as what it is — a containment measurement —
  or supported by a mapping between the two id spaces.
- **Standing:** **19 arms are UNKNOWN under ③, the paradigm case among them**, and the definition
  still owes a third verdict.

## Impossible here, named

- **deciding the other 18 UNKNOWN arms** — needs each one's construction history, which R465 showed
  the object does not carry.
- **the label-reader construction** — needs a mapping between the rubric and ranking id spaces; none
  exists on disk, and inventing one would decide the question by assumption.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
