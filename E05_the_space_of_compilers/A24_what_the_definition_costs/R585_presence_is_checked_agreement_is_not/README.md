# R585 · Presence was checked; agreement was not — and the first cross-document check found one

**Decision this makes safe:** what the provenance gate does and does not span.

⛔ **My NEXT line said the two documents' decimals "have never been checked."** False.
`statement_provenance.py` checks that **all 92** statement decimals appear in `DEFINITION.md` — it
checks **PRESENCE**. **Nothing checked whether a shared label carries the same VALUE.**

**WORLD B.** Across 114 labelled decimals on the statement and 738 in the definition, **24 label
fragments appear in both. 23 agree. 1 disagrees:**

> **`random predictor lands at`** — statement **0.3342**, definition **0.3321**

## ⭐⭐⭐ And it is not an error — which makes it worse
Both values are real, from different rounds:

| source | `random.mean` | comparison |
|---|---|---|
| **R504 / R505** | **0.33212…** | pair predictors |
| **R506** | **0.334151…** | ranker-restricted |

**Neither document is wrong. The label *"a random predictor lands at X"* reads as a property of the
release when it is a property of a round's design** — a different comparison population gives a
different random baseline. **A typo would have been cheaper: it would be visibly wrong somewhere.
This is correct in both places and misleading in either alone.**

**Landed:** the statement now names both baselines and the design each belongs to.

⚠ **Both sites were ALREADY attributed** — the statement cites `*(R506)*` and the definition's
value sits under its own round. **The defect was never missing provenance; it was that each
document named its own round and neither said the other value existed.** A reader of one page
sees a correctly-cited number and no reason to suspect a second.

⚠ **And the edit's first attempt failed on a LINE WRAP** — twelfth instance this session of
matching a string as I picture it. **The commit guard stopped it**, unlike two rounds ago when
an identical failure let a false claim through.

## Controls
- **Positive** — at least one label is shared, so a cross-document comparison exists and a `0` would
  have been a measurement rather than silence. **PASS.**
- **Negative** — an invented label appears in neither. **PASS.**
- ⚠ **A 26-character label prefix DETECTS disagreement and cannot prove agreement.** The 23 agreeing
  labels are *not contradicted*, not *verified*.
