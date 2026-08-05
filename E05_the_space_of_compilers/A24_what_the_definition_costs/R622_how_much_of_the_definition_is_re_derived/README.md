# R622 · The gate named "every number is re-derived" re-derives 18.5% of them

**Decision this makes safe:** how large the repair R621 implies actually is. **Not epistemic —
mechanical.** The numbers are traceable; **nothing enforces it.**

| tier | `DEFINITION.md` (n=642) | `STATEMENT.md` (n=135) |
|---|---|---|
| **T1 gate-verified** — an artifact drift breaks the build | **119 (18.5%)** | 28 (20.7%) |
| **T2 anchorable** — the value is a persisted value position, unchecked | **507 (79.0%)** | 104 (77.0%) |
| **T3 unbacked** — appears in no artifact at all | **16 (2.5%)** | 3 (2.2%) |

**World C.** R621's laundering path is real and **is not the normal case** — but the file's dominant
state is **traceable and unenforced**, and the gate's hand-enumerated list covers **one fifth** of
what its name claims.

## ⭐⭐ The g=0 control failed, and the failure was the finding
v1 tested anchoring by **raw substring over concatenated artifact text**. Under it, **`0.9187` — the
number I fabricated in R621, which has no measurement behind it — landed in T2 ANCHORABLE**, because
**R621's own artifact records the mutation string containing it.**

> **The laundering path completed itself through the audit record.**

So raw-text presence was never anchoring; it was *"these digits occur somewhere in a JSON file"* —
which includes prose fields, check notes and quoted retractions. **v2 walks the parsed JSON and
counts only VALUE POSITIONS** — numbers, and strings that are exactly the decimal. `0.9187` then
lands in **T3**, and the control passes.

⚠ **Two changes in one edit, stated:** the repair also normalises formats (`.3f`/`.4f`/absolute), so
matching widened — T2 rose 65.9% → 79.0% and T3 fell 15.6% → 2.5%. **The bound direction is
unchanged and conservative: T3 is understated.**

## The 16 unbacked values, named rather than counted
`0.1695 · 0.1725 · 0.1829 · 0.2116 · 0.2124 · 0.2335 · 0.2482 · 0.2746 · 0.2868 · 0.4309` *(first
10 of 16)* — and **`0.2335`, `0.2482` also appear on `STATEMENT.md`**, alongside **`0.9574`**. Those
three are the transitive anchoring's blind spot made concrete: **present in both documents, backed by
neither.**

## Controls
| control | returned |
|---|---|
| **positive** — a value `derive()` returns | lands in **T1** — PASS |
| **g=0** — R621's fabricated `0.9187` | **T3** under v2 — backed and unbacked are distinguishable |
| **negative** — a decimal drawn from an artifact but absent from `derive()` | **T2** — the tiers are disjoint and the search is not blind |
| **placebo** — a same-shape decimal occurring nowhere | **T3** — PASS |

**MULTIPLICITY:** every decimal × 3 tiers × 2 documents — **777 cells, no sampling.**

**IMPOSSIBLE, named:** *"this number is CORRECT"* would require re-executing 613 rounds, which this
site cannot do. **T1 means only that an artifact drift would break the build.** ⚠ And the unit gap:
the instrument counts **decimal literals**, the claim is about **numeric assertions** — one assertion
can carry several literals and one literal can serve several assertions.

## ⛔ Check #221
*"the **cheapest** repair"* — **an uncomputed comparative**; §4 says a comparative must be computed,
not typed. Nothing compared the two repairs' costs. ✓ The other half — *"which
`definition_matches_the_record` already does for the values it knows"* — **was checked against the
object before building on it, and held**: `derive()` returns `label → (artifact value, round)` and
the gate's own proxy line says *"the numbers this file knows how to extract."*

## The sentence I can no longer write
> *"`definition_matches_the_record` re-derives every number in `DEFINITION.md` from an artifact."*

**It re-derives 119 of 642.** The file's own docstring opens with that sentence, and it is off by a
factor of **five**.

## NEXT
`derive()` is hand-enumerated, so its 18.5% grows only when someone adds a label — the same
hand-list structure R620 measured on the artifact-noun set. **The mechanical repair is to generate
the coverage instead of writing it**: every round's `results/*.json` already carries its values, so a
gate could require that any decimal on either document match a value position in the artifact of a
round the same paragraph cites. **Measure what that automatic rule would flag today** before building
it — if it flags hundreds of correct lines, the rule is unusable regardless of being right.
