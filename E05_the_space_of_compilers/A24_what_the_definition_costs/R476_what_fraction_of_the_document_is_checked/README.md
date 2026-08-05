# R476 · What fraction of the document is actually checked

**The decision this made safe.** Whether `assurance/definition_matches_the_record.py`'s **PASS** may
be read as *"the document's numbers are verified"*. It may not. The gate checks **28.0%–69.2%** of
DEFINITION.md's numeric claims, depending on what counts as one.

## Why the round exists

R475 corrupted `+0.1298` with a substring replace and **the gate returned PASS**, because that number
is not among its anchors. The gate reported *"302 of 302 assertions"* — a fact about the **list**. A
count with no denominator reads as coverage.

## The measurement

Coverage is decided **by span, never by value**: a number is covered iff its character span lies
inside the span an anchor captured *at that site*. Value-matching would mark every `0.5` in the
document as checked because one anchor captures a `0.5` somewhere else.

| extractor | numeric claims | covered | coverage | 95% Wilson |
|---|---|---|---|---|
| `bold_any` — author emphasised it | 169 | 117 | **69.2%** | [0.6191, 0.7570] |
| `decimal` — any decimal | 443 | 156 | **35.2%** | [0.3091, 0.3977] |
| `sig2plus` — ≥2 dp, i.e. a measurement | 391 | 134 | **34.3%** | [0.2974, 0.3911] |
| `all_number` — every number | 1007 | 282 | **28.0%** | [0.2532, 0.3086] |

**Denominator spread 5.96×.** World **C** fires alongside MIXED: *"coverage" is not a single
well-posed quantity here*, and the range is the answer rather than a defect in the measurement.

## Controls

| control | returned |
|---|---|
| POSITIVE — a site an anchor actually captured (`r475_ceil_abs`, `0.8437` at char 41653) is COVERED | ✓ |
| g=0 — `+0.1298`, the value R475 corrupted while the gate passed, is UNCOVERED | ✓ |
| NEGATIVE — a literal absent from the document is extracted 0×, and seen once injected | ✓ |
| PLACEBO — coverage under never-matching anchors is exactly 0 | ✓ |

## What was produced, not just measured

The gate now **prints its own denominator** on every run, and its numbers reproduce this round's
independently — 117/169, 156/443, 134/391, 282/1007. **A PASS certifies the anchored numbers, never
the document**, and the instrument now says so in its own output instead of in a round README.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R476_what_fraction_of_the_document_is_checked/run.py

Deterministic census · artifact `results/r476_coverage.json` · exit 2 if any control fails.
