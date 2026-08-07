# R684 · the judge is not in the record

**⭐⭐⭐ 90 rounds vary a judge in executable code. **9 record one in their artifact; 7 record two.**
So for **90%** of judge-varying rounds the scope R683 proved decisive is **unrecoverable without
opening the source** — and the deliverable inherits that.**

## WHY THIS MATTERS AND IS NOT BOOKKEEPING
R683 measured that the ③ separation **resolves at 2B and does not at 0.8B**. **The judge is not a
detail, it is the scope.** A verdict whose artifact does not name its judge cannot be read as
one-judge or two-judge by anyone who does not open the code.

## THE COUNTS (G3 — every category, none hidden)

| | |
|---|---|
| rounds with a `run.py` and an artifact | 360 |
| ⚠ **EXCLUDED** — no judge mentioned in code at all | **270** |
| population — code references a judge | **90** |
| ⭐ RECORDED_MULTI (≥2 judge keys) | **7** — R361 R362 R365 R477 R479 R481 R540 |
| RECORDED_ONE | 2 |
| ⛔ **UNRECORDED** | **81** |
| **share recording the judge** | **10.0%** |

**Controls:** POSITIVE — R361 (two judges in code *and* artifact) → `RECORDED_MULTI`. **g=0** — rounds
mentioning no judge are **EXCLUDED**, not counted unrecorded → 270 excluded, *silence is not a
verdict here*. NEGATIVE — an artifact with no judge key → none. PLACEBO — identical.

## ⚠ I BUILT THE SOURCE SCAN WITHOUT R680's DOCSTRING STRIP, AND IT HALVED THE POPULATION
Every round's header discusses judges in prose. The raw scan counted **179** rounds as
judge-referencing; with comments and docstrings stripped it is **90** — **half the population was
documentation.** R680 established this exact confound and built the tool; **I re-implemented the scan
without importing it.** *Ledger 766, recurring: a validated instrument does not carry itself
forward.*

## ⛔ AND THE REPAIR MOVED BOTH PRE-REGISTERED SCORES ACROSS THEIR BOUNDARIES

| | contaminated | repaired |
|---|---|---|
| **A** — share recording (registered **40% [10,80]**) | **6.7% — OUTSIDE** | **10.0% — INSIDE, at the exact boundary** |
| **B** — multi-judge count (registered **7 [2,14]**) | 8 (+1) | **7 — error exactly 0** |

**Both are reported.** A forecast rescued by a repair I made *after seeing it miss* is not a clean
forecast, and presenting only the post-repair number would hide that the verdict was decided by an
instrument fix rather than by the world. *(Ledger 756, the same shape.)*

## THE CONFOUND IS WHY THIS NUMBER IS 10% AND NOT 3%
**270 rounds mention no judge anywhere and are EXCLUDED, never counted as unrecorded.** Absence of a
judge key is **not** evidence of one judge — a set census has no judge dimension at all. Folding them
in would have manufactured a far worse-looking gap out of rounds the question does not apply to.

## IDENTIFICATION LIMIT
*"Code references a judge"* is **lexical**. A round varying the judge without a catchable name is
excluded, which biases the population **down** and the recorded share **up**. So **10.0% is a
ceiling** on how recoverable the scope is.

## NEXT
Seven rounds record two judges while 81 that vary one record it nowhere in their artifact
(`results/judge_record.json`, fields `multi_judge_rounds` and `counts`). Check whether the 7 agree across their two judges or split the way R683's did:
read each one's per-judge verdict field from its own artifact and tabulate agree / disagree. If they
mostly split, "instrument-dependent" is a property of this benchmark rather than of clause ③, and
that is a different claim from the one now in `STATEMENT.md`.
