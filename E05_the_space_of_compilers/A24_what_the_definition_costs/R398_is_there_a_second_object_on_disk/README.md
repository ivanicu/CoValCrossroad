# R398 — "one release" was never a wall. It was a query nobody ran.

**The decision this makes safe:** *is the campaign's largest limit structural?* **No. A second corpus
with 68,371 human-scored responses has been in `data/` since 2026-07-29, read by no round.**

## Result — `W_SECOND_OBJECT`. Both reader controls pass. **No GPU spent.**

| criterion | measured | threshold |
|---|---:|---|
| rows | **68,371** | — |
| distinct conversations | **8,011** | ≥ 100 ✅ |
| rows with a parseable human `score` | **68,371 — 100.0%** | ≥ 50% ✅ |
| prompts with **≥ 2 distinct** model responses | **26,285** of 27,172 | ≥ 100 ✅ |
| distinct models | **21** (`claude-2`, `claude-2.1`, `claude-instant-1`, `zephyr-7b-beta`, `oasst-sft-4-pythia-12b`, `command`, …) | — |
| **files in this repository referencing it** | **0** | — |

## ⛔ What the register said

> `| transfer to another release | one release |`

**Every transport result in the campaign is bounded by that line**, and R233's limit is stated in the
definition's strongest terms: the fresh responses carry **no human rankings**, so transport is of the
**compilation** and *"never agreement with people"*.

**That sentence described this release, and was silently read as describing the world.**

## ⛔ This campaign's own failure table predicted this exact miss — twice

- *"**a wall never checked** — three permanent limits of a dataset; one was a query never run, and
  the falsifying arithmetic was in the author's own sentence."*
- *"**a retraction feels so much like the end of an audit that nobody asks the cheapest question
  left: does the data have more to give?** Here it had 5× more, sitting on disk, unused through three
  rounds of increasingly careful reasoning about what could not be known."*

**It happened again, larger: 153 MB across two files, fetched two days after the release triple,
absent from `DATASET_CARD.md`, and referenced by zero `.py` and zero `.md` in the repository.**

## Controls

| | returned |
|---|---|
| **READER (+)** | a known-good CoVal file yields **50 rows** — `PASS`. A count of zero from a reader never shown to return non-zero is silence, not evidence the file is empty |
| **READER (−)** | a nonexistent path yields **0 rows**, not a traceback a caller could misread as "no data" — `PASS` |
| **PRIOR ART** ⭐ | the zero-references claim is **re-measured inside the round**, not quoted from my shell history — it is the single sentence that makes this look like a discovery, so it is the one that must not be taken on trust |
| **MEMORY** | streamed line by line; nothing accumulates but counters. 68 MB, and **an OOM does not raise — it kills the session** |
| **MULTIPLICITY** | all four criteria printed regardless of verdict, so passing three and failing one could not have been reported as a pass |

## ⚠ What this round did NOT do

**It computed no core, ran no transport test, and reports no effect.** *A second object exists* is the
whole claim. The excitement is the red flag, which is why the design is a **census** — one line of a
`head` showed fields that *look* like exactly what the definition needs, and that appearance was worth
nothing until counted.

## Register

| criterion | status |
|---|---|
| **scores comparable to CoVal's rankings** | **UNTESTED** — needs a shared population or a linking study. Named, not assumed in either direction |
| **whether any core transports** | **UNTESTED** — a later round |
| **a rubric for the second corpus** | **ABSENT** — CoVal's `full` has no counterpart here, so clauses defined against `full` **still cannot transport**. Clause ② and the human-agreement target can |
| **provenance and licence** | **D5** — the schema resembles a published dataset, but naming it from field names is inference and **the finding does not need the name** |

## What moved in `DEFINITION.md`

Both the register row **and** the transport section it governed were corrected — a correction has to
reach the artifact that provoked it, not only the round that found it. **And all five numbers above
were added as assertions to `definition_matches_the_record.py`** (51 → 56): a retraction that states
counts must be re-derivable exactly like the claims it replaces, or the correction becomes the one
sentence in the document nobody can check.

> ⚠ **The gate immediately caught my first attempt** — the anchor regex missed because my bold wrapped
> the whole clause, **the identical trap R373 paid for.** The document was reworded; the assertion was
> not weakened.

## The sentence I can no longer write

> *"transport is of the compilation and never agreement with people"* — **as a property of the
> problem.** It is a property of one file, and the file that would test it was already on the disk.

Artifact: `results/r398_second_object.json`, source-stamped.
