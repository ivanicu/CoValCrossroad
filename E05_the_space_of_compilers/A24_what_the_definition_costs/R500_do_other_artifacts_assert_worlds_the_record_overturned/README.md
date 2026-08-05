# R500 · 18 of 98 cited rounds carry an artifact that never learned it was retracted

**Decision this makes safe:** whether R497/R499's laundering was a one-off or a property of the
record. **It is a property of the record.** But the stronger reading — that 18 *worlds* are stale —
is **not** what was measured, and this round's own first verdict string asserted it anyway.

## The measured quantity

| | |
|---|---|
| cited rounds (the provenance gate's own population) | **98** |
| named in the ledger as the **retracted party**, artifact carrying **no** annotation | **18** |
| ambiguous under classification (no arrow in the entry) | 20–29 |
| band once ambiguity is counted | **[18, 47]** |

**Both id-extraction specifications agree exactly on the hard set of 18** — spec-robust on the point.

## Controls

- **POSITIVE, and real rather than imagined** — `git show` recovers R497's artifact *before*
  annotation. It asserts `B (REAL STRUCTURE …)` with no marker, and entry 325 names R497 as
  retracted. **The detector flags it. PASS.** A case that actually occurred, not one invented.
- **NEGATIVE** — the same file, one field changed, now annotated. **Not flagged. PASS.** The
  narrowest possible contrast, so a flag on both would localise the fault to the detector.
- **SHAM** — R499 appears throughout entry 325 as the **corrector**. Classified `corrector, not
  retracted` under both specs. **PASS.** This is the unit mismatch made executable.

## ⛔ What this round got wrong about itself

The first verdict printed **"the gate has been certifying stale verdicts"** off a threshold applied
to the census. **That is a claim about WORLDS derived from a count of LEDGER-ARTIFACT
INCONSISTENCIES** — two different populations, and the difference is the entire subject of the round.
**The verdict string was prose that looked like output**, in the round auditing exactly that drift.

A hand read of 5 of the 18:

| round | what the ledger retracted | artifact world | world stale? |
|---|---|---|---|
| R443 | textual containment was the wrong **proxy** | `W-CORE-SURVIVES` | no |
| R455 | *"the MDE will fall as √(16/3)"* — **an announced arithmetic** | `W-STRONGER` | no |
| R460 | *"the announced audit was a grep"* — **an announced step** | `W-STRENGTH` | no |
| R477 | read the wrong one of two percentiles | `A (CHEAP …)` | plausibly |
| R485 | *"② and ③ conflict"* is **UNDERDETERMINED** | `B (CONFLICTED …)` | **YES** |

**n = 5 is far too small to become a rate and is not made into one.** R485's artifact is now
annotated — `world_original` preserved, `superseded_by: [R486, R487, R499]`.

## Verdict, three-valued

**CONFIRMED:** the artifacts do not record their own retractions, at **18 of 98**. The provenance
gate's `PASS` certifies **json freshness, not truth**.
**UNVERIFIED:** how many of the 18 have a genuinely stale *world*. Two are known (**R485**, **R497**);
the rest are unread.

## ⭐ The thing nobody designed

**The dominant retraction target in the sample is the ANNOUNCED NEXT STEP** — the arithmetic that
was wrong, the audit that was a grep, the proxy that was the wrong one. That is precisely the
sentence the standard names as *the highest-risk line in a report: written last, acted on by a later
round, the only one with no control attached.* **Without anyone building it for that purpose, the
retraction ledger is a longitudinal record of that one failure mode recurring** — which is a stronger
argument for checking the closing sentence than the standard's own two anecdotes.
