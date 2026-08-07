# R722 · a shared FILE is not a shared INPUT — and my probe of that was an uncontrolled search

**All `4` readers of `clause_ledger.json` parse, and they share `4` fields — `clause23_admits` in
`3 of 4`. So the sharing is NOT nominal: the derivations behind the number 5 take the **same field**
from the **same file**, and R721's "not disjoint evidences" was right. ⛔ My registered directional —
that coverage would be incomplete — FAILED, because the pattern ladder fixed the blind spot my
previous probe had.**

## check #324 — it holds, and my first probe of it was uncontrolled

✓ 11 sources with 3 shared, `clause_ledger.json` in 4 of 6, and R680's `derivers` is a list of **round
ids** — it counted rounds, not fields.

⛔ **But the probe I ran returned fields for R404 and R405 and nothing for R408 and R667.** That is
**silence, not zero** — my regex matched a few subscript shapes. §4's *a search is an instrument*, and
reporting *"R408 reads no fields"* would have been a **fabricated zero**.

## what each reader takes from the shared file

| round | verdict | fields |
|---|---|---|
| R404 | PARSED | `arms`, `clause23_admits`, `clause2_admits` |
| R405 | PARSED | `clause23_admits`, `sweep` |
| R408 | PARSED | `clause2_admits`, `k`, `sweep` |
| R667 | PARSED | `clause23_admits`, `k` |

**COVERAGE 4 of 4 = 1.00**, reported first-class — because an unparsed round is **UNMEASURED**, never
a zero.

**Shared fields: 4** — `clause23_admits` **3**, `clause2_admits` **2**, `sweep` **2**, `k` **2**.

## controls — 6 PASS, 0 FAIL *(the ⛔ is the registered directional, a prediction not a control)*

| control | returned |
|---|---|
| **POSITIVE** | R404's `clause2_admits` recovered by the subscript pass alone |
| **g=0** | a source with no ledger access → **0** fields, and **UNMEASURED is a distinct value** |
| **NEGATIVE** | R360, which **writes** the ledger → **2** schema fields, with `floor 0 < t 1 ≤ ceiling 2` |
| **SHAM** | docstring-only → **0** mentions vs the body's **10** |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |

⛔ **My negative control's first threshold was 3 and the ceiling is 2** — a **control that could not
pass** (§4). R360 builds the ledger dict from variables, so only 2 of its 15 schema keys appear as
literals anywhere in its source. **The threshold is now computed, not guessed**: floor 0, ceiling 2,
t = 1 — recovering *any* schema field from the writer is what shows the extractor matches field
**names** rather than one reader's idiom.

## specification sweep — 3 pattern sets × 2 populations

| patterns | readers parsed | shared fields | writer schema fields |
|---|---|---|---|
| subscript | 4/4 | 3 | 0 |
| + `.get` | 4/4 | 3 | 0 |
| + bare mention | 4/4 | **4** | **2** |

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** readers parsed | 3 [1, 4] | **4** |
| **B** fields shared by >1 | 1 [0, 5] | **4** |
| **C** most-shared field's reader count | 2 [0, 4] | **3** |
| directional | coverage incomplete | ⛔ **FAILS — all four parsed** |

## limits

- **Absence of a pattern match is NOT absence of access.** The sharing count is a **lower bound** over
  the parsed rounds — here all four, so the bound is tight, but it is still a bound.
- An access I cannot see is not an access that is absent, which is why `UNMEASURED` exists as a value
  distinct from zero.

## impossible here

| criterion | what it would require |
|---|---|
| proving a round does NOT read a field | static analysis stronger than pattern matching |
| cross-release | a second release |
