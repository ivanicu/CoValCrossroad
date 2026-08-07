# R687 · is there a convention to enforce? — **no, and R686 is downgraded**

**⭐⭐⭐ Of R686's 13 "value-field" rounds, only **6** carry a STRUCTURED judge record; the other **7**
merely MENTION a judge inside a prose field — and one of those is **R684's own verdict sentence**.
Across the 6 there are **7 distinct field names**. The kill fired: **no rule is writable**, and the
production decision is closed rather than deferred.**

## THE DECISION THIS ROUND MAKES SAFE
R686 left a build blocked on an unread fact: a shared field name → a **gate**; one-offs → **by hand**.
Measured: one-offs. **Nothing is built, and that is the answer, not a shortfall.**

## ⭐⭐⭐ THE SPLIT THAT DOWNGRADES R686

| | |
|---|---|
| R686's "value field" rounds | 13 |
| **STRUCTURED record** | **6** |
| **PROSE mention only** | **7** — `R419 R427 R433 R490 R556 R560` **R684** |
| distinct field names across the structured 6 | **7** — `direction evidence names larger_complete not_measured incumbent name` |
| commonest name | covers **1** |

v1 counted *any string containing a judge token*, so `world`, `direction`, `evidence`,
`not_measured` — **prose fields** — read as records. **R684's `world` field is my own verdict string,
which says "2B" because it is describing the finding.** Instrument unit was *a string containing a
token*; claim unit is *a field recording the judge*.

**Controls:** POSITIVE — a judge under a known field name → attributed to it. **g=0** — a judge in a
bare list item → **not** attributed, *the attributor returns both values*. NEGATIVE — no judge → no
name. PLACEBO — identical.

## ⛔ MY REGISTERED INTERVALS SPANNED THE ENTIRE POSSIBLE RANGE
**A [1, 13]** and **B [1, 13]** on a population of 13. **Both scored INSIDE, and both were
unfailable** — any outcome the world could produce lies in `[1, 13]`. *§0: a standard nobody can
fail is not a standard.* The **directional** (one name covers ≥half) is the only row here that could
have failed, and it **did**. **Only that row carries information.**

## ⚠ "STRUCTURED" IS A LENGTH HEURISTIC, STATED AS ONE
A value is called structured if it is **≤24 characters**. That is a proxy for "this field holds a
judge name" and it is not an identification: `"2B wins clearly"` would pass. **The 6/7 split is
therefore approximate**, and the direction of its error is toward **over**-counting structured
records, which makes the "no convention" verdict conservative.

## IMPOSSIBLE HERE
Whether two rounds using the same field name **mean** the same thing needs their code read by a
reader. **A gate sees a spelling, never a semantics** — which is why building one on 7 names over 6
rounds would have enforced nothing.

## NEXT
R686's recoverable count is now 6 structured records plus 13 mentions rather than 19 recoveries
(`results/convention.json`, fields `n_structured` and `n_prose_only`); R686's README is annotated.
Six structured rounds have a machine-readable judge (`results/convention.json`, field
`n_structured`). Read those six field values and check whether each names a judge the round actually
ran at, by comparing against the judge named in its own source. A field holding the wrong judge is worse than a field holding none.
