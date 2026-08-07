# R587 · The round-id join reaches two documents of three — and the branch refused, correctly

**Decision this makes safe:** how far an exact join key reaches. **Not as far as I predicted.**

**UNVERIFIED.** The join key — the `(R###)` citation within 200 characters after each decimal — is
**exact**, unlike R586's 26-character prose prefix. It still does not connect the corpus:

| pair | shared cited rounds |
|---|---|
| **STATEMENT ∩ DEFINITION** | **11** |
| **STATEMENT ∩ FORMULATION** | **0** |
| **DEFINITION ∩ FORMULATION** | **0** |

**`FORMULATION.md` cites 24 rounds carrying attributed decimals and shares none with either other
document.** My NEXT line said the citations "could" connect them. **They connect two of three, and
the third is disjoint by round as well as by phrasing.**

## ⭐⭐⭐ What the working pair shows, reported as a bound not a count
Three rounds cited in both STATEMENT and DEFINITION have **overlapping but unequal** value sets —
e.g. `R479`: the statement attributes 8 decimals, the definition 9, sharing 6. **That is the
definition carrying values the statement omits, which is expected by design** *(the statement is the
residue; the definition is the reasoning)*. **It is not a disagreement, and the instrument cannot
tell those apart** — a set difference is not a contradiction.

## ⭐ The branch read its control and refused
Three consecutive rounds — R562, R582, R586 — printed a verdict while a positive control printed
FAIL. **Here the control block was written before the verdict text, and the verdict is UNVERIFIED.**
The finding above is reported as **structure**, not as a count, precisely because the control failed.

## Controls
- **Positive** — every document pair must share ≥1 cited round. **FAILED: 2 of 3 pairs share none.**
- **Negative** — an invented round id is cited nowhere. **PASS.**
