# R442 · the definition's extension is **5 arms as implemented, 1 as written** — and neither is the published five

**The decision this round makes safe:** what the definition actually admits. **The document states
two incompatible answers and reconciles neither.**

## ⛔ The announced intersection was forced

R360 commits `clause23_admits`; R440 measured ④ excluding 0 and R441 measured size half A excluding
0 among ②∧③∧④. **The extension *is* `clause23_admits` — a lookup.** *Eleventh announced step checked,
seventh killed.* But the lookup surfaced what nobody had looked at.

## Result

| | |
|---|---|
| **EXT_impl** — ③ as **implemented** (the hand-written 4-arm set) | **5**: `coval_core, topw_k3, topw_k4, topw_k6, topw_k8` |
| **EXT_writ** — ③ as **written** (also excluding `topw_k`) | **1**: `coval_core` |
| the published five | `coval_core, topabs_k4, topvar_k4, topw_k4, topwvar_k4` |
| **EXT_impl ∩ published** | **2 of 5** |

## ⭐ Two findings, and the second is the one this document is named after

**① The definition does not reproduce the published answer.** Its boundary runs along the
**selector** axis, not the k axis: it admits `topw` at **four sizes** (k=3,4,6,8) and rejects **three
sibling selectors** at k=4 (`topabs`, `topvar`, `topwvar`). Only 2 of the published 5 survive.

**② Under its own written clause ③, the extension is one arm — the released core.**
`DEFINITION.md` says, in its own words, that `topw_k` is **"not producible from the conversation
alone"** (DERIVED, from a 95.3% annotator overlap census). *"Producible from the conversation
alone"* is the definition's **own opening phrase**. So ③ as written excludes `topw_k` — and removing
those four leaves `{coval_core}`.

> **That is "the definition describes the instance" at the level of the whole conjunction, not one
> clause.**

⚠ **What this is NOT:** a claim that ③'s derivation is wrong. The round takes the document at its
word and computes the consequence. **If the derivation stands, the extension is one arm; if it
falls, `topw_k` returns and the extension is five. The document currently states both and reconciles
neither** — the `declared ≠ implemented` failure, in the definition's extension.

## Controls

| control | returned |
|---|---|
| **POSITIVE — rebuild the extension the campaign uses** | matches R360's committed `clause23_admits` **exactly** ✅ |
| g=0 — the `as written` filter with an empty exclusion set | no-op ✅ |
| **NEGATIVE — the selector filter, both directions** | selects the 8 `topw_k` arms **including `topw_k4_sham`**; rejects `topabs_k4`, `topvar_k4`, `topwvar_k4` ✅ |
| PLACEBO — a filter matching nothing | removes **0** ✅ |

⚠ **7 arms have selectors the source cannot name** (`coval_core`, `coval_core_sham`, `gen`,
`gen_sham`, `generic`, `promptecho`, …) — reported, not silently bucketed.

## ⛔ The control failed first, and it was right to

The first version matched `^topw_k\d+$` and validated it against a "known set" defined by
`startswith("topw_k")` — **two patterns of my own, compared to each other.** They disagreed on
`topw_k4_sham`, and the control failed with nothing to adjudicate between them.

**The fix was to stop inventing patterns and read `corebench/select_core.py:51`**, which enumerates
the nine selectors this campaign builds arms from. An arm's selector is the **longest** of those its
name starts with — which is what keeps `topwvar_k4` from being read as a `topw_k` arm. The sham
*is* included, because the exclusion is about **provenance**: a sham of `topw_k` read the same
importance scores.

## Impossible here, named

- **re-adjudicating whether `topw_k` is truly non-producible** — R363/R364's job; this round computes
  the consequence of the document's own DERIVED finding.
- **an extension on the second release** — ② admits 0 there (R434); empty by arithmetic.
- **construct validity of "producible from the conversation alone"** — the phrase is the
  definition's, and no release provides an external test of it.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
